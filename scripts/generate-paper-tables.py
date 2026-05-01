#!/usr/bin/env python3
"""Generate LaTeX tables for the paper from report CSV snapshots."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPORTS = Path("reports")
TABLES = Path("paper/tables")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=TABLES)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    campaign_rows = read_report(args.reports / "lobby-capture-campaign.csv")
    sensitivity_rows = read_report(args.reports / "lobby-capture-sensitivity.csv")
    ablation_rows = read_report(args.reports / "lobby-capture-ablation.csv")

    write(args.output / "campaign_snapshot.tex", campaign_table(campaign_rows))
    write(args.output / "sensitivity_snapshot.tex", sensitivity_table(sensitivity_rows))
    write(args.output / "ablation_snapshot.tex", ablation_table(ablation_rows))
    return 0


def campaign_table(rows: list[dict[str, str]]) -> str:
    wanted = [
        "open-access-lobbying",
        "reform-threat-mobilization",
        "full-anti-capture-bundle",
        "bundle-with-evasion",
        "low-salience-technical-rulemaking",
    ]
    selected = by_key(rows, wanted)
    body = [
        [
            label(row["scenarioName"], {"Low-salience technical rulemaking": "Low-salience rulemaking"}),
            f4(row["captureRate"]),
            f4(row["antiCaptureSuccess"]),
            f4(row["defensiveReformSpendShare"]),
            f4(row["darkMoneyShare"]),
            f4(row["clientFundingPerContest"]),
        ]
        for row in selected
    ]
    return table(
        label="tab:first-campaign",
        caption="Current simulation snapshot. Metrics are comparative model outputs, not calibrated empirical estimates.",
        headers=["Scenario", "Capture", "Reform", "Defensive", "Dark money", "Funding"],
        rows=body,
        size="scriptsize",
    )


def sensitivity_table(rows: list[dict[str, str]]) -> str:
    wanted = [
        "sensitivity-public-financing-1-25",
        "sensitivity-public-financing-0-35",
        "sensitivity-evasion-0-00",
        "sensitivity-evasion-0-60",
        "sensitivity-enforcement-0-35",
        "sensitivity-disclosure-0-35",
    ]
    selected = by_key(rows, wanted)
    renames = {
        "Sensitivity public financing 1.25": "Public financing 1.25",
        "Sensitivity public financing 0.35": "Public financing 0.35",
        "Sensitivity evasion 0.00": "Evasion 0.00",
        "Sensitivity evasion 0.60": "Evasion 0.60",
        "Sensitivity enforcement 0.35": "Enforcement 0.35",
        "Sensitivity disclosure 0.35": "Disclosure 0.35",
    }
    body = [
        [
            label(row["scenarioName"], renames),
            f4(row["directionalScore"]),
            f4(row["antiCaptureSuccess"]),
            f4(row["darkMoneyShare"]),
            f4(row["evasionShiftRate"]),
        ]
        for row in selected
    ]
    return table(
        label="tab:sensitivity",
        caption="Selected sensitivity sweep rows. The current bundle is robust in this stylized setup, but evasion freedom strongly shifts spending into opaque channels.",
        headers=["Scenario", "Directional", "Reform success", "Dark-money share", "Evasion shift"],
        rows=body,
        size="small",
    )


def ablation_table(rows: list[dict[str, str]]) -> str:
    baseline = next(row for row in rows if row["scenarioKey"] == "ablation-full-bundle")
    base_capture = float(baseline["captureRate"])
    ablations = [row for row in rows if row["scenarioKey"] != "ablation-full-bundle"]
    ablations.sort(key=lambda row: float(row["captureRate"]) - base_capture, reverse=True)
    renames = {
        "No public advocate or blind review": "Public advocate/blind review",
        "No enforcement": "Enforcement",
        "No public financing or vouchers": "Public financing/vouchers",
        "No beneficial-owner disclosure": "Beneficial-owner disclosure",
        "No cooling-off rules": "Cooling-off rules",
        "No anti-astroturf authentication": "Anti-astroturf authentication",
    }
    body = [
        [
            label(row["scenarioName"], renames),
            f"{float(row['captureRate']) - base_capture:.4f}",
            f4(row["antiCaptureSuccess"]),
            f4(row["darkMoneyShare"]),
            f4(row["commentRecordDistortion"]),
            f4(row["donorInfluenceGini"]),
        ]
        for row in ablations
    ]
    return table(
        label="tab:ablation",
        caption="Selected ablation results. Removing public advocate/blind-review capacity creates the largest modeled capture opening, while removing beneficial-owner disclosure mainly shifts spending toward dark money.",
        headers=["Removed component", "Capture increase", "Reform", "Dark money", "Comment distortion", "Donor Gini"],
        rows=body,
        size="scriptsize",
    )


def table(label: str, caption: str, headers: list[str], rows: list[list[str]], size: str) -> str:
    spec = "l" + ("r" * (len(headers) - 1))
    lines = [
        "\\begin{table}[h]",
        "\\centering",
        f"\\{size}",
        f"\\begin{{tabular}}{{@{{}}{spec}@{{}}}}",
        "\\toprule",
        " & ".join(escape(header) for header in headers) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(escape(cell) for cell in row) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            f"\\caption{{{escape(caption)}}}",
            f"\\label{{{label}}}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def read_report(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def by_key(rows: list[dict[str, str]], keys: list[str]) -> list[dict[str, str]]:
    indexed = {row["scenarioKey"]: row for row in rows}
    missing = [key for key in keys if key not in indexed]
    if missing:
        raise SystemExit(f"Missing report rows for: {', '.join(missing)}")
    return [indexed[key] for key in keys]


def label(value: str, renames: dict[str, str]) -> str:
    return renames.get(value, value)


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
