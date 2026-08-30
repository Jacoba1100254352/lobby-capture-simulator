#!/usr/bin/env python3
"""Probe historical source access for the HLOGA substitution panel.

This is a live acquisition diagnostic, not a deterministic paper-artifact
builder. It checks whether official LDA surfaces can provide observed rows
around the September 14, 2007 HLOGA treatment date for reviewed exact-ID
actors, and records why the current actor-time spine still cannot be promoted
to estimation readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIRST_WAVE = ROOT / "data" / "calibration" / "first-wave"
TREATMENT_DATE = "2007-09-14"
POST_END_DATE = "2008-12-31"
LDA_API = "https://lda.gov/api/v1/filings/"
LEGACY_SENATE_HOST = "soprweb.senate.gov"
SENATE_DOWNLOAD_PAGE = "https://www.senate.gov/legislative/Public_Disclosure/database_download.htm"
LEGACY_DOWNLOADS = [
    "http://soprweb.senate.gov/downloads/2006_1.zip",
    "http://soprweb.senate.gov/downloads/2006_2.zip",
    "http://soprweb.senate.gov/downloads/2006_3.zip",
    "http://soprweb.senate.gov/downloads/2006_4.zip",
    "http://soprweb.senate.gov/downloads/2007_1.zip",
    "http://soprweb.senate.gov/downloads/2007_2.zip",
    "http://soprweb.senate.gov/downloads/2007_3.zip",
    "http://soprweb.senate.gov/downloads/2007_4.zip",
    "http://soprweb.senate.gov/downloads/2008_1.zip",
    "http://soprweb.senate.gov/downloads/2008_2.zip",
    "http://soprweb.senate.gov/downloads/2008_3.zip",
    "http://soprweb.senate.gov/downloads/2008_4.zip",
]
FILING_PERIODS = (
    "first_quarter",
    "second_quarter",
    "third_quarter",
    "fourth_quarter",
)
PRIORITY_NAMES = (
    "AMERICAN PETROLEUM INSTITUTE",
    "AMERICAN BANKERS ASSOCIATION",
    "AMERICAN GAS ASSOCIATION",
    "AMERICAN ASSOCIATION FOR JUSTICE",
    "AMERICAN BENEFITS COUNCIL",
    "AMERICAN PUBLIC GAS ASSOCIATION",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--first-wave", type=Path, default=FIRST_WAVE)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-actors", type=int, default=12)
    args = parser.parse_args()

    reports = args.reports if args.reports.is_absolute() else ROOT / args.reports
    first_wave = args.first_wave if args.first_wave.is_absolute() else ROOT / args.first_wave
    reports.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict[str, str]] = []
    rows.extend(legacy_download_rows(args.timeout, generated_at))
    rows.extend(aggregate_lda_rows(args.timeout, generated_at))
    rows.extend(actor_probe_rows(first_wave, args.timeout, args.max_actors, generated_at))

    csv_path = reports / "substitution-historical-source-access.csv"
    md_path = reports / "substitution-historical-source-access.md"
    write_csv(csv_path, rows)
    write_markdown(md_path, rows, generated_at)
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    return 0


def legacy_download_rows(timeout: float, generated_at: str) -> list[dict[str, str]]:
    rows = []
    try:
        socket.getaddrinfo(LEGACY_SENATE_HOST, 80)
        status = "host_resolved_not_downloaded"
        evidence = "legacy Senate disclosure host resolved from this environment"
    except OSError as exc:
        status = "blocked_host_unresolved"
        evidence = f"{LEGACY_SENATE_HOST} could not be resolved: {exc.__class__.__name__}"
    for url in LEGACY_DOWNLOADS:
        rows.append(row(
            generated_at,
            "legacy-senate-xml-download",
            status,
            url,
            "historical_lda_xml_zip",
            "pre_and_post_hloga_candidate",
            "",
            "",
            "",
            "",
            evidence,
            (
                "Use the Senate download page to retrieve the historical XML ZIP manually "
                "or from an environment where the legacy host resolves, then normalize it "
                "before any pre-HLOGA visible-lobbying rows are promoted."
            ),
        ))
    rows.append(row(
        generated_at,
        "legacy-senate-download-index",
        "source_index_available",
        SENATE_DOWNLOAD_PAGE,
        "historical_lda_xml_index",
        "download_page",
        "",
        "",
        "",
        "",
        "Senate disclosure download page publishes quarter ZIP links for 2006-2008.",
        "Keep the current HLOGA pre-window blocked until those XML files are retrieved and parsed.",
    ))
    return rows


def aggregate_lda_rows(timeout: float, generated_at: str) -> list[dict[str, str]]:
    rows = []
    for year in (2006, 2007, 2008):
        for period in FILING_PERIODS:
            url = api_url({"filing_year": year, "filing_period": period, "page_size": 1})
            data, error = fetch_json(url, timeout)
            count = data.get("count", "") if data else ""
            status = "ok" if data is not None else "blocked_api_error"
            coverage = coverage_bucket(year, period)
            evidence = f"count={count}" if data is not None else error
            rows.append(row(
                generated_at,
                "lda-api-period-count",
                status,
                url,
                "official_lda_api",
                coverage,
                str(year),
                period,
                str(count),
                "",
                evidence,
                "API counts are source-access diagnostics; rows must still be fetched, normalized, and linked by actor/issue before promotion.",
            ))
    return rows


def actor_probe_rows(first_wave: Path, timeout: float, max_actors: int, generated_at: str) -> list[dict[str, str]]:
    actors = read_csv(first_wave / "canonical-actor-identifiers.csv")
    by_name = {actor.get("primaryName", "").upper(): actor for actor in actors}
    selected = []
    for name in PRIORITY_NAMES:
        if name in by_name:
            selected.append(by_name[name])
    for actor in actors:
        if len(selected) >= max_actors:
            break
        if actor in selected:
            continue
        name = actor.get("primaryName", "")
        if name.startswith("AMERICAN ") or " ASSOCIATION" in name:
            selected.append(actor)
    rows = []
    for actor in selected[:max_actors]:
        actor_name = actor.get("primaryName", "")
        url = api_url({"client_name": actor_name, "filing_year": 2008, "page_size": 100})
        data, error = fetch_json(url, timeout)
        if data is None:
            rows.append(row(
                generated_at,
                "accepted-actor-lda-api-probe",
                "blocked_api_error",
                url,
                "official_lda_api_client_name_search",
                "accepted_actor_probe",
                "2008",
                "",
                "",
                actor.get("canonicalActorId", ""),
                error,
                "Retry the bounded client-name probe before using this actor in a historical visible-lobbying panel.",
                actor_name,
            ))
            continue
        pre_rows = 0
        post_rows = 0
        later_rows = 0
        sample_ids = []
        for result in data.get("results", []):
            posted = str(result.get("dt_posted") or "")[:10]
            if posted and posted < TREATMENT_DATE:
                pre_rows += 1
            elif posted and posted <= POST_END_DATE:
                post_rows += 1
            elif posted:
                later_rows += 1
            if len(sample_ids) < 5 and result.get("filing_uuid"):
                sample_ids.append(result["filing_uuid"])
        status = "post_only_observed" if post_rows and not pre_rows else "prepost_probe_observed" if pre_rows and post_rows else "no_hloga_window_rows"
        rows.append(row(
            generated_at,
            "accepted-actor-lda-api-probe",
            status,
            url,
            "official_lda_api_client_name_search",
            "accepted_actor_probe",
            "2008",
            "",
            str(data.get("count", "")),
            actor.get("canonicalActorId", ""),
            (
                f"client={actor_name}; fetchedRows={len(data.get('results', []))}; "
                f"preDtPostedRows={pre_rows}; postDtPostedRows={post_rows}; "
                f"laterDtPostedRows={later_rows}; sampleFilingUuids={'; '.join(sample_ids)}"
            ),
            "Use only as post-HLOGA acquisition evidence until matching pre-HLOGA XML/API rows are retrieved.",
            actor_name,
        ))
    return rows


def api_url(params: dict[str, object]) -> str:
    return LDA_API + "?" + urllib.parse.urlencode(params)


def fetch_json(url: str, timeout: float) -> tuple[dict[str, object] | None, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "Codex source audit"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), ""
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


def coverage_bucket(year: int, period: str) -> str:
    if year < 2007 or (year == 2007 and period in {"first_quarter", "second_quarter"}):
        return "pre_hloga"
    if year == 2007 and period == "third_quarter":
        return "straddles_hloga_treatment"
    return "post_hloga"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def row(
    generated_at: str,
    item: str,
    status: str,
    source_url: str,
    source_surface: str,
    coverage_role: str,
    year: str,
    period: str,
    observed_count: str,
    canonical_actor_id: str,
    evidence: str,
    next_action: str,
    actor_name: str = "",
) -> dict[str, str]:
    return {
        "generatedAt": generated_at,
        "item": item,
        "status": status,
        "sourceUrl": source_url,
        "sourceSurface": source_surface,
        "coverageRole": coverage_role,
        "year": year,
        "period": period,
        "observedCount": observed_count,
        "canonicalActorId": canonical_actor_id,
        "actorName": actor_name,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "generatedAt",
        "item",
        "status",
        "sourceUrl",
        "sourceSurface",
        "coverageRole",
        "year",
        "period",
        "observedCount",
        "canonicalActorId",
        "actorName",
        "evidence",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], generated_at: str) -> None:
    statuses: dict[str, int] = {}
    for source_row in rows:
        statuses[source_row["status"]] = statuses.get(source_row["status"], 0) + 1
    lines = [
        "# Substitution Historical Source Access",
        "",
        f"Generated: `{generated_at}`",
        "",
        "This live diagnostic checks whether official LDA surfaces can support the HLOGA pre/post source window for the reviewed exact-ID substitution slice. It is acquisition evidence only; it does not promote any source product to estimation readiness.",
        "",
        "## Status Counts",
        "",
        "| Status | Rows |",
        "| --- | ---: |",
    ]
    for status, count in sorted(statuses.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend([
        "",
        "## Key Findings",
        "",
        f"- Treatment date: `{TREATMENT_DATE}`.",
        f"- Legacy Senate XML index: {SENATE_DOWNLOAD_PAGE}.",
        f"- Legacy Senate XML host: `{LEGACY_SENATE_HOST}`.",
    ])
    aggregate = [source_row for source_row in rows if source_row["item"] == "lda-api-period-count"]
    pre_counts = [int(source_row["observedCount"] or 0) for source_row in aggregate if source_row["coverageRole"] == "pre_hloga"]
    post_counts = [int(source_row["observedCount"] or 0) for source_row in aggregate if source_row["coverageRole"] == "post_hloga"]
    lines.append(f"- LDA API aggregate pre-HLOGA count across probed periods: `{sum(pre_counts)}`.")
    lines.append(f"- LDA API aggregate post-HLOGA count across probed periods: `{sum(post_counts)}`.")
    actor_rows = [source_row for source_row in rows if source_row["item"] == "accepted-actor-lda-api-probe"]
    post_only = sum(1 for source_row in actor_rows if source_row["status"] == "post_only_observed")
    lines.append(f"- Accepted actor probes with post-only LDA rows: `{post_only}` of `{len(actor_rows)}`.")
    lines.extend([
        "",
        "## Acquisition Table",
        "",
        "| Item | Status | Coverage | Actor | Count | Evidence | Next action |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ])
    for source_row in rows:
        lines.append(
            "| {item} | `{status}` | {coverage} | {actor} | {count} | {evidence} | {next_action} |".format(
                item=source_row["item"],
                status=source_row["status"],
                coverage=source_row["coverageRole"],
                actor=source_row["actorName"] or source_row["period"] or source_row["year"],
                count=source_row["observedCount"] or "",
                evidence=source_row["evidence"].replace("|", "/"),
                next_action=source_row["nextAction"].replace("|", "/"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
