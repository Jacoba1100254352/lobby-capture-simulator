#!/usr/bin/env python3
"""Build an optional state-lobbying control panel for HLOGA substitution.

This live acquisition helper pulls official Colorado Secretary of State
professional-lobbyist income rows around the federal HLOGA treatment date. The
rows are used only as an unaffected-jurisdiction state-lobbying control surface;
they are not evidence that a Colorado client lacked separate federal LDA
exposure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRST_WAVE = ROOT / "data" / "calibration" / "first-wave"
REPORTS = ROOT / "reports"
PANEL_PATH = FIRST_WAVE / "substitution-state-lobbying-control-panel.csv"
REPORT_CSV = REPORTS / "substitution-state-lobbying-control-panel.csv"
REPORT_MD = REPORTS / "substitution-state-lobbying-control-panel.md"
DEFAULT_REVIEW_DATE = "2026-07-24"
COLORADO_API = "https://data.colorado.gov/resource/dxfk-9ifj.csv"
COLORADO_DATASET_URL = (
    "https://data.colorado.gov/Legislative/"
    "Professional-Lobbyist-Income-in-Colorado/dxfk-9ifj"
)
SOURCE_SYSTEM = "Colorado Secretary of State lobbyist income data"
REFORM_EVENT_ID = "hloga-2007-federal-lobbying-disclosure"
TREATMENT_START = "2007-09-14"
CONTROL_GROUP = "control_unaffected_colorado_state_lobbying_jurisdiction"
REVIEWER = "codex-source-audit"

API_FIELDS = [
    "lobbyistname",
    "primarylobbyistid",
    "annuallobbyistregistrationid",
    "clientname",
    "businesstype",
    "industrytradetype",
    "incomeamount",
    "dateincomereceived",
    "reportmonth",
    "reportduedate",
    "fiscalyear",
]

STATE_LOCAL_TERMS = (
    "COLORADO",
    "COLO",
    "DENVER",
    "BOULDER",
    "AURORA",
    "ADAMS",
    "ARAPAHOE",
    "DOUGLAS",
    "JEFFERSON",
    "MESA",
    "PUEBLO",
    "WELD",
)

PANEL_FIELDS = [
    "canonicalActorId",
    "primaryName",
    "stateClientKey",
    "stateClientName",
    "lobbyistName",
    "primaryLobbyistId",
    "annualLobbyistRegistrationId",
    "businessType",
    "industryTradeType",
    "sourceDate",
    "reportMonth",
    "reportDueDate",
    "fiscalYear",
    "issueCode",
    "periodStart",
    "periodEnd",
    "venue",
    "activityType",
    "activityMeasure",
    "activityAmount",
    "sourceSystem",
    "sourceRecordId",
    "exposureGroup",
    "reformEventId",
    "activityUnits",
    "jurisdiction",
    "matchConfidence",
    "reviewStatus",
    "evidenceRule",
    "reviewer",
    "reviewDate",
    "sourceUrl",
    "notes",
]

REPORT_FIELDS = [
    "generatedAt",
    "canonicalActorId",
    "primaryName",
    "status",
    "sourceRows",
    "preRows",
    "postRows",
    "totalIncome",
    "firstDate",
    "lastDate",
    "businessTypes",
    "issueCodes",
    "sourceUrl",
    "nextAction",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-wave", type=Path, default=FIRST_WAVE)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=PANEL_PATH)
    parser.add_argument("--max-control-clients", type=int, default=25)
    parser.add_argument("--source-row-limit", type=int, default=50000)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument(
        "--review-date",
        default=os.environ.get("SUBSTITUTION_STATE_CONTROL_REVIEW_DATE", DEFAULT_REVIEW_DATE),
    )
    args = parser.parse_args()

    first_wave = resolve(args.first_wave)
    reports = resolve(args.reports)
    output = resolve(args.output)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    excluded_names = exact_federal_treated_names(first_wave)
    source_rows = fetch_colorado_rows(args.source_row_limit, args.timeout)
    selected_keys = select_control_clients(source_rows, excluded_names, args.max_control_clients)

    panel_rows = [
        panel_row(row, args.review_date, index)
        for index, row in enumerate(source_rows, start=1)
        if client_key(row.get("clientname", "")) in selected_keys
    ]
    panel_rows.sort(key=lambda row: (
        row["canonicalActorId"],
        row["periodStart"],
        row["sourceRecordId"],
    ))
    report_rows = report_summary_rows(panel_rows, generated_at)

    output.parent.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    write_csv(output, panel_rows, PANEL_FIELDS)
    write_csv(reports / REPORT_CSV.name, report_rows, REPORT_FIELDS)
    write_markdown(reports / REPORT_MD.name, panel_rows, report_rows, generated_at, len(source_rows))
    print(f"Wrote {output}")
    print(f"Wrote {reports / REPORT_CSV.name}")
    print(f"Wrote {reports / REPORT_MD.name}")
    return 0


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def exact_federal_treated_names(first_wave: Path) -> set[str]:
    names = set()
    for row in read_csv(first_wave / "substitution-historical-lda-panel.csv"):
        for field in ("primaryName", "clientName"):
            key = normalize_name(row.get(field, ""))
            if key:
                names.add(key)
    return names


def fetch_colorado_rows(limit: int, timeout: float) -> list[dict[str, str]]:
    params = {
        "$select": ", ".join(API_FIELDS),
        "$where": (
            "dateincomereceived between "
            "'2007-01-01T00:00:00' and '2008-12-31T23:59:59'"
        ),
        "$order": "clientname, dateincomereceived, primarylobbyistid",
        "$limit": str(limit),
    }
    url = os.environ.get("COLORADO_LOBBYING_INCOME_API", COLORADO_API) + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "Codex source audit"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit(f"Could not fetch Colorado lobbying income rows: {exc}") from exc
    return list(csv.DictReader(io.StringIO(text)))


def select_control_clients(
    rows: list[dict[str, str]],
    excluded_names: set[str],
    limit: int,
) -> set[str]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = client_key(row.get("clientname", ""))
        if key and key not in excluded_names:
            grouped[key].append(row)

    candidates: list[tuple[int, float, int, str]] = []
    for key, client_rows in grouped.items():
        pre, post = coverage_counts(client_rows)
        if not pre or not post:
            continue
        name = client_rows[0].get("clientname", "")
        state_local_rank = 1 if any(term in normalize_name(name) for term in STATE_LOCAL_TERMS) else 0
        amount = sum(money(row.get("incomeamount", "")) for row in client_rows)
        candidates.append((state_local_rank, amount, len(client_rows), key))
    candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3]), reverse=True)
    return {key for *_unused, key in candidates[:limit]}


def panel_row(source_row: dict[str, str], review_date: str, index: int) -> dict[str, str]:
    name = source_row.get("clientname", "")
    key = client_key(name)
    actor_id = "co-control-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    source_date = iso_date(source_row.get("dateincomereceived", ""))
    amount = money(source_row.get("incomeamount", ""))
    issue = issue_code(source_row)
    source_record_id = "|".join([
        source_row.get("primarylobbyistid", ""),
        source_row.get("annuallobbyistregistrationid", ""),
        key,
        source_date,
        str(index),
    ])
    return {
        "canonicalActorId": actor_id,
        "primaryName": name,
        "stateClientKey": key,
        "stateClientName": name,
        "lobbyistName": source_row.get("lobbyistname", ""),
        "primaryLobbyistId": source_row.get("primarylobbyistid", ""),
        "annualLobbyistRegistrationId": source_row.get("annuallobbyistregistrationid", ""),
        "businessType": source_row.get("businesstype", ""),
        "industryTradeType": source_row.get("industrytradetype", ""),
        "sourceDate": source_date,
        "reportMonth": source_row.get("reportmonth", ""),
        "reportDueDate": iso_date(source_row.get("reportduedate", "")),
        "fiscalYear": source_row.get("fiscalyear", ""),
        "issueCode": issue,
        "periodStart": source_date,
        "periodEnd": source_date,
        "venue": "state_lobbying",
        "activityType": "state_lobbying_income",
        "activityMeasure": f"{amount:.4f}",
        "activityAmount": f"{amount / 1_000_000.0:.4f}",
        "sourceSystem": SOURCE_SYSTEM,
        "sourceRecordId": source_record_id,
        "exposureGroup": CONTROL_GROUP,
        "reformEventId": REFORM_EVENT_ID,
        "activityUnits": "income_dollars; amount_millions",
        "jurisdiction": "Colorado state",
        "matchConfidence": "0.7000",
        "reviewStatus": "reviewed_official_state_lobbying_control_source_row",
        "evidenceRule": "official-colorado-state-lobbying-income-row-with-observed-prepost-client-coverage",
        "reviewer": REVIEWER,
        "reviewDate": review_date,
        "sourceUrl": COLORADO_DATASET_URL,
        "notes": (
            "official Colorado Secretary of State professional-lobbyist income row; "
            "usable as an unaffected-state-jurisdiction control surface for the "
            "federal HLOGA shock only; does not prove the client lacks separate "
            "federal LDA exposure and does not clear calibrated policy claims"
        ),
    }


def report_summary_rows(panel_rows: list[dict[str, str]], generated_at: str) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in panel_rows:
        grouped[row["canonicalActorId"]].append(row)
    summaries: list[dict[str, str]] = []
    for actor_id, rows in sorted(grouped.items(), key=lambda item: item[1][0]["primaryName"]):
        pre, post = coverage_counts(rows)
        dates = sorted(row["periodStart"] for row in rows if row.get("periodStart"))
        total_income = sum(float(row.get("activityMeasure", "0") or 0) for row in rows)
        summaries.append({
            "generatedAt": generated_at,
            "canonicalActorId": actor_id,
            "primaryName": rows[0].get("primaryName", ""),
            "status": "prepost_control_source_rows" if pre and post else "incomplete_control_source_rows",
            "sourceRows": str(len(rows)),
            "preRows": str(pre),
            "postRows": str(post),
            "totalIncome": f"{total_income:.2f}",
            "firstDate": dates[0] if dates else "",
            "lastDate": dates[-1] if dates else "",
            "businessTypes": "; ".join(sorted({row.get("businessType", "") for row in rows if row.get("businessType", "")})),
            "issueCodes": "; ".join(sorted({row.get("issueCode", "") for row in rows if row.get("issueCode", "")})),
            "sourceUrl": COLORADO_DATASET_URL,
            "nextAction": (
                "Use only as a Colorado state-jurisdiction control in the HLOGA source panel; "
                "run falsification and sensitivity checks before estimating substitution."
            ),
        })
    return summaries


def coverage_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    pre = post = 0
    treatment = datetime.fromisoformat(TREATMENT_START)
    for row in rows:
        value = row.get("dateincomereceived", row.get("periodStart", ""))
        dt = parse_date(value)
        if dt is None:
            continue
        if dt < treatment:
            pre += 1
        else:
            post += 1
    return pre, post


def issue_code(row: dict[str, str]) -> str:
    issue = row.get("industrytradetype") or row.get("businesstype") or "unclassified"
    return "co-state-" + slug(issue)


def client_key(value: str) -> str:
    return normalize_name(value)


def normalize_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", (value or "").upper()).strip()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-") or "unclassified"


def money(value: str) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def parse_date(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def iso_date(value: str) -> str:
    parsed = parse_date(value)
    return parsed.date().isoformat() if parsed else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    panel_rows: list[dict[str, str]],
    report_rows: list[dict[str, str]],
    generated_at: str,
    source_row_count: int,
) -> None:
    pre, post = coverage_counts(panel_rows)
    status_counts = Counter(row["status"] for row in report_rows)
    total_income = sum(float(row.get("activityMeasure", "0") or 0) for row in panel_rows)
    lines = [
        "# Substitution State-Lobbying Control Panel",
        "",
        f"Generated: `{generated_at}`",
        "",
        "This optional live-acquisition artifact uses the official Colorado Secretary of State professional-lobbyist income dataset to add an unaffected-state-jurisdiction control surface around the federal HLOGA treatment date. It supplies source rows for comparison/control assignment only; it does not prove that any client lacks separate federal LDA exposure and does not clear calibrated policy claims.",
        "",
        "## Summary",
        "",
        f"- Source rows inspected: `{source_row_count}`",
        f"- Control clients selected: `{len(report_rows)}`",
        f"- Panel rows: `{len(panel_rows)}`",
        f"- Pre-HLOGA control rows: `{pre}`",
        f"- Post-HLOGA control rows: `{post}`",
        f"- Total reported state-lobbying income: `{total_income:.2f}`",
        f"- Source dataset: {COLORADO_DATASET_URL}",
        "- Claim status: `source-acquisition control surface only; effect estimation and calibrated policy claims remain blocked`",
        "",
        "## Status Counts",
        "",
        "| Status | Clients |",
        "| --- | ---: |",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend([
        "",
        "## Control Acquisition Rows",
        "",
        "| Client | Status | Rows | Pre | Post | Total income | First | Last | Issue codes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ])
    for row in report_rows:
        lines.append(
            f"| {md(row['primaryName'])} | `{row['status']}` | {row['sourceRows']} | "
            f"{row['preRows']} | {row['postRows']} | {row['totalIncome']} | "
            f"{row['firstDate']} | {row['lastDate']} | {md(row['issueCodes'])} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
