#!/usr/bin/env python3
"""Summarize empirical source-panel coverage and remaining bridge gaps."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


SOURCE_MOMENTS = Path("reports/source-moments.csv")
OUTPUT = Path("reports")


PANELS = [
    {
        "panel": "Direct dark money",
        "metric": "darkMoneySourceShare",
        "mechanism": "Opaque donor routing and hidden electoral influence",
        "evidenceClass": "proxy/thin",
        "minimum": 0.001,
        "good": 0.05,
        "missing": "no direct DARK_MONEY rows or opaque-capacity bridge rows in the snapshot",
        "action": "Add explicit electioneering/curated dark-money rows where available; use IRS 501(c)(4)/(c)(6) rows only as opaque-capacity proxies and keep Schedule E super PAC rows separate.",
    },
    {
        "panel": "Outside spending",
        "metric": "outsideSpendingRows",
        "mechanism": "Independent expenditure pressure outside candidate finance",
        "evidenceClass": "direct",
        "minimum": 25.0,
        "good": 250.0,
        "missing": "outside-spending bridge is too small",
        "action": "Broaden OpenFEC Schedule E, electioneering communication, independent expenditure, and spender/payee coverage.",
    },
    {
        "panel": "Public financing",
        "metric": "publicFinancingSourceShare",
        "mechanism": "Countervailing campaign finance and voucher/matching funds",
        "evidenceClass": "direct when present",
        "minimum": 0.01,
        "good": 0.10,
        "missing": "public-financing rows are sparse or absent",
        "action": "Add NYC matching-fund, Seattle voucher, and federal public-financing panels as direct program rows.",
    },
    {
        "panel": "Intermediaries",
        "metric": "intermediaryRows",
        "mechanism": "Association, nonprofit, think-tank, and campaign-intermediary capacity",
        "evidenceClass": "proxy",
        "minimum": 5.0,
        "good": 50.0,
        "missing": "intermediary panel is absent or only a schema stub",
        "action": "Expand NYC CFB intermediary and IRS EO BMF rows with IRS 8871/8872, Form 990 XML, association, think-tank, and grantmaking exports.",
    },
    {
        "panel": "Revolving door",
        "metric": "revolvingDoorRows",
        "mechanism": "Post-government access, covered-position links, and cooling-off exposure",
        "evidenceClass": "proxy/thin",
        "minimum": 100.0,
        "good": 500.0,
        "missing": "revolving-door panel is too small",
        "action": "Supplement LDA covered-position rows with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports.",
    },
    {
        "panel": "Procurement identifiers",
        "metric": "procurementKnownPiidShare",
        "mechanism": "Vendor and award-path matching for procurement influence",
        "evidenceClass": "direct identifier coverage",
        "minimum": 0.50,
        "good": 0.90,
        "missing": "PIID coverage is too weak for procurement-network matching",
        "action": "Broaden SAM/FPDS and USAspending enrichment with PIID, UEI, action-date, modification, competition, exclusion, and protest fields.",
    },
    {
        "panel": "Procurement modification risk",
        "metric": "procurementExPostModificationShare",
        "mechanism": "Post-award modification and specification-change pressure",
        "evidenceClass": "proxy/thin",
        "minimum": 0.0,
        "good": 0.05,
        "maximum": 0.40,
        "missing": "modification proxy appears saturated or missing",
        "action": "Separate initial awards from post-award modifications and validate nonzero modification numbers against FPDS transactions.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-moments", type=Path, default=SOURCE_MOMENTS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    moments = read_moments(args.source_moments)
    rows = [panel_row(panel, moments) for panel in PANELS]
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "source-panel-inventory.csv", rows)
    write_markdown(args.output / "source-panel-inventory.md", rows)
    print(f"Wrote {args.output / 'source-panel-inventory.csv'}")
    print(f"Wrote {args.output / 'source-panel-inventory.md'}")
    return 0


def read_moments(path: Path) -> dict[str, dict[str, float]]:
    moments = {"snapshot": {}, "fixture": {}}
    if not path.exists():
        return moments
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            scope = row.get("scope")
            if scope in moments and row.get("metric") and row.get("value"):
                moments[scope][row["metric"]] = float(row["value"])
    return moments


def panel_row(panel: dict[str, object], moments: dict[str, dict[str, float]]) -> dict[str, str]:
    metric = str(panel["metric"])
    value = moments["snapshot"].get(metric)
    fixture_value = moments["fixture"].get(metric)
    fixture_available = fixture_supported(panel, fixture_value)
    if value is None:
        if fixture_available:
            status = "fixture-only"
            note = "snapshot source moment not present; fixture bridge is available for schema and mechanism tests only"
        else:
            status = "missing"
            note = "source moment not present"
    elif value < float(panel["minimum"]):
        if fixture_available:
            status = "fixture-only"
            note = str(panel["missing"]) + "; fixture bridge is available but not article-level empirical coverage"
        else:
            status = "missing"
            note = str(panel["missing"])
    elif "maximum" in panel and value > float(panel["maximum"]):
        status = "warning"
        note = str(panel["missing"])
    elif value >= float(panel["good"]):
        status = "usable"
        note = "coverage is usable for mechanism diagnostics, subject to source-scope limits"
    else:
        status = "thin"
        note = "coverage is present but thin for article-level calibration"
    return {
        "panel": str(panel["panel"]),
        "mechanism": str(panel["mechanism"]),
        "evidenceClass": str(panel["evidenceClass"]),
        "metric": metric,
        "value": "" if value is None else f"{value:.4f}",
        "fixtureValue": "" if fixture_value is None else f"{fixture_value:.4f}",
        "fixtureSupported": "yes" if fixture_available else "no",
        "status": status,
        "note": note,
        "nextAction": str(panel["action"]),
    }


def fixture_supported(panel: dict[str, object], value: float | None) -> bool:
    return value is not None and value >= float(panel["minimum"])


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["panel", "mechanism", "evidenceClass", "metric", "value", "fixtureValue", "fixtureSupported", "status", "note", "nextAction"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ("usable", "thin", "warning", "fixture-only", "missing")}
    lines = [
        "# Source Panel Inventory",
        "",
        "This inventory separates source coverage from simulated outcomes. A missing or thin panel is a validation gap, not evidence that the underlying form of influence is absent.",
        "",
        f"- Usable: `{counts['usable']}`",
        f"- Thin: `{counts['thin']}`",
        f"- Warning: `{counts['warning']}`",
        f"- Fixture-only: `{counts['fixture-only']}`",
        f"- Missing: `{counts['missing']}`",
        "",
        "| Panel | Mechanism constrained | Evidence | Moment | Snapshot | Fixture | Status | Note | Next action |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['panel']} | {row['mechanism']} | {row['evidenceClass']} | `{row['metric']}` | {row['value'] or 'n/a'} | {row['fixtureValue'] or 'n/a'} | {row['status']} | {row['note']} | {row['nextAction']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
