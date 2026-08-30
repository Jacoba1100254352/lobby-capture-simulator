#!/usr/bin/env python3
"""Promote the reviewed exact-ID slice into first-wave source products.

The entity-resolution seed generator writes broad candidate worklists. This
script runs after the reviewed cross-venue adjudication ledger and replaces the
entity/substitution worklist products with only source-confirmed exact-ID rows.
The promoted products are auditable source rows, but they intentionally do not
clear the broader substitution or venue-shifting gates when row counts,
issue-mapping coverage, or observed pre/post comparison windows are still
insufficient.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUTPUT = ROOT / "data" / "calibration" / "first-wave"
RAW = ROOT / "data" / "raw"
REVIEWER = "codex-source-audit"
DEFAULT_REVIEW_DATE = "2026-06-28"
SUBSTITUTION_REFORM_EVENT_ID = "hloga-2007-federal-lobbying-disclosure"
SNAPSHOT_PERIOD_START = "2024-01-01"
SNAPSHOT_PERIOD_END = "2024-12-31"
HLOGA_PRE_START = "2006-01-01"
HLOGA_PRE_END = "2007-09-13"
HLOGA_POST_START = "2007-09-14"
HLOGA_POST_END = "2008-12-31"
REVIEW_NOTE = (
    "reviewed exact-identifier slice from cross-venue adjudication; broader "
    "source-product, source-readiness, and calibrated policy-simulation gates "
    "remain blocked until row-count, issue-comparability, false-match, and "
    "observed pre/post comparison requirements pass"
)
NOT_OBSERVED = "not_observed_in_reviewed_exact_id_slice"
TAXONOMY_MAPPING_NOTE = (
    "reviewed broad issue-taxonomy crosswalk for comparability only; values "
    "map the reviewed issue domain to source taxonomies and do not imply that "
    "row-level LDA, docket, NAICS, PSC, or FEC records have been observed for "
    "each accepted actor"
)
ISSUE_TAXONOMY_CROSSWALK = {
    "energy": {
        "ldaIssueCode": (
            "ENG Energy/Nuclear; ENV Environmental/Superfund; "
            "FUE Fuel/Gas/Oil; UTI Utilities"
        ),
        "docketTerms": (
            "energy; utilities; electric power; fuel; emissions; "
            "clean air; environmental review"
        ),
        "naicsCodes": (
            "NAICS 22 Utilities; NAICS 2211 Electric Power Generation, "
            "Transmission and Distribution; NAICS 324 Petroleum and Coal "
            "Products Manufacturing"
        ),
        "pscCodes": (
            "PSC S111 Utilities-Gas; PSC S112 Utilities-Electric; "
            "PSC 9140 Fuel Oils"
        ),
        "fecPurposeTerms": (
            "purpose text terms: energy; utility; climate; environment; "
            "clean energy"
        ),
    },
    "finance": {
        "ldaIssueCode": (
            "FIN Financial Institutions/Investments/Securities; "
            "BAN Banking; INS Insurance"
        ),
        "docketTerms": (
            "banking; securities; consumer finance; insurance; "
            "financial regulation"
        ),
        "naicsCodes": (
            "NAICS 52 Finance and Insurance; NAICS 522 Credit "
            "Intermediation; NAICS 523 Securities, Commodity Contracts, "
            "and Other Financial Investments"
        ),
        "pscCodes": "PSC R710 Financial Services",
        "fecPurposeTerms": (
            "purpose text terms: banking; finance; securities; insurance; "
            "credit"
        ),
    },
    "procurement": {
        "ldaIssueCode": (
            "GOV Government Issues; BUD Budget/Appropriations; DEF Defense"
        ),
        "docketTerms": (
            "procurement; acquisition; FAR; contractor responsibility; "
            "source selection; competition"
        ),
        "naicsCodes": (
            "cross-industry procurement vendor NAICS; seed review terms: "
            "NAICS 5416 Management, Scientific, and Technical Consulting "
            "Services; NAICS 5415 Computer Systems Design and Related "
            "Services; NAICS 5612 Facilities Support Services"
        ),
        "pscCodes": (
            "PSC R707 Contract/Procurement/Acquisition Support; "
            "PSC R499 Other Professional Services"
        ),
        "fecPurposeTerms": (
            "purpose text terms: procurement; contracting; acquisition; "
            "government services; defense contract"
        ),
    },
    "technology": {
        "ldaIssueCode": (
            "CPI Computer Industry; TEC Telecommunications; "
            "SCI Science/Technology; CPT Copyright/Patent/Trademark"
        ),
        "docketTerms": (
            "telecommunications; broadband; cybersecurity; software; "
            "standards; spectrum; data security"
        ),
        "naicsCodes": (
            "NAICS 517 Telecommunications; NAICS 518 Computing "
            "Infrastructure Providers, Data Processing, Web Hosting, and "
            "Related Services; NAICS 5415 Computer Systems Design and "
            "Related Services; NAICS 334 Computer and Electronic Product "
            "Manufacturing"
        ),
        "pscCodes": (
            "PSC D399 IT and Telecom - Other IT and Telecommunications; "
            "PSC 7A20 IT and Telecom - Application Development Software"
        ),
        "fecPurposeTerms": (
            "purpose text terms: technology; telecom; cybersecurity; "
            "software; internet"
        ),
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--review-date", default=DEFAULT_REVIEW_DATE)
    args = parser.parse_args()

    reports = args.reports if args.reports.is_absolute() else ROOT / args.reports
    output = args.output if args.output.is_absolute() else ROOT / args.output
    raw = args.raw if args.raw.is_absolute() else ROOT / args.raw
    adjudication_rows = read_csv(reports / "first-wave-cross-venue-adjudication.csv")
    record_rows = read_csv(reports / "first-wave-cross-venue-adjudication-records.csv")
    source_index = source_period_index(raw)
    historical_lda_rows = read_csv(output / "substitution-historical-lda-panel.csv")
    state_control_rows = read_csv(output / "substitution-state-lobbying-control-panel.csv")

    accepted = [row for row in adjudication_rows if row.get("promotedToReviewedPanel") == "yes"]
    accepted_by_actor = {row["candidateActorId"]: row for row in accepted}
    accepted_records = [
        row
        for row in record_rows
        if row.get("recordDecision") == "reviewed_accept"
        and row.get("candidateActorId") in accepted_by_actor
    ]
    negative_records = [
        row
        for row in record_rows
        if row.get("recordDecision") in {
            "reviewed_reject_from_cross_venue_panel",
            "held_for_manual_review",
        }
    ]

    output.mkdir(parents=True, exist_ok=True)
    products = {
        "canonical-actor-identifiers.csv": canonical_actor_rows(
            accepted,
            accepted_records,
            state_control_rows,
            args.review_date,
        ),
        "alias-resolution-audit-sample.csv": alias_rows(accepted_by_actor, accepted_records, negative_records, args.review_date),
        "issue-code-crosswalk.csv": issue_rows(accepted, args.review_date),
        "false-match-review-log.csv": false_match_rows(accepted_records, negative_records, args.review_date),
        "linked-actor-issue-venue-time.csv": linked_rows(
            accepted_records,
            source_index,
            historical_lda_rows,
            state_control_rows,
        ),
        "actor-issue-time-spine.csv": actor_issue_time_rows(
            accepted_records,
            source_index,
            historical_lda_rows,
            state_control_rows,
        ),
        "substitution-comparison-groups.csv": comparison_rows(
            accepted,
            accepted_records,
            historical_lda_rows,
            state_control_rows,
        ),
    }
    for filename, rows in products.items():
        write_csv(output / filename, rows)
        print(f"Wrote {output / filename}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_period_index(raw: Path) -> dict[str, dict[tuple[str, str, str], str]]:
    return {
        "usaspending-procurement-actions.csv": usaspending_action_dates(
            raw / "usaspending-procurement-actions.csv"
        ),
    }


def usaspending_action_dates(path: Path) -> dict[tuple[str, str, str], str]:
    rows = read_csv(path)
    index: dict[tuple[str, str, str], str] = {}
    for row in rows:
        piid = row.get("piid", "").strip()
        award_id = row.get("awardId", "").strip()
        uei = row.get("uei", "").strip()
        action_date = row.get("actionDate", "").strip()
        if piid and award_id and uei and action_date:
            index[(piid, award_id, uei)] = action_date
    return index


def canonical_actor_rows(
    accepted: list[dict[str, str]],
    accepted_records: list[dict[str, str]],
    state_control_rows: list[dict[str, str]],
    review_date: str,
) -> list[dict[str, str]]:
    records_by_actor = group_by(accepted_records, "candidateActorId")
    rows: list[dict[str, str]] = []
    for actor in sorted(accepted, key=lambda row: row.get("primaryName", "")):
        actor_id = actor.get("candidateActorId", "")
        records = records_by_actor.get(actor_id, [])
        ein = confirmed_ein(actor)
        ueis = sorted({uei for record in records for uei in record_ueis(record)})
        rows.append(
            {
                "canonicalActorId": actor_id,
                "primaryName": actor.get("primaryName", actor.get("normalizedName", "")),
                "actorType": actor_type(actor),
                "ldaClientId": NOT_OBSERVED,
                "fecCommitteeId": NOT_OBSERVED,
                "uei": "; ".join(ueis) if ueis else NOT_OBSERVED,
                "docketSubmitterId": NOT_OBSERVED,
                "intermediaryId": ein or NOT_OBSERVED,
                "sourceSystems": actor.get("sourceSystems", ""),
                "parentActorId": "not_reviewed_for_parent_subsidiary_scope",
                "country": "not_reviewed_for_jurisdiction_scope",
                "state": "not_reviewed_for_jurisdiction_scope",
                "reviewStatus": "reviewed_exact_identifier_match",
                "reviewer": REVIEWER,
                "reviewDate": review_date,
                "confirmedIdentifiers": actor.get("confirmedIdentifiers", ""),
                "evidenceRule": actor.get("evidenceRule", ""),
                "confidenceScore": actor.get("confidenceScore", ""),
                "notes": REVIEW_NOTE,
            }
        )
    rows.extend(canonical_state_control_actor_rows(state_control_rows, review_date))
    return rows


def canonical_state_control_actor_rows(
    state_control_rows: list[dict[str, str]],
    review_date: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for source_row in sorted(state_control_rows, key=lambda row: row.get("primaryName", "")):
        if source_row.get("reviewStatus") != "reviewed_official_state_lobbying_control_source_row":
            continue
        actor_id = source_row.get("canonicalActorId", "")
        if not actor_id or actor_id in seen:
            continue
        seen.add(actor_id)
        rows.append(
            {
                "canonicalActorId": actor_id,
                "primaryName": source_row.get("primaryName", ""),
                "actorType": "official_state_lobbying_control_client",
                "ldaClientId": NOT_OBSERVED,
                "fecCommitteeId": NOT_OBSERVED,
                "uei": NOT_OBSERVED,
                "docketSubmitterId": NOT_OBSERVED,
                "intermediaryId": source_row.get("stateClientKey", NOT_OBSERVED),
                "sourceSystems": source_row.get("sourceSystem", "Colorado Secretary of State lobbyist income data"),
                "parentActorId": "not_reviewed_for_parent_subsidiary_scope",
                "country": "United States",
                "state": "Colorado",
                "reviewStatus": "reviewed_official_state_lobbying_control_actor",
                "reviewer": REVIEWER,
                "reviewDate": review_date,
                "confirmedIdentifiers": "Colorado state lobbying client key=" + source_row.get("stateClientKey", ""),
                "evidenceRule": "official-colorado-state-lobbying-income-client-key",
                "confidenceScore": source_row.get("matchConfidence", "0.7000"),
                "notes": (
                    "official Colorado state-lobbying control actor derived from "
                    "reviewed source rows with observed pre/post HLOGA-window state "
                    "lobbying income; unaffected-jurisdiction control surface only"
                ),
            }
        )
    return rows


def alias_rows(
    accepted_by_actor: dict[str, dict[str, str]],
    accepted_records: list[dict[str, str]],
    negative_records: list[dict[str, str]],
    review_date: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in accepted_records:
        actor = accepted_by_actor[record.get("candidateActorId", "")]
        rows.append(
            alias_row(
                len(rows) + 1,
                record,
                actor.get("decision", ""),
                "accepted_exact_identifier_match",
                "reviewed source-native identifier match promoted from adjudication ledger",
                actor.get("confidenceScore", "0.9000"),
                review_date,
            )
        )
    for record in negative_records[:50]:
        rows.append(
            alias_row(
                len(rows) + 1,
                record,
                record.get("actorDecision", ""),
                "rejected_or_held_not_panel_match",
                "not promoted by the cross-venue adjudication rule; retained as false-match boundary evidence",
                record.get("confidenceScore", "0.0000"),
                review_date,
            )
        )
    return rows


def alias_row(
    index: int,
    record: dict[str, str],
    actor_decision: str,
    manual_decision: str,
    notes: str,
    confidence: str,
    review_date: str,
) -> dict[str, str]:
    return {
        "auditId": f"alias-reviewed-{index:04d}",
        "canonicalActorId": record.get("candidateActorId", ""),
        "aliasName": record.get("displayName", ""),
        "sourceSystem": record.get("sourceSystem", ""),
        "sourceRecordId": record.get("sourceRecordId", ""),
        "matchRule": record.get("matchRule", "normalized-name-exact"),
        "manualDecision": manual_decision,
        "reviewer": REVIEWER,
        "reviewDate": review_date,
        "confidenceScore": confidence,
        "reviewStatus": "reviewed",
        "actorDecision": actor_decision,
        "notes": f"{notes}; {REVIEW_NOTE}",
    }


def issue_rows(accepted: list[dict[str, str]], review_date: str) -> list[dict[str, str]]:
    source_systems_by_issue: dict[str, set[str]] = defaultdict(set)
    for actor in accepted:
        systems = split_semicolon(actor.get("sourceSystems", ""))
        for issue in split_semicolon(actor.get("issueDomains", "")):
            source_systems_by_issue[normalize_issue(issue)].update(systems)
    rows = []
    for issue in sorted(source_systems_by_issue):
        if not issue:
            continue
        mapping = ISSUE_TAXONOMY_CROSSWALK.get(issue, {})
        rows.append(
            {
                "issueCode": issue_code(issue),
                "ldaIssueCode": mapping.get("ldaIssueCode", NOT_OBSERVED),
                "policyDomain": issue,
                "docketTerms": mapping.get("docketTerms", NOT_OBSERVED),
                "naicsCodes": mapping.get("naicsCodes", NOT_OBSERVED),
                "pscCodes": mapping.get("pscCodes", NOT_OBSERVED),
                "fecPurposeTerms": mapping.get("fecPurposeTerms", NOT_OBSERVED),
                "notes": (
                    f"{REVIEW_NOTE}; {TAXONOMY_MAPPING_NOTE}; "
                    "taxonomy anchors reviewed against LDA issue-code, "
                    "Regulations.gov/Federal Register docket-term, Census "
                    "NAICS, Acquisition.gov PSC, and FEC purpose-text source "
                    "families; reviewed source systems for this issue: "
                    f"{'; '.join(sorted(source_systems_by_issue[issue]))}"
                ),
                "reviewer": REVIEWER,
                "reviewDate": review_date,
                "reviewStatus": "reviewed_issue_taxonomy_crosswalk_from_exact_id_slice",
                "sourceSystems": "; ".join(sorted(source_systems_by_issue[issue])),
            }
        )
    return rows


def false_match_rows(
    accepted_records: list[dict[str, str]],
    negative_records: list[dict[str, str]],
    review_date: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in accepted_records[:50]:
        rows.append(
            false_match_row(
                len(rows) + 1,
                record,
                "accepted",
                "true_positive_exact_identifier",
                "accepted exact-ID cross-venue evidence; not a causal panel clearance",
                record.get("confidenceScore", "0.9000"),
                review_date,
            )
        )
    for record in negative_records[:50]:
        decision = record.get("recordDecision", "")
        error_type = (
            "false_positive_same_venue_candidate"
            if decision == "reviewed_reject_from_cross_venue_panel"
            else "held_identifier_evidence_incomplete"
        )
        rows.append(
            false_match_row(
                len(rows) + 1,
                record,
                "rejected",
                error_type,
                "not promoted by reviewed cross-venue adjudication; retained to bound linkage risk",
                record.get("confidenceScore", "0.0000"),
                review_date,
            )
        )
    return rows


def false_match_row(
    index: int,
    record: dict[str, str],
    decision: str,
    error_type: str,
    notes: str,
    confidence: str,
    review_date: str,
) -> dict[str, str]:
    return {
        "reviewId": f"false-match-reviewed-{index:04d}",
        "canonicalActorId": record.get("candidateActorId", ""),
        "candidateRecordId": record.get("sourceRecordId", ""),
        "sourceSystem": record.get("sourceSystem", ""),
        "issueCode": issue_code(record.get("issueDomain", "")),
        "decision": decision,
        "errorType": error_type,
        "notes": f"{notes}; {REVIEW_NOTE}",
        "reviewer": REVIEWER,
        "reviewDate": review_date,
        "confidenceScore": confidence,
    }


def linked_rows(
    accepted_records: list[dict[str, str]],
    source_index: dict[str, dict[tuple[str, str, str], str]],
    historical_lda_rows: list[dict[str, str]],
    state_control_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in accepted_records:
        period_start, period_end, period_note = source_period(record, source_index)
        rows.append(
            {
                "canonicalActorId": record.get("candidateActorId", ""),
                "issueCode": issue_code(record.get("issueDomain", "")),
                "venue": record.get("venue", ""),
                "periodStart": period_start,
                "periodEnd": period_end,
                "activityType": activity_type(record),
                "activityMeasure": numeric_or_zero(record.get("activityAmount", "")),
                "sourceSystem": record.get("sourceSystem", ""),
                "sourceRecordId": record.get("sourceRecordId", ""),
                "matchConfidence": record.get("confidenceScore", "0.9000"),
                "activityAmount": numeric_or_zero(record.get("activityAmount", "")),
                "jurisdiction": "source_snapshot",
                "reviewStatus": "reviewed_exact_identifier_link",
                "notes": f"{REVIEW_NOTE}; {period_note}",
            }
        )
    rows.extend(linked_lda_rows(historical_lda_rows))
    rows.extend(linked_state_control_rows(state_control_rows))
    return rows


def actor_issue_time_rows(
    accepted_records: list[dict[str, str]],
    source_index: dict[str, dict[tuple[str, str, str], str]],
    historical_lda_rows: list[dict[str, str]],
    state_control_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in accepted_records:
        period_start, period_end, period_note = source_period(record, source_index)
        rows.append(
            {
                "canonicalActorId": record.get("candidateActorId", ""),
                "issueCode": issue_code(record.get("issueDomain", "")),
                "periodStart": period_start,
                "periodEnd": period_end,
                "venue": record.get("venue", ""),
                "activityType": activity_type(record),
                "activityMeasure": numeric_or_zero(record.get("activityAmount", "")),
                "activityAmount": numeric_or_zero(record.get("activityAmount", "")),
                "sourceSystem": record.get("sourceSystem", ""),
                "sourceRecordId": record.get("sourceRecordId", ""),
                "exposureGroup": "unassigned_reviewed_exact_id_slice",
                "reformEventId": SUBSTITUTION_REFORM_EVENT_ID,
                "activityUnits": "normalized_source_amount",
                "jurisdiction": "source_snapshot",
                "matchConfidence": record.get("confidenceScore", "0.9000"),
                "reviewStatus": "reviewed_exact_identifier_link",
                "notes": f"{REVIEW_NOTE}; {period_note}; exposure group and observed pre/post outcome movement remain unresolved",
            }
        )
    rows.extend(actor_issue_time_lda_rows(historical_lda_rows))
    rows.extend(actor_issue_time_state_control_rows(state_control_rows))
    return rows


def linked_lda_rows(historical_lda_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_row in historical_lda_rows:
        if source_row.get("reviewStatus") != "reviewed_exact_lda_client_name_source_row":
            continue
        rows.append(
            {
                "canonicalActorId": source_row.get("canonicalActorId", ""),
                "issueCode": source_row.get("issueCode", ""),
                "venue": source_row.get("venue", "visible_lobbying"),
                "periodStart": source_row.get("periodStart", ""),
                "periodEnd": source_row.get("periodEnd", ""),
                "activityType": source_row.get("activityType", "visible_lobbying_filing"),
                "activityMeasure": source_row.get("activityMeasure", "1.0000"),
                "sourceSystem": source_row.get("sourceSystem", "Official LDA API"),
                "sourceRecordId": source_row.get("sourceRecordId", ""),
                "matchConfidence": source_row.get("matchConfidence", "0.8000"),
                "activityAmount": source_row.get("activityAmount", "0.0000"),
                "jurisdiction": source_row.get("jurisdiction", "United States federal"),
                "reviewStatus": source_row.get("reviewStatus", ""),
                "notes": source_row.get("notes", ""),
            }
        )
    return rows


def actor_issue_time_lda_rows(historical_lda_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_row in historical_lda_rows:
        if source_row.get("reviewStatus") != "reviewed_exact_lda_client_name_source_row":
            continue
        rows.append(
            {
                "canonicalActorId": source_row.get("canonicalActorId", ""),
                "issueCode": source_row.get("issueCode", ""),
                "periodStart": source_row.get("periodStart", ""),
                "periodEnd": source_row.get("periodEnd", ""),
                "venue": source_row.get("venue", "visible_lobbying"),
                "activityType": source_row.get("activityType", "visible_lobbying_filing"),
                "activityMeasure": source_row.get("activityMeasure", "1.0000"),
                "activityAmount": source_row.get("activityAmount", "0.0000"),
                "sourceSystem": source_row.get("sourceSystem", "Official LDA API"),
                "sourceRecordId": source_row.get("sourceRecordId", ""),
                "exposureGroup": source_row.get("exposureGroup", "treated_hloga_lda_client"),
                "reformEventId": source_row.get("reformEventId", SUBSTITUTION_REFORM_EVENT_ID),
                "activityUnits": source_row.get("activityUnits", "filing_count; amount_millions"),
                "jurisdiction": source_row.get("jurisdiction", "United States federal"),
                "matchConfidence": source_row.get("matchConfidence", "0.8000"),
                "reviewStatus": source_row.get("reviewStatus", ""),
                "notes": source_row.get("notes", ""),
            }
        )
    return rows


def linked_state_control_rows(state_control_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_row in state_control_rows:
        if source_row.get("reviewStatus") != "reviewed_official_state_lobbying_control_source_row":
            continue
        rows.append(
            {
                "canonicalActorId": source_row.get("canonicalActorId", ""),
                "issueCode": source_row.get("issueCode", ""),
                "venue": source_row.get("venue", "state_lobbying"),
                "periodStart": source_row.get("periodStart", ""),
                "periodEnd": source_row.get("periodEnd", ""),
                "activityType": source_row.get("activityType", "state_lobbying_income"),
                "activityMeasure": source_row.get("activityMeasure", "0.0000"),
                "sourceSystem": source_row.get("sourceSystem", "Colorado Secretary of State lobbyist income data"),
                "sourceRecordId": source_row.get("sourceRecordId", ""),
                "matchConfidence": source_row.get("matchConfidence", "0.7000"),
                "activityAmount": source_row.get("activityAmount", "0.0000"),
                "jurisdiction": source_row.get("jurisdiction", "Colorado state"),
                "reviewStatus": source_row.get("reviewStatus", ""),
                "notes": source_row.get("notes", ""),
            }
        )
    return rows


def actor_issue_time_state_control_rows(state_control_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_row in state_control_rows:
        if source_row.get("reviewStatus") != "reviewed_official_state_lobbying_control_source_row":
            continue
        rows.append(
            {
                "canonicalActorId": source_row.get("canonicalActorId", ""),
                "issueCode": source_row.get("issueCode", ""),
                "periodStart": source_row.get("periodStart", ""),
                "periodEnd": source_row.get("periodEnd", ""),
                "venue": source_row.get("venue", "state_lobbying"),
                "activityType": source_row.get("activityType", "state_lobbying_income"),
                "activityMeasure": source_row.get("activityMeasure", "0.0000"),
                "activityAmount": source_row.get("activityAmount", "0.0000"),
                "sourceSystem": source_row.get("sourceSystem", "Colorado Secretary of State lobbyist income data"),
                "sourceRecordId": source_row.get("sourceRecordId", ""),
                "exposureGroup": source_row.get("exposureGroup", "control_unaffected_colorado_state_lobbying_jurisdiction"),
                "reformEventId": source_row.get("reformEventId", SUBSTITUTION_REFORM_EVENT_ID),
                "activityUnits": source_row.get("activityUnits", "income_dollars; amount_millions"),
                "jurisdiction": source_row.get("jurisdiction", "Colorado state"),
                "matchConfidence": source_row.get("matchConfidence", "0.7000"),
                "reviewStatus": source_row.get("reviewStatus", ""),
                "notes": source_row.get("notes", ""),
            }
        )
    return rows


def source_period(
    record: dict[str, str],
    source_index: dict[str, dict[tuple[str, str, str], str]],
) -> tuple[str, str, str]:
    if record.get("sourceFile") == "usaspending-procurement-actions.csv":
        parts = record.get("sourceRecordId", "").split("|")
        if len(parts) >= 3:
            key = (parts[0].strip(), parts[1].strip(), parts[2].strip())
            action_date = source_index.get("usaspending-procurement-actions.csv", {}).get(key, "")
            if action_date:
                return (
                    action_date,
                    action_date,
                    "period is observed USAspending actionDate for this reviewed procurement row; not HLOGA pre/post movement",
                )
    return (
        SNAPSHOT_PERIOD_START,
        SNAPSHOT_PERIOD_END,
        "period is normalized source snapshot coverage, not observed pre/post movement",
    )


def comparison_rows(
    accepted: list[dict[str, str]],
    accepted_records: list[dict[str, str]],
    historical_lda_rows: list[dict[str, str]],
    state_control_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    record_issues_by_actor: dict[str, set[str]] = defaultdict(set)
    venues_by_actor: dict[str, set[str]] = defaultdict(set)
    systems_by_actor: dict[str, set[str]] = defaultdict(set)
    for record in accepted_records:
        actor = record.get("candidateActorId", "")
        record_issues_by_actor[actor].add(issue_code(record.get("issueDomain", "")))
        venues_by_actor[actor].add(record.get("venue", ""))
        systems_by_actor[actor].add(record.get("sourceSystem", ""))
    historical = historical_lda_prepost_summary(historical_lda_rows)
    for actor_id, issues in historical.items():
        record_issues_by_actor[actor_id].update(issues)
        venues_by_actor[actor_id].add("visible_lobbying")
        systems_by_actor[actor_id].add("Official LDA API")
    state_controls = state_lobbying_control_prepost_summary(state_control_rows)
    for actor_id, issues in state_controls.items():
        record_issues_by_actor[actor_id].update(issues)
        venues_by_actor[actor_id].add("state_lobbying")
        systems_by_actor[actor_id].add("Colorado Secretary of State lobbyist income data")
    rows: list[dict[str, str]] = []
    for actor in sorted(accepted, key=lambda row: row.get("primaryName", "")):
        actor_id = actor.get("candidateActorId", "")
        for issue in sorted(record_issues_by_actor.get(actor_id) or {issue_code("")}):
            if issue in historical.get(actor_id, set()):
                rows.append(
                    {
                        "reformEventId": SUBSTITUTION_REFORM_EVENT_ID,
                        "canonicalActorId": actor_id,
                        "issueCode": issue,
                        "comparisonGroup": "treated_hloga_lda_client",
                        "matchingVariables": (
                            "official LDA API exact normalized client-name match; "
                            "visible-lobbying pre/post rows observed; comparison/control "
                            "assignment remains unresolved"
                        ),
                        "prePeriodStart": HLOGA_PRE_START,
                        "prePeriodEnd": HLOGA_PRE_END,
                        "postPeriodStart": HLOGA_POST_START,
                        "postPeriodEnd": HLOGA_POST_END,
                        "matchScore": "0.8000",
                        "exclusionReason": "",
                        "reviewStatus": "reviewed_treated_visible_lobbying_prepost",
                        "notes": (
                            f"{REVIEW_NOTE}; treated visible-lobbying assignment comes "
                            "from official LDA API pre/post rows matched by exact "
                            "normalized client name; matched comparison/control actors "
                            "are still required before estimation"
                        ),
                    }
                )
                continue
            rows.append(
                {
                    "reformEventId": SUBSTITUTION_REFORM_EVENT_ID,
                    "canonicalActorId": actor_id,
                    "issueCode": issue,
                    "comparisonGroup": "excluded_no_observed_prepost_window",
                    "matchingVariables": (
                        "reviewed exact-ID source systems="
                        f"{'; '.join(sorted(systems_by_actor.get(actor_id, [])))}; "
                        "venues="
                        f"{'; '.join(sorted(venues_by_actor.get(actor_id, [])))}"
                    ),
                    "prePeriodStart": HLOGA_PRE_START,
                    "prePeriodEnd": HLOGA_PRE_END,
                    "postPeriodStart": HLOGA_POST_START,
                    "postPeriodEnd": HLOGA_POST_END,
                    "matchScore": actor.get("confidenceScore", "0.9000"),
                    "exclusionReason": "observed_prepost_outcome_rows_missing",
                    "reviewStatus": "reviewed_actor_excluded_from_estimation_panel",
                    "notes": f"{REVIEW_NOTE}; not assigned to treated or comparison group",
                }
            )
    for actor_id, issues in sorted(state_controls.items()):
        for issue in sorted(issues):
            rows.append(
                {
                    "reformEventId": SUBSTITUTION_REFORM_EVENT_ID,
                    "canonicalActorId": actor_id,
                    "issueCode": issue,
                    "comparisonGroup": "control_unaffected_colorado_state_lobbying_jurisdiction",
                    "matchingVariables": (
                        "official Colorado Secretary of State lobbyist-income source rows; "
                        "unaffected state-jurisdiction control for federal HLOGA shock; "
                        "pre/post rows observed for same state lobbying client and source-derived issue"
                    ),
                    "prePeriodStart": HLOGA_PRE_START,
                    "prePeriodEnd": HLOGA_PRE_END,
                    "postPeriodStart": HLOGA_POST_START,
                    "postPeriodEnd": HLOGA_POST_END,
                    "matchScore": "0.6500",
                    "exclusionReason": "",
                    "reviewStatus": "reviewed_control_unaffected_state_lobbying_prepost",
                    "notes": (
                        "control assignment comes from official Colorado state-lobbying "
                        "income rows with observed pre/post HLOGA-window coverage; "
                        "it is an unaffected-jurisdiction control surface, not proof "
                        "that the client lacks separate federal LDA exposure"
                    ),
                }
            )
    return rows


def historical_lda_prepost_summary(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    coverage: dict[tuple[str, str], dict[str, bool]] = defaultdict(lambda: {"pre": False, "post": False})
    for row in rows:
        if row.get("reformEventId") != SUBSTITUTION_REFORM_EVENT_ID:
            continue
        actor = row.get("canonicalActorId", "")
        issue = row.get("issueCode", "")
        if not actor or not issue:
            continue
        period_start = row.get("periodStart", "")
        period_end = row.get("periodEnd", "")
        if period_end and period_end < HLOGA_POST_START:
            coverage[(actor, issue)]["pre"] = True
        if period_start and period_start >= HLOGA_POST_START:
            coverage[(actor, issue)]["post"] = True
    ready: dict[str, set[str]] = defaultdict(set)
    for (actor, issue), flags in coverage.items():
        if flags["pre"] and flags["post"]:
            ready[actor].add(issue)
    return dict(ready)


def state_lobbying_control_prepost_summary(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    coverage: dict[tuple[str, str], dict[str, bool]] = defaultdict(lambda: {"pre": False, "post": False})
    for row in rows:
        if row.get("reformEventId") != SUBSTITUTION_REFORM_EVENT_ID:
            continue
        if row.get("reviewStatus") != "reviewed_official_state_lobbying_control_source_row":
            continue
        actor = row.get("canonicalActorId", "")
        issue = row.get("issueCode", "")
        if not actor or not issue:
            continue
        period_start = row.get("periodStart", "")
        period_end = row.get("periodEnd", "")
        if period_end and period_end < HLOGA_POST_START:
            coverage[(actor, issue)]["pre"] = True
        if period_start and period_start >= HLOGA_POST_START:
            coverage[(actor, issue)]["post"] = True
    ready: dict[str, set[str]] = defaultdict(set)
    for (actor, issue), flags in coverage.items():
        if flags["pre"] and flags["post"]:
            ready[actor].add(issue)
    return dict(ready)


def group_by(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get(field, "")].append(row)
    return grouped


def confirmed_ein(actor: dict[str, str]) -> str:
    match = re.search(r"\bEIN=([^;]+)", actor.get("confirmedIdentifiers", ""))
    return match.group(1).strip() if match else ""


def record_ueis(record: dict[str, str]) -> list[str]:
    if "USAspending" not in record.get("sourceSystem", ""):
        return []
    ueis: list[str] = []
    for part in record.get("sourceRecordId", "").split(";"):
        pieces = part.split("|")
        if len(pieces) >= 3 and pieces[2].strip():
            ueis.append(pieces[2].strip())
    return ueis


def actor_type(actor: dict[str, str]) -> str:
    venues = set(split_semicolon(actor.get("reviewedVenues", "")))
    if "procurement" in venues:
        return "reviewed_nonprofit_intermediary_with_procurement_link"
    return "reviewed_nonprofit_or_intermediary"


def activity_type(record: dict[str, str]) -> str:
    source = record.get("sourceSystem", "")
    if "dark-money" in source.lower() or "irs/propublica" in source.lower():
        return "opaque_nonprofit_capacity"
    if "intermediary" in source.lower():
        return "intermediary_capacity"
    if "usaspending" in source.lower():
        return "procurement_action"
    return "source_activity"


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def normalize_issue(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def issue_code(value: str) -> str:
    normalized = normalize_issue(value)
    if not normalized:
        return "reviewed-unclassified"
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return f"reviewed-{slug or 'unclassified'}"


def numeric_or_zero(value: str) -> str:
    try:
        return f"{float(value or 0):.4f}"
    except ValueError:
        return "0.0000"


if __name__ == "__main__":
    raise SystemExit(main())
