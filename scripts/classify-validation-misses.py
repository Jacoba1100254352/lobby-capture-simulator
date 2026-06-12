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
    "averageDisclosureLag": ("scale-alignment", "legacy blended visibility lag; use lobbyingDisclosureLag and campaignDisclosureLag for source-specific validation"),
    "lobbyingDisclosureLag": ("scale-alignment", "compare modeled lobbying visibility lag against LDA timing ranges while keeping raw archived source age in source moments"),
    "campaignDisclosureLag": ("scale-alignment", "compare modeled campaign visibility lag against FEC timing ranges while keeping lobbying visibility separate"),
    "donorInfluenceGini": ("direct-source-moment", "replace report-level proxy with top-k donor/client moments from source tables"),
    "largeDonorDependence": ("model-tuning", "inspect remaining campaign/outside rows and tune allocation-to-source concentration only where high-end outside spending is intended"),
    "darkMoneyTraceability": ("metric-split", "keep all-flow traceability separate from dark-only direct visibility"),
    "darkMoneyDirectVisibility": ("direct-source-moment", "replace thin proxy rows with direct hidden-donor or nonprofit-routing source records; keep electioneering rows separate from hidden-donor evidence"),
    "darkMoneyDirectRoutingRows": ("direct-source-moment", "add non-proxy direct hidden-donor, transfer, or nonprofit-routing records; keep IRS EO BMF capacity proxies and electoral-communication rows separate"),
    "hiddenInfluenceShare": ("scenario-coverage", "add stress cases where reforms bind enough to force hidden substitution"),
    "commentUniqueInformationShare": ("model-tuning", "lower unique-information weight for template-heavy dockets"),
    "commentCompressionRate": ("model-tuning", "raise compression under anti-astroturf and duplicate-detection tooling"),
    "commentAuthenticity": ("metric-split", "separate all-comment authenticity from contacted/verified commenter coverage"),
    "detectionRate": ("metric-split", "split narrow reporting-error incidence from broader modeled detection under enforcement-heavy regimes"),
    "sanctionRate": ("model-tuning", "raise sanction incidence after detection or narrow benchmark to campaign filer cases"),
    "procurementBias": ("direct-source-moment", "use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration"),
    "procurementAgencyTop1Share": ("direct-source-moment", "replace the bounded USAspending concentration panel with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated"),
    "procurementRecipientTop3Share": ("direct-source-moment", "compare recipient concentration against the bounded procurement concentration panel, then broaden by award type and fiscal year before treating it as calibrated"),
    "procurementSingleBidShare": ("direct-source-moment", "fill SAM/FPDS competition fields and compare single-bid exposure against the procurement bridge target"),
    "procurementExPostModificationShare": ("direct-source-moment", "broaden the bounded USAspending action panel with representative SAM/FPDS action histories that support transaction-row, distinct-award, and amount-weighted denominators before treating modification incidence as calibrated"),
    "revolvingDoorInfluence": ("direct-source-moment", "replace fixture rows with a documented personnel/export panel and keep headcount share separate from modeled influence intensity"),
    "voucherParticipation": ("metric-split", "split resident voucher participation from regime strength"),
    "publicFinancingShare": ("metric-split", "split candidate uptake from public-financing regime strength"),
    "venueSubstitutionRate": ("scenario-coverage", "add cooling-off and advisory-lobbying stress cases"),
    "networkOpacityIndex": ("direct-source-moment", "anchor with source-network panels that connect LDA, FEC, IRS/nonprofit, docket, procurement, and revolving-door identifiers"),
    "intermediaryCentrality": ("direct-source-moment", "anchor intermediary routing with nonprofit, 527, association, think-tank, and sponsored-expert source panels"),
    "procurementNetworkExposure": ("direct-source-moment", "anchor procurement exposure with UEI/PIID coverage, single-bid share, and ex-post modification moments"),
    "revolvingDoorBridgeIndex": ("direct-source-moment", "anchor revolving-door bridges with documented personnel movement rows and source-match confidence"),
    "venueShiftNetworkLoad": ("scenario-coverage", "add venue-shifting detection stress cases and source panels for alternate venues"),
    "crossVenueDetectionIndex": ("benchmark-review", "treat as a synthetic portfolio capability until linked source coverage is measured"),
    "participationProtectionIndex": ("benchmark-review", "separate representation equalization from restrictions on participation"),
    "speechRestrictionRisk": ("benchmark-review", "bound legal and civil-liberties risk with reform-specific evidence"),
}


DIRECT_SOURCE_HINTS = {
    "donorInfluenceGini": "fecDonorTop3Share",
    "largeDonorDependence": "fecLargeDonorWeightedShare",
    "darkMoneyTraceability": "moneyFlowTraceability",
    "darkMoneyDirectVisibility": "darkMoneyDirectVisibility",
    "darkMoneyDirectRoutingRows": "darkMoneyDirectRoutingRows",
    "commentAuthenticity": "commentAuthenticationShareMean",
    "commentCompressionRate": "commentTemplateShareMean",
    "procurementBias": "procurementAmountWeightedSingleBidShare",
    "procurementAgencyTop1Share": "procurementAgencyTop1Share",
    "procurementRecipientTop3Share": "procurementRecipientTop3Share",
    "procurementSingleBidShare": "procurementSingleBidShare",
    "procurementExPostModificationShare": "procurementExPostModificationShare",
    "revolvingDoorInfluence": "revolvingDoorFormerOfficialShare",
    "publicFinancingShare": "publicFinancingSourceShare",
    "voucherParticipation": "publicFinancingSourceShare",
    "networkOpacityIndex": "intermediaryDonorDisclosureMean",
    "intermediaryCentrality": "intermediaryPoliticalSpendShare",
    "procurementNetworkExposure": "procurementKnownUeiShare",
    "revolvingDoorBridgeIndex": "revolvingDoorInfluenceWeightedFormerOfficialShare",
    "venueShiftNetworkLoad": "venueShiftNetworkLoad",
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
        if row["status"] in {"miss", "partial", "unknown", "source_gap"}
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
    category, action = refine_partial_action(row, category, action)
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


def refine_partial_action(row: dict[str, str], category: str, action: str) -> tuple[str, str]:
    if row["status"] != "partial" or category != "scenario-coverage":
        return category, action
    observed_min = as_float(row.get("observedMin"))
    observed_max = as_float(row.get("observedMax"))
    benchmark_min = as_float(row.get("benchmarkMin"))
    benchmark_max = as_float(row.get("benchmarkMax"))
    if None in {observed_min, observed_max, benchmark_min, benchmark_max}:
        return category, action
    if observed_min < benchmark_min and observed_max > benchmark_max:
        return (
            "scenario-family-split",
            "split baseline, substitution-stress, and extreme-stress scenarios before using this benchmark as a single calibration target",
        )
    if observed_max < benchmark_max and observed_min < benchmark_min:
        return (
            "scenario-coverage",
            "add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor",
        )
    if observed_min > benchmark_min and observed_max > benchmark_max:
        return (
            "benchmark-review",
            "treat the current scoped rows as an extreme-stress family or raise the benchmark only with source evidence",
        )
    return category, action


def as_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def priority_for(row: dict[str, str]) -> str:
    if row["status"] == "unknown":
        return "P0"
    if row["status"] == "source_gap" and row["evidenceType"] in {"observed", "observed_proxy", "benchmark"}:
        return "P1"
    if row["status"] == "source_gap":
        return "P2"
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
