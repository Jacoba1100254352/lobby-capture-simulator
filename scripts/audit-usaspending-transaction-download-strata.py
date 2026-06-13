#!/usr/bin/env python3
"""Audit and optionally download no-key USAspending transaction strata.

This operational tool exists for the remaining procurement source gap. It uses
USAspending's public download/count and download/transactions endpoints to
identify a deterministic set of fiscal-year transaction strata that fit under
the row-limited download ceiling. Count-only mode is safe for quick audits. Full
downloads require --download and write only ignored local data/raw outputs.
"""

from __future__ import annotations

import argparse
import calendar
import csv
from datetime import date, datetime, timedelta
from io import TextIOWrapper
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen, urlretrieve
import zipfile


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
RAW_DIR = ROOT / "data" / "raw" / "usaspending-transaction-downloads"
DEFAULT_OUTPUT = ROOT / "data" / "raw" / "usaspending-procurement-bulk-transactions.csv"
DEFAULT_AGENCIES = (
    "Environmental Protection Agency",
    "Department of Energy",
    "Department of the Interior",
    "Department of Agriculture",
    "Department of Transportation",
    "Department of Defense",
    "Department of Health and Human Services",
    "Department of Veterans Affairs",
    "Department of Homeland Security",
    "National Aeronautics and Space Administration",
    "General Services Administration",
    "Department of Commerce",
)
CONTRACT_AWARD_TYPES = (
    "A", "B", "C", "D",
    "IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C", "IDV_C", "IDV_D", "IDV_E",
)
DOWNLOAD_COLUMNS = (
    "award_id_piid",
    "parent_award_id_piid",
    "modification_number",
    "federal_action_obligation",
    "action_date",
    "recipient_name",
    "recipient_uei",
    "awarding_agency_name",
    "awarding_sub_agency_name",
    "award_type",
    "type_of_contract_pricing",
    "extent_competed",
    "number_of_offers_received",
)
NORMALIZED_FIELDS = (
    "awardId",
    "recipient",
    "agency",
    "subAgency",
    "awardType",
    "amount",
    "issueDomain",
    "awardCount",
    "uei",
    "piid",
    "modificationNumber",
    "actionDate",
    "competitionType",
    "numberOfOffers",
    "priceOnlyAward",
    "exPostModification",
    "protestFiled",
    "exclusionFlag",
    "firewallCovered",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base", default=os.environ.get("USASPENDING_API_BASE", "https://api.usaspending.gov/api/v2"))
    parser.add_argument("--fiscal-year", type=int, default=int_env("USASPENDING_TRANSACTION_DOWNLOAD_FISCAL_YEAR", 2024))
    parser.add_argument("--agencies", default=os.environ.get("USASPENDING_TRANSACTION_DOWNLOAD_AGENCIES", ",".join(DEFAULT_AGENCIES)))
    parser.add_argument("--max-rows", type=int, default=int_env("USASPENDING_TRANSACTION_DOWNLOAD_MAX_ROWS", 500000))
    parser.add_argument("--poll-attempts", type=int, default=int_env("USASPENDING_TRANSACTION_DOWNLOAD_POLL_ATTEMPTS", 60))
    parser.add_argument("--poll-seconds", type=float, default=float_env("USASPENDING_TRANSACTION_DOWNLOAD_POLL_SECONDS", 5.0))
    parser.add_argument("--limit-per-stratum", type=int, default=0, help="Optional smoke-test row limit per stratum.")
    parser.add_argument("--download", action="store_true", help="Download and normalize strata after the count audit passes.")
    args = parser.parse_args()

    args.reports.mkdir(parents=True, exist_ok=True)
    strata = build_strata(args)
    downloaded_rows = 0
    output_path = ""
    if args.download:
        blocked = [row for row in strata if row["status"] == "blocked"]
        if blocked:
            raise SystemExit("Refusing download because at least one stratum is blocked.")
        downloaded_rows = download_strata(args, strata)
        output_path = str(args.output)

    write_csv(args.reports / "usaspending-transaction-download-strata.csv", strata)
    write_markdown(
        args.reports / "usaspending-transaction-download-strata.md",
        strata,
        downloaded_rows=downloaded_rows,
        output_path=output_path,
        args=args,
    )
    print(f"Wrote {args.reports / 'usaspending-transaction-download-strata.csv'}")
    print(f"Wrote {args.reports / 'usaspending-transaction-download-strata.md'}")
    if args.download:
        print(f"Wrote {args.output}")
    return 0 if not any(row["status"] == "blocked" for row in strata) else 1


def build_strata(args: argparse.Namespace) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for agency in split_csv(args.agencies):
        for label, start, end in fiscal_quarters(args.fiscal_year):
            rows.extend(strata_for_period(args, agency, label, start, end))
    return rows


def strata_for_period(
        args: argparse.Namespace,
        agency: str,
        label: str,
        start: date,
        end: date,
) -> list[dict[str, str]]:
    payload = count_payload(agency, start, end)
    response = post_json(endpoint(args.base, "/download/count/"), payload)
    count = int(response.get("calculated_count") or response.get("calculated_transaction_count") or 0)
    maximum = int(response.get("maximum_limit") or response.get("maximum_transaction_limit") or args.max_rows)
    over_limit = bool(response.get("rows_gt_limit") or response.get("transaction_rows_gt_limit") or count > maximum)
    effective_limit = min(maximum, args.max_rows)
    if count <= effective_limit and not over_limit:
        return [stratum_row(agency, label, start, end, count, effective_limit, "ready", "count fits public download limit")]
    if (end - start).days > 31:
        rows: list[dict[str, str]] = []
        for month_start, month_end in month_ranges(start, end):
            rows.extend(strata_for_period(args, agency, f"{label}-{month_start:%Y-%m}", month_start, month_end))
        return rows
    if (end - start).days > 0:
        rows = []
        for day in day_ranges(start, end):
            rows.extend(strata_for_period(args, agency, f"{label}-{day:%Y-%m-%d}", day, day))
        return rows
    return [stratum_row(agency, label, start, end, count, effective_limit, "blocked", "single-day stratum exceeds public download limit")]


def count_payload(agency: str, start: date, end: date) -> dict[str, object]:
    return {
        "spending_level": "transactions",
        "filters": filters(agency, start, end),
    }


def download_payload(agency: str, start: date, end: date, limit: int) -> dict[str, object]:
    payload: dict[str, object] = {
        "filters": filters(agency, start, end),
        "columns": list(DOWNLOAD_COLUMNS),
        "file_format": "csv",
    }
    if limit > 0:
        payload["limit"] = limit
    return payload


def filters(agency: str, start: date, end: date) -> dict[str, object]:
    return {
        "time_period": [{"start_date": start.isoformat(), "end_date": end.isoformat()}],
        "award_type_codes": list(CONTRACT_AWARD_TYPES),
        "agencies": [{"type": "awarding", "tier": "toptier", "name": agency}],
    }


def stratum_row(
        agency: str,
        label: str,
        start: date,
        end: date,
        count: int,
        maximum: int,
        status: str,
        notes: str,
) -> dict[str, str]:
    return {
        "agency": agency,
        "period": label,
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "transactionCount": str(count),
        "downloadLimit": str(maximum),
        "status": status,
        "downloadFile": "",
        "normalizedRows": "0",
        "notes": notes,
    }


def download_strata(args: argparse.Namespace, strata: list[dict[str, str]]) -> int:
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with args.output.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=NORMALIZED_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in strata:
            count = int(row["transactionCount"])
            limit = args.limit_per_stratum if args.limit_per_stratum > 0 else count
            payload = download_payload(row["agency"], parse_date(row["startDate"]), parse_date(row["endDate"]), limit)
            created = post_json(endpoint(args.base, "/download/transactions/"), payload)
            file_url = poll_download(args, created)
            zip_path = args.raw_dir / f"{slug(row['agency'])}-{row['startDate']}-{row['endDate']}.zip"
            urlretrieve(file_url, zip_path)
            normalized = write_normalized_zip_rows(zip_path, writer)
            row["downloadFile"] = str(zip_path)
            row["normalizedRows"] = str(normalized)
            total += normalized
    return total


def poll_download(args: argparse.Namespace, created: dict[str, object]) -> str:
    status_url = str(created.get("status_url", ""))
    file_name = str(created.get("file_name", ""))
    file_url = str(created.get("file_url", ""))
    if not status_url:
        raise RuntimeError(f"USAspending download did not return a status_url: {created}")
    if "localhost" in status_url and file_name:
        status_url = endpoint(args.base, f"/download/status?file_name={file_name}")
    for _ in range(args.poll_attempts):
        status = get_json(status_url)
        state = str(status.get("status", ""))
        if state in {"finished", "ready"}:
            file_url = str(status.get("file_url") or file_url)
            break
        if state == "failed":
            raise RuntimeError(f"USAspending download failed: {status.get('message')}")
        time.sleep(args.poll_seconds)
    else:
        raise TimeoutError(f"USAspending download did not finish after {args.poll_attempts} polls: {status_url}")
    if file_url.startswith("/"):
        return urljoin("https://api.usaspending.gov", file_url)
    return file_url


def write_normalized_zip_rows(zip_path: Path, writer: csv.DictWriter) -> int:
    count = 0
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if "PrimeTransactions" not in name or not name.endswith(".csv"):
                continue
            with archive.open(name) as source:
                reader = csv.DictReader(TextIOWrapper(source, encoding="utf-8-sig", newline=""))
                for raw in reader:
                    writer.writerow(normalized_row(raw))
                    count += 1
    return count


def normalized_row(raw: dict[str, str]) -> dict[str, object]:
    modification_number = first(raw, "modification_number")
    competition_type = first(raw, "extent_competed")
    number_of_offers = first(raw, "number_of_offers_received") or "0"
    amount = money_millions(first(raw, "federal_action_obligation"))
    return {
        "awardId": first(raw, "award_id_piid", "parent_award_id_piid") or "UNKNOWN",
        "recipient": first(raw, "recipient_name") or "Unknown recipient",
        "agency": first(raw, "awarding_agency_name") or "Unknown agency",
        "subAgency": first(raw, "awarding_sub_agency_name") or "Unknown agency",
        "awardType": first(raw, "award_type") or "contract",
        "amount": f"{amount:.8f}",
        "issueDomain": "procurement",
        "awardCount": "1",
        "uei": first(raw, "recipient_uei"),
        "piid": first(raw, "award_id_piid"),
        "modificationNumber": modification_number or "0",
        "actionDate": first(raw, "action_date"),
        "competitionType": competition_type or "unknown",
        "numberOfOffers": number_of_offers,
        "priceOnlyAward": str(price_only_procurement_flag(number_of_offers, competition_type)).lower(),
        "exPostModification": str(modification_sequence(modification_number) > 0).lower(),
        "protestFiled": "false",
        "exclusionFlag": str("exclusion" in competition_type.lower()).lower(),
        "firewallCovered": "false",
    }


def price_only_procurement_flag(number_of_offers: str, competition_type: str) -> bool:
    return numeric(number_of_offers) == 1 or "only one" in competition_type.lower() or "not competed" in competition_type.lower()


def modification_sequence(value: str) -> int:
    text = str(value or "").strip()
    if not text or text.lower() in {"0", "0.0", "none", "null", "nan"}:
        return 0
    digits = ""
    for char in reversed(text):
        if char.isdigit():
            digits = char + digits
        elif digits:
            break
    return int(digits) if digits else 0


def money_millions(value: str) -> float:
    return numeric(value) / 1_000_000.0


def numeric(value: str) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = str(row.get(key, "")).strip()
        if value:
            return value
    return ""


def fiscal_quarters(fiscal_year: int) -> list[tuple[str, date, date]]:
    previous = fiscal_year - 1
    return [
        ("Q1", date(previous, 10, 1), date(previous, 12, 31)),
        ("Q2", date(fiscal_year, 1, 1), date(fiscal_year, 3, 31)),
        ("Q3", date(fiscal_year, 4, 1), date(fiscal_year, 6, 30)),
        ("Q4", date(fiscal_year, 7, 1), date(fiscal_year, 9, 30)),
    ]


def month_ranges(start: date, end: date) -> list[tuple[date, date]]:
    current = date(start.year, start.month, 1)
    ranges: list[tuple[date, date]] = []
    while current <= end:
        last_day = calendar.monthrange(current.year, current.month)[1]
        month_end = date(current.year, current.month, last_day)
        ranges.append((max(start, current), min(end, month_end)))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return ranges


def day_ranges(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "lobby-capture-simulator/1.0"},
    )
    with urlopen(request, timeout=90) as response:
        decoded = json.loads(response.read())
    if not isinstance(decoded, dict):
        raise RuntimeError(f"POST {url} returned a non-object response.")
    return decoded


def get_json(url: str) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": "lobby-capture-simulator/1.0"})
    with urlopen(request, timeout=90) as response:
        decoded = json.loads(response.read())
    if not isinstance(decoded, dict):
        raise RuntimeError(f"GET {url} returned a non-object response.")
    return decoded


def endpoint(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["agency", "period", "startDate", "endDate", "transactionCount", "downloadLimit", "status", "downloadFile", "normalizedRows", "notes"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
        path: Path,
        rows: list[dict[str, str]],
        *,
        downloaded_rows: int,
        output_path: str,
        args: argparse.Namespace,
) -> None:
    total = sum(int(row["transactionCount"]) for row in rows)
    blocked = [row for row in rows if row["status"] == "blocked"]
    max_row = max(rows, key=lambda row: int(row["transactionCount"])) if rows else {}
    lines = [
        "# USAspending Transaction Download Strata Audit",
        "",
        (
            "This live operational audit uses USAspending's no-key public count/download endpoints "
            "to plan representative transaction-history acquisition. It is not a source moment until "
            "the ZIP strata are downloaded, normalized, frozen into a snapshot, and rerun through validation."
        ),
        "",
        f"- Fiscal year: `{args.fiscal_year}`",
        f"- Agencies: `{len(set(row['agency'] for row in rows))}`",
        f"- Download strata: `{len(rows)}`",
        f"- Planned transaction rows: `{total}`",
        f"- Blocked strata: `{len(blocked)}`",
        f"- Largest stratum: `{max_row.get('agency', '')} {max_row.get('period', '')}` with `{max_row.get('transactionCount', '0')}` rows",
        f"- Downloaded normalized rows: `{downloaded_rows}`",
    ]
    if output_path:
        lines.append(f"- Normalized output: `{output_path}`")
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        (
            "A clean count audit means the no-key USAspending transaction download path is feasible. "
            "It does not by itself clear the SAM/FPDS procurement calibration blocker. Claim clearance "
            "requires archived transaction rows, source-moment regeneration, validation, calibration-readiness "
            "review, and the full paper artifact gate."
        ),
        "",
        "## Strata",
        "",
        "| Agency | Period | Dates | Count | Limit | Status | Notes |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {agency} | {period} | {startDate} to {endDate} | {transactionCount} | {downloadLimit} | {status} | {notes} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Full Download Command",
        "",
        "```sh",
        "python3 scripts/audit-usaspending-transaction-download-strata.py --download",
        "```",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def float_env(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


if __name__ == "__main__":
    raise SystemExit(main())
