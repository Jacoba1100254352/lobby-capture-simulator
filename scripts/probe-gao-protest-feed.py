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
from html.parser import HTMLParser
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DEFAULT_FEED_URL = "https://www.gao.gov/rss/reportslegal.xml"
DEFAULT_RECENT_PAGE_URL = "https://www.gao.gov/legal/bid-protests/recent"
DEFAULT_OUTPUT_PREFIX = REPORTS / "gao-protest-feed-preflight"
DEFAULT_RECENT_PAGE_FALLBACK = ROOT / "data" / "fixtures" / "source-native" / "gao-recent-bid-protests.html"
CANDIDATE_BOUNDARY = (
    "candidate-only GAO protest discovery row; does not clear the "
    "gao-protest-overlay source-product gate until PIID, UEI, agency, vendor, "
    "outcome, and issue linkage are manually reviewed"
)
SOURCE_PRODUCT_BOUNDARY = (
    "candidate-only procurement source-surface worklist; does not clear "
    "first-wave source-product, procurement-modification, or causal-calibration gates"
)
PROTEST_RE = re.compile(r"\bprotests?\b", re.IGNORECASE)
B_NUMBER_RE = re.compile(r"\bB-\d+(?:\.\d+)?(?:,\s*B-\d+(?:\.\d+)?)*\b", re.IGNORECASE)
DEPARTMENT_RE = re.compile(
    r"\b(?:Department of [A-Z][A-Za-z &.-]+|Environmental Protection Agency|General Services Administration|"
    r"National Aeronautics and Space Administration|Small Business Administration|Department of Defense|"
    r"Department of the Army|Department of the Navy|Department of the Air Force)\b"
)
AWARDEE_RE = re.compile(
    r"\b(?:award(?: of)?|issuance|issued|selection)\b.{0,90}?\bto\s+(.+?)(?:,?\s+(?:a|an|the)\s+|,\s+of\b|[.;]|$)",
    re.IGNORECASE,
)
OUTCOME_PATTERNS = (
    ("sustained", re.compile(r"\bsustain(?:s|ed|ing)?\b", re.IGNORECASE)),
    ("denied", re.compile(r"\bdeny(?:ies|ied|ing)?\b", re.IGNORECASE)),
    ("dismissed", re.compile(r"\bdismiss(?:es|ed|ing)?\b", re.IGNORECASE)),
    ("withdrawn", re.compile(r"\bwithdraw(?:s|n|ing)?\b", re.IGNORECASE)),
    ("corrective_action", re.compile(r"\bcorrective action\b", re.IGNORECASE)),
)
ISSUE_PATTERNS = (
    ("technical-evaluation", re.compile(r"\btechnical(?:ly)?\b|\bevaluation\b", re.IGNORECASE)),
    ("past-performance", re.compile(r"\bpast performance\b", re.IGNORECASE)),
    ("price-cost", re.compile(r"\bprice\b|\bcost\b", re.IGNORECASE)),
    ("best-value", re.compile(r"\bbest[- ]value\b", re.IGNORECASE)),
    ("small-business-status", re.compile(r"\bsmall business\b|\bSDVOSB\b|\bservice-disabled\b", re.IGNORECASE)),
    ("solicitation-terms", re.compile(r"\bsolicitation\b|\brequest for proposals?\b|\bRFP\b", re.IGNORECASE)),
    ("organizational-conflict", re.compile(r"\borganizational conflict\b|\bOCI\b|\bconflict of interest\b", re.IGNORECASE)),
    ("responsibility", re.compile(r"\bresponsib(?:le|ility)\b", re.IGNORECASE)),
    ("timeliness", re.compile(r"\btimely\b|\btimeliness\b|\blate\b", re.IGNORECASE)),
    ("jurisdiction", re.compile(r"\bjurisdiction\b|\btask order\b|\bcall order\b", re.IGNORECASE)),
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
        "--recent-page-url",
        default=os.environ.get("GAO_RECENT_BID_PROTESTS_URL", DEFAULT_RECENT_PAGE_URL),
        help="GAO recent bid-protest decisions page used to enrich outcome hints.",
    )
    parser.add_argument(
        "--recent-page-input",
        type=Path,
        help="Read recent-decisions HTML from a local fixture instead of the network.",
    )
    parser.add_argument(
        "--recent-page-fallback-input",
        type=Path,
        default=Path(os.environ.get("GAO_RECENT_BID_PROTESTS_FALLBACK_INPUT", DEFAULT_RECENT_PAGE_FALLBACK.as_posix())),
        help=(
            "Fallback recent-decisions HTML fixture used when the live GAO recent page is blocked. "
            "Set to an empty path to disable fallback enrichment."
        ),
    )
    parser.add_argument(
        "--skip-recent-page",
        action="store_true",
        help="Skip recent-decisions page enrichment and use the RSS feed only.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when the feed could not be read or no likely protest rows are found.",
    )
    parser.add_argument(
        "--overlay-candidate-output",
        type=Path,
        help=(
            "Optional path for a candidate-only gao-protest-overlay CSV. "
            "Only likely bid-protest discovery rows are written, and every row "
            "keeps candidateOnly=true so source-product gates cannot promote it."
        ),
    )
    args = parser.parse_args()

    output_prefix = args.output_prefix if args.output_prefix.is_absolute() else ROOT / args.output_prefix
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_label, xml_text = read_xml(args)
        rows, metadata = parse_feed(xml_text, source_label, args.max_items)
        enrich_from_recent_page(rows, metadata, args)
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
    if args.overlay_candidate_output:
        overlay_path = args.overlay_candidate_output if args.overlay_candidate_output.is_absolute() else ROOT / args.overlay_candidate_output
        write_overlay_candidates(overlay_path, rows)
        print(f"Wrote {display_path(overlay_path)}")
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


def enrich_from_recent_page(rows: list[dict[str, str]], metadata: dict[str, str], args: argparse.Namespace) -> None:
    """Attach official recent-page outcome hints when available.

    The RSS feed is the discovery surface, while the GAO recent-decisions page
    often exposes short outcome sentences such as "We deny the protest." The
    enrichment is still a source hint, not adjudicated outcome coding.
    """
    metadata["recentPageSource"] = ""
    metadata["recentPageOutcomeHints"] = "0"
    metadata["recentPageError"] = ""
    if args.skip_recent_page:
        metadata["recentPageSource"] = "skipped"
        return
    if args.input and not args.recent_page_input:
        metadata["recentPageSource"] = "skipped_for_feed_fixture"
        return
    try:
        source_label, html_text = read_recent_page(args)
        outcomes = recent_page_outcomes(html_text)
    except Exception as exc:
        metadata["recentPageSource"] = args.recent_page_input.as_posix() if args.recent_page_input else args.recent_page_url
        metadata["recentPageError"] = f"{type(exc).__name__}: {exc}"
        if args.recent_page_input:
            return
        fallback = fallback_recent_page(args)
        if not fallback:
            return
        fallback_source, html_text = fallback
        source_label = fallback_source
        metadata["recentPageSource"] = fallback_source
        metadata["recentPageFallback"] = f"live recent page unavailable; used {fallback_source}"
        outcomes = recent_page_outcomes(html_text)
    enriched = 0
    for row in rows:
        if row.get("outcomeHint"):
            continue
        outcome = outcome_for_row(row, outcomes)
        if not outcome:
            continue
        row["outcomeHint"] = outcome
        row["outcomeHintSource"] = metadata.get("recentPageSource", "")
        row["manualReviewNeeds"] = manual_review_needs(
            row.get("agencyHint", ""),
            row.get("awardeeNameHint", ""),
            row.get("outcomeHint", ""),
            row.get("issueCodeHints", ""),
        )
        enriched += 1
    metadata["recentPageSource"] = source_label
    metadata["recentPageOutcomeHints"] = str(enriched)


def read_recent_page(args: argparse.Namespace) -> tuple[str, str]:
    if args.recent_page_input:
        path = args.recent_page_input if args.recent_page_input.is_absolute() else ROOT / args.recent_page_input
        return path.as_posix(), path.read_text(encoding="utf-8")
    request = Request(
        args.recent_page_url,
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
            return args.recent_page_url, response.read().decode(encoding, errors="replace")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"GAO recent page HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"GAO recent page request failed: {exc.reason}") from exc


def fallback_recent_page(args: argparse.Namespace) -> tuple[str, str] | None:
    path = args.recent_page_fallback_input
    if not path or str(path).strip() == "":
        return None
    resolved = path if path.is_absolute() else ROOT / path
    if not resolved.exists():
        return None
    return resolved.as_posix(), resolved.read_text(encoding="utf-8")


def recent_page_outcomes(html_text: str) -> dict[str, str]:
    tokens = visible_text_tokens(html_text)
    outcomes: dict[str, str] = {}
    for index, token in enumerate(tokens):
        b_numbers = split_b_numbers(token)
        if not b_numbers:
            continue
        outcome = ""
        for previous in reversed(tokens[max(0, index - 8) : index]):
            candidate = outcome_hint(previous)
            if candidate:
                outcome = candidate
                break
        if not outcome:
            continue
        for b_number in b_numbers:
            outcomes.setdefault(b_number, outcome)
    return outcomes


def visible_text_tokens(html_text: str) -> list[str]:
    parser = VisibleTextParser()
    parser.feed(html_text)
    return [token for token in (clean_text(value) for value in parser.tokens) if token]


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tokens: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and data.strip():
            self.tokens.append(data)


def outcome_for_row(row: dict[str, str], outcomes: dict[str, str]) -> str:
    for value in (row.get("protestId", ""), row.get("guid", ""), row.get("sourceUrl", "")):
        for b_number in split_b_numbers(value):
            if b_number in outcomes:
                return outcomes[b_number]
    return ""


def split_b_numbers(value: str) -> list[str]:
    found: list[str] = []
    for match in B_NUMBER_RE.finditer(value or ""):
        found.extend(part.strip().upper() for part in match.group(0).split(",") if part.strip())
    return list(dict.fromkeys(found))


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
        agency = agency_hint(combined)
        awardee = awardee_hint(description)
        outcome = outcome_hint(combined)
        issues = issue_hints(combined)
        rows.append(
            {
                "protestId": b_numbers or protest_id_from_link(link, guid),
                "sourceUrl": link,
                "title": title,
                "guid": guid,
                "publishedAt": decision_at,
                "decisionDate": decision_at[:10] if decision_at else "",
                "likelyBidProtest": "true" if likely else "false",
                "agencyHint": agency,
                "protesterNameHint": title if likely else "",
                "awardeeNameHint": awardee,
                "outcomeHint": outcome,
                "outcomeHintSource": "",
                "issueCodeHints": issues,
                "description": description,
                "piid": "",
                "uei": "",
                "reviewPriority": review_priority(likely, agency, awardee, issues),
                "manualReviewNeeds": manual_review_needs(agency, awardee, outcome, issues),
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
        "awardeeNameHint",
        "outcomeHint",
        "outcomeHintSource",
        "issueCodeHints",
        "description",
        "piid",
        "uei",
        "reviewPriority",
        "manualReviewNeeds",
        "linkageStatus",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_overlay_candidates(path: Path, rows: list[dict[str, str]]) -> None:
    """Write likely protest rows in the first-wave GAO overlay schema.

    These are review worklist rows, not source evidence. The candidate markers
    are deliberately repeated on every row so the source-product audit defers
    field and semantic checks until a reviewer replaces discovery hints with
    adjudicated values.
    """
    fieldnames = [
        "protestId",
        "piid",
        "uei",
        "agency",
        "filedDate",
        "decisionDate",
        "outcome",
        "issueCodes",
        "sourceUrl",
        "docketNumber",
        "protesterName",
        "awardeeName",
        "notes",
        "candidateOnly",
        "candidateStatus",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    likely_rows = [row for row in rows if row.get("likelyBidProtest") == "true"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in likely_rows:
            writer.writerow(overlay_candidate_row(row))


def overlay_candidate_row(row: dict[str, str]) -> dict[str, str]:
    review_needs = row.get("manualReviewNeeds", "")
    notes = (
        f"{SOURCE_PRODUCT_BOUNDARY}; "
        "candidate-only GAO RSS discovery row; "
        f"reviewPriority={row.get('reviewPriority', '')}; "
        f"manualReviewNeeds={review_needs}; "
        f"feedPublishedAt={row.get('publishedAt', '')}; "
        f"outcomeHintSource={row.get('outcomeHintSource', '') or 'rss_or_unavailable'}; "
        "not estimation ready until agency, filed date, outcome, issue coding, "
        "PIID/UEI or reviewed vendor linkage, and source-page details are adjudicated"
    )
    return {
        "protestId": row.get("protestId", "") or "candidate_unreviewed",
        "piid": "candidate_unreviewed",
        "uei": "candidate_unreviewed",
        "agency": row.get("agencyHint", "") or "candidate_unreviewed",
        "filedDate": "candidate_unreviewed",
        "decisionDate": row.get("decisionDate", "") or "candidate_unreviewed",
        "outcome": row.get("outcomeHint", "") or "candidate_unreviewed",
        "issueCodes": row.get("issueCodeHints", "") or "candidate_unreviewed",
        "sourceUrl": row.get("sourceUrl", "") or "https://www.gao.gov/legal/bid-protests/recent",
        "docketNumber": row.get("protestId", "") or "candidate_unreviewed",
        "protesterName": row.get("protesterNameHint", "") or "candidate_unreviewed",
        "awardeeName": row.get("awardeeNameHint", "") or "candidate_unreviewed",
        "notes": notes,
        "candidateOnly": "true",
        "candidateStatus": "candidate_unreviewed_not_estimation_ready",
    }


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
        f"- Recent page source: `{metadata.get('recentPageSource', '')}`",
        f"- Outcome hints from recent page: `{metadata.get('recentPageOutcomeHints', '0')}`",
        f"- Last build date: `{metadata.get('lastBuildDate', '')}`",
        f"- Generated at: `{metadata.get('generatedAt', '')}`",
        f"- Items scanned: `{len(rows)}`",
        f"- Likely bid-protest rows: `{len(likely)}`",
        f"- Claim boundary: `{CANDIDATE_BOUNDARY}`",
    ]
    if error:
        lines.append(f"- Error: `{md(error)}`")
    if metadata.get("recentPageError"):
        lines.append(f"- Recent page enrichment error: `{md(metadata.get('recentPageError', ''))}`")
    if metadata.get("recentPageFallback"):
        lines.append(f"- Recent page fallback: `{md(metadata.get('recentPageFallback', ''))}`")
    lines.extend(
        [
            "",
            "## Promotion Rule",
            "",
            "Rows from this report can become procurement source-product evidence only after manual review adds or confirms PIID, UEI, agency, vendor, outcome, issue, and source-linkage fields in `data/calibration/first-wave/gao-protest-overlay.csv`, followed by `make first-wave-source-products`, `make first-wave-source-readiness`, and `make paper-artifacts-check`.",
            "",
            "## Likely Protest Rows",
            "",
            "| Protest ID | Protester | Decision date | Outcome hint | Agency hint | Awardee hint | Issue hints | Priority | Source |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    if likely:
        for row in likely[:25]:
            lines.append(
                "| {protest} | {title} | {date} | {outcome} | {agency} | {awardee} | {issues} | {priority} | {source} |".format(
                    protest=md(row["protestId"]),
                    title=md(row["title"]),
                    date=md(row["decisionDate"]),
                    outcome=md(row["outcomeHint"]),
                    agency=md(row["agencyHint"]),
                    awardee=md(row["awardeeNameHint"]),
                    issues=md(row["issueCodeHints"]),
                    priority=md(row["reviewPriority"]),
                    source=md(row["sourceUrl"]),
                )
            )
    else:
        lines.append("| none |  |  |  |  |  |  |  |  |")
    lines.extend(
        [
            "",
            "## Review Fields",
            "",
            "The parser extracts B-numbers, protester names, decision dates, agency hints, awardee hints, coarse issue-code hints, outcome language visible in the RSS item, and short outcome sentences from the official recent-decisions page when available. These are discovery fields only. Manual promotion still requires reviewed PIID, UEI or vendor linkage, outcome coding, issue coding, and source records in `data/calibration/first-wave/gao-protest-overlay.csv`.",
        ]
    )
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


def awardee_hint(text_value: str) -> str:
    match = AWARDEE_RE.search(text_value)
    if not match:
        return ""
    value = clean_text(match.group(1))
    value = value.replace("\u2026", "...")
    value = re.sub(r"^(?:a|an|the)\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r",?\s+(?:a|an|the)(?:\s+|\.\.\.)?$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*\([^)]*$", "", value)
    value = value.rstrip(" ,.;")
    return value[:120]


def outcome_hint(text_value: str) -> str:
    outcomes = [label for label, pattern in OUTCOME_PATTERNS if pattern.search(text_value)]
    return ";".join(dict.fromkeys(outcomes))


def issue_hints(text_value: str) -> str:
    issues = [label for label, pattern in ISSUE_PATTERNS if pattern.search(text_value)]
    return ";".join(dict.fromkeys(issues))


def review_priority(likely: bool, agency: str, awardee: str, issues: str) -> str:
    if not likely:
        return "not_bid_protest"
    observed = sum(1 for value in (agency, awardee, issues) if value)
    if observed >= 2:
        return "high"
    if observed == 1:
        return "medium"
    return "needs_source_page_review"


def manual_review_needs(agency: str, awardee: str, outcome: str, issues: str) -> str:
    needs = ["piid_or_uei_linkage"]
    if not agency:
        needs.append("agency")
    if not awardee:
        needs.append("awardee_or_vendor")
    if not outcome:
        needs.append("outcome")
    if not issues:
        needs.append("issue_codes")
    return ";".join(needs)


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
