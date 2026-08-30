#!/usr/bin/env python3
"""Build no-claim HLOGA substitution-estimation diagnostics.

The estimator compares treated federal LDA clients with Colorado state-lobbying
controls on a balanced actor-quarter panel. It is deliberately diagnostic:
treatment is perfectly confounded with source system, the outcome definitions
are not identical, and the committed panel has only two clean pre-HLOGA
quarters. The outputs record those failures instead of promoting the contrast
to a causal substitution estimate.
"""

from __future__ import annotations

import argparse
import csv
import html
import math
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paper_release_metadata import (  # noqa: E402
    RELEASE_METADATA_FIELDS,
    metadata_summary_lines,
    release_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
FIRST_WAVE = ROOT / "data" / "calibration" / "first-wave"
REPORTS = ROOT / "reports"
LDA_INPUT = "substitution-historical-lda-panel.csv"
CONTROL_INPUT = "substitution-state-lobbying-control-panel.csv"
PANEL_OUTPUT = FIRST_WAVE / "substitution-estimation-panel.csv"
DIAGNOSTIC_OUTPUT = REPORTS / "substitution-estimation-diagnostics.csv"
EVENT_STUDY_OUTPUT = REPORTS / "substitution-estimation-event-study.csv"
LEAVE_ONE_OUTPUT = REPORTS / "substitution-estimation-leave-one-actor.csv"
REPORT_OUTPUT = REPORTS / "substitution-estimation-diagnostics.md"
FIGURE_OUTPUT = REPORTS / "substitution-estimation-specification-contrast.svg"

REFORM_EVENT_ID = "hloga-2007-federal-lobbying-disclosure"
TREATMENT_DATE = date(2007, 9, 14)
EVENT_QUARTER = "2007Q3"
PRIMARY_PRE = ("2007Q1", "2007Q2")
PRIMARY_POST = ("2007Q4", "2008Q1", "2008Q2", "2008Q3", "2008Q4")
MINIMUM_CLEAN_PRE_QUARTERS = 3
MINIMUM_INDEPENDENT_PLACEBO_DATES = 2
DEFAULT_BOOTSTRAP_REPS = 10_000
DEFAULT_SEED = 20_070_914

TREATED_GROUP = "treated_hloga_lda_client"
CONTROL_GROUP = "control_unaffected_colorado_state_lobbying_jurisdiction"
CLAIM_BOUNDARY = (
    "Descriptive source-confounded HLOGA panel diagnostics only; no causal "
    "substitution effect, hidden-channel magnitude, policy calibration, or "
    "national generalization."
)
OVERALL_NOT_CLEARED = "effect_model_and_falsification_gates_not_cleared"

REGISTRATION_FILING_TYPES = {"RA", "RR"}


@dataclass(frozen=True)
class Quarter:
    key: str
    start: date
    end: date
    event_time: int


QUARTERS = (
    Quarter("2007Q1", date(2007, 1, 1), date(2007, 3, 31), -2),
    Quarter("2007Q2", date(2007, 4, 1), date(2007, 6, 30), -1),
    Quarter("2007Q3", date(2007, 7, 1), date(2007, 9, 30), 0),
    Quarter("2007Q4", date(2007, 10, 1), date(2007, 12, 31), 1),
    Quarter("2008Q1", date(2008, 1, 1), date(2008, 3, 31), 2),
    Quarter("2008Q2", date(2008, 4, 1), date(2008, 6, 30), 3),
    Quarter("2008Q3", date(2008, 7, 1), date(2008, 9, 30), 4),
    Quarter("2008Q4", date(2008, 10, 1), date(2008, 12, 31), 5),
)
QUARTER_BY_KEY = {quarter.key: quarter for quarter in QUARTERS}


PANEL_FIELDS = [
    "reformEventId",
    "canonicalActorId",
    "actorName",
    "comparisonGroup",
    "treated",
    "sourceSystem",
    "sourceOutcome",
    "quarter",
    "quarterIndex",
    "eventTimeQuarter",
    "periodStart",
    "periodEnd",
    "eventQuarter",
    "includedInPrimary",
    "prePostClass",
    "observedSourceRecords",
    "zeroFilled",
    "activityAmountMillions",
    "activityAmountDollars",
    "log1pActivityDollars",
    "preparationRule",
    "claimBoundary",
]

DIAGNOSTIC_FIELDS = [
    *RELEASE_METADATA_FIELDS,
    "diagnosticFamily",
    "diagnosticId",
    "label",
    "status",
    "gateResult",
    "outcome",
    "estimator",
    "preWindow",
    "postWindow",
    "estimate",
    "estimateExpPercent",
    "lower95",
    "upper95",
    "treatedActors",
    "controlActors",
    "observations",
    "evidence",
    "interpretation",
    "claimBoundary",
    "nextAction",
]

EVENT_STUDY_FIELDS = [
    *RELEASE_METADATA_FIELDS,
    "quarter",
    "eventTimeQuarter",
    "eventQuarter",
    "includedInPrimary",
    "treatedActors",
    "controlActors",
    "treatedMeanLogActivity",
    "controlMeanLogActivity",
    "treatedNormalizedFromPre",
    "controlNormalizedFromPre",
    "differenceNormalized",
    "claimBoundary",
    "notes",
]

LEAVE_ONE_FIELDS = [
    *RELEASE_METADATA_FIELDS,
    "omittedActorId",
    "omittedActorName",
    "omittedGroup",
    "fullEstimate",
    "leaveOneEstimate",
    "leaveOneEstimateExpPercent",
    "shiftFromFull",
    "signStable",
    "status",
    "claimBoundary",
    "notes",
]


SPECIFICATIONS = (
    {
        "id": "primary_actor_quarter_did",
        "family": "estimate",
        "label": "Primary window",
        "pre": PRIMARY_PRE,
        "post": PRIMARY_POST,
        "kind": "primary",
    },
    {
        "id": "balanced_two_quarter_window",
        "family": "window_sensitivity",
        "label": "Balanced two-quarter post window",
        "pre": PRIMARY_PRE,
        "post": ("2007Q4", "2008Q1"),
        "kind": "window",
    },
    {
        "id": "calendar_2008_post_window",
        "family": "window_sensitivity",
        "label": "Calendar 2008 post window",
        "pre": PRIMARY_PRE,
        "post": ("2008Q1", "2008Q2", "2008Q3", "2008Q4"),
        "kind": "window",
    },
    {
        "id": "late_2008_post_window",
        "family": "window_sensitivity",
        "label": "Late 2008 post window",
        "pre": PRIMARY_PRE,
        "post": ("2008Q3", "2008Q4"),
        "kind": "window",
    },
    {
        "id": "clean_pre_hloga_2007q2_placebo",
        "family": "placebo",
        "label": "Clean pre-HLOGA 2007Q2 placebo",
        "pre": ("2007Q1",),
        "post": ("2007Q2",),
        "kind": "clean_placebo",
    },
    {
        "id": "post_treatment_2008q2_timing_placebo",
        "family": "placebo",
        "label": "Post-treatment 2008Q2 timing placebo",
        "pre": ("2007Q4", "2008Q1"),
        "post": ("2008Q2", "2008Q3"),
        "kind": "contaminated_placebo",
    },
    {
        "id": "post_treatment_2008q3_timing_placebo",
        "family": "placebo",
        "label": "Post-treatment 2008Q3 timing placebo",
        "pre": ("2008Q1", "2008Q2"),
        "post": ("2008Q3", "2008Q4"),
        "kind": "contaminated_placebo",
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-wave", type=Path, default=FIRST_WAVE)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--panel-output", type=Path)
    parser.add_argument("--bootstrap-reps", type=int, default=DEFAULT_BOOTSTRAP_REPS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    first_wave = resolve(args.first_wave)
    reports = resolve(args.reports)
    panel_output = resolve(args.panel_output) if args.panel_output else first_wave / PANEL_OUTPUT.name
    reports.mkdir(parents=True, exist_ok=True)
    panel_output.parent.mkdir(parents=True, exist_ok=True)

    lda_rows = read_csv(first_wave / LDA_INPUT)
    control_rows = read_csv(first_wave / CONTROL_INPUT)
    if not lda_rows:
        raise SystemExit(f"Missing or empty treated panel: {first_wave / LDA_INPUT}")
    if not control_rows:
        raise SystemExit(f"Missing or empty control panel: {first_wave / CONTROL_INPUT}")
    if args.bootstrap_reps < 100:
        raise SystemExit("--bootstrap-reps must be at least 100")

    metadata = release_metadata()
    panel_rows, preparation = prepare_panel(lda_rows, control_rows)
    diagnostics, event_rows, leave_one_rows, estimates = analyze_panel(
        panel_rows,
        preparation,
        metadata,
        bootstrap_reps=args.bootstrap_reps,
        seed=args.seed,
    )

    diagnostic_output = reports / DIAGNOSTIC_OUTPUT.name
    event_output = reports / EVENT_STUDY_OUTPUT.name
    leave_output = reports / LEAVE_ONE_OUTPUT.name
    report_output = reports / REPORT_OUTPUT.name
    figure_output = reports / FIGURE_OUTPUT.name

    write_csv(panel_output, panel_rows, PANEL_FIELDS)
    write_csv(diagnostic_output, diagnostics, DIAGNOSTIC_FIELDS)
    write_csv(event_output, event_rows, EVENT_STUDY_FIELDS)
    write_csv(leave_output, leave_one_rows, LEAVE_ONE_FIELDS)
    write_specification_figure(figure_output, estimates)
    write_report(
        report_output,
        diagnostics,
        event_rows,
        leave_one_rows,
        preparation,
        metadata,
        panel_output,
        diagnostic_output,
        event_output,
        leave_output,
        figure_output,
        bootstrap_reps=args.bootstrap_reps,
        bootstrap_seed=args.seed,
    )

    for path in (
        panel_output,
        diagnostic_output,
        event_output,
        leave_output,
        report_output,
        figure_output,
    ):
        print(f"Wrote {path}")
    return 0


def resolve(path: Path | None) -> Path:
    if path is None:
        raise ValueError("path is required")
    return path if path.is_absolute() else ROOT / path


def prepare_panel(
    lda_rows: list[dict[str, str]],
    control_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int | str]]:
    selected_filings, lda_stats = select_lda_filings(lda_rows)
    selected_controls, control_stats = deduplicate_control_rows(control_rows)
    treated_issue_codes = {
        row["issueCode"].strip()
        for row in lda_rows
        if row.get("issueCode", "").strip()
    }
    control_issue_codes = {
        row["issueCode"].strip()
        for row in control_rows
        if row.get("issueCode", "").strip()
    }

    amounts: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    observed_records: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    actor_names: dict[str, Counter[str]] = defaultdict(Counter)
    actor_groups: dict[str, str] = {}
    actor_sources: dict[str, str] = {}
    actor_outcomes: dict[str, str] = {}

    for row in selected_filings:
        actor_id = required(row, "canonicalActorId", "selected LDA filing")
        register_actor(
            actor_id,
            row.get("primaryName", ""),
            TREATED_GROUP,
            row.get("sourceSystem", "Official LDA API"),
            "federal LDA reported lobbying amount",
            actor_names,
            actor_groups,
            actor_sources,
            actor_outcomes,
        )
        start = parse_date(required(row, "periodStart", "selected LDA filing"))
        end = parse_date(required(row, "periodEnd", "selected LDA filing"))
        value = nonnegative_float(row.get("activityAmount", ""), "LDA activityAmount")
        period_days = (end - start).days + 1
        if period_days <= 0:
            raise ValueError(f"Invalid LDA period for filing {row.get('filingUuid', '')}")
        for quarter in QUARTERS:
            overlap = overlap_days(start, end, quarter.start, quarter.end)
            if overlap <= 0:
                continue
            amounts[actor_id][quarter.key] += value * overlap / period_days
            observed_records[actor_id][quarter.key] += 1

    for row in selected_controls:
        actor_id = required(row, "canonicalActorId", "Colorado control row")
        register_actor(
            actor_id,
            row.get("primaryName", row.get("stateClientName", "")),
            CONTROL_GROUP,
            row.get("sourceSystem", "Colorado Secretary of State lobbyist income data"),
            "Colorado state-lobbyist income transaction amount",
            actor_names,
            actor_groups,
            actor_sources,
            actor_outcomes,
        )
        source_date = parse_date(row.get("sourceDate") or required(row, "periodStart", "Colorado control row"))
        value = nonnegative_float(row.get("activityAmount", ""), "Colorado activityAmount")
        quarter = quarter_for_date(source_date)
        if quarter is None:
            continue
        amounts[actor_id][quarter.key] += value
        observed_records[actor_id][quarter.key] += 1

    panel_rows: list[dict[str, str]] = []
    for actor_id in sorted(actor_groups):
        group = actor_groups[actor_id]
        actor_name = preferred_name(actor_names[actor_id])
        for quarter_index, quarter in enumerate(QUARTERS):
            amount_millions = amounts[actor_id].get(quarter.key, 0.0)
            amount_dollars = amount_millions * 1_000_000.0
            source_count = observed_records[actor_id].get(quarter.key, 0)
            pre_post_class = (
                "clean_pre"
                if quarter.key in PRIMARY_PRE
                else "event_quarter_excluded"
                if quarter.key == EVENT_QUARTER
                else "post"
            )
            panel_rows.append({
                "reformEventId": REFORM_EVENT_ID,
                "canonicalActorId": actor_id,
                "actorName": actor_name,
                "comparisonGroup": group,
                "treated": "1" if group == TREATED_GROUP else "0",
                "sourceSystem": actor_sources[actor_id],
                "sourceOutcome": actor_outcomes[actor_id],
                "quarter": quarter.key,
                "quarterIndex": str(quarter_index),
                "eventTimeQuarter": str(quarter.event_time),
                "periodStart": quarter.start.isoformat(),
                "periodEnd": quarter.end.isoformat(),
                "eventQuarter": "yes" if quarter.key == EVENT_QUARTER else "no",
                "includedInPrimary": "no" if quarter.key == EVENT_QUARTER else "yes",
                "prePostClass": pre_post_class,
                "observedSourceRecords": str(source_count),
                "zeroFilled": "yes" if source_count == 0 else "no",
                "activityAmountMillions": fixed(amount_millions, 8),
                "activityAmountDollars": fixed(amount_dollars, 2),
                "log1pActivityDollars": fixed(math.log1p(amount_dollars), 8),
                "preparationRule": (
                    "LDA issue rows collapsed to filing UUID, registration rows removed, "
                    "latest filing revision retained per actor-client-registrant-period, "
                    "semiannual amounts allocated to quarters by covered days"
                    if group == TREATED_GROUP
                    else "one Colorado row retained per client-lobbyist-registration-date-amount receipt key and remaining income summed by actor-quarter"
                ),
                "claimBoundary": CLAIM_BOUNDARY,
            })

    treated_actors = {row["canonicalActorId"] for row in panel_rows if row["comparisonGroup"] == TREATED_GROUP}
    control_actors = {row["canonicalActorId"] for row in panel_rows if row["comparisonGroup"] == CONTROL_GROUP}
    zero_treated = sum(
        row["zeroFilled"] == "yes" for row in panel_rows if row["comparisonGroup"] == TREATED_GROUP
    )
    zero_control = sum(
        row["zeroFilled"] == "yes" for row in panel_rows if row["comparisonGroup"] == CONTROL_GROUP
    )
    preparation: dict[str, int | str] = {
        **lda_stats,
        **control_stats,
        "treatedActors": len(treated_actors),
        "controlActors": len(control_actors),
        "panelRows": len(panel_rows),
        "zeroTreatedActorQuarters": zero_treated,
        "zeroControlActorQuarters": zero_control,
        "treatedIssueCodeCount": len(treated_issue_codes),
        "controlIssueCodeCount": len(control_issue_codes),
        "sharedIssueCodeCount": len(treated_issue_codes & control_issue_codes),
        "cleanPreQuarters": len(PRIMARY_PRE),
        "postQuarters": len(PRIMARY_POST),
        "eventQuartersExcluded": 1,
    }
    return panel_rows, preparation


def select_lda_filings(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int | str]]:
    by_uuid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for index, row in enumerate(rows):
        filing_uuid = row.get("filingUuid") or f"missing-filing-uuid-{index}"
        by_uuid[filing_uuid].append(row)

    unique_filings: list[dict[str, str]] = []
    conflicting_issue_duplicates = 0
    comparison_fields = (
        "canonicalActorId",
        "ldaClientId",
        "registrantName",
        "filingYear",
        "filingPeriod",
        "periodStart",
        "periodEnd",
        "activityAmount",
    )
    for filing_uuid, filing_rows in sorted(by_uuid.items()):
        representative = min(
            filing_rows,
            key=lambda row: (
                row.get("sourceRecordId", ""),
                row.get("issueCode", ""),
            ),
        )
        signatures = {
            tuple(row.get(field, "") for field in comparison_fields)
            for row in filing_rows
        }
        if len(signatures) > 1:
            conflicting_issue_duplicates += 1
        unique_filings.append(representative)

    non_registration = [
        row for row in unique_filings
        if row.get("filingType", "") not in REGISTRATION_FILING_TYPES
    ]
    revision_groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in non_registration:
        key = (
            row.get("canonicalActorId", ""),
            row.get("ldaClientId", ""),
            normalize(row.get("registrantName", "")),
            row.get("filingYear", ""),
            row.get("filingPeriod", ""),
        )
        revision_groups[key].append(row)

    selected = [
        max(group, key=filing_revision_sort_key)
        for _key, group in sorted(revision_groups.items())
    ]
    selected.sort(key=lambda row: (
        row.get("canonicalActorId", ""),
        row.get("periodStart", ""),
        row.get("ldaClientId", ""),
        normalize(row.get("registrantName", "")),
        row.get("filingUuid", ""),
    ))
    revised_groups = sum(len(group) > 1 for group in revision_groups.values())
    superseded = sum(len(group) - 1 for group in revision_groups.values())
    return selected, {
        "ldaInputRows": len(rows),
        "ldaUniqueFilingUuids": len(unique_filings),
        "ldaIssueRowsCollapsed": len(rows) - len(unique_filings),
        "ldaConflictingIssueDuplicateFilings": conflicting_issue_duplicates,
        "ldaRegistrationFilingsExcluded": len(unique_filings) - len(non_registration),
        "ldaRevisionGroups": len(revision_groups),
        "ldaRevisedGroups": revised_groups,
        "ldaSupersededFilingsExcluded": superseded,
        "ldaSelectedFilings": len(selected),
    }


def deduplicate_control_rows(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int | str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        business_key = (
            row.get("primaryLobbyistId", ""),
            row.get("annualLobbyistRegistrationId", ""),
            normalize(row.get("stateClientKey") or row.get("stateClientName", "")),
            row.get("sourceDate") or row.get("periodStart", ""),
            row.get("activityMeasure", ""),
            normalize(row.get("lobbyistName", "")),
        )
        if not any(business_key):
            business_key = (row.get("sourceRecordId", ""),)
        grouped[business_key].append(row)
    selected = [
        min(group, key=lambda row: row.get("sourceRecordId", ""))
        for _key, group in sorted(grouped.items())
    ]
    selected.sort(key=lambda row: (
        row.get("canonicalActorId", ""),
        row.get("periodStart", ""),
        row.get("sourceRecordId", ""),
    ))
    repeated_groups = [group for group in grouped.values() if len(group) > 1]
    report_metadata_conflicts = sum(
        len({
            (row.get("reportMonth", ""), row.get("reportDueDate", ""))
            for row in group
        }) > 1
        for group in repeated_groups
    )
    return selected, {
        "controlInputRows": len(rows),
        "controlRepeatedReceiptRowsExcluded": len(rows) - len(selected),
        "controlRepeatedReceiptKeyGroups": len(repeated_groups),
        "controlReportMetadataConflictGroups": report_metadata_conflicts,
        "controlSelectedTransactions": len(selected),
    }


def analyze_panel(
    panel_rows: list[dict[str, str]],
    preparation: dict[str, int | str],
    metadata: dict[str, str],
    *,
    bootstrap_reps: int,
    seed: int,
) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, dict[str, float | str | tuple[str, ...]]],
]:
    panel = index_panel(panel_rows)
    actors = sorted(panel["groups"])
    treated = [actor for actor in actors if panel["groups"][actor] == TREATED_GROUP]
    controls = [actor for actor in actors if panel["groups"][actor] == CONTROL_GROUP]
    observations = len(panel_rows) - len(actors)

    estimates: dict[str, dict[str, float | str | tuple[str, ...]]] = {}
    for index, specification in enumerate(SPECIFICATIONS):
        result = estimate_contrast(
            panel,
            specification["pre"],
            specification["post"],
            bootstrap_reps=bootstrap_reps,
            seed=seed + index,
        )
        estimates[specification["id"]] = {
            **specification,
            **result,
        }

    winsorized = estimate_contrast(
        panel,
        PRIMARY_PRE,
        PRIMARY_POST,
        bootstrap_reps=bootstrap_reps,
        seed=seed + 100,
        winsor_quantile=0.95,
    )
    estimates["within_group_p95_winsorized"] = {
        "id": "within_group_p95_winsorized",
        "family": "outlier_sensitivity",
        "label": "Within-group p95 winsorized",
        "pre": PRIMARY_PRE,
        "post": PRIMARY_POST,
        "kind": "outlier",
        **winsorized,
    }

    primary = estimates["primary_actor_quarter_did"]
    leave_one_rows = leave_one_actor_rows(panel, primary, metadata)
    event_rows = event_study_rows(panel, metadata)
    diagnostic_rows = diagnostic_summary_rows(
        panel,
        preparation,
        estimates,
        leave_one_rows,
        metadata,
        observations=observations,
        bootstrap_reps=bootstrap_reps,
        seed=seed,
    )
    return diagnostic_rows, event_rows, leave_one_rows, estimates


def diagnostic_summary_rows(
    panel: dict[str, object],
    preparation: dict[str, int | str],
    estimates: dict[str, dict[str, float | str | tuple[str, ...]]],
    leave_one_rows: list[dict[str, str]],
    metadata: dict[str, str],
    *,
    observations: int,
    bootstrap_reps: int,
    seed: int,
) -> list[dict[str, str]]:
    groups = panel["groups"]
    sources = panel["sources"]
    outcomes = panel["sourceOutcomes"]
    treated = [actor for actor, group in groups.items() if group == TREATED_GROUP]
    controls = [actor for actor, group in groups.items() if group == CONTROL_GROUP]
    treated_sources = {sources[actor] for actor in treated}
    control_sources = {sources[actor] for actor in controls}
    treated_outcomes = {outcomes[actor] for actor in treated}
    control_outcomes = {outcomes[actor] for actor in controls}

    rows: list[dict[str, str]] = []

    def add(
        family: str,
        diagnostic_id: str,
        label: str,
        status: str,
        gate_result: str,
        evidence: str,
        interpretation: str,
        next_action: str,
        *,
        outcome: str = "",
        estimator: str = "",
        pre_window: str = "",
        post_window: str = "",
        estimate: float | None = None,
        estimate_exp_percent: float | None = None,
        lower95: float | None = None,
        upper95: float | None = None,
        treated_actors: int | None = None,
        control_actors: int | None = None,
        row_observations: int | None = None,
    ) -> None:
        rows.append({
            **metadata,
            "diagnosticFamily": family,
            "diagnosticId": diagnostic_id,
            "label": label,
            "status": status,
            "gateResult": gate_result,
            "outcome": outcome,
            "estimator": estimator,
            "preWindow": pre_window,
            "postWindow": post_window,
            "estimate": optional_fixed(estimate, 6),
            "estimateExpPercent": optional_fixed(estimate_exp_percent, 2),
            "lower95": optional_fixed(lower95, 6),
            "upper95": optional_fixed(upper95, 6),
            "treatedActors": str(treated_actors if treated_actors is not None else len(treated)),
            "controlActors": str(control_actors if control_actors is not None else len(controls)),
            "observations": str(row_observations if row_observations is not None else observations),
            "evidence": evidence,
            "interpretation": interpretation,
            "claimBoundary": CLAIM_BOUNDARY,
            "nextAction": next_action,
        })

    issue_conflicts = int(preparation["ldaConflictingIssueDuplicateFilings"])
    add(
        "data_quality",
        "lda_issue_row_deduplication",
        "LDA issue-row amount duplication",
        "resolved_for_diagnostic" if issue_conflicts == 0 else "blocked",
        "pass" if issue_conflicts == 0 else "fail",
        (
            f"inputRows={preparation['ldaInputRows']}; "
            f"uniqueFilingUuids={preparation['ldaUniqueFilingUuids']}; "
            f"issueRowsCollapsed={preparation['ldaIssueRowsCollapsed']}; "
            f"conflictingFilings={issue_conflicts}"
        ),
        (
            "Repeated issue rows no longer multiply filing amounts."
            if issue_conflicts == 0
            else "At least one filing has conflicting values across repeated issue rows."
        ),
        "Review conflicting filing UUIDs before reusing the amount outcome." if issue_conflicts else "Retain filing-UUID collapse in every estimator.",
    )
    add(
        "data_quality",
        "lda_revision_deduplication",
        "LDA amendments and registration filings",
        "resolved_for_diagnostic",
        "pass",
        (
            f"registrationFilingsExcluded={preparation['ldaRegistrationFilingsExcluded']}; "
            f"revisedGroups={preparation['ldaRevisedGroups']}; "
            f"supersededFilingsExcluded={preparation['ldaSupersededFilingsExcluded']}; "
            f"selectedFilings={preparation['ldaSelectedFilings']}"
        ),
        "The latest observed filing revision is retained within each actor-client-registrant-period.",
        "Validate filing-version rules against official LDA amendment semantics before claim-bearing use.",
    )
    add(
        "data_quality",
        "colorado_repeated_receipt_key_deduplication",
        "Colorado repeated receipt-key rows",
        "diagnostic_rule_with_source_caveat",
        "informational",
        (
            f"inputRows={preparation['controlInputRows']}; "
            f"repeatedReceiptRowsExcluded={preparation['controlRepeatedReceiptRowsExcluded']}; "
            f"receiptKeyGroups={preparation['controlRepeatedReceiptKeyGroups']}; "
            f"reportMetadataConflictGroups={preparation['controlReportMetadataConflictGroups']}; "
            f"selectedTransactions={preparation['controlSelectedTransactions']}"
        ),
        (
            "One row is retained for each client, lobbyist, registration, receipt-date, and amount key. "
            "Repeated keys differ in report-month metadata, so this is a diagnostic deduplication rule rather than verified source supersession."
        ),
        "Validate repeated receipt keys against Colorado reporting and amendment semantics before claim-bearing use.",
    )
    add(
        "data_quality",
        "balanced_actor_quarter_panel",
        "Balanced actor-quarter preparation",
        "ready_for_diagnostic",
        "pass",
        (
            f"panelRows={preparation['panelRows']}; treatedActors={len(treated)}; "
            f"controlActors={len(controls)}; "
            f"zeroTreatedActorQuarters={preparation['zeroTreatedActorQuarters']}; "
            f"zeroControlActorQuarters={preparation['zeroControlActorQuarters']}"
        ),
        "Every selected actor has eight quarter rows; absent transactions are represented as zero activity.",
        "Distinguish true zero activity from missing reporting before inferential use.",
    )

    source_separated = treated_sources.isdisjoint(control_sources)
    add(
        "design_gate",
        "treatment_source_system_separation",
        "Treatment is separable from source system",
        "blocked" if source_separated else "ready_for_review",
        "fail" if source_separated else "pass",
        (
            f"treatedSources={'; '.join(sorted(treated_sources))}; "
            f"controlSources={'; '.join(sorted(control_sources))}; "
            f"sharedSources={'; '.join(sorted(treated_sources & control_sources)) or 'none'}"
        ),
        (
            "Treatment status is perfectly confounded with source and jurisdiction, so time-varying reporting changes are inseparable from the contrast."
            if source_separated
            else "At least one source system spans treated and control observations."
        ),
        "Add unaffected federal LDA controls or another within-source comparison design.",
    )
    common_outcome = bool(treated_outcomes & control_outcomes)
    add(
        "design_gate",
        "common_outcome_semantics",
        "Treated and control outcomes share a measurement definition",
        "blocked" if not common_outcome else "ready_for_review",
        "fail" if not common_outcome else "pass",
        (
            f"treatedOutcome={'; '.join(sorted(treated_outcomes))}; "
            f"controlOutcome={'; '.join(sorted(control_outcomes))}"
        ),
        (
            "Federal LDA reported amounts and Colorado lobbyist-income transactions are not the same outcome process."
            if not common_outcome
            else "The outcome definition overlaps across groups."
        ),
        "Use the same filing or transaction definition on both sides of the comparison.",
    )
    treated_issue_count = int(preparation["treatedIssueCodeCount"])
    control_issue_count = int(preparation["controlIssueCodeCount"])
    shared_issue_count = int(preparation["sharedIssueCodeCount"])
    issue_overlap = shared_issue_count > 0
    add(
        "design_gate",
        "actor_issue_unit_comparability",
        "Actor-issue-quarter unit is estimable",
        "blocked" if not issue_overlap else "ready_for_review",
        "fail" if not issue_overlap else "pass",
        (
            f"treatedIssueCodes={treated_issue_count}; controlIssueCodes={control_issue_count}; "
            f"sharedIssueCodes={shared_issue_count}"
        ),
        (
            "LDA issue codes and Colorado business/industry labels have no shared reviewed issue taxonomy, so the estimator falls back to actor-quarter."
            if not issue_overlap
            else "A reviewed issue-code overlap exists."
        ),
        "Build and adjudicate a common substantive issue crosswalk before estimating actor-issue effects.",
    )
    pre_depth_ready = len(PRIMARY_PRE) >= MINIMUM_CLEAN_PRE_QUARTERS
    add(
        "design_gate",
        "clean_pre_period_depth",
        "Clean pre-trend depth",
        "blocked" if not pre_depth_ready else "ready_for_review",
        "fail" if not pre_depth_ready else "pass",
        (
            f"cleanPreQuarters={len(PRIMARY_PRE)}; minimum={MINIMUM_CLEAN_PRE_QUARTERS}; "
            f"eventQuarter={EVENT_QUARTER} excluded because it straddles {TREATMENT_DATE.isoformat()}"
        ),
        (
            "Two clean quarters permit one pre-period contrast but not a credible trend-shape assessment."
            if not pre_depth_ready
            else "The panel has the minimum clean pre-period depth."
        ),
        "Extend both groups backward by at least two years at a common quarterly grain.",
    )
    independent_placebos = 1
    placebo_depth_ready = independent_placebos >= MINIMUM_INDEPENDENT_PLACEBO_DATES
    add(
        "design_gate",
        "independent_clean_placebo_depth",
        "Independent clean placebo-date depth",
        "blocked" if not placebo_depth_ready else "ready_for_review",
        "fail" if not placebo_depth_ready else "pass",
        (
            f"independentCleanPlaceboDates={independent_placebos}; "
            f"minimum={MINIMUM_INDEPENDENT_PLACEBO_DATES}; "
            "the only clean placebo is the same Q1-to-Q2 contrast used for the one-step pre-trend check"
        ),
        "The committed time window cannot supply multiple independent, uncontaminated placebo dates.",
        "Add earlier same-source quarters before treating placebo evidence as a falsification gate.",
    )

    primary = estimates["primary_actor_quarter_did"]
    primary_interval_excludes_zero = not (
        float(primary["lower95"]) <= 0.0 <= float(primary["upper95"])
    )
    add_estimate_row(
        add,
        primary,
        status="diagnostic_only",
        gate_result="pass" if primary_interval_excludes_zero else "fail",
        evidence=(
            f"bootstrapReps={bootstrap_reps}; baseSeed={seed}; "
            f"actorBootstrap95=[{float(primary['lower95']):.3f}, {float(primary['upper95']):.3f}]; "
            f"treatedMeanChange={float(primary['treatedMeanChange']):.3f}; "
            f"controlMeanChange={float(primary['controlMeanChange']):.3f}"
        ),
        interpretation=(
            "The descriptive differential log change is not distinguishable from zero in the actor bootstrap and remains source-confounded."
            if not primary_interval_excludes_zero
            else "The actor-bootstrap interval excludes zero, but structural design gates still block causal interpretation."
        ),
        next_action="Treat this as a model diagnostic only; do not label it a HLOGA or substitution effect.",
    )

    pretrend = estimates["clean_pre_hloga_2007q2_placebo"]
    add_estimate_row(
        add,
        {
            **pretrend,
            "id": "single_interval_pretrend_check",
            "family": "pretrend",
            "label": "Single clean pre-period change",
        },
        status="not_testable_as_trend",
        gate_result="fail",
        evidence=(
            f"Q1-to-Q2 differential={float(pretrend['estimate']):.3f}; "
            f"actorBootstrap95=[{float(pretrend['lower95']):.3f}, {float(pretrend['upper95']):.3f}]; "
            "only one clean pre interval is available"
        ),
        interpretation="The pre-period contrast is opposite in sign to the primary estimate and cannot establish parallel trends.",
        next_action="Acquire at least three, preferably eight or more, clean pre-treatment quarters in both groups.",
    )

    placebo_magnitude_reassuring = abs(float(pretrend["estimate"])) <= 0.25 * max(
        abs(float(primary["estimate"])),
        1e-12,
    )
    for specification in SPECIFICATIONS:
        if specification["family"] != "placebo":
            continue
        result = estimates[specification["id"]]
        if specification["kind"] == "clean_placebo":
            status = "does_not_reassure" if not placebo_magnitude_reassuring else "reassuring_but_underpowered"
            gate_result = "fail" if not placebo_magnitude_reassuring else "informational"
            interpretation = (
                "The only clean placebo is large relative to the primary estimate and is not independent of the pre-trend check."
            )
            next_action = "Do not treat this single placebo as causal validation; extend the clean pre-period."
        else:
            status = "post_treatment_timing_sensitivity_only"
            gate_result = "informational"
            interpretation = "This shifted date occurs after the true HLOGA treatment and cannot function as a no-treatment placebo."
            next_action = "Use earlier uncontaminated placebo dates after extending the panel."
        add_estimate_row(
            add,
            result,
            status=status,
            gate_result=gate_result,
            evidence=(
                f"actorBootstrap95=[{float(result['lower95']):.3f}, {float(result['upper95']):.3f}]"
            ),
            interpretation=interpretation,
            next_action=next_action,
        )

    window_results = [
        estimates["balanced_two_quarter_window"],
        estimates["calendar_2008_post_window"],
        estimates["late_2008_post_window"],
    ]
    primary_sign = sign(float(primary["estimate"]))
    window_sign_stable = all(sign(float(result["estimate"])) == primary_sign for result in window_results)
    for result in window_results:
        add_estimate_row(
            add,
            result,
            status="direction_stable_diagnostic" if window_sign_stable else "direction_unstable",
            gate_result="informational" if window_sign_stable else "fail",
            evidence=(
                f"actorBootstrap95=[{float(result['lower95']):.3f}, {float(result['upper95']):.3f}]; "
                f"primaryEstimate={float(primary['estimate']):.3f}"
            ),
            interpretation=(
                "The sign matches the primary diagnostic, but uncertainty and structural source confounding remain."
                if window_sign_stable
                else "The estimate changes sign across reasonable windows."
            ),
            next_action="Re-run window sensitivity only after a comparable same-source design is available.",
        )

    winsorized = estimates["within_group_p95_winsorized"]
    winsor_sign_stable = sign(float(winsorized["estimate"])) == primary_sign
    relative_shift = abs(float(winsorized["estimate"]) - float(primary["estimate"])) / max(
        abs(float(primary["estimate"])),
        1e-12,
    )
    add_estimate_row(
        add,
        winsorized,
        status="direction_stable_diagnostic" if winsor_sign_stable else "direction_unstable",
        gate_result="informational" if winsor_sign_stable else "fail",
        evidence=(
            f"relativeShiftFromPrimary={relative_shift:.3f}; "
            f"actorBootstrap95=[{float(winsorized['lower95']):.3f}, {float(winsorized['upper95']):.3f}]"
        ),
        interpretation=(
            "Within-source-group p95 winsorization does not change the descriptive sign."
            if winsor_sign_stable
            else "Outlier treatment changes the descriptive sign."
        ),
        next_action="Retain actor-level and amount-distribution sensitivity checks in any successor design.",
    )

    leave_estimates = [float(row["leaveOneEstimate"]) for row in leave_one_rows]
    sign_flips = sum(row["signStable"] != "yes" for row in leave_one_rows)
    add(
        "leave_one_actor",
        "leave_one_actor_stability",
        "Leave-one-actor stability",
        "failed" if sign_flips else "direction_stable_diagnostic",
        "fail" if sign_flips else "informational",
        (
            f"omissions={len(leave_one_rows)}; signFlips={sign_flips}; "
            f"minimumEstimate={min(leave_estimates):.3f}; maximumEstimate={max(leave_estimates):.3f}"
        ),
        (
            "At least one actor omission reverses the primary descriptive sign."
            if sign_flips
            else "No single actor omission reverses the descriptive sign."
        ),
        "Increase the treated and comparison cohorts and pre-specify influence diagnostics for high-leverage actors.",
        outcome="log1p quarterly reported activity dollars",
        estimator="leave-one-actor actor-level pre/post contrast",
        pre_window=format_window(PRIMARY_PRE),
        post_window=format_window(PRIMARY_POST),
        estimate=float(primary["estimate"]),
        estimate_exp_percent=float(primary["estimateExpPercent"]),
        lower95=min(leave_estimates),
        upper95=max(leave_estimates),
    )

    failed_gate_ids = [
        row["diagnosticId"]
        for row in rows
        if row["diagnosticFamily"] in {"design_gate", "pretrend", "leave_one_actor"}
        and row["gateResult"] == "fail"
    ]
    if not primary_interval_excludes_zero:
        failed_gate_ids.append("primary_actor_quarter_did")
    if not placebo_magnitude_reassuring:
        failed_gate_ids.append("clean_pre_hloga_2007q2_placebo")
    failed_gate_ids = sorted(set(failed_gate_ids))
    overall_status = OVERALL_NOT_CLEARED if failed_gate_ids else "diagnostic_gates_clear_for_external_review"
    add(
        "overall",
        "overall_effect_model_and_falsification_gate",
        "Overall effect-model and falsification gate",
        overall_status,
        "fail" if failed_gate_ids else "pass",
        f"failedGates={'; '.join(failed_gate_ids) if failed_gate_ids else 'none'}",
        (
            "The current panel does not survive the effect-model and falsification gates. "
            "It can document preparation and descriptive instability, but it cannot estimate substitution or a causal HLOGA effect."
            if failed_gate_ids
            else "The diagnostic gates clear for external methods review, not automatic causal-claim promotion."
        ),
        (
            "Build a longer within-LDA matched-control panel with observed alternate-channel outcomes, then rerun this packet."
            if failed_gate_ids
            else "Obtain independent methods review before changing any claim boundary."
        ),
        outcome="gate synthesis",
        estimator="pre-specified diagnostic gate conjunction",
    )
    return rows


def add_estimate_row(
    add,
    result: dict[str, float | str | tuple[str, ...]],
    *,
    status: str,
    gate_result: str,
    evidence: str,
    interpretation: str,
    next_action: str,
) -> None:
    add(
        str(result["family"]),
        str(result["id"]),
        str(result["label"]),
        status,
        gate_result,
        evidence,
        interpretation,
        next_action,
        outcome="log1p quarterly reported activity dollars",
        estimator="actor-level mean-change difference with actor bootstrap",
        pre_window=format_window(result["pre"]),
        post_window=format_window(result["post"]),
        estimate=float(result["estimate"]),
        estimate_exp_percent=float(result["estimateExpPercent"]),
        lower95=float(result["lower95"]),
        upper95=float(result["upper95"]),
    )


def index_panel(panel_rows: list[dict[str, str]]) -> dict[str, object]:
    amounts: dict[str, dict[str, float]] = defaultdict(dict)
    groups: dict[str, str] = {}
    names: dict[str, str] = {}
    sources: dict[str, str] = {}
    source_outcomes: dict[str, str] = {}
    seen_keys: set[tuple[str, str]] = set()
    for row in panel_rows:
        actor_id = row["canonicalActorId"]
        quarter = row["quarter"]
        key = (actor_id, quarter)
        if key in seen_keys:
            raise ValueError(f"Duplicate estimation-panel key: {actor_id}, {quarter}")
        seen_keys.add(key)
        amounts[actor_id][quarter] = float(row["activityAmountMillions"])
        groups[actor_id] = row["comparisonGroup"]
        names[actor_id] = row["actorName"]
        sources[actor_id] = row["sourceSystem"]
        source_outcomes[actor_id] = row["sourceOutcome"]

    expected_quarters = {quarter.key for quarter in QUARTERS}
    for actor_id, actor_amounts in amounts.items():
        if set(actor_amounts) != expected_quarters:
            missing = sorted(expected_quarters - set(actor_amounts))
            raise ValueError(f"Unbalanced estimation panel for {actor_id}: missing={missing}")
    return {
        "amounts": amounts,
        "groups": groups,
        "names": names,
        "sources": sources,
        "sourceOutcomes": source_outcomes,
    }


def estimate_contrast(
    panel: dict[str, object],
    pre: tuple[str, ...],
    post: tuple[str, ...],
    *,
    bootstrap_reps: int,
    seed: int,
    excluded_actor: str = "",
    winsor_quantile: float | None = None,
) -> dict[str, float]:
    groups: dict[str, str] = panel["groups"]
    actors = [actor for actor in sorted(groups) if actor != excluded_actor]
    transformed = transformed_outcomes(panel, actors, winsor_quantile)
    actor_changes = {
        actor: mean(transformed[actor][quarter] for quarter in post)
        - mean(transformed[actor][quarter] for quarter in pre)
        for actor in actors
    }
    treated_changes = [
        actor_changes[actor] for actor in actors if groups[actor] == TREATED_GROUP
    ]
    control_changes = [
        actor_changes[actor] for actor in actors if groups[actor] == CONTROL_GROUP
    ]
    if not treated_changes or not control_changes:
        raise ValueError("Every contrast requires treated and control actors")
    estimate = mean(treated_changes) - mean(control_changes)
    lower95, upper95 = bootstrap_interval(
        treated_changes,
        control_changes,
        bootstrap_reps,
        seed,
    )
    return {
        "estimate": estimate,
        "estimateExpPercent": exp_percent(estimate),
        "lower95": lower95,
        "upper95": upper95,
        "treatedMeanChange": mean(treated_changes),
        "controlMeanChange": mean(control_changes),
    }


def transformed_outcomes(
    panel: dict[str, object],
    actors: list[str],
    winsor_quantile: float | None,
) -> dict[str, dict[str, float]]:
    amounts: dict[str, dict[str, float]] = panel["amounts"]
    groups: dict[str, str] = panel["groups"]
    thresholds: dict[str, float] = {}
    if winsor_quantile is not None:
        for group in (TREATED_GROUP, CONTROL_GROUP):
            values = sorted(
                amounts[actor][quarter.key]
                for actor in actors
                if groups[actor] == group
                for quarter in QUARTERS
            )
            thresholds[group] = nearest_rank(values, winsor_quantile)
    transformed: dict[str, dict[str, float]] = defaultdict(dict)
    for actor in actors:
        threshold = thresholds.get(groups[actor], math.inf)
        for quarter in QUARTERS:
            amount_millions = min(amounts[actor][quarter.key], threshold)
            transformed[actor][quarter.key] = math.log1p(amount_millions * 1_000_000.0)
    return transformed


def bootstrap_interval(
    treated_changes: list[float],
    control_changes: list[float],
    reps: int,
    seed: int,
) -> tuple[float, float]:
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(reps):
        treated_sample = [rng.choice(treated_changes) for _item in treated_changes]
        control_sample = [rng.choice(control_changes) for _item in control_changes]
        samples.append(mean(treated_sample) - mean(control_sample))
    samples.sort()
    lower_index = max(0, math.ceil(0.025 * reps) - 1)
    upper_index = min(reps - 1, math.ceil(0.975 * reps) - 1)
    return samples[lower_index], samples[upper_index]


def leave_one_actor_rows(
    panel: dict[str, object],
    primary: dict[str, float | str | tuple[str, ...]],
    metadata: dict[str, str],
) -> list[dict[str, str]]:
    groups: dict[str, str] = panel["groups"]
    names: dict[str, str] = panel["names"]
    full_estimate = float(primary["estimate"])
    rows: list[dict[str, str]] = []
    for index, actor in enumerate(sorted(groups)):
        result = estimate_contrast(
            panel,
            PRIMARY_PRE,
            PRIMARY_POST,
            bootstrap_reps=100,
            seed=DEFAULT_SEED + 1_000 + index,
            excluded_actor=actor,
        )
        estimate = result["estimate"]
        stable = sign(estimate) == sign(full_estimate)
        rows.append({
            **metadata,
            "omittedActorId": actor,
            "omittedActorName": names[actor],
            "omittedGroup": groups[actor],
            "fullEstimate": fixed(full_estimate, 6),
            "leaveOneEstimate": fixed(estimate, 6),
            "leaveOneEstimateExpPercent": fixed(exp_percent(estimate), 2),
            "shiftFromFull": fixed(estimate - full_estimate, 6),
            "signStable": "yes" if stable else "no",
            "status": "direction_stable" if stable else "sign_flip",
            "claimBoundary": CLAIM_BOUNDARY,
            "notes": "Leave-one-actor diagnostic only; the full design remains source-confounded.",
        })
    return rows


def event_study_rows(
    panel: dict[str, object],
    metadata: dict[str, str],
) -> list[dict[str, str]]:
    groups: dict[str, str] = panel["groups"]
    actors = sorted(groups)
    transformed = transformed_outcomes(panel, actors, winsor_quantile=None)
    treated = [actor for actor in actors if groups[actor] == TREATED_GROUP]
    controls = [actor for actor in actors if groups[actor] == CONTROL_GROUP]
    baselines = {
        actor: mean(transformed[actor][quarter] for quarter in PRIMARY_PRE)
        for actor in actors
    }
    rows: list[dict[str, str]] = []
    for quarter in QUARTERS:
        treated_mean = mean(transformed[actor][quarter.key] for actor in treated)
        control_mean = mean(transformed[actor][quarter.key] for actor in controls)
        treated_normalized = mean(
            transformed[actor][quarter.key] - baselines[actor]
            for actor in treated
        )
        control_normalized = mean(
            transformed[actor][quarter.key] - baselines[actor]
            for actor in controls
        )
        rows.append({
            **metadata,
            "quarter": quarter.key,
            "eventTimeQuarter": str(quarter.event_time),
            "eventQuarter": "yes" if quarter.key == EVENT_QUARTER else "no",
            "includedInPrimary": "no" if quarter.key == EVENT_QUARTER else "yes",
            "treatedActors": str(len(treated)),
            "controlActors": str(len(controls)),
            "treatedMeanLogActivity": fixed(treated_mean, 6),
            "controlMeanLogActivity": fixed(control_mean, 6),
            "treatedNormalizedFromPre": fixed(treated_normalized, 6),
            "controlNormalizedFromPre": fixed(control_normalized, 6),
            "differenceNormalized": fixed(treated_normalized - control_normalized, 6),
            "claimBoundary": CLAIM_BOUNDARY,
            "notes": (
                "Event quarter is shown descriptively but excluded from the primary contrast because the source period straddles HLOGA."
                if quarter.key == EVENT_QUARTER
                else "Normalized to each actor's 2007Q1-2007Q2 mean; descriptive only."
            ),
        })
    return rows


def write_report(
    path: Path,
    diagnostics: list[dict[str, str]],
    event_rows: list[dict[str, str]],
    leave_one_rows: list[dict[str, str]],
    preparation: dict[str, int | str],
    metadata: dict[str, str],
    panel_path: Path,
    diagnostic_path: Path,
    event_path: Path,
    leave_path: Path,
    figure_path: Path,
    *,
    bootstrap_reps: int,
    bootstrap_seed: int,
) -> None:
    by_id = {row["diagnosticId"]: row for row in diagnostics}
    primary = by_id["primary_actor_quarter_did"]
    overall = by_id["overall_effect_model_and_falsification_gate"]
    placebo = by_id["clean_pre_hloga_2007q2_placebo"]
    leave = by_id["leave_one_actor_stability"]
    window_ids = (
        "primary_actor_quarter_did",
        "balanced_two_quarter_window",
        "calendar_2008_post_window",
        "late_2008_post_window",
        "within_group_p95_winsorized",
        "clean_pre_hloga_2007q2_placebo",
        "post_treatment_2008q2_timing_placebo",
        "post_treatment_2008q3_timing_placebo",
    )
    structural_gate_ids = (
        "treatment_source_system_separation",
        "common_outcome_semantics",
        "actor_issue_unit_comparability",
        "clean_pre_period_depth",
        "independent_clean_placebo_depth",
    )
    sign_flip_rows = [row for row in leave_one_rows if row["signStable"] == "no"]
    figure_relative = figure_path.name if figure_path.parent == path.parent else figure_path.as_posix()

    lines = [
        "# HLOGA Substitution Estimation Diagnostics",
        "",
        "## Technical Summary",
        "",
        f"**Verdict: `{overall['status']}`.** The panel is usable for a reproducible descriptive contrast and for diagnosing why the design fails, but it does not survive the effect-model and falsification gates. The current rows cannot identify a causal HLOGA effect or cross-channel substitution.",
        "",
        f"The primary actor-level contrast is `{primary['estimate']}` log points (mechanically `{signed_percent(primary['estimateExpPercent'])}` after exponentiation), with a deterministic actor-bootstrap 95% interval of `[{primary['lower95']}, {primary['upper95']}]`. The interval crosses zero. More importantly, treatment is perfectly confounded with source and jurisdiction, federal LDA amounts and Colorado lobbyist-income transactions are not the same outcome, the issue taxonomies are not comparable, only two clean pre-treatment quarters exist, the sole clean placebo duplicates the one-step pre-trend contrast, and one actor omission reverses the descriptive sign.",
        "",
        "This packet therefore supports a negative result about design readiness: the source products are ready enough to expose the model's failure modes, not ready enough to estimate substitution.",
        "",
        "## The Descriptive Contrast Is Negative but Not Stable Enough for Inference",
        "",
        f"![Specification contrasts]({figure_relative})",
        "",
        "The figure compares the primary window, alternative windows, p95 winsorization, and timing placebos on the same log-activity scale. The primary bootstrap interval is shown as a horizontal whisker. Window estimates retain the same sign, but the only clean pre-HLOGA placebo is larger and opposite in sign, the primary interval crosses zero, and leave-one-actor results include a sign reversal. These patterns are useful as diagnostics; they do not establish an effect.",
        "",
        "The quarter-by-quarter trajectory is saved as a table rather than a line chart because excluding the HLOGA-straddling quarter leaves only seven clean temporal points, too few for a strong trend visual.",
        "",
        "## Structural Design Gates Fail Before Causal Interpretation",
        "",
        "| Gate | Result | Evidence | Consequence |",
        "| --- | --- | --- | --- |",
    ]
    for diagnostic_id in structural_gate_ids:
        row = by_id[diagnostic_id]
        lines.append(
            f"| {md(row['label'])} | `{row['gateResult']}` | {md(row['evidence'])} | {md(row['interpretation'])} |"
        )

    lines.extend([
        "",
        "The control cohort is an unaffected-jurisdiction source surface, not a matched untreated cohort. Because every treated observation comes from federal LDA and every control observation comes from Colorado state lobbying, source-system changes are mathematically indistinguishable from treatment-group changes. HLOGA also coincides with the LDA shift from semiannual to quarterly filing periods on the treated side, which makes timing comparability especially fragile.",
        "",
        "The panel also lacks treated-actor alternate-channel outcomes. It can compare reported activity trajectories, but it cannot calculate a substitution elasticity because it does not observe where treated actors redirected influence.",
        "",
        "## Scope, Data, and Metric Definitions",
        "",
        f"- Treated cohort: `{preparation['treatedActors']}` exact-name-matched federal LDA clients.",
        f"- Control cohort: `{preparation['controlActors']}` Colorado state-lobbying clients selected for observed pre/post coverage.",
        f"- Analysis grain: balanced actor-quarter panel with `{preparation['panelRows']}` rows.",
        f"- Clean pre window: `{format_window(PRIMARY_PRE)}`.",
        f"- Event quarter: `{EVENT_QUARTER}`, excluded because it contains the September 14, 2007 treatment date.",
        f"- Primary post window: `{format_window(PRIMARY_POST)}`.",
        "- Outcome: `log1p` of quarterly reported activity dollars. This transform reduces scale leverage but does not make the two source definitions equivalent.",
        "- Estimand: mean actor-level post-minus-pre change among treated actors minus the corresponding mean among controls.",
        f"- Prepared panel: `{relative_path(panel_path)}`.",
        "",
        "Absent actor-quarter transactions are represented as zero activity. That produces a balanced computational panel, but it is not proof that every zero is a verified no-activity observation.",
        "",
        "## Filing and Transaction Cleaning Prevents Mechanical Inflation",
        "",
        f"- LDA issue rows: `{preparation['ldaInputRows']}` input rows collapsed to `{preparation['ldaUniqueFilingUuids']}` filing UUIDs; `{preparation['ldaIssueRowsCollapsed']}` repeated issue rows removed from amount aggregation.",
        f"- LDA filing versions: `{preparation['ldaRegistrationFilingsExcluded']}` registration filings excluded and `{preparation['ldaSupersededFilingsExcluded']}` superseded filing versions removed, leaving `{preparation['ldaSelectedFilings']}` selected filings.",
        f"- Colorado transactions: `{preparation['controlRepeatedReceiptRowsExcluded']}` rows in `{preparation['controlRepeatedReceiptKeyGroups']}` repeated receipt-key groups were collapsed from `{preparation['controlInputRows']}` source rows. All `{preparation['controlReportMetadataConflictGroups']}` repeated groups differ in report-month metadata, so the rule prevents likely receipt double counting but is not proof of source-record supersession.",
        "- Semiannual 2007 LDA amounts are allocated to covered quarters in proportion to calendar days. This avoids counting a six-month amount twice, but it does not create independent monthly or quarterly observations.",
        "",
        "## Estimator and Uncertainty",
        "",
        f"For each actor, the script computes the mean transformed outcome in the selected post window minus the mean in the selected pre window. The diagnostic estimate is the treated-group mean change minus the control-group mean change. Uncertainty is summarized with a deterministic actor-level percentile bootstrap that resamples actors within each group. The committed run uses `{bootstrap_reps:,}` repetitions and base seed `{bootstrap_seed}`; specification-specific seeds are deterministic offsets from that base. No p-value is promoted because treatment assignment is not exchangeable across the source-confounded cohorts.",
        "",
        "The event-study table normalizes each actor to its 2007Q1-2007Q2 mean. It includes the event quarter for audit but marks that quarter as excluded from the primary contrast.",
        "",
        "## Falsification and Sensitivity Checks Do Not Clear the Design",
        "",
        "| Check | Pre window | Post window | Estimate | 95% actor bootstrap | Status |",
        "| --- | --- | --- | ---: | --- | --- |",
    ])
    for diagnostic_id in window_ids:
        row = by_id[diagnostic_id]
        lines.append(
            f"| {md(row['label'])} | {md(row['preWindow'])} | {md(row['postWindow'])} | {row['estimate']} | [{row['lower95']}, {row['upper95']}] | `{row['status']}` |"
        )
    lines.extend([
        "",
        f"The sole clean pre-HLOGA placebo is `{placebo['estimate']}` log points, opposite in sign to the primary estimate. It is also numerically the same Q1-to-Q2 contrast used by the one-step pre-trend diagnostic, so it is not independent falsification evidence.",
        "",
        f"Leave-one-actor estimates range from `{leave['lower95']}` to `{leave['upper95']}`. Sign reversals: `{len(sign_flip_rows)}`. "
        + (
            "The sign reversal occurs when omitting "
            + ", ".join(f"`{row['omittedActorName']}`" for row in sign_flip_rows)
            + "."
            if sign_flip_rows
            else "No single omission changes the descriptive sign."
        ),
        "",
        "## What the Current Design Can and Cannot Support",
        "",
        "It can support:",
        "",
        "- an auditable actor-quarter preparation layer over the committed treated and control source rows;",
        "- a descriptive comparison of transformed reported-activity changes across those cohorts;",
        "- concrete evidence that source comparability, pre-period depth, placebo depth, uncertainty, and influence diagnostics remain inadequate;",
        "- prioritization of the next source and design upgrades.",
        "",
        "It cannot support:",
        "",
        "- a claim that HLOGA caused lobbying activity to rise or fall;",
        "- a cross-channel substitution elasticity or a claim that influence moved into a particular alternate venue;",
        "- hidden-channel magnitudes, national prevalence, or representative policy effects;",
        "- calibration of simulator policy-effect parameters from this contrast.",
        "",
        "## Recommended Next Steps",
        "",
        "1. Add unaffected federal LDA actors or provision-level exposure variation so treated and comparison observations share a source and outcome definition.",
        "2. Extend both cohorts backward to provide at least eight clean pre-treatment quarters and multiple uncontaminated placebo dates.",
        "3. Build a reviewed common issue taxonomy and estimate at actor-issue-quarter rather than actor-quarter.",
        "4. Add observed alternate-channel outcomes for the treated actors; without them, the design cannot estimate substitution.",
        "5. Validate LDA filing-version rules and explicitly model the HLOGA-linked change from semiannual to quarterly reporting.",
        "6. Re-run this packet and require every structural, pre-trend, placebo, uncertainty, window, outlier, and leave-one-actor gate to clear before requesting external causal review.",
        "",
        "## Further Questions",
        "",
        "- Which HLOGA provisions generated plausibly heterogeneous exposure among otherwise comparable LDA clients?",
        "- Can unaffected issue families within federal LDA provide a stronger control than a different jurisdiction and source system?",
        "- Which alternate public influence channels can be linked to the same treated actors before and after the reform?",
        "- Can filing amendments be resolved against official supersession identifiers rather than latest-posted heuristics?",
        "",
        "## Regeneration",
        "",
        f"Run `make substitution-estimation-diagnostics substitution-causal-upgrade-packet paper-artifacts-check`. Supporting audit tables are `{relative_path(diagnostic_path)}`, `{relative_path(event_path)}`, and `{relative_path(leave_path)}`.",
        "",
        f"Claim boundary: `{CLAIM_BOUNDARY}`",
        "",
        *metadata_summary_lines(metadata),
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_specification_figure(
    path: Path,
    estimates: dict[str, dict[str, float | str | tuple[str, ...]]],
) -> None:
    selected_ids = (
        "clean_pre_hloga_2007q2_placebo",
        "primary_actor_quarter_did",
        "balanced_two_quarter_window",
        "calendar_2008_post_window",
        "late_2008_post_window",
        "within_group_p95_winsorized",
        "post_treatment_2008q2_timing_placebo",
        "post_treatment_2008q3_timing_placebo",
    )
    rows = [estimates[diagnostic_id] for diagnostic_id in selected_ids]
    primary = estimates["primary_actor_quarter_did"]
    values = [float(row["estimate"]) for row in rows]
    values.extend([float(primary["lower95"]), float(primary["upper95"]), 0.0])
    minimum, maximum = padded_domain(min(values), max(values))
    ticks = nice_ticks(minimum, maximum, count=6)

    width = 1600
    height = 940
    left = 510
    right = 180
    top = 190
    bottom = 125
    plot_width = width - left - right
    plot_height = height - top - bottom
    row_gap = plot_height / max(1, len(rows) - 1)

    def x(value: float) -> float:
        return left + (value - minimum) / (maximum - minimum) * plot_width

    body: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">HLOGA diagnostic specification contrasts</title>",
        "<desc id=\"desc\">Horizontal dot and interval chart of source-confounded actor-level log activity contrasts across the primary, alternative-window, winsorized, and placebo specifications.</desc>",
        "<style>",
        "text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#202124;letter-spacing:0}",
        ".title{font-size:38px;font-weight:700}.subtitle{font-size:21px;fill:#4d5156}",
        ".label{font-size:21px}.value{font-size:19px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}",
        ".tick{font-size:17px;fill:#5f6368;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}",
        ".grid{stroke:#e2e5e9;stroke-width:2}.zero{stroke:#202124;stroke-width:3}",
        ".interval{stroke:#1f5a8a;stroke-width:7;stroke-linecap:round}.cap{stroke:#1f5a8a;stroke-width:4}",
        ".note{font-size:17px;fill:#5f6368}",
        "</style>",
        '<rect x="0" y="0" width="1600" height="940" fill="#ffffff"/>',
        '<text x="72" y="72" class="title">HLOGA diagnostic specification contrasts</text>',
        '<text x="72" y="112" class="subtitle">Actor-level log activity; primary 95% actor-bootstrap interval shown; diagnostic values are not causal effects</text>',
    ]

    for tick in ticks:
        tick_x = x(tick)
        css_class = "zero" if abs(tick) < 1e-12 else "grid"
        body.append(
            f'<line x1="{tick_x:.1f}" y1="{top - 24}" x2="{tick_x:.1f}" y2="{height - bottom + 18}" class="{css_class}"/>'
        )
        body.append(
            f'<text x="{tick_x:.1f}" y="{height - bottom + 54}" text-anchor="middle" class="tick">{tick:+.2f}</text>'
        )

    primary_y = top + selected_ids.index("primary_actor_quarter_did") * row_gap
    low_x = x(float(primary["lower95"]))
    high_x = x(float(primary["upper95"]))
    body.extend([
        f'<line x1="{low_x:.1f}" y1="{primary_y:.1f}" x2="{high_x:.1f}" y2="{primary_y:.1f}" class="interval"/>',
        f'<line x1="{low_x:.1f}" y1="{primary_y - 14:.1f}" x2="{low_x:.1f}" y2="{primary_y + 14:.1f}" class="cap"/>',
        f'<line x1="{high_x:.1f}" y1="{primary_y - 14:.1f}" x2="{high_x:.1f}" y2="{primary_y + 14:.1f}" class="cap"/>',
    ])

    for index, row in enumerate(rows):
        y = top + index * row_gap
        estimate = float(row["estimate"])
        point_x = x(estimate)
        body.append(
            f'<text x="{left - 28}" y="{y + 7:.1f}" text-anchor="end" class="label">{html.escape(str(row["label"]))}</text>'
        )
        if row["kind"] in {"clean_placebo", "contaminated_placebo"}:
            body.append(
                f'<rect x="{point_x - 10:.1f}" y="{y - 10:.1f}" width="20" height="20" fill="#ffffff" stroke="#c17c00" stroke-width="5"/>'
            )
        elif row["kind"] == "outlier":
            body.append(
                f'<circle cx="{point_x:.1f}" cy="{y:.1f}" r="11" fill="#ffffff" stroke="#1f5a8a" stroke-width="5"/>'
            )
        else:
            body.append(
                f'<circle cx="{point_x:.1f}" cy="{y:.1f}" r="11" fill="#1f5a8a" stroke="#153e5f" stroke-width="3"/>'
            )
        body.append(
            f'<text x="{width - 68}" y="{y + 7:.1f}" text-anchor="end" class="value">{estimate:+.3f}</text>'
        )

    body.extend([
        f'<text x="{left + plot_width / 2:.1f}" y="{height - 30}" text-anchor="middle" class="note">Treated mean change minus Colorado-control mean change in log1p reported activity dollars</text>',
        f'<text x="72" y="{height - 30}" class="note">HLOGA event quarter excluded from primary window</text>',
        "</svg>",
        "",
    ])
    path.write_text("\n".join(body), encoding="utf-8")


def register_actor(
    actor_id: str,
    actor_name: str,
    group: str,
    source: str,
    source_outcome: str,
    actor_names: dict[str, Counter[str]],
    actor_groups: dict[str, str],
    actor_sources: dict[str, str],
    actor_outcomes: dict[str, str],
) -> None:
    existing_group = actor_groups.get(actor_id)
    if existing_group and existing_group != group:
        raise ValueError(f"Actor {actor_id} appears in treated and control groups")
    actor_groups[actor_id] = group
    actor_sources[actor_id] = source
    actor_outcomes[actor_id] = source_outcome
    if actor_name:
        actor_names[actor_id][actor_name] += 1


def filing_revision_sort_key(row: dict[str, str]) -> tuple[float, str, str]:
    value = row.get("dtPosted", "")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (ValueError, OverflowError):
        timestamp = float("-inf")
    return timestamp, row.get("filingType", ""), row.get("filingUuid", "")


def overlap_days(start: date, end: date, other_start: date, other_end: date) -> int:
    overlap_start = max(start, other_start)
    overlap_end = min(end, other_end)
    return max(0, (overlap_end - overlap_start).days + 1)


def quarter_for_date(value: date) -> Quarter | None:
    for quarter in QUARTERS:
        if quarter.start <= value <= quarter.end:
            return quarter
    return None


def preferred_name(counter: Counter[str]) -> str:
    if not counter:
        return "missing actor name"
    maximum = max(counter.values())
    return sorted(name for name, count in counter.items() if count == maximum)[0]


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value[:10])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid date: {value!r}") from exc


def required(row: dict[str, str], field: str, context: str) -> str:
    value = row.get(field, "").strip()
    if not value:
        raise ValueError(f"Missing {field} in {context}")
    return value


def nonnegative_float(value: str, context: str) -> float:
    try:
        number = float(value or "0")
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value for {context}: {value!r}") from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"Expected nonnegative finite value for {context}: {value!r}")
    return number


def normalize(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()


def nearest_rank(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("Cannot calculate a quantile of an empty list")
    index = min(len(values) - 1, max(0, math.ceil(quantile * len(values)) - 1))
    return values[index]


def mean(values: Iterable[float]) -> float:
    values_list = list(values)
    if not values_list:
        raise ValueError("Cannot calculate mean of an empty collection")
    return sum(values_list) / len(values_list)


def exp_percent(value: float) -> float:
    try:
        return math.expm1(value) * 100.0
    except OverflowError:
        return math.inf if value > 0 else -100.0


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def padded_domain(minimum: float, maximum: float) -> tuple[float, float]:
    span = maximum - minimum
    if span <= 0:
        span = max(abs(maximum), 1.0)
    padding = span * 0.08
    return minimum - padding, maximum + padding


def nice_ticks(minimum: float, maximum: float, count: int) -> list[float]:
    raw_step = (maximum - minimum) / max(1, count - 1)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10
    step = nice * magnitude
    start = math.ceil(minimum / step) * step
    end = math.floor(maximum / step) * step
    ticks = []
    value = start
    while value <= end + step / 2:
        ticks.append(0.0 if abs(value) < step / 1_000 else value)
        value += step
    return ticks


def format_window(quarters: tuple[str, ...] | object) -> str:
    if not isinstance(quarters, tuple):
        return str(quarters)
    return "; ".join(quarters)


def fixed(value: float, digits: int) -> str:
    return f"{value:.{digits}f}"


def optional_fixed(value: float | None, digits: int) -> str:
    return "" if value is None else fixed(value, digits)


def signed_percent(value: str) -> str:
    return f"{float(value):+.1f}%"


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(
            destination,
            fieldnames=fieldnames,
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
