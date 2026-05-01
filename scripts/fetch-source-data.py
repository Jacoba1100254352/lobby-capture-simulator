#!/usr/bin/env python3
"""Fetch source-native public data and normalize it to simulator schemas."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


MODEL_DOMAINS = ("energy", "technology", "finance", "procurement", "democracy")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="kind", required=True)

    lda = subparsers.add_parser("lda", help="Fetch LDA REST filings.")
    lda.add_argument("--output", type=Path, default=Path("data/raw/lda-lobbying.csv"))

    fec = subparsers.add_parser("fec", help="Fetch FEC OpenFEC schedule A records.")
    fec.add_argument("--output", type=Path, default=Path("data/raw/fec-campaign-finance.csv"))

    regulatory = subparsers.add_parser("regulatory", help="Fetch Regulations.gov or Federal Register records.")
    regulatory.add_argument("--output", type=Path, default=Path("data/raw/regulatory-dockets.csv"))

    args = parser.parse_args()
    if args.kind == "lda":
        return fetch_lda(args.output)
    if args.kind == "fec":
        return fetch_fec(args.output)
    if args.kind == "regulatory":
        return fetch_regulatory(args.output)
    raise AssertionError(args.kind)


def fetch_lda(output: Path) -> int:
    base = os.environ.get("LDA_API_BASE", "https://lda.senate.gov/api/v1").rstrip("/")
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

    grouped: dict[tuple[str, str, str], dict[str, float | str]] = {}
    for record in records:
        client = first_text(record, "client.name", "client_name", "client", default="Unknown client")
        registrant = first_text(record, "registrant.name", "registrant_name", "registrant", default="Unknown registrant")
        amount = money_millions(first_text(record, "income", "expenses", "amount", default="0"))
        disclosure_lag = disclosure_lag_score(first_text(record, "filing_date", "dt_posted", "filing_dt", default=""))
        covered_share = 0.20 + (0.10 if first_text(record, "lobbyists", "covered_position", default="") else 0.0)
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

    write_rows(output, ["client", "registrant", "issueDomain", "amount", "disclosureLag", "coveredOfficialShare"], grouped.values())
    return 0


def fetch_fec(output: Path) -> int:
    api_key = os.environ.get("FEC_API_KEY")
    if not api_key:
        raise SystemExit("Set FEC_API_KEY before running ./scripts/fetch-fec.sh --live without FEC_LIVE_CSV or FEC_LIVE_URL.")
    base = os.environ.get("FEC_API_BASE", "https://api.open.fec.gov/v1").rstrip("/")
    params = {
        "api_key": api_key,
        "per_page": os.environ.get("FEC_PAGE_SIZE", "50"),
        "sort": "-contribution_receipt_amount",
        "two_year_transaction_period": os.environ.get("FEC_CYCLE", "2024"),
    }
    if os.environ.get("FEC_COMMITTEE_ID"):
        params["committee_id"] = os.environ["FEC_COMMITTEE_ID"]
    payload = get_json(f"{base}/schedules/schedule_a/?{urlencode(params)}")

    rows = []
    for record in payload.get("results", []):
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
            }
        )

    write_rows(output, ["source", "recipient", "issueDomain", "amount", "flowType", "traceability", "largeDonorShare"], rows)
    return 0


def fetch_regulatory(output: Path) -> int:
    source = os.environ.get("REGULATORY_SOURCE", "regulations").lower()
    if source == "federal-register":
        rows = fetch_federal_register_rows()
    else:
        rows = fetch_regulations_gov_rows()
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
    )
    return 0


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
    issues = record.get("issues") or record.get("issue_codes") or []
    if isinstance(issues, dict):
        issues = [issues]
    domains = []
    for issue in issues if isinstance(issues, list) else []:
        text = json.dumps(issue) if not isinstance(issue, str) else issue
        domains.append(classify_domain(text))
    if not domains:
        domains.append(classify_domain(json.dumps(record)))
    return sorted(set(domains))


def classify_domain(text: str) -> str:
    normalized = text.lower()
    rules = {
        "energy": ("energy", "oil", "gas", "electric", "climate", "pipeline", "utility"),
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


def get_json(url: str, headers: dict[str, str] | None = None) -> dict[str, object] | list[object]:
    request_headers = {"User-Agent": "lobby-capture-simulator/0.1"}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"GET {redact_url(url)} failed with HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise SystemExit(f"GET {redact_url(url)} failed: {error.reason}") from error


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


def disclosure_lag_score(value: str) -> float:
    parsed = parse_date(value)
    if parsed is None:
        return 0.45
    days = max(0, (date.today() - parsed).days)
    return min(1.0, 0.20 + (days / 365.0))


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
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return str(max(minimum, min(maximum, value)))


def redact_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, "REDACTED") if "key" in key.lower() else (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def write_rows(output: Path, fieldnames: list[str], rows: object) -> None:
    materialized = list(rows)
    if not materialized:
        raise SystemExit("Source API returned no rows to normalize.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
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
