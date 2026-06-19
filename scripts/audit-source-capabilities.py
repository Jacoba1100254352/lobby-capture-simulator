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
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(".")
REPORTS = ROOT / "reports"
SNAPSHOT = ROOT / "data" / "snapshots" / "2024-env"
SOURCE_PANEL_INVENTORY = REPORTS / "source-panel-inventory.csv"
LIVE_STATUS = SNAPSHOT / "live-run-status.csv"

SAM_REPRESENTATIVE_THRESHOLDS = {
    "rows": 5000,
    "distinctAwardCount": 1000,
    "agencyCount": 6,
    "dateSpanDays": 270,
    "knownPiidShare": 0.95,
    "actionDateShare": 0.80,
}

SAM_REPRESENTATIVE_WARNINGS = {
    "knownUeiShare": 0.50,
    "knownCompetitionShare": 0.25,
}


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
            "SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL for downloaded "
            "CSV/JSON/ZIP exports and SAM.gov emailed download-token links, or "
            "SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 and SAM_API_KEY for keyed API access; supports synchronous page fetches or "
            "SAM_CONTRACT_AWARDS_EXTRACT_MODE extract downloads, "
            "department-code and PIID-subtier filters, plus non-adjacent offset page-index "
            "strata through SAM_CONTRACT_AWARDS_OFFSET_STARTS for synchronous runs; "
            "SOURCE_FETCH_CURL_FALLBACK=1 handles endpoints that respond to curl but hang under urllib"
        ),
        "snapshotSource": "sam-contract-awards",
        "panel": "Procurement modification risk",
        "neededFor": "Procurement modification capture and calibrated policy-simulation claims",
        "nextAction": (
            "Use the archived USAspending bulk summary for public modification diagnostics; "
            "add a SAM/FPDS pull or configured export to crosswalk modification coding, exclusions, offer counts, protests, and firewalls."
        ),
    },
    {
        "capability": "sam-exclusions-overlay",
        "mechanism": "Public procurement exclusion and integrity overlay",
        "implementedRoute": (
            "operational SAM.gov Exclusions API preflight through make sam-exclusions-preflight "
            "plus a public SAM_Exclusions_Public_Extract fallback path; the preflight records "
            "redacted access, quota, and sample-shape state only"
        ),
        "snapshotSource": "",
        "panel": "",
        "neededFor": (
            "Procurement integrity controls and exclusion overlays for procurement modification "
            "causal-calibration claims"
        ),
        "nextAction": (
            "After SAM quota resets, run make sam-exclusions-preflight, then populate reviewed "
            "sam-exclusion-overlay rows with UEI, recipient, exclusion type, dates, agency, cause, "
            "and source provenance before rerunning first-wave gates."
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
        "capability": "usaspending-national-action-panel",
        "mechanism": "National-volume agency and recipient concentration diagnostics",
        "implementedRoute": "source-native USAspending transaction/action fetcher with agency filter omitted by USASPENDING_PROCUREMENT_ACTIONS_AGENCIES=ALL",
        "snapshotSource": "usaspending-procurement-national-actions",
        "panel": "Procurement concentration panel",
        "neededFor": "Stronger public procurement concentration diagnostics",
        "nextAction": (
            "Use this no-key national-volume panel as a fallback concentration diagnostic; "
            "prefer the archived bulk summary when present and keep modification incidence blocked on benchmark/coding reconciliation."
        ),
    },
    {
        "capability": "usaspending-bulk-transaction-download-panel",
        "mechanism": "Representative public procurement transaction-history denominator",
        "implementedRoute": (
            "no-key USAspending download/count and download/transactions route; "
            "make usaspending-transaction-download-strata plans row-limit-safe strata, "
            "and scripts/audit-usaspending-transaction-download-strata.py --download archives ZIPs, "
            "a normalized CSV, and a compact checksumed summary"
        ),
        "snapshotSource": "usaspending-procurement-bulk-summary",
        "snapshotFile": "usaspending-procurement-bulk-summary",
        "snapshotFormat": "json-summary",
        "panel": "Procurement modification risk",
        "neededFor": "Procurement modification denominator robustness and calibrated policy-simulation claim review",
        "nextAction": (
            "Use the compact frozen summary for public transaction-history diagnostics; archive the full normalized CSV/ZIP payloads externally only when full byte-for-byte reproduction is required."
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
    suffix = ".json" if capability.get("snapshotFormat") == "json-summary" else ".csv"
    file_path = normalized / f"{file_source}{suffix}" if file_source else Path("")
    row_count = snapshot_row_count(file_path, capability.get("snapshotFormat", "csv")) if source else 0
    sam_quality = sam_quality_status(file_path) if capability["capability"] == "sam-contract-awards-action-history" else ""
    live_status = statuses.get(source, {})
    source_status = live_status.get("status", "")
    snapshot_status = source_status or ("present" if row_count > 0 else ("not-promoted" if not source else "missing"))
    panel_status = panel.get("status", "")
    capability_status = classify_capability(
        capability["capability"], row_count, source_status, panel_status, sam_quality
    )
    return {
        "capability": capability["capability"],
        "mechanism": capability["mechanism"],
        "implementedRoute": capability["implementedRoute"],
        "snapshotSource": source or "not-promoted",
        "snapshotStatus": snapshot_status,
        "snapshotRows": str(row_count),
        "snapshotQuality": sam_quality or "not-applicable",
        "snapshotPlan": snapshot_plan(capability["capability"], live_status, row_count),
        "panel": capability["panel"] or "not-promoted",
        "panelStatus": panel_status or "not-promoted",
        "capabilityStatus": capability_status,
        "neededFor": capability["neededFor"],
        "nextAction": capability["nextAction"],
    }


def classify_capability(
    capability: str, row_count: int, source_status: str, panel_status: str, sam_quality: str
) -> str:
    if capability == "licensed-access-overlays":
        return "planned-overlay"
    if capability == "sam-exclusions-overlay":
        return "implemented-not-promoted"
    if capability == "direct-dark-money-routing":
        if panel_status == "usable":
            return "active-usable"
        if panel_status == "thin":
            return "active-bounded"
        if row_count > 0:
            return "proxy-only"
        return panel_status or "missing"
    if capability == "sam-contract-awards-action-history":
        if row_count > 0 and source_status == "ok" and sam_quality == "candidate":
            return "active-representative"
        if row_count > 0 and source_status == "ok":
            return "active-bounded"
        if source_status == "quota_blocked":
            return "quota-blocked"
        return "implemented-not-active"
    if capability == "usaspending-bulk-transaction-download-panel":
        if row_count >= 500000:
            return "active-representative"
        if row_count > 0:
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
            "Not active in the committed snapshot. Set SAM_CONTRACT_AWARDS_LIVE_CSV or "
            "SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded Contract Awards export, or enable "
            "SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 with SAM_API_KEY; use "
            "SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 for asynchronous extracts or department-code/"
            "PIID-subtier filters plus SAM_CONTRACT_AWARDS_OFFSET_STARTS for synchronous "
            "non-adjacent page-index slices; respect SAM.gov 429 nextAccessTime before "
            "rerunning quota-limited keyed refreshes."
        )
    if note:
        return note
    if row_count > 0:
        return "Active rows are present in the frozen snapshot."
    return "No active committed rows."


def snapshot_row_count(path: Path, snapshot_format: str) -> int:
    if snapshot_format == "json-summary":
        return json_summary_row_count(path)
    return csv_row_count(path)


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as source:
        return sum(1 for _ in csv.DictReader(source))


def json_summary_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    return int(float(payload.get("downloadedNormalizedRows", payload.get("rowCount", 0)) or 0))


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def sam_quality_status(path: Path) -> str:
    rows = read_rows(path)
    if not rows:
        return "blocked"
    awards = {award_key(row) for row in rows if award_key(row)}
    agencies = {row.get("agency", "").strip() for row in rows if row.get("agency", "").strip()}
    dates = [parsed for parsed in (parse_date(row.get("actionDate", "")) for row in rows) if parsed]
    metrics = {
        "rows": len(rows),
        "distinctAwardCount": len(awards),
        "agencyCount": len(agencies),
        "dateSpanDays": (max(dates) - min(dates)).days if len(dates) >= 2 else 0,
        "knownPiidShare": share_with_value(rows, "piid"),
        "knownUeiShare": share_with_value(rows, "uei"),
        "actionDateShare": share_with_value(rows, "actionDate"),
        "knownCompetitionShare": known_competition_share(rows),
    }
    blockers = [
        name for name, threshold in SAM_REPRESENTATIVE_THRESHOLDS.items()
        if float(metrics.get(name, 0.0)) < float(threshold)
    ]
    if blockers:
        return "blocked"
    warnings = [
        name for name, threshold in SAM_REPRESENTATIVE_WARNINGS.items()
        if float(metrics.get(name, 0.0)) < float(threshold)
    ]
    return "diagnostic" if warnings else "candidate"


def award_key(row: dict[str, str]) -> str:
    for key in ("piid", "awardId"):
        value = row.get(key, "").strip()
        if value:
            return value
    return ""


def share_with_value(rows: list[dict[str, str]], key: str) -> float:
    return sum(1 for row in rows if row.get(key, "").strip()) / len(rows) if rows else 0.0


def known_competition_share(rows: list[dict[str, str]]) -> float:
    unknown = {"", "unknown", "none", "null"}
    return (
        sum(1 for row in rows if row.get("competitionType", "").strip().lower() not in unknown) / len(rows)
        if rows else 0.0
    )


def parse_date(value: str) -> datetime | None:
    text = str(value or "").strip()
    for candidate in (text, text[:10], text[:20]):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue
    return None


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "capability",
        "mechanism",
        "implementedRoute",
        "snapshotSource",
        "snapshotStatus",
        "snapshotRows",
        "snapshotQuality",
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
            "## Key implemented routes",
            "",
            (
                "- Direct dark-money routing: configured `DARK_MONEY_LIVE_CSV`/"
                "`DARK_MONEY_LIVE_URL`, ProPublica Schedule I nonprofit-routing rows, "
                "and IRS EO BMF opaque-capacity proxies remain separate evidence classes."
            ),
            (
                "- SAM/FPDS action-history route: downloaded `SAM_CONTRACT_AWARDS_LIVE_CSV`/"
                "`SAM_CONTRACT_AWARDS_LIVE_URL` exports, including SAM.gov emailed "
                "`api_key=REPLACE_WITH_API_KEY` download links, or keyed `SAM_API_KEY` runs can "
                "use `SAM_CONTRACT_AWARDS_EXTRACT_MODE` for asynchronous extracts and "
                "`SAM_CONTRACT_AWARDS_OFFSET_STARTS` for non-adjacent synchronous page-index strata."
            ),
            (
                "- SAM.gov Exclusions route: `make sam-exclusions-preflight` records redacted "
                "quota/access/sample-shape status for the exclusion-overlay acquisition path, "
                "but no exclusion rows support claims until a reviewed calibration CSV is promoted."
            ),
            (
                "- USAspending procurement route: no-key action, national action, and bulk-summary "
                "panels remain separate from SAM.gov Contract Awards rows so procurement provenance "
                "is auditable."
            ),
            (
                "- Revolving-door route: LDA covered-position rows support exposure diagnostics, "
                "but documented post-employment movement still requires an additional personnel source."
            ),
        ]
    )
    lines.extend(
        [
            "",
            (
                "| Capability | Snapshot source | Rows | Panel status | Capability status | "
                "Snapshot quality | Snapshot plan | Needed for | Next action |"
            ),
            "| --- | --- | ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {capability} | {snapshotSource} ({snapshotStatus}) | {snapshotRows} | "
            "{panelStatus} | {capabilityStatus} | {snapshotQuality} | {snapshotPlan} | {neededFor} | {nextAction} |".format(
                **escaped
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
