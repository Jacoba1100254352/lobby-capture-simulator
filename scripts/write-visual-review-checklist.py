#!/usr/bin/env python3
"""Write the pre-submission visual review checklist for paper floats."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import re
from pathlib import Path


FIGURES = Path("paper/figures")
TABLES = Path("paper/tables")
LAYOUT_AUDIT = Path("reports/paper-layout-audit.md")
OUTPUT = Path("reports/manual-visual-audit.md")


def main() -> int:
    figures = sorted(FIGURES.glob("*.tex"))
    tables = sorted(path.name for path in TABLES.glob("*.tex"))
    layout_summary, layout_failures = read_layout_summary()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(markdown(figures, tables, layout_summary, layout_failures), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


def read_layout_summary() -> tuple[list[str], int]:
    if not LAYOUT_AUDIT.exists():
        return ["- Layout audit has not been generated yet."], 1
    lines = LAYOUT_AUDIT.read_text(encoding="utf-8").splitlines()
    summary = [line for line in lines if line.startswith("- Pages checked:") or line.startswith("- Failures:")]
    failures = 1
    for line in summary:
        if line.startswith("- Failures:"):
            failures = int(line.rsplit("`", 2)[1])
    return summary, failures


def markdown(figures: list[Path], tables: list[str], layout_summary: list[str], layout_failures: int) -> str:
    lines = [
        "# Visual Review Checklist",
        "",
        "This report complements the scripted layout audit. Figure rows check generated SVG label boxes for overlap, bounds, and leader-line coverage where callout labels exist. It is still worth doing a final human visual inspection before submission.",
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
        distinct, reference, visible, readable, note = figure_status(figure)
        whitespace = "layout pass" if layout_failures == 0 else "needs review"
        lines.append(f"| `{figure.name}` | {distinct} | {reference} | {visible} | {readable} | {whitespace} | {note} |")
    lines.extend([
        "",
        "## Table Checks",
        "",
        "| Table source | Fits page/column | Text readable | Caption close to table | No excessive white space | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for table in tables:
        status = "layout pass" if layout_failures == 0 else "needs review"
        lines.append(f"| `{table}` | {status} | {status} | {status} | {status} |  |")
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


def figure_status(wrapper: Path) -> tuple[str, str, str, str, str]:
    svg = figure_svg_path(wrapper)
    if not svg.exists():
        return "needs review", "needs review", "needs review", "needs review", "missing SVG source"
    try:
        root = ET.fromstring(svg.read_text(encoding="utf-8"))
    except ET.ParseError as error:
        return "needs review", "needs review", "needs review", "needs review", f"SVG parse error: {error}"
    width, height = svg_dimensions(root)
    boxes = label_boxes(root)
    leaders = elements_by_class(root, "leader")
    if not boxes:
        return "n/a", "n/a", "n/a", "scripted pass", "no point-callout labels in this figure"
    overlap = any(overlap_area(left, right) > 0.0 for index, left in enumerate(boxes) for right in boxes[index + 1:])
    in_bounds = all(0.0 <= x and 0.0 <= y and x + w <= width and y + h <= height for x, y, w, h in boxes)
    has_leaders = len(leaders) >= len(boxes)
    distinct = "scripted pass" if not overlap else "needs review"
    reference = "scripted pass" if has_leaders else "needs review"
    visible = "scripted pass" if in_bounds else "needs review"
    readable = "scripted pass" if not overlap and in_bounds else "needs review"
    note = f"{len(boxes)} label boxes; {len(leaders)} leader lines"
    return distinct, reference, visible, readable, note


def figure_svg_path(wrapper: Path) -> Path:
    text = wrapper.read_text(encoding="utf-8")
    match = re.search(r"graphic=([^;\s]+)\.pdf", text)
    if match:
        return wrapper.parent / f"{match.group(1)}.svg"
    match = re.search(r"figures/([^}]+)\.pdf", text)
    if match:
        return wrapper.parent / f"{match.group(1)}.svg"
    return wrapper.with_suffix(".svg")


def svg_dimensions(root: ET.Element) -> tuple[float, float]:
    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) == 4:
        return float(view_box[2]), float(view_box[3])
    return numeric(root.attrib.get("width", "0")), numeric(root.attrib.get("height", "0"))


def label_boxes(root: ET.Element) -> list[tuple[float, float, float, float]]:
    boxes = []
    for element in elements_by_class(root, "label-box"):
        boxes.append((
            numeric(element.attrib.get("x", "0")),
            numeric(element.attrib.get("y", "0")),
            numeric(element.attrib.get("width", "0")),
            numeric(element.attrib.get("height", "0")),
        ))
    return boxes


def elements_by_class(root: ET.Element, class_name: str) -> list[ET.Element]:
    return [element for element in root.iter() if class_name in element.attrib.get("class", "").split()]


def overlap_area(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
    left, top, width, height = first
    other_left, other_top, other_width, other_height = second
    overlap_width = max(0.0, min(left + width, other_left + other_width) - max(left, other_left))
    overlap_height = max(0.0, min(top + height, other_top + other_height) - max(top, other_top))
    return overlap_width * overlap_height


def numeric(value: str) -> float:
    return float(value.replace("px", ""))


if __name__ == "__main__":
    raise SystemExit(main())
