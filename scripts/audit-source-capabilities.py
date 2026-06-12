#!/usr/bin/env python3
"""Report implemented source routes and their committed snapshot status.

The source-panel inventory answers whether a panel is usable for the paper. This
audit answers a different reviewer question: whether a stronger live route is
implemented, active in the frozen snapshot, merely optional, or still future
work.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
REPORTS = ROOT / "reports"
SNAPSHOT = ROOT / "data" / "snapshots" / "2024-env"
SOURCE_PANEL_INVENTORY = REPORTS / "source-panel-inventory.csv"
LIVE_STATUS = SNAPSHOT / "live-run-status.csv"


CAPABILITIES = [
    {
        "capability": "direct-dark-money-routing",
        "mechanism": "Direct hidden-donor or nonprofit-routing evidence",
        "implementedRoute": (
            "configured DARK_MONEY_LIVE_CSV/DARK_MONEY_LIVE_URL; "
            "source-native ProPublica Nonprofit Explorer Schedule I grant-routing; "
            "IRS EO BMF remains an opaque-capacity proxy"
        ),
        "snapshotSource": "dark-money",
        "panel": "Direct dark money",
        "neededFor": "Hidden-channel magnitude and calibrated policy-simulation claims",
        "nextAction": (
            "Broaden nonprofit-routing beyond the bounded top-EIN Schedule I slice and keep "
            "these transfer rows separate from Schedule E, electioneering, communication-cost, "
            "IRS BMF capacity proxies, and hidden-donor identity claims."
        ),
    },
    {
        "capability": "sam-contract-awards-action-history",
        "mechanism": "Representative SAM/FPDS action-history denominator",
        "implementedRoute": (
            "optional SAM.gov Contract Awards importer behind "
            "SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 and SAM_API_KEY; supports "
            "department-code and PIID-subtier filters plus "
            "non-adjacent offset page-index strata through SAM_CONTRACT_AWARDS_OFFSET_STARTS"
        ),
        "snapshotSource": "sam-contract-awards",
        "panel": "Procurement modification risk",
        "neededFor": "Procurement modification capture and calibrated policy-simulation claims",
        "nextAction": (
            "Archive a representative SAM/FPDS action-history pull or configured export; "
            "compare modification incidence against the bounded USAspending action panel."
        ),
    },
    {
        "capability": "usaspending-stratified-action-panel",
        "mechanism": "Bounded transaction/action procurement diagnostics",
        "implementedRoute": "source-native USAspending transaction/action fetcher",
        "snapshotSource": "usaspending-procurement-actions",
        "panel": "Procurement action history",
        "neededFor": "Bounded procurement concentration and modification diagnostics",
        "nextAction": (
            "Broaden beyond the selected 12-agency quarterly stress panel before treating "
            "modification incidence as calibration-grade."
        ),
    },
    {
        "capability": "lda-covered-position-revolving-door",
        "mechanism": "Covered-position exposure and cooling-off diagnostics",
        "implementedRoute": "source-native LDA covered-position derivation",
        "snapshotSource": "revolving-door",
        "panel": "Revolving door",
        "neededFor": "Revolving-door access mechanism diagnostics",
        "nextAction": (
            "Supplement with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived "
            "personnel-movement exports before claiming representative post-employment movement."
        ),
    },
    {
        "capability": "irs-527-political-organizations",
        "mechanism": "Campaign-adjacent 527 intermediary receipts and disbursements",
        "implementedRoute": "source-native IRS POFD Form 8872 bounded slice",
        "snapshotSource": "intermediary",
        "snapshotFile": "intermediaries",
        "panel": "IRS 527 political organizations",
        "neededFor": "Intermediary and campaign-adjacent substitution diagnostics",
        "nextAction": (
            "Broaden beyond the bounded alphabetic slice while preserving 527 rows as "
            "distinct from 501(c)(4)/(c)(6) dark-money evidence."
        ),
    },
    {
        "capability": "licensed-access-overlays",
        "mechanism": (
            "OpenSecrets, LegiStorm, ProPublica, FACA, OGE, witness, and richer "
            "access-network overlays"
        ),
        "implementedRoute": (
            "documented keys/exports only; no promoted source-native importer in the paper snapshot"
        ),
        "snapshotSource": "",
        "panel": "",
        "neededFor": "Representative hidden-channel, intermediary, and personnel-movement validation",
        "nextAction": (
            "Implement importer-specific schemas only after licensing and export fields are "
            "fixed enough to preserve reproducibility."
        ),
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args()

    panels = read_panel_inventory(args.reports / SOURCE_PANEL_INVENTORY.name)
    statuses = read_live_status(args.snapshot / LIVE_STATUS.name)
    normalized = args.snapshot / "normalized"
    rows = [
        capability_row(capability, panels, statuses, normalized)
        for capability in CAPABILITIES
    ]
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "source-capability-audit.csv", rows)
    write_markdown(args.reports / "source-capability-audit.md", rows)
    print(f"Wrote {args.reports / 'source-capability-audit.csv'}")
    print(f"Wrote {args.reports / 'source-capability-audit.md'}")
    return 0


def read_panel_inventory(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get("panel", ""): row for row in csv.DictReader(source)}


def read_live_status(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get("source", ""): row for row in csv.DictReader(source)}


def capability_row(
    capability: dict[str, str],
    panels: dict[str, dict[str, str]],
    statuses: dict[str, dict[str, str]],
    normalized: Path,
) -> dict[str, str]:
    panel = panels.get(capability["panel"], {})
    source = capability["snapshotSource"]
    file_source = capability.get("snapshotFile", source)
    file_path = normalized / f"{file_source}.csv" if file_source else Path("")
    row_count = csv_row_count(file_path) if source else 0
    live_status = statuses.get(source, {})
    source_status = live_status.get("status", "")
    panel_status = panel.get("status", "")
    capability_status = classify_capability(
        capability["capability"], row_count, source_status, panel_status
    )
    return {
        "capability": capability["capability"],
        "mechanism": capability["mechanism"],
        "implementedRoute": capability["implementedRoute"],
        "snapshotSource": source or "not-promoted",
        "snapshotStatus": source_status or ("not-promoted" if not source else "missing"),
        "snapshotRows": str(row_count),
        "snapshotPlan": snapshot_plan(capability["capability"], live_status, row_count),
        "panel": capability["panel"] or "not-promoted",
        "panelStatus": panel_status or "not-promoted",
        "capabilityStatus": capability_status,
        "neededFor": capability["neededFor"],
        "nextAction": capability["nextAction"],
    }


def classify_capability(
    capability: str, row_count: int, source_status: str, panel_status: str
) -> str:
    if capability == "licensed-access-overlays":
        return "planned-overlay"
    if capability == "direct-dark-money-routing":
        if panel_status == "usable":
            return "active-usable"
        if panel_status == "thin":
            return "active-bounded"
        if row_count > 0:
            return "proxy-only"
        return panel_status or "missing"
    if capability == "sam-contract-awards-action-history":
        if row_count > 0 and source_status == "ok":
            return "active-bounded"
        return "implemented-not-active"
    if row_count > 0 and source_status == "ok" and panel_status == "usable":
        return "active-usable"
    if row_count > 0:
        return "active-bounded"
    return "missing"


def snapshot_plan(capability: str, live_status: dict[str, str], row_count: int) -> str:
    note = live_status.get("notes", "").strip()
    if capability == "sam-contract-awards-action-history":
        if note:
            return note
        if row_count > 0:
            return "SAM.gov Contract Awards rows are present, but the live status note is missing."
        return (
            "Not active in the committed snapshot. Enable SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 "
            "with SAM_API_KEY; use department-code or PIID-subtier filters plus "
            "SAM_CONTRACT_AWARDS_OFFSET_STARTS for non-adjacent page-index slices."
        )
    if note:
        return note
    if row_count > 0:
        return "Active rows are present in the frozen snapshot."
    return "No active committed rows."


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as source:
        return sum(1 for _ in csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "capability",
        "mechanism",
        "implementedRoute",
        "snapshotSource",
        "snapshotStatus",
        "snapshotRows",
        "snapshotPlan",
        "panel",
        "panelStatus",
        "capabilityStatus",
        "neededFor",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["capabilityStatus"]] = counts.get(row["capabilityStatus"], 0) + 1
    lines = [
        "# Source Capability Audit",
        "",
        (
            "This audit separates implemented live-source routes from the empirical support "
            "actually present in the committed 2024 snapshot. It is a process guardrail: an "
            "implemented importer does not support manuscript claims unless the frozen snapshot "
            "contains usable rows and the claim ledger permits the claim. Direct hidden-donor "
            "and SAM/FPDS action-history routes remain especially important claim boundaries."
        ),
        "",
        "## Summary",
        "",
    ]
    for status in sorted(counts):
        lines.append(f"- {status}: `{counts[status]}`")
    lines.extend(
        [
            "",
            (
                "| Capability | Snapshot source | Rows | Panel status | Capability status | "
                "Snapshot plan | Needed for | Next action |"
            ),
            "| --- | --- | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {capability} | {snapshotSource} ({snapshotStatus}) | {snapshotRows} | "
            "{panelStatus} | {capabilityStatus} | {snapshotPlan} | {neededFor} | {nextAction} |".format(
                **escaped
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
