#!/usr/bin/env python3
"""Fetch source-native public data and normalize it to simulator schemas."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import html
from html.parser import HTMLParser
from io import BytesIO, StringIO
import json
import multiprocessing
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import time
import tempfile
import zipfile
import zlib
from http.client import RemoteDisconnected
from datetime import date, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote_plus, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


MODEL_DOMAINS = ("energy", "technology", "finance", "procurement", "democracy")
RAW_SEQUENCE = 0
USASPENDING_ALL_AGENCIES = {"*", "all", "all-federal", "all_federal", "federal", "none"}


class SourceHttpStatus(Exception):
    def __init__(self, code: int, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(f"HTTP {code}")
        self.code = code
        self.detail = detail
        self.headers = headers or {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="kind", required=True)

    lda = subparsers.add_parser("lda", help="Fetch LDA REST filings.")
    lda.add_argument("--output", type=Path, default=Path("data/raw/lda-lobbying.csv"))

    fec = subparsers.add_parser("fec", help="Fetch FEC OpenFEC schedule A records.")
    fec.add_argument("--output", type=Path, default=Path("data/raw/fec-campaign-finance.csv"))

    revolving_door = subparsers.add_parser("revolving-door", help="Derive revolving-door rows from LDA covered-position filings.")
    revolving_door.add_argument("--output", type=Path, default=Path("data/raw/revolving-door.csv"))

    regulatory = subparsers.add_parser("regulatory", help="Fetch Regulations.gov or Federal Register records.")
    regulatory.add_argument("--output", type=Path, default=Path("data/raw/regulatory-dockets.csv"))

    oira_meetings = subparsers.add_parser("oira-meetings", help="Fetch Reginfo.gov EO 12866 public meeting disclosures.")
    oira_meetings.add_argument("--output", type=Path, default=Path("data/raw/oira-meetings.csv"))

    usaspending = subparsers.add_parser("usaspending", help="Fetch USAspending award records.")
    usaspending.add_argument("--output", type=Path, default=Path("data/raw/usaspending-awards.csv"))

    usaspending_actions = subparsers.add_parser("usaspending-actions", help="Fetch USAspending transaction/action rows for procurement modification diagnostics.")
    usaspending_actions.add_argument("--output", type=Path, default=Path("data/raw/usaspending-procurement-actions.csv"))

    sam_contract_awards = subparsers.add_parser("sam-contract-awards", help="Fetch SAM.gov Contract Awards rows into the procurement action schema.")
    sam_contract_awards.add_argument("--output", type=Path, default=Path("data/raw/sam-contract-awards.csv"))

    sam_contract_awards_export = subparsers.add_parser("sam-contract-awards-export", help="Normalize a downloaded SAM.gov Contract Awards CSV/JSON/ZIP export into the procurement action schema.")
    sam_contract_awards_export.add_argument("--input", type=Path)
    sam_contract_awards_export.add_argument("--url", default=os.environ.get("SAM_CONTRACT_AWARDS_LIVE_URL", "").strip())
    sam_contract_awards_export.add_argument("--output", type=Path, default=Path("data/raw/sam-contract-awards.csv"))

    nyc_public_financing = subparsers.add_parser("nyc-public-financing", help="Fetch NYC CFB public-funds payments.")
    nyc_public_financing.add_argument("--output", type=Path, default=Path("data/raw/public-financing.csv"))

    seattle_democracy_vouchers = subparsers.add_parser("seattle-democracy-vouchers", help="Fetch Seattle Democracy Voucher program rows.")
    seattle_democracy_vouchers.add_argument("--output", type=Path, default=Path("data/raw/public-financing.csv"))

    nyc_intermediaries = subparsers.add_parser("nyc-intermediaries", help="Fetch NYC CFB intermediary fundraising rows.")
    nyc_intermediaries.add_argument("--output", type=Path, default=Path("data/raw/intermediaries.csv"))

    irs_eo_bmf = subparsers.add_parser("irs-eo-bmf", help="Fetch IRS EO BMF nonprofit and association capacity rows.")
    irs_eo_bmf.add_argument("--output", type=Path, default=Path("data/raw/intermediaries.csv"))

    irs_dark_money_capacity = subparsers.add_parser("irs-dark-money-capacity", help="Fetch IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows.")
    irs_dark_money_capacity.add_argument("--output", type=Path, default=Path("data/raw/dark-money.csv"))

    propublica_nonprofit_routing = subparsers.add_parser("propublica-nonprofit-routing", help="Fetch ProPublica Nonprofit Explorer Form 990 Schedule I grant-routing rows.")
    propublica_nonprofit_routing.add_argument("--output", type=Path, default=Path("data/raw/dark-money.csv"))

    irs_527 = subparsers.add_parser("irs-527", help="Fetch IRS POFD Form 8872 political-organization rows.")
    irs_527.add_argument("--output", type=Path, default=Path("data/raw/intermediaries.csv"))

    args = parser.parse_args()
    if args.kind == "lda":
        return fetch_lda(args.output)
    if args.kind == "fec":
        return fetch_fec(args.output)
    if args.kind == "revolving-door":
        return fetch_revolving_door(args.output)
    if args.kind == "regulatory":
        return fetch_regulatory(args.output)
    if args.kind == "oira-meetings":
        return fetch_oira_meetings(args.output)
    if args.kind == "usaspending":
        return fetch_usaspending(args.output)
    if args.kind == "usaspending-actions":
        return fetch_usaspending_actions(args.output)
    if args.kind == "sam-contract-awards":
        return fetch_sam_contract_awards(args.output)
    if args.kind == "sam-contract-awards-export":
        return fetch_sam_contract_awards_export(args.input, args.output, args.url)
    if args.kind == "nyc-public-financing":
        return fetch_nyc_public_financing(args.output)
    if args.kind == "seattle-democracy-vouchers":
        return fetch_seattle_democracy_vouchers(args.output)
    if args.kind == "nyc-intermediaries":
        return fetch_nyc_intermediaries(args.output)
    if args.kind == "irs-eo-bmf":
        return fetch_irs_eo_bmf(args.output)
    if args.kind == "irs-dark-money-capacity":
        return fetch_irs_dark_money_capacity(args.output)
    if args.kind == "propublica-nonprofit-routing":
        return fetch_propublica_nonprofit_routing(args.output)
    if args.kind == "irs-527":
        return fetch_irs_527(args.output)
    raise AssertionError(args.kind)


def fetch_lda(output: Path) -> int:
    base = os.environ.get("LDA_API_BASE", "https://lda.gov/api/v1").rstrip("/")
    params = {
        "page_size": os.environ.get("LDA_PAGE_SIZE", "25"),
    }
    if os.environ.get("LDA_YEAR"):
        params["filing_year"] = os.environ["LDA_YEAR"]
    if os.environ.get("LDA_PERIOD"):
        params["filing_period"] = os.environ["LDA_PERIOD"]
    headers = {}
    if os.environ.get("LDA_API_KEY"):
        headers["Authorization"] = f"Token {os.environ['LDA_API_KEY']}"

    records = []
    next_url = f"{base}/filings/?{urlencode(params)}"
    max_pages = int(os.environ.get("LDA_MAX_PAGES", "2"))
    for _ in range(max_pages):
        payload = get_json(next_url, headers)
        records.extend(payload.get("results", payload if isinstance(payload, list) else []))
        next_url = payload.get("next") if isinstance(payload, dict) else None
        if not next_url:
            break

    records = [record for record in records if record_matches_lda_filters(record)]
    rows = normalize_lda_records(records)
    write_rows(output, ["client", "registrant", "issueDomain", "amount", "disclosureLag", "coveredOfficialShare"], rows, "LDA filings")
    return 0


def normalize_lda_records(records: list[dict[str, object]]) -> list[dict[str, float | str]]:
    grouped: dict[tuple[str, str, str], dict[str, float | str]] = {}
    for record in records:
        client = first_text(record, "client.name", "client_name", "client", default="Unknown client")
        registrant = first_text(record, "registrant.name", "registrant_name", "registrant", default="Unknown registrant")
        amount = money_millions(first_text(record, "income", "expenses", "amount", default="0"))
        disclosure_lag = disclosure_lag_score(first_text(record, "filing_date", "dt_posted", "filing_dt", default=""))
        covered_share = round(0.20 + (0.10 if first_text(record, "lobbyists", "covered_position", default="") else 0.0), 4)
        for issue in issue_domains_from_lda(record):
            key = (client, registrant, issue)
            existing = grouped.setdefault(
                key,
                {
                    "client": client,
                    "registrant": registrant,
                    "issueDomain": issue,
                    "amount": 0.0,
                    "disclosureLag": disclosure_lag,
                    "coveredOfficialShare": covered_share,
                },
            )
            existing["amount"] = float(existing["amount"]) + amount
            existing["disclosureLag"] = max(float(existing["disclosureLag"]), disclosure_lag)
            existing["coveredOfficialShare"] = max(float(existing["coveredOfficialShare"]), covered_share)
    return [grouped[key] for key in sorted(grouped)]


def fetch_fec(output: Path) -> int:
    api_key = os.environ.get("FEC_API_KEY")
    if not api_key:
        raise SystemExit("Set FEC_API_KEY before running ./scripts/fetch-fec.sh --live without FEC_LIVE_CSV or FEC_LIVE_URL.")
    base = os.environ.get("FEC_API_BASE", "https://api.open.fec.gov/v1").rstrip("/")
    rows = []
    if os.environ.get("FEC_ONLY_SCHEDULE_E", "0") != "1":
        params = {
            "api_key": api_key,
            "per_page": os.environ.get("FEC_PAGE_SIZE", "50"),
            "sort": "-contribution_receipt_amount",
            "two_year_transaction_period": os.environ.get("FEC_CYCLE", "2024"),
        }
        if os.environ.get("FEC_COMMITTEE_ID"):
            params["committee_id"] = os.environ["FEC_COMMITTEE_ID"]
        payload = get_json(f"{base}/schedules/schedule_a/?{urlencode(params)}")
        rows.extend(normalize_fec_contribution_records(payload.get("results", [])))

    if os.environ.get("FEC_INCLUDE_SCHEDULE_E", "1") == "1":
        rows.extend(fetch_fec_outside_spending_rows(base, api_key))
    if os.environ.get("FEC_INCLUDE_ELECTIONEERING", os.environ.get("FEC_INCLUDE_ELECTORAL_COMMUNICATIONS", "0")) == "1":
        rows.extend(fetch_fec_electioneering_rows(base, api_key))
    if os.environ.get("FEC_INCLUDE_COMMUNICATION_COSTS", os.environ.get("FEC_INCLUDE_ELECTORAL_COMMUNICATIONS", "0")) == "1":
        rows.extend(fetch_fec_communication_cost_rows(base, api_key))

    write_rows(output, FEC_FIELDS, rows, "OpenFEC campaign finance, independent-expenditure, electioneering, and communication-cost records")
    return 0


FEC_FIELDS = [
    "source",
    "recipient",
    "issueDomain",
    "amount",
    "flowType",
    "traceability",
    "largeDonorShare",
    "sourceRecordId",
    "sourceUrl",
    "committeeType",
    "spendingPurpose",
    "supportOppose",
    "disclosureLag",
]


def fetch_fec_outside_spending_rows(base: str, api_key: str) -> list[dict[str, object]]:
    params = {
        "api_key": api_key,
        "per_page": os.environ.get("FEC_SCHEDULE_E_PAGE_SIZE", os.environ.get("FEC_PAGE_SIZE", "50")),
        "cycle": os.environ.get("FEC_CYCLE", "2024"),
        "sort": os.environ.get("FEC_SCHEDULE_E_SORT", "-expenditure_date"),
        "min_amount": os.environ.get("FEC_SCHEDULE_E_MIN_AMOUNT", "1000"),
    }
    if os.environ.get("FEC_SCHEDULE_E_COMMITTEE_ID"):
        params["committee_id"] = os.environ["FEC_SCHEDULE_E_COMMITTEE_ID"]
    rows = []
    max_pages = int_env("FEC_SCHEDULE_E_MAX_PAGES", 3, 1, 25)
    next_params = dict(params)
    for _ in range(max_pages):
        payload = get_json(f"{base}/schedules/schedule_e/?{urlencode(next_params)}")
        rows.extend(normalize_fec_independent_expenditure_records(payload.get("results", [])))
        last_indexes = nested(payload, "pagination.last_indexes")
        if not isinstance(last_indexes, dict) or not last_indexes:
            break
        next_params.update({key: str(value) for key, value in last_indexes.items() if value not in (None, "")})
    return rows


def fetch_fec_electioneering_rows(base: str, api_key: str) -> list[dict[str, object]]:
    params = {
        "api_key": api_key,
        "per_page": os.environ.get("FEC_ELECTIONEERING_PAGE_SIZE", os.environ.get("FEC_PAGE_SIZE", "50")),
        "report_year": os.environ.get("FEC_CYCLE", "2024"),
        "sort": os.environ.get("FEC_ELECTIONEERING_SORT", "-disbursement_date"),
        "min_amount": os.environ.get("FEC_ELECTIONEERING_MIN_AMOUNT", "1000"),
    }
    if os.environ.get("FEC_ELECTIONEERING_COMMITTEE_ID"):
        params["committee_id"] = os.environ["FEC_ELECTIONEERING_COMMITTEE_ID"]
    if os.environ.get("FEC_ELECTIONEERING_CANDIDATE_ID"):
        params["candidate_id"] = os.environ["FEC_ELECTIONEERING_CANDIDATE_ID"]
    rows = []
    max_pages = int_env("FEC_ELECTIONEERING_MAX_PAGES", 3, 1, 25)
    for page in range(1, max_pages + 1):
        page_params = dict(params)
        page_params["page"] = str(page)
        payload = get_json(f"{base}/electioneering/?{urlencode(page_params)}")
        rows.extend(normalize_fec_electioneering_records(payload.get("results", [])))
        pagination = payload.get("pagination", {}) if isinstance(payload, dict) else {}
        if not pagination.get("pages") or page >= int(pagination.get("pages", page)):
            break
    return rows


def fetch_fec_communication_cost_rows(base: str, api_key: str) -> list[dict[str, object]]:
    start_date, end_date = fec_cycle_window()
    params = {
        "api_key": api_key,
        "per_page": os.environ.get("FEC_COMMUNICATION_COST_PAGE_SIZE", os.environ.get("FEC_PAGE_SIZE", "50")),
        "min_date": os.environ.get("FEC_COMMUNICATION_COST_MIN_DATE", start_date),
        "max_date": os.environ.get("FEC_COMMUNICATION_COST_MAX_DATE", end_date),
        "min_amount": os.environ.get("FEC_COMMUNICATION_COST_MIN_AMOUNT", "1000"),
    }
    if os.environ.get("FEC_COMMUNICATION_COST_COMMITTEE_ID"):
        params["committee_id"] = os.environ["FEC_COMMUNICATION_COST_COMMITTEE_ID"]
    if os.environ.get("FEC_COMMUNICATION_COST_CANDIDATE_ID"):
        params["candidate_id"] = os.environ["FEC_COMMUNICATION_COST_CANDIDATE_ID"]
    rows = []
    max_pages = int_env("FEC_COMMUNICATION_COST_MAX_PAGES", 3, 1, 25)
    for page in range(1, max_pages + 1):
        page_params = dict(params)
        page_params["page"] = str(page)
        payload = get_json(f"{base}/communication_costs/?{urlencode(page_params)}")
        rows.extend(normalize_fec_communication_cost_records(payload.get("results", [])))
        pagination = payload.get("pagination", {}) if isinstance(payload, dict) else {}
        if not pagination.get("pages") or page >= int(pagination.get("pages", page)):
            break
    return rows


def normalize_fec_contribution_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for record in records:
        source = first_text(record, "contributor_name", "source", default="Unknown contributor")
        recipient = first_text(record, "committee.name", "committee_name", "recipient", default="Unknown recipient")
        amount = money_millions(first_text(record, "contribution_receipt_amount", "amount", default="0"))
        domain = classify_domain(" ".join([source, recipient, first_text(record, "contributor_employer", "contributor_occupation", default="")]))
        rows.append(
            {
                "source": source,
                "recipient": recipient,
                "issueDomain": domain,
                "amount": amount,
                "flowType": infer_fec_flow_type(recipient),
                "traceability": 0.78 if amount < 0.02 else 0.62,
                "largeDonorShare": min(0.95, 0.35 + (amount * 4.0)),
                "sourceRecordId": first_text(record, "transaction_id", "image_number", default=""),
                "sourceUrl": fec_source_url(first_text(record, "image_number", default="")),
                "committeeType": first_text(record, "committee.committee_type_full", "committee_type_full", default="recipient committee"),
                "spendingPurpose": first_text(record, "receipt_type_full", "memo_text", default="contribution"),
                "supportOppose": "",
                "disclosureLag": fec_visibility_lag(record),
            }
        )
    return rows


def normalize_fec_independent_expenditure_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for record in records:
        committee_type = first_text(record, "committee.committee_type_full", "committee_type_full", default="")
        source = first_text(record, "committee.name", "spender_name", "filer_name_text", "payee_name", default="Unknown outside spender")
        candidate = first_text(record, "candidate_name", "candidate.name", default="Unknown candidate")
        amount = money_millions(first_text(record, "expenditure_amount", "amount", default="0"))
        purpose = first_text(record, "expenditure_description", "category_code_full", default="independent expenditure")
        flow_type = infer_independent_expenditure_flow_type(source, committee_type, purpose)
        traceability = traceability_for_outside_spending(flow_type, committee_type)
        rows.append(
            {
                "source": source,
                "recipient": candidate,
                "issueDomain": classify_domain(" ".join([source, candidate, committee_type, purpose, "election democracy"])),
                "amount": amount,
                "flowType": flow_type,
                "traceability": traceability,
                "largeDonorShare": 0.86 if flow_type in {"SUPER_PAC", "DARK_MONEY"} else 0.68,
                "sourceRecordId": first_text(record, "transaction_id", "image_number", "file_number", default=""),
                "sourceUrl": fec_source_url(first_text(record, "image_number", default="")),
                "committeeType": committee_type or "independent expenditure",
                "spendingPurpose": purpose,
                "supportOppose": first_text(record, "support_oppose_indicator", "support_oppose_indicator_full", default=""),
                "disclosureLag": fec_visibility_lag(record),
            }
        )
    return rows


def normalize_fec_electioneering_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for record in records:
        source = first_text(record, "committee_name", "committee.name", "filer_name_text", default="Unknown electioneering filer")
        candidate = first_text(record, "candidate_name", "candidate.name", default="Unknown candidate")
        purpose = first_text(record, "purpose_description", "disbursement_description", default="electioneering communication")
        amount = money_millions(first_text(record, "disbursement_amount", "calculated_candidate_share", "amount", default="0"))
        rows.append(
            {
                "source": source,
                "recipient": candidate,
                "issueDomain": classify_domain(" ".join([source, candidate, purpose, "election democracy"])),
                "amount": amount,
                "flowType": "ELECTIONEERING",
                "traceability": 0.50,
                "largeDonorShare": 0.74,
                "sourceRecordId": first_text(record, "sub_id", "link_id", "file_number", "sb_image_num", default=""),
                "sourceUrl": first_text(record, "pdf_url", default=fec_source_url(first_text(record, "sb_image_num", "beginning_image_number", default=""))),
                "committeeType": "electioneering communication",
                "spendingPurpose": purpose,
                "supportOppose": first_text(record, "election_type", default=""),
                "disclosureLag": fec_visibility_lag(record),
            }
        )
    return rows


def normalize_fec_communication_cost_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for record in records:
        source = first_text(record, "committee_name", "committee.name", default="Unknown communication spender")
        candidate = first_text(record, "candidate_name", default="Unknown candidate")
        purpose = first_text(record, "purpose", "communication_type_full", "schedule_type_full", default="communication cost")
        amount = money_millions(first_text(record, "transaction_amount", "amount", default="0"))
        rows.append(
            {
                "source": source,
                "recipient": candidate,
                "issueDomain": classify_domain(" ".join([source, candidate, purpose, "election democracy"])),
                "amount": amount,
                "flowType": "COMMUNICATION_COST",
                "traceability": 0.64,
                "largeDonorShare": 0.66,
                "sourceRecordId": first_text(record, "tran_id", "transaction_id", "sub_id", "image_number", default=""),
                "sourceUrl": first_text(record, "pdf_url", default=fec_source_url(first_text(record, "image_number", default=""))),
                "committeeType": first_text(record, "schedule_type_full", "communication_type_full", default="communication cost"),
                "spendingPurpose": purpose,
                "supportOppose": first_text(record, "support_oppose_indicator", "support_oppose_indicator_full", default=""),
                "disclosureLag": fec_visibility_lag(record),
            }
        )
    return rows


def fetch_revolving_door(output: Path) -> int:
    base = os.environ.get("LDA_API_BASE", "https://lda.gov/api/v1").rstrip("/")
    params = {
        "page_size": os.environ.get("REVOLVING_DOOR_LDA_PAGE_SIZE", os.environ.get("LDA_PAGE_SIZE", "50")),
    }
    if os.environ.get("LDA_YEAR"):
        params["filing_year"] = os.environ["LDA_YEAR"]
    if os.environ.get("LDA_PERIOD"):
        params["filing_period"] = os.environ["LDA_PERIOD"]
    headers = {}
    if os.environ.get("LDA_API_KEY"):
        headers["Authorization"] = f"Token {os.environ['LDA_API_KEY']}"

    records = []
    next_url = f"{base}/filings/?{urlencode(params)}"
    max_pages = int_env("REVOLVING_DOOR_LDA_MAX_PAGES", 25, 1, 50)
    for _ in range(max_pages):
        payload = get_json(next_url, headers)
        records.extend(payload.get("results", payload if isinstance(payload, list) else []))
        next_url = payload.get("next") if isinstance(payload, dict) else None
        if not next_url:
            break

    records = [record for record in records if record_matches_lda_filters(record)]
    rows = normalize_revolving_door_from_lda(records)
    write_rows(
        output,
        [
            "person",
            "organization",
            "sector",
            "agency",
            "formerOfficialRole",
            "coolingOffMonths",
            "sourceType",
            "influenceShare",
            "sourceRecordId",
            "sourceUrl",
            "positionType",
            "confidence",
        ],
        rows,
        "LDA covered-position lobbyist rows",
    )
    return 0


def normalize_revolving_door_from_lda(records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        registrant = first_text(record, "registrant.name", "registrant_name", "registrant", default="Unknown registrant")
        filing_id = first_text(record, "id", "filing_uuid", default="")
        filing_url = first_text(record, "filing_url", "url", default="")
        amount = money_millions(first_text(record, "income", "expenses", "amount", default="0"))
        issue_domain = issue_domains_from_lda(record)[0]
        for lobbyist in lobbyists_from_lda(record):
            role = first_text(lobbyist, "covered_position", "covered_position_display", "official_position", default="")
            if not role:
                continue
            person = lobbyist_name(lobbyist)
            key = (filing_id, person, role)
            if key in seen:
                continue
            seen.add(key)
            agency = agency_from_role(role)
            rows.append(
                {
                    "person": person,
                    "organization": registrant,
                    "sector": issue_domain,
                    "agency": agency,
                    "formerOfficialRole": role,
                    "coolingOffMonths": first_text(lobbyist, "cooling_off_months", default="12"),
                    "sourceType": "lda-covered-position",
                    "influenceShare": ValuesProxy.clamp(0.34 + (amount * 0.04), 0.20, 0.82),
                    "sourceRecordId": filing_id,
                    "sourceUrl": filing_url,
                    "positionType": "covered-position-lobbyist",
                    "confidence": 0.74 if person != "Unknown lobbyist" else 0.56,
                }
            )
    return rows


def lobbyists_from_lda(record: dict[str, object]) -> list[dict[str, object]]:
    collected: list[dict[str, object]] = []
    lobbyists = record.get("lobbyists") or record.get("lobbyist_conviction_disclosures") or []
    if isinstance(lobbyists, dict):
        collected.append(lobbyists)
    elif isinstance(lobbyists, list):
        collected.extend(item for item in lobbyists if isinstance(item, dict))
    activities = record.get("lobbying_activities") or []
    if isinstance(activities, dict):
        activities = [activities]
    if isinstance(activities, list):
        for activity in activities:
            if not isinstance(activity, dict):
                continue
            activity_lobbyists = activity.get("lobbyists") or []
            if isinstance(activity_lobbyists, dict):
                activity_lobbyists = [activity_lobbyists]
            collected.extend(item for item in activity_lobbyists if isinstance(item, dict))
    return collected


def lobbyist_name(lobbyist: dict[str, object]) -> str:
    name = first_text(lobbyist, "name", "lobbyist.name", default="")
    if name:
        return name
    first = first_text(lobbyist, "first_name", "lobbyist.first_name", default="")
    last = first_text(lobbyist, "last_name", "lobbyist.last_name", default="")
    combined = " ".join(part for part in [first, last] if part).strip()
    return combined or "Unknown lobbyist"


def agency_from_role(role: str) -> str:
    normalized = role.lower()
    if "epa" in normalized or "environment" in normalized:
        return "Environmental Protection Agency"
    if "sec" in normalized or "securities" in normalized:
        return "Securities and Exchange Commission"
    if "ftc" in normalized or "federal trade" in normalized:
        return "Federal Trade Commission"
    if "defense" in normalized or "dod" in normalized:
        return "Department of Defense"
    if "congress" in normalized or "house" in normalized or "senate" in normalized:
        return "Congress"
    return "covered federal office"


class ValuesProxy:
    @staticmethod
    def clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))


def fetch_regulatory(output: Path) -> int:
    source = os.environ.get("REGULATORY_SOURCE", "regulations").lower()
    if source == "federal-register":
        rows = fetch_federal_register_rows()
        source_name = "Federal Register documents"
    else:
        rows = fetch_regulations_gov_rows()
        source_name = "Regulations.gov documents"
    write_rows(
        output,
        [
            "docketId",
            "issueDomain",
            "agency",
            "commentVolume",
            "genuineShare",
            "templateShare",
            "technicalClaimCredibility",
            "authenticationShare",
        ],
        rows,
        source_name,
    )
    return 0


OIRA_MEETING_FIELDS = [
    "meetingId",
    "rin",
    "agency",
    "subagency",
    "ruleTitle",
    "stage",
    "meetingStatus",
    "meetingDate",
    "meetingTime",
    "meetingDateTime",
    "requestorOrganization",
    "requestorName",
    "requestorClient",
    "sourceUrl",
    "detailFetched",
    "participantDisclosure",
    "clientDisclosure",
    "sourceSystem",
    "notes",
]


def fetch_oira_meetings(output: Path) -> int:
    base = os.environ.get("REGINFO_BASE_URL", "https://www.reginfo.gov").rstrip("/")
    url = os.environ.get(
        "REGINFO_EO_MEETINGS_URL",
        f"{base}/public/do/eom12866SearchResults?pubId=&rin=&viewRule=true",
    )
    source_html = read_env_text_file("REGINFO_EO_MEETINGS_SOURCE_HTML")
    html_text = source_html if source_html else get_text(url)
    max_rows = int_env("REGINFO_EO_MEETINGS_MAX_ROWS", 100, 1, 5000)
    rows = parse_oira_meeting_results(html_text, base, max_rows)
    if os.environ.get("REGINFO_EO_MEETINGS_FETCH_DETAILS", "1") != "0":
        detail_limit = int_env("REGINFO_EO_MEETINGS_DETAIL_LIMIT", 25, 0, max_rows)
        detail_fixture = read_env_text_file("REGINFO_EO_MEETINGS_DETAIL_HTML")
        for index, row in enumerate(rows):
            if index >= detail_limit:
                break
            row.update(oira_detail_defaults(f"detail fetch skipped after limit={detail_limit}"))
            try:
                detail_html = detail_fixture if detail_fixture else get_text(str(row["sourceUrl"]))
                row.update(parse_oira_meeting_detail(detail_html))
                row["detailFetched"] = True
                row["notes"] = "public Reginfo.gov EO 12866 meeting disclosure"
            except SystemExit as error:
                row.update(oira_detail_defaults(f"detail fetch failed: {str(error)[:160]}"))
    write_rows(output, OIRA_MEETING_FIELDS, rows, "Reginfo.gov EO 12866 meetings")
    return 0


class TableRowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[dict[str, str]]] = []
        self.in_row = False
        self.in_cell = False
        self.current_cells: list[dict[str, str]] = []
        self.current_text: list[str] = []
        self.current_href = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "tr":
            self.in_row = True
            self.current_cells = []
        elif self.in_row and tag.lower() == "td":
            self.in_cell = True
            self.current_text = []
            self.current_href = ""
        elif self.in_cell and tag.lower() == "a":
            attrs_dict = {key.lower(): value or "" for key, value in attrs}
            href = attrs_dict.get("href", "")
            if "viewEO12866Meeting" in href:
                self.current_href = href

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "td" and self.in_cell:
            self.current_cells.append(
                {
                    "text": normalize_html_space(" ".join(self.current_text)),
                    "href": self.current_href,
                }
            )
            self.in_cell = False
            self.current_text = []
            self.current_href = ""
        elif lowered == "tr" and self.in_row:
            if self.current_cells:
                self.rows.append(self.current_cells)
            self.in_row = False


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return normalize_html_space(" ".join(self.parts))


def parse_oira_meeting_results(html_text: str, base_url: str, max_rows: int) -> list[dict[str, object]]:
    parser = TableRowParser()
    parser.feed(html_text)
    rows: list[dict[str, object]] = []
    for cells in parser.rows:
        if len(cells) < 5 or "viewEO12866Meeting" not in cells[0].get("href", ""):
            continue
        source_url = urljoin(base_url + "/", cells[0]["href"])
        query = dict(parse_qsl(urlsplit(source_url).query, keep_blank_values=True))
        meeting_date, meeting_time = parse_oira_meeting_datetime(cells[0]["text"])
        agency, subagency = split_agency_subagency(cells[1]["text"] or query.get("acronym", ""))
        rows.append(
            {
                "meetingId": query.get("meetingId", ""),
                "rin": query.get("rin", ""),
                "agency": agency,
                "subagency": subagency,
                "ruleTitle": cells[2]["text"],
                "stage": cells[3]["text"],
                "meetingStatus": cells[4]["text"],
                "meetingDate": meeting_date,
                "meetingTime": meeting_time,
                "meetingDateTime": cells[0]["text"],
                "requestorOrganization": "",
                "requestorName": "",
                "requestorClient": "",
                "sourceUrl": source_url,
                "detailFetched": False,
                "participantDisclosure": False,
                "clientDisclosure": False,
                "sourceSystem": "reginfo-eo12866-meetings",
                "notes": "results-list row only; detail not fetched",
            }
        )
        if len(rows) >= max_rows:
            break
    return rows


def parse_oira_meeting_detail(html_text: str) -> dict[str, object]:
    parser = TextParser()
    parser.feed(html_text)
    text = parser.text()
    stop_labels = oira_detail_stop_labels()
    title = labeled_text(text, "Title:", ["Agency/Subagency:", "Stage of Rulemaking:", "Meeting Date/Time:", "Requestor:", *stop_labels])
    agency_text = labeled_text(text, "Agency/Subagency:", ["Stage of Rulemaking:", "Meeting Date/Time:", "Requestor:", *stop_labels])
    stage = labeled_text(text, "Stage of Rulemaking:", ["Meeting Date/Time:", "Requestor:", *stop_labels])
    meeting_datetime = labeled_text(text, "Meeting Date/Time:", ["Requestor:", "Requestor's Name:", "Requestor's Client:", *stop_labels])
    requestor = labeled_text(text, "Requestor:", ["Requestor's Name:", "Requestor's Client:", *stop_labels])
    requestor_name = labeled_text(text, "Requestor's Name:", ["Requestor's Client:", *stop_labels])
    requestor_client = labeled_text(text, "Requestor's Client:", stop_labels)
    meeting_date, meeting_time = parse_oira_meeting_datetime(meeting_datetime)
    agency, subagency = split_agency_subagency(agency_text)
    output: dict[str, object] = {
        "requestorOrganization": requestor,
        "requestorName": requestor_name,
        "requestorClient": requestor_client,
        "participantDisclosure": bool(requestor or requestor_name or requestor_client),
        "clientDisclosure": bool(requestor_client),
    }
    if title:
        output["ruleTitle"] = title
    if agency:
        output["agency"] = agency
    if subagency:
        output["subagency"] = subagency
    if stage:
        output["stage"] = stage
    if meeting_datetime:
        output["meetingDateTime"] = meeting_datetime
        output["meetingDate"] = meeting_date
        output["meetingTime"] = meeting_time
    return output


def oira_detail_defaults(notes: str) -> dict[str, object]:
    return {
        "detailFetched": False,
        "participantDisclosure": False,
        "clientDisclosure": False,
        "notes": notes,
    }


def read_env_text_file(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        return ""
    return Path(value).read_text(encoding="utf-8")


def normalize_html_space(value: str) -> str:
    return " ".join(html.unescape(value).split())


def labeled_text(text: str, label: str, next_labels: list[str]) -> str:
    start = text.find(label)
    if start < 0:
        return ""
    start += len(label)
    end_candidates = [text.find(next_label, start) for next_label in next_labels]
    end_candidates = [index for index in end_candidates if index >= 0]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start:end].strip()


def oira_detail_stop_labels() -> list[str]:
    return [
        "function downloadFileOrShowMessage",
        "Something went wrong when downloading this file.",
        "Reginfo.gov An official website",
        "An official website of the U.S. General Services Administration",
        "About Us About GSA",
    ]


def parse_oira_meeting_datetime(value: str) -> tuple[str, str]:
    text = value.strip()
    for fmt in ("%m/%d/%Y %I:%M %p", "%m/%d/%Y"):
        try:
            parsed = datetime.strptime(text, fmt)
            meeting_time = "" if fmt == "%m/%d/%Y" else parsed.strftime("%H:%M")
            return parsed.date().isoformat(), meeting_time
        except ValueError:
            continue
    return "", ""


def split_agency_subagency(value: str) -> tuple[str, str]:
    text = value.strip()
    if "/" not in text:
        return text, ""
    agency, subagency = text.split("/", 1)
    return agency.strip(), subagency.strip()


def fetch_usaspending(output: Path) -> int:
    base = os.environ.get("USASPENDING_API_BASE", "https://api.usaspending.gov/api/v2").rstrip("/")
    limit = int_env("USASPENDING_PAGE_SIZE", 100, 1, 100)
    max_pages = int_env("USASPENDING_MAX_PAGES", 2, 1, 20)
    start_date, end_date = usaspending_time_period()
    rows = []
    for agency_filter in usaspending_agency_filters():
        for page in range(1, max_pages + 1):
            payload = {
                "filters": usaspending_filters(start_date, end_date, agency_filter),
                "fields": [
                    "Award ID",
                    "Recipient Name",
                    "Recipient UEI",
                    "Award Amount",
                    "Awarding Agency",
                    "Awarding Sub Agency",
                    "Award Type",
                    "PIID",
                    "Action Date",
                    "Modification Number",
                    "Competition Type",
                    "Number of Offers",
                ],
                "page": page,
                "limit": limit,
                "sort": os.environ.get("USASPENDING_SORT", "Award Amount"),
                "order": os.environ.get("USASPENDING_ORDER", "desc"),
            }
            response = post_json(f"{base}/search/spending_by_award/", payload)
            page_rows = normalize_usaspending_records(base, response.get("results", []))
            rows.extend(page_rows)
            metadata = response.get("page_metadata", {})
            if not metadata.get("hasNext"):
                break
    write_rows(
        output,
        USASPENDING_FIELDS,
        rows,
        "USAspending awards",
    )
    return 0


def fetch_usaspending_actions(output: Path) -> int:
    if os.environ.get("USASPENDING_ACTION_AWARD_EXPANSION", "0") == "1":
        return fetch_usaspending_actions_by_award(output)

    base = os.environ.get("USASPENDING_API_BASE", "https://api.usaspending.gov/api/v2").rstrip("/")
    limit = int_env_any(
        ("USASPENDING_ACTION_TRANSACTION_PAGE_SIZE", "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_PAGE_SIZE"),
        int_env("USASPENDING_ACTION_AWARD_PAGE_SIZE", int_env("USASPENDING_PAGE_SIZE", 50, 1, 100), 1, 100),
        1,
        100,
    )
    max_pages = int_env_any(
        ("USASPENDING_ACTION_TRANSACTION_MAX_PAGES", "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_MAX_PAGES"),
        int_env("USASPENDING_ACTION_AWARD_MAX_PAGES", int_env("USASPENDING_MAX_PAGES", 1, 1, 20), 1, 20),
        1,
        20,
    )
    periods = usaspending_action_periods()
    sort_specs = usaspending_action_transaction_sort_specs()
    rows: list[dict[str, object]] = []
    seen_rows: set[tuple[object, ...]] = set()
    for agency_filter in usaspending_agency_filters(allow_procurement_actions_alias=True):
        for start_date, end_date in periods:
            for sort_field, sort_order in sort_specs:
                for page in range(1, max_pages + 1):
                    payload = {
                        "filters": usaspending_filters(start_date, end_date, agency_filter),
                        "fields": [
                            "Award ID",
                            "Action Date",
                            "Action Type",
                            "Mod",
                            "Transaction Amount",
                            "Recipient Name",
                            "Recipient UEI",
                            "Awarding Agency",
                            "Awarding Sub Agency",
                            "Award Type",
                            "generated_internal_id",
                        ],
                        "page": page,
                        "limit": limit,
                        "sort": sort_field,
                        "order": sort_order,
                    }
                    response = post_json(f"{base}/search/spending_by_transaction/", payload)
                    for row in normalize_usaspending_direct_transaction_records(response.get("results", [])):
                        row_key = usaspending_action_row_key(row)
                        if row_key in seen_rows:
                            continue
                        seen_rows.add(row_key)
                        rows.append(row)
                    metadata = response.get("page_metadata", {})
                    if not metadata.get("hasNext"):
                        break
    write_rows(
        output,
        USASPENDING_FIELDS,
        rows,
        "USAspending procurement action rows",
    )
    return 0


def fetch_usaspending_actions_by_award(output: Path) -> int:
    base = os.environ.get("USASPENDING_API_BASE", "https://api.usaspending.gov/api/v2").rstrip("/")
    limit = int_env_any(
        ("USASPENDING_ACTION_AWARD_PAGE_SIZE", "USASPENDING_PROCUREMENT_ACTIONS_AWARD_PAGE_SIZE"),
        int_env("USASPENDING_PAGE_SIZE", 50, 1, 100),
        1,
        100,
    )
    max_pages = int_env_any(
        ("USASPENDING_ACTION_AWARD_MAX_PAGES", "USASPENDING_PROCUREMENT_ACTIONS_AWARD_MAX_PAGES"),
        int_env("USASPENDING_MAX_PAGES", 1, 1, 20),
        1,
        20,
    )
    start_date, end_date = usaspending_time_period()
    rows: list[dict[str, object]] = []
    for agency_filter in usaspending_agency_filters(allow_procurement_actions_alias=True):
        for page in range(1, max_pages + 1):
            payload = {
                "filters": usaspending_filters(start_date, end_date, agency_filter),
                "fields": [
                    "Award ID",
                    "Recipient Name",
                    "Recipient UEI",
                    "Award Amount",
                    "Awarding Agency",
                    "Awarding Sub Agency",
                    "Award Type",
                    "PIID",
                    "Action Date",
                    "Modification Number",
                    "Competition Type",
                    "Number of Offers",
                ],
                "page": page,
                "limit": limit,
                "sort": os.environ.get("USASPENDING_ACTION_AWARD_SORT", os.environ.get("USASPENDING_SORT", "Award Amount")),
                "order": os.environ.get("USASPENDING_ACTION_AWARD_ORDER", os.environ.get("USASPENDING_ORDER", "desc")),
            }
            response = post_json(f"{base}/search/spending_by_award/", payload)
            for record in response.get("results", []):
                if not isinstance(record, dict):
                    continue
                detail = usaspending_award_detail(base, record)
                piid = first_text(detail, "piid", default=first_text(record, "PIID", "piid", "Award ID", "award_id", default=""))
                transactions = usaspending_transaction_records(base, piid)
                rows.extend(normalize_usaspending_transaction_records(record, detail, transactions))
            metadata = response.get("page_metadata", {})
            if not metadata.get("hasNext"):
                break
    write_rows(
        output,
        USASPENDING_FIELDS,
        rows,
        "USAspending procurement action rows",
    )
    return 0


def fetch_sam_contract_awards(output: Path) -> int:
    api_key = os.environ.get("SAM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set SAM_API_KEY before running the SAM.gov Contract Awards source-native fetcher.")
    base = os.environ.get("SAM_API_BASE", "https://api.sam.gov").rstrip("/")
    if sam_contract_awards_extract_mode():
        return fetch_sam_contract_awards_extract(output, base, api_key)
    limit = int_env("SAM_CONTRACT_AWARDS_PAGE_SIZE", 100, 1, 100)
    max_pages = int_env("SAM_CONTRACT_AWARDS_MAX_PAGES", 1, 1, 20)
    offsets = sam_contract_awards_offsets(max_pages, limit)
    base_params = sam_contract_awards_base_params(api_key, limit)
    rows: list[dict[str, object]] = []
    seen_rows: set[tuple[object, ...]] = set()
    for filter_key, filter_value in sam_contract_awards_filters():
        total_records = 0
        for offset in offsets:
            if total_records > 0 and offset * limit >= total_records:
                break
            params = dict(base_params)
            params[filter_key] = filter_value
            params["offset"] = str(offset)
            payload = get_json(f"{base}/contract-awards/v1/search?{urlencode(params)}")
            page_records = sam_contract_award_records(payload)
            for row in normalize_sam_contract_award_records(page_records):
                row_key = usaspending_action_row_key(row)
                if row_key in seen_rows:
                    continue
                seen_rows.add(row_key)
                rows.append(row)
            total_records = sam_contract_awards_total_records(payload)
            if not page_records and total_records <= 0:
                break
    write_rows(
        output,
        USASPENDING_FIELDS,
        rows,
        "SAM.gov Contract Awards",
    )
    return 0


def fetch_sam_contract_awards_export(input_path: Path | None, output: Path, url: str = "") -> int:
    if input_path is None:
        if not url:
            raise SystemExit("Set SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL or pass --input/--url.")
        with tempfile.TemporaryDirectory(prefix="lobby-sam-export-") as tmp:
            downloaded = Path(tmp) / "sam-contract-awards-export"
            download_sam_contract_awards_export_url(url, downloaded)
            return fetch_sam_contract_awards_export(downloaded, output)
    records = sam_contract_awards_records_from_export_file(input_path)
    rows = dedupe_usaspending_action_rows(normalize_sam_contract_award_records(records))
    write_rows(
        output,
        USASPENDING_FIELDS,
        rows,
        "SAM.gov Contract Awards export",
    )
    return 0


def fetch_sam_contract_awards_extract(output: Path, base: str, api_key: str) -> int:
    extract_format = sam_contract_awards_extract_format()
    base_params = sam_contract_awards_extract_params(api_key, extract_format)
    rows: list[dict[str, object]] = []
    seen_rows: set[tuple[object, ...]] = set()
    for filter_key, filter_value in sam_contract_awards_filters():
        params = dict(base_params)
        params[filter_key] = filter_value
        token_payload = get_json(f"{base}/contract-awards/v1/search?{urlencode(params)}")
        for row in normalize_sam_contract_award_records(
            sam_contract_awards_extract_records(token_payload, api_key, extract_format)
        ):
            row_key = usaspending_action_row_key(row)
            if row_key in seen_rows:
                continue
            seen_rows.add(row_key)
            rows.append(row)
    write_rows(
        output,
        USASPENDING_FIELDS,
        rows,
        "SAM.gov Contract Awards extract",
    )
    return 0


def sam_contract_awards_extract_mode() -> bool:
    mode = os.environ.get("SAM_CONTRACT_AWARDS_EXTRACT_MODE", "").strip().lower()
    if mode in {"1", "true", "yes", "y"}:
        return True
    if mode in {"0", "false", "no", "n"}:
        return False
    return bool(os.environ.get("SAM_CONTRACT_AWARDS_EXTRACT_FORMAT", os.environ.get("SAM_CONTRACT_AWARDS_FORMAT", "")).strip())


def sam_contract_awards_extract_format() -> str:
    value = os.environ.get("SAM_CONTRACT_AWARDS_EXTRACT_FORMAT", os.environ.get("SAM_CONTRACT_AWARDS_FORMAT", "json")).strip().lower()
    if value not in {"json", "csv"}:
        raise SystemExit(f"SAM_CONTRACT_AWARDS_EXTRACT_FORMAT must be json or csv, got: {value}")
    return value


def sam_contract_awards_extract_params(api_key: str, extract_format: str) -> dict[str, str]:
    params = sam_contract_awards_base_params(api_key, int_env("SAM_CONTRACT_AWARDS_PAGE_SIZE", 100, 1, 100))
    params.pop("limit", None)
    params["format"] = extract_format
    params["emailId"] = os.environ.get("SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID", "Yes").strip() or "Yes"
    return params


def sam_contract_awards_extract_records(
        token_payload: dict[str, object] | list[object],
        api_key: str,
        extract_format: str,
) -> list[dict[str, object]]:
    direct_records = sam_contract_award_records(token_payload)
    if direct_records:
        return direct_records
    if not isinstance(token_payload, dict):
        return []
    download_url = sam_contract_awards_download_url(token_payload, api_key)
    if not download_url:
        return []
    attempts = int_env("SAM_CONTRACT_AWARDS_EXTRACT_POLL_ATTEMPTS", 8, 1, 40)
    wait_seconds = float_env("SAM_CONTRACT_AWARDS_EXTRACT_POLL_SECONDS", 10.0, 0.0, 300.0)
    last_message = first_text(token_payload, "message", default="extract not ready")
    for attempt in range(1, attempts + 1):
        records, message = sam_contract_awards_download_records_or_message(download_url)
        if records:
            return records
        if message:
            last_message = message
        if attempt < attempts:
            time.sleep(wait_seconds)
    raise SystemExit(
        f"SAM.gov Contract Awards extract did not become ready after {attempts} poll attempts: {last_message}"
    )


def sam_contract_awards_download_url(token_payload: dict[str, object], api_key: str) -> str:
    url = first_text(token_payload, "presignedUrl", "downloadUrl", "url", default="")
    if not url:
        token = first_text(token_payload, "exportToken", "token", default="")
        if not token:
            return ""
        base = os.environ.get("SAM_API_BASE", "https://api.sam.gov").rstrip("/")
        url = f"{base}/contract-awards/v1/download?api_key=REPLACE_WITH_API_KEY&token={quote_plus(token)}"
    return sam_contract_awards_resolved_download_url(url, api_key)


def sam_contract_awards_resolved_download_url(raw_url: str, api_key: str | None = None) -> str:
    url = raw_url.strip()
    if not url:
        return ""
    needs_key = "REPLACE_WITH_API_KEY" in url
    key = api_key if api_key is not None else os.environ.get("SAM_API_KEY", "").strip()
    if needs_key:
        if not key:
            raise SystemExit(
                "SAM.gov Contract Awards download URL contains REPLACE_WITH_API_KEY; "
                "set SAM_API_KEY in .env or pass a local export file instead."
            )
        url = url.replace("REPLACE_WITH_API_KEY", quote_plus(key))
    return url


def sam_contract_awards_download_records_or_message(download_url: str) -> tuple[list[dict[str, object]], str]:
    with tempfile.TemporaryDirectory(prefix="lobby-sam-extract-") as tmp:
        target = Path(tmp) / "sam-contract-awards-extract"
        download_sam_contract_awards_export_url(download_url, target)
        data = target.read_bytes()
        if not data:
            return [], ""
        try:
            return sam_contract_awards_records_from_export_file(target), ""
        except SystemExit as error:
            text = data.decode("utf-8", errors="replace")
            return [], sam_contract_awards_extract_message(text) or str(error)


def download_sam_contract_awards_export_url(raw_url: str, target: Path) -> Path:
    url = sam_contract_awards_resolved_download_url(raw_url)
    if not url:
        raise SystemExit("SAM.gov Contract Awards export URL is empty.")
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "lobby-capture-simulator/0.1"}
    timeout = float_env("SOURCE_FETCH_TIMEOUT_SECONDS", 60.0, 1.0, 300.0)
    hard_timeout = float_env("SOURCE_FETCH_HARD_TIMEOUT_SECONDS", min(timeout + 5.0, 305.0), 1.0, 600.0)
    if shutil.which("curl") is not None:
        try:
            return download_url_to_file_with_curl(url, headers, target, timeout, hard_timeout)
        except SourceHttpStatus as error:
            detail = error.detail[:500]
            hint = auth_hint(error.code)
            raise SystemExit(f"GET {redact_url(url)} failed with HTTP {error.code}: {detail}{hint}") from error
        except (subprocess.TimeoutExpired, TimeoutError, OSError) as error:
            reason = getattr(error, "reason", str(error))
            raise SystemExit(f"GET {redact_url(url)} failed: {reason}") from error
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            target.write_bytes(response.read())
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        hint = auth_hint(error.code)
        raise SystemExit(f"GET {redact_url(url)} failed with HTTP {error.code}: {detail}{hint}") from error
    except (URLError, RemoteDisconnected, TimeoutError, ConnectionError, OSError) as error:
        reason = getattr(error, "reason", str(error))
        raise SystemExit(f"GET {redact_url(url)} failed: {reason}") from error
    return target


def download_url_to_file_with_curl(
        url: str,
        headers: dict[str, str],
        target: Path,
        timeout: float,
        hard_timeout: float,
) -> Path:
    command = [
        "curl",
        "-sS",
        "-L",
        "--compressed",
        "--connect-timeout",
        f"{min(timeout, hard_timeout):.1f}",
        "--max-time",
        f"{hard_timeout:.1f}",
        "-o",
        str(target),
        "-w",
        "%{http_code}",
    ]
    for key, value in headers.items():
        command.extend(["-H", f"{key}: {value}"])
    command.append(url)
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=hard_timeout + 2.0,
    )
    status_text = completed.stdout.strip() or "000"
    try:
        status_code = int(status_text[-3:])
    except ValueError:
        status_code = 0
    if completed.returncode != 0:
        detail = completed.stderr.strip().replace(url, redact_url(url))[:500]
        raise OSError(f"curl download failed with exit {completed.returncode}: {detail}")
    if status_code >= 400:
        detail = target.read_bytes().decode("utf-8", errors="replace")[:500] if target.exists() else ""
        raise SourceHttpStatus(status_code, detail, {})
    if status_code == 0:
        raise OSError("curl download did not report an HTTP status")
    return target


def sam_contract_awards_records_from_csv_or_message(text: str) -> list[dict[str, object]]:
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("{") or stripped.startswith("["):
        payload = json.loads(stripped)
        return sam_contract_award_records(payload)
    return [
        sam_contract_awards_csv_record_aliases(row)
        for row in csv.DictReader(StringIO(text))
        if any(str(value).strip() for value in row.values())
    ]


def sam_contract_awards_records_from_export_file(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"SAM.gov Contract Awards export does not exist: {path}")
    data = path.read_bytes()
    if path.suffix.lower() == ".zip" or data.startswith(b"PK\x03\x04"):
        records = sam_contract_awards_records_from_zip(path)
    else:
        if path.suffix.lower() == ".gz" or data.startswith(b"\x1f\x8b"):
            data = gzip.decompress(data)
        records = sam_contract_awards_records_from_csv_or_message(data.decode("utf-8", errors="replace"))
    if not records:
        raise SystemExit(f"SAM.gov Contract Awards export contained no award records: {path}")
    return records


def sam_contract_awards_records_from_zip(path: Path) -> list[dict[str, object]]:
    with zipfile.ZipFile(BytesIO(path.read_bytes())) as archive:
        candidate_names = [
            name for name in archive.namelist()
            if not name.endswith("/") and Path(name).suffix.lower() in {".csv", ".json", ".txt"}
        ]
        for name in candidate_names:
            text = archive.read(name).decode("utf-8", errors="replace")
            records = sam_contract_awards_records_from_csv_or_message(text)
            if records:
                return records
    return []


def sam_contract_awards_csv_record_aliases(row: dict[str, object]) -> dict[str, object]:
    expanded = dict(row)
    normalized = {
        normalize_header_key(key): value
        for key, value in row.items()
        if key is not None
    }
    aliases = {
        "piid": ("contractidpiid", "contractawardid", "contractid", "piid"),
        "modificationNumber": ("modificationnumber", "modificationno", "modnumber", "mod"),
        "transactionNumber": ("transactionnumber", "transactionno"),
        "awardId": ("awardid", "generatedinternalid", "contractawarduniqueid"),
        "awardeeLegalBusinessName": (
            "awardeelegalbusinessname",
            "awardeename",
            "recipientname",
            "vendorname",
            "legalbusinessname",
        ),
        "contractingDepartmentName": (
            "contractingdepartmentname",
            "contractingdepartment",
            "departmentname",
            "awardingagency",
            "contractingagency",
            "agency",
        ),
        "contractingSubtierName": (
            "contractingsubtiername",
            "contractingsubtier",
            "contractingofficename",
            "awardingsubagency",
            "subagency",
        ),
        "awardOrIDVTypeName": (
            "awardoridvtype",
            "awardoridvtypename",
            "awardtype",
            "contractawardtype",
        ),
        "actionObligation": (
            "actionobligation",
            "federalactionobligation",
            "totalactionobligation",
            "dollarsobligated",
            "currenttotalvalueofaward",
            "baseandalloptionsvalue",
        ),
        "awardeeUEI": ("uniqueentityid", "awardeeuei", "recipientuei", "uei"),
        "dateSigned": ("datesigned", "actiondate", "awarddate", "approveddate", "lastmodifieddate"),
        "extentCompetedName": (
            "extentcompeted",
            "extentcompetedname",
            "competitiontype",
            "solicitationprocedures",
            "reasonnotcompeted",
        ),
        "numberOfOffersReceived": (
            "numberofoffersreceived",
            "idvnumberofoffersreceived",
            "numberofoffers",
            "offersreceived",
        ),
        "typeOfContractPricingName": (
            "typeofcontractpricing",
            "typeofcontractpricingname",
            "pricingtype",
        ),
    }
    for alias, keys in aliases.items():
        if alias in expanded and expanded[alias] not in (None, ""):
            continue
        for key in keys:
            value = normalized.get(key)
            if value not in (None, ""):
                expanded[alias] = value
                break
    return expanded


def normalize_header_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def dedupe_usaspending_action_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for row in rows:
        key = usaspending_action_row_key(row)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def sam_contract_awards_extract_message(text: str) -> str:
    stripped = text.strip()
    if not stripped or not stripped.startswith("{"):
        return ""
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    return first_text(payload, "message", "status", default="")


def sam_contract_awards_base_params(api_key: str, limit: int) -> dict[str, str]:
    params = {
        "api_key": api_key,
        "limit": str(limit),
        "includeSections": os.environ.get(
            "SAM_CONTRACT_AWARDS_INCLUDE_SECTIONS",
            "contractId,coreData,awardDetails,awardeeData",
        ),
    }
    fiscal_year = os.environ.get("SAM_CONTRACT_AWARDS_FISCAL_YEAR", os.environ.get("USASPENDING_FISCAL_YEAR", "2024")).strip()
    if fiscal_year:
        params["fiscalYear"] = fiscal_year
    date_signed = sam_contract_awards_range_param("SAM_CONTRACT_AWARDS_DATE")
    if date_signed:
        params["dateSigned"] = date_signed
    last_modified = sam_contract_awards_range_param("SAM_CONTRACT_AWARDS_LAST_MODIFIED")
    if last_modified:
        params["lastModifiedDate"] = last_modified
    for env_name, parameter_name in (
        ("SAM_CONTRACT_AWARDS_AWARD_OR_IDV", "awardOrIDV"),
        ("SAM_CONTRACT_AWARDS_AWARD_OR_IDV_TYPE", "awardOrIDVTypeName"),
        ("SAM_CONTRACT_AWARDS_PRODUCT_OR_SERVICE_TYPE", "productOrServiceType"),
        ("SAM_CONTRACT_AWARDS_EXTENT_COMPETED", "extentCompetedName"),
        ("SAM_CONTRACT_AWARDS_MIN_MAX_DOLLARS", "dollarsObligated"),
        ("SAM_CONTRACT_AWARDS_MODIFICATION_NUMBER", "modificationNumber"),
    ):
        value = os.environ.get(env_name, "").strip()
        if value:
            params[parameter_name] = value
    return params


def sam_contract_awards_offset(offset_start: int, page_index: int, limit: int) -> int:
    offset = offset_start + page_index
    if offset * limit > 400000:
        raise SystemExit(
            "SAM.gov Contract Awards rejects requests where offset * limit exceeds 400000; "
            f"got offset={offset}, limit={limit}."
        )
    return offset


def sam_contract_awards_offset_starts() -> list[int]:
    starts = split_csv_env("SAM_CONTRACT_AWARDS_OFFSET_STARTS", "")
    if not starts:
        return [int_env("SAM_CONTRACT_AWARDS_OFFSET_START", 0, 0, 400000)]
    parsed: list[int] = []
    for start in starts:
        try:
            offset = int(start)
        except ValueError as error:
            raise SystemExit(f"SAM_CONTRACT_AWARDS_OFFSET_STARTS contains a non-integer page index: {start}") from error
        if offset < 0 or offset > 400000:
            raise SystemExit(f"SAM_CONTRACT_AWARDS_OFFSET_STARTS page index out of range 0..400000: {start}")
        parsed.append(offset)
    return sorted(dict.fromkeys(parsed))


def sam_contract_awards_offsets(max_pages: int, limit: int) -> list[int]:
    offsets = [
        sam_contract_awards_offset(offset_start, page_index, limit)
        for offset_start in sam_contract_awards_offset_starts()
        for page_index in range(max_pages)
    ]
    return sorted(dict.fromkeys(offsets))


def sam_contract_awards_range_param(prefix: str) -> str:
    start = os.environ.get(f"{prefix}_FROM", "").strip()
    end = os.environ.get(f"{prefix}_TO", "").strip()
    if not start and not end:
        return ""
    return f"[{sam_contract_awards_date(start)},{sam_contract_awards_date(end)}]"


def sam_contract_awards_date(value: str) -> str:
    parsed = parse_date(value)
    if parsed is None:
        return value
    return parsed.strftime("%m/%d/%Y")


def sam_contract_awards_filters() -> list[tuple[str, str]]:
    piid_subtier_codes = split_csv_env("SAM_CONTRACT_AWARDS_PIID_SUBTIER_CODES", "")
    if piid_subtier_codes:
        return [("piidSubtierCode", code) for code in piid_subtier_codes]
    piid_subtier_names = split_csv_env("SAM_CONTRACT_AWARDS_PIID_SUBTIER_NAMES", "")
    if piid_subtier_names:
        return [("piidSubtierName", name) for name in piid_subtier_names]
    department_codes = split_csv_env("SAM_CONTRACT_AWARDS_DEPARTMENT_CODES", "")
    if department_codes:
        return [("contractingDepartmentCode", code) for code in department_codes]
    agency_names = split_csv_env(
        "SAM_CONTRACT_AWARDS_AGENCIES",
        os.environ.get(
            "USASPENDING_PROCUREMENT_ACTIONS_AGENCIES",
            os.environ.get("USASPENDING_AGENCIES", os.environ.get("USASPENDING_AGENCY", "Environmental Protection Agency")),
        ),
    )
    return [("contractingDepartmentName", agency) for agency in agency_names if agency]


def sam_contract_award_records(payload: dict[str, object] | list[object]) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("awardSummary", "results", "records", "data", "awards", "contracts"):
        value = payload.get(key)
        if isinstance(value, list):
            return [record for record in value if isinstance(record, dict)]
    return []


def sam_contract_awards_total_records(payload: dict[str, object] | list[object]) -> int:
    if not isinstance(payload, dict):
        return 0
    return int_or_zero(first_text(payload, "totalRecords", "total_records", "page_metadata.total", default="0"))


def normalize_sam_contract_award_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in records:
        piid = first_text(record, "contractId.piid", "piid", "PIID", "awardDetails.contractId.piid", "contractAwardId", "Contract Award ID", "Contract ID", default="UNKNOWN")
        modification_number = first_text(record, "contractId.modificationNumber", "modificationNumber", "modification_number", "Modification Number", "Modification No", "Mod Number", "Mod", "mod", default="0")
        transaction_number = first_text(record, "contractId.transactionNumber", "transactionNumber", "Transaction Number", default="")
        award_id = first_text(record, "awardId", "Award ID", "generated_internal_id", "contractAwardUniqueId", "Contract Award Unique ID", default=piid)
        if award_id == "UNKNOWN" and transaction_number:
            award_id = f"{piid}-{modification_number}-{transaction_number}"
        competition_type = sam_contract_awards_competition_type(record)
        pricing_type = first_text(
            record,
            "coreData.acquisitionData.typeOfContractPricing.name",
            "awardDetails.acquisitionData.typeOfContractPricing.name",
            "typeOfContractPricingName",
            "typeOfContractPricing",
            "Type Of Contract Pricing",
            "Type of Contract Pricing",
            default="",
        )
        number_of_offers = first_text(
            record,
            "awardDetails.competitionInformation.numberOfOffersReceived",
            "awardDetails.competitionInformation.idvNumberOfOffersReceived",
            "coreData.competitionInformation.numberOfOffersReceived",
            "coreData.competitionInformation.idvNumberOfOffersReceived",
            "numberOfOffersReceived",
            "Number Of Offers Received",
            "Number of Offers Received",
            "numberOfOffers",
            default="0",
        )
        competition_lower = competition_type.lower()
        rows.append(
            {
                "awardId": award_id,
                "recipient": first_text(
                    record,
                    "awardDetails.awardeeData.awardeeHeader.legalBusinessName",
                    "awardDetails.awardeeData.awardeeHeader.awardeeName",
                    "awardDetails.awardeeData.awardeeHeader.awardeeNameFromContract",
                    "awardeeData.awardeeHeader.legalBusinessName",
                    "awardeeData.awardeeHeader.awardeeName",
                    "awardeeLegalBusinessName",
                    "Awardee Legal Business Name",
                    "Awardee Name",
                    "recipientName",
                    "Recipient Name",
                    "Vendor Name",
                    "Legal Business Name",
                    "recipient",
                    default="Unknown recipient",
                ),
                "agency": first_text(
                    record,
                    "coreData.federalOrganization.contractingInformation.contractingDepartment.name",
                    "awardDetails.federalOrganization.contractingInformation.contractingDepartment.name",
                    "contractingDepartmentName",
                    "Contracting Department Name",
                    "Contracting Department",
                    "Department Name",
                    "Awarding Agency",
                    "Contracting Agency",
                    "Agency",
                    "contractId.subtier.name",
                    default="Unknown agency",
                ),
                "subAgency": first_text(
                    record,
                    "coreData.federalOrganization.contractingInformation.contractingSubtier.name",
                    "awardDetails.federalOrganization.contractingInformation.contractingSubtier.name",
                    "contractingSubtierName",
                    "Contracting Subtier Name",
                    "Contracting Subtier",
                    "Contracting Office Name",
                    "Awarding Sub Agency",
                    "Sub Agency",
                    "contractId.subtier.name",
                    default="Unknown agency",
                ),
                "awardType": first_text(record, "coreData.awardOrIDVType.name", "awardOrIDVTypeName", "Award or IDV Type", "Award Type", "Contract Award Type", "awardType", default="contract"),
                "amount": money_millions(first_text(
                    record,
                    "awardDetails.dollars.actionObligation",
                    "awardDetails.dollars.dollarsObligated",
                    "awardDetails.dollars.baseAndAllOptionsValue",
                    "awardDetails.dollars.currentTotalValueOfAward",
                    "awardDetails.totalContractDollars.totalActionObligation",
                    "dollarsObligated",
                    "actionObligation",
                    "Action Obligation",
                    "Federal Action Obligation",
                    "Total Action Obligation",
                    "Dollars Obligated",
                    "Current Total Value of Award",
                    "totalDollarsObligated",
                    default="0",
                )),
                "issueDomain": os.environ.get("SAM_CONTRACT_AWARDS_ISSUE_DOMAIN", os.environ.get("USASPENDING_ISSUE_DOMAIN", "procurement")),
                "awardCount": 1,
                "uei": first_text(
                    record,
                    "awardDetails.awardeeData.awardeeUEIInformation.uniqueEntityId",
                    "awardeeData.awardeeUEIInformation.uniqueEntityId",
                    "awardeeUEI",
                    "Unique Entity ID",
                    "Awardee UEI",
                    "Recipient UEI",
                    "uei",
                    "UEI",
                    default="",
                ),
                "piid": piid,
                "modificationNumber": modification_number,
                "actionDate": first_text(
                    record,
                    "awardDetails.transactionData.approvedDate",
                    "coreData.dateSigned",
                    "dateSigned",
                    "Date Signed",
                    "Award Date",
                    "Last Modified Date",
                    "approvedDate",
                    "Approved Date",
                    "actionDate",
                    default="",
                ),
                "competitionType": competition_type,
                "numberOfOffers": number_of_offers,
                "priceOnlyAward": str(price_only_procurement_flag(number_of_offers, pricing_type, competition_type)).lower(),
                "exPostModification": str(modification_sequence(modification_number) > 0).lower(),
                "protestFiled": "false",
                "exclusionFlag": str("exclusion" in competition_lower).lower(),
                "firewallCovered": str(os.environ.get("SAM_CONTRACT_AWARDS_FIREWALL_COVERED", os.environ.get("USASPENDING_FIREWALL_COVERED", "false")).lower() == "true").lower(),
            }
        )
    return rows


def sam_contract_awards_competition_type(record: dict[str, object]) -> str:
    return first_text(
        record,
        "awardDetails.competitionInformation.extentCompeted.name",
        "coreData.competitionInformation.extentCompeted.name",
        "awardDetails.competitionInformation.extentCompetedForReferencedIdv.name",
        "coreData.competitionInformation.extentCompetedForReferencedIdv.name",
        "extentCompetedName",
        "Extent Competed",
        "Extent Competed Name",
        "Competition Type",
        "Solicitation Procedures",
        "Reason Not Competed",
        default="unknown",
    )


def usaspending_filters(start_date: str, end_date: str, agency_filter: dict[str, str]) -> dict[str, object]:
    filters: dict[str, object] = {
        "time_period": [{"start_date": start_date, "end_date": end_date}],
        "award_type_codes": split_csv_env("USASPENDING_AWARD_TYPE_CODES", "A,B,C,D"),
    }
    if agency_filter:
        filters["agencies"] = [agency_filter]
    return filters


def usaspending_agency_filters(allow_procurement_actions_alias: bool = False) -> list[dict[str, str]]:
    agency_type = os.environ.get("USASPENDING_AGENCY_TYPE", "awarding")
    agency_tier = os.environ.get("USASPENDING_AGENCY_TIER", "toptier")
    agency_alias_default = (
        os.environ.get("USASPENDING_PROCUREMENT_ACTIONS_AGENCIES", "")
        if allow_procurement_actions_alias
        else ""
    )
    agencies = split_csv_env(
        "USASPENDING_AGENCIES",
        agency_alias_default,
    )
    if not agencies:
        agencies = [os.environ.get("USASPENDING_AGENCY", "Environmental Protection Agency")]
    if any(agency.strip().lower() in USASPENDING_ALL_AGENCIES for agency in agencies):
        return [{}]
    return [
        {
            "type": agency_type,
            "tier": agency_tier,
            "name": agency,
        }
        for agency in agencies
        if agency
    ]


def usaspending_time_period() -> tuple[str, str]:
    if os.environ.get("USASPENDING_DATE_FROM") and os.environ.get("USASPENDING_DATE_TO"):
        return os.environ["USASPENDING_DATE_FROM"], os.environ["USASPENDING_DATE_TO"]
    fiscal_year = int_env("USASPENDING_FISCAL_YEAR", 2024, 2008, 2100)
    return f"{fiscal_year - 1}-10-01", f"{fiscal_year}-09-30"


def usaspending_action_periods() -> list[tuple[str, str]]:
    start_text, end_text = usaspending_time_period()
    bucket = env_first(
        "USASPENDING_ACTION_PERIOD_BUCKETS",
        "USASPENDING_PROCUREMENT_ACTIONS_PERIOD_BUCKETS",
        default="",
    ).strip().lower()
    if bucket in {"", "year", "yearly", "annual", "full", "full-year"}:
        return [(start_text, end_text)]
    if bucket not in {"month", "monthly", "quarter", "quarterly"}:
        raise SystemExit(
            "USASPENDING_ACTION_PERIOD_BUCKETS must be one of annual, monthly, or quarterly."
        )
    start = parse_date(start_text)
    end = parse_date(end_text)
    if start is None or end is None:
        return [(start_text, end_text)]
    periods: list[tuple[str, str]] = []
    if bucket in {"quarter", "quarterly"}:
        first_quarter_month = ((start.month - 1) // 3) * 3 + 1
        cursor = date(start.year, first_quarter_month, 1)
        while cursor <= end:
            next_quarter_month = cursor.month + 3
            next_quarter_year = cursor.year
            if next_quarter_month > 12:
                next_quarter_month -= 12
                next_quarter_year += 1
            next_quarter = date(next_quarter_year, next_quarter_month, 1)
            period_start = max(cursor, start)
            period_end = min(date.fromordinal(next_quarter.toordinal() - 1), end)
            periods.append((period_start.isoformat(), period_end.isoformat()))
            cursor = next_quarter
        return periods
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        next_month = date(cursor.year + (1 if cursor.month == 12 else 0), 1 if cursor.month == 12 else cursor.month + 1, 1)
        period_start = max(cursor, start)
        period_end = min(date.fromordinal(next_month.toordinal() - 1), end)
        periods.append((period_start.isoformat(), period_end.isoformat()))
        cursor = next_month
    return periods


def usaspending_action_transaction_sort_specs() -> list[tuple[str, str]]:
    """Return transaction sort/order pairs for stratified action sampling."""
    default_order = env_first(
        "USASPENDING_ACTION_TRANSACTION_ORDER",
        "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_ORDER",
        default="desc",
    ).strip().lower()
    if default_order not in {"asc", "desc"}:
        default_order = "desc"
    raw_specs = env_first(
        "USASPENDING_ACTION_TRANSACTION_SORT_SPECS",
        "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_SORT_SPECS",
        default="",
    ).strip()
    if not raw_specs:
        return [
            (
                env_first(
                    "USASPENDING_ACTION_TRANSACTION_SORT",
                    "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_SORT",
                    default="Action Date",
                ),
                default_order,
            )
        ]
    specs: list[tuple[str, str]] = []
    for token in re.split(r"[;\n]+", raw_specs):
        token = token.strip()
        if not token:
            continue
        if ":" in token:
            sort_field, sort_order = token.rsplit(":", 1)
            sort_field = sort_field.strip()
            sort_order = sort_order.strip().lower()
        else:
            sort_field = token
            sort_order = default_order
        if not sort_field:
            continue
        if sort_order not in {"asc", "desc"}:
            sort_order = default_order
        specs.append((sort_field, sort_order))
    return specs or [(os.environ.get("USASPENDING_ACTION_TRANSACTION_SORT", "Action Date"), default_order)]


def usaspending_action_row_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row.get("awardId", ""),
        row.get("agency", ""),
        row.get("actionDate", ""),
        row.get("modificationNumber", ""),
        row.get("amount", ""),
        row.get("recipient", ""),
    )


USASPENDING_FIELDS = [
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
]


def normalize_usaspending_records(base: str, records: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    enrich_limit = int_env("USASPENDING_ENRICH_LIMIT", 100, 0, 500)
    for index, record in enumerate(records):
        detail = usaspending_award_detail(base, record) if index < enrich_limit else {}
        award_id = first_text(record, "Award ID", "award_id", "generated_internal_id", default="UNKNOWN")
        piid = first_text(detail, "piid", default=first_text(record, "PIID", "piid", default=award_id))
        recipient = first_text(record, "Recipient Name", "recipient_name", "recipient", default="Unknown recipient")
        agency = first_text(record, "Awarding Agency", "awarding_agency", default="Unknown agency")
        sub_agency = first_text(record, "Awarding Sub Agency", "awarding_sub_agency", default=agency)
        award_type = first_text(detail, "type_description", default=first_text(record, "Award Type", "award_type", default="contract"))
        transaction = usaspending_transaction_summary(base, piid) if index < enrich_limit else {}
        contract_data = detail.get("latest_transaction_contract_data") if isinstance(detail, dict) else {}
        contract_data = contract_data if isinstance(contract_data, dict) else {}
        record_modification_number = first_text(record, "Modification Number", "modification_number", default="0")
        latest_transaction_modification_number = first_text(transaction, "modificationNumber", default="")
        modification_number = record_modification_number
        if os.environ.get("USASPENDING_TREAT_LATEST_TRANSACTION_AS_MODIFICATION", "0") == "1" and modification_sequence(latest_transaction_modification_number) > 0:
            modification_number = latest_transaction_modification_number
        number_of_offers = first_text(contract_data, "number_of_offers_received", default=first_text(record, "Number of Offers", "number_of_offers_received", default="0"))
        competition_type = first_text(
            contract_data,
            "extent_competed_description",
            "extent_competed",
            "solicitation_procedures_description",
            default=first_text(record, "Competition Type", "extent_competed", default="unknown"),
        )
        pricing_type = first_text(contract_data, "type_of_contract_pricing_description", "type_of_contract_pricing", default="")
        modified = modification_sequence(modification_number) > 0
        exclusion_flag = "exclusion" in competition_type.lower()
        rows.append(
            {
                "awardId": award_id,
                "recipient": recipient,
                "agency": agency,
                "subAgency": sub_agency,
                "awardType": award_type or "contract",
                "amount": money_millions(first_text(record, "Award Amount", "award_amount", "amount", default="0")),
                "issueDomain": os.environ.get("USASPENDING_ISSUE_DOMAIN", "procurement"),
                "awardCount": 1,
                "uei": first_text(detail, "recipient.recipient_uei", default=first_text(record, "Recipient UEI", "recipient_uei", "UEI", default="")),
                "piid": piid,
                "modificationNumber": modification_number,
                "actionDate": first_text(detail, "date_signed", default=first_text(record, "Action Date", "action_date", default=first_text(transaction, "actionDate", default=""))),
                "competitionType": competition_type,
                "numberOfOffers": number_of_offers,
                "priceOnlyAward": str(price_only_procurement_flag(number_of_offers, pricing_type, competition_type)).lower(),
                "exPostModification": str(modified).lower(),
                "protestFiled": "false",
                "exclusionFlag": str(exclusion_flag).lower(),
                "firewallCovered": str(os.environ.get("USASPENDING_FIREWALL_COVERED", "false").lower() == "true").lower(),
            }
        )
    return rows


def normalize_usaspending_transaction_records(
        award_record: dict[str, object],
        detail: dict[str, object],
        transactions: list[dict[str, object]],
) -> list[dict[str, object]]:
    contract_data = detail.get("latest_transaction_contract_data") if isinstance(detail, dict) else {}
    contract_data = contract_data if isinstance(contract_data, dict) else {}
    award_id = first_text(award_record, "Award ID", "award_id", "generated_internal_id", default="UNKNOWN")
    piid = first_text(detail, "piid", default=first_text(award_record, "PIID", "piid", default=award_id))
    recipient = first_text(award_record, "Recipient Name", "recipient_name", "recipient", default="Unknown recipient")
    agency = first_text(award_record, "Awarding Agency", "awarding_agency", default="Unknown agency")
    sub_agency = first_text(award_record, "Awarding Sub Agency", "awarding_sub_agency", default=agency)
    award_type = first_text(detail, "type_description", default=first_text(award_record, "Award Type", "award_type", default="contract"))
    number_of_offers = first_text(contract_data, "number_of_offers_received", default=first_text(award_record, "Number of Offers", "number_of_offers_received", default="0"))
    competition_type = first_text(
        contract_data,
        "extent_competed_description",
        "extent_competed",
        "solicitation_procedures_description",
        default=first_text(award_record, "Competition Type", "extent_competed", default="unknown"),
    )
    pricing_type = first_text(contract_data, "type_of_contract_pricing_description", "type_of_contract_pricing", default="")
    exclusion_flag = "exclusion" in competition_type.lower()
    rows: list[dict[str, object]] = []
    for transaction in transactions:
        modification_number = first_text(transaction, "Mod", "mod", "Modification Number", "modification_number", default="0")
        transaction_amount = first_text(transaction, "Transaction Amount", "transaction_amount", "Award Amount", "award_amount", default=first_text(award_record, "Award Amount", "award_amount", default="0"))
        action_date = first_text(transaction, "Action Date", "action_date", default=first_text(award_record, "Action Date", "action_date", default=""))
        rows.append(
            {
                "awardId": first_text(transaction, "Award ID", "award_id", default=award_id),
                "recipient": first_text(transaction, "Recipient Name", "recipient_name", default=recipient),
                "agency": first_text(transaction, "Awarding Agency", "awarding_agency", default=agency),
                "subAgency": first_text(transaction, "Awarding Sub Agency", "awarding_sub_agency", default=sub_agency),
                "awardType": first_text(transaction, "Award Type", "award_type", default=award_type or "contract"),
                "amount": money_millions(transaction_amount),
                "issueDomain": os.environ.get("USASPENDING_ISSUE_DOMAIN", "procurement"),
                "awardCount": 1,
                "uei": first_text(detail, "recipient.recipient_uei", default=first_text(transaction, "Recipient UEI", "recipient_uei", default=first_text(award_record, "Recipient UEI", "recipient_uei", "UEI", default=""))),
                "piid": first_text(transaction, "PIID", "piid", default=piid),
                "modificationNumber": modification_number,
                "actionDate": action_date,
                "competitionType": competition_type,
                "numberOfOffers": number_of_offers,
                "priceOnlyAward": str(price_only_procurement_flag(number_of_offers, pricing_type, competition_type)).lower(),
                "exPostModification": str(modification_sequence(modification_number) > 0).lower(),
                "protestFiled": "false",
                "exclusionFlag": str(exclusion_flag).lower(),
                "firewallCovered": str(os.environ.get("USASPENDING_FIREWALL_COVERED", "false").lower() == "true").lower(),
            }
        )
    return rows


def normalize_usaspending_direct_transaction_records(transactions: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue
        award_id = first_text(transaction, "Award ID", "generated_internal_id", default="UNKNOWN")
        modification_number = first_text(transaction, "Mod", "mod", "Modification Number", "modification_number", default="0")
        rows.append(
            {
                "awardId": award_id,
                "recipient": first_text(transaction, "Recipient Name", "recipient_name", default="Unknown recipient"),
                "agency": first_text(transaction, "Awarding Agency", "awarding_agency", default="Unknown agency"),
                "subAgency": first_text(transaction, "Awarding Sub Agency", "awarding_sub_agency", default="Unknown agency"),
                "awardType": first_text(transaction, "Award Type", "award_type", default="contract"),
                "amount": money_millions(first_text(transaction, "Transaction Amount", "transaction_amount", "Award Amount", "award_amount", default="0")),
                "issueDomain": os.environ.get("USASPENDING_ISSUE_DOMAIN", "procurement"),
                "awardCount": 1,
                "uei": first_text(transaction, "Recipient UEI", "recipient_uei", default=""),
                "piid": award_id,
                "modificationNumber": modification_number,
                "actionDate": first_text(transaction, "Action Date", "action_date", default=""),
                "competitionType": "unknown",
                "numberOfOffers": "0",
                "priceOnlyAward": "false",
                "exPostModification": str(modification_sequence(modification_number) > 0).lower(),
                "protestFiled": "false",
                "exclusionFlag": "false",
                "firewallCovered": str(os.environ.get("USASPENDING_FIREWALL_COVERED", "false").lower() == "true").lower(),
            }
        )
    return rows


NYC_PUBLIC_FINANCING_SOURCE = "NYC Campaign Finance Board"
SEATTLE_DVP_SOURCE = "Seattle Democracy Voucher Program"
SEATTLE_DVP_PROGRAM_DATA_PAGE = "https://www.seattle.gov/ethics-and-elections/democracy-voucher-program/program-data"
INTERMEDIARY_FIELDS = [
    "organization",
    "ein",
    "sourceType",
    "subsection",
    "issueDomain",
    "revenue",
    "politicalSpend",
    "grantmaking",
    "donorDisclosure",
    "recipient",
    "sourceUrl",
]


def fetch_nyc_public_financing(output: Path) -> int:
    election = os.environ.get("NYC_CFB_ELECTION", "2025")
    payments_url = os.environ.get("NYC_CFB_PUBLIC_PAYMENTS_URL") or nyc_cfb_data_url(f"{election}_Payments.csv")
    analysis_url = os.environ.get("NYC_CFB_FINANCIAL_ANALYSIS_URL") or nyc_cfb_data_url(f"EC{election}_FinancialAnalysis.csv")
    payments = csv_rows_from_url(payments_url, int_env("NYC_CFB_PUBLIC_PAYMENTS_MAX_ROWS", 5000, 1, 50000))
    try:
        analysis = csv_rows_from_url(analysis_url, int_env("NYC_CFB_FINANCIAL_ANALYSIS_MAX_ROWS", 5000, 1, 50000))
    except SystemExit:
        if os.environ.get("NYC_CFB_STRICT_ANALYSIS", "0") == "1":
            raise
        analysis = []
    rows = normalize_nyc_public_financing_records(payments, analysis, payments_url, election)
    write_rows(output, FEC_FIELDS, rows, "NYC CFB public-funds payment rows")
    return 0


def fetch_seattle_democracy_vouchers(output: Path) -> int:
    source_url = os.environ.get("SEATTLE_DVP_XLSX_URL") or latest_seattle_dvp_xlsx_url()
    records = seattle_democracy_voucher_source_rows(source_url)
    rows = normalize_seattle_democracy_voucher_records(records, source_url)
    write_rows(output, FEC_FIELDS, rows, "Seattle Democracy Voucher program rows")
    return 0


def latest_seattle_dvp_xlsx_url() -> str:
    page_url = os.environ.get("SEATTLE_DVP_PROGRAM_DATA_PAGE", SEATTLE_DVP_PROGRAM_DATA_PAGE)
    page = get_text(page_url)
    matches = re.findall(r'href=["\']([^"\']+\.xlsx)["\']', page, flags=re.IGNORECASE)
    if not matches:
        raise SystemExit(f"{redact_url(page_url)} did not expose a Democracy Voucher XLSX link.")
    root = "https://www.seattle.gov"
    urls = [absolute_seattle_url(html.unescape(match), root) for match in matches]
    urls.sort(reverse=True)
    return urls[0]


def absolute_seattle_url(href: str, root: str) -> str:
    if href.startswith(("http://", "https://")):
        return href
    if href.startswith("/"):
        return root + href
    return root + "/" + href


def seattle_democracy_voucher_source_rows(source_url: str) -> list[dict[str, str]]:
    max_rows = int_env("SEATTLE_DVP_MAX_ROWS", 50000, 1, 500000)
    with tempfile.TemporaryFile() as workbook_file:
        download_binary(source_url, workbook_file)
        workbook_file.seek(0)
        rows = xlsx_rows_from_file(workbook_file, os.environ.get("SEATTLE_DVP_SHEET", "Web Program Data"), max_rows)
    if not rows:
        raise SystemExit(f"{redact_url(source_url)} returned no Democracy Voucher rows.")
    write_raw_binary_source_manifest(source_url, "seattle-democracy-vouchers", len(rows), [])
    return rows


def normalize_seattle_democracy_voucher_records(records: list[dict[str, str]], source_url: str = "") -> list[dict[str, object]]:
    accepted_statuses = {
        status.lower()
        for status in split_csv_env("SEATTLE_DVP_ACCEPTED_STATUSES", "Redeemed,Accepted")
    }
    voucher_value = float_env("SEATTLE_DVP_VOUCHER_VALUE", 25.0, 0.0, 1000.0)
    minimum_vouchers = int_env("SEATTLE_DVP_MIN_VOUCHERS", 2, 1, 100000)
    disclosure_lag = float_env("SEATTLE_DVP_DISCLOSURE_LAG", 0.08, 0.0, 1.0)
    campaign_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for record in records:
        status = first_text(record, "Voucher Status", "status", "voucher_status", default="").strip()
        status_counts[status] = status_counts.get(status, 0) + 1
        if status.lower() not in accepted_statuses:
            continue
        campaign = first_text(record, "Assigned Campaign", "assigned_campaign", "campaign", default="").strip()
        if not campaign or campaign.lower() == "unassigned":
            continue
        campaign_counts[campaign] = campaign_counts.get(campaign, 0) + 1
    rows: list[dict[str, object]] = []
    for campaign, voucher_count in sorted(campaign_counts.items()):
        if voucher_count < minimum_vouchers:
            continue
        amount = voucher_count * voucher_value
        digest = hashlib.sha256(campaign.encode("utf-8")).hexdigest()[:10]
        rows.append(
            {
                "source": SEATTLE_DVP_SOURCE,
                "recipient": campaign,
                "issueDomain": "democracy",
                "amount": money_millions(str(amount)),
                "flowType": "DEMOCRACY_VOUCHER",
                "traceability": 0.98,
                "largeDonorShare": 0.04,
                "sourceRecordId": f"seattle-dvp-{digest}",
                "sourceUrl": source_url,
                "committeeType": "municipal democracy vouchers",
                "spendingPurpose": f"{voucher_count} accepted or redeemed vouchers",
                "supportOppose": "",
                "disclosureLag": disclosure_lag,
            }
        )
    rows.sort(key=lambda row: (float(row["amount"]), str(row["recipient"])), reverse=True)
    if not rows:
        details = ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items())[:8])
        raise SystemExit(f"Seattle Democracy Voucher workbook had no accepted voucher rows after filters ({details}).")
    return rows


def normalize_nyc_public_financing_records(
        payments: list[dict[str, str]],
        analysis: list[dict[str, str]] | None = None,
        source_url: str = "",
        election: str = ""
) -> list[dict[str, object]]:
    analysis_by_candidate = {
        first_text(row, "CANDID", "candid", "candidate_id", default=""): row
        for row in (analysis or [])
        if first_text(row, "CANDID", "candid", "candidate_id", default="")
    }
    rows: list[dict[str, object]] = []
    minimum_payment = float_env("NYC_CFB_MIN_PUBLIC_PAYMENT", 1.0, 0.0, 1_000_000_000.0)
    for record in payments:
        candidate_id = first_text(record, "CANDID", "candid", "candidate_id", default="").strip()
        candidate = first_text(record, "CANDNAME", "candname", "candidate_name", default=f"NYC candidate {candidate_id or 'unknown'}").strip()
        total_payment_raw = raw_money(first_text(record, "TOTALPAY", "totalpay", "TOTAL_PAYMENT", "amount", default="0"))
        if total_payment_raw <= minimum_payment:
            continue
        analysis_row = analysis_by_candidate.get(candidate_id, {})
        rows.append(
            {
                "source": NYC_PUBLIC_FINANCING_SOURCE,
                "recipient": candidate,
                "issueDomain": "democracy",
                "amount": money_millions(str(total_payment_raw)),
                "flowType": "PUBLIC_MATCH",
                "traceability": 0.96,
                "largeDonorShare": nyc_large_donor_share(analysis_row, total_payment_raw),
                "sourceRecordId": "-".join(part for part in ["nyc-cfb", election, candidate_id] if part),
                "sourceUrl": source_url,
                "committeeType": "municipal public matching funds",
                "spendingPurpose": "public funds payment",
                "supportOppose": "",
                "disclosureLag": 0.04,
            }
        )
    return rows


def fetch_nyc_intermediaries(output: Path) -> int:
    election = os.environ.get("NYC_CFB_ELECTION", "2025")
    url = os.environ.get("NYC_CFB_INTERMEDIARIES_URL") or nyc_cfb_data_url(f"{election}_Intermediaries.csv")
    source_rows = csv_rows_from_url(url, int_env("NYC_CFB_INTERMEDIARY_MAX_ROWS", 2500, 1, 50000))
    rows = normalize_nyc_intermediary_records(source_rows, url)
    write_rows(output, INTERMEDIARY_FIELDS, rows, "NYC CFB intermediary rows")
    return 0


def normalize_nyc_intermediary_records(records: list[dict[str, str]], source_url: str = "") -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for record in records:
        organization = first_text(record, "NAME", "name", "intermediary_name", default="").strip()
        if not organization:
            continue
        amount = money_millions(first_text(record, "AMNT", "amount", "total", default="0"))
        if amount <= 0.0:
            continue
        recipient = candidate_name_from_nyc_row(record)
        key = (organization, recipient)
        existing = grouped.setdefault(
            key,
            {
                "organization": organization,
                "ein": "",
                "sourceType": "nyc-cfb-intermediary",
                "subsection": "campaign-intermediary",
                "issueDomain": "democracy",
                "revenue": 0.0,
                "politicalSpend": 0.0,
                "grantmaking": 0.0,
                "donorDisclosure": donor_disclosure_for_nyc_intermediary(record),
                "recipient": recipient,
                "sourceUrl": source_url,
            },
        )
        existing["revenue"] = float(existing["revenue"]) + amount
        existing["politicalSpend"] = float(existing["politicalSpend"]) + amount
        existing["donorDisclosure"] = max(float(existing["donorDisclosure"]), donor_disclosure_for_nyc_intermediary(record))
    return [grouped[key] for key in sorted(grouped)]


def fetch_irs_eo_bmf(output: Path) -> int:
    source_rows = irs_eo_bmf_source_rows()
    rows = normalize_irs_eo_bmf_records(source_rows)
    write_rows(output, INTERMEDIARY_FIELDS, rows, "IRS EO BMF nonprofit/intermediary capacity rows")
    return 0


def normalize_irs_eo_bmf_records(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in filtered_irs_eo_bmf_records(source_rows, split_csv_env("IRS_EO_BMF_SUBSECTIONS", "03,04,06")):
        revenue = money_millions(first_text(record, "REVENUE_AMT", "INCOME_AMT", "ASSET_AMT", default="0"))
        subsection = first_text(record, "SUBSECTION", default="")
        name = first_text(record, "NAME", default="Unknown exempt organization")
        rows.append(
            {
                "organization": name,
                "ein": first_text(record, "EIN", default=""),
                "sourceType": "irs-eo-bmf-capacity",
                "subsection": irs_subsection_label(subsection),
                "issueDomain": classify_domain(" ".join([name, first_text(record, "NTEE_CD", "ACTIVITY", default="")])),
                "revenue": revenue,
                "politicalSpend": political_capacity_proxy(revenue, subsection),
                "grantmaking": grantmaking_capacity_proxy(revenue, record),
                "donorDisclosure": donor_disclosure_for_irs_subsection(subsection),
                "recipient": "",
                "sourceUrl": first_text(record, "_sourceUrl", default=""),
            }
        )
    return rows


def fetch_irs_dark_money_capacity(output: Path) -> int:
    source_rows = irs_eo_bmf_source_rows(
        states_env="IRS_DARK_MONEY_BMF_STATES",
        urls_env="IRS_DARK_MONEY_BMF_URLS",
        max_rows_env="IRS_DARK_MONEY_CAPACITY_MAX_ROWS",
    )
    rows = normalize_irs_dark_money_capacity_records(source_rows)
    write_rows(output, FEC_FIELDS, rows, "IRS EO BMF opaque nonprofit capacity rows")
    return 0


def normalize_irs_dark_money_capacity_records(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in filtered_irs_eo_bmf_records(source_rows, split_csv_env("IRS_DARK_MONEY_BMF_SUBSECTIONS", "04,06")):
        subsection = first_text(record, "SUBSECTION", default="")
        revenue = money_millions(first_text(record, "REVENUE_AMT", "INCOME_AMT", "ASSET_AMT", default="0"))
        capacity = dark_money_capacity_proxy(revenue, subsection)
        if capacity <= 0.0:
            continue
        name = first_text(record, "NAME", default="Unknown exempt organization")
        rows.append(
            {
                "source": name,
                "recipient": "Opaque issue-advocacy capacity",
                "issueDomain": classify_domain(" ".join([name, first_text(record, "NTEE_CD", "ACTIVITY", default="")])),
                "amount": capacity,
                "flowType": "DARK_MONEY",
                "traceability": 0.12 if normalize_subsection(subsection) == "04" else 0.24,
                "largeDonorShare": 0.74 if normalize_subsection(subsection) == "04" else 0.64,
                "sourceRecordId": first_text(record, "EIN", default=""),
                "sourceUrl": first_text(record, "_sourceUrl", default=""),
                "committeeType": f"{irs_subsection_label(subsection)} capacity proxy",
                "spendingPurpose": "opaque nonprofit advocacy capacity proxy",
                "supportOppose": "",
                "disclosureLag": 0.55,
            }
        )
    rows.sort(key=lambda row: float(row["amount"]), reverse=True)
    return rows[: int_env("IRS_DARK_MONEY_CAPACITY_OUTPUT_ROWS", 250, 1, 5000)]


PROPUBLICA_NONPROFIT_API_BASE = "https://projects.propublica.org/nonprofits/api/v2"
PROPUBLICA_NONPROFIT_PUBLIC_BASE = "https://projects.propublica.org/nonprofits"


def fetch_propublica_nonprofit_routing(output: Path) -> int:
    rows = propublica_nonprofit_routing_rows()
    write_rows(output, FEC_FIELDS, rows, "ProPublica Nonprofit Explorer Schedule I routing rows")
    return 0


def propublica_nonprofit_routing_rows() -> list[dict[str, object]]:
    api_base = os.environ.get("PROPUBLICA_NONPROFIT_API_BASE", PROPUBLICA_NONPROFIT_API_BASE).rstrip("/")
    public_base = os.environ.get("PROPUBLICA_NONPROFIT_PUBLIC_BASE", PROPUBLICA_NONPROFIT_PUBLIC_BASE).rstrip("/")
    rows: list[dict[str, object]] = []
    max_rows = int_env("PROPUBLICA_NONPROFIT_ROUTING_OUTPUT_ROWS", 100, 1, 5000)
    for ein in propublica_nonprofit_routing_eins():
        if len(rows) >= max_rows:
            break
        organization_payload = get_json(f"{api_base}/organizations/{ein}.json")
        if not isinstance(organization_payload, dict):
            continue
        organization = organization_payload.get("organization")
        if not isinstance(organization, dict):
            continue
        if not propublica_organization_allowed(organization):
            continue
        object_id = first_text(organization, "latest_object_id", default="")
        if not object_id:
            continue
        schedule_url = f"{public_base}/full_text/{object_id}/IRS990ScheduleI"
        try:
            schedule_html = get_text(schedule_url, {"Accept": "text/html"})
        except SystemExit:
            if os.environ.get("PROPUBLICA_NONPROFIT_ROUTING_STRICT", "0") == "1":
                raise
            continue
        rows.extend(normalize_propublica_schedule_i_rows(organization, schedule_html, schedule_url))
    rows.sort(key=lambda row: (float(row["amount"]), str(row["source"]), str(row["recipient"])), reverse=True)
    return rows[:max_rows]


def propublica_nonprofit_routing_eins() -> list[str]:
    explicit = split_csv_env("PROPUBLICA_NONPROFIT_ROUTING_EINS", "")
    if explicit:
        return [normalize_ein(ein) for ein in explicit if normalize_ein(ein)]
    input_path = Path(os.environ.get("PROPUBLICA_NONPROFIT_ROUTING_INPUT", "data/raw/dark-money.csv"))
    rows = read_csv_rows(input_path)
    rows.sort(key=lambda row: number_for_sort(row.get("amount", "")), reverse=True)
    max_orgs = int_env("PROPUBLICA_NONPROFIT_ROUTING_MAX_ORGS", 12, 1, 250)
    eins: list[str] = []
    seen: set[str] = set()
    for row in rows:
        ein = normalize_ein(row.get("sourceRecordId", ""))
        if not ein or ein in seen:
            continue
        if is_dark_money_capacity_proxy(row):
            seen.add(ein)
            eins.append(ein)
        if len(eins) >= max_orgs:
            break
    return eins


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def number_for_sort(value: object) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return 0.0


def is_dark_money_capacity_proxy(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("committeeType", ""),
            row.get("spendingPurpose", ""),
            row.get("sourceUrl", ""),
        ]
    ).lower()
    return "capacity proxy" in text or ("eo_" in text and "irs-soi" in text)


def normalize_ein(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    return digits if len(digits) == 9 else ""


def propublica_organization_allowed(organization: dict[str, object]) -> bool:
    allowed = {normalize_subsection(value) for value in split_csv_env("PROPUBLICA_NONPROFIT_ROUTING_SUBSECTIONS", "04,06")}
    subsection = normalize_subsection(first_text(organization, "subsection_code", "subseccd", default=""))
    return not allowed or subsection in allowed


def normalize_propublica_schedule_i_rows(
        organization: dict[str, object],
        schedule_html: str,
        schedule_url: str,
) -> list[dict[str, object]]:
    recipient_tables: dict[int, dict[str, str]] = {}
    for match in re.finditer(r'id="([^"]*RecipientTable\[(\d+)\][^"]*)"[^>]*>(.*?)</span>', schedule_html, flags=re.IGNORECASE | re.DOTALL):
        path, index_text, raw_value = match.groups()
        value = clean_html_cell(raw_value)
        if not value:
            continue
        field = propublica_schedule_i_field(path)
        if not field:
            continue
        recipient_tables.setdefault(int(index_text), {})[field] = value
    rows: list[dict[str, object]] = []
    source = first_text(organization, "name", default="Unknown nonprofit")
    source_ein = normalize_ein(first_text(organization, "ein", default=""))
    subsection = irs_subsection_label(first_text(organization, "subsection_code", "subseccd", default=""))
    tax_period = first_text(organization, "tax_period", default="")
    for index in sorted(recipient_tables):
        record = recipient_tables[index]
        recipient = record.get("recipient", "").strip()
        amount = money_millions(record.get("cashGrant", "0"))
        if amount <= 0.0 or not propublica_recipient_is_specific(recipient):
            continue
        rows.append(
            {
                "source": source,
                "recipient": recipient,
                "issueDomain": classify_domain(" ".join([source, recipient, record.get("purpose", ""), record.get("ircSection", "")])),
                "amount": amount,
                "flowType": "DARK_MONEY",
                "traceability": propublica_nonprofit_routing_traceability(subsection),
                "largeDonorShare": propublica_nonprofit_routing_large_donor_share(subsection),
                "sourceRecordId": "-".join(part for part in [source_ein, tax_period, f"schedule-i-{index}"] if part),
                "sourceUrl": schedule_url,
                "committeeType": f"{subsection} Schedule I nonprofit routing",
                "spendingPurpose": record.get("purpose", "reported Form 990 Schedule I grant"),
                "supportOppose": "",
                "disclosureLag": 0.48,
            }
        )
    return rows


def propublica_schedule_i_field(path: str) -> str:
    if "RecipientBusinessName" in path and "BusinessNameLine1Txt" in path:
        return "recipient"
    if "RecipientEIN" in path:
        return "recipientEin"
    if "IRCSectionDesc" in path:
        return "ircSection"
    if "CashGrantAmt" in path:
        return "cashGrant"
    if "NonCashAssistanceAmt" in path:
        return "noncashAssistance"
    if "PurposeOfGrantTxt" in path or "PurposeOfGrantOrAssistanceDesc" in path:
        return "purpose"
    return ""


def clean_html_cell(raw_value: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw_value))
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def propublica_recipient_is_specific(recipient: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", recipient.lower()).strip()
    if not normalized:
        return False
    generic = {
        "see attached schedule",
        "see schedule",
        "attached schedule",
        "various",
        "various recipients",
        "miscellaneous",
    }
    return normalized not in generic


def propublica_nonprofit_routing_traceability(subsection: str) -> float:
    code = normalize_subsection(subsection)
    if code == "04":
        return 0.06
    if code == "06":
        return 0.08
    return 0.07


def propublica_nonprofit_routing_large_donor_share(subsection: str) -> float:
    code = normalize_subsection(subsection)
    if code == "04":
        return 0.68
    if code == "06":
        return 0.58
    return 0.62


IRS_POFD_DOWNLOAD_BASE = "https://forms.irs.gov/app/pod/dataDownload"
IRS_POFD_FILE_ENDPOINTS = {
    "FULL": "fullData",
    "AG": "dataAG",
    "HM": "dataHM",
    "NR": "dataNR",
    "SZ": "dataSZ",
}
IRS_POFD_DATA_PAGE = f"{IRS_POFD_DOWNLOAD_BASE}/dataDownload"


def fetch_irs_527(output: Path) -> int:
    source_rows = irs_pofd_8872_source_rows()
    rows = normalize_irs_pofd_8872_records(source_rows)
    write_rows(output, INTERMEDIARY_FIELDS, rows, "IRS POFD Form 8872 political-organization rows")
    return 0


def normalize_irs_pofd_8872_records(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for record in source_rows:
        organization = first_text(record, "organization", default="").strip()
        ein = first_text(record, "ein", default="").strip()
        if not organization:
            continue
        contributions = money_millions(first_text(record, "totalContributions", default="0"))
        expenditures = money_millions(first_text(record, "totalExpenditures", default="0"))
        activity_volume = round(contributions + expenditures, 4)
        if activity_volume <= 0.0:
            continue
        period_end = first_text(record, "periodEnd", default="")
        key = (ein or organization, period_end)
        existing = grouped.setdefault(
            key,
            {
                "organization": organization,
                "ein": ein,
                "sourceType": "irs-pofd-8872",
                "subsection": "527",
                "issueDomain": classify_domain(" ".join([
                    organization,
                    first_text(record, "purpose", default=""),
                    first_text(record, "state", default=""),
                ])),
                "revenue": 0.0,
                "politicalSpend": 0.0,
                "grantmaking": 0.0,
                "donorDisclosure": donor_disclosure_for_irs_8872(record),
                "recipient": first_text(record, "state", default="527 political activity"),
                "sourceUrl": first_text(record, "sourceUrl", default=IRS_POFD_DATA_PAGE),
            },
        )
        existing["revenue"] = round(float(existing["revenue"]) + activity_volume, 4)
        existing["politicalSpend"] = round(float(existing["politicalSpend"]) + expenditures, 4)
        existing["donorDisclosure"] = max(float(existing["donorDisclosure"]), donor_disclosure_for_irs_8872(record))
    rows = [grouped[key] for key in sorted(grouped)]
    rows.sort(key=lambda row: (float(row["politicalSpend"]), float(row["revenue"])), reverse=True)
    return rows[: int_env("IRS_POFD_OUTPUT_ROWS", 500, 1, 10000)]


def irs_pofd_8872_source_rows() -> list[dict[str, str]]:
    urls = split_csv_env("IRS_POFD_URLS", "")
    if not urls:
        base = os.environ.get("IRS_POFD_DOWNLOAD_BASE", IRS_POFD_DOWNLOAD_BASE).rstrip("/")
        files = [file_code.upper() for file_code in split_csv_env("IRS_POFD_FILES", "AG")]
        urls = [f"{base}/{IRS_POFD_FILE_ENDPOINTS.get(file_code, file_code)}" for file_code in files]
    max_lines = int_env("IRS_POFD_MAX_LINES_PER_FILE", 0, 0, 50_000_000)
    max_records = int_env("IRS_POFD_MAX_RECORDS", 2500, 1, 100000)
    rows: list[dict[str, str]] = []
    for url in urls:
        remaining = max_records - len(rows)
        if remaining <= 0:
            break
        rows.extend(irs_pofd_8872_records_from_url(url, remaining, max_lines))
    if not rows:
        raise SystemExit("IRS POFD Form 8872 source returned no rows after filters. Check IRS_POFD_YEAR, IRS_POFD_FILES, IRS_POFD_MAX_LINES_PER_FILE, and upstream availability.")
    return rows


def irs_pofd_8872_records_from_url(url: str, max_records: int, max_lines: int = 0) -> list[dict[str, str]]:
    year_filter = os.environ.get("IRS_POFD_YEAR", os.environ.get("FEC_CYCLE", "2024")).strip()
    minimum_activity = float_env("IRS_POFD_MIN_ACTIVITY_DOLLARS", 1.0, 0.0, 1_000_000_000.0)
    purposes_by_ein: dict[str, str] = {}
    rows: list[dict[str, str]] = []
    selected_lines: list[str] = []
    with tempfile.TemporaryFile() as archive_file:
        download_binary(url, archive_file)
        archive_file.seek(0)
        with zipfile.ZipFile(archive_file) as archive:
            text_members = [name for name in archive.namelist() if name.lower().endswith(".txt")]
            if not text_members:
                raise SystemExit(f"{redact_url(url)} did not contain a text data file.")
            with archive.open(text_members[0]) as source:
                for line_number, raw_line in enumerate(source, 1):
                    if max_lines and line_number > max_lines:
                        break
                    line = raw_line.decode("latin-1", errors="replace").rstrip("\r\n")
                    if not line:
                        continue
                    parts = line.split("|")
                    if not parts:
                        continue
                    if parts[0] == "1" and len(parts) > 41:
                        ein = parts[6].strip()
                        purpose = parts[39].strip() if len(parts) > 39 else ""
                        if ein and purpose and ein not in purposes_by_ein:
                            purposes_by_ein[ein] = purpose
                        continue
                    if parts[0] != "2" or len(parts) < 49:
                        continue
                    period_end = parts[4].strip()
                    insert_datetime = parts[48].strip() if len(parts) > 48 else ""
                    if year_filter and not pofd_record_matches_year(period_end, insert_datetime, year_filter):
                        continue
                    total_contributions = raw_money(parts[45] if len(parts) > 45 else "0")
                    total_expenditures = raw_money(parts[47] if len(parts) > 47 else "0")
                    if total_contributions + total_expenditures < minimum_activity:
                        continue
                    ein = parts[10].strip()
                    row = {
                        "formId": parts[2].strip(),
                        "periodBegin": parts[3].strip(),
                        "periodEnd": period_end,
                        "organization": parts[9].strip(),
                        "ein": ein,
                        "state": (parts[43].strip() if len(parts) > 43 else "") or (parts[14].strip() if len(parts) > 14 else ""),
                        "scheduleAIndicator": parts[44].strip() if len(parts) > 44 else "",
                        "totalContributions": str(total_contributions),
                        "scheduleBIndicator": parts[46].strip() if len(parts) > 46 else "",
                        "totalExpenditures": str(total_expenditures),
                        "insertDateTime": insert_datetime,
                        "purpose": purposes_by_ein.get(ein, ""),
                        "sourceUrl": url,
                    }
                    rows.append(row)
                    if len(selected_lines) < 25:
                        selected_lines.append(line)
                    if len(rows) >= max_records:
                        break
    write_raw_binary_source_manifest(url, "irs-pofd-8872", len(rows), selected_lines)
    return rows


def pofd_record_matches_year(period_end: str, insert_datetime: str, year_filter: str) -> bool:
    if not year_filter:
        return True
    years = {part.strip() for part in year_filter.split(",") if part.strip()}
    period_year = period_end[:4] if len(period_end) >= 4 else ""
    insert_year = insert_datetime[:4] if len(insert_datetime) >= 4 else ""
    return period_year in years or insert_year in years


def donor_disclosure_for_irs_8872(record: dict[str, str]) -> float:
    has_schedule_a = first_text(record, "scheduleAIndicator", default="1") == "0"
    has_schedule_b = first_text(record, "scheduleBIndicator", default="1") == "0"
    contributions = raw_money(first_text(record, "totalContributions", default="0"))
    expenditures = raw_money(first_text(record, "totalExpenditures", default="0"))
    if has_schedule_a and contributions > 0.0:
        return 0.72
    if has_schedule_b and expenditures > 0.0:
        return 0.66
    return donor_disclosure_for_irs_subsection("527")


def download_binary(url: str, destination) -> None:
    request = Request(url, headers={"User-Agent": "lobby-capture-simulator/0.1"})
    attempts = int_env("SOURCE_FETCH_RETRIES", 3, 1, 8)
    backoff = float_env("SOURCE_FETCH_BACKOFF_SECONDS", 1.0, 0.0, 30.0)
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=120) as response:
                digest = hashlib.sha256()
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    destination.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
                write_raw_binary_source_manifest(url, "binary-download", 0, [], total, digest.hexdigest())
                return
        except HTTPError as error:
            if should_retry(error.code, attempt, attempts):
                sleep_before_retry(error, attempt, backoff)
                continue
            detail = error.read().decode("utf-8", errors="replace")[:500]
            raise SystemExit(f"GET {redact_url(url)} failed with HTTP {error.code}: {detail}{auth_hint(error.code)}") from error
        except (URLError, RemoteDisconnected, TimeoutError, ConnectionError, OSError) as error:
            if attempt < attempts:
                sleep_before_retry(None, attempt, backoff)
                continue
            reason = getattr(error, "reason", str(error))
            raise SystemExit(f"GET {redact_url(url)} failed after {attempts} attempts: {reason}") from error
    raise AssertionError("unreachable")


def write_raw_binary_source_manifest(
        url: str,
        source_name: str,
        normalized_rows: int,
        sample_lines: list[str],
        byte_count: int | None = None,
        sha256_digest: str | None = None,
) -> None:
    raw_dir = os.environ.get("SOURCE_RAW_DIR")
    if not raw_dir:
        return
    root = Path(raw_dir)
    root.mkdir(parents=True, exist_ok=True)
    entry = {
        "source": source_name,
        "url": redact_url(url),
        "normalizedRows": normalized_rows,
    }
    if byte_count is not None:
        entry["byteCount"] = byte_count
    if sha256_digest:
        entry["sha256"] = sha256_digest
    with (root / "request-manifest.jsonl").open("a", encoding="utf-8") as manifest:
        manifest.write(json.dumps(entry, sort_keys=True) + "\n")
    if sample_lines:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        sample_path = root / f"irs-pofd-8872-sample-{digest}.txt"
        sample_path.write_text("\n".join(sample_lines) + "\n", encoding="utf-8")


def nyc_cfb_data_url(filename: str) -> str:
    return f"{os.environ.get('NYC_CFB_DATA_BASE', 'https://nyccfb.info/DataLibrary').rstrip('/')}/{filename}"


def nyc_large_donor_share(analysis_row: dict[str, str], public_payment_raw: float) -> float:
    if not analysis_row:
        return 0.10
    max_amount = raw_money(first_text(analysis_row, "max_amt", "MAX_AMT", default="0"))
    private_contributions = raw_money(first_text(analysis_row, "net_cntns", "NET_CNTNS", default="0"))
    public_funds = raw_money(first_text(analysis_row, "pubfnd_pmt", "PUBFND_PMT", default=str(public_payment_raw)))
    denominator = max(1.0, private_contributions + public_funds)
    return round(ValuesProxy.clamp(0.05 + (0.55 * (max_amount / denominator)), 0.03, 0.45), 4)


def candidate_name_from_nyc_row(record: dict[str, str]) -> str:
    first = first_text(record, "CANDFIRST", "candfirst", default="").strip()
    last = first_text(record, "CANDLAST", "candlast", default="").strip()
    combined = " ".join(part for part in [first, last] if part).strip()
    return combined or first_text(record, "CANDNAME", "candname", "CANDID", default="unknown candidate")


def donor_disclosure_for_nyc_intermediary(record: dict[str, str]) -> float:
    code = first_text(record, "C_CODE", "c_code", default="").upper()
    if code == "IND":
        return 0.72
    if code:
        return 0.62
    return 0.58


def irs_eo_bmf_source_rows(
        states_env: str = "IRS_EO_BMF_STATES",
        urls_env: str = "IRS_EO_BMF_URLS",
        max_rows_env: str = "IRS_EO_BMF_MAX_ROWS"
) -> list[dict[str, str]]:
    urls = split_csv_env(urls_env, "")
    if not urls:
        states = split_csv_env(states_env, "DC")
        urls = [irs_eo_bmf_url(state) for state in states]
    max_rows = int_env(max_rows_env, 500, 1, 50000)
    collected: list[dict[str, str]] = []
    for url in urls:
        remaining = max_rows - len(collected)
        if remaining <= 0:
            break
        for row in csv_rows_from_url(url, max(max_rows * 8, remaining)):
            row["_sourceUrl"] = url
            collected.append(row)
            if len(collected) >= max_rows * 8:
                break
    return collected


def filtered_irs_eo_bmf_records(source_rows: list[dict[str, str]], subsections: list[str]) -> list[dict[str, str]]:
    allowed = {normalize_subsection(subsection) for subsection in subsections}
    keywords = [keyword.lower() for keyword in split_csv_env("IRS_EO_BMF_KEYWORDS", "association,council,institute,policy,advocacy,action,coalition,chamber,forum,center,foundation,committee,project,alliance,network")]
    max_rows = int_env("IRS_EO_BMF_FILTERED_MAX_ROWS", 500, 1, 50000)
    filtered = []
    seen: set[str] = set()
    for record in source_rows:
        subsection = normalize_subsection(first_text(record, "SUBSECTION", default=""))
        if allowed and subsection not in allowed:
            continue
        name = first_text(record, "NAME", default="")
        identity = first_text(record, "EIN", default=name)
        if identity in seen:
            continue
        seen.add(identity)
        haystack = " ".join([name, first_text(record, "NTEE_CD", "ACTIVITY", "SORT_NAME", default="")]).lower()
        if keywords and not any(keyword in haystack for keyword in keywords):
            continue
        if money_millions(first_text(record, "REVENUE_AMT", "INCOME_AMT", "ASSET_AMT", default="0")) <= 0.0:
            continue
        filtered.append(record)
        if len(filtered) >= max_rows:
            break
    return filtered


def irs_eo_bmf_url(state: str) -> str:
    state_code = state.strip().lower()
    return f"{os.environ.get('IRS_EO_BMF_CSV_BASE', 'https://www.irs.gov/pub/irs-soi').rstrip('/')}/eo_{state_code}.csv"


def normalize_subsection(value: str) -> str:
    text = value.strip().lower().replace("501(c)(", "").replace(")", "").replace("c", "")
    digits = "".join(character for character in text if character.isdigit())
    return digits.zfill(2) if digits else text


def irs_subsection_label(value: str) -> str:
    code = normalize_subsection(value)
    if code in {"03", "04", "05", "06", "07"}:
        return f"501(c)({int(code)})"
    if code == "527":
        return "527"
    return f"501(c)({code})" if code else "unknown-exempt"


def donor_disclosure_for_irs_subsection(value: str) -> float:
    return {
        "03": 0.74,
        "04": 0.20,
        "05": 0.36,
        "06": 0.32,
        "07": 0.40,
        "527": 0.68,
    }.get(normalize_subsection(value), 0.42)


def political_capacity_proxy(revenue: float, subsection: str) -> float:
    rates = {
        "03": float_env("IRS_EO_BMF_POLITICAL_CAPACITY_RATE_C3", 0.003, 0.0, 1.0),
        "04": float_env("IRS_EO_BMF_POLITICAL_CAPACITY_RATE_C4", 0.025, 0.0, 1.0),
        "05": float_env("IRS_EO_BMF_POLITICAL_CAPACITY_RATE_C5", 0.012, 0.0, 1.0),
        "06": float_env("IRS_EO_BMF_POLITICAL_CAPACITY_RATE_C6", 0.018, 0.0, 1.0),
        "07": float_env("IRS_EO_BMF_POLITICAL_CAPACITY_RATE_C7", 0.006, 0.0, 1.0),
    }
    return round(revenue * rates.get(normalize_subsection(subsection), 0.006), 4)


def dark_money_capacity_proxy(revenue: float, subsection: str) -> float:
    code = normalize_subsection(subsection)
    rate = float_env("IRS_DARK_MONEY_CAPACITY_RATE_C4", 0.012, 0.0, 1.0) if code == "04" else float_env("IRS_DARK_MONEY_CAPACITY_RATE_C6", 0.006, 0.0, 1.0)
    cap = float_env("IRS_DARK_MONEY_CAPACITY_AMOUNT_CAP_MILLIONS", 8.0, 0.0, 1_000_000.0)
    return round(min(cap, revenue * rate), 4)


def grantmaking_capacity_proxy(revenue: float, record: dict[str, str]) -> float:
    ntee = first_text(record, "NTEE_CD", default="").upper()
    foundation = first_text(record, "FOUNDATION", default="")
    rate = 0.012 if ntee.startswith("T") or foundation not in {"", "0"} else 0.004
    return round(revenue * rate, 4)


def csv_rows_from_url(url: str, max_rows: int) -> list[dict[str, str]]:
    text = get_text(url)
    reader = csv.DictReader(StringIO(text.lstrip("\ufeff")))
    if reader.fieldnames is None:
        raise SystemExit(f"{redact_url(url)} returned CSV data without a header row.")
    rows = []
    for row in reader:
        rows.append(row)
        if len(rows) >= max_rows:
            break
    if not rows:
        raise SystemExit(f"{redact_url(url)} returned no CSV rows.")
    return rows


def xlsx_rows_from_file(workbook_file, sheet_name: str | None = None, max_rows: int = 50000) -> list[dict[str, str]]:
    with zipfile.ZipFile(workbook_file) as archive:
        shared_strings = xlsx_shared_strings(archive)
        worksheet = xlsx_worksheet_member(archive, sheet_name)
        xml_root = ET_from_zip(archive, worksheet)
        namespace = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        matrix: list[list[str]] = []
        for row in xml_root.findall(".//a:sheetData/a:row", namespace):
            values: list[str] = []
            for cell in row.findall("a:c", namespace):
                column = xlsx_cell_column_index(cell.attrib.get("r", ""))
                while len(values) <= column:
                    values.append("")
                values[column] = xlsx_cell_value(cell, shared_strings, namespace)
            matrix.append(values)
            if len(matrix) > max_rows:
                break
    if not matrix:
        return []
    header = [value.strip() for value in matrix[0]]
    rows: list[dict[str, str]] = []
    for values in matrix[1:]:
        if not any(value.strip() for value in values):
            continue
        row = {
            header[index]: values[index].strip() if index < len(values) else ""
            for index in range(len(header))
            if header[index]
        }
        rows.append(row)
        if len(rows) >= max_rows:
            break
    return rows


def xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    namespace = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET_from_zip(archive, "xl/sharedStrings.xml")
    strings: list[str] = []
    for item in root.findall("a:si", namespace):
        strings.append("".join(text.text or "" for text in item.findall(".//a:t", namespace)))
    return strings


def xlsx_worksheet_member(archive: zipfile.ZipFile, sheet_name: str | None) -> str:
    worksheets = sorted(name for name in archive.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name))
    if not worksheets:
        raise SystemExit("XLSX workbook did not contain worksheet XML.")
    if not sheet_name:
        return worksheets[0]
    namespace = {
        "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    try:
        workbook = ET_from_zip(archive, "xl/workbook.xml")
        rels = xlsx_workbook_relationships(archive)
    except KeyError:
        return worksheets[0]
    for sheet in workbook.findall("a:sheets/a:sheet", namespace):
        if sheet.attrib.get("name") != sheet_name:
            continue
        relationship_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
        target = rels.get(relationship_id, "")
        if not target:
            break
        member = "xl/" + target.lstrip("/")
        if member in archive.namelist():
            return member
        member = "xl/worksheets/" + Path(target).name
        if member in archive.namelist():
            return member
    return worksheets[0]


def xlsx_workbook_relationships(archive: zipfile.ZipFile) -> dict[str, str]:
    namespace = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    root = ET_from_zip(archive, "xl/_rels/workbook.xml.rels")
    return {
        relationship.attrib.get("Id", ""): relationship.attrib.get("Target", "")
        for relationship in root.findall("r:Relationship", namespace)
    }


def xlsx_cell_column_index(reference: str) -> int:
    letters = "".join(ch for ch in reference if ch.isalpha()).upper()
    if not letters:
        return 0
    index = 0
    for letter in letters:
        index = index * 26 + (ord(letter) - ord("A") + 1)
    return index - 1


def xlsx_cell_value(cell, shared_strings: list[str], namespace: dict[str, str]) -> str:
    if cell.attrib.get("t") == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//a:t", namespace))
    value = cell.find("a:v", namespace)
    if value is None or value.text is None:
        return ""
    text = value.text
    if cell.attrib.get("t") == "s":
        index = int(text)
        return shared_strings[index] if index < len(shared_strings) else ""
    return text


def ET_from_zip(archive: zipfile.ZipFile, member: str):
    import xml.etree.ElementTree as ET

    return ET.fromstring(archive.read(member))


def usaspending_award_detail(base: str, record: dict[str, object]) -> dict[str, object]:
    if os.environ.get("USASPENDING_ENRICH_AWARD_DETAILS", "1") != "1":
        return {}
    generated_id = first_text(record, "generated_internal_id", "generated_unique_award_id", default="")
    if not generated_id:
        return {}
    try:
        payload = get_json(f"{base}/awards/{generated_id}/")
        return payload if isinstance(payload, dict) else {}
    except SystemExit:
        if os.environ.get("USASPENDING_STRICT_ENRICHMENT", "0") == "1":
            raise
        return {}


def usaspending_transaction_summary(base: str, piid: str) -> dict[str, object]:
    if os.environ.get("USASPENDING_ENRICH_TRANSACTIONS", "1") != "1" or not piid:
        return {}
    rows = usaspending_transaction_records(base, piid)
    mods = [first_text(row, "Mod", "mod", default="") for row in rows if isinstance(row, dict)]
    nonzero_mods = [mod for mod in mods if mod.strip() not in {"", "0", "0.0", "none", "None"}]
    return {
        "modificationNumber": nonzero_mods[0] if nonzero_mods else (mods[0] if mods else "0"),
        "actionDate": first_text(rows[0], "Action Date", "action_date", default="") if rows else "",
    }


def usaspending_transaction_records(base: str, piid: str) -> list[dict[str, object]]:
    if os.environ.get("USASPENDING_ENRICH_TRANSACTIONS", "1") != "1" or not piid:
        return []
    payload = {
        "filters": {
            "award_ids": [piid],
            "award_type_codes": split_csv_env("USASPENDING_AWARD_TYPE_CODES", "A,B,C,D"),
        },
        "fields": [
            "Award ID",
            "Action Date",
            "Mod",
            "Transaction Amount",
            "Recipient Name",
            "Recipient UEI",
            "Awarding Agency",
            "Awarding Sub Agency",
            "Award Type",
        ],
        "page": 1,
        "limit": int_env("USASPENDING_TRANSACTION_LIMIT", int_env("USASPENDING_ACTION_TRANSACTION_LIMIT", 50, 1, 100), 1, 100),
        "sort": "Action Date",
        "order": "desc",
    }
    try:
        response = post_json(f"{base}/search/spending_by_transaction/", payload)
    except SystemExit:
        if os.environ.get("USASPENDING_STRICT_ENRICHMENT", "0") == "1":
            raise
        return []
    rows = response.get("results", []) if isinstance(response, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def fetch_regulations_gov_rows() -> list[dict[str, object]]:
    api_key = os.environ.get("REGULATIONS_API_KEY", "DEMO_KEY")
    base = os.environ.get("REGULATIONS_API_BASE", "https://api.regulations.gov/v4").rstrip("/")
    params = {
        "page[size]": bounded_int_env("REGULATORY_PAGE_SIZE", 25, 5, 250),
        "sort": os.environ.get("REGULATORY_SORT", "-postedDate"),
    }
    if os.environ.get("REGULATORY_AGENCY"):
        params["filter[agencyId]"] = os.environ["REGULATORY_AGENCY"]
    if os.environ.get("REGULATORY_SEARCH_TERM"):
        params["filter[searchTerm]"] = os.environ["REGULATORY_SEARCH_TERM"]
    if os.environ.get("REGULATORY_DATE_FROM"):
        params["filter[postedDate][ge]"] = os.environ["REGULATORY_DATE_FROM"]
    if os.environ.get("REGULATORY_DATE_TO"):
        params["filter[postedDate][le]"] = os.environ["REGULATORY_DATE_TO"]

    payload = get_json(f"{base}/documents?{urlencode(params)}", {"X-Api-Key": api_key})
    return normalize_regulations_gov_payload(payload)


def normalize_regulations_gov_payload(payload: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for item in payload.get("data", []):
        attributes = item.get("attributes", {})
        title = first_text(attributes, "title", default="")
        docket_id = first_text(attributes, "docketId", default=item.get("id", "UNKNOWN"))
        agency = first_text(attributes, "agencyId", default="unknown-agency")
        comments = int_or_zero(first_text(attributes, "commentCount", "comment_count", default="0"))
        rows.append(regulatory_row(docket_id, title, agency, comments))
    return rows


def fetch_federal_register_rows() -> list[dict[str, object]]:
    base = os.environ.get("FEDERAL_REGISTER_API_BASE", "https://www.federalregister.gov/api/v1").rstrip("/")
    params = {
        "per_page": os.environ.get("REGULATORY_PAGE_SIZE", "25"),
        "order": "newest",
        "conditions[type][]": os.environ.get("FEDERAL_REGISTER_TYPE", "PRORULE"),
    }
    if os.environ.get("REGULATORY_SEARCH_TERM"):
        params["conditions[term]"] = os.environ["REGULATORY_SEARCH_TERM"]
    if os.environ.get("REGULATORY_DATE_FROM"):
        params["conditions[publication_date][gte]"] = os.environ["REGULATORY_DATE_FROM"]
    if os.environ.get("REGULATORY_DATE_TO"):
        params["conditions[publication_date][lte]"] = os.environ["REGULATORY_DATE_TO"]

    payload = get_json(f"{base}/documents.json?{urlencode(params)}")
    return normalize_federal_register_payload(payload)


def normalize_federal_register_payload(payload: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for item in payload.get("results", []):
        title = first_text(item, "title", "abstract", default="")
        docket_id = first_text(item, "docket_ids.0", "document_number", default=first_text(item, "document_number", default="UNKNOWN"))
        agencies = item.get("agencies") or []
        agency = agencies[0].get("slug", agencies[0].get("name", "unknown-agency")) if agencies else "unknown-agency"
        rows.append(regulatory_row(docket_id, title, agency, 0))
    return rows


def regulatory_row(docket_id: str, title: str, agency: str, comment_volume: int) -> dict[str, object]:
    domain = classify_domain(" ".join([docket_id, title, agency]))
    volume = max(comment_volume, 120 if domain in {"energy", "technology", "finance"} else 60)
    return {
        "docketId": docket_id,
        "issueDomain": domain,
        "agency": agency,
        "commentVolume": volume,
        "genuineShare": 0.38,
        "templateShare": 0.46,
        "technicalClaimCredibility": 0.50,
        "authenticationShare": 0.32,
    }


def issue_domains_from_lda(record: dict[str, object]) -> list[str]:
    issues = record.get("lobbying_activities") or record.get("issues") or record.get("issue_codes") or []
    if isinstance(issues, dict):
        issues = [issues]
    domains = []
    for issue in issues if isinstance(issues, list) else []:
        if isinstance(issue, dict):
            text = " ".join(
                first_text(
                    issue,
                    "general_issue_code",
                    "general_issue_code_display",
                    "description",
                    default=json.dumps(issue),
                ).split()
            )
        else:
            text = issue if isinstance(issue, str) else json.dumps(issue)
        domains.append(classify_domain(text))
    if not domains:
        domains.append(classify_domain(json.dumps(record)))
    return sorted(set(domains))


def record_matches_lda_filters(record: dict[str, object]) -> bool:
    issue_codes = set(split_env("LDA_ISSUE_CODE"))
    if issue_codes and not (issue_codes & set(lda_issue_codes(record))):
        return False
    text_filter = os.environ.get("LDA_TEXT_FILTER", "").strip().lower()
    if text_filter and text_filter not in json.dumps(record).lower():
        return False
    return True


def lda_issue_codes(record: dict[str, object]) -> list[str]:
    activities = record.get("lobbying_activities") or []
    if isinstance(activities, dict):
        activities = [activities]
    codes = []
    for activity in activities if isinstance(activities, list) else []:
        if isinstance(activity, dict):
            code = first_text(activity, "general_issue_code", default="").upper()
            if code:
                codes.append(code)
    return codes


def split_env(name: str) -> list[str]:
    value = os.environ.get(name, "")
    return [part.strip().upper() for part in value.split(",") if part.strip()]


def split_csv_env(name: str, default: str) -> list[str]:
    value = os.environ.get(name, default)
    return [part.strip() for part in value.split(",") if part.strip()]


def classify_domain(text: str) -> str:
    normalized = text.lower()
    rules = {
        "energy": ("energy", "oil", "gas", "electric", "climate", "pipeline", "utility", "environment", "environmental", "epa", "clean air", "env"),
        "technology": ("technology", "platform", "data", "privacy", "internet", "software", "telecom", "ai"),
        "finance": ("finance", "bank", "securities", "capital", "insurance", "tax", "credit"),
        "procurement": ("procurement", "contract", "defense", "acquisition", "federal services"),
        "democracy": ("election", "campaign", "disclosure", "ethics", "voting", "democracy"),
    }
    for domain, keywords in rules.items():
        if any(keyword_matches(normalized, keyword) for keyword in keywords):
            return domain
    return os.environ.get("DEFAULT_ISSUE_DOMAIN", "democracy")


def keyword_matches(text: str, keyword: str) -> bool:
    if len(keyword) <= 2 and keyword.isalnum():
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
    return keyword in text


def infer_fec_flow_type(recipient: str) -> str:
    text = recipient.lower()
    if "super pac" in text or "independent expenditure" in text:
        return "SUPER_PAC"
    if "pac" in text:
        return "PAC"
    return "DIRECT_CONTRIBUTION"


def infer_independent_expenditure_flow_type(source: str, committee_type: str, purpose: str) -> str:
    text = " ".join([source, committee_type, purpose]).lower()
    if "super pac" in text or "independent expenditure-only" in text:
        return "SUPER_PAC"
    if "501(c)(4)" in text or "social welfare" in text or "dark money" in text:
        return "DARK_MONEY"
    if "trade association" in text or "501(c)(6)" in text:
        return "TRADE_ASSOCIATION"
    if "independent expenditor" in text and "political committee" not in text:
        return "DARK_MONEY"
    return "SUPER_PAC"


def traceability_for_outside_spending(flow_type: str, committee_type: str) -> float:
    if flow_type == "DARK_MONEY":
        return 0.28
    if flow_type == "TRADE_ASSOCIATION":
        return 0.42
    if "Super PAC" in committee_type or "Independent Expenditure-Only" in committee_type:
        return 0.58
    return 0.48


def fec_source_url(image_number: str) -> str:
    if not image_number:
        return ""
    return f"https://docquery.fec.gov/cgi-bin/fecimg/?{image_number}"


def fec_visibility_lag(record: dict[str, object]) -> float:
    filed = parse_date(first_text(record, "filed_date", "filing_date", "receipt_date", default=""))
    activity = parse_date(first_text(
        record,
        "expenditure_date",
        "disbursement_date",
        "communication_date",
        "transaction_date",
        "public_distribution_date",
        "dissemination_date",
        "contribution_receipt_date",
        default="",
    ))
    if filed is None or activity is None:
        return float_env("FEC_DISCLOSURE_VISIBILITY_LAG", 0.28, 0.0, 1.0)
    days = max(0, (filed - activity).days)
    return round(ValuesProxy.clamp(0.08 + (days / 120.0), 0.04, 0.70), 4)


def fec_cycle_window() -> tuple[str, str]:
    cycle = int_or_zero(os.environ.get("FEC_CYCLE", "2024"))
    if cycle <= 0:
        cycle = 2024
    return f"{cycle - 1}-01-01", f"{cycle}-12-31"


def get_json(url: str, headers: dict[str, str] | None = None) -> dict[str, object] | list[object]:
    return request_json("GET", url, headers)


def get_text(url: str, headers: dict[str, str] | None = None) -> str:
    return request_text("GET", url, headers)


def post_json(
        url: str,
        payload: dict[str, object],
        headers: dict[str, str] | None = None
) -> dict[str, object]:
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    response = request_json("POST", url, request_headers, body)
    if not isinstance(response, dict):
        raise SystemExit(f"POST {redact_url(url)} returned a non-object JSON payload.")
    return response


def request_json(
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: bytes | None = None
) -> dict[str, object] | list[object]:
    text = request_text(method, url, headers, body)
    return json.loads(text)


def request_text(
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: bytes | None = None
) -> str:
    request_headers = {"User-Agent": "lobby-capture-simulator/0.1"}
    if headers:
        request_headers.update(headers)
    attempts = int_env("SOURCE_FETCH_RETRIES", 3, 1, 8)
    backoff = float_env("SOURCE_FETCH_BACKOFF_SECONDS", 1.0, 0.0, 30.0)
    timeout = float_env("SOURCE_FETCH_TIMEOUT_SECONDS", 30.0, 1.0, 300.0)
    hard_timeout = float_env("SOURCE_FETCH_HARD_TIMEOUT_SECONDS", min(timeout + 5.0, 305.0), 1.0, 600.0)
    for attempt in range(1, attempts + 1):
        try:
            text = fetch_url_text_with_hard_timeout(method, url, request_headers, body, timeout, hard_timeout)
            write_raw_payload(url, text, method, body)
            return text
        except SourceHttpStatus as error:
            if should_retry(error.code, attempt, attempts):
                sleep_before_retry(error, attempt, backoff)
                continue
            detail = error.detail[:500]
            hint = auth_hint(error.code)
            raise SystemExit(f"{method} {redact_url(url)} failed with HTTP {error.code}: {detail}{hint}") from error
        except (URLError, RemoteDisconnected, TimeoutError, ConnectionError, OSError) as error:
            if attempt < attempts:
                sleep_before_retry(None, attempt, backoff)
                continue
            reason = getattr(error, "reason", str(error))
            raise SystemExit(f"{method} {redact_url(url)} failed after {attempts} attempts: {reason}") from error
    raise AssertionError("unreachable")


def fetch_url_text_with_hard_timeout(
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout: float,
        hard_timeout: float,
) -> str:
    """Fetch URL text in a child process so stuck sockets cannot block live snapshots."""
    fd, output_name = tempfile.mkstemp(prefix="lobby-source-fetch-", suffix=".txt")
    os.close(fd)
    output_path = Path(output_name)
    context = multiprocessing_context()
    result_queue = context.Queue()
    process = context.Process(
        target=fetch_url_text_child,
        args=(method, url, headers, body, timeout, output_name, result_queue),
    )
    process.start()
    process.join(hard_timeout)
    if process.is_alive():
        process.terminate()
        process.join(2.0)
        output_path.unlink(missing_ok=True)
        if curl_fallback_enabled(method, body):
            return fetch_url_text_with_curl(method, url, headers, body, timeout, hard_timeout)
        raise TimeoutError(f"source fetch exceeded hard timeout ({hard_timeout:.1f}s)")
    try:
        result = result_queue.get_nowait()
    except queue.Empty as error:
        output_path.unlink(missing_ok=True)
        raise OSError(f"source fetch child exited without a result (exit code {process.exitcode})") from error
    status = result.get("status")
    if status == "ok":
        try:
            return output_path.read_text(encoding="utf-8")
        finally:
            output_path.unlink(missing_ok=True)
    output_path.unlink(missing_ok=True)
    if status == "http":
        raise SourceHttpStatus(int(result.get("code", 0)), str(result.get("detail", "")), result.get("headers", {}))
    reason = str(result.get("reason", result.get("type", "unknown source fetch error")))
    raise OSError(reason)


def curl_fallback_enabled(method: str, body: bytes | None) -> bool:
    setting = os.environ.get("SOURCE_FETCH_CURL_FALLBACK", "1").strip().lower()
    return (
        setting not in {"0", "false", "no", "n"}
        and method.upper() == "GET"
        and body is None
        and shutil.which("curl") is not None
    )


def fetch_url_text_with_curl(
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout: float,
        hard_timeout: float,
) -> str:
    """Fallback for endpoints that hang under urllib but respond to curl."""
    if method.upper() != "GET" or body is not None:
        raise TimeoutError(f"source fetch exceeded hard timeout ({hard_timeout:.1f}s)")
    fd, output_name = tempfile.mkstemp(prefix="lobby-source-curl-", suffix=".txt")
    os.close(fd)
    output_path = Path(output_name)
    command = [
        "curl",
        "-sS",
        "-L",
        "--compressed",
        "--connect-timeout",
        f"{min(timeout, hard_timeout):.1f}",
        "--max-time",
        f"{hard_timeout:.1f}",
        "-o",
        output_name,
        "-w",
        "%{http_code}",
    ]
    for key, value in headers.items():
        command.extend(["-H", f"{key}: {value}"])
    command.append(url)
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=hard_timeout + 2.0,
        )
        status_text = completed.stdout.strip() or "000"
        try:
            status_code = int(status_text[-3:])
        except ValueError:
            status_code = 0
        if completed.returncode != 0:
            detail = completed.stderr.strip().replace(url, redact_url(url))[:500]
            raise OSError(f"curl fallback failed with exit {completed.returncode}: {detail}")
        text = output_path.read_text(encoding="utf-8")
        if status_code >= 400:
            raise SourceHttpStatus(status_code, text[:500], {})
        if status_code == 0:
            raise OSError("curl fallback did not report an HTTP status")
        return text
    except subprocess.TimeoutExpired as error:
        raise TimeoutError(f"curl fallback exceeded hard timeout ({hard_timeout:.1f}s)") from error
    finally:
        output_path.unlink(missing_ok=True)


def multiprocessing_context() -> multiprocessing.context.BaseContext:
    try:
        return multiprocessing.get_context("fork")
    except ValueError:
        return multiprocessing.get_context("spawn")


def fetch_url_text_child(
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout: float,
        output_name: str,
        result_queue: multiprocessing.Queue,
) -> None:
    previous_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        request = Request(url, data=body, headers=headers, method=method)
        with urlopen(request, timeout=timeout) as response:
            data = response.read()
            text = decode_response_text(data, response.headers.get("Content-Encoding", ""))
        Path(output_name).write_text(text, encoding="utf-8")
        result_queue.put({"status": "ok"})
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        result_queue.put({"status": "http", "code": error.code, "detail": detail, "headers": dict(error.headers)})
    except BaseException as error:  # noqa: BLE001 - child reports all source-fetch failures to parent.
        reason = getattr(error, "reason", str(error))
        result_queue.put({"status": "error", "type": type(error).__name__, "reason": str(reason)})
    finally:
        socket.setdefaulttimeout(previous_timeout)


def decode_response_text(data: bytes, content_encoding: str = "") -> str:
    encoding = content_encoding.lower()
    if "gzip" in encoding or data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    elif "deflate" in encoding:
        data = zlib.decompress(data)
    return data.decode("utf-8", errors="replace")


def first_text(record: dict[str, object], *paths: str, default: str = "") -> str:
    for path in paths:
        value = nested(record, path)
        if value not in (None, ""):
            return str(value)
    return default


def nested(record: dict[str, object], path: str) -> object | None:
    if path in record:
        return record.get(path)
    value: object = record
    for part in path.split("."):
        if isinstance(value, list) and part.isdigit():
            index = int(part)
            value = value[index] if index < len(value) else None
        elif isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def money_millions(value: str) -> float:
    amount = raw_money(value)
    return round(amount / 1_000_000.0, 4)


def raw_money(value: str) -> float:
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except ValueError:
        return 0.0


def numeric_value(value: str) -> float:
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0


def disclosure_lag_score(value: str) -> float:
    parsed = parse_date(value)
    if parsed is None:
        return float_env("LDA_DISCLOSURE_VISIBILITY_LAG", 0.32, 0.0, 1.0)
    quarter_end = lda_period_end()
    if quarter_end is None:
        return float_env("LDA_DISCLOSURE_VISIBILITY_LAG", 0.32, 0.0, 1.0)
    days = max(0, (parsed - quarter_end).days)
    return ValuesProxy.clamp(0.10 + (days / 120.0), 0.08, 0.70)


def lda_period_end() -> date | None:
    year_value = os.environ.get("LDA_YEAR")
    period = os.environ.get("LDA_PERIOD", "").lower()
    try:
        year = int(year_value) if year_value else date.today().year
    except ValueError:
        return None
    mapping = {
        "first_quarter": date(year, 3, 31),
        "second_quarter": date(year, 6, 30),
        "third_quarter": date(year, 9, 30),
        "fourth_quarter": date(year, 12, 31),
        "1": date(year, 3, 31),
        "2": date(year, 6, 30),
        "3": date(year, 9, 30),
        "4": date(year, 12, 31),
    }
    return mapping.get(period)


def parse_date(value: str) -> date | None:
    candidates = [value, value[:10], value[:20]]
    for candidate in candidates:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(candidate, fmt).date()
            except ValueError:
                continue
    return None


def int_or_zero(value: str) -> int:
    try:
        return int(float(value))
    except ValueError:
        return 0


def modification_sequence(value: str) -> int:
    if value is None:
        return 0
    text = str(value).strip()
    if text.lower() in {"", "0", "0.0", "none", "null"}:
        return 0
    if text.isdigit():
        return int(text)
    index = len(text) - 1
    while index >= 0 and text[index].isdigit():
        index -= 1
    if index == len(text) - 1:
        return 0
    return int(text[index + 1:])


def price_only_procurement_flag(number_of_offers: str, pricing_type: str, competition_type: str) -> bool:
    offers = numeric_value(number_of_offers)
    single_bid = 0.0 < offers <= 1.0
    pricing_lower = pricing_type.lower()
    competition_lower = competition_type.lower()
    explicit_price_only = any(
        marker in pricing_lower
        for marker in (
            "lowest price",
            "low price",
            "price only",
            "lpta",
        )
    )
    constrained_competition = any(
        marker in competition_lower
        for marker in (
            "sole source",
            "not competed",
            "only one source",
            "single source",
            "single award",
        )
    )
    return single_bid or explicit_price_only or constrained_competition


def bounded_int_env(name: str, default: int, minimum: int, maximum: int) -> str:
    return str(int_env(name, default, minimum, maximum))


def env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def int_env_any(names: tuple[str, ...], default: int, minimum: int, maximum: int) -> int:
    for name in names:
        value = os.environ.get(name, "").strip()
        if not value:
            continue
        try:
            parsed = int(value)
        except ValueError:
            continue
        return max(minimum, min(maximum, parsed))
    return max(minimum, min(maximum, default))


def int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def float_env(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def should_retry(status_code: int, attempt: int, attempts: int) -> bool:
    return attempt < attempts and (status_code == 429 or 500 <= status_code <= 599)


def sleep_before_retry(error: HTTPError | SourceHttpStatus | None, attempt: int, backoff: float) -> None:
    retry_after = error.headers.get("Retry-After") if error is not None else None
    if retry_after is not None:
        try:
            delay = min(30.0, float(retry_after))
        except ValueError:
            delay = backoff * attempt
    else:
        delay = backoff * attempt
    if delay > 0.0:
        time.sleep(delay)


def auth_hint(status_code: int) -> str:
    if status_code in {401, 403}:
        return " Check the relevant API key environment variable and endpoint permissions."
    return ""


def redact_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, "REDACTED") if sensitive_query_key(key) else (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def sensitive_query_key(key: str) -> bool:
    lowered = key.lower()
    return lowered in {"token", "access_token"} or "key" in lowered or "secret" in lowered


def write_raw_payload(url: str, text: str, method: str = "GET", body: bytes | None = None) -> None:
    raw_dir = os.environ.get("SOURCE_RAW_DIR")
    if not raw_dir:
        return
    global RAW_SEQUENCE
    RAW_SEQUENCE += 1
    root = Path(raw_dir)
    root.mkdir(parents=True, exist_ok=True)
    request_identity = method.encode("utf-8") + url.encode("utf-8") + (body or b"")
    digest = hashlib.sha256(request_identity).hexdigest()[:12]
    path = root / f"{RAW_SEQUENCE:04d}-{digest}.json"
    path.write_text(text, encoding="utf-8")
    entry = {"file": path.name, "method": method, "url": redact_url(url)}
    if body:
        entry["requestBodySha256"] = hashlib.sha256(body).hexdigest()
    with (root / "request-manifest.jsonl").open("a", encoding="utf-8") as manifest:
        manifest.write(json.dumps(entry) + "\n")


def write_rows(output: Path, fieldnames: list[str], rows: object, source_name: str = "source API") -> None:
    materialized = list(rows)
    if not materialized:
        raise SystemExit(f"{source_name} returned no rows to normalize. Check filters, date ranges, API credentials, and upstream availability.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: format_value(row[field]) for field in fieldnames})
    print(f"Wrote {output}")


def format_value(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.4f}"
    return value


if __name__ == "__main__":
    sys.exit(main())
