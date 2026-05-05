#!/usr/bin/env python3
"""Compare report metrics against empirical benchmark plausibility ranges."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


BENCHMARKS = Path("data/calibration/empirical-benchmarks.csv")
PARAMETER_MAP = Path("data/calibration/parameter-map.csv")
REPORTS = Path("reports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", type=Path, default=BENCHMARKS)
    parser.add_argument("--parameter-map", type=Path, default=PARAMETER_MAP)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=REPORTS)
    args = parser.parse_args()

    benchmarks = read_benchmarks(args.benchmarks)
    if args.parameter_map.exists():
        benchmarks.extend(read_parameter_map(args.parameter_map))
    report_paths = sorted(args.reports.glob("lobby-capture-*.csv"))
    report_paths = [path for path in report_paths if path.name != "validation-summary.csv"]
    if not report_paths:
        raise SystemExit(f"No report CSVs found in {args.reports}. Run make campaign first.")

    rows = []
    for report in report_paths:
        rows.extend(validate_report(report, benchmarks))
    substitution_rows = audit_substitution_failures(report_paths)
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "validation-summary.csv", rows)
    write_markdown(args.output / "validation-summary.md", rows)
    write_substitution_csv(args.output / "substitution-audit.csv", substitution_rows)
    write_substitution_markdown(args.output / "substitution-audit.md", substitution_rows)
    print(f"Wrote {args.output / 'validation-summary.csv'}")
    print(f"Wrote {args.output / 'validation-summary.md'}")
    print(f"Wrote {args.output / 'substitution-audit.csv'}")
    print(f"Wrote {args.output / 'substitution-audit.md'}")
    return 0


def read_benchmarks(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = []
        for row in csv.DictReader(source):
            row.setdefault("evidenceType", "benchmark")
            row.setdefault("targetKind", "report_metric")
            rows.append(row)
        return rows


def read_parameter_map(path: Path) -> list[dict[str, str]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row.get("implementationStatus") == "planned":
                continue
            rows.append(
                {
                    "key": "parameter-map:" + row["parameter"],
                    "source": row["sourceReport"],
                    "observable": row["modelTarget"],
                    "metric": row["modelMetric"],
                    "min": row["low"],
                    "max": row["high"],
                    "notes": row["notes"],
                    "evidenceType": row["evidenceType"],
                    "targetKind": row["implementationStatus"],
                }
            )
    return rows


def validate_report(report: Path, benchmarks: list[dict[str, str]]) -> list[dict[str, str]]:
    with report.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        return []
    output = []
    for benchmark in benchmarks:
        metric = benchmark["metric"]
        if metric not in rows[0]:
            output.append(summary_row(report, benchmark, "", "", "unknown", "metric not present in report"))
            continue
        values = [float(row[metric]) for row in rows if row.get(metric, "") != ""]
        if not values:
            output.append(summary_row(report, benchmark, "", "", "unknown", "metric has no values"))
            continue
        observed_min = min(values)
        observed_max = max(values)
        benchmark_min = float(benchmark["min"])
        benchmark_max = float(benchmark["max"])
        if observed_min >= benchmark_min and observed_max <= benchmark_max:
            status = "fit"
            note = "all scenario values inside benchmark range"
        elif observed_max >= benchmark_min and observed_min <= benchmark_max:
            status = "partial"
            note = "some scenario values overlap benchmark range"
        else:
            status = "miss"
            note = "scenario range outside benchmark range"
        output.append(summary_row(report, benchmark, f4(observed_min), f4(observed_max), status, note))
    return output


def audit_substitution_failures(report_paths: list[Path]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for report in report_paths:
        with report.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        if not rows:
            continue
        baseline = baseline_row(rows)
        for row in rows:
            if row is baseline:
                status = "baseline"
            else:
                status = substitution_status(row, baseline)
            output.append(substitution_row(report, row, baseline, status))
    return output


def baseline_row(rows: list[dict[str, str]]) -> dict[str, str]:
    for row in rows:
        if row.get("scenarioKey") == "open-access-lobbying":
            return row
    return max(rows, key=lambda row: metric(row, "visibleLobbyingSpendShare"))


def substitution_status(row: dict[str, str], baseline: dict[str, str]) -> str:
    capture_delta = metric(row, "observedCaptureRate") - metric(baseline, "observedCaptureRate")
    hidden_delta = metric(row, "hiddenInfluenceShare") - metric(baseline, "hiddenInfluenceShare")
    hidden_capture_delta = metric(row, "hiddenCaptureIndex") - metric(baseline, "hiddenCaptureIndex")
    distortion_delta = metric(row, "totalInfluenceDistortion") - metric(baseline, "totalInfluenceDistortion")
    risk_delta = metric(row, "substitutionFailureRisk") - metric(baseline, "substitutionFailureRisk")
    visible_delta = metric(row, "visibleLobbyingSpendShare") - metric(baseline, "visibleLobbyingSpendShare")
    if capture_delta < -0.02 and (hidden_delta > 0.02 or hidden_capture_delta > 0.02 or distortion_delta > 0.02 or risk_delta > 0.02):
        return "possible_failure"
    if visible_delta < -0.02 and (hidden_delta > 0.02 or hidden_capture_delta > 0.02 or risk_delta > 0.02):
        return "substitution_tradeoff"
    if capture_delta < -0.02 and distortion_delta <= 0.02 and risk_delta <= 0.02:
        return "improved"
    if distortion_delta > 0.02:
        return "worse_total_distortion"
    return "no_material_tradeoff"


def substitution_row(report: Path, row: dict[str, str], baseline: dict[str, str], status: str) -> dict[str, str]:
    return {
        "report": report.name,
        "scenarioKey": row.get("scenarioKey", ""),
        "scenarioName": row.get("scenarioName", ""),
        "baselineScenarioKey": baseline.get("scenarioKey", ""),
        "status": status,
        "observedCaptureDelta": delta(row, baseline, "observedCaptureRate"),
        "hiddenInfluenceDelta": delta(row, baseline, "hiddenInfluenceShare"),
        "hiddenCaptureDelta": delta(row, baseline, "hiddenCaptureIndex"),
        "totalInfluenceDistortionDelta": delta(row, baseline, "totalInfluenceDistortion"),
        "substitutionFailureRiskDelta": delta(row, baseline, "substitutionFailureRisk"),
        "visibleLobbyingSpendShareDelta": delta(row, baseline, "visibleLobbyingSpendShare"),
        "intermediarySpendShare": f4(metric(row, "intermediaryShare")),
        "darkMoneySpendShare": f4(metric(row, "darkMoneyShare")),
        "defensiveReformSpendShare": f4(metric(row, "defensiveReformSpendShare")),
        "administrativeCost": f4(metric(row, "administrativeCost")),
    }


def delta(row: dict[str, str], baseline: dict[str, str], key: str) -> str:
    return f4(metric(row, key) - metric(baseline, key))


def metric(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0") or "0")
    except ValueError:
        return 0.0


def summary_row(
        report: Path,
        benchmark: dict[str, str],
        observed_min: str,
        observed_max: str,
        status: str,
        validation_note: str,
) -> dict[str, str]:
    return {
        "report": report.name,
        "benchmarkKey": benchmark["key"],
        "metric": benchmark["metric"],
        "observedMin": observed_min,
        "observedMax": observed_max,
        "benchmarkMin": benchmark["min"],
        "benchmarkMax": benchmark["max"],
        "status": status,
        "source": benchmark["source"],
        "observable": benchmark["observable"],
        "evidenceType": benchmark.get("evidenceType", "benchmark"),
        "targetKind": benchmark.get("targetKind", "report_metric"),
        "notes": benchmark["notes"],
        "validationNote": validation_note,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "report",
        "benchmarkKey",
        "metric",
        "observedMin",
        "observedMax",
        "benchmarkMin",
        "benchmarkMax",
        "status",
        "source",
        "observable",
        "evidenceType",
        "targetKind",
        "notes",
        "validationNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_substitution_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "report",
        "scenarioKey",
        "scenarioName",
        "baselineScenarioKey",
        "status",
        "observedCaptureDelta",
        "hiddenInfluenceDelta",
        "hiddenCaptureDelta",
        "totalInfluenceDistortionDelta",
        "substitutionFailureRiskDelta",
        "visibleLobbyingSpendShareDelta",
        "intermediarySpendShare",
        "darkMoneySpendShare",
        "defensiveReformSpendShare",
        "administrativeCost",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ("fit", "partial", "miss", "unknown")}
    lines = [
        "# Validation Summary",
        "",
        "Benchmark ranges are plausibility checks, not causal empirical claims.",
        "",
        f"- Fit: `{counts['fit']}`",
        f"- Partial: `{counts['partial']}`",
        f"- Miss: `{counts['miss']}`",
        f"- Unknown: `{counts['unknown']}`",
        "",
        "## Evidence Classes",
        "",
    ]
    for evidence_type in sorted({row["evidenceType"] for row in rows}):
        evidence_rows = [row for row in rows if row["evidenceType"] == evidence_type]
        fit = sum(1 for row in evidence_rows if row["status"] == "fit")
        partial = sum(1 for row in evidence_rows if row["status"] == "partial")
        miss = sum(1 for row in evidence_rows if row["status"] == "miss")
        unknown = sum(1 for row in evidence_rows if row["status"] == "unknown")
        lines.append(f"- `{evidence_type}`: fit `{fit}`, partial `{partial}`, miss `{miss}`, unknown `{unknown}`")
    lines.extend([
        "",
        "| Report | Metric | Observed | Benchmark | Status | Note |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ])
    for row in rows:
        observed = range_label(row["observedMin"], row["observedMax"])
        benchmark = range_label(row["benchmarkMin"], row["benchmarkMax"])
        lines.append(
            f"| {row['report']} | {row['metric']} | {observed} | {benchmark} | {row['status']} | {row['validationNote']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_substitution_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {
        status: sum(1 for row in rows if row["status"] == status)
        for status in ("possible_failure", "substitution_tradeoff", "worse_total_distortion", "improved", "no_material_tradeoff", "baseline")
    }
    lines = [
        "# Substitution Audit",
        "",
        "This audit treats lower observed capture as insufficient when hidden influence, hidden capture, total distortion, or substitution failure risk rises. It is a diagnostic over synthetic simulation reports, not an empirical causal claim.",
        "",
        f"- Possible failure: `{counts['possible_failure']}`",
        f"- Substitution tradeoff: `{counts['substitution_tradeoff']}`",
        f"- Worse total distortion: `{counts['worse_total_distortion']}`",
        f"- Improved: `{counts['improved']}`",
        f"- No material tradeoff: `{counts['no_material_tradeoff']}`",
        "",
        "## Flagged Rows",
        "",
        "| Report | Scenario | Status | Capture delta | Hidden delta | Hidden capture delta | Total distortion delta | Risk delta | Visible spend delta | Intermediary | Dark money | Defensive | Admin |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    flagged = [
        row for row in rows
        if row["status"] in {"possible_failure", "substitution_tradeoff", "worse_total_distortion"}
    ]
    for row in flagged:
        lines.append(
            f"| {row['report']} | {row['scenarioName']} | {row['status']} | "
            f"{row['observedCaptureDelta']} | {row['hiddenInfluenceDelta']} | "
            f"{row['hiddenCaptureDelta']} | {row['totalInfluenceDistortionDelta']} | "
            f"{row['substitutionFailureRiskDelta']} | {row['visibleLobbyingSpendShareDelta']} | "
            f"{row['intermediarySpendShare']} | {row['darkMoneySpendShare']} | "
            f"{row['defensiveReformSpendShare']} | {row['administrativeCost']} |"
        )
    if not flagged:
        lines.append("| n/a | n/a | no flagged rows |  |  |  |  |  |  |  |  |  |  |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def range_label(low: str, high: str) -> str:
    if not low or not high:
        return "n/a"
    return f"{low}-{high}"


def f4(value: float) -> str:
    return f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
