#!/usr/bin/env python3
"""Generate LaTeX tables for the paper from report CSV snapshots."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REPORTS = Path("reports")
TABLES = Path("paper/tables")
CONFIG = Path("paper/tables.yml")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=TABLES)
    parser.add_argument("--config", type=Path, default=CONFIG)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    config = read_config(args.config)
    for table_config in config["tables"]:
        source_path = args.reports / table_config["source"]
        rows = read_report(source_path)
        selected, baseline = select_rows(rows, table_config)
        content = render_configured_table(table_config, selected, baseline, source_path, args.config)
        write(args.output / table_config["output"], content)
    return 0


def render_configured_table(
        table_config: dict[str, object],
        selected: list[dict[str, str]],
        baseline: dict[str, str] | None,
        source_path: Path,
        config_path: Path,
) -> str:
    body = []
    for row in selected:
        body.append([render_cell(column, row, baseline) for column in table_config["columns"]])
    return table(
        label=str(table_config["label"]),
        caption=str(table_config["caption"]),
        headers=[str(column["header"]) for column in table_config["columns"]],
        rows=body,
        size=str(table_config.get("size", "small")),
        environment=str(table_config.get("environment", "table")),
        placement=str(table_config.get("placement", "tbp")),
        width=str(table_config.get("width", "\\linewidth")),
        provenance=provenance_comment(selected, source_path, config_path),
    )


def select_rows(
        rows: list[dict[str, str]],
        table_config: dict[str, object],
) -> tuple[list[dict[str, str]], dict[str, str] | None]:
    indexed = {row["scenarioKey"]: row for row in rows}
    row_mode = table_config.get("rowMode", "listed")
    if row_mode == "listed":
        keys = list(table_config["rows"])
        missing = [key for key in keys if key not in indexed]
        if missing:
            raise SystemExit(f"Missing report rows for {table_config['output']}: {', '.join(missing)}")
        return [indexed[key] for key in keys], None
    if row_mode == "ablation-delta":
        baseline_key = str(table_config["baseline"])
        if baseline_key not in indexed:
            raise SystemExit(f"Missing ablation baseline for {table_config['output']}: {baseline_key}")
        baseline = indexed[baseline_key]
        selected = [row for row in rows if row["scenarioKey"] != baseline_key]
        selected.sort(key=lambda row: float(row["captureRate"]) - float(baseline["captureRate"]), reverse=True)
        return selected, baseline
    raise SystemExit(f"Unknown rowMode for {table_config['output']}: {row_mode}")


def render_cell(column: dict[str, object], row: dict[str, str], baseline: dict[str, str] | None) -> str:
    source = str(column["source"])
    cell_format = str(column.get("format", "text"))
    if cell_format == "label":
        return dict(column.get("labels", {})).get(row[source], row[source])
    if cell_format == "float4":
        return f4(row[source])
    if cell_format == "float3":
        return f"{float(row[source]):.3f}"
    if cell_format == "float3ci":
        lower = str(column["lowerSource"])
        upper = str(column["upperSource"])
        return f"{float(row[source]):.3f} [{float(row[lower]):.3f}, {float(row[upper]):.3f}]"
    if cell_format == "count-ratio":
        denominator_source = str(column["denominatorSource"])
        return f"{int(float(row[source]))}/{int(float(row[denominator_source]))}"
    if cell_format == "delta4":
        if baseline is None:
            raise SystemExit(f"Column {column['header']} requires a baseline row.")
        baseline_source = str(column.get("baselineSource", source))
        return f"{float(row[source]) - float(baseline[baseline_source]):.4f}"
    return row[source]


def table(
        label: str,
        caption: str,
        headers: list[str],
        rows: list[list[str]],
        size: str,
        environment: str,
        placement: str,
        width: str,
        provenance: str,
) -> str:
    if environment not in {"table", "table*"}:
        raise SystemExit(f"Unsupported table environment: {environment}")
    spec = "l" + ("r" * (len(headers) - 1))
    lines = [
        provenance,
        f"\\begin{{{environment}}}[{placement}]",
        "\\centering",
        f"\\{size}",
        "\\setlength{\\tabcolsep}{4pt}",
        f"\\begin{{tabular*}}{{{width}}}{{@{{\\extracolsep{{\\fill}}}}{spec}@{{}}}}",
        "\\toprule",
        " & ".join(escape(header) for header in headers) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(escape(cell) for cell in row) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular*}",
            f"\\caption{{{escape(caption)}}}",
            f"\\label{{{label}}}",
            f"\\end{{{environment}}}",
            "",
        ]
    )
    return "\n".join(lines)


def provenance_comment(rows: list[dict[str, str]], source_path: Path, config_path: Path) -> str:
    first = rows[0] if rows else {}
    parts = [
        "% Generated by scripts/generate-paper-tables.py",
        f"source={source_path}",
        f"config={config_path}",
    ]
    for key in ("generatedAt", "seed", "runs", "contestsPerRun"):
        if first.get(key):
            label = "reportGeneratedAt" if key == "generatedAt" else key
            parts.append(f"{label}={first[key]}")
    return "; ".join(parts)


def read_config(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def read_report(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def f4(value: str) -> str:
    return f"{float(value):.4f}"


def escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    raise SystemExit(main())
