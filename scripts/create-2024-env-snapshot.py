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


SOURCES = {
    "lda": {
        "input": RAW / "lda-lobbying.csv",
        "description": "LDA 2024 Q1-Q4 LD-2 activity reports, post-filtered to ENV and EPA-facing contacts when live payloads are available.",
        "request": "LDA_YEAR=2024 LDA_PERIOD={first_quarter,second_quarter,third_quarter,fourth_quarter} ./scripts/fetch-lda.sh --live",
    },
    "fec": {
        "input": RAW / "fec-campaign-finance.csv",
        "description": "FEC 2024 cycle six national party committee receipts/disbursements, plus optional lobbyist bundled contributions.",
        "request": "FEC_CYCLE=2024 FEC_COMMITTEE_ID in C00010603,C00042366,C00000935,C00003418,C00027466,C00075820 ./scripts/fetch-fec.sh --live",
    },
    "regulatory": {
        "input": RAW / "regulatory-dockets.csv",
        "description": "EPA 2024 Regulations.gov/Federal Register rulemaking docket and document slice.",
        "request": "REGULATORY_AGENCY=EPA REGULATORY_DATE_FROM=2024-01-01 REGULATORY_DATE_TO=2024-12-31 ./scripts/fetch-regulatory.sh --live",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    normalized = args.output / "normalized"
    normalized.mkdir(parents=True, exist_ok=True)
    entries = []
    for key, source in SOURCES.items():
        source_path = args.raw / source["input"].name
        destination = normalized / source_path.name
        if source_path.exists():
            copy_normalized_csv(source_path, destination)
            row_count = count_rows(destination)
            checksum = sha256(destination)
            status = "copied"
        else:
            row_count = 0
            checksum = "missing"
            status = "missing"
        entries.append(
            {
                "source": key,
                "description": source["description"],
                "requestTemplate": source["request"],
                "normalizedFile": str(destination),
                "rowCount": row_count,
                "sha256": checksum,
                "status": status,
            }
        )

    manifest = {
        "snapshot": "2024-env",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "gitCommit": git("rev-parse", "--short", "HEAD"),
        "gitTreeState": git_tree_state(),
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    try:
        return subprocess.check_output(("git", *args), text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def git_tree_state() -> str:
    status = git("status", "--short")
    if status == "unknown":
        return "unknown"
    return "dirty" if status else "clean"


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
