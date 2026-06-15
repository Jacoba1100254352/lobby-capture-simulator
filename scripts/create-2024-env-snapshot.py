#!/usr/bin/env python3
"""Freeze the current normalized inputs under the 2024 EPA/ENV snapshot protocol."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RAW = Path("data/raw")
OUTPUT = Path("data/snapshots/2024-env")
NORMALIZED = OUTPUT / "normalized"
ROOT = Path(__file__).resolve().parents[1]


SOURCES = {
    "lda": {
        "input": RAW / "lda-lobbying.csv",
        "description": "LDA 2024 Q1-Q4 LD-2 activity reports, post-filtered to ENV and EPA-facing contacts when live payloads are available.",
        "request": "LDA_YEAR=2024 LDA_PERIOD={first_quarter,second_quarter,third_quarter,fourth_quarter} ./scripts/fetch-lda.sh --live",
    },
    "fec": {
        "input": RAW / "fec-campaign-finance.csv",
        "description": "FEC 2024 cycle party committee contributions, OpenFEC Schedule E independent expenditures, electioneering communications, and communication-cost rows when available. Public-financing and opaque-capacity bridge rows are stored in separate panels.",
        "request": "FEC_CYCLE=2024 FEC_COMMITTEE_ID in C00010603,C00042366,C00000935,C00003418,C00027466,C00075820 plus FEC_ONLY_SCHEDULE_E=1 FEC_INCLUDE_SCHEDULE_E=1 for Schedule E plus FEC_INCLUDE_SCHEDULE_E=0 FEC_INCLUDE_ELECTIONEERING=1 FEC_INCLUDE_COMMUNICATION_COSTS=1 for electoral-communication rows",
    },
    "public-financing": {
        "input": RAW / "public-financing.csv",
        "description": "Public financing and voucher bridge rows for direct program participation and public-fund share diagnostics.",
        "request": "PUBLIC_FINANCING_SOURCE_NATIVE=1 with nyc-public-financing and seattle-democracy-vouchers source-native fetchers, or PUBLIC_FINANCING_LIVE_CSV=/path/to/program-export.csv ./scripts/fetch-public-financing.sh --live",
    },
    "dark-money": {
        "input": RAW / "dark-money.csv",
        "description": "Explicit dark-money rows from a configured source export, ProPublica/IRS Form 990 Schedule I nonprofit-routing rows, or IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows; donor identities remain unobserved.",
        "request": "DARK_MONEY_SOURCE_NATIVE=1 python3 scripts/fetch-source-data.py irs-dark-money-capacity --output data/raw/dark-money.csv followed by PROPUBLICA_NONPROFIT_ROUTING_SOURCE_NATIVE=1 python3 scripts/fetch-source-data.py propublica-nonprofit-routing --output /tmp/propublica-nonprofit-routing.csv and append, or DARK_MONEY_LIVE_CSV=/path/to/export.csv ./scripts/fetch-dark-money.sh --live",
    },
    "regulatory": {
        "input": RAW / "regulatory-dockets.csv",
        "description": "EPA 2024 Regulations.gov/Federal Register rulemaking docket and document slice.",
        "request": "REGULATORY_AGENCY=EPA REGULATORY_DATE_FROM=2024-01-01 REGULATORY_DATE_TO=2024-12-31 ./scripts/fetch-regulatory.sh --live",
    },
    "usaspending": {
        "input": RAW / "usaspending-awards.csv",
        "description": "EPA fiscal-year 2024 USAspending award panel for procurement concentration, SAM/FPDS bridge identifiers, competition, modification, and firewall moments.",
        "request": "USASPENDING_FISCAL_YEAR=2024 USASPENDING_AGENCY='Environmental Protection Agency' ./scripts/fetch-usaspending.sh --live",
    },
    "usaspending-procurement-bridge": {
        "input": RAW / "usaspending-procurement-bridge.csv",
        "description": "Multi-agency fiscal-year 2024 USAspending top-award bridge for high-value procurement concentration and latest-transaction modification diagnostics; kept separate from the EPA calibration slice and action-panel denominator.",
        "request": "USASPENDING_AGENCIES='Environmental Protection Agency,Department of Energy,Department of the Interior,Department of Agriculture,Department of Transportation,Department of Defense' USASPENDING_PAGE_SIZE=25 USASPENDING_MAX_PAGES=1 USASPENDING_TREAT_LATEST_TRANSACTION_AS_MODIFICATION=1 python3 scripts/fetch-source-data.py usaspending --output data/raw/usaspending-procurement-bridge.csv",
    },
    "usaspending-procurement-actions": {
        "input": RAW / "usaspending-procurement-actions.csv",
        "description": "Expanded stratified 12-agency quarterly USAspending transaction/action panel for action-level procurement concentration and modification diagnostics; rows are deduplicated across modification, amount, and action-date strata and kept separate from award rows, top-award bridge rows, and SAM.gov Contract Awards rows.",
        "request": "USASPENDING_AGENCIES='Environmental Protection Agency,Department of Energy,Department of the Interior,Department of Agriculture,Department of Transportation,Department of Defense,Department of Health and Human Services,Department of Veterans Affairs,Department of Homeland Security,National Aeronautics and Space Administration,General Services Administration,Department of Commerce' USASPENDING_ACTION_PERIOD_BUCKETS=quarterly USASPENDING_ACTION_TRANSACTION_PAGE_SIZE=100 USASPENDING_ACTION_TRANSACTION_MAX_PAGES=2 USASPENDING_ACTION_TRANSACTION_SORT_SPECS='Mod:asc;Transaction Amount:desc;Action Date:asc' python3 scripts/fetch-source-data.py usaspending-actions --output data/raw/usaspending-procurement-actions.csv",
    },
    "usaspending-procurement-national-actions": {
        "input": RAW / "usaspending-procurement-national-actions.csv",
        "description": "National-volume no-agency-filtered USAspending fiscal-year 2024 transaction/action panel for agency and recipient concentration diagnostics; kept separate from the balanced action panel and SAM.gov Contract Awards modification-incidence route.",
        "request": "USASPENDING_PROCUREMENT_ACTIONS_AGENCIES=ALL USASPENDING_ACTION_PERIOD_BUCKETS=annual USASPENDING_ACTION_TRANSACTION_PAGE_SIZE=100 USASPENDING_ACTION_TRANSACTION_MAX_PAGES=5 USASPENDING_ACTION_TRANSACTION_SORT_SPECS='Transaction Amount:desc;Mod:asc;Action Date:asc' python3 scripts/fetch-source-data.py usaspending-actions --output data/raw/usaspending-procurement-national-actions.csv",
    },
    "usaspending-procurement-bulk-summary": {
        "input": RAW / "usaspending-procurement-bulk-summary.json",
        "format": "json-summary",
        "description": "Checksumed summary for the no-key USAspending fiscal-year 2024 bulk transaction download route; raw normalized CSV/ZIP payloads are kept outside git and can be archived as release assets.",
        "request": "make usaspending-transaction-download-strata, then python3 scripts/audit-usaspending-transaction-download-strata.py --download",
    },
    "sam-contract-awards": {
        "input": RAW / "sam-contract-awards.csv",
        "description": "Optional SAM.gov Contract Awards action panel for PIID/UEI, competition, modification, award-date, and contracting-department diagnostics; kept separate from USAspending action rows so procurement provenance remains auditable.",
        "request": "SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/export.csv python3 scripts/fetch-source-data.py sam-contract-awards-export --input /path/to/export.csv --output data/raw/sam-contract-awards.csv, or SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 SAM_API_KEY=... python3 scripts/fetch-source-data.py sam-contract-awards --output data/raw/sam-contract-awards.csv",
    },
    "revolving-door": {
        "input": RAW / "revolving-door.csv",
        "description": "Normalized revolving-door source panel from a licensed/exported CSV or LDA covered-position derivation, with fixture fallback.",
        "request": "REVOLVING_DOOR_LIVE_CSV=/path/to/export.csv ./scripts/fetch-revolving-door.sh --live or REVOLVING_DOOR_SOURCE_NATIVE=1 python3 scripts/fetch-source-data.py revolving-door",
    },
    "intermediary": {
        "input": RAW / "intermediaries.csv",
        "description": "Normalized nonprofit, 527, think-tank, campaign-intermediary, and association panel from NYC CFB, IRS EO BMF, IRS POFD Form 8872, ProPublica, OpenSecrets, or curated source exports.",
        "request": "INTERMEDIARY_SOURCE_NATIVE=1 with nyc-intermediaries, irs-eo-bmf, and irs-527 source-native fetchers, or INTERMEDIARY_LIVE_CSV=/path/to/export.csv ./scripts/fetch-intermediaries.sh --live",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    normalized = args.output / "normalized"
    normalized.mkdir(parents=True, exist_ok=True)
    live_status = read_live_status(args.output / "live-run-status.csv")
    entries = []
    for key, source in SOURCES.items():
        source_path = args.raw / source["input"].name
        destination = normalized / source_path.name
        if source_path.exists():
            if source.get("format") == "json-summary":
                copy_json_summary(source_path, destination)
                row_count = summary_row_count(destination)
            else:
                copy_normalized_csv(source_path, destination)
                row_count = count_rows(destination)
            checksum = sha256(destination)
            status, notes = source_status(key, live_status)
        else:
            if destination.exists():
                destination.unlink()
            row_count = 0
            checksum = "missing"
            status, notes = source_status(key, live_status)
            if status == "copied":
                status = "missing"
                notes = "normalized source file missing"
        entries.append(
            {
                "source": key,
                "description": source["description"],
                "requestTemplate": source["request"],
                "normalizedFile": str(destination),
                "rowCount": row_count,
                "sha256": checksum,
                "status": status,
                "statusNotes": notes,
            }
        )

    manifest = {
        "snapshot": "2024-env",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "gitCommit": git("rev-parse", "--short", "HEAD"),
        "gitTreeState": git_tree_state(
            exclude_prefixes=(
                str(args.output) + "/",
                "reports/",
                "paper/tables/",
                "paper/figures/",
            )
        ),
        "gitTreeStateScope": (
            "working tree status excluding generated 2024-env snapshot, reports, "
            "paper tables, and paper figures"
        ),
        "scope": {
            "calendarWindow": "2024-01-01/2024-12-31",
            "fecCycle": "2024",
            "policyDomain": "environment",
            "ldaIssueCode": "ENV",
            "agency": "EPA",
            "validationMode": "closed historical window, not latest moving data",
        },
        "sources": entries,
    }
    status_path = args.output / "live-run-status.csv"
    if status_path.exists():
        manifest["liveRunStatus"] = {
            "file": str(status_path),
            "sha256": sha256(status_path),
        }
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_readme(args.output, entries)
    print(f"Wrote {manifest_path}")
    return 0


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as source:
        return sum(1 for _ in csv.DictReader(source))


def copy_normalized_csv(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")
    destination.write_text(text.rstrip() + "\n", encoding="utf-8")


def copy_json_summary(source: Path, destination: Path) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload = scrub_local_paths(payload)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def scrub_local_paths(value):
    if isinstance(value, dict):
        return {key: scrub_local_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub_local_paths(item) for item in value]
    if isinstance(value, str):
        return portable_path_string(value)
    return value


def portable_path_string(value: str) -> str:
    try:
        path = Path(value)
    except (OSError, ValueError):
        return value
    if not path.is_absolute():
        return value
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, ValueError):
        return value


def summary_row_count(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    return int(float(payload.get("downloadedNormalizedRows", payload.get("rowCount", 0)) or 0))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_live_status(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def source_status(source: str, live_status: list[dict[str, str]]) -> tuple[str, str]:
    if not live_status:
        return "copied", "normalized file copied from data/raw"
    names = {
        "lda": [row for row in live_status if row["source"].startswith("lda-")],
        "fec": [row for row in live_status if row["source"].startswith("fec-")],
        "public-financing": [row for row in live_status if row["source"] == "public-financing"],
        "dark-money": [row for row in live_status if row["source"] == "dark-money"],
        "regulatory": [row for row in live_status if row["source"] in {"regulations-gov", "federal-register"}],
        "usaspending": [row for row in live_status if row["source"] == "usaspending"],
        "usaspending-procurement-bridge": [row for row in live_status if row["source"] == "usaspending-procurement-bridge"],
        "usaspending-procurement-actions": [row for row in live_status if row["source"] == "usaspending-procurement-actions"],
        "usaspending-procurement-national-actions": [row for row in live_status if row["source"] == "usaspending-procurement-national-actions"],
        "usaspending-procurement-bulk-summary": [row for row in live_status if row["source"] == "usaspending-procurement-bulk-summary"],
        "sam-contract-awards": [row for row in live_status if row["source"] == "sam-contract-awards"],
        "revolving-door": [row for row in live_status if row["source"] == "revolving-door"],
        "intermediary": [row for row in live_status if row["source"] == "intermediary"],
    }.get(source, [])
    if not names:
        return "copied", "normalized file copied from data/raw"
    statuses = {row["status"] for row in names}
    notes = "; ".join(f"{row['source']}: {row['status']} ({row['notes']})" for row in names)
    if statuses == {"ok"}:
        return "live", notes
    if "ok" in statuses or "partial" in statuses:
        return "partial-live", notes
    if "archived_fallback" in statuses:
        return "archived-fallback", notes
    if "fixture" in statuses:
        return "fixture", notes
    return "unavailable", notes


def git(*args: str) -> str:
    output = git_raw(*args)
    return output.strip() if output is not None else "unknown"


def git_raw(*args: str) -> str | None:
    try:
        return subprocess.check_output(("git", *args), text=True)
    except (OSError, subprocess.CalledProcessError):
        return None


def git_tree_state(exclude_prefixes: tuple[str, ...] = ()) -> str:
    status = git_raw("status", "--short")
    if status is None:
        return "unknown"
    dirty_paths = []
    for line in status.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in exclude_prefixes):
            continue
        dirty_paths.append(path)
    return "dirty" if dirty_paths else "clean"


def write_readme(root: Path, entries: list[dict[str, object]]) -> None:
    lines = [
        "# 2024 EPA/ENV Snapshot",
        "",
        "This directory is the reproducible closed-window snapshot scaffold for the first paper-grade validation slice.",
        "",
        "Scope:",
        "",
        "- Calendar window: 2024-01-01 through 2024-12-31.",
        "- LDA issue code: ENV.",
        "- Agency: EPA.",
        "- FEC cycle: 2024, with the six national party committees as the first electoral-pressure panel.",
        "- Outside-spending bridge: OpenFEC Schedule E independent expenditures.",
        "- Electoral-communication bridge: OpenFEC electioneering communications and communication-cost rows when available.",
        "- Public-financing bridge: NYC CFB public-funds payments, Seattle Democracy Voucher rows, or configured program export rows carried as a separate bridge panel.",
        "- Dark-money bridge: configured source export rows, ProPublica/IRS Form 990 Schedule I nonprofit-routing transfer rows, or IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows; super PAC rows remain separate and nonprofit-routing rows do not identify underlying donors.",
        "- USAspending fiscal year: 2024, Environmental Protection Agency awards.",
        "- USAspending procurement bridge: multi-agency fiscal-year 2024 top-award rows for high-value procurement diagnostics, kept separate from the EPA calibration slice and action-panel denominator.",
        "- USAspending procurement actions: expanded stratified 12-agency quarterly transaction/action rows for concentration and modification-incidence diagnostics when present, combining initial-action, high-value, and action-date strata and kept separate from award rows and top-award bridge rows.",
        "- USAspending national procurement actions: no-agency-filtered fiscal-year 2024 transaction/action rows for national-volume agency and recipient concentration diagnostics, kept separate from modification-incidence denominators.",
        "- USAspending bulk transaction summary: checksumed summary of the public download/count and download/transactions route when full normalized rows are archived outside git.",
        "- SAM.gov Contract Awards: optional source-native action rows for PIID/UEI, competition, modification, award-date, and contracting-department diagnostics, kept separate from USAspending action rows so source provenance remains visible.",
        "- Revolving-door panel: licensed/source export or LDA covered-position derivation when available; fixture otherwise.",
        "- Intermediary panel: NYC CFB intermediary rows, IRS EO BMF nonprofit/association capacity rows, IRS POFD Form 8872 527 political-organization rows, or configured nonprofit, 527, association, and think-tank export when available; fixture otherwise.",
        "",
        "The current command freezes whatever normalized files are present under `data/raw/`. Live paper snapshots should first run the request templates in `manifest.json`, preserve raw payloads outside git when too large, normalize into the same schemas, and then rerun `make snapshot-2024-env`.",
        "",
        "| Source | Rows | Status | Normalized file |",
        "| --- | ---: | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['source']} | {entry['rowCount']} | {entry['status']} | `{entry['normalizedFile']}` |"
        )
    status_path = root / "live-run-status.csv"
    if status_path.exists():
        lines.extend(
            [
                "",
                "`live-run-status.csv` records which official live requests completed and which were blocked by public API limits or missing credentials.",
            ]
        )
    lines.append("")
    (root / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
