#!/usr/bin/env python3
"""Summarize which manuscript claim postures are cleared by current evidence."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


REPORTS = Path("reports")
SOURCE_PANEL_INVENTORY = REPORTS / "source-panel-inventory.csv"
CLAIM_BOUNDARY_AUDIT = REPORTS / "claim-boundary-audit.csv"
CLAIM_SOURCE_DEPENDENCY = REPORTS / "claim-source-dependency.csv"
CAUSAL_CALIBRATION_TARGETS = REPORTS / "causal-calibration-targets.csv"
VALIDATION_SUMMARY = REPORTS / "validation-summary.csv"
CALIBRATION_QUEUE = REPORTS / "calibration-queue.csv"
LAYOUT_AUDIT = REPORTS / "paper-layout-audit.md"
VISUAL_AUDIT = REPORTS / "manual-visual-audit.md"

WEAK_STATUSES = {"thin", "warning", "fixture-only", "missing"}
OUT_OF_SCOPE_POLICY_DEPENDENCIES = {"calibrated-policy-simulation"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    panels = read_csv(args.reports / SOURCE_PANEL_INVENTORY.name)
    claim_rows = read_csv(args.reports / CLAIM_BOUNDARY_AUDIT.name)
    dependency_rows = read_csv(args.reports / CLAIM_SOURCE_DEPENDENCY.name)
    causal_rows = read_csv(args.reports / CAUSAL_CALIBRATION_TARGETS.name)
    validation_rows = read_csv(args.reports / VALIDATION_SUMMARY.name)
    calibration_rows = read_csv(args.reports / CALIBRATION_QUEUE.name)
    layout = read_text(args.reports / LAYOUT_AUDIT.name)
    visual = read_text(args.reports / VISUAL_AUDIT.name)

    rows = posture_rows(panels, claim_rows, dependency_rows, causal_rows, validation_rows, calibration_rows, layout, visual)
    write_csv(args.reports / "claim-posture-audit.csv", rows)
    write_markdown(args.reports / "claim-posture-audit.md", rows, panels, claim_rows, dependency_rows, causal_rows, validation_rows, calibration_rows)
    print(f"Wrote {args.reports / 'claim-posture-audit.csv'}")
    print(f"Wrote {args.reports / 'claim-posture-audit.md'}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def posture_rows(
        panels: list[dict[str, str]],
        claim_rows: list[dict[str, str]],
        dependency_rows: list[dict[str, str]],
        causal_rows: list[dict[str, str]],
        validation_rows: list[dict[str, str]],
        calibration_rows: list[dict[str, str]],
        layout: str,
        visual: str,
) -> list[dict[str, str]]:
    counts = validation_counts(validation_rows)
    weak_panels = [row for row in panels if row.get("status") in WEAK_STATUSES]
    bounded_support_panels = [
        row for row in claim_rows
        if row.get("status") == "usable" and row.get("supportLevel") != "direct-bounded"
    ]
    p1_queue_actions = [row for row in calibration_rows if field(row, "priority", "Priority") == "P1"]
    p2_queue_actions = [row for row in calibration_rows if field(row, "priority", "Priority") == "P2"]
    source_gaps = counts.get("source_gap", 0)
    dependency_counts = claim_dependency_counts(dependency_rows)
    article_blocking_dependencies = article_blocking_dependency_rows(dependency_rows)
    layout_pass = "- Failures: `0`" in layout
    visual_pass = bool(visual) and "needs review" not in visual and "Layout audit has not been generated yet" not in visual
    claim_audit_complete = len(claim_rows) == len(panels) and bool(claim_rows)
    dependency_audit_complete = bool(dependency_rows)
    bounded_dependencies = dependency_counts.get("bounded", 0)

    mechanism_status = "cleared" if (
        counts.get("miss", 0) == 0
        and counts.get("unknown", 0) == 0
        and claim_audit_complete
        and dependency_audit_complete
    ) else "needs_revision"
    reproducibility_status = "cleared" if layout_pass and visual_pass else "needs_revision"
    empirical_status = "bounded" if weak_panels or source_gaps or bounded_dependencies else "cleared"
    calibrated_dependency = next(
        (row for row in dependency_rows if row.get("claimKey") == "calibrated-policy-simulation"),
        {},
    )
    causal_blockers = [
        row for row in causal_rows
        if row.get("blocksPolicySimulation", "yes") == "yes"
    ]
    causal_priority_counts = priority_counts(causal_blockers)
    policy_status = "cleared" if calibrated_dependency.get("status") == "cleared" and not causal_blockers else "not_cleared"

    return [
        row(
            "Mechanism-model article",
            mechanism_status,
            (
                f"{counts.get('miss', 0)} validation misses, "
                f"{counts.get('unknown', 0)} unknown validations, "
                f"{len(weak_panels)} weak-status source panels, "
                f"{len(bounded_support_panels)} bounded-support source panels, "
                f"{len(article_blocking_dependencies)} article-blocking dependency claims not cleared"
            ),
            "The manuscript can present a transparent mechanism model and synthetic stress tests under explicit source limits.",
            "Keep empirical language tied to source moments, source gaps, and model diagnostics.",
        ),
        row(
            "Empirical bridge",
            empirical_status,
            (
                f"{source_gaps} source-gap validations, "
                f"{len(weak_panels)} thin, warning, fixture-only, or missing panels, "
                f"{len(bounded_support_panels)} bounded-support source panels"
                f"; {dependency_counts.get('bounded', 0)} bounded claim dependencies"
            ),
            "The bridge constrains plausible ranges and flags evidence gaps; it does not validate hidden-channel magnitudes.",
            "Prioritize SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, nonprofit-routing beyond the top-EIN Schedule I slice, and post-employment revolving-door overlays; broaden electoral-communication and public-financing rows as secondary coverage upgrades.",
        ),
        row(
            "Calibrated policy-simulation claim",
            policy_status,
            (
                f"validation queue P1={len(p1_queue_actions)}, P2={len(p2_queue_actions)}; "
                f"causal targets P1={causal_priority_counts.get('P1', 0)}, "
                f"P2={causal_priority_counts.get('P2', 0)}; "
                f"{dependency_counts.get('not_cleared', 0)} claim dependencies not cleared; "
                f"calibrated-policy dependency={calibrated_dependency.get('status', 'missing')}; "
                f"open causal targets={len(causal_blockers)}"
            ),
            "The current artifact should not claim calibrated reform effects or representative national hidden-channel magnitudes.",
            "Clear the causal-calibration target matrix, add stronger source panels, and rerun validation before using calibrated policy-simulation language.",
        ),
        row(
            "Reproducibility and layout bundle",
            reproducibility_status,
            (
                f"layout failures={0 if layout_pass else 'not cleared'}, "
                f"visual checklist={'pass' if visual_pass else 'not cleared'}"
            ),
            "The generated review bundle is reproducible when the paper artifact gate passes.",
            "Rerun the full artifact gate after any source, table, figure, LaTeX, or package change.",
        ),
    ]


def validation_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {"fit": 0, "partial": 0, "miss": 0, "source_gap": 0, "unknown": 0, "not_applicable": 0}
    for row in rows:
        status = row.get("status", "")
        if status in counts:
            counts[status] += 1
    return counts


def claim_dependency_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {"cleared": 0, "bounded": 0, "not_cleared": 0}
    for row in rows:
        status = row.get("status", "")
        if status in counts:
            counts[status] += 1
    return counts


def article_blocking_dependency_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row for row in rows
        if row.get("status") == "not_cleared"
        and row.get("claimKey") not in OUT_OF_SCOPE_POLICY_DEPENDENCIES
    ]


def priority_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        priority = field(row, "priority", "Priority")
        if priority:
            counts[priority] = counts.get(priority, 0) + 1
    return counts


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
        panels: list[dict[str, str]],
        claim_rows: list[dict[str, str]],
        dependency_rows: list[dict[str, str]],
        causal_rows: list[dict[str, str]],
        validation_rows: list[dict[str, str]],
        calibration_rows: list[dict[str, str]],
) -> None:
    counts = validation_counts(validation_rows)
    weak_panels = [row for row in panels if row.get("status") in WEAK_STATUSES]
    bounded_support_panels = [
        row for row in claim_rows
        if row.get("status") == "usable" and row.get("supportLevel") != "direct-bounded"
    ]
    p1_p2 = [
        row for row in calibration_rows
        if field(row, "priority", "Priority") in {"P1", "P2"}
    ]
    dependency_counts = claim_dependency_counts(dependency_rows)
    causal_blockers = [
        row for row in causal_rows
        if row.get("blocksPolicySimulation", "yes") == "yes"
    ]
    causal_priority_counts = priority_counts(causal_blockers)
    lines = [
        "# Claim Posture Audit",
        "",
        "This audit summarizes which claim posture is cleared by the current source panels, validation results, and generated paper bundle. It is not a substitute for peer review; it is a guardrail against letting the manuscript drift from a mechanism-model article into a calibrated policy-simulation claim.",
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
            "## Validation Counts",
            "",
            f"- Fit: `{counts['fit']}`",
            f"- Partial: `{counts['partial']}`",
            f"- Miss: `{counts['miss']}`",
            f"- Source gap: `{counts['source_gap']}`",
            f"- Unknown: `{counts['unknown']}`",
            f"- Not applicable: `{counts['not_applicable']}`",
            "",
            "## Weak Source Panels",
            "",
            f"- Weak panels: `{len(weak_panels)}`",
        ]
    )
    for panel in weak_panels:
        lines.append(
            f"- `{panel.get('panel', '')}` ({panel.get('status', '')}): {panel.get('note', '')}"
        )
    lines.extend(
        [
            "",
            "## Bounded Support Panels",
            "",
            f"- Bounded-support panels: `{len(bounded_support_panels)}`",
        ]
    )
    for panel in bounded_support_panels:
        lines.append(
            f"- `{panel.get('panel', '')}` ({panel.get('supportLevel', '')}): {panel.get('claimBoundary', '')}"
        )
    lines.extend(
        [
            "",
            "## Claim-Source Dependencies",
            "",
            f"- Cleared claim dependencies: `{dependency_counts['cleared']}`",
            f"- Bounded claim dependencies: `{dependency_counts['bounded']}`",
            f"- Not-cleared claim dependencies: `{dependency_counts['not_cleared']}`",
        ]
    )
    for item in dependency_rows:
        if item.get("status") in {"bounded", "not_cleared"}:
            lines.append(
                f"- `{item.get('claimFamily', '')}` ({item.get('status', '')}): {item.get('sourceSupport', '')}"
            )
    lines.extend(
        [
            "",
            "## Causal Calibration Targets",
            "",
            f"- Blocking targets: `{len(causal_blockers)}`",
            f"- Blocking P1 targets: `{causal_priority_counts.get('P1', 0)}`",
            f"- Blocking P2 targets: `{causal_priority_counts.get('P2', 0)}`",
        ]
    )
    if causal_blockers:
        for item in causal_blockers[:6]:
            lines.append(
                f"- `{item.get('targetKey', '')}` ({item.get('priority', '')}, {item.get('status', '')}): "
                f"{item.get('nextAction', '')}"
            )
        if len(causal_blockers) > 6:
            lines.append(
                f"- Additional blocking targets: `{len(causal_blockers) - 6}`; see `reports/causal-calibration-targets.md`."
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Validation-Queue P1/P2 Actions", ""])
    if not p1_p2:
        lines.append("- None. The validation-calibration queue is clear; calibrated policy-simulation remains blocked by the causal-calibration targets above.")
    for item in p1_p2:
        lines.append(
            "- `{metric}` ({priority}, {category}): {action}".format(
                metric=field(item, "metric", "Metric"),
                priority=field(item, "priority", "Priority"),
                category=field(item, "category", "Category"),
                action=field(item, "recommendedAction", "Action"),
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("|", "\\|")).strip()


def field(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row:
            return row.get(name, "")
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
