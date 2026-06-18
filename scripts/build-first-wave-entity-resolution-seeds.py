#!/usr/bin/env python3
"""Build candidate-only first-wave entity-resolution source-product seeds.

These files intentionally do not clear the source-product gate. They convert
the linkage-candidate report into reviewable CSV worklists under
data/calibration/first-wave/ so entity-resolution review can start from a
stable artifact without treating automated name overlap as evidence.
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
MAX_ALIAS_ROWS = 80
MAX_FALSE_MATCH_ROWS = 40
MAX_LINKED_ROWS = 1500
MAX_SPINE_ROWS = 1500
MAX_COMPARISON_ROWS = 80
SUBSTITUTION_REFORM_EVENT_ID = "hloga-2007-federal-lobbying-disclosure"
CANDIDATE_MARKER = "candidate_unreviewed_not_estimation_ready"
CLAIM_BOUNDARY = (
    "candidate-only automated name-overlap seed; not manually adjudicated; "
    "does not clear first-wave source-product, venue-shifting, or causal-calibration gates"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    reports = args.reports if args.reports.is_absolute() else ROOT / args.reports
    output = args.output if args.output.is_absolute() else ROOT / args.output
    candidates = read_rows(reports / "first-wave-linkage-candidates.csv")
    records = read_rows(reports / "first-wave-linkage-candidate-records.csv")
    records_by_actor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        records_by_actor[record.get("candidateActorId", "")].append(record)
    linked_rows = linked_actor_issue_rows(candidates, records_by_actor)

    output.mkdir(parents=True, exist_ok=True)
    write_csv(
        output / "canonical-actor-identifiers.csv",
        canonical_actor_rows(candidates, records_by_actor),
    )
    write_csv(
        output / "alias-resolution-audit-sample.csv",
        alias_review_rows(candidates, records_by_actor),
    )
    write_csv(
        output / "issue-code-crosswalk.csv",
        issue_crosswalk_rows(candidates, records),
    )
    write_csv(
        output / "false-match-review-log.csv",
        false_match_rows(candidates, records_by_actor),
    )
    write_csv(
        output / "linked-actor-issue-venue-time.csv",
        linked_rows,
    )
    write_csv(
        output / "actor-issue-time-spine.csv",
        actor_issue_time_spine_rows(candidates, linked_rows),
    )
    write_csv(
        output / "substitution-comparison-groups.csv",
        substitution_comparison_group_rows(candidates, linked_rows),
    )
    for filename in (
        "canonical-actor-identifiers.csv",
        "alias-resolution-audit-sample.csv",
        "issue-code-crosswalk.csv",
        "false-match-review-log.csv",
        "linked-actor-issue-venue-time.csv",
        "actor-issue-time-spine.csv",
        "substitution-comparison-groups.csv",
    ):
        print(f"Wrote {output / filename}")
    return 0


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def canonical_actor_rows(
    candidates: list[dict[str, str]],
    records_by_actor: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in candidates:
        actor_id = candidate.get("candidateActorId", "")
        records = records_by_actor.get(actor_id, [])
        rows.append(
            {
                "canonicalActorId": actor_id,
                "primaryName": candidate.get("displayName") or candidate.get("normalizedName", ""),
                "actorType": infer_actor_type(candidate),
                "ldaClientId": source_ids(records, "LDA"),
                "fecCommitteeId": source_ids(records, "OpenFEC"),
                "uei": procurement_ueis(records),
                "docketSubmitterId": "not_observed_in_candidate_snapshot",
                "intermediaryId": source_ids(records, "Intermediary bridge"),
                "sourceSystems": candidate.get("sourceSystems", ""),
                "parentActorId": "not_reviewed",
                "country": "not_reviewed",
                "state": "not_reviewed",
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_MARKER,
                "notes": (
                    f"{CLAIM_BOUNDARY}; sourceRecordCount={candidate.get('sourceRecordCount', '0')}; "
                    f"venues={candidate.get('venues', '')}"
                ),
            }
        )
    return rows


def alias_review_rows(
    candidates: list[dict[str, str]],
    records_by_actor: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in candidates:
        actor_id = candidate.get("candidateActorId", "")
        for record in unique_review_records(records_by_actor.get(actor_id, [])):
            rows.append(
                {
                    "auditId": f"alias-seed-{len(rows) + 1:04d}",
                    "canonicalActorId": actor_id,
                    "aliasName": record.get("displayName", ""),
                    "sourceSystem": record.get("sourceSystem", ""),
                    "sourceRecordId": record.get("sourceRecordId", ""),
                    "matchRule": record.get("matchRule", "normalized-name-exact"),
                    "manualDecision": CANDIDATE_MARKER,
                    "reviewer": "not_reviewed",
                    "reviewDate": "not_reviewed",
                    "confidenceScore": "0.3500",
                    "candidateOnly": "true",
                    "notes": CLAIM_BOUNDARY,
                }
            )
            if len(rows) >= MAX_ALIAS_ROWS:
                return rows
    return rows


def issue_crosswalk_rows(
    candidates: list[dict[str, str]],
    records: list[dict[str, str]],
) -> list[dict[str, str]]:
    issue_values: list[str] = []
    for candidate in candidates:
        issue_values.extend(split_semicolon(candidate.get("issueDomains", "")))
    for record in records:
        issue_values.extend(split_semicolon(record.get("issueDomain", "")))
    normalized_issues = sorted({normalize_issue(issue) for issue in issue_values if normalize_issue(issue)})
    rows = []
    for issue in normalized_issues[:8]:
        rows.append(
            {
                "issueCode": f"candidate-{slug(issue)}",
                "ldaIssueCode": "candidate_unreviewed",
                "policyDomain": issue,
                "docketTerms": "candidate_unreviewed",
                "naicsCodes": "candidate_unreviewed",
                "pscCodes": "candidate_unreviewed",
                "fecPurposeTerms": "candidate_unreviewed",
                "notes": f"{CLAIM_BOUNDARY}; issue concept observed in candidate linkage rows.",
                "reviewer": "not_reviewed",
                "reviewDate": "not_reviewed",
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_MARKER,
            }
        )
    while len(rows) < 3:
        index = len(rows) + 1
        rows.append(
            {
                "issueCode": f"candidate-placeholder-{index}",
                "ldaIssueCode": "candidate_unreviewed",
                "policyDomain": f"candidate issue {index}",
                "docketTerms": "candidate_unreviewed",
                "naicsCodes": "candidate_unreviewed",
                "pscCodes": "candidate_unreviewed",
                "fecPurposeTerms": "candidate_unreviewed",
                "notes": f"{CLAIM_BOUNDARY}; added only to preserve review-template shape.",
                "reviewer": "not_reviewed",
                "reviewDate": "not_reviewed",
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_MARKER,
            }
        )
    return rows


def false_match_rows(
    candidates: list[dict[str, str]],
    records_by_actor: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in candidates:
        actor_id = candidate.get("candidateActorId", "")
        records = unique_review_records(records_by_actor.get(actor_id, []))
        for record in records[:2]:
            rows.append(
                {
                    "reviewId": f"false-match-seed-{len(rows) + 1:04d}",
                    "canonicalActorId": actor_id,
                    "candidateRecordId": record.get("sourceRecordId", ""),
                    "sourceSystem": record.get("sourceSystem", ""),
                    "issueCode": issue_code(record.get("issueDomain", "")),
                    "decision": CANDIDATE_MARKER,
                    "errorType": "unreviewed_possible_false_positive",
                    "notes": CLAIM_BOUNDARY,
                    "reviewer": "not_reviewed",
                    "reviewDate": "not_reviewed",
                    "confidenceScore": "0.3500",
                    "candidateOnly": "true",
                }
            )
            if len(rows) >= MAX_FALSE_MATCH_ROWS:
                return rows
    return rows


def unique_review_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Collapse repeated source rows for manual-review samples.

    Linkage candidate records can contain repeated activity rows for the same
    actor/source identifier. Those repetitions are useful in activity panels,
    but they waste scarce manual-review sample slots.
    """
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for record in records:
        key = (
            record.get("displayName", ""),
            record.get("sourceSystem", ""),
            record.get("sourceRecordId", ""),
            record.get("matchRule", ""),
            issue_code(record.get("issueDomain", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def linked_actor_issue_rows(
    candidates: list[dict[str, str]],
    records_by_actor: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    candidate_by_id = {candidate.get("candidateActorId", ""): candidate for candidate in candidates}
    for actor_id in sorted(candidate_by_id, key=lambda key: sort_key(candidate_by_id[key])):
        for record in records_by_actor.get(actor_id, []):
            rows.append(
                {
                    "canonicalActorId": actor_id,
                    "issueCode": issue_code(record.get("issueDomain", "")),
                    "venue": record.get("venue", ""),
                    "periodStart": "2024-01-01",
                    "periodEnd": "2024-12-31",
                    "activityType": record.get("sourceColumn", "source_record"),
                    "activityMeasure": record.get("activityAmount", "0.0000") or "0.0000",
                    "sourceSystem": record.get("sourceSystem", ""),
                    "sourceRecordId": record.get("sourceRecordId", ""),
                    "matchConfidence": "0.3500",
                    "activityAmount": record.get("activityAmount", "0.0000") or "0.0000",
                    "jurisdiction": "candidate_unreviewed",
                    "candidateOnly": "true",
                    "candidateStatus": CANDIDATE_MARKER,
                    "notes": CLAIM_BOUNDARY,
                }
            )
            if len(rows) >= MAX_LINKED_ROWS:
                return rows
    return rows


def actor_issue_time_spine_rows(
    candidates: list[dict[str, str]],
    linked_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Create a candidate-only substitution spine from linked venue rows.

    The file uses two review periods so the source-product shape can be audited,
    but it remains explicitly marked as unreviewed and not estimation-ready.
    """
    candidate_by_id = {candidate.get("candidateActorId", ""): candidate for candidate in candidates}
    rows: list[dict[str, str]] = []
    periods = (
        ("candidate-pre-window", "2024-01-01", "2024-06-30"),
        ("candidate-post-window", "2024-07-01", "2024-12-31"),
    )
    for source_row in linked_rows:
        actor_id = source_row.get("canonicalActorId", "")
        exposure_group = substitution_exposure_group(candidate_by_id.get(actor_id, {}))
        amount = half_amount(source_row.get("activityAmount", "") or source_row.get("activityMeasure", ""))
        for period_label, period_start, period_end in periods:
            rows.append(
                {
                    "canonicalActorId": actor_id,
                    "issueCode": source_row.get("issueCode", ""),
                    "periodStart": period_start,
                    "periodEnd": period_end,
                    "venue": source_row.get("venue", ""),
                    "activityType": source_row.get("activityType", ""),
                    "activityMeasure": amount,
                    "activityAmount": amount,
                    "sourceSystem": source_row.get("sourceSystem", ""),
                    "sourceRecordId": source_row.get("sourceRecordId", ""),
                    "exposureGroup": exposure_group,
                    "reformEventId": SUBSTITUTION_REFORM_EVENT_ID,
                    "activityUnits": "normalized_candidate_activity",
                    "jurisdiction": source_row.get("jurisdiction", "candidate_unreviewed"),
                    "matchConfidence": source_row.get("matchConfidence", "0.3500"),
                    "candidateOnly": "true",
                    "candidateStatus": CANDIDATE_MARKER,
                    "notes": (
                        f"{CLAIM_BOUNDARY}; {period_label} periodization is a review scaffold, "
                        "not observed pre/post substitution evidence"
                    ),
                }
            )
            if len(rows) >= MAX_SPINE_ROWS:
                return rows
    return rows


def substitution_comparison_group_rows(
    candidates: list[dict[str, str]],
    linked_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    issues_by_actor: dict[str, set[str]] = defaultdict(set)
    for row in linked_rows:
        actor_id = row.get("canonicalActorId", "")
        issue = row.get("issueCode", "")
        if actor_id and issue:
            issues_by_actor[actor_id].add(issue)

    rows: list[dict[str, str]] = []
    for candidate in candidates:
        actor_id = candidate.get("candidateActorId", "")
        issues = sorted(issues_by_actor.get(actor_id) or {"candidate-uncoded"})
        for issue in issues[:2]:
            rows.append(
                {
                    "reformEventId": SUBSTITUTION_REFORM_EVENT_ID,
                    "canonicalActorId": actor_id,
                    "issueCode": issue,
                    "comparisonGroup": substitution_exposure_group(candidate),
                    "matchingVariables": (
                        "candidate sourceSystems="
                        f"{candidate.get('sourceSystems', '')}; venues={candidate.get('venues', '')}; "
                        "matchRule=normalized-name-exact; manualReviewRequired=true"
                    ),
                    "prePeriodStart": "2006-01-01",
                    "prePeriodEnd": "2007-09-13",
                    "postPeriodStart": "2007-09-14",
                    "postPeriodEnd": "2008-12-31",
                    "matchScore": "0.3500",
                    "exclusionReason": "candidate_unreviewed",
                    "candidateOnly": "true",
                    "candidateStatus": CANDIDATE_MARKER,
                    "notes": (
                        f"{CLAIM_BOUNDARY}; HLOGA windows are encoded for design review only; "
                        "the 2024 candidate snapshot does not supply observed pre/post rows"
                    ),
                }
            )
            if len(rows) >= MAX_COMPARISON_ROWS:
                return rows
    return rows


def sort_key(candidate: dict[str, str]) -> tuple[int, int, float, str]:
    return (
        -int_or_zero(candidate.get("venueCount", "")),
        -int_or_zero(candidate.get("sourceSystemCount", "")),
        -float_or_zero(candidate.get("totalActivityAmount", "")),
        candidate.get("normalizedName", ""),
    )


def infer_actor_type(candidate: dict[str, str]) -> str:
    venues = set(split_semicolon(candidate.get("venues", "")))
    if "procurement" in venues and len(venues) == 1:
        return "vendor_candidate"
    if "revolving_door" in venues and "visible_lobbying" in venues:
        return "lobbying_firm_or_client_candidate"
    if {"intermediary", "opaque_nonprofit_or_dark_money"} & venues:
        return "nonprofit_association_or_intermediary_candidate"
    if "electoral_money" in venues:
        return "political_spender_or_recipient_candidate"
    return "organization_candidate"


def substitution_exposure_group(candidate: dict[str, str]) -> str:
    venues = set(split_semicolon(candidate.get("venues", "")))
    if {"visible_lobbying", "revolving_door"} & venues:
        return "exposed_candidate_unreviewed"
    return "comparison_candidate_unreviewed"


def half_amount(value: str) -> str:
    return format_float(float_or_zero(value) / 2.0)


def source_ids(records: list[dict[str, str]], source_system: str) -> str:
    values = [
        record.get("sourceRecordId", "")
        for record in records
        if record.get("sourceSystem") == source_system and record.get("sourceRecordId")
    ]
    return compact_values(values)


def procurement_ueis(records: list[dict[str, str]]) -> str:
    ueis: list[str] = []
    for record in records:
        if not record.get("sourceSystem", "").startswith("USAspending"):
            continue
        parts = [part.strip() for part in record.get("sourceRecordId", "").split("|")]
        if len(parts) >= 3 and parts[2]:
            ueis.append(parts[2])
    return compact_values(ueis)


def compact_values(values: list[str], limit: int = 6) -> str:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    if not seen:
        return "not_observed_in_candidate_snapshot"
    truncated = seen[:limit]
    suffix = f"; +{len(seen) - limit} more" if len(seen) > limit else ""
    return "; ".join(truncated) + suffix


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def normalize_issue(value: str) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip().lower())
    if not text or text in {"unknown", "none", "n/a"}:
        return ""
    return text


def issue_code(value: str) -> str:
    issue = normalize_issue(value)
    return f"candidate-{slug(issue)}" if issue else "candidate-uncoded"


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "uncoded"


def int_or_zero(value: str) -> int:
    try:
        return int(float(value or "0"))
    except ValueError:
        return 0


def float_or_zero(value: str) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def format_float(value: float) -> str:
    return f"{value:.4f}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fieldnames = list(rows[0])
    else:
        fieldnames = []
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
