#!/usr/bin/env python3
"""Build an operational GAO bid-protest discovery worklist.

The GAO Legal Products RSS feed is useful for finding recent bid-protest
decisions, but it does not reliably expose PIID, UEI, awardee, or vendor linkage
fields. This preflight therefore writes an ignored discovery report only. Rows
remain candidate-only until manually reviewed and linked through the first-wave
source-product gate.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import html
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DEFAULT_FEED_URL = "https://www.gao.gov/rss/reportslegal.xml"
DEFAULT_OUTPUT_PREFIX = REPORTS / "gao-protest-feed-preflight"
CANDIDATE_BOUNDARY = (
    "candidate-only GAO protest discovery row; does not clear the "
    "gao-protest-overlay source-product gate until PIID, UEI, agency, vendor, "
    "outcome, and issue linkage are manually reviewed"
)
PROTEST_RE = re.compile(r"\bprotests?\b", re.IGNORECASE)
B_NUMBER_RE = re.compile(r"\bB-\d+(?:\.\d+)?(?:,\s*B-\d+(?:\.\d+)?)*\b", re.IGNORECASE)
DEPARTMENT_RE = re.compile(
    r"\b(?:Department of [A-Z][A-Za-z &.-]+|Environmental Protection Agency|General Services Administration|"
    r"National Aeronautics and Space Administration|Small Business Administration|Department of Defense|"
    r"Department of the Army|Department of the Navy|Department of the Air Force)\b"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.environ.get("GAO_LEGAL_PRODUCTS_FEED_URL", DEFAULT_FEED_URL),
        help="GAO Legal Products RSS feed URL.",
    )
    parser.add_argument("--input", type=Path, help="Read RSS XML from a local fixture instead of the network.")
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=DEFAULT_OUTPUT_PREFIX,
        help="Output path prefix; .csv and .md are appended.",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=int(os.environ.get("GAO_PROTEST_FEED_MAX_ITEMS", "50")),
        help="Maximum feed items to keep in the worklist.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=int(os.environ.get("GAO_PROTEST_FEED_TIMEOUT_SECONDS", "30")),
        help="Network timeout for the feed request.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when the feed could not be read or no likely protest rows are found.",
    )
    args = parser.parse_args()

    output_prefix = args.output_prefix if args.output_prefix.is_absolute() else ROOT / args.output_prefix
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_label, xml_text = read_xml(args)
        rows, metadata = parse_feed(xml_text, source_label, args.max_items)
        status = "ready" if any(row["likelyBidProtest"] == "true" for row in rows) else "manual_required"
        error = ""
    except Exception as exc:
        rows = []
        metadata = {
            "feedTitle": "",
            "lastBuildDate": "",
            "source": args.input.as_posix() if args.input else args.url,
            "generatedAt": now_utc(),
        }
        status = "unavailable"
        error = f"{type(exc).__name__}: {exc}"

    write_csv(output_prefix.with_suffix(".csv"), rows)
    write_markdown(output_prefix.with_suffix(".md"), rows, metadata, status, error)
    print(f"Wrote {display_path(output_prefix.with_suffix('.csv'))}")
    print(f"Wrote {display_path(output_prefix.with_suffix('.md'))}")
    if args.strict and (status == "unavailable" or not any(row.get("likelyBidProtest") == "true" for row in rows)):
        return 1
    return 0


def read_xml(args: argparse.Namespace) -> tuple[str, str]:
    if args.input:
        path = args.input if args.input.is_absolute() else ROOT / args.input
        return path.as_posix(), path.read_text(encoding="utf-8")
    request = Request(
        args.url,
        headers={
            "User-Agent": os.environ.get(
                "GAO_PROTEST_FEED_USER_AGENT",
                "lobby-capture-simulator/1.0 (+https://github.com/Jacoba1100254352/lobby-capture-simulator)",
            )
        },
    )
    try:
        with urlopen(request, timeout=args.timeout_seconds) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            return args.url, response.read().decode(encoding, errors="replace")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"GAO feed HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"GAO feed request failed: {exc.reason}") from exc


def parse_feed(xml_text: str, source_label: str, max_items: int) -> tuple[list[dict[str, str]], dict[str, str]]:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS channel element missing")
    metadata = {
        "feedTitle": text(channel.find("title")),
        "lastBuildDate": text(channel.find("lastBuildDate")),
        "source": source_label,
        "generatedAt": now_utc(),
    }
    rows = []
    for item in channel.findall("item")[:max_items]:
        title = clean_text(text(item.find("title")))
        link = clean_text(text(item.find("link")))
        description = clean_text(text(item.find("description")))
        guid = clean_text(text(item.find("guid")))
        pub_date = clean_text(text(item.find("pubDate")))
        combined = " ".join([title, description])
        b_numbers = b_numbers_from([guid, link, title, description])
        likely = bool(PROTEST_RE.search(combined))
        decision_at = iso_datetime(pub_date)
        rows.append(
            {
                "protestId": b_numbers or protest_id_from_link(link, guid),
                "sourceUrl": link,
                "title": title,
                "guid": guid,
                "publishedAt": decision_at,
                "decisionDate": decision_at[:10] if decision_at else "",
                "likelyBidProtest": "true" if likely else "false",
                "agencyHint": agency_hint(combined),
                "protesterNameHint": title if likely else "",
                "description": description,
                "piid": "",
                "uei": "",
                "linkageStatus": "candidate_unreviewed",
                "notes": CANDIDATE_BOUNDARY,
            }
        )
    return rows, metadata


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "protestId",
        "sourceUrl",
        "title",
        "guid",
        "publishedAt",
        "decisionDate",
        "likelyBidProtest",
        "agencyHint",
        "protesterNameHint",
        "description",
        "piid",
        "uei",
        "linkageStatus",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], metadata: dict[str, str], status: str, error: str) -> None:
    likely = [row for row in rows if row.get("likelyBidProtest") == "true"]
    lines = [
        "# GAO Protest Feed Preflight",
        "",
        "This ignored operational report turns the official GAO Legal Products RSS feed into a bid-protest discovery worklist. It is not promoted source evidence and does not clear the procurement calibration gate.",
        "",
        "## Summary",
        "",
        f"- Status: `{status}`",
        f"- Feed title: `{metadata.get('feedTitle', '')}`",
        f"- Feed source: `{metadata.get('source', '')}`",
        f"- Last build date: `{metadata.get('lastBuildDate', '')}`",
        f"- Generated at: `{metadata.get('generatedAt', '')}`",
        f"- Items scanned: `{len(rows)}`",
        f"- Likely bid-protest rows: `{len(likely)}`",
        f"- Claim boundary: `{CANDIDATE_BOUNDARY}`",
    ]
    if error:
        lines.append(f"- Error: `{md(error)}`")
    lines.extend(
        [
            "",
            "## Promotion Rule",
            "",
            "Rows from this report can become procurement source-product evidence only after manual review adds or confirms PIID, UEI, agency, vendor, outcome, issue, and source-linkage fields in `data/calibration/first-wave/gao-protest-overlay.csv`, followed by `make first-wave-source-products`, `make first-wave-source-readiness`, and `make paper-artifacts-check`.",
            "",
            "## Likely Protest Rows",
            "",
            "| Protest ID | Title | Decision date | Agency hint | Source | Linkage status |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if likely:
        for row in likely[:25]:
            lines.append(
                "| {protest} | {title} | {date} | {agency} | {source} | {status} |".format(
                    protest=md(row["protestId"]),
                    title=md(row["title"]),
                    date=md(row["decisionDate"]),
                    agency=md(row["agencyHint"]),
                    source=md(row["sourceUrl"]),
                    status=md(row["linkageStatus"]),
                )
            )
    else:
        lines.append("| none |  |  |  |  |  |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def b_numbers_from(values: list[str]) -> str:
    found: list[str] = []
    for value in values:
        found.extend(match.group(0).upper().replace(" ", "") for match in B_NUMBER_RE.finditer(value or ""))
    return ";".join(dict.fromkeys(found))


def protest_id_from_link(link: str, guid: str) -> str:
    value = guid or link
    if not value:
        return ""
    return value.rstrip("/").split("/")[-1].upper()


def agency_hint(text_value: str) -> str:
    match = DEPARTMENT_RE.search(text_value)
    if match:
        return match.group(0)
    possessive = re.search(r"protests?\s+(?:the\s+)?(.+?)(?:'s|’s)\s+", text_value, re.IGNORECASE)
    if possessive:
        return clean_text(possessive.group(1))[:120]
    return ""


def iso_datetime(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return ""
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def text(element: ET.Element | None) -> str:
    return "" if element is None or element.text is None else element.text


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
