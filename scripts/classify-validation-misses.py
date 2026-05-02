#!/usr/bin/env python3
"""Turn validation misses into an explicit calibration work queue."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


VALIDATION = Path("reports/validation-summary.csv")
SOURCE_MOMENTS = Path("reports/source-moments.csv")
OUTPUT = Path("reports")


CATEGORY_BY_METRIC = {
    "averageDisclosureLag": ("scale-alignment", "separate current-public-visibility lag from historical age of archived filings"),
    "donorInfluenceGini": ("direct-source-moment", "replace report-level proxy with top-k donor/client moments from source tables"),
    "largeDonorDependence": ("model-tuning", "use source large-donor moments and scale campaign finance influence into report state"),
    "darkMoneyTraceability": ("metric-split", "keep all-flow traceability separate from dark-only direct visibility"),
    "hiddenInfluenceShare": ("scenario-coverage", "add stress cases where reforms bind enough to force hidden substitution"),
    "commentUniqueInformationShare": ("model-tuning", "lower unique-information weight for template-heavy dockets"),
    "commentCompressionRate": ("model-tuning", "raise compression under anti-astroturf and duplicate-detection tooling"),
    "commentAuthenticity": ("metric-split", "separate all-comment authenticity from contacted/verified commenter coverage"),
    "detectionRate": ("model-tuning", "increase detection response under enforcement-heavy regimes"),
    "sanctionRate": ("model-tuning", "raise sanction incidence after detection or narrow benchmark to campaign filer cases"),
    "procurementBias": ("direct-source-moment", "add USAspending-style top-recipient and top-agency concentration moments"),
    "revolvingDoorInfluence": ("direct-source-moment", "separate headcount share from modeled influence intensity"),
    "voucherParticipation": ("metric-split", "split resident voucher participation from regime strength"),
    "publicFinancingShare": ("metric-split", "split candidate uptake from public-financing regime strength"),
    "venueSubstitutionRate": ("scenario-coverage", "add cooling-off and advisory-lobbying stress cases"),
}


DIRECT_SOURCE_HINTS = {
    "donorInfluenceGini": "fecDonorTop3Share",
    "largeDonorDependence": "fecLargeDonorWeightedShare",
    "darkMoneyTraceability": "moneyFlowTraceability",
    "commentAuthenticity": "commentAuthenticationShareMean",
    "commentCompressionRate": "commentTemplateShareMean",
    "procurementBias": "procurementRecipientTop3Share",
    "revolvingDoorInfluence": "revolvingDoorFormerOfficialShare",
    "publicFinancingShare": "publicFinancingSourceShare",
    "voucherParticipation": "publicFinancingSourceShare",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", type=Path, default=VALIDATION)
    parser.add_argument("--source-moments", type=Path, default=SOURCE_MOMENTS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    validation_rows = read_rows(args.validation)
    source_moments = read_source_moments(args.source_moments)
    queue = [
        classify(row, source_moments)
        for row in validation_rows
        if row["status"] in {"miss", "partial", "unknown"}
    ]
    queue.sort(key=lambda row: (priority_rank(row["priority"]), row["metric"], row["report"]))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "calibration-queue.csv", queue)
    write_markdown(args.output / "calibration-queue.md", queue)
    print(f"Wrote {args.output / 'calibration-queue.csv'}")
    print(f"Wrote {args.output / 'calibration-queue.md'}")
    return 0


def classify(row: dict[str, str], source_moments: dict[str, str]) -> dict[str, str]:
    metric = row["metric"]
    category, action = CATEGORY_BY_METRIC.get(metric, ("benchmark-review", "decide whether the benchmark applies to this scenario family"))
    source_metric = DIRECT_SOURCE_HINTS.get(metric, "")
    source_value = source_moments.get(source_metric, "") if source_metric else ""
    priority = priority_for(row)
    return {
        "priority": priority,
        "category": category,
        "report": row["report"],
        "metric": metric,
        "status": row["status"],
        "evidenceType": row["evidenceType"],
        "observedRange": range_label(row["observedMin"], row["observedMax"]),
        "benchmarkRange": range_label(row["benchmarkMin"], row["benchmarkMax"]),
        "sourceMetric": source_metric,
        "sourceValue": source_value,
        "recommendedAction": action,
    }


def priority_for(row: dict[str, str]) -> str:
    if row["status"] == "unknown":
        return "P0"
    if row["status"] == "miss" and row["evidenceType"] in {"observed", "observed_proxy", "benchmark"}:
        return "P1"
    if row["status"] == "miss":
        return "P2"
    return "P3"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_source_moments(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    snapshot_rows = [row for row in rows if row["scope"] == "snapshot"]
    return {row["metric"]: row["value"] for row in snapshot_rows}


def priority_rank(priority: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(priority, 4)


def range_label(low: str, high: str) -> str:
    if not low or not high:
        return "n/a"
    return f"{low}-{high}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "priority",
        "category",
        "report",
        "metric",
        "status",
        "evidenceType",
        "observedRange",
        "benchmarkRange",
        "sourceMetric",
        "sourceValue",
        "recommendedAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = Counter(row["category"] for row in rows)
    lines = [
        "# Calibration Queue",
        "",
        "This queue classifies validation misses and partial overlaps into concrete follow-up actions.",
        "",
        "## Category Counts",
        "",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(
        [
            "",
            "| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |",
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        source = f"{row['sourceMetric']}={row['sourceValue']}" if row["sourceMetric"] else ""
        lines.append(
            f"| {row['priority']} | {row['category']} | {row['report']} | `{row['metric']}` | {row['status']} | {row['observedRange']} | {row['benchmarkRange']} | {source} | {row['recommendedAction']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
