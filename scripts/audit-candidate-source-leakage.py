#!/usr/bin/env python3
"""Audit that candidate-only source worklists cannot clear empirical gates.

The first-wave source bundle intentionally includes deterministic candidate
worklists so reviewers can inspect the intended acquisition and adjudication
units. Those files are useful as a work plan, but they must not become evidence
for causal estimation or calibrated policy claims until manual review replaces
candidate markers with reviewed source rows. This audit fails if the candidate
state leaks into ready-to-estimate or calibrated-claim gates.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIRST_WAVE_DIR = ROOT / "data" / "calibration" / "first-wave"
OUTPUT_CSV = REPORTS / "candidate-source-leakage-audit.csv"
OUTPUT_MD = REPORTS / "candidate-source-leakage-audit.md"


def main() -> int:
    rows = audit_rows()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown(rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 0 if not any(row["status"] == "fail" for row in rows) else 1


def audit_rows() -> list[dict[str, str]]:
    rows = [
        candidate_file_markers_row(),
        manual_adjudication_burden_row(),
        source_product_status_row(),
        source_readiness_status_row(),
        calibrated_claim_boundary_row(),
    ]
    rows.append(summary_row(rows))
    return rows


def candidate_file_markers_row() -> dict[str, str]:
    product_rows = read_csv(REPORTS / "first-wave-source-products.csv")
    candidate_products = [
        row
        for row in product_rows
        if row.get("productStatus") == "candidate_unreviewed"
    ]
    missing_files: list[str] = []
    unmarked_files: list[str] = []
    marker_rows = 0
    total_candidate_rows = 0
    for row in candidate_products:
        expected = row.get("expectedPath", "")
        path = ROOT / expected
        product = row.get("productKey", expected)
        if not expected or not path.exists():
            missing_files.append(product)
            continue
        marked, marked_rows, row_count = candidate_markers(path)
        marker_rows += marked_rows
        total_candidate_rows += row_count
        if not marked:
            unmarked_files.append(product)

    status = "pass" if candidate_products and not missing_files and not unmarked_files else "fail"
    return audit_row(
        "candidate-file-markers",
        status,
        (
            f"candidateProducts={len(candidate_products)}; "
            f"candidateRows={total_candidate_rows}; markerRows={marker_rows}; "
            f"missingFiles={len(missing_files)}; unmarkedFiles={len(unmarked_files)}"
        ),
        "candidateProducts=13; missingFiles=0; unmarkedFiles=0",
        (
            "Candidate-only source-product files retain candidateOnly=true, "
            "candidate_unreviewed, or equivalent manual-review markers."
        ),
        (
            "Do not remove candidate markers until the matching manual promotion "
            "checklist is completed and the source-product/readiness reports are regenerated."
        ),
        details="; ".join([*missing_files, *unmarked_files]),
    )


def manual_adjudication_burden_row() -> dict[str, str]:
    product_rows = read_csv(REPORTS / "first-wave-source-products.csv")
    candidate_products = [
        row
        for row in product_rows
        if row.get("productStatus") == "candidate_unreviewed"
    ]
    target_counts: dict[str, dict[str, int]] = {}
    priority_counts: dict[str, int] = {}
    candidate_rows = 0
    marker_rows = 0
    reviewed_rows = 0
    reviewer_date_gaps = 0
    minimum_row_shortfalls: list[str] = []
    largest_products: list[tuple[int, str]] = []

    for product in candidate_products:
        product_key = product.get("productKey", "")
        target = product.get("targetKey", "unknown")
        priority = product.get("priority", "unknown")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        target_bucket = target_counts.setdefault(
            target,
            {"products": 0, "rows": 0, "markers": 0, "reviewerDateGaps": 0},
        )
        target_bucket["products"] += 1
        path = ROOT / product.get("expectedPath", "")
        if not path.exists() or path.suffix.lower() != ".csv":
            continue
        rows = read_csv(path)
        row_count = len(rows)
        minimum_rows = int_or_zero(product.get("minimumRows", ""))
        marked_rows = 0
        local_reviewer_date_gaps = 0
        for row in rows:
            if row_is_marked_candidate(row):
                marked_rows += 1
            else:
                reviewed_rows += 1
            if reviewer_date_gap(row):
                local_reviewer_date_gaps += 1
        candidate_rows += row_count
        marker_rows += marked_rows
        reviewer_date_gaps += local_reviewer_date_gaps
        target_bucket["rows"] += row_count
        target_bucket["markers"] += marked_rows
        target_bucket["reviewerDateGaps"] += local_reviewer_date_gaps
        largest_products.append((row_count, product_key))
        if row_count < minimum_rows:
            minimum_row_shortfalls.append(
                f"{product_key}:{row_count}/{minimum_rows}"
            )

    largest_products.sort(reverse=True)
    target_summary = "; ".join(
        f"{target}:products={values['products']},rows={values['rows']},markers={values['markers']}"
        for target, values in sorted(target_counts.items())
    )
    priority_summary = "; ".join(
        f"{priority}={count}"
        for priority, count in sorted(priority_counts.items())
    )
    largest_summary = "; ".join(
        f"{product}={count}"
        for count, product in largest_products[:5]
    )
    status = (
        "pass"
        if candidate_products
        and candidate_rows > 0
        and candidate_rows == marker_rows
        and reviewed_rows == 0
        else "fail"
    )
    return audit_row(
        "manual-adjudication-burden",
        status,
        (
            f"candidateProducts={len(candidate_products)}; candidateRows={candidate_rows}; "
            f"markerRows={marker_rows}; reviewedRows={reviewed_rows}; "
            f"reviewerDateGaps={reviewer_date_gaps}; "
            f"minimumRowShortfalls={len(minimum_row_shortfalls)}; priorities={priority_summary}"
        ),
        "candidateRows=markerRows; reviewedRows=0 while candidate gate is active",
        (
            "The remaining empirical work is measurable manual adjudication, not "
            "untracked missingness: candidate files identify source-product rows that "
            "must be reviewed before promotion."
        ),
        (
            "Prioritize the largest P1/P2 candidate products, replace candidate markers "
            "with reviewed source rows, and rerun first-wave source-product, readiness, "
            "candidate-leakage, and artifact gates before strengthening claims."
        ),
        details=(
            f"byTarget: {target_summary} || largestProducts: {largest_summary} || "
            f"minimumRowShortfalls: {'; '.join(minimum_row_shortfalls) or 'none'}"
        ),
    )


def source_product_status_row() -> dict[str, str]:
    product_rows = read_csv(REPORTS / "first-wave-source-products.csv")
    candidate_products = [
        row.get("productKey", "")
        for row in product_rows
        if row.get("productStatus") == "candidate_unreviewed"
    ]
    promoted_candidate_products = [
        row.get("productKey", "")
        for row in product_rows
        if row.get("expectedPath", "").startswith("data/calibration/first-wave/")
        and has_candidate_marker(ROOT / row.get("expectedPath", ""))
        and row.get("productStatus") in {"schema_ready", "text_ready", "ready", "estimation_ready"}
    ]
    invalid_statuses = [
        f"{row.get('productKey', '')}:{row.get('productStatus', '')}"
        for row in product_rows
        if row.get("productStatus") not in {"schema_ready", "text_ready", "candidate_unreviewed"}
    ]
    status = "pass" if len(candidate_products) == 13 and not promoted_candidate_products and not invalid_statuses else "fail"
    return audit_row(
        "source-product-status",
        status,
        (
            f"candidate_unreviewed={len(candidate_products)}; "
            f"promotedCandidateProducts={len(promoted_candidate_products)}; "
            f"invalidStatuses={len(invalid_statuses)}"
        ),
        "candidate_unreviewed=13; promotedCandidateProducts=0",
        "The source-product audit keeps candidate-only worklists out of ready source-product status.",
        "Regenerate first-wave source products after manual review; do not edit report statuses by hand.",
        details="; ".join([*promoted_candidate_products, *invalid_statuses]),
    )


def source_readiness_status_row() -> dict[str, str]:
    readiness_rows = read_csv(REPORTS / "first-wave-source-readiness.csv")
    ready_to_estimate = [
        row.get("targetKey", "")
        for row in readiness_rows
        if any(
            "ready_to_estimate" in row.get(field, "").lower()
            or row.get(field, "").lower() in {"ready", "estimation_ready"}
            for field in ("protocolStatus", "sourceReadiness", "sourceProductGate")
        )
    ]
    unblocked_candidate_gates = [
        row.get("targetKey", "")
        for row in readiness_rows
        if row.get("candidateOnlySourceProducts", "").strip()
        and "candidate_only_blocked" not in row.get("sourceProductGate", "")
    ]
    blocking_misses = [
        row.get("targetKey", "")
        for row in readiness_rows
        if row.get("candidateOnlySourceProducts", "").strip()
        and not row.get("blockingSourceProducts", "").strip()
    ]
    status = "pass" if readiness_rows and not ready_to_estimate and not unblocked_candidate_gates and not blocking_misses else "fail"
    return audit_row(
        "source-readiness-status",
        status,
        (
            f"targets={len(readiness_rows)}; readyToEstimate={len(ready_to_estimate)}; "
            f"unblockedCandidateGates={len(unblocked_candidate_gates)}; "
            f"missingBlockingProducts={len(blocking_misses)}"
        ),
        "readyToEstimate=0; unblockedCandidateGates=0",
        "The first-wave readiness audit keeps candidate-only products from clearing estimation readiness.",
        "Complete the manual adjudication checklists before changing any target to ready_to_estimate.",
        details="; ".join([*ready_to_estimate, *unblocked_candidate_gates, *blocking_misses]),
    )


def calibrated_claim_boundary_row() -> dict[str, str]:
    causal_rows = read_csv(REPORTS / "causal-calibration-targets.csv")
    causal_not_cleared = [
        row.get("targetKey", "")
        for row in causal_rows
        if row.get("policyClaimStatus") == "not_cleared"
    ]
    policy_clearances = [
        row.get("targetKey", "")
        for row in causal_rows
        if row.get("blocksPolicySimulation") == "yes"
        and row.get("policyClaimStatus") != "not_cleared"
    ]
    policy_blockers = [
        row.get("targetKey", "")
        for row in causal_rows
        if row.get("blocksPolicySimulation") == "yes"
        and row.get("policyClaimStatus") == "not_cleared"
    ]
    status = "pass" if causal_rows and policy_blockers and not policy_clearances else "fail"
    return audit_row(
        "calibrated-claim-boundary",
        status,
        (
            "calibratedPolicy=blocked; "
            f"causalNotCleared={len(causal_not_cleared)}; "
            f"policyBlockedTargets={len(policy_blockers)}; "
            f"policyClearances={len(policy_clearances)}"
        ),
        "calibratedPolicy=blocked; policyBlockedTargets>0; policyClearances=0",
        "Candidate-only source worklists do not clear calibrated policy-simulation claims.",
        "Clear causal-calibration targets with reviewed source panels before strengthening policy-effect language.",
        details="; ".join(policy_clearances),
    )


def summary_row(rows: list[dict[str, str]]) -> dict[str, str]:
    failures = [row for row in rows if row["status"] == "fail"]
    return audit_row(
        "summary",
        "pass" if not failures else "fail",
        f"checks={len(rows)}; Failures={len(failures)}",
        "Failures=0",
        "Candidate-only source-product worklists remain blocked from estimation and calibrated policy claims.",
        "Keep this audit in the publication bundle and rerun it after every source-product or readiness edit.",
        details="; ".join(failure["item"] for failure in failures),
    )


def candidate_markers(path: Path) -> tuple[bool, int, int]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        if not rows:
            return False, 0, 0
        marked_rows = 0
        for row in rows:
            if row_is_marked_candidate(row):
                marked_rows += 1
        return marked_rows == len(rows), marked_rows, len(rows)
    lowered = text.lower()
    marked = any(
        marker in lowered
        for marker in ("candidate_unreviewed", "candidate-only", "candidateonly", "does not clear")
    )
    return marked, 1 if marked else 0, 1


def has_candidate_marker(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8").lower()
    return any(
        marker in text
        for marker in ("candidateonly", "candidate_unreviewed", "candidate-only")
    )


def row_is_marked_candidate(row: dict[str, str]) -> bool:
    values = " ".join(str(value) for value in row.values()).lower()
    return (
        row.get("candidateOnly", "").lower() == "true"
        or "candidate_unreviewed" in values
        or "candidate-only" in values
        or "does not clear" in values
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


def int_or_zero(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path) if row.get(key)}


def audit_row(
    item: str,
    status: str,
    value: str,
    threshold: str,
    notes: str,
    next_action: str,
    *,
    details: str = "",
) -> dict[str, str]:
    return {
        "item": item,
        "status": status,
        "value": value,
        "threshold": threshold,
        "notes": notes,
        "nextAction": next_action,
        "details": details,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["item", "status", "value", "threshold", "notes", "nextAction", "details"]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    failures = [row for row in rows if row["status"] == "fail"]
    lines = [
        "# Candidate Source Leakage Audit",
        "",
        (
            "This generated audit verifies that candidate-only first-wave source-product "
            "worklists remain blocked from estimation readiness and calibrated policy-simulation claims."
        ),
        "",
        "## Summary",
        "",
        f"- Overall status: `{'pass' if not failures else 'fail'}`",
        f"- Failures: `{len(failures)}`",
        "- Candidate marker state: `candidate_unreviewed`",
        "- Required readiness boundary: `readyToEstimate=0`",
        "- Required policy boundary: `calibratedPolicy=blocked`",
        "",
        "## Checks",
        "",
        "| Item | Status | Value | Threshold | Notes | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for audit_row in rows:
        lines.append(
            "| {item} | {status} | {value} | {threshold} | {notes} | {nextAction} |".format(
                item=cell(audit_row["item"]),
                status=cell(audit_row["status"]),
                value=cell(audit_row["value"]),
                threshold=cell(audit_row["threshold"]),
                notes=cell(audit_row["notes"]),
                nextAction=cell(audit_row["nextAction"]),
            )
        )
    burden = next((row for row in rows if row["item"] == "manual-adjudication-burden"), None)
    if burden and burden.get("details"):
        lines.extend([
            "",
            "## Manual Adjudication Burden",
            "",
        ])
        for detail in burden["details"].split(" || "):
            lines.append(f"- {detail}")
    if failures:
        lines.extend(["", "## Failure Details", ""])
        for audit_row in failures:
            lines.append(f"- `{audit_row['item']}`: {audit_row.get('details') or audit_row['value']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "Passing this audit does not validate any candidate source product. It only "
                "shows that candidate-only files are still treated as manual-review worklists "
                "and cannot support ready-to-estimate or calibrated policy-effect claims."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
