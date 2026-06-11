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
        alignments=column_alignments(table_config),
        size=str(table_config.get("size", "small")),
        environment=str(table_config.get("environment", "table")),
        placement=str(table_config.get("placement", "tbp")),
        width=str(table_config.get("width", "\\linewidth")),
        tabcolsep=str(table_config.get("tabcolsep", "3pt")),
        provenance=provenance_comment(selected, source_path, config_path),
    )


def column_alignments(table_config: dict[str, object]) -> list[str]:
    alignments = []
    for index, column in enumerate(table_config["columns"]):
        alignment = str(column.get("align", "l" if index == 0 else "r"))
        if alignment not in {"l", "c", "r"}:
            raise SystemExit(f"Unsupported column alignment for {table_config['output']}: {alignment}")
        alignments.append(alignment)
    return alignments


def select_rows(
        rows: list[dict[str, str]],
        table_config: dict[str, object],
) -> tuple[list[dict[str, str]], dict[str, str] | None]:
    row_mode = table_config.get("rowMode", "listed")
    if row_mode == "all":
        selected = filter_selected_rows(rows, table_config)
        sort_source = table_config.get("sortSource")
        if sort_source:
            selected = sorted(selected, key=lambda row: row.get(str(sort_source), ""))
        limit = int(table_config.get("limit", len(selected)))
        return selected[:limit], None
    indexed = {row["scenarioKey"]: row for row in rows}
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
        sort_source = str(table_config.get("sortSource", "captureRate"))
        selected.sort(key=lambda row: float(row[sort_source]) - float(baseline[sort_source]), reverse=True)
        return selected, baseline
    if row_mode == "substitution-warning-top":
        statuses = set(table_config.get("statuses", [
            "distortion_failure",
            "worse_total_distortion",
            "hidden_capture_warning",
            "hidden_influence_warning",
            "substitution_warning",
        ]))
        selected = [row for row in filter_selected_rows(rows, table_config) if row.get("status") in statuses]
        sort_source = str(table_config.get("sortSource", "warningScore"))
        selected.sort(key=lambda row: (status_rank(row.get("status", "")), float(row.get(sort_source, "0") or "0")), reverse=True)
        limit = int(table_config.get("limit", len(selected)))
        return selected[:limit], None
    raise SystemExit(f"Unknown rowMode for {table_config['output']}: {row_mode}")


def filter_selected_rows(rows: list[dict[str, str]], table_config: dict[str, object]) -> list[dict[str, str]]:
    selected = rows
    exclude_reports = set(str(item) for item in table_config.get("excludeReports", []))
    if exclude_reports:
        selected = [row for row in selected if row.get("report") not in exclude_reports]
    if bool(table_config.get("requireObservedImprovement", False)):
        selected = [row for row in selected if float(row.get("observedCaptureDelta", "0") or "0") < -0.02]
    return selected


def render_cell(column: dict[str, object], row: dict[str, str], baseline: dict[str, str] | None) -> str:
    source = str(column["source"])
    raw_value = value_for(row, source)
    cell_format = str(column.get("format", "text"))
    if cell_format == "label":
        return dict(column.get("labels", {})).get(raw_value, raw_value)
    if cell_format == "float4":
        return f4(raw_value)
    if cell_format == "float3":
        return f"{float(raw_value):.3f}"
    if cell_format == "float3ci":
        lower = str(column["lowerSource"])
        upper = str(column["upperSource"])
        return f"{float(row[source]):.3f} [{float(row[lower]):.3f}, {float(row[upper]):.3f}]"
    if cell_format == "count-ratio":
        denominator_source = str(column["denominatorSource"])
        return f"{int(float(raw_value))}/{int(float(row[denominator_source]))}"
    if cell_format == "delta4":
        if baseline is None:
            raise SystemExit(f"Column {column['header']} requires a baseline row.")
        baseline_source = str(column.get("baselineSource", source))
        return f"{float(row[source]) - float(baseline[baseline_source]):.4f}"
    if cell_format == "signed4":
        value = float(raw_value)
        return f"{value:+.4f}"
    return raw_value


def value_for(row: dict[str, str], source: str) -> str:
    if source in row:
        return row[source]
    if source == "warningScore":
        values = [
            max(0.0, -float(row.get("observedCaptureDelta", "0") or "0")),
            max(0.0, float(row.get("hiddenInfluenceDelta", "0") or "0")),
            max(0.0, float(row.get("hiddenCaptureDelta", "0") or "0")),
            max(0.0, float(row.get("totalInfluenceDistortionDelta", "0") or "0")),
            max(0.0, float(row.get("substitutionRiskDelta", "0") or "0")),
        ]
        return f"{sum(values):.4f}"
    if source == "designLoss":
        values = [
            0.30 * float(row.get("totalInfluenceDistortion", "0") or "0"),
            0.20 * float(row.get("hiddenCaptureIndex", "0") or "0"),
            0.16 * float(row.get("substitutionRisk", "0") or "0"),
            0.10 * float(row.get("administrativeCost", "0") or "0"),
            0.09 * float(row.get("networkOpacityIndex", "0") or "0"),
            0.07 * float(row.get("legitimateAdvocacyChill", "0") or "0"),
            0.06 * float(row.get("speechRestrictionRisk", "0") or "0"),
            -0.05 * float(row.get("crossVenueDetectionIndex", "0") or "0"),
            -0.03 * float(row.get("participationProtectionIndex", "0") or "0"),
        ]
        return f"{max(0.0, sum(values)):.4f}"
    return ""


def status_rank(status: str) -> int:
    return {
        "distortion_failure": 6,
        "worse_total_distortion": 5,
        "hidden_capture_warning": 4,
        "possible_failure": 4,
        "hidden_influence_warning": 3,
        "substitution_warning": 3,
        "visible_channel_warning": 3,
        "channel_shift_tradeoff": 2,
        "substitution_tradeoff": 2,
    }.get(status, 0)


def table(
        label: str,
        caption: str,
        headers: list[str],
        rows: list[list[str]],
        alignments: list[str],
        size: str,
        environment: str,
        placement: str,
        width: str,
        tabcolsep: str,
        provenance: str,
) -> str:
    if environment not in {"table", "table*", "longtable", "inline-table"}:
        raise SystemExit(f"Unsupported table environment: {environment}")
    spec = "".join(alignments)
    if environment == "longtable":
        return longtable(label, caption, headers, rows, size, tabcolsep, provenance, spec)
    if environment == "inline-table":
        return inline_table(label, caption, headers, rows, alignments, size, width, tabcolsep, provenance)
    lines = [
        provenance,
        f"\\begin{{{environment}}}[{placement}]",
        "\\centering",
        f"\\{size}",
        f"\\setlength{{\\tabcolsep}}{{{tabcolsep}}}",
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


def inline_table(
        label: str,
        caption: str,
        headers: list[str],
        rows: list[list[str]],
        alignments: list[str],
        size: str,
        width: str,
        tabcolsep: str,
        provenance: str,
) -> str:
    spec = "".join(alignments)
    lines = [
        provenance,
        "\\begingroup",
        "\\begin{center}",
        f"\\begin{{minipage}}{{{width}}}",
        "\\centering",
        "\\refstepcounter{table}",
        f"\\label{{{label}}}",
        f"\\{size}",
        f"\\setlength{{\\tabcolsep}}{{{tabcolsep}}}",
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
            "\\par\\smallskip",
            f"\\small \\textbf{{\\tablename~\\thetable.}} {escape(caption)}",
            "\\end{minipage}",
            "\\end{center}",
            "\\endgroup",
            "",
        ]
    )
    return "\n".join(lines)


def longtable(
        label: str,
        caption: str,
        headers: list[str],
        rows: list[list[str]],
        size: str,
        tabcolsep: str,
        provenance: str,
        spec: str,
) -> str:
    header = " & ".join(escape(header) for header in headers) + " \\\\"
    lines = [
        provenance,
        "\\begingroup",
        f"\\{size}",
        f"\\setlength{{\\tabcolsep}}{{{tabcolsep}}}",
        f"\\begin{{longtable}}{{{spec}}}",
        f"\\caption{{{escape(caption)}}}\\label{{{label}}}\\\\",
        "\\toprule",
        header,
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        header,
        "\\midrule",
        "\\endhead",
    ]
    for row in rows:
        lines.append(" & ".join(escape(cell) for cell in row) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{longtable}",
            "\\endgroup",
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
