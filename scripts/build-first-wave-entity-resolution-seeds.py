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
        linked_actor_issue_rows(candidates, records_by_actor),
    )
    for filename in (
        "canonical-actor-identifiers.csv",
        "alias-resolution-audit-sample.csv",
        "issue-code-crosswalk.csv",
        "false-match-review-log.csv",
        "linked-actor-issue-venue-time.csv",
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
        for record in records_by_actor.get(actor_id, []):
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
        records = records_by_actor.get(actor_id, [])
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
