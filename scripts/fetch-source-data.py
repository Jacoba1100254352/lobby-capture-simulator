#!/usr/bin/env python3
"""Fetch source-native public data and normalize it to simulator schemas."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
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

    write_rows(output, FEC_FIELDS, rows, "OpenFEC campaign finance and independent-expenditure records")
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
    for page in range(1, max_pages + 1):
        payload = {
            "filters": {
                "time_period": [{"start_date": start_date, "end_date": end_date}],
                "agencies": [
                    {
                        "type": os.environ.get("USASPENDING_AGENCY_TYPE", "awarding"),
                        "tier": os.environ.get("USASPENDING_AGENCY_TIER", "toptier"),
                        "name": os.environ.get("USASPENDING_AGENCY", "Environmental Protection Agency"),
                    }
                ],
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
        [
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
        ],
        rows,
        "USAspending awards",
    )
    return 0


def usaspending_time_period() -> tuple[str, str]:
    if os.environ.get("USASPENDING_DATE_FROM") and os.environ.get("USASPENDING_DATE_TO"):
        return os.environ["USASPENDING_DATE_FROM"], os.environ["USASPENDING_DATE_TO"]
    fiscal_year = int_env("USASPENDING_FISCAL_YEAR", 2024, 2008, 2100)
    return f"{fiscal_year - 1}-10-01", f"{fiscal_year}-09-30"


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
        modification_number = first_text(transaction, "modificationNumber", default=first_text(record, "Modification Number", "modification_number", default="0"))
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
        modified = modification_number.strip() not in {"", "0", "0.0", "none", "None"}
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
                "actionDate": first_text(transaction, "actionDate", default=first_text(detail, "date_signed", default=first_text(record, "Action Date", "action_date", default=""))),
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
        ],
        "page": 1,
        "limit": int_env("USASPENDING_TRANSACTION_LIMIT", 20, 1, 100),
        "sort": "Action Date",
        "order": "desc",
    }
    try:
        response = post_json(f"{base}/search/spending_by_transaction/", payload)
    except SystemExit:
        if os.environ.get("USASPENDING_STRICT_ENRICHMENT", "0") == "1":
            raise
        return {}
    rows = response.get("results", []) if isinstance(response, dict) else []
    mods = [first_text(row, "Mod", "mod", default="") for row in rows if isinstance(row, dict)]
    nonzero_mods = [mod for mod in mods if mod.strip() not in {"", "0", "0.0", "none", "None"}]
    return {
        "modificationNumber": nonzero_mods[0] if nonzero_mods else (mods[0] if mods else "0"),
        "actionDate": first_text(rows[0], "Action Date", "action_date", default="") if rows else "",
    }


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
        if any(keyword in normalized for keyword in keywords):
            return domain
    return os.environ.get("DEFAULT_ISSUE_DOMAIN", "democracy")


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
    activity = parse_date(first_text(record, "expenditure_date", "dissemination_date", "contribution_receipt_date", default=""))
    if filed is None or activity is None:
        return float_env("FEC_DISCLOSURE_VISIBILITY_LAG", 0.28, 0.0, 1.0)
    days = max(0, (filed - activity).days)
    return ValuesProxy.clamp(0.08 + (days / 120.0), 0.04, 0.70)


def get_json(url: str, headers: dict[str, str] | None = None) -> dict[str, object] | list[object]:
    return request_json("GET", url, headers)


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
                return json.loads(text)
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
    try:
        amount = float(value.replace("$", "").replace(",", ""))
    except ValueError:
        return 0.0
    return round(amount / 1_000_000.0 if amount > 1_000 else amount, 4)


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
