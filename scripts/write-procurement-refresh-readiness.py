#!/usr/bin/env python3
"""Write a no-network readiness plan for the procurement source refresh.

This report is operational evidence, not empirical evidence. It exists so a
future SAM/FPDS refresh can be run deliberately after quota reset without
promoting partial payloads or confusing the bounded USAspending action panel
with representative procurement calibration.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path


ROOT = Path(".")
REPORTS = ROOT / "reports"
SNAPSHOT = ROOT / "data" / "snapshots" / "2024-env"
ENV_EXAMPLE = ROOT / ".env.example"

LIVE_STATUS = SNAPSHOT / "live-run-status.csv"
SOURCE_CAPABILITY = REPORTS / "source-capability-audit.csv"
PROCUREMENT_DENOMINATOR = REPORTS / "procurement-denominator-audit.csv"
CALIBRATION_QUEUE = REPORTS / "calibration-queue.csv"

REQUIRED_ENV_VARS = [
    "SAM_API_KEY",
    "SAM_CONTRACT_AWARDS_SOURCE_NATIVE",
    "SAM_CONTRACT_AWARDS_EXTRACT_MODE",
    "SAM_CONTRACT_AWARDS_EXTRACT_FORMAT",
    "SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID",
    "SAM_CONTRACT_AWARDS_EXTRACT_POLL_ATTEMPTS",
    "SAM_CONTRACT_AWARDS_EXTRACT_POLL_SECONDS",
    "SAM_CONTRACT_AWARDS_OFFSET_STARTS",
    "SAM_CONTRACT_AWARDS_DEPARTMENT_CODES",
    "SAM_CONTRACT_AWARDS_PIID_SUBTIER_CODES",
    "SAM_CONTRACT_AWARDS_FETCH_RETRIES",
    "SAM_CONTRACT_AWARDS_FETCH_TIMEOUT_SECONDS",
    "SAM_CONTRACT_AWARDS_FETCH_HARD_TIMEOUT_SECONDS",
    "SOURCE_FETCH_CURL_FALLBACK",
]

QUOTA_UNTIL_RE = re.compile(r"quota blocked until\s*([^;,\n]+UTC)", re.IGNORECASE)
NEXT_ACCESS_RE = re.compile(
    r'"nextAccessTime"\s*:\s*"([^"]+)"|nextAccessTime=([^;,\n]+UTC)',
    re.IGNORECASE,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--env-example", type=Path, default=ENV_EXAMPLE)
    args = parser.parse_args()

    args.reports.mkdir(parents=True, exist_ok=True)
    rows = readiness_rows(args.reports, args.snapshot, args.env_example)
    write_csv(args.reports / "procurement-refresh-readiness.csv", rows)
    write_markdown(args.reports / "procurement-refresh-readiness.md", rows)
    print(f"Wrote {args.reports / 'procurement-refresh-readiness.csv'}")
    print(f"Wrote {args.reports / 'procurement-refresh-readiness.md'}")
    return 0


def readiness_rows(reports: Path, snapshot: Path, env_example: Path) -> list[dict[str, str]]:
    statuses = read_keyed_csv(snapshot / LIVE_STATUS.name, "source")
    capabilities = read_keyed_csv(reports / SOURCE_CAPABILITY.name, "capability")
    denominators = read_keyed_csv(reports / PROCUREMENT_DENOMINATOR.name, "source")
    queue = read_csv(reports / CALIBRATION_QUEUE.name)

    sam_status = statuses.get("sam-contract-awards", {})
    sam_capability = capabilities.get("sam-contract-awards-action-history", {})
    usa_action = denominators.get("usaspending-procurement-actions", {})
    sam_denominator = denominators.get("sam-contract-awards", {})
    p1_procurement = [
        row for row in queue
        if row.get("priority") == "P1" and row.get("metric", "").startswith("procurement")
    ]

    env_vars = documented_env_vars(env_example)
    missing_env = [name for name in REQUIRED_ENV_VARS if name not in env_vars]
    sam_rows = int_value(sam_capability.get("snapshotRows") or sam_denominator.get("rows"))
    usa_rows = int_value(usa_action.get("rows"))
    quota_reset = next_access_time(sam_status.get("notes", "") or sam_capability.get("snapshotPlan", ""))

    rows = [
        {
            "item": "provenance",
            "status": "informational",
            "evidence": generated_at(),
            "nextAction": "Regenerate this report with make procurement-refresh-readiness after source-status changes.",
        },
        {
            "item": "sam-control-variables",
            "status": "ready" if not missing_env else "missing",
            "evidence": (
                "All SAM_CONTRACT_AWARDS controls documented in .env.example"
                if not missing_env else f"Missing from .env.example: {', '.join(missing_env)}"
            ),
            "nextAction": (
                "Fill real values in .env only; do not commit private keys or raw payload archives."
            ),
        },
        {
            "item": "sam-live-status",
            "status": sam_status.get("status") or sam_capability.get("snapshotStatus") or "missing",
            "evidence": sam_status.get("notes") or sam_capability.get("snapshotPlan") or "No SAM Contract Awards row is recorded in live-run-status.csv.",
            "nextAction": (
                f"Wait until {quota_reset} before rerunning SAM."
                if quota_reset else
                "Run only after confirming quota/access status; if the endpoint returns nextAccessTime, wait for that UTC timestamp."
            ),
        },
        {
            "item": "representative-sam-fpds-action-history",
            "status": "ready" if sam_rows > 0 else "blocked",
            "evidence": f"SAM/FPDS action-history rows in frozen snapshot: {sam_rows}",
            "nextAction": (
                "Archive a representative SAM/FPDS action-history panel before clearing procurement modification capture."
                if sam_rows == 0 else
                "Compare SAM modification, concentration, and denominator moments against the bounded USAspending panel."
            ),
        },
        {
            "item": "bounded-usaspending-fallback",
            "status": "ready" if usa_rows > 0 else "missing",
            "evidence": (
                f"USAspending action rows remain available as bounded diagnostics: {usa_rows}"
            ),
            "nextAction": (
                "Keep this fallback for schema checks and directional diagnostics, but do not treat it as volume-representative calibration."
            ),
        },
        {
            "item": "p1-procurement-calibration-actions",
            "status": "blocked" if p1_procurement else "clear",
            "evidence": f"P1 procurement source-gap actions: {len(p1_procurement)}",
            "nextAction": (
                "; ".join(row.get("recommendedAction", "") for row in p1_procurement)
                if p1_procurement else
                "No P1 procurement source-gap actions remain."
            ),
        },
        {
            "item": "extract-mode-path",
            "status": "ready",
            "evidence": (
                "SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 supports asynchronous JSON/CSV extract downloads."
            ),
            "nextAction": (
                "Use extract mode for the next representative keyed refresh when the SAM account has Contract Awards access."
            ),
        },
        {
            "item": "offset-strata-path",
            "status": "ready",
            "evidence": (
                "SAM_CONTRACT_AWARDS_OFFSET_STARTS supports non-adjacent synchronous page-index strata."
            ),
            "nextAction": (
                "Use department-code or PIID-subtier filters plus non-adjacent offsets only for bounded samples or diagnostics."
            ),
        },
        {
            "item": "partial-payload-policy",
            "status": "ready",
            "evidence": (
                "The live runner classifies SAM quota failures and falls back to USAspending action rows."
            ),
            "nextAction": (
                "Do not promote partial SAM payloads; archive rows only after a completed source run and rerun paper-artifacts-check."
            ),
        },
        {
            "item": "claim-boundary",
            "status": "blocked" if sam_rows == 0 or p1_procurement else "ready",
            "evidence": (
                "Calibrated policy-simulation claims remain blocked until representative SAM/FPDS action-history coverage clears the procurement P1 gaps."
            ),
            "nextAction": (
                "Keep the manuscript framed as a mechanism-model article with bounded empirical bridges."
            ),
        },
    ]
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_keyed_csv(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path) if row.get(key, "")}


def documented_env_vars(path: Path) -> set[str]:
    if not path.exists():
        return set()
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        names.add(stripped.split("=", 1)[0].strip())
    return names


def next_access_time(notes: str) -> str:
    quota_match = QUOTA_UNTIL_RE.search(notes)
    if quota_match:
        return quota_match.group(1).strip()
    match = NEXT_ACCESS_RE.search(notes)
    if not match:
        return ""
    return next(group.strip() for group in match.groups() if group)


def int_value(value: object) -> int:
    try:
        return int(float(str(value or "0").replace(",", "")))
    except ValueError:
        return 0


def generated_at() -> str:
    return os.environ.get("LOBBY_CAPTURE_REPORT_TIMESTAMP", "tracked-artifact-build")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["item", "status", "evidence", "nextAction"]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    by_item = {row["item"]: row for row in rows}
    claim_boundary = by_item["claim-boundary"]
    p1 = by_item["p1-procurement-calibration-actions"]
    sam_status = by_item["sam-live-status"]
    sam_rows = by_item["representative-sam-fpds-action-history"]
    lines = [
        "# Procurement Refresh Readiness",
        "",
        (
            "This no-network preflight describes how to refresh the procurement bridge without "
            "spending quota during ordinary paper builds. It is an operational guardrail, not "
            "a source moment or empirical validation result."
        ),
        "",
        "## Publication Boundary",
        "",
        f"- {claim_boundary['evidence']}",
        f"- Representative SAM/FPDS action-history status: `{sam_rows['status']}` ({sam_rows['evidence']}).",
        f"- P1 procurement source-gap status: `{p1['status']}` ({p1['evidence']}).",
        "",
        "## Current SAM Status",
        "",
        f"- Status: `{sam_status['status']}`.",
        f"- Evidence: {sam_status['evidence']}",
        f"- Next action: {sam_status['nextAction']}",
        "",
        "## Refresh Modes",
        "",
        (
            "1. Preferred representative run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, "
            "`SAM_CONTRACT_AWARDS_EXTRACT_MODE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_FORMAT=json`, "
            "`SAM_API_KEY`, and `SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID`, then run "
            "`scripts/run-2024-env-live-snapshot.sh` after quota/access is available."
        ),
        (
            "2. Bounded diagnostic run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, "
            "`SAM_CONTRACT_AWARDS_OFFSET_STARTS`, and either department-code or "
            "PIID-subtier filters, then compare the resulting rows against the bounded "
            "USAspending action panel."
        ),
        (
            "3. Fallback path: keep the USAspending transaction/action panel as a schema and "
            "directional diagnostic if SAM is unavailable, quota-blocked, or returns no rows."
        ),
        "",
        "## Safety Rules",
        "",
        "- Respect SAM.gov 429 `nextAccessTime` values before rerunning quota-limited refreshes.",
        "- Keep `SOURCE_FETCH_CURL_FALLBACK=1` enabled when SAM responds to curl but hangs under urllib.",
        "- Do not promote partial SAM payloads or timeout logs as source evidence.",
        "- Rebuild with `make paper-artifacts-check` after any archived source refresh.",
        "",
        "## Readiness Checklist",
        "",
        "| Item | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['item']} | {row['status']} | {row['evidence']} | {row['nextAction']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
