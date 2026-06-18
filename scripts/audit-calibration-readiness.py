#!/usr/bin/env python3
"""Summarize calibration readiness without blurring manuscript claim boundaries."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


REPORTS = Path("reports")
VALIDATION_SUMMARY = REPORTS / "validation-summary.csv"
CALIBRATION_QUEUE = REPORTS / "calibration-queue.csv"
CLAIM_POSTURE_AUDIT = REPORTS / "claim-posture-audit.csv"
CAUSAL_CALIBRATION_TARGETS = REPORTS / "causal-calibration-targets.csv"
VALIDATION_SCOPE_COVERAGE = REPORTS / "validation-scope-coverage.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    validation_rows = read_csv(args.reports / VALIDATION_SUMMARY.name)
    calibration_rows = read_csv(args.reports / CALIBRATION_QUEUE.name)
    claim_rows = read_csv(args.reports / CLAIM_POSTURE_AUDIT.name)
    causal_rows = read_csv(args.reports / CAUSAL_CALIBRATION_TARGETS.name)
    scope_rows = read_csv(args.reports / VALIDATION_SCOPE_COVERAGE.name)
    rows = readiness_rows(validation_rows, calibration_rows, claim_rows, causal_rows, scope_rows)

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "calibration-readiness.csv", rows)
    write_markdown(args.reports / "calibration-readiness.md", rows, validation_rows, calibration_rows, causal_rows, scope_rows)
    print(f"Wrote {args.reports / 'calibration-readiness.csv'}")
    print(f"Wrote {args.reports / 'calibration-readiness.md'}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def readiness_rows(
        validation_rows: list[dict[str, str]],
        calibration_rows: list[dict[str, str]],
        claim_rows: list[dict[str, str]],
        causal_rows: list[dict[str, str]],
        scope_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    validation = validation_counts(validation_rows)
    by_priority = Counter(row.get("priority", "") for row in calibration_rows)
    by_category = Counter(row.get("category", "") for row in calibration_rows)
    hard_rows = [
        row for row in calibration_rows
        if row.get("priority") in {"P0", "P1", "P2"}
    ]
    p3_rows = [row for row in calibration_rows if row.get("priority") == "P3"]
    unknown_rows = [row for row in validation_rows if row.get("status") == "unknown"]
    miss_rows = [row for row in validation_rows if row.get("status") == "miss"]
    source_gap_rows = [row for row in validation_rows if row.get("status") == "source_gap"]
    not_applicable_rows = [row for row in validation_rows if row.get("status") == "not_applicable"]
    scope_counts = Counter(row.get("status", "") for row in scope_rows)
    mechanism_posture = claim_status(claim_rows, "Mechanism-model article")
    empirical_posture = claim_status(claim_rows, "Empirical bridge")
    empirical_evidence = claim_field(claim_rows, "Empirical bridge", "evidence")
    policy_posture = claim_status(claim_rows, "Calibrated policy-simulation claim")
    causal_blockers = [
        row for row in causal_rows
        if row.get("blocksPolicySimulation", "yes") == "yes"
    ]
    causal_by_priority = Counter(row.get("priority", "") for row in causal_blockers)

    hard_evidence = (
        f"validation_queue P0={by_priority.get('P0', 0)}; "
        f"validation_queue P1={by_priority.get('P1', 0)}; "
        f"validation_queue P2={by_priority.get('P2', 0)}; "
        f"misses={len(miss_rows)}; unknown={len(unknown_rows)}; "
        f"source_gaps={len(source_gap_rows)}; "
        f"causal_targets P1={causal_by_priority.get('P1', 0)}; "
        f"causal_targets P2={causal_by_priority.get('P2', 0)}"
    )
    if hard_rows:
        hard_next = "; ".join(compact_action(row) for row in hard_rows[:4])
    elif policy_posture != "cleared":
        hard_next = "Clear the causal-calibration target matrix and add stronger source panels before using calibrated policy-simulation language."
    else:
        hard_next = "No hard calibration actions remain."

    p3_evidence = "; ".join(
        f"{category}={count}"
        for category, count in sorted(by_category.items())
        if category and any(
            row.get("priority") == "P3" and row.get("category") == category
            for row in p3_rows
        )
    ) or "none"
    scope_evidence = (
        f"not_applicable={len(not_applicable_rows)}; "
        f"covered_elsewhere={scope_counts.get('covered_elsewhere', 0)}; "
        f"partial_elsewhere={scope_counts.get('partial_elsewhere', 0)}; "
        f"coverage_gaps={scope_counts.get('coverage_gap', 0)}"
    )

    return [
        row(
            "mechanism-model-readiness",
            "cleared" if mechanism_posture == "cleared" and not miss_rows and not unknown_rows else "needs_revision",
            (
                f"claimPosture={mechanism_posture or 'missing'}; "
                f"fit={validation.get('fit', 0)}; partial={validation.get('partial', 0)}; "
                f"miss={validation.get('miss', 0)}; unknown={validation.get('unknown', 0)}"
            ),
            "Mechanism-model manuscript claims can proceed when misses and unknowns are zero and claim posture is cleared.",
            "Keep synthetic results framed as mechanism diagnostics under explicit source limits.",
        ),
        row(
            "empirical-bridge-readiness",
            "bounded" if empirical_posture == "bounded" else (
                "cleared" if empirical_posture == "cleared" else "needs_revision"
            ),
            f"claimPosture={empirical_posture or 'missing'}; {empirical_evidence or 'no empirical-bridge evidence row'}",
            "Empirical bridge rows can support distributional anchors and validation-gap diagnostics; bounded status means stronger hidden-channel, procurement-capture, or policy-effect claims remain outside scope.",
            "Clear bounded claim-source dependencies before describing the empirical bridge as fully cleared.",
        ),
        row(
            "calibrated-policy-readiness",
            "blocked" if hard_rows or policy_posture != "cleared" else "cleared",
            f"claimPosture={policy_posture or 'missing'}; {hard_evidence}; open_causal_targets={len(causal_blockers)}",
            "Calibrated policy-simulation claims require both the validation-calibration queue and the independent causal-calibration target matrix to clear.",
            hard_next,
        ),
        row(
            "soft-validation-scope",
            "needs_scope_review" if scope_counts.get("coverage_gap", 0) else (
                "nonblocking" if p3_rows else "cleared"
            ),
            f"P3={len(p3_rows)}; {scope_evidence}; {p3_evidence}",
            "P3 partials and not-applicable rows are validation-scope, scenario-family, or benchmark-review work; they do not by themselves clear or block calibrated empirical claims when the same benchmark is covered elsewhere.",
            "Resolve P3 rows or validation-scope coverage gaps by documenting benchmark scope, splitting scenario families, or adding targeted stress scenarios before treating them as calibration evidence.",
        ),
        row(
            "source-gap-boundary",
            "blocked" if source_gap_rows else "cleared",
            source_gap_summary(source_gap_rows),
            "Source gaps identify evidence panels that cannot test a benchmark directly.",
            "Do not upgrade bounded source moments into empirical validation without representative source rows.",
        ),
    ]


def validation_counts(rows: list[dict[str, str]]) -> Counter[str]:
    return Counter(row.get("status", "") for row in rows)


def claim_status(rows: list[dict[str, str]], gate: str) -> str:
    return claim_field(rows, gate, "status")


def claim_field(rows: list[dict[str, str]], gate: str, field: str) -> str:
    for row in rows:
        if row.get("gate") == gate:
            return row.get(field, "")
    return ""


def compact_action(row: dict[str, str]) -> str:
    metric = row.get("metric", "unknown")
    action = row.get("recommendedAction", "").strip()
    return f"{row.get('priority', '')} {metric}: {action}"


def source_gap_summary(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "source_gaps=0"
    metrics = ", ".join(row.get("metric", "") for row in rows[:4])
    return f"source_gaps={len(rows)}; metrics={metrics}"


def row(gate: str, status: str, evidence: str, claim_boundary: str, next_action: str) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "evidence": evidence,
        "claimBoundary": claim_boundary,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["gate", "status", "evidence", "claimBoundary", "nextAction"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
        path: Path,
        rows: list[dict[str, str]],
        validation_rows: list[dict[str, str]],
        calibration_rows: list[dict[str, str]],
        causal_rows: list[dict[str, str]],
        scope_rows: list[dict[str, str]],
) -> None:
    validation = validation_counts(validation_rows)
    by_priority = Counter(row.get("priority", "") for row in calibration_rows)
    scope_counts = Counter(row.get("status", "") for row in scope_rows)
    causal_blockers = [
        row for row in causal_rows
        if row.get("blocksPolicySimulation", "yes") == "yes"
    ]
    causal_by_priority = Counter(row.get("priority", "") for row in causal_blockers)
    lines = [
        "# Calibration Readiness Audit",
        "",
        "This audit separates hard blockers for calibrated policy-simulation claims from non-blocking validation-scope work. It does not replace peer review or the claim-posture audit.",
        "",
        "## Gate Summary",
        "",
        "| Gate | Status | Evidence | Claim boundary | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {gate} | {status} | {evidence} | {claimBoundary} | {nextAction} |".format(
                **{key: md(value) for key, value in item.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Validation fits: `{validation.get('fit', 0)}`",
            f"- Validation partials: `{validation.get('partial', 0)}`",
            f"- Validation misses: `{validation.get('miss', 0)}`",
            f"- Validation source gaps: `{validation.get('source_gap', 0)}`",
            f"- Validation unknowns: `{validation.get('unknown', 0)}`",
            f"- Validation not applicable: `{validation.get('not_applicable', 0)}`",
            f"- Validation-scope covered elsewhere: `{scope_counts.get('covered_elsewhere', 0)}`",
            f"- Validation-scope coverage gaps: `{scope_counts.get('coverage_gap', 0)}`",
            f"- Validation-queue P0: `{by_priority.get('P0', 0)}`",
            f"- Validation-queue P1: `{by_priority.get('P1', 0)}`",
            f"- Validation-queue P2: `{by_priority.get('P2', 0)}`",
            f"- Validation-queue P3: `{by_priority.get('P3', 0)}`",
            f"- Open causal calibration targets: `{len(causal_blockers)}`",
            f"- Open causal P1 targets: `{causal_by_priority.get('P1', 0)}`",
            f"- Open causal P2 targets: `{causal_by_priority.get('P2', 0)}`",
            "",
            "## P3 Work Queue",
            "",
        ]
    )
    p3_rows = [row for row in calibration_rows if row.get("priority") == "P3"]
    if not p3_rows:
        lines.append("- No P3 calibration-scope rows remain.")
    else:
        for item in p3_rows:
            lines.append(
                f"- `{item.get('metric', '')}` in `{item.get('report', '')}`: "
                f"{item.get('category', '')}; {item.get('recommendedAction', '')}"
            )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
