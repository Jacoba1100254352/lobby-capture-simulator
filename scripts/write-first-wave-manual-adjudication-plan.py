#!/usr/bin/env python3
"""Write the manual adjudication workplan for first-wave candidate products."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
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
OUTPUT_CSV = "first-wave-manual-adjudication-plan.csv"
OUTPUT_MD = "first-wave-manual-adjudication-plan.md"
RERUN_COMMAND = (
    "make first-wave-source-products first-wave-source-readiness "
    "first-wave-manual-adjudication-plan candidate-source-leakage-audit "
    "paper-artifacts-check"
)
FIRST_REVIEW_BATCH_LIMIT = 3
TARGET_ORDER = {
    "substitution-elasticity": 0,
    "procurement-modification-causal-capture": 1,
    "comment-authenticity-and-uptake-effect": 2,
    "venue-shifting-detection-effect": 3,
}
PRIORITY_ORDER = {"P1": 0, "P2": 1, "P3": 2}
ROW_PRIORITY_ORDER = {
    "P1-manual-review": 0,
    "P2-manual-review": 1,
    "P3-manual-review": 2,
}
ROW_ID_FIELDS = {
    "actor-issue-time-spine": [
        "canonicalActorId",
        "issueCode",
        "venue",
        "periodStart",
        "periodEnd",
        "sourceSystem",
        "sourceRecordId",
        "exposureGroup",
    ],
    "substitution-comparison-groups": [
        "reformEventId",
        "canonicalActorId",
        "issueCode",
        "comparisonGroup",
        "prePeriodStart",
        "postPeriodStart",
    ],
    "sam-fpds-action-history-crosswalk": [
        "piid",
        "uei",
        "agency",
        "actionDate",
        "modificationNumber",
        "sourceUrl",
    ],
    "gao-protest-overlay": [
        "protestId",
        "docketNumber",
        "agency",
        "decisionDate",
        "outcome",
        "sourceUrl",
    ],
    "sam-exclusion-overlay": [
        "exclusionId",
        "uei",
        "recipientName",
        "exclusionType",
        "startDate",
        "agency",
        "sourceUrl",
    ],
    "procurement-offer-competition-enrichment": [
        "piid",
        "uei",
        "agency",
        "actionDate",
        "extentCompeted",
        "numberOfOffers",
        "sourceUrl",
    ],
    "agency-response-final-rule-linkage": [
        "docketId",
        "commentId",
        "responseSectionId",
        "finalRuleId",
        "finalRuleDate",
        "ruleCitation",
    ],
    "canonical-actor-identifiers": [
        "canonicalActorId",
        "primaryName",
        "actorType",
        "sourceSystems",
        "uei",
        "intermediaryId",
    ],
    "alias-resolution-audit-sample": [
        "auditId",
        "canonicalActorId",
        "aliasName",
        "sourceSystem",
        "sourceRecordId",
        "matchRule",
    ],
    "false-match-review-log": [
        "reviewId",
        "canonicalActorId",
        "candidateRecordId",
        "sourceSystem",
        "issueCode",
        "errorType",
    ],
    "issue-code-crosswalk": [
        "issueCode",
        "policyDomain",
        "ldaIssueCode",
        "docketTerms",
        "naicsCodes",
        "pscCodes",
        "fecPurposeTerms",
    ],
    "linked-actor-issue-venue-time": [
        "canonicalActorId",
        "issueCode",
        "venue",
        "periodStart",
        "periodEnd",
        "sourceSystem",
        "sourceRecordId",
    ],
}
FIRST_REVIEW_FOCUS = {
    "actor-issue-time-spine": (
        "Start with high-priority cross-source rows and verify canonical actor, "
        "issue, venue, source record, exposure group, and pre/post comparability."
    ),
    "substitution-comparison-groups": (
        "Verify that treated and comparison assignments are tied to the named "
        "reform shock and that exclusions and pre/post windows are defensible."
    ),
    "sam-fpds-action-history-crosswalk": (
        "Replace the placeholder with reviewed SAM/FPDS action-history rows and "
        "verify modification coding, competition fields, offers, and source IDs."
    ),
    "gao-protest-overlay": (
        "Start with discovered GAO rows and adjudicate agency, filed date, outcome, "
        "issue code, and PIID, UEI, protester, awardee, or vendor linkage."
    ),
    "sam-exclusion-overlay": (
        "Replace the placeholder with reviewed exclusions rows carrying UEI, "
        "dates, exclusion type, agency, cause, and source provenance."
    ),
    "procurement-offer-competition-enrichment": (
        "Replace the placeholder with reviewed source-system competition rows and "
        "verify extent-competed codes, offer counts, source records, and dates."
    ),
    "agency-response-final-rule-linkage": (
        "Open the cited docket materials and adjudicate response section, final-rule "
        "movement, uptake code, text similarity, reviewer, and review date."
    ),
    "canonical-actor-identifiers": (
        "Start with high-risk shared-identifier rows and verify actor identity, "
        "source-system coverage, parent/subsidiary ambiguity, and procurement UEI linkage."
    ),
    "alias-resolution-audit-sample": (
        "Review accept/reject alias decisions with reviewer/date provenance and "
        "retain enough rejected examples to bound false-positive risk."
    ),
    "false-match-review-log": (
        "Adjudicate both accepted and rejected linkage examples, including error type, "
        "reviewer/date provenance, and confidence evidence."
    ),
    "issue-code-crosswalk": (
        "Review each issue concept against lobbying, docket, procurement, and electoral "
        "terms before using movement across venues as comparable."
    ),
    "linked-actor-issue-venue-time": (
        "Promote only after canonical actors, aliases, issue crosswalks, and false-match "
        "logs pass review; then verify each linked source record and activity measure."
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    product_rows = read_csv(args.reports / "first-wave-source-products.csv")
    readiness_rows = keyed_rows(args.reports / "first-wave-source-readiness.csv", "targetKey")
    candidate_rows = [
        row
        for row in product_rows
        if row.get("productStatus") == "candidate_unreviewed"
    ]
    planned_rows = sorted(
        [plan_row(args.root, row, readiness_rows) for row in candidate_rows],
        key=plan_sort_key,
    )
    metadata = release_metadata()
    output_rows = with_release_metadata(planned_rows, metadata)
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / OUTPUT_CSV, output_rows)
    write_markdown(args.reports / OUTPUT_MD, output_rows, metadata)
    print(f"Wrote {args.reports / OUTPUT_CSV}")
    print(f"Wrote {args.reports / OUTPUT_MD}")
    return 0


def plan_row(
    root: Path,
    product: dict[str, str],
    readiness_rows: dict[str, dict[str, str]],
) -> dict[str, str]:
    product_key = product.get("productKey", "")
    expected_path = product.get("expectedPath", "")
    path = root / expected_path
    file_rows = read_csv(path) if path.suffix.lower() == ".csv" else []
    first_batch = first_review_batch(product_key, file_rows)
    candidate_count = 0
    reviewed_count = 0
    reviewer_date_gaps = 0
    priority_counts: Counter[str] = Counter()
    evidence_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    for row in file_rows:
        if row_is_marked_candidate(row):
            candidate_count += 1
        else:
            reviewed_count += 1
        if reviewer_date_gap(row):
            reviewer_date_gaps += 1
        priority = row.get("reviewPriority", "").strip()
        if priority:
            priority_counts[priority] += 1
        evidence = row.get("linkageEvidenceClass", "").strip()
        if evidence:
            evidence_counts[evidence] += 1
        for flag in split_semicolon(row.get("reviewRiskFlags", "")):
            if flag and flag != "none":
                risk_counts[flag] += 1

    observed_rows = int_or_zero(product.get("observedRows", ""))
    minimum_rows = int_or_zero(product.get("minimumRows", ""))
    row_shortfall = max(0, minimum_rows - observed_rows)
    readiness = readiness_rows.get(product.get("targetKey", ""), {})
    promotion_blockers = [
        "candidate markers remain present",
        "manual review not signed off",
        f"target gate={readiness.get('sourceProductGate', 'missing') or 'missing'}",
        "ready-to-estimate status remains blocked",
        "calibrated policy-simulation remains not cleared",
    ]
    if row_shortfall:
        promotion_blockers.append(f"minimum row shortfall={row_shortfall}")
    return {
        "targetKey": product.get("targetKey", ""),
        "productKey": product.get("productKey", ""),
        "productLabel": product.get("productLabel", ""),
        "priority": product.get("priority", ""),
        "expectedPath": expected_path,
        "productStatus": product.get("productStatus", ""),
        "observedRows": product.get("observedRows", ""),
        "minimumRows": product.get("minimumRows", ""),
        "rowShortfall": str(row_shortfall),
        "candidateRows": str(candidate_count),
        "reviewedRows": str(reviewed_count),
        "reviewerDateGaps": str(reviewer_date_gaps),
        "rowPriorityCounts": counter_summary(priority_counts),
        "linkageEvidenceClasses": counter_summary(evidence_counts),
        "reviewRiskFlags": counter_summary(risk_counts, limit=6),
        "firstReviewBatchSize": str(len(first_batch)),
        "firstReviewBatchRows": " || ".join(first_batch),
        "firstReviewBatchFocus": first_review_focus(product_key, product),
        "targetSourceProductGate": readiness.get("sourceProductGate", "missing"),
        "targetBlockingIssue": readiness.get("blockingIssue", "missing"),
        "promotionState": "manual_review_required",
        "promotionBlockers": "; ".join(promotion_blockers),
        "manualReviewChecklist": product.get("manualReviewChecklist", ""),
        "promotionCommand": RERUN_COMMAND,
        "claimBoundary": product.get("claimBoundary", ""),
    }


def plan_sort_key(row: dict[str, str]) -> tuple[int, int, int, str]:
    return (
        PRIORITY_ORDER.get(row.get("priority", ""), 9),
        TARGET_ORDER.get(row.get("targetKey", ""), 9),
        -int_or_zero(row.get("candidateRows", "")),
        row.get("productKey", ""),
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path) if row.get(key)}


def row_is_marked_candidate(row: dict[str, str]) -> bool:
    values = " ".join(str(value) for value in row.values()).lower()
    return (
        row.get("candidateOnly", "").lower() == "true"
        or "candidate_unreviewed" in values
        or "candidate-only" in values
    )


def reviewer_date_gap(row: dict[str, str]) -> bool:
    reviewer = row.get("reviewer", "").strip().lower()
    review_date = row.get("reviewDate", "").strip().lower()
    if not reviewer and not review_date:
        return False
    return reviewer in {"", "not_reviewed", "candidate_unreviewed"} or review_date in {
        "",
        "not_reviewed",
        "candidate_unreviewed",
    }


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def first_review_batch(product_key: str, rows: list[dict[str, str]]) -> list[str]:
    indexed_rows = list(enumerate(rows, start=1))
    indexed_rows.sort(key=lambda item: row_review_sort_key(item[1], item[0]))
    return [
        format_review_candidate(product_key, row_number, row)
        for row_number, row in indexed_rows[:FIRST_REVIEW_BATCH_LIMIT]
    ]


def row_review_sort_key(row: dict[str, str], row_number: int) -> tuple[int, float, int]:
    priority = row.get("reviewPriority", "").strip()
    score = float_or_zero(row.get("reviewPriorityScore", ""))
    return (ROW_PRIORITY_ORDER.get(priority, 9), -score, row_number)


def format_review_candidate(
    product_key: str,
    row_number: int,
    row: dict[str, str],
) -> str:
    parts: list[str] = []
    for field in ROW_ID_FIELDS.get(product_key, []):
        value = compact_value(row.get(field, ""))
        if value:
            parts.append(f"{field}={value}")
    if not parts:
        for field, value in row.items():
            if field in {"notes", "candidateStatus"}:
                continue
            compacted = compact_value(value)
            if compacted:
                parts.append(f"{field}={compacted}")
            if len(parts) >= 6:
                break
    priority = compact_value(row.get("reviewPriority", ""))
    score = compact_value(row.get("reviewPriorityScore", ""))
    risks = compact_value(row.get("reviewRiskFlags", ""))
    if priority:
        parts.append(f"reviewPriority={priority}")
    if score:
        parts.append(f"reviewPriorityScore={score}")
    if risks and risks != "none":
        parts.append(f"reviewRiskFlags={risks}")
    return f"row{row_number}: " + "; ".join(parts)


def first_review_focus(product_key: str, product: dict[str, str]) -> str:
    return FIRST_REVIEW_FOCUS.get(
        product_key,
        product.get("manualReviewChecklist", "Use the product checklist to review candidate rows."),
    )


def counter_summary(counter: Counter[str], limit: int | None = None) -> str:
    items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    if limit is not None:
        items = items[:limit]
    return "; ".join(f"{key}={count}" for key, count in items) or "none"


def int_or_zero(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def float_or_zero(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def compact_value(value: str, limit: int = 90) -> str:
    compacted = " ".join(str(value or "").split())
    if len(compacted) <= limit:
        return compacted
    return compacted[: limit - 3] + "..."


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        *RELEASE_METADATA_FIELDS,
        "targetKey",
        "productKey",
        "productLabel",
        "priority",
        "expectedPath",
        "productStatus",
        "observedRows",
        "minimumRows",
        "rowShortfall",
        "candidateRows",
        "reviewedRows",
        "reviewerDateGaps",
        "rowPriorityCounts",
        "linkageEvidenceClasses",
        "reviewRiskFlags",
        "firstReviewBatchSize",
        "firstReviewBatchRows",
        "firstReviewBatchFocus",
        "targetSourceProductGate",
        "targetBlockingIssue",
        "promotionState",
        "promotionBlockers",
        "manualReviewChecklist",
        "promotionCommand",
        "claimBoundary",
    ]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], metadata: dict[str, str]) -> None:
    total_candidate_rows = sum(int_or_zero(row.get("candidateRows", "")) for row in rows)
    total_reviewed_rows = sum(int_or_zero(row.get("reviewedRows", "")) for row in rows)
    total_shortfalls = sum(1 for row in rows if int_or_zero(row.get("rowShortfall", "")) > 0)
    total_first_batch_rows = sum(int_or_zero(row.get("firstReviewBatchSize", "")) for row in rows)
    priority_counts = Counter(row.get("priority", "unknown") for row in rows)
    target_counts = Counter(row.get("targetKey", "unknown") for row in rows)
    lines = [
        "# First-Wave Manual Adjudication Plan",
        "",
        (
            "This generated plan turns candidate-only first-wave source products into "
            "a bounded manual-review queue. Candidate-only products are manual-review "
            "queues, not evidence; this plan does not clear ready-to-estimate or "
            "calibrated policy-simulation claims."
        ),
        "",
        "## Summary",
        "",
        *metadata_summary_lines(metadata),
        f"- Candidate products: `{len(rows)}`",
        f"- Candidate rows: `{total_candidate_rows}`",
        f"- Reviewed rows while candidate gate is active: `{total_reviewed_rows}`",
        f"- Products below minimum-row threshold: `{total_shortfalls}`",
        f"- First-review batch rows: `{total_first_batch_rows}`",
        f"- Product priorities: `{counter_summary(priority_counts)}`",
        f"- Targets represented: `{counter_summary(target_counts)}`",
        "- Ready-to-estimate status remains blocked: `yes`",
        "- No calibrated policy-simulation claim clears from this plan.",
        "",
        "## Promotion Rule",
        "",
        (
            "A product can be promoted only after the product-specific checklist is "
            "completed against source records, reviewer/date provenance is recorded "
            "where applicable, candidateOnly and candidate_unreviewed markers are removed, "
            "and the source-product, source-readiness, manual-adjudication, leakage, "
            "and artifact gates pass."
        ),
        "",
        f"Promotion command sequence: `{RERUN_COMMAND}`",
        "",
        "The `reviewPriorityScore` field orders review work; it is not adjudicated match confidence.",
        "The first-review batch lists candidate row identifiers to inspect first; those rows remain candidate-only until the same promotion rule clears.",
        "",
        "## Product Queue",
        "",
        "| Target | Product | Priority | Candidate rows | Minimum rows | Shortfall | Row priorities | Evidence classes | Risk flags | Promotion state |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {targetKey} | {productLabel} | {priority} | {candidateRows} | {minimumRows} | {rowShortfall} | {rowPriorityCounts} | {linkageEvidenceClasses} | {reviewRiskFlags} | {promotionState} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## First Review Batch",
        "",
        "| Product | Batch size | First rows to inspect | Review focus |",
        "| --- | ---: | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {productLabel} | {firstReviewBatchSize} | {firstReviewBatchRows} | {firstReviewBatchFocus} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Promotion Checklists",
        "",
        "| Product | Expected path | Blockers | Checklist |",
        "| --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {productLabel} | `{expectedPath}` | {promotionBlockers} | {manualReviewChecklist} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        "| Product | Claim boundary | Target blocking issue |",
        "| --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {productLabel} | {claimBoundary} | {targetBlockingIssue} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
