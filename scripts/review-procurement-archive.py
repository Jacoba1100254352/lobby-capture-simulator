#!/usr/bin/env python3
"""Review archived VA labels without converting them into solicitation or stay dates."""

import base64
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import gzip
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("va_publisher", ROOT / "scripts/review-procurement-publisher.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
fingerprint = publisher.fingerprint
ORIGINAL_URL = "https://www.va.gov/opal/sac/mspv.asp"
JUNE, SEPTEMBER = "20240613162439", "20240906233447"
HEADER = ["VISN", "Prime Vendor", "Delivery Order Number", "Base Period of Performance"]
CAPTION = "MSPV Gen-Z V1 Delivery Order Awards"
NOTE = "*DO awards are currently under GAO protest. Stay of performance in effect until further notice."
JUNE_AREAS = ["VISN 8 (excl. Puerto Rico)", "VISN 19", "VISN 20", "VISN 22", "Other Government Agencies (OGAs)"]
SEPTEMBER_AREAS = [area for area in publisher.AREAS if area != "VISN 23"]
ALIASES = {"VISN 8 (excl. Puerto Rico)": "VISN 8", "VISN 8 excluding Puerto Rico": "VISN 8",
           "Other Government Agencies (OGAs)": "OGA"}


def decoded(raw):
    return gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw


def period(value):
    match = re.fullmatch(r"(\d{2}/\d{2}/\d{4})\s*[-\u2013\u2014]\s*(\d{2}/\d{2}/\d{4})", value)
    if not match:
        raise ValueError("Unreviewed archived performance-period format")
    start, end = [datetime.strptime(part, "%m/%d/%Y").date().isoformat() for part in match.groups()]
    if start > end:
        raise ValueError("Invalid archived performance chronology")
    return start, end


class Lists(HTMLParser):
    """Capture list boundaries, keeping nested lists distinct."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.items, self.lists = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in {"ul", "ol"}:
            self.stack.append([])
        elif tag == "li" and self.stack:
            self.items.append((self.stack[-1], []))
        elif tag == "br" and self.items:
            self.items[-1][1].append(" ")

    def handle_data(self, data):
        if self.items:
            self.items[-1][1].append(data)

    def handle_endtag(self, tag):
        if tag == "li" and self.items:
            target, parts = self.items.pop()
            target.append(" ".join("".join(parts).split()))
        elif tag in {"ul", "ol"} and self.stack:
            self.lists.append(self.stack.pop())


def project(native_rows, stamp):
    result = []
    for ordinal, native in enumerate(native_rows, 1):
        if stamp == JUNE:
            if len(native) != 4 or native[1] != "Medline Industries, LP":
                raise ValueError("Unreviewed archived table cells")
            area, vendor, key, dates = native
            marker = None  # A table without a note is not a finding of no protest.
        elif stamp == SEPTEMBER:
            tbd = re.fullmatch(r"(.+) - (?:To be determined \(TBD\)|TBD)", native)
            if tbd:
                result.append({"rowNumber": ordinal, "serviceAreaNative": tbd[1],
                               "listingStatus": "source_tbd", "awardeeNative": None,
                               "parentPiid": None, "piid": None,
                               "performanceStartDate": None, "performanceEndDate": None,
                               "protestNoteMarker": None})
                continue
            match = re.fullmatch(r"(.+) Medline Industries, LP Delivery Order: "
                                 r"(36C10X\d{2}D\d{4} 36C10X\d{2}N\d{4})(\*)? Performance Period: (.+)", native)
            if not match:
                raise ValueError("Unreviewed archived list entry")
            area, key, star, dates = match.groups()
            vendor, marker = "Medline Industries, LP", bool(star)
        else:
            raise ValueError("Unknown reviewed capture")
        keys = re.fullmatch(r"(36C10X\d{2}D\d{4}) (36C10X\d{2}N\d{4})", key)
        if not keys:
            raise ValueError("Unreviewed archived parent/child key")
        start, end = period(dates)
        result.append({"rowNumber": ordinal, "serviceAreaNative": area,
                       "listingStatus": "named_order", "awardeeNative": vendor,
                       "parentPiid": keys[1], "piid": keys[2],
                       "performanceStartDate": start, "performanceEndDate": end,
                       "protestNoteMarker": marker})
    expected = JUNE_AREAS if stamp == JUNE else SEPTEMBER_AREAS
    if [row["serviceAreaNative"] for row in result] != expected:
        raise ValueError("Incomplete archived display frame")
    return result


def parse(raw, stamp):
    html = decoded(raw).decode("utf-8")
    tables = publisher.Tables()
    tables.feed(html)
    text = " ".join(" ".join(tables.text_parts).split())
    updated = re.findall(r"Last updated ([A-Za-z]+ \d{1,2}, \d{4})", text)
    if len(updated) != 1:
        raise ValueError("Missing or ambiguous archived page date")
    if stamp == JUNE:
        candidates = [table for table in tables.tables if table and table[0] == HEADER]
        if len(candidates) != 1 or CAPTION not in text:
            raise ValueError("Missing or ambiguous archived award table")
        native = candidates[0][1:]
        note = None
    elif stamp == SEPTEMBER:
        lists = Lists()
        lists.feed(html)
        candidates = [items for items in lists.lists if items and items[0] == "VISN 1 - To be determined (TBD)"]
        if (len(candidates) != 1 or NOTE not in text
                or "Delivery order (DO) awards expected through October 2024." not in text):
            raise ValueError("Missing or ambiguous archived delivery-order list/note")
        # Public projection ends before the contact fields; no staff contacts are retained.
        native = [item.split("Contracting Officer:")[0].strip() for item in candidates[0]]
        note = NOTE
    else:
        raise ValueError("Unknown reviewed capture")
    return {"pageUpdatedDate": datetime.strptime(updated[0], "%B %d, %Y").date().isoformat(),
            "nativeRows": native, "rows": project(native, stamp), "protestNote": note}


def validate(review, original_review, provisional_links, docket_sources, raw_sources=None, raw_index=None):
    """Check full display projections and optional payloads; adjudication remains pending."""
    if (review.get("schema") != "gao-archived-publisher-review-v1"
            or review.get("reviewFingerprint") != fingerprint({k: v for k, v in review.items() if k != "reviewFingerprint"})
            or review.get("originalReviewFingerprint") != fingerprint(original_review)
            or review.get("docketSourceFingerprint") != fingerprint(docket_sources)):
        raise ValueError("Stale archive review or baseline fingerprint")
    boundary = {"independentReviewStatus": "pending", "baselineUnchanged": True,
                "solicitationIdentityPromoted": False, "awardSpecificDatesPromoted": False,
                "stayIntervalsPromoted": False, "historicalExclusionsPromoted": False,
                "representativeSamExport": False, "causalEffect": "not_identified"}
    if any(review.get(key) != value for key, value in boundary.items()):
        raise ValueError("Unsupported archive promotion")
    for key in ("selection", "sourceAuthentication", "scope", "reviewer"):
        if not review.get(key):
            raise ValueError("Missing archive review provenance")
    index = review["archiveIndex"]
    if (index["request"] != {"url": "www.va.gov/opal/sac/mspv.asp", "output": "json",
                             "filter": ["statuscode:200", "mimetype:text/html"], "from": "2024", "to": "2024",
                             "fl": "timestamp,original,statuscode,digest"}
            or index["response"][0] != ["timestamp", "original", "statuscode", "digest"]
            or index["endpoint"] != "https://web.archive.org/cdx/search/cdx"):
        raise ValueError("Archive index scope mismatch")
    indexed = index["response"][1:]
    stamps = [row[0] for row in indexed]
    if (len(indexed) != 7 or stamps != sorted(set(stamps))
            or any(row[1] != ORIGINAL_URL or row[2] != "200" or not re.fullmatch(r"[A-Z2-7]{32}", row[3]) for row in indexed)):
        raise ValueError("Incomplete archive index projection")
    for stamp in stamps:
        datetime.strptime(stamp, "%Y%m%d%H%M%S")
    if raw_index is not None and (hashlib.sha256(raw_index).hexdigest() != index["rawSha256"]
                                  or json.loads(raw_index) != index["response"]):
        raise ValueError("Raw archive index mismatch")
    captures = review["captures"]
    if [capture["timestamp"] for capture in captures] != [JUNE, SEPTEMBER]:
        raise ValueError("Missing reviewed capture")
    if raw_sources is not None and set(raw_sources) - {JUNE, SEPTEMBER}:
        raise ValueError("Unknown raw capture")
    for capture in captures:
        stamp = capture["timestamp"]
        url = f"https://web.archive.org/web/{stamp}id_/{ORIGINAL_URL}"
        indexed_row = next(row for row in indexed if row[0] == stamp)
        memento = parsedate_to_datetime(capture["mementoDatetime"])
        if memento.tzinfo is None:
            raise ValueError("Archive capture timezone is missing")
        parsed_stamp = memento.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
        if (capture["requestedUrl"] != url or capture["resolvedUrl"] != url or capture["status"] != 200
                or parsed_stamp != stamp or capture["cdxDigest"] != indexed_row[3]
                or capture["pageUpdatedDate"] != {JUNE: "2024-06-06", SEPTEMBER: "2024-09-04"}[stamp]
                or capture["wireEncoding"] != {JUNE: "identity", SEPTEMBER: "gzip"}[stamp]
                or capture["protestNote"] != (None if stamp == JUNE else NOTE)
                or capture["rows"] != project(capture["nativeRows"], stamp)
                or capture["nativeRowsFingerprint"] != fingerprint(capture["nativeRows"])):
            raise ValueError("Archive provenance or native projection mismatch")
        for field in ("rawSha256", "decodedSha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", capture[field]):
                raise ValueError("Missing archived payload hash")
        raw = (raw_sources or {}).get(stamp)
        if raw is not None:
            # CDX indexes the archived payload: for September that payload is still gzip encoded.
            if (hashlib.sha256(raw).hexdigest() != capture["rawSha256"]
                    or base64.b32encode(hashlib.sha1(raw).digest()).decode() != capture["cdxDigest"]
                    or hashlib.sha256(decoded(raw)).hexdigest() != capture["decodedSha256"]):
                raise ValueError("Raw archived payload or CDX digest mismatch")
            parsed = parse(raw, stamp)
            if any(parsed[key] != capture[key] for key in parsed):
                raise ValueError("Raw archive extraction mismatch")

    june, september = [capture["rows"] for capture in captures]
    by_area = lambda rows: {ALIASES.get(row["serviceAreaNative"], row["serviceAreaNative"]): row for row in rows}
    earlier, later = by_area(june), by_area(september)
    conflicts = []
    for area, row in earlier.items():
        other = later.get(area)
        if other and other["listingStatus"] == "named_order":
            for field in ("parentPiid", "piid", "performanceStartDate", "performanceEndDate"):
                if row[field] != other[field]:
                    conflicts.append({"serviceArea": area, "field": field, "june": row[field], "september": other[field]})
    grouped = defaultdict(list)
    for row in september:
        if row["piid"]:
            grouped[(row["parentPiid"], row["piid"])].append(row["serviceAreaNative"])
    duplicates = [{"parentPiid": key[0], "piid": key[1], "serviceAreas": areas}
                  for key, areas in grouped.items() if len(areas) > 1]
    footnotes = {row["serviceArea"]: row["caseNumbers"] for row in docket_sources["decisionReview"]["serviceAreaFootnotes"]}
    pairs = set()
    for award in original_review["awards"]:
        area = award["provisionalServiceArea"]
        row = earlier[area]
        if (row["piid"] != award["piid"]
                or row["parentPiid"] != award["originalProjection"]["parent_award_id_piid"]):
            raise ValueError("June archive disagrees with pilot mapping")
        pairs.update((award["piid"], area, case) for case in footnotes[area])
    if (len(provisional_links) != len(pairs)
            or {(row["piid"], row["serviceArea"], row["decisionCaseId"]) for row in provisional_links} != pairs
            or any(row["status"] != "provisional_not_promoted" for row in provisional_links)):
        raise ValueError("Archive follow-up requires complete unchanged provisional links")
    marked = [row for row in september if row["protestNoteMarker"]]
    return {"indexedCaptures": len(indexed), "reviewedCaptures": len(captures),
            "juneRows": len(june), "junePilotAwardsCorroborated": len(original_review["awards"]),
            "juneCorroboratedProvisionalPairs": len(pairs), "distinctDockets": len({p[2] for p in pairs}),
            "septemberRows": len(september), "septemberTbdRows": sum(row["listingStatus"] == "source_tbd" for row in september),
            "septemberDuplicateKeys": duplicates, "crossCaptureConflicts": conflicts,
            "septemberMissingCurrentServiceAreas": sorted(set(publisher.AREAS) - set(row["serviceAreaNative"] for row in september)),
            "septemberMarkedRows": len(marked), "septemberDistinctMarkedKeys": len({(r["parentPiid"], r["piid"]) for r in marked}),
            "independentlyReviewedMappings": 0, "awardSpecificDatesPromoted": 0,
            "stayIntervalsPromoted": 0, "historicalExclusionsPromoted": 0, "causalEffect": "not_identified"}
