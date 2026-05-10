#!/usr/bin/env python3
"""Write the pre-submission visual review checklist for paper floats."""

from __future__ import annotations

from pathlib import Path


FIGURES = Path("paper/figures")
TABLES = Path("paper/tables")
LAYOUT_AUDIT = Path("reports/paper-layout-audit.md")
OUTPUT = Path("reports/manual-visual-audit.md")


def main() -> int:
    figures = sorted(path.name for path in FIGURES.glob("*.tex"))
    tables = sorted(path.name for path in TABLES.glob("*.tex"))
    layout_summary = read_layout_summary()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(markdown(figures, tables, layout_summary), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


def read_layout_summary() -> list[str]:
    if not LAYOUT_AUDIT.exists():
        return ["- Layout audit has not been generated yet."]
    lines = LAYOUT_AUDIT.read_text(encoding="utf-8").splitlines()
    return [line for line in lines if line.startswith("- Pages checked:") or line.startswith("- Failures:")]


def markdown(figures: list[str], tables: list[str], layout_summary: list[str]) -> str:
    lines = [
        "# Manual Visual Review Checklist",
        "",
        "This is the human visual-review pass that complements the scripted layout audit. It exists to keep figure and table placement, label readability, and float whitespace from becoming invisible process debt.",
        "",
        "## Current Automated Layout Summary",
        "",
        *layout_summary,
        "",
        "## Figure Checks",
        "",
        "| Figure source | Labels distinct | Labels near/reference point | Labels visible | Readable in PDF | Float whitespace acceptable | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for figure in figures:
        lines.append(f"| `{figure}` | pending | pending | pending | pending | pending |  |")
    lines.extend([
        "",
        "## Table Checks",
        "",
        "| Table source | Fits page/column | Text readable | Caption close to table | No excessive white space | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for table in tables:
        lines.append(f"| `{table}` | pending | pending | pending | pending |  |")
    lines.extend([
        "",
        "## Review Standard",
        "",
        "- Every point label in scatter or tradeoff figures should be distinct, non-overlapping, completely visible, and connected to the intended point by proximity or a leader line.",
        "- Figure pages should include enough surrounding readable text that a float does not create a mostly blank page.",
        "- Tables should avoid unreadable shrinkage; if a table requires extreme compression, move detail to the supplement or split the table.",
        "- The final review should be rerun after any change to generated reports, tables, figures, LaTeX wrappers, or journal template files.",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
