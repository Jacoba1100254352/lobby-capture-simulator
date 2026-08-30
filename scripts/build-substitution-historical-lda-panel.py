#!/usr/bin/env python3
"""Build an optional historical LDA panel for the HLOGA substitution product.

This is a live source-acquisition helper. It queries the official LDA API for
reviewed canonical actors by exact normalized client name, keeps observed
2007-2008 filing rows, and writes a local panel that the first-wave promotion
script can consume. The output is source evidence for a visible-lobbying
pre/post surface; it is not a comparison design or a causal estimate.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
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
        )
        panel_rows.extend(rows)
        report_rows.append(summary)

    panel_rows.sort(key=lambda row: (
        row["canonicalActorId"],
        row["periodStart"],
        row["filingUuid"],
        row["issueCode"],
    ))
    output.parent.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    write_csv(output, panel_rows, PANEL_FIELDS)
    write_csv(reports / REPORT_CSV.name, report_rows, REPORT_FIELDS)
    write_markdown(reports / REPORT_MD.name, panel_rows, report_rows, generated_at)
    print(f"Wrote {output}")
    print(f"Wrote {reports / REPORT_CSV.name}")
    print(f"Wrote {reports / REPORT_MD.name}")
    return 0


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
) -> tuple[list[dict[str, str]], dict[str, str]]:
    actor_name = actor.get("primaryName", "")
    actor_key = normalize_name(actor_name)
    api_result_count = 0
    matched_filings: dict[str, dict[str, object]] = {}
    source_urls: set[str] = set()
    errors: list[str] = []
    for year in years:
        url = api_url({
            "client_name": actor_name,
            "filing_year": year,
            "page_size": str(page_size),
        })
        for _ in range(max_pages):
            payload, error = fetch_json(url, timeout)
            if payload is None:
                errors.append(error)
                break
            api_result_count += int(payload.get("count", 0)) if not matched_filings else 0
            for record in payload.get("results", []):
                client = record.get("client") if isinstance(record.get("client"), dict) else {}
                client_name = str(client.get("name", ""))
                if normalize_name(client_name) != actor_key:
                    continue
                filing_uuid = str(record.get("filing_uuid", ""))
                if filing_uuid:
                    matched_filings[filing_uuid] = record
                    if record.get("filing_document_url"):
                        source_urls.add(str(record["filing_document_url"]))
            next_url = payload.get("next")
            if not next_url:
                break
            url = str(next_url)

    panel_rows: list[dict[str, str]] = []
    for record in matched_filings.values():
        panel_rows.extend(panel_rows_for_record(actor, record, review_date))
    pre_rows, post_rows, straddle_rows = coverage_counts(panel_rows)
    status = "prepost_source_rows" if pre_rows and post_rows else "post_only_source_rows" if post_rows else "pre_only_source_rows" if pre_rows else "no_exact_client_rows"
    if errors and not panel_rows:
        status = "api_error"
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
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), ""
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


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
        "This optional live-acquisition artifact uses the official LDA API to locate exact normalized client-name matches for reviewed canonical actors around the HLOGA treatment date. It supplies treated visible-lobbying source rows only; it does not supply comparison/control actors and does not clear causal substitution claims.",
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
