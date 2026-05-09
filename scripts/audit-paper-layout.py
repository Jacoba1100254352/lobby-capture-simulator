#!/usr/bin/env python3
"""Audit generated PDFs for sparse float pages and obvious layout regressions."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDFS = [
    Path("paper/main.pdf"),
    Path("paper/regulation-governance-wiley.pdf"),
    Path("paper/supplement.pdf"),
]
OUTPUT = Path("reports/paper-layout-audit.md")


@dataclass(frozen=True)
class PageMetric:
    pdf: Path
    page: int
    width: float
    height: float
    text_blocks: int
    characters: int
    text_coverage: float
    largest_gap: float
    has_float_label: bool
    status: str
    note: str


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", action="append", type=Path, help="PDF to audit. May be repeated.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if shutil.which("pdftohtml") is None:
        raise SystemExit("pdftohtml is required for the paper layout audit.")

    pdfs = args.pdf if args.pdf else DEFAULT_PDFS
    pdfs = [path for path in pdfs if path.exists()]
    if not pdfs:
        raise SystemExit("No generated PDFs found to audit. Run make paper first.")

    metrics: list[PageMetric] = []
    for pdf in pdfs:
        metrics.extend(audit_pdf(pdf))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown(metrics), encoding="utf-8")
    failures = [metric for metric in metrics if metric.status == "fail"]
    print(f"Wrote {args.output}")
    if failures:
        for failure in failures:
            print(
                f"{failure.pdf}:{failure.page}: {failure.note}",
                file=sys.stderr,
            )
        return 1
    return 0


def audit_pdf(path: Path) -> list[PageMetric]:
    xml_text = subprocess.check_output(
        ["pdftohtml", "-xml", "-stdout", str(path)],
        cwd=ROOT,
        text=True,
        stderr=subprocess.DEVNULL,
    )
    root = ET.fromstring(xml_text)
    pages = root.findall("page")
    metrics = []
    for page in pages:
        metrics.append(audit_page(path, page, len(pages)))
    return metrics


def audit_page(path: Path, page: ET.Element, total_pages: int) -> PageMetric:
    page_number = int(page.attrib["number"])
    width = float(page.attrib["width"])
    height = float(page.attrib["height"])
    text_nodes = page.findall("text")
    blocks = []
    text_parts: list[str] = []
    for node in text_nodes:
        text_value = "".join(node.itertext()).strip()
        if not text_value:
            continue
        top = float(node.attrib.get("top", "0"))
        node_height = float(node.attrib.get("height", "0"))
        blocks.append((top, top + node_height))
        text_parts.append(text_value)

    characters = sum(len(value) for value in text_parts)
    coverage = text_coverage(blocks, height)
    gap = largest_vertical_gap(blocks, height)
    joined = " ".join(text_parts)
    has_float_label = "Figure" in joined or "Table" in joined
    status, note = classify_page(page_number, total_pages, characters, coverage, gap, has_float_label)
    return PageMetric(
        pdf=path,
        page=page_number,
        width=width,
        height=height,
        text_blocks=len(blocks),
        characters=characters,
        text_coverage=coverage,
        largest_gap=gap,
        has_float_label=has_float_label,
        status=status,
        note=note,
    )


def classify_page(
        page_number: int,
        total_pages: int,
        characters: int,
        coverage: float,
        largest_gap: float,
        has_float_label: bool,
) -> tuple[str, str]:
    if page_number == 1:
        return "pass", "title/front-matter page"
    if page_number >= max(1, total_pages - 1) and characters >= 900:
        return "pass", "references/declarations page"
    if characters < 450 and coverage < 0.45:
        return "fail", "page is too sparse; likely float-only or mostly blank"
    if has_float_label and characters < 700:
        return "fail", "figure/table page has too little surrounding readable text"
    if largest_gap > 0.62 and characters < 1_600:
        return "fail", "large vertical whitespace gap with little text"
    if coverage < 0.52 and characters < 1_000:
        return "fail", "low page coverage and low text density"
    return "pass", "layout density acceptable"


def text_coverage(blocks: list[tuple[float, float]], page_height: float) -> float:
    if not blocks:
        return 0.0
    return clamp((max(bottom for _top, bottom in blocks) - min(top for top, _bottom in blocks)) / page_height)


def largest_vertical_gap(blocks: list[tuple[float, float]], page_height: float) -> float:
    if not blocks:
        return 1.0
    sorted_blocks = sorted(blocks)
    usable_top = page_height * 0.04
    usable_bottom = page_height * 0.96
    gaps = [max(0.0, sorted_blocks[0][0] - usable_top), max(0.0, usable_bottom - sorted_blocks[-1][1])]
    for (_top, bottom), (next_top, _next_bottom) in zip(sorted_blocks, sorted_blocks[1:]):
        gaps.append(max(0.0, next_top - bottom))
    return clamp(max(gaps) / page_height)


def markdown(metrics: list[PageMetric]) -> str:
    failures = [metric for metric in metrics if metric.status == "fail"]
    lines = [
        "# Paper Layout Audit",
        "",
        "This audit checks generated PDFs for sparse float pages, large whitespace gaps, and figure or table pages without enough surrounding readable text. It is a regression guard, not a substitute for final visual inspection.",
        "",
        f"- Pages checked: `{len(metrics)}`",
        f"- Failures: `{len(failures)}`",
        "",
        "| PDF | Page | Blocks | Chars | Coverage | Largest gap | Float label | Status | Note |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for metric in metrics:
        lines.append(
            f"| {metric.pdf} | {metric.page} | {metric.text_blocks} | {metric.characters} | "
            f"{metric.text_coverage:.3f} | {metric.largest_gap:.3f} | "
            f"{'yes' if metric.has_float_label else 'no'} | {metric.status} | {metric.note} |"
        )
    lines.append("")
    return "\n".join(lines)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


if __name__ == "__main__":
    raise SystemExit(main())
