#!/usr/bin/env python3
"""Fetch source-native public data and normalize it to simulator schemas."""

from __future__ import annotations

import argparse
import csv
import hashlib
from io import StringIO
import json
import os
import re
import sys
import time
import tempfile
import zipfile
from http.client import RemoteDisconnected
from datetime import date, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


MODEL_DOMAINS = ("energy", "technology", "finance", "procurement", "democracy")
RAW_SEQUENCE = 0


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

    usaspending = subparsers.add_parser("usaspending", help="Fetch USAspending award records.")
    usaspending.add_argument("--output", type=Path, default=Path("data/raw/usaspending-awards.csv"))

    usaspending_actions = subparsers.add_parser("usaspending-actions", help="Fetch USAspending transaction/action rows for procurement modification diagnostics.")
    usaspending_actions.add_argument("--output", type=Path, default=Path("data/raw/usaspending-procurement-actions.csv"))

    nyc_public_financing = subparsers.add_parser("nyc-public-financing", help="Fetch NYC CFB public-funds payments.")
    nyc_public_financing.add_argument("--output", type=Path, default=Path("data/raw/public-financing.csv"))

    nyc_intermediaries = subparsers.add_parser("nyc-intermediaries", help="Fetch NYC CFB intermediary fundraising rows.")
    nyc_intermediaries.add_argument("--output", type=Path, default=Path("data/raw/intermediaries.csv"))

    irs_eo_bmf = subparsers.add_parser("irs-eo-bmf", help="Fetch IRS EO BMF nonprofit and association capacity rows.")
    irs_eo_bmf.add_argument("--output", type=Path, default=Path("data/raw/intermediaries.csv"))

    irs_dark_money_capacity = subparsers.add_parser("irs-dark-money-capacity", help="Fetch IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows.")
    irs_dark_money_capacity.add_argument("--output", type=Path, default=Path("data/raw/dark-money.csv"))

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
    if args.kind == "usaspending":
        return fetch_usaspending(args.output)
    if args.kind == "usaspending-actions":
        return fetch_usaspending_actions(args.output)
    if args.kind == "nyc-public-financing":
        return fetch_nyc_public_financing(args.output)
    if args.kind == "nyc-intermediaries":
        return fetch_nyc_intermediaries(args.output)
    if args.kind == "irs-eo-bmf":
        return fetch_irs_eo_bmf(args.output)
    if args.kind == "irs-dark-money-capacity":
        return fetch_irs_dark_money_capacity(args.output)
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
    max_pages = int_env("REVOLVING_DOOR_LDA_MAX_PAGES", 5, 1, 50)
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


def fetch_usaspending(output: Path) -> int:
    base = os.environ.get("USASPENDING_API_BASE", "https://api.usaspending.gov/api/v2").rstrip("/")
    limit = int_env("USASPENDING_PAGE_SIZE", 100, 1, 100)
    max_pages = int_env("USASPENDING_MAX_PAGES", 2, 1, 20)
    start_date, end_date = usaspending_time_period()
    rows = []
    for agency_filter in usaspending_agency_filters():
        for page in range(1, max_pages + 1):
            payload = {
                "filters": {
                    "time_period": [{"start_date": start_date, "end_date": end_date}],
                    "agencies": [agency_filter],
                    "award_type_codes": split_csv_env("USASPENDING_AWARD_TYPE_CODES", "A,B,C,D"),
                },
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
    limit = int_env("USASPENDING_ACTION_TRANSACTION_PAGE_SIZE", int_env("USASPENDING_ACTION_AWARD_PAGE_SIZE", int_env("USASPENDING_PAGE_SIZE", 50, 1, 100), 1, 100), 1, 100)
    max_pages = int_env("USASPENDING_ACTION_TRANSACTION_MAX_PAGES", int_env("USASPENDING_ACTION_AWARD_MAX_PAGES", int_env("USASPENDING_MAX_PAGES", 1, 1, 20), 1, 20), 1, 20)
    periods = usaspending_action_periods()
    rows: list[dict[str, object]] = []
    for agency_filter in usaspending_agency_filters():
        for start_date, end_date in periods:
            for page in range(1, max_pages + 1):
                payload = {
                    "filters": {
                        "time_period": [{"start_date": start_date, "end_date": end_date}],
                        "agencies": [agency_filter],
                        "award_type_codes": split_csv_env("USASPENDING_AWARD_TYPE_CODES", "A,B,C,D"),
                    },
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
                    "sort": os.environ.get("USASPENDING_ACTION_TRANSACTION_SORT", "Action Date"),
                    "order": os.environ.get("USASPENDING_ACTION_TRANSACTION_ORDER", "desc"),
                }
                response = post_json(f"{base}/search/spending_by_transaction/", payload)
                rows.extend(normalize_usaspending_direct_transaction_records(response.get("results", [])))
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
    limit = int_env("USASPENDING_ACTION_AWARD_PAGE_SIZE", int_env("USASPENDING_PAGE_SIZE", 50, 1, 100), 1, 100)
    max_pages = int_env("USASPENDING_ACTION_AWARD_MAX_PAGES", int_env("USASPENDING_MAX_PAGES", 1, 1, 20), 1, 20)
    start_date, end_date = usaspending_time_period()
    rows: list[dict[str, object]] = []
    for agency_filter in usaspending_agency_filters():
        for page in range(1, max_pages + 1):
            payload = {
                "filters": {
                    "time_period": [{"start_date": start_date, "end_date": end_date}],
                    "agencies": [agency_filter],
                    "award_type_codes": split_csv_env("USASPENDING_AWARD_TYPE_CODES", "A,B,C,D"),
                },
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


def usaspending_agency_filters() -> list[dict[str, str]]:
    agency_type = os.environ.get("USASPENDING_AGENCY_TYPE", "awarding")
    agency_tier = os.environ.get("USASPENDING_AGENCY_TIER", "toptier")
    agencies = split_csv_env("USASPENDING_AGENCIES", "")
    if not agencies:
        agencies = [os.environ.get("USASPENDING_AGENCY", "Environmental Protection Agency")]
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
    bucket = os.environ.get("USASPENDING_ACTION_PERIOD_BUCKETS", "").strip().lower()
    if bucket not in {"month", "monthly"}:
        return [(start_text, end_text)]
    start = parse_date(start_text)
    end = parse_date(end_text)
    if start is None or end is None:
        return [(start_text, end_text)]
    periods: list[tuple[str, str]] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        next_month = date(cursor.year + (1 if cursor.month == 12 else 0), 1 if cursor.month == 12 else cursor.month + 1, 1)
        period_start = max(cursor, start)
        period_end = min(date.fromordinal(next_month.toordinal() - 1), end)
        periods.append((period_start.isoformat(), period_end.isoformat()))
        cursor = next_month
    return periods


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
        single_bid = numeric_value(number_of_offers) <= 1.0 and numeric_value(number_of_offers) > 0.0
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
                "priceOnlyAward": str(single_bid or "price" in pricing_type.lower() or "sole source" in competition_type.lower()).lower(),
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
    single_bid = numeric_value(number_of_offers) <= 1.0 and numeric_value(number_of_offers) > 0.0
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
                "priceOnlyAward": str(single_bid or "price" in pricing_type.lower() or "sole source" in competition_type.lower()).lower(),
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
    request = Request(url, data=body, headers=request_headers, method=method)
    attempts = int_env("SOURCE_FETCH_RETRIES", 3, 1, 8)
    backoff = float_env("SOURCE_FETCH_BACKOFF_SECONDS", 1.0, 0.0, 30.0)
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=30) as response:
                text = response.read().decode("utf-8")
                write_raw_payload(url, text, method, body)
                return text
        except HTTPError as error:
            if should_retry(error.code, attempt, attempts):
                sleep_before_retry(error, attempt, backoff)
                continue
            detail = error.read().decode("utf-8", errors="replace")[:500]
            hint = auth_hint(error.code)
            raise SystemExit(f"{method} {redact_url(url)} failed with HTTP {error.code}: {detail}{hint}") from error
        except (URLError, RemoteDisconnected, TimeoutError, ConnectionError, OSError) as error:
            if attempt < attempts:
                sleep_before_retry(None, attempt, backoff)
                continue
            reason = getattr(error, "reason", str(error))
            raise SystemExit(f"{method} {redact_url(url)} failed after {attempts} attempts: {reason}") from error
    raise AssertionError("unreachable")


def first_text(record: dict[str, object], *paths: str, default: str = "") -> str:
    for path in paths:
        value = nested(record, path)
        if value not in (None, ""):
            return str(value)
    return default


def nested(record: dict[str, object], path: str) -> object | None:
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


def bounded_int_env(name: str, default: int, minimum: int, maximum: int) -> str:
    return str(int_env(name, default, minimum, maximum))


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


def sleep_before_retry(error: HTTPError | None, attempt: int, backoff: float) -> None:
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
            (key, "REDACTED") if "key" in key.lower() else (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


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
