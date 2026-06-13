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
        "metric": "darkMoneyDirectRoutingRows",
        "mechanism": "Opaque donor routing and hidden electoral influence",
        "evidenceClass": "direct/proxy gap",
        "minimum": 1.0,
        "good": 50.0,
        "missing": "no non-proxy direct DARK_MONEY routing rows in the snapshot",
        "thin": "direct DARK_MONEY routing rows are present but too sparse for article-level calibration",
        "action": "Add curated direct dark-money or nonprofit-routing rows where available; use IRS 501(c)(4)/(c)(6) rows only as opaque-capacity proxies and keep Schedule E, electioneering, and communication-cost rows separate.",
    },
    {
        "panel": "Outside spending",
        "metric": "outsideSpendingRows",
        "mechanism": "Independent expenditure pressure outside candidate finance",
        "evidenceClass": "direct",
        "minimum": 25.0,
        "good": 250.0,
        "missing": "outside-spending bridge is too small",
        "action": "Broaden OpenFEC Schedule E, electioneering communication, communication-cost, independent-expenditure, and spender/payee coverage.",
    },
    {
        "panel": "Electoral communications",
        "metric": "electoralCommunicationRows",
        "mechanism": "Electioneering and communication-cost channels outside ordinary receipts",
        "evidenceClass": "direct",
        "minimum": 1.0,
        "good": 50.0,
        "missing": "no electioneering or communication-cost rows in the pinned snapshot",
        "action": "Broaden OpenFEC electioneering and communication-cost coverage and keep these rows separate from direct dark-money evidence.",
    },
    {
        "panel": "Public financing",
        "metric": "publicFinancingProgramCount",
        "mechanism": "Countervailing campaign finance and voucher/matching funds",
        "evidenceClass": "direct program rows when present",
        "minimum": 1.0,
        "good": 2.0,
        "missing": "public-financing program rows are sparse or absent",
        "thin": "only one public-financing program source is represented; add a second local, state, or federal program before using the panel as a cross-program mechanism anchor",
        "action": "Broaden NYC matching-fund and Seattle voucher rows with federal, state, and additional local public-financing panels before treating uptake as representative.",
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
        "panel": "IRS 527 political organizations",
        "metric": "intermediary527Rows",
        "mechanism": "Political-organization receipts and disbursements for campaign-adjacent intermediaries",
        "evidenceClass": "direct observed 527 filings",
        "minimum": 1.0,
        "good": 100.0,
        "missing": "no source-native IRS POFD Form 8872 rows in the pinned snapshot",
        "action": "Broaden beyond the default bounded IRS POFD alphabetic slice, preserve the electronic-filing scope note, and keep 527 political-organization rows separate from 501(c)(4)/(c)(6) hidden-donor evidence.",
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
        "panel": "Procurement concentration panel",
        "metric": "procurementConcentrationPanelAgencyCount",
        "mechanism": "Multi-agency vendor and agency concentration diagnostics",
        "evidenceClass": "denominator-mapped public bulk panel",
        "minimum": 2.0,
        "good": 10.0,
        "missing": "multi-agency procurement concentration panel is absent",
        "thin": "bounded procurement concentration panel is present, but benchmark mapping should remain denominator-specific",
        "action": "Use the procurement benchmark crosswalk for aggregate, agency, award-type, and agency-award-type concentration diagnostics; retain SAM/FPDS exports for exclusions, protests, and coding overlays.",
    },
    {
        "panel": "Procurement action history",
        "metric": "procurementActionRows",
        "mechanism": "Transaction/action denominator for post-award modification incidence",
        "evidenceClass": "direct primary SAM/USAspending action rows when present",
        "minimum": 1.0,
        "good": 50.0,
        "missing": "no USAspending/SAM/FPDS transaction/action rows in the pinned snapshot",
        "action": "Use the archived USAspending bulk summary for action-row, distinct-award, and amount-weighted denominators; add SAM/FPDS action-history extracts to crosswalk modification coding before treating modification incidence as calibration-grade.",
    },
    {
        "panel": "Procurement modification risk",
        "metric": "procurementExPostModificationShare",
        "mechanism": "Post-award modification and specification-change pressure",
        "evidenceClass": "denominator-mapped observed proxy",
        "minimum": 0.0,
        "good": 0.10,
        "maximum": 0.90,
        "missing": "modification-action share is outside the benchmark range, likely reflecting bounded action-sample scope or nonrepresentative transaction coverage",
        "thin": "archived USAspending bulk rows are present, but modification incidence should remain denominator-specific until crosswalked against SAM/FPDS coding",
        "warningMetric": "procurementLatestTransactionModificationProxy",
        "warningAbsentMetric": "procurementActionRows",
        "warning": "latest-transaction modification enrichment is available but an action-level transaction denominator is still absent",
        "contextMetrics": [
            ("procurementModifiedAwardShare", "distinct-award share"),
            ("procurementAmountWeightedModificationShare", "amount-weighted share"),
        ],
        "action": "Use the procurement benchmark crosswalk for action-row, distinct-award, and amount-weighted denominators; add SAM/FPDS exports to reconcile coding before claiming causal procurement-modification effects.",
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
    elif panel_warning(panel, moments):
        status = "warning"
        note = str(panel["warning"])
    elif "maximum" in panel and value > float(panel["maximum"]):
        status = "warning"
        note = str(panel["missing"])
    elif panel.get("lowerIsBetter") and value > float(panel["good"]):
        status = "thin"
        note = str(panel.get("thin", "coverage is present, but the observed diagnostic remains too high for article-level calibration"))
    elif value >= float(panel["good"]):
        status = "usable"
        note = "coverage is usable for mechanism diagnostics, subject to source-scope limits"
    else:
        status = "thin"
        note = str(panel.get("thin", "coverage is present but thin for article-level calibration"))
    context_note = context_metrics_note(panel, moments)
    if context_note:
        note = f"{note}; {context_note}"
    row = {
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
    row["supportLevel"] = support_level(row)
    return row


def support_level(row: dict[str, str]) -> str:
    status = row.get("status", "missing")
    if status in {"missing", "fixture-only"}:
        return "schema-only"
    if status in {"warning", "thin"}:
        return status
    if status != "usable":
        return "limited"

    evidence = row.get("evidenceClass", "").lower()
    if "proxy/thin" in evidence:
        return "proxy-thin"
    if "direct/proxy" in evidence:
        return "direct-proxy-bounded"
    if "denominator-mapped" in evidence:
        return "denominator-bounded"
    if "proxy" in evidence:
        return "proxy-bounded"
    if "program" in evidence:
        return "program-bounded"
    if "when present" in evidence:
        return "conditional-direct"
    if "direct" in evidence:
        return "direct-bounded"
    return "source-bounded"


def fixture_supported(panel: dict[str, object], value: float | None) -> bool:
    return value is not None and value >= float(panel["minimum"])


def panel_warning(panel: dict[str, object], moments: dict[str, dict[str, float]]) -> bool:
    metric = panel.get("warningMetric")
    if not metric:
        return False
    absent_metric = panel.get("warningAbsentMetric")
    if absent_metric and moments["snapshot"].get(str(absent_metric), 0.0) > 0.0:
        return False
    return moments["snapshot"].get(str(metric), 0.0) >= 0.5


def context_metrics_note(panel: dict[str, object], moments: dict[str, dict[str, float]]) -> str:
    items = []
    for metric, label in list(panel.get("contextMetrics", [])):
        value = moments["snapshot"].get(str(metric))
        if value is not None:
            items.append(f"{label}={value:.4f}")
    return ", ".join(items)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "panel",
        "mechanism",
        "evidenceClass",
        "metric",
        "value",
        "fixtureValue",
        "fixtureSupported",
        "status",
        "supportLevel",
        "note",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ("usable", "thin", "warning", "fixture-only", "missing")}
    bounded_rows = [
        row for row in rows
        if row["status"] == "usable" and row["supportLevel"] != "direct-bounded"
    ]
    direct_rows = [
        row for row in rows
        if row["status"] == "usable" and row["supportLevel"] == "direct-bounded"
    ]
    lines = [
        "# Source Panel Inventory",
        "",
        "This inventory separates source coverage from simulated outcomes. `Usable` means the frozen snapshot clears a mechanism-diagnostic coverage threshold; it does not mean the panel is direct, representative, or calibration-grade. The `Claim support` column is the controlling strength label for manuscript claims.",
        "",
        "## Coverage Status",
        "",
        f"- Usable: `{counts['usable']}`",
        f"- Thin: `{counts['thin']}`",
        f"- Warning: `{counts['warning']}`",
        f"- Fixture-only: `{counts['fixture-only']}`",
        f"- Missing: `{counts['missing']}`",
        "",
        "## Claim-Support Limits",
        "",
        f"- Direct-bounded usable panels: `{len(direct_rows)}`",
        f"- Usable panels with proxy, denominator, program, mixed, conditional, or otherwise bounded support: `{len(bounded_rows)}`",
    ]
    for row in bounded_rows:
        lines.append(f"- `{row['panel']}` ({row['supportLevel']}): {row['nextAction']}")
    lines.extend([
        "",
        "| Panel | Mechanism constrained | Evidence | Moment | Snapshot | Fixture scaffold? | Status | Claim support | Note | Next action |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            f"| {row['panel']} | {row['mechanism']} | {row['evidenceClass']} | `{row['metric']}` | {row['value'] or 'n/a'} | {row['fixtureSupported']} | {row['status']} | {row['supportLevel']} | {row['note']} | {row['nextAction']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
