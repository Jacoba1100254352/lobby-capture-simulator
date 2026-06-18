#!/usr/bin/env python3
"""Audit not-applicable validation rows as explicit scope decisions.

The validation summary can legitimately contain ``not_applicable`` rows when a
scenario-specific benchmark is evaluated against a report that was not designed
to contain that scenario family. This audit makes those rows inspectable and
fails publication checks only when a benchmark has no successful validation
coverage anywhere else in the generated report bundle.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


REPORTS = Path("reports")
VALIDATION_SUMMARY = REPORTS / "validation-summary.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", type=Path, default=VALIDATION_SUMMARY)
    parser.add_argument("--output", type=Path, default=REPORTS)
    args = parser.parse_args()

    validation_rows = read_csv(args.validation)
    rows = coverage_rows(validation_rows)
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "validation-scope-coverage.csv", rows)
    write_markdown(args.output / "validation-scope-coverage.md", rows, validation_rows)
    print(f"Wrote {args.output / 'validation-scope-coverage.csv'}")
    print(f"Wrote {args.output / 'validation-scope-coverage.md'}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def coverage_rows(validation_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows_by_benchmark: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in validation_rows:
        rows_by_benchmark[row.get("benchmarkKey", "")].append(row)

    rows: list[dict[str, str]] = []
    for item in validation_rows:
        if item.get("status") != "not_applicable":
            continue
        benchmark_key = item.get("benchmarkKey", "")
        coverage = [
            row for row in rows_by_benchmark.get(benchmark_key, [])
            if row.get("status") in {"fit", "partial"}
        ]
        fit_coverage = [row for row in coverage if row.get("status") == "fit"]
        if fit_coverage:
            status = "covered_elsewhere"
            action = "No publication-blocking action; this report lacks the scoped scenario family, while the same benchmark is covered elsewhere."
        elif coverage:
            status = "partial_elsewhere"
            action = "Review benchmark scope before treating the partial coverage as calibration support."
        else:
            status = "coverage_gap"
            action = "Add a targeted scenario/report row or remove this benchmark from the active validation map before claiming full scope coverage."
        rows.append(
            {
                "report": item.get("report", ""),
                "benchmarkKey": benchmark_key,
                "metric": item.get("metric", ""),
                "validationScope": item.get("validationScope", ""),
                "evidenceType": item.get("evidenceType", ""),
                "targetKind": item.get("targetKind", ""),
                "status": status,
                "coverageReports": report_list(fit_coverage or coverage),
                "fitCoverageCount": str(len(fit_coverage)),
                "partialCoverageCount": str(len([row for row in coverage if row.get("status") == "partial"])),
                "nextAction": action,
            }
        )
    rows.sort(key=lambda row: (row["status"], row["benchmarkKey"], row["report"]))
    return rows


def report_list(rows: list[dict[str, str]]) -> str:
    reports = sorted({row.get("report", "") for row in rows if row.get("report", "")})
    return "; ".join(reports) if reports else "none"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "report",
        "benchmarkKey",
        "metric",
        "validationScope",
        "evidenceType",
        "targetKind",
        "status",
        "coverageReports",
        "fitCoverageCount",
        "partialCoverageCount",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], validation_rows: list[dict[str, str]]) -> None:
    validation_counts = Counter(row.get("status", "") for row in validation_rows)
    coverage_counts = Counter(row.get("status", "") for row in rows)
    lines = [
        "# Validation Scope Coverage",
        "",
        "This audit explains validation rows marked `not_applicable`. These rows are expected when a scenario-specific benchmark is checked against a report family that does not contain that scenario family. A row is publication-safe only when the same benchmark is covered by a fit or partial row elsewhere in the generated report bundle.",
        "",
        "## Summary",
        "",
        f"- Validation rows: `{len(validation_rows)}`",
        f"- Fit rows: `{validation_counts.get('fit', 0)}`",
        f"- Not-applicable validations: `{validation_counts.get('not_applicable', 0)}`",
        f"- Covered elsewhere: `{coverage_counts.get('covered_elsewhere', 0)}`",
        f"- Partial elsewhere: `{coverage_counts.get('partial_elsewhere', 0)}`",
        f"- Coverage gaps: `{coverage_counts.get('coverage_gap', 0)}`",
        "",
        "## Scope Matrix",
        "",
        "| Report | Benchmark | Metric | Scope | Evidence | Status | Covered by | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if rows:
        for row in rows:
            lines.append(
                "| {report} | {benchmarkKey} | `{metric}` | {validationScope} | {evidenceType}/{targetKind} | {status} | {coverageReports} | {nextAction} |".format(
                    **{key: md(value) for key, value in row.items()}
                )
            )
    else:
        lines.append("|  |  |  |  |  |  |  | No not-applicable validation rows. |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
