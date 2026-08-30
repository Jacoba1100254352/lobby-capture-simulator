#!/usr/bin/env python3
"""Write a reviewed cross-venue adjudication ledger for first-wave candidates.

This is an evidence ledger, not a source-product promotion script. It records
which automated candidate links have enough source-native identifier support to
enter a reviewed cross-venue slice while preserving the broader source-product
and claim gates until the full panel clears row-count, venue, issue, false-match,
and pre/post comparison requirements.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paper_release_metadata import (
    RELEASE_METADATA_FIELDS,
    metadata_summary_lines,
    release_metadata,
    with_release_metadata,
)


ROOT = Path(".")
REPORTS = Path("reports")
RAW = Path("data") / "raw"
OUTPUT_CSV = "first-wave-cross-venue-adjudication.csv"
OUTPUT_RECORDS_CSV = "first-wave-cross-venue-adjudication-records.csv"
OUTPUT_MD = "first-wave-cross-venue-adjudication.md"
REVIEWER = "codex-source-audit"
DEFAULT_REVIEW_DATE = "2026-06-28"
ACCEPTED_DECISIONS = {
    "accepted_exact_ein_cross_venue_reviewed",
    "accepted_exact_ein_plus_procurement_identifier_reviewed",
}
POLICY_BOUNDARY = (
    "reviewed identifier evidence only; does not clear source-product, "
    "ready-to-estimate, causal substitution, venue-shifting, or calibrated "
    "policy-simulation claims"
)
ESTIMATION_NEXT_ACTION = (
    "Keep candidate seed products blocked, expand reviewed rows until source-product "
    "minimums and semantic gates pass, adjudicate issue comparability and false "
    "matches, then replace synthetic HLOGA comparison windows with observed "
    "pre/post source rows before estimating substitution."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument(
        "--review-date",
        default=os.environ.get("FIRST_WAVE_ADJUDICATION_REVIEW_DATE", DEFAULT_REVIEW_DATE),
    )
    args = parser.parse_args()

    root = args.root
    reports = args.reports if args.reports.is_absolute() else root / args.reports
    raw = args.raw if args.raw.is_absolute() else root / args.raw
    candidates = read_csv(reports / "first-wave-linkage-candidates.csv")
    record_rows = read_csv(reports / "first-wave-linkage-candidate-records.csv")
    records_by_actor = grouped_records(record_rows)
    indexes = raw_indexes(raw)

    metadata = release_metadata()
    adjudicated = [
        adjudication_row(candidate, records_by_actor.get(candidate.get("candidateActorId", ""), []), indexes, args.review_date)
        for candidate in candidates
    ]
    adjudicated.sort(key=adjudication_sort_key)
    record_output = []
    decision_by_actor = {row["candidateActorId"]: row for row in adjudicated}
    for record in record_rows:
        actor_decision = decision_by_actor.get(record.get("candidateActorId", ""))
        if actor_decision is None:
            continue
        record_output.append(record_adjudication_row(record, actor_decision, indexes, args.review_date))
    record_output.sort(key=record_sort_key)

    reports.mkdir(parents=True, exist_ok=True)
    summary_rows = with_release_metadata(adjudicated, metadata)
    detail_rows = with_release_metadata(record_output, metadata)
    write_csv(reports / OUTPUT_CSV, summary_rows, SUMMARY_FIELDS)
    write_csv(reports / OUTPUT_RECORDS_CSV, detail_rows, RECORD_FIELDS)
    write_markdown(reports / OUTPUT_MD, summary_rows, detail_rows, metadata)
    print(f"Wrote {reports / OUTPUT_CSV}")
    print(f"Wrote {reports / OUTPUT_RECORDS_CSV}")
    print(f"Wrote {reports / OUTPUT_MD}")
    return 0


def grouped_records(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("candidateActorId", "")].append(row)
    return grouped


def raw_indexes(raw: Path) -> dict[str, object]:
    dark_rows = read_csv(raw / "dark-money.csv")
    intermediary_rows = read_csv(raw / "intermediaries.csv")
    action_rows = read_csv(raw / "usaspending-procurement-actions.csv")
    dark_by_ein: dict[str, list[dict[str, str]]] = defaultdict(list)
    intermediary_by_ein: dict[str, list[dict[str, str]]] = defaultdict(list)
    action_by_piid_uei: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    action_by_award_uei: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in dark_rows:
        ein = clean_identifier(row.get("sourceRecordId", ""))
        if ein:
            dark_by_ein[ein].append(row)
    for row in intermediary_rows:
        ein = clean_identifier(row.get("ein", ""))
        if ein:
            intermediary_by_ein[ein].append(row)
    for row in action_rows:
        piid = row.get("piid", "").strip()
        award_id = row.get("awardId", "").strip()
        uei = row.get("uei", "").strip()
        if piid and uei:
            action_by_piid_uei[(piid, uei)].append(row)
        if award_id and uei:
            action_by_award_uei[(award_id, uei)].append(row)
    return {
        "dark_by_ein": dict(dark_by_ein),
        "intermediary_by_ein": dict(intermediary_by_ein),
        "action_by_piid_uei": dict(action_by_piid_uei),
        "action_by_award_uei": dict(action_by_award_uei),
    }


def adjudication_row(
    candidate: dict[str, str],
    records: list[dict[str, str]],
    indexes: dict[str, object],
    review_date: str,
) -> dict[str, str]:
    decision = decide(candidate, records, indexes)
    accepted = decision["decision"] in ACCEPTED_DECISIONS
    record_count = len(records)
    reviewed_records = len(records) if accepted else 0
    rejected_records = record_count if decision["decision"] == "rejected_same_venue_only_not_cross_venue" else 0
    held_records = 0 if accepted else record_count - rejected_records
    source_systems = split_semicolon(candidate.get("sourceSystems", ""))
    venues = split_semicolon(candidate.get("venues", ""))
    issues = split_semicolon(candidate.get("issueDomains", ""))
    return {
        "candidateActorId": candidate.get("candidateActorId", ""),
        "normalizedName": candidate.get("normalizedName", ""),
        "primaryName": candidate.get("displayName", candidate.get("normalizedName", "")),
        "decision": decision["decision"],
        "promotedToReviewedPanel": "yes" if accepted else "no",
        "evidenceRule": decision["evidenceRule"],
        "reviewedVenues": "; ".join(venues if accepted else []),
        "sourceSystems": "; ".join(source_systems),
        "sourceRecordCount": str(record_count),
        "reviewedRecordCount": str(reviewed_records),
        "heldRecordCount": str(held_records),
        "rejectedRecordCount": str(rejected_records),
        "confirmedIdentifiers": decision["confirmedIdentifiers"],
        "issueDomains": "; ".join(issues),
        "sourceEvidence": decision["sourceEvidence"],
        "reviewer": REVIEWER,
        "reviewDate": review_date,
        "confidenceScore": decision["confidenceScore"],
        "riskDisposition": decision["riskDisposition"],
        "estimationReadinessContribution": decision["estimationReadinessContribution"],
        "claimBoundary": POLICY_BOUNDARY,
        "nextAction": decision["nextAction"],
    }


def decide(
    candidate: dict[str, str],
    records: list[dict[str, str]],
    indexes: dict[str, object],
) -> dict[str, str]:
    source_systems = set(split_semicolon(candidate.get("sourceSystems", "")))
    venues = set(split_semicolon(candidate.get("venues", "")))
    risk_flags = set(split_semicolon(candidate.get("reviewRiskFlags", "")))
    if risk_flags == {"none"}:
        risk_flags = set()
    common_eins = confirmed_common_eins(records, indexes)
    procurement = confirmed_procurement_records(records, indexes)
    has_dark_intermediary = {
        "IRS/ProPublica dark-money bridge",
        "Intermediary bridge",
    }.issubset(source_systems)
    if (
        source_systems == {"IRS/ProPublica dark-money bridge", "Intermediary bridge"}
        and venues == {"intermediary", "opaque_nonprofit_or_dark_money"}
        and not risk_flags
        and common_eins
    ):
        return {
            "decision": "accepted_exact_ein_cross_venue_reviewed",
            "evidenceRule": "exact-shared-ein-dark-money-intermediary-v1",
            "confirmedIdentifiers": "EIN=" + ";".join(common_eins),
            "sourceEvidence": exact_ein_evidence(common_eins, records, indexes),
            "confidenceScore": "0.9500",
            "riskDisposition": "accepted: exact nonempty EIN appears in both raw dark-money and intermediary files; candidate risk flags are none",
            "estimationReadinessContribution": "reviewed_slice_actor_and_row_evidence_only",
            "nextAction": ESTIMATION_NEXT_ACTION,
        }
    if (
        has_dark_intermediary
        and "USAspending agency actions" in source_systems
        and common_eins
        and procurement["allProcurementRecordsVerified"] == "yes"
    ):
        return {
            "decision": "accepted_exact_ein_plus_procurement_identifier_reviewed",
            "evidenceRule": "exact-shared-ein-plus-usaspending-piid-uei-v1",
            "confirmedIdentifiers": "EIN=" + ";".join(common_eins) + "; " + procurement["confirmedIdentifiers"],
            "sourceEvidence": exact_ein_evidence(common_eins, records, indexes) + "; " + procurement["sourceEvidence"],
            "confidenceScore": "0.9000",
            "riskDisposition": "accepted: exact EIN bridge is source-confirmed and procurement rows are verified by PIID plus UEI; procurement name-overlap risk is retained for panel-level false-match review",
            "estimationReadinessContribution": "reviewed_slice_actor_and_row_evidence_only",
            "nextAction": ESTIMATION_NEXT_ACTION,
        }
    if "same-venue-only" in risk_flags:
        return held_decision(
            "rejected_same_venue_only_not_cross_venue",
            "same-venue-procurement-rejection-v1",
            "same-venue-only candidates are not cross-venue evidence even when source identifiers are repeated",
            "excluded_from_cross_venue_panel",
        )
    if "covered-position-proxy-not-person-movement" in risk_flags:
        return held_decision(
            "held_revolving_door_proxy_not_person_movement",
            "revolving-door-proxy-hold-v1",
            "LDA covered-position proxy rows do not prove individual post-employment movement or coordinated venue shifting",
            "manual_personnel_evidence_required",
        )
    if "name-only-cross-venue" in risk_flags or candidate.get("linkageEvidenceClass") == "cross-venue-name-overlap":
        return held_decision(
            "held_name_only_needs_stable_identifier",
            "name-only-cross-venue-hold-v1",
            "normalized-name overlap lacks a stable shared public identifier",
            "stable_identifier_or_manual_false_match_review_required",
        )
    if "procurement-name-overlap-requires-UEI-review" in risk_flags:
        return held_decision(
            "held_procurement_name_overlap_needs_uei_review",
            "procurement-name-overlap-hold-v1",
            "procurement name overlap requires reviewed UEI/PIID evidence before panel promotion",
            "uei_piid_review_required",
        )
    return held_decision(
        "held_manual_review_required",
        "manual-review-required-v1",
        "candidate row does not meet a conservative acceptance rule",
        "manual_identifier_issue_and_false_match_review_required",
    )


def held_decision(
    decision: str,
    evidence_rule: str,
    risk_disposition: str,
    readiness: str,
) -> dict[str, str]:
    return {
        "decision": decision,
        "evidenceRule": evidence_rule,
        "confirmedIdentifiers": "none",
        "sourceEvidence": "not promoted; reviewed acceptance rule did not pass",
        "confidenceScore": "0.0000",
        "riskDisposition": risk_disposition,
        "estimationReadinessContribution": readiness,
        "nextAction": ESTIMATION_NEXT_ACTION,
    }


def confirmed_common_eins(
    records: list[dict[str, str]],
    indexes: dict[str, object],
) -> list[str]:
    dark_by_ein = indexes["dark_by_ein"]
    intermediary_by_ein = indexes["intermediary_by_ein"]
    dark_eins = {
        clean_identifier(row.get("sourceRecordId", ""))
        for row in records
        if row.get("sourceSystem") == "IRS/ProPublica dark-money bridge"
    }
    intermediary_eins = {
        clean_identifier(row.get("sourceRecordId", ""))
        for row in records
        if row.get("sourceSystem") == "Intermediary bridge"
    }
    return sorted(
        ein
        for ein in dark_eins & intermediary_eins
        if ein and ein in dark_by_ein and ein in intermediary_by_ein
    )


def confirmed_procurement_records(
    records: list[dict[str, str]],
    indexes: dict[str, object],
) -> dict[str, str]:
    action_by_piid_uei = indexes["action_by_piid_uei"]
    action_by_award_uei = indexes["action_by_award_uei"]
    procurement_records = [
        row for row in records if row.get("sourceSystem") == "USAspending agency actions"
    ]
    confirmed: list[str] = []
    missing: list[str] = []
    evidence: list[str] = []
    for record in procurement_records:
        parts = [part.strip() for part in record.get("sourceRecordId", "").split("|")]
        piid = parts[0] if parts else ""
        award_id = parts[1] if len(parts) > 1 else ""
        uei = parts[2] if len(parts) > 2 else ""
        matches = []
        if piid and uei:
            matches.extend(action_by_piid_uei.get((piid, uei), []))
        if award_id and uei:
            matches.extend(action_by_award_uei.get((award_id, uei), []))
        if matches:
            confirmed.append(record.get("sourceRecordId", ""))
            sample = matches[0]
            evidence.append(
                f"USAspending action PIID={sample.get('piid', '')} awardId={sample.get('awardId', '')} UEI={sample.get('uei', '')}"
            )
        else:
            missing.append(record.get("sourceRecordId", ""))
    return {
        "allProcurementRecordsVerified": "yes" if procurement_records and not missing else "no",
        "confirmedIdentifiers": "PIID_UEI=" + ";".join(confirmed) if confirmed else "PIID_UEI=none",
        "sourceEvidence": "; ".join(evidence) if evidence else "no USAspending PIID/UEI rows confirmed",
        "missing": ";".join(missing),
    }


def exact_ein_evidence(
    common_eins: list[str],
    records: list[dict[str, str]],
    indexes: dict[str, object],
) -> str:
    dark_by_ein = indexes["dark_by_ein"]
    intermediary_by_ein = indexes["intermediary_by_ein"]
    evidence: list[str] = []
    for ein in common_eins:
        dark = dark_by_ein[ein][0]
        intermediary = intermediary_by_ein[ein][0]
        evidence.append(
            f"EIN {ein} in dark-money sourceRecordId for {dark.get('source', '')} and intermediary ein for {intermediary.get('organization', '')}"
        )
    return "; ".join(evidence)


def record_adjudication_row(
    record: dict[str, str],
    actor_decision: dict[str, str],
    indexes: dict[str, object],
    review_date: str,
) -> dict[str, str]:
    accepted = actor_decision.get("decision") in ACCEPTED_DECISIONS
    raw_status, raw_evidence = record_raw_evidence(record, actor_decision, indexes)
    if accepted and raw_status == "source_confirmed":
        record_decision = "reviewed_accept"
        promoted = "yes"
    elif actor_decision.get("decision") == "rejected_same_venue_only_not_cross_venue":
        record_decision = "reviewed_reject_from_cross_venue_panel"
        promoted = "no"
    else:
        record_decision = "held_for_manual_review"
        promoted = "no"
    return {
        "candidateActorId": record.get("candidateActorId", ""),
        "normalizedName": record.get("normalizedName", ""),
        "displayName": record.get("displayName", ""),
        "actorDecision": actor_decision.get("decision", "missing"),
        "recordDecision": record_decision,
        "promotedToReviewedPanel": promoted,
        "sourceSystem": record.get("sourceSystem", ""),
        "venue": record.get("venue", ""),
        "sourceFile": record.get("sourceFile", ""),
        "sourceColumn": record.get("sourceColumn", ""),
        "sourceRecordId": record.get("sourceRecordId", ""),
        "issueDomain": record.get("issueDomain", ""),
        "activityAmount": record.get("activityAmount", ""),
        "matchRule": record.get("matchRule", ""),
        "rawEvidenceStatus": raw_status,
        "rawEvidence": raw_evidence,
        "reviewer": REVIEWER,
        "reviewDate": review_date,
        "confidenceScore": actor_decision.get("confidenceScore", ""),
        "claimBoundary": POLICY_BOUNDARY,
    }


def record_raw_evidence(
    record: dict[str, str],
    actor_decision: dict[str, str],
    indexes: dict[str, object],
) -> tuple[str, str]:
    if actor_decision.get("decision") not in ACCEPTED_DECISIONS:
        return "not_promoted", "actor-level acceptance rule did not pass"
    source_system = record.get("sourceSystem", "")
    source_record_id = record.get("sourceRecordId", "")
    if source_system == "IRS/ProPublica dark-money bridge":
        ein = clean_identifier(source_record_id)
        rows = indexes["dark_by_ein"].get(ein, [])
        if rows:
            return "source_confirmed", f"dark-money sourceRecordId={ein}"
    if source_system == "Intermediary bridge":
        ein = clean_identifier(source_record_id)
        rows = indexes["intermediary_by_ein"].get(ein, [])
        if rows:
            return "source_confirmed", f"intermediary ein={ein}"
    if source_system == "USAspending agency actions":
        procurement = confirmed_procurement_records([record], indexes)
        if procurement["allProcurementRecordsVerified"] == "yes":
            return "source_confirmed", procurement["sourceEvidence"]
    return "source_missing", "source-native identifier not confirmed in raw files"


def adjudication_sort_key(row: dict[str, str]) -> tuple[int, float, str]:
    accepted = 0 if row.get("decision", "") in ACCEPTED_DECISIONS else 1
    confidence = -parse_float(row.get("confidenceScore", "0"))
    return (accepted, confidence, row.get("primaryName", ""))


def record_sort_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("candidateActorId", ""),
        row.get("recordDecision", ""),
        row.get("sourceSystem", ""),
        row.get("sourceRecordId", ""),
    )


def clean_identifier(value: str) -> str:
    return re.sub(r"\D+", "", value or "")


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def parse_float(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    record_rows: list[dict[str, str]],
    metadata: dict[str, str],
) -> None:
    accepted = [row for row in rows if row["decision"] in ACCEPTED_DECISIONS]
    held = [row for row in rows if row["heldRecordCount"] != "0"]
    rejected = [row for row in rows if row["rejectedRecordCount"] != "0"]
    accepted_records = [row for row in record_rows if row["recordDecision"] == "reviewed_accept"]
    accepted_venues = sorted({row["venue"] for row in accepted_records if row["venue"]})
    accepted_sources = sorted({row["sourceSystem"] for row in accepted_records if row["sourceSystem"]})
    decision_counts = Counter(row["decision"] for row in rows)
    lines = [
        "# First-Wave Cross-Venue Adjudication",
        "",
        (
            "This generated ledger records the first reviewed slice of the automated "
            "cross-venue candidate worklist. It promotes only source-native identifier "
            "matches into a reviewed evidence slice and keeps all causal, source-product, "
            "ready-to-estimate, and calibrated policy-simulation claim boundaries blocked."
        ),
        "",
        "## Summary",
        "",
        *metadata_summary_lines(metadata),
        f"- Candidate actors adjudicated: `{len(rows)}`",
        f"- Reviewed accepted actors: `{len(accepted)}`",
        f"- Reviewed accepted records: `{len(accepted_records)}`",
        f"- Reviewed venues: `{len(accepted_venues)}` ({'; '.join(accepted_venues) or 'none'})",
        f"- Reviewed source systems: `{len(accepted_sources)}` ({'; '.join(accepted_sources) or 'none'})",
        f"- Held actors: `{len(held)}`",
        f"- Rejected from cross-venue panel actors: `{len(rejected)}`",
        "- Source-product status: `partial_reviewed_slice_not_estimation_ready`",
        "- Ready to estimate: `0`",
        "- Policy-simulation status: `not_cleared`",
        "",
        "## Decision Counts",
        "",
        "| Decision | Actors |",
        "| --- | ---: |",
    ]
    for decision, count in sorted(decision_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {cell(decision)} | {count} |")
    lines.extend([
        "",
        "## Accepted Evidence Rules",
        "",
        "| Evidence rule | Accepted actors | Accepted records | Accepted venues | Source systems | Boundary |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ])
    for rule in sorted({row["evidenceRule"] for row in accepted}):
        rule_rows = [row for row in accepted if row["evidenceRule"] == rule]
        actor_ids = {row["candidateActorId"] for row in rule_rows}
        rule_record_rows = [
            row for row in accepted_records if row["candidateActorId"] in actor_ids
        ]
        venues = sorted({row["venue"] for row in rule_record_rows if row["venue"]})
        sources = sorted({row["sourceSystem"] for row in rule_record_rows if row["sourceSystem"]})
        lines.append(
            f"| {cell(rule)} | {len(rule_rows)} | {len(rule_record_rows)} | "
            f"{cell('; '.join(venues))} | {cell('; '.join(sources))} | {cell(POLICY_BOUNDARY)} |"
        )
    lines.extend([
        "",
        "## Accepted Actor Sample",
        "",
        "| Actor | Decision | Confirmed identifiers | Records | Evidence |",
        "| --- | --- | --- | ---: | --- |",
    ])
    for row in accepted[:20]:
        lines.append(
            f"| {cell(row['primaryName'])} | {cell(row['decision'])} | "
            f"{cell(row['confirmedIdentifiers'])} | {row['reviewedRecordCount']} | "
            f"{cell(row['sourceEvidence'])} |"
        )
    lines.extend([
        "",
        "## Held Or Rejected Boundary",
        "",
        "| Decision | Actors | Risk disposition | Next action |",
        "| --- | ---: | --- | --- |",
    ])
    for decision, count in sorted(
        Counter(row["decision"] for row in rows if row["decision"] not in ACCEPTED_DECISIONS).items(),
        key=lambda item: (-item[1], item[0]),
    ):
        sample = next(row for row in rows if row["decision"] == decision)
        lines.append(
            f"| {cell(decision)} | {count} | {cell(sample['riskDisposition'])} | {cell(sample['nextAction'])} |"
        )
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        (
            "The accepted rows are reviewed identifier evidence only. They do not clear "
            "the candidate seed products, the substitution-elasticity source-product "
            "gate, the venue-shifting source-product gate, the source-readiness gate, "
            "or calibrated policy-simulation claims. The current reviewed slice remains "
            "below the linked-panel threshold and still lacks audited false-match, issue "
            "comparability, and observed pre/post comparison-group evidence."
        ),
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


SUMMARY_FIELDS = [
    *RELEASE_METADATA_FIELDS,
    "candidateActorId",
    "normalizedName",
    "primaryName",
    "decision",
    "promotedToReviewedPanel",
    "evidenceRule",
    "reviewedVenues",
    "sourceSystems",
    "sourceRecordCount",
    "reviewedRecordCount",
    "heldRecordCount",
    "rejectedRecordCount",
    "confirmedIdentifiers",
    "issueDomains",
    "sourceEvidence",
    "reviewer",
    "reviewDate",
    "confidenceScore",
    "riskDisposition",
    "estimationReadinessContribution",
    "claimBoundary",
    "nextAction",
]

RECORD_FIELDS = [
    *RELEASE_METADATA_FIELDS,
    "candidateActorId",
    "normalizedName",
    "displayName",
    "actorDecision",
    "recordDecision",
    "promotedToReviewedPanel",
    "sourceSystem",
    "venue",
    "sourceFile",
    "sourceColumn",
    "sourceRecordId",
    "issueDomain",
    "activityAmount",
    "matchRule",
    "rawEvidenceStatus",
    "rawEvidence",
    "reviewer",
    "reviewDate",
    "confidenceScore",
    "claimBoundary",
]


if __name__ == "__main__":
    raise SystemExit(main())
