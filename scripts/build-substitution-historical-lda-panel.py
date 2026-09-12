#!/usr/bin/env python3
"""Build an optional historical LDA panel for the HLOGA substitution product.

This is a live source-acquisition helper. It queries the official LDA API for
reviewed canonical actors by exact normalized client name, keeps observed
filing rows (2007-2008 by default), and writes a local panel that the first-wave promotion
script can consume. The output is source evidence for a visible-lobbying
pre/post surface; it is not a comparison design or a causal estimate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRST_WAVE = ROOT / "data" / "calibration" / "first-wave"
REPORTS = ROOT / "reports"
PANEL_PATH = FIRST_WAVE / "substitution-historical-lda-panel.csv"
REPORT_CSV = REPORTS / "substitution-historical-lda-panel.csv"
REPORT_MD = REPORTS / "substitution-historical-lda-panel.md"
DEFAULT_REVIEW_DATE = "2026-07-24"
DEFAULT_YEARS = ("2007", "2008")
LDA_API_BASE = "https://lda.gov/api/v1"
REVIEWER = "codex-source-audit"
REFORM_EVENT_ID = "hloga-2007-federal-lobbying-disclosure"
TREATMENT_START = "2007-09-14"

PRIORITY_NAMES = (
    "AMERICAN PETROLEUM INSTITUTE",
    "AMERICAN BANKERS ASSOCIATION",
    "AMERICAN GAS ASSOCIATION",
    "AMERICAN ASSOCIATION FOR JUSTICE",
    "AMERICAN BENEFITS COUNCIL",
    "AMERICAN PUBLIC GAS ASSOCIATION",
    "ADVANCED MEDICAL TECHNOLOGY ASSOCIATION",
    "ADULT VACCINE ACCESS COALITION",
)

LIKELY_LOBBYING_NAME_TERMS = (
    "ASSOCIATION",
    "COALITION",
    "COUNCIL",
    "FEDERATION",
    "INSTITUTE",
    "SOCIETY",
)

PERIOD_RANGES = {
    "first_quarter": ("{year}-01-01", "{year}-03-31"),
    "second_quarter": ("{year}-04-01", "{year}-06-30"),
    "third_quarter": ("{year}-07-01", "{year}-09-30"),
    "fourth_quarter": ("{year}-10-01", "{year}-12-31"),
    "mid_year": ("{year}-01-01", "{year}-06-30"),
    "year_end": ("{year}-07-01", "{year}-12-31"),
}

PANEL_FIELDS = [
    "canonicalActorId",
    "primaryName",
    "ldaClientId",
    "ldaClientApiUrl",
    "filingUuid",
    "filingYear",
    "filingPeriod",
    "filingType",
    "filingDocumentUrl",
    "dtPosted",
    "clientName",
    "registrantName",
    "issueCode",
    "ldaIssueCode",
    "ldaIssueDisplay",
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
    "yearsQueried",
    "apiResultCount",
    "exactClientMatchedFilings",
    "panelRows",
    "preRows",
    "postRows",
    "straddleRows",
    "clientIds",
    "sourceUrls",
    "nextAction",
]

# One source row per filing, separate from the repeated issue rows. API nulls
# remain blank; source zeros are not adjudicated exact zeros or below-threshold
# intervals until the original form is reviewed.
METADATA_FIELDS = [
    "canonicalActorId", "primaryName", "filingUuid", "filingYear", "filingPeriod",
    "filingType", "periodStart", "periodEnd", "clientName", "clientApiId",
    "clientRelationshipId", "registrantName", "registrantApiId", "incomeDollars",
    "expensesDollars", "expensesMethod", "expensesMethodDisplay", "amountKind",
    "sameClientRegistrantName", "dtPosted", "terminationDate", "filingDocumentUrl",
    "filingApiUrl", "aliasReviewId", "retrievedDate", "sourceFingerprint",
]
ALIAS_REQUIRED = {
    "aliasReviewId", "canonicalActorId", "aliasName", "clientApiId", "registrantApiId",
    "startYear", "endYear", "sourceUrl", "pdfSha256", "pagesReviewed", "reviewer",
    "reviewDate", "rationale", "independentReviewStatus",
}


def read_alias_reviews(path: Path, actors: list[dict[str, str]]) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("Alias review file is missing")
    return validate_alias_reviews(read_csv(path), actors)


def validate_alias_reviews(reviews: list[dict[str, str]], actors: list[dict[str, str]]) -> list[dict[str, str]]:
    actor_ids = {row["canonicalActorId"] for row in actors}
    seen = set()
    for row in reviews:
        if any(not row.get(field) for field in ALIAS_REQUIRED):
            raise ValueError("Incomplete LDA alias review")
        key = (row["canonicalActorId"], normalize_name(row["aliasName"]), row["clientApiId"], row["registrantApiId"])
        if (key in seen or row["canonicalActorId"] not in actor_ids
                or not row["clientApiId"].isdigit() or not row["registrantApiId"].isdigit()
                or not re.fullmatch(r"[0-9a-f]{64}", row["pdfSha256"])
                or not re.fullmatch(r"\d{4}", row["startYear"])
                or not re.fullmatch(r"\d{4}", row["endYear"])
                or row["endYear"] < row["startYear"]
                or row["independentReviewStatus"] != "pending"):
            raise ValueError("Invalid, duplicate or off-cohort LDA alias review")
        datetime.fromisoformat(row["reviewDate"])
        seen.add(key)
    if len({row["aliasReviewId"] for row in reviews}) != len(reviews):
        raise ValueError("Duplicate LDA alias review identifier")
    return reviews


def source_text(value: object) -> str:
    return "" if value is None else str(value)


def dollar_value(value: object) -> str:
    if value is None or value == "":
        return ""
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid LDA source amount") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("Invalid LDA source amount")
    # Preserve source decimal precision, rather than manufacturing cents.
    return str(value)


def metadata_fingerprint(row: dict[str, str]) -> str:
    fields = set(METADATA_FIELDS) - {"sourceFingerprint", "retrievedDate", "aliasReviewId"}
    payload = json.dumps({key: row[key] for key in sorted(fields)}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def measurement_amount(row: dict[str, str]) -> str:
    """Do not combine income and expense reports or replace missing with zero."""
    field = {"income": "incomeDollars", "expenses": "expensesDollars"}.get(row["amountKind"])
    if field is None:
        return ""
    return f"{Decimal(dollar_value(row[field])) / Decimal(1_000_000):.8f}"


def filing_metadata(actor: dict[str, str], record: dict[str, object], retrieved_date: str, alias_id: str = "") -> dict[str, str]:
    client, registrant = record.get("client") or {}, record.get("registrant") or {}
    year, period = str(record["filing_year"]), str(record["filing_period"])
    start, end = period_range(year, period)
    income, expenses = dollar_value(record.get("income")), dollar_value(record.get("expenses"))
    uuid = str(record["filing_uuid"])
    row = {
        "canonicalActorId": actor["canonicalActorId"], "primaryName": actor["primaryName"],
        "filingUuid": uuid, "filingYear": year, "filingPeriod": period,
        "filingType": str(record["filing_type"]), "periodStart": start, "periodEnd": end,
        "clientName": source_text(client.get("name")), "clientApiId": source_text(client.get("id")),
        "clientRelationshipId": source_text(client.get("client_id")),
        "registrantName": source_text(registrant.get("name")), "registrantApiId": source_text(registrant.get("id")),
        "incomeDollars": income, "expensesDollars": expenses,
        "expensesMethod": source_text(record.get("expenses_method")),
        "expensesMethodDisplay": source_text(record.get("expenses_method_display")),
        "amountKind": "both" if income and expenses else "income" if income else "expenses" if expenses else "neither",
        "sameClientRegistrantName": str(bool(client.get("name")) and normalize_name(client.get("name", "")) == normalize_name(registrant.get("name", ""))).lower(),
        "dtPosted": source_text(record.get("dt_posted")), "terminationDate": source_text(record.get("termination_date")),
        "filingDocumentUrl": source_text(record.get("filing_document_url")),
        "filingApiUrl": f"{LDA_API_BASE}/filings/{uuid}/", "aliasReviewId": alias_id,
        "retrievedDate": retrieved_date,
    }
    row["sourceFingerprint"] = metadata_fingerprint(row)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-wave", type=Path, default=FIRST_WAVE)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--output", type=Path, default=PANEL_PATH)
    parser.add_argument("--max-actors", type=int, default=20)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--max-pages-per-actor-year", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--years", nargs="+", default=list(DEFAULT_YEARS))
    parser.add_argument("--design-candidate", action="store_true", help="Leave reform exposure unassigned for a successor study.")
    parser.add_argument("--alias-reviews", type=Path, help="Reviewed exact-name and registration-ID alias allowlist; successor design only.")
    parser.add_argument("--metadata-output", type=Path, help="Optional filing-grain source-measurement CSV; successor design only.")
    parser.add_argument("--response-cache", type=Path, help="Local public-response cache for same-UTC-day resumable acquisition; keep outside tracked files.")
    parser.add_argument(
        "--review-date",
        default=os.environ.get("SUBSTITUTION_HISTORICAL_LDA_REVIEW_DATE", DEFAULT_REVIEW_DATE),
    )
    args = parser.parse_args()

    first_wave = resolve(args.first_wave)
    reports = resolve(args.reports)
    output = resolve(args.output)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    actors = select_actors(read_csv(first_wave / "canonical-actor-identifiers.csv"), args.max_actors)
    if (args.alias_reviews or args.metadata_output) and not args.design_candidate:
        parser.error("Alias and measurement acquisition requires --design-candidate")
    if args.alias_reviews and not args.metadata_output:
        parser.error("Alias acquisition requires --metadata-output to retain registration and measurement provenance")
    aliases = read_alias_reviews(resolve(args.alias_reviews), actors) if args.alias_reviews else []
    metadata_rows: list[dict[str, str]] = []

    panel_rows: list[dict[str, str]] = []
    report_rows: list[dict[str, str]] = []
    for actor in actors:
        rows, summary = fetch_actor_rows(
            actor,
            args.years,
            page_size=args.page_size,
            max_pages=args.max_pages_per_actor_year,
            timeout=args.timeout,
            review_date=args.review_date,
            generated_at=generated_at,
            aliases=aliases,
            metadata_rows=metadata_rows if args.metadata_output else None,
            response_cache=resolve(args.response_cache) if args.response_cache else None,
        )
        panel_rows.extend(rows)
        report_rows.append(summary)

    if args.design_candidate:
        mark_design_candidates(panel_rows)
    if len({row["filingUuid"] for row in metadata_rows}) != len(metadata_rows):
        raise ValueError("A filing was assigned to multiple canonical actors")
    if args.metadata_output:
        metadata_by_uuid = {row["filingUuid"]: row for row in metadata_rows}
        for row in panel_rows:
            row["activityAmount"] = measurement_amount(metadata_by_uuid[row["filingUuid"]])

    panel_rows.sort(key=lambda row: (
        row["canonicalActorId"],
        row["periodStart"],
        row["filingUuid"],
        row["issueCode"],
    ))
    output.parent.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    write_csv(output, panel_rows, PANEL_FIELDS)
    if args.metadata_output:
        metadata_output = resolve(args.metadata_output)
        metadata_output.parent.mkdir(parents=True, exist_ok=True)
        metadata_rows.sort(key=lambda row: (row["canonicalActorId"], row["periodStart"], row["filingUuid"]))
        write_csv(metadata_output, metadata_rows, METADATA_FIELDS)
        print(f"Wrote {metadata_output}")
    write_csv(reports / REPORT_CSV.name, report_rows, REPORT_FIELDS)
    write_markdown(reports / REPORT_MD.name, panel_rows, report_rows, generated_at)
    print(f"Wrote {output}")
    print(f"Wrote {reports / REPORT_CSV.name}")
    print(f"Wrote {reports / REPORT_MD.name}")
    return 0


def mark_design_candidates(rows: list[dict[str, str]]) -> None:
    for row in rows:
        row["exposureGroup"] = "unassigned_design_candidate"
        row["notes"] = (
            "official LDA API filing row matched by exact normalized client name or an explicit reviewed registration alias; "
            "successor-design acquisition only; treatment/control exposure unassigned; "
            "filing versions, source timestamps, reporting cadence, and cross-source "
            "actor links require review before estimation"
        )


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def select_actors(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    by_name = {normalize_name(row.get("primaryName", "")): row for row in rows}
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    for name in PRIORITY_NAMES:
        key = normalize_name(name)
        if key in by_name and key not in seen:
            selected.append(by_name[key])
            seen.add(key)
    likely = [
        row for row in rows
        if any(term in row.get("primaryName", "").upper() for term in LIKELY_LOBBYING_NAME_TERMS)
    ]
    for row in sorted(likely, key=lambda item: item.get("primaryName", "")):
        key = normalize_name(row.get("primaryName", ""))
        if key and key not in seen:
            selected.append(row)
            seen.add(key)
        if len(selected) >= limit:
            return selected
    for row in sorted(rows, key=lambda item: item.get("primaryName", "")):
        key = normalize_name(row.get("primaryName", ""))
        if key and key not in seen:
            selected.append(row)
            seen.add(key)
        if len(selected) >= limit:
            break
    return selected


def fetch_actor_rows(
    actor: dict[str, str],
    years: list[str],
    *,
    page_size: int,
    max_pages: int,
    timeout: float,
    review_date: str,
    generated_at: str,
    aliases: list[dict[str, str]] | None = None,
    metadata_rows: list[dict[str, str]] | None = None,
    response_cache: Path | None = None,
) -> tuple[list[dict[str, str]], dict[str, str]]:
    actor_name = actor.get("primaryName", "")
    api_result_count = 0
    matched_filings: dict[str, dict[str, object]] = {}
    source_urls: set[str] = set()
    matched_aliases: dict[str, str] = {}
    queries = [(year, actor_name, None) for year in years]
    for alias in aliases or []:
        if alias["canonicalActorId"] == actor["canonicalActorId"]:
            queries.extend((year, alias["aliasName"], alias) for year in years if alias["startYear"] <= year <= alias["endYear"])
    for year, query_name, alias in queries:
        url = api_url({
            "client_name": query_name,
            "filing_year": year,
            "page_size": str(page_size),
        })
        query_ids: set[str] = set()
        expected_count = None
        for page_index in range(max_pages):
            payload, error = cached_fetch_json(url, timeout, response_cache, generated_at[:10])
            if payload is None:
                raise RuntimeError("Incomplete LDA acquisition for " + actor_name
                    + "; refusing partial source rows after request failure: " + error)
            if (not isinstance(payload, dict) or not isinstance(payload.get("results"), list)
                    or not isinstance(payload.get("count"), int) or payload["count"] < 0
                    or "next" not in payload):
                raise ValueError("Malformed LDA source response")
            if page_index == 0:
                expected_count = payload["count"]
                api_result_count += expected_count
            elif payload["count"] != expected_count:
                raise ValueError("LDA query population changed during pagination")
            for record in payload["results"]:
                uuid = record.get("filing_uuid") if isinstance(record, dict) else None
                if not uuid or uuid in query_ids:
                    raise ValueError("Missing or repeated UUID within an LDA query")
                query_ids.add(uuid)
                client = record.get("client") if isinstance(record.get("client"), dict) else {}
                client_name = str(client.get("name", ""))
                if normalize_name(client_name) != normalize_name(query_name):
                    continue
                registrant = record.get("registrant") or {}
                if alias and (str(client.get("id", "")) != alias["clientApiId"]
                        or str(registrant.get("id", "")) != alias["registrantApiId"]):
                    continue
                if str(record.get("filing_year", "")) != year:
                    raise ValueError("Off-year LDA source response")
                filing_uuid = str(record.get("filing_uuid", ""))
                if filing_uuid:
                    if filing_uuid in matched_filings and matched_filings[filing_uuid] != record:
                        raise ValueError("Conflicting LDA source versions for one UUID")
                    matched_filings[filing_uuid] = record
                    if alias:
                        matched_aliases[filing_uuid] = alias["aliasReviewId"]
                    if record.get("filing_document_url"):
                        source_urls.add(str(record["filing_document_url"]))
            next_url = payload.get("next")
            if not next_url:
                if len(query_ids) != expected_count:
                    raise ValueError("Incomplete LDA source result count")
                break
            if urllib.parse.urlsplit(str(next_url))[:2] != urllib.parse.urlsplit(url)[:2]:
                raise ValueError("Off-origin LDA pagination URL")
            url = str(next_url)
        else:
            raise RuntimeError("Incomplete LDA acquisition for " + actor_name
                + "; refusing partial source rows after pagination limit")

    panel_rows: list[dict[str, str]] = []
    for record in matched_filings.values():
        rows = panel_rows_for_record(actor, record, review_date)
        alias_id = matched_aliases.get(str(record["filing_uuid"]), "")
        if alias_id:
            for row in rows:
                row["reviewStatus"] = "reviewed_alias_registration_source_row"
                row["evidenceRule"] = "reviewed-exact-alias-and-registration-ids:" + alias_id
        panel_rows.extend(rows)
        if metadata_rows is not None:
            metadata_rows.append(filing_metadata(actor, record, generated_at[:10], alias_id))
    pre_rows, post_rows, straddle_rows = coverage_counts(panel_rows)
    status = "prepost_source_rows" if pre_rows and post_rows else "post_only_source_rows" if post_rows else "pre_only_source_rows" if pre_rows else "no_exact_client_rows"
    client_ids = sorted({
        str((record.get("client") or {}).get("client_id", ""))
        for record in matched_filings.values()
        if isinstance(record.get("client"), dict) and (record.get("client") or {}).get("client_id") is not None
    })
    summary = {
        "generatedAt": generated_at,
        "canonicalActorId": actor.get("canonicalActorId", ""),
        "primaryName": actor_name,
        "status": status,
        "yearsQueried": "; ".join(years),
        "apiResultCount": str(api_result_count),
        "exactClientMatchedFilings": str(len(matched_filings)),
        "panelRows": str(len(panel_rows)),
        "preRows": str(pre_rows),
        "postRows": str(post_rows),
        "straddleRows": str(straddle_rows),
        "clientIds": "; ".join(client_ids),
        "sourceUrls": "; ".join(sorted(source_urls)[:5]),
        "nextAction": summary_next_action(status),
    }
    return panel_rows, summary


def panel_rows_for_record(actor: dict[str, str], record: dict[str, object], review_date: str) -> list[dict[str, str]]:
    year = str(record.get("filing_year", ""))
    period = str(record.get("filing_period", ""))
    period_start, period_end = period_range(year, period)
    client = record.get("client") if isinstance(record.get("client"), dict) else {}
    registrant = record.get("registrant") if isinstance(record.get("registrant"), dict) else {}
    activities = record.get("lobbying_activities") if isinstance(record.get("lobbying_activities"), list) else []
    if not activities:
        activities = [{"general_issue_code": "UNS", "general_issue_code_display": "Unspecified"}]
    amount = money_millions(record.get("income") or record.get("expenses") or "")
    filing_uuid = str(record.get("filing_uuid", ""))
    rows = []
    for index, activity in enumerate(activities, start=1):
        if not isinstance(activity, dict):
            continue
        lda_issue_code = str(activity.get("general_issue_code") or "UNS")
        issue_code = "lda-" + slug(lda_issue_code or "unspecified")
        rows.append({
            "canonicalActorId": actor.get("canonicalActorId", ""),
            "primaryName": actor.get("primaryName", ""),
            "ldaClientId": str(client.get("client_id", "")),
            "ldaClientApiUrl": str(client.get("url", "")),
            "filingUuid": filing_uuid,
            "filingYear": year,
            "filingPeriod": period,
            "filingType": str(record.get("filing_type", "")),
            "filingDocumentUrl": str(record.get("filing_document_url", "")),
            "dtPosted": str(record.get("dt_posted", "")),
            "clientName": str(client.get("name", "")),
            "registrantName": str(registrant.get("name", "")),
            "issueCode": issue_code,
            "ldaIssueCode": lda_issue_code,
            "ldaIssueDisplay": str(activity.get("general_issue_code_display", "")),
            "periodStart": period_start,
            "periodEnd": period_end,
            "venue": "visible_lobbying",
            "activityType": "visible_lobbying_filing",
            "activityMeasure": "1.0000",
            "activityAmount": f"{amount:.4f}",
            "sourceSystem": "Official LDA API",
            "sourceRecordId": f"{filing_uuid}|{issue_code}|{index}",
            "exposureGroup": "treated_hloga_lda_client",
            "reformEventId": REFORM_EVENT_ID,
            "activityUnits": "filing_count; amount_millions",
            "jurisdiction": "United States federal",
            "matchConfidence": "0.8000",
            "reviewStatus": "reviewed_exact_lda_client_name_source_row",
            "evidenceRule": "exact-normalized-client-name-match-to-reviewed-canonical-actor",
            "reviewer": REVIEWER,
            "reviewDate": review_date,
            "sourceUrl": str(record.get("filing_document_url", "")),
            "notes": (
                "official LDA API filing row matched by exact normalized client name "
                "to the reviewed canonical actor; usable as treated visible-lobbying "
                "pre/post source surface only; stable cross-source LDA client-ID "
                "promotion and comparison-group design remain unresolved"
            ),
        })
    return rows


def coverage_counts(rows: list[dict[str, str]]) -> tuple[int, int, int]:
    pre = post = straddle = 0
    treatment = datetime.fromisoformat(TREATMENT_START)
    for row in rows:
        start = parse_date(row.get("periodStart", ""))
        end = parse_date(row.get("periodEnd", ""))
        if start is None or end is None:
            continue
        if end < treatment:
            pre += 1
        elif start >= treatment:
            post += 1
        else:
            straddle += 1
    return pre, post, straddle


def period_range(year: str, period: str) -> tuple[str, str]:
    template = PERIOD_RANGES.get(period)
    if not template:
        if re.fullmatch(r"\d{4}", year):
            return year + "-01-01", year + "-12-31"
        return "", ""
    return template[0].format(year=year), template[1].format(year=year)


def api_url(params: dict[str, str]) -> str:
    base = os.environ.get("LDA_API_BASE", LDA_API_BASE).rstrip("/")
    return base + "/filings/?" + urllib.parse.urlencode(params)


def fetch_json(url: str, timeout: float) -> tuple[dict[str, object] | None, str]:
    headers = {"User-Agent": "Codex source audit"}
    if os.environ.get("LDA_API_KEY"):
        headers["Authorization"] = f"Token {os.environ['LDA_API_KEY']}"
    request = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8")), ""
        except urllib.error.HTTPError as exc:
            # Retry only transient service failures, never auth or quota errors.
            if exc.code not in {500, 502, 503, 504} or attempt == 2:
                return None, f"HTTPError: status {exc.code}"
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == 2:
                return None, exc.__class__.__name__
        except json.JSONDecodeError:
            return None, "JSONDecodeError"
        time.sleep(0.5 * (attempt + 1))
    return None, "request failed"


def cached_fetch_json(url: str, timeout: float, cache_dir: Path | None, retrieved_date: str) -> tuple[dict[str, object] | None, str]:
    if cache_dir is None:
        return fetch_json(url, timeout)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / (retrieved_date + "-" + hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")
    if cache_path.is_file():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        response_bytes = json.dumps(cached["response"], sort_keys=True, separators=(",", ":")).encode("utf-8")
        if (cached["url"] != url or cached["retrievedDate"] != retrieved_date
                or hashlib.sha256(response_bytes).hexdigest() != cached["responseSha256"]):
            raise ValueError("LDA response cache provenance mismatch")
        return cached["response"], ""
    payload, error = fetch_json(url, timeout)
    if payload is not None:
        response_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        # Only public response bodies and query URLs, never request auth headers.
        cached = {"url": url, "retrievedDate": retrieved_date,
            "responseSha256": hashlib.sha256(response_bytes).hexdigest(), "response": payload}
        cache_path.write_text(json.dumps(cached, indent=2) + "\n", encoding="utf-8")
    return payload, error


def summary_next_action(status: str) -> str:
    if status == "prepost_source_rows":
        return "Review treated assignment and add matched comparison/control actors before any estimate."
    if status == "post_only_source_rows":
        return "Keep as post-only source evidence until pre-HLOGA rows are observed for the same actor/issue."
    if status == "pre_only_source_rows":
        return "Keep as pre-only source evidence until post-HLOGA rows are observed for the same actor/issue."
    if status == "api_error":
        return "Retry the official LDA API query or narrow the actor batch."
    return "No exact normalized LDA client-name rows found in the queried years."


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
) -> None:
    status_counts = Counter(row["status"] for row in report_rows)
    pre_rows, post_rows, straddle_rows = coverage_counts(panel_rows)
    actors_with_prepost = sum(1 for row in report_rows if row["status"] == "prepost_source_rows")
    issue_count = len({row["issueCode"] for row in panel_rows})
    lines = [
        "# Substitution Historical LDA Panel",
        "",
        f"Generated: `{generated_at}`",
        "",
        "This optional live-acquisition artifact uses the official LDA API to locate exact normalized client-name matches for reviewed canonical actors around the HLOGA treatment date. It supplies visible-lobbying source rows only; it does not establish treatment/control exposure or clear causal substitution claims.",
        "",
        "## Summary",
        "",
        f"- Actors queried: `{len(report_rows)}`",
        f"- Actors with pre/post source rows: `{actors_with_prepost}`",
        f"- Panel rows: `{len(panel_rows)}`",
        f"- Pre-HLOGA rows: `{pre_rows}`",
        f"- Post-HLOGA rows: `{post_rows}`",
        f"- Straddling-period rows: `{straddle_rows}`",
        f"- Distinct LDA issue codes: `{issue_count}`",
        "- Claim status: `source-acquisition only; comparison design still blocked`",
        "",
        "## Status Counts",
        "",
        "| Status | Actors |",
        "| --- | ---: |",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend([
        "",
        "## Actor Acquisition Rows",
        "",
        "| Actor | Status | Filings | Panel rows | Pre | Post | Straddle | Next action |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for row in report_rows:
        lines.append(
            f"| {md(row['primaryName'])} | `{row['status']}` | {row['exactClientMatchedFilings']} | "
            f"{row['panelRows']} | {row['preRows']} | {row['postRows']} | {row['straddleRows']} | "
            f"{md(row['nextAction'])} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def normalize_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", (value or "").upper()).strip()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-") or "unspecified"


def money_millions(value: object) -> float:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return 0.0
    try:
        return float(text) / 1_000_000.0
    except ValueError:
        return 0.0


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def md(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
