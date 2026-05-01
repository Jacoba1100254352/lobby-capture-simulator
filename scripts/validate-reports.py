#!/usr/bin/env python3
"""Compare report metrics against empirical benchmark plausibility ranges."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


BENCHMARKS = Path("data/calibration/empirical-benchmarks.csv")
REPORTS = Path("reports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", type=Path, default=BENCHMARKS)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=REPORTS)
    args = parser.parse_args()

    benchmarks = read_benchmarks(args.benchmarks)
    report_paths = sorted(args.reports.glob("lobby-capture-*.csv"))
    report_paths = [path for path in report_paths if path.name != "validation-summary.csv"]
    if not report_paths:
        raise SystemExit(f"No report CSVs found in {args.reports}. Run make campaign first.")

    rows = []
    for report in report_paths:
        rows.extend(validate_report(report, benchmarks))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "validation-summary.csv", rows)
    write_markdown(args.output / "validation-summary.md", rows)
    print(f"Wrote {args.output / 'validation-summary.csv'}")
    print(f"Wrote {args.output / 'validation-summary.md'}")
    return 0


def read_benchmarks(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


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
        "notes",
        "validationNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
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
        "| Report | Metric | Observed | Benchmark | Status | Note |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        observed = range_label(row["observedMin"], row["observedMax"])
        benchmark = range_label(row["benchmarkMin"], row["benchmarkMax"])
        lines.append(
            f"| {row['report']} | {row['metric']} | {observed} | {benchmark} | {row['status']} | {row['validationNote']} |"
        )
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
