#!/usr/bin/env python3
"""Validate a selected disclosure-route probe, never assign reform exposure."""

import hashlib
import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import UUID


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/calibration/first-wave/substitution-coalition-disclosure-review.json"
RAW = ROOT / "data/raw/nam-coalition-review"
ACTOR = "NATIONAL ASSOCIATION OF MANUFACTURERS"
BLANK_TABLE = ("Name Address Principal Place of Business (city and state or country) "
               "Street Address City State/Province Zip Country City State Country")
PROJECTION_FIELDS = ("filing_uuid", "filing_year", "filing_period", "filing_type",
                     "dt_posted", "filing_document_url", "filing_document_content_type",
                     "affiliated_organizations")


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def project(record):
    return {**{key: record[key] for key in PROJECTION_FIELDS},
            "client": {"name": record["client"]["name"]},
            "registrant": {"name": record["registrant"]["name"]}}


class FormText(HTMLParser):
    """Retain checkbox state while decoding text, entities and blank placeholders."""

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            self.parts.append("[checked]" if "checked" in dict(attrs) else "[unchecked]")


def parse_form(html):
    """Restricted to the reviewed 2008 electronic template; fail on ambiguity.

    This extracts text and checkbox attributes, not a visual or full-form review.
    A blank additions table is not a complete historical affiliation roster.
    """
    parser = FormText()
    parser.feed(html)
    text = " ".join(" ".join(parser.parts).replace("\u200b", "").split())

    def one(pattern):
        matches = re.findall(pattern, text)
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous reviewed HTML field")
        return matches[0]

    registrant = one(r"1\. Registrant Name \[checked\] Organization/Lobbying Firm "
                     r"\[unchecked\] Self Employed Individual (.*?) 2\. Address")
    client = one(r"7\. Client Name \[checked\] Self \[unchecked\] Check if client is a "
                 r"state or local government or instrumentality (.*?) 6\. House ID#")
    period = one(r"8\. Year (\d{4}) Q1 \(1/1 - 3/31\) \[checked\] "
                 r"Q2 \(4/1 - 6/30\) \[unchecked\] Q3 \(7/1 - 9/30\) \[unchecked\] "
                 r"Q4 \(10/1 - 12/31\) \[unchecked\]")
    amended = one(r"9\. Check if this filing amends a previously filed version of this report \[(checked|unchecked)\]")
    website, table = one(r"AFFILIATED ORGANIZATIONS 25\. Add the following affiliated "
                         r"organization\(s\) Internet Address: (https?://\S+) (.*?) 26\. Name")
    if table != BLANK_TABLE:
        raise ValueError("Affiliate additions table differs from reviewed blank template")
    return {"registrantName": registrant, "clientName": client, "clientSelf": True,
            "senateId": one(r"5\. Senate ID# (\S+) 7\. Client Name"),
            "houseId": one(r"6\. House ID# (\S+) TYPE OF REPORT"),
            "year": int(period), "quarter": "Q1", "amendmentChecked": amended == "checked",
            "signedDate": datetime.strptime(
                    one(r"Signature Digitally Signed By: .*? Date (\d{2}/\d{2}/\d{4}) LOBBYING ACTIVITY"),
                    "%m/%d/%Y").date().isoformat(),
            "line25Website": website, "namedTableText": table,
            "line25Scope": "affiliate_additions_not_complete_roster"}


def validate_review(review, frozen_metadata):
    if (review.get("schema") != "substitution-coalition-disclosure-review-v1"
            or review.get("reviewFingerprint") != fingerprint(
                {k: v for k, v in review.items() if k != "reviewFingerprint"})):
        raise ValueError("Stale coalition review fingerprint or schema")
    date.fromisoformat(review["reviewDate"])
    expected_scope = {
        "selection": "purposeful_measurement_probe_outside_frozen_cohort",
        "unit": "filing_version_not_independent_event",
        "independentReviewStatus": "pending",
        "exposureAssignment": "not_assigned",
        "historicalWebsiteContents": "not_acquired",
        "financialVersionSelection": "not_reviewed",
        "causalEffect": "not_identified",
    }
    if any(review.get(key) != value for key, value in expected_scope.items()):
        raise ValueError("Coalition probe cannot promote cohort, exposure, website or review scope")
    query = review["query"]
    parsed = urlparse(query["url"])
    if (parsed.scheme != "https" or parsed.netloc != "lda.gov" or parsed.path != "/api/v1/filings/"
            or parse_qs(parsed.query) != {"client_name": [ACTOR], "filing_year": ["2008"],
                "filing_period": ["first_quarter"], "page_size": ["100"]}
            or query["next"] is not None or query["previous"] is not None
            or not re.fullmatch(r"[a-f0-9]{64}", query["responseSha256"])
            or query["hashConvention"] != "sha256_of_sorted_compact_parsed_response_json_not_http_bytes"):
        raise ValueError("Incomplete or mismatched coalition query provenance")
    records = query["projections"]
    by_id = {r["filing_uuid"]: r for r in records}
    if len(by_id) != len(records) or len(records) != query["count"] or not records:
        raise ValueError("Duplicate, missing or incomplete coalition query inventory")
    for r in records:
        UUID(r["filing_uuid"])
        if (set(r) != set(PROJECTION_FIELDS) | {"client", "registrant"}
                or r["filing_year"] != 2008 or r["filing_period"] != "first_quarter"
                or not isinstance(r["affiliated_organizations"], list)
                or r["filing_document_url"] != f"https://lda.gov/filings/public/filing/{r['filing_uuid']}/print/"):
            raise ValueError("Coalition projection outside query scope")
    exact = [r for r in records if r["client"]["name"] == ACTOR]
    own = {r["filing_uuid"]: r for r in exact if r["registrant"]["name"] == ACTOR}
    forms = review["forms"]
    if (not own or len(forms) != len(own) or {r["filingUuid"] for r in forms} != set(own)
            or {r["filing_type"] for r in own.values()} != {"Q1", "1A"}):
        raise ValueError("Reviewed forms must cover the exact own-registrant selection once")
    if (set(own) & {r["filingUuid"] for r in frozen_metadata}
            or ACTOR in {r["primaryName"] for r in frozen_metadata}):
        raise ValueError("Measurement probe is no longer outside the frozen cohort")
    for row in forms:
        api = own[row["filingUuid"]]
        form = row["form"]
        if (api["affiliated_organizations"] != []
                or api["filing_document_content_type"] != "text/html"
                or api["filing_type"] not in {"Q1", "1A"}
                or form["amendmentChecked"] is not (api["filing_type"] == "1A")
                or form["year"] != 2008 or form["quarter"] != "Q1"
                or form["clientSelf"] is not True
                or (form["registrantName"], form["clientName"], form["senateId"], form["houseId"]) !=
                    ("NATL ASSN OF MANUFACTURERS", "NATL ASSN OF MANUFACTURERS", "26912-12", "316640000")
                or form["namedTableText"] != BLANK_TABLE
                or form["line25Scope"] != "affiliate_additions_not_complete_roster"
                or row["reviewScope"] != "html_text_and_checkbox_attributes_header_and_line25_only"
                or not re.fullmatch(r"[a-f0-9]{64}", row["htmlSha256"])
                or Path(row["documentFile"]).name != row["documentFile"]
                or not row["apiTopLevelKeys"] or len(set(row["apiTopLevelKeys"])) != len(row["apiTopLevelKeys"])
                or "affiliated_organizations" not in row["apiTopLevelKeys"]):
            raise ValueError("Coalition form identity, source field or review boundary mismatch")
        date.fromisoformat(form["signedDate"])
        website = urlparse(form["line25Website"])
        if website.scheme != "http" or website.netloc != "www.nam.org" or not website.path:
            raise ValueError("Missing or invalid reviewed affiliation website")
    return {
        "queryRows": len(records), "exactClientRows": len(exact),
        "otherClientRowsExcluded": len(records) - len(exact), "reviewedOwnRegistrantForms": len(forms),
        "emptyApiAffiliateListsInReviewedForms": len(forms),
        "distinctDisclosedWebpages": len({r["form"]["line25Website"] for r in forms}),
        "reviewedActorPeriods": len({(r["form"]["senateId"], r["form"]["year"], r["form"]["quarter"]) for r in forms}),
        "historicalWebsiteContentsAcquired": 0, "exposureAssignments": 0,
        "independentReviewStatus": review["independentReviewStatus"], "causalEffect": review["causalEffect"],
    }


def verify_raw(review, raw_directory):
    """Reopen preserved acquisitions. Missing files are unavailable, never passes."""
    verified, unavailable = [], []
    cache_path = raw_directory / "query.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
        query = review["query"]
        response = cache["response"]
        if (cache["url"] != query["url"] or cache["retrievedDate"] != review["reviewDate"]
                or cache["responseSha256"] != query["responseSha256"]
                or fingerprint(response) != query["responseSha256"]
                or any(response[key] != query[key] for key in ("count", "next", "previous"))
                or [project(r) for r in response["results"]] != query["projections"]):
            raise ValueError("Raw coalition parsed-response cache mismatch")
        by_id = {r["filing_uuid"]: r for r in response["results"]}
        for row in review["forms"]:
            if sorted(by_id[row["filingUuid"]]) != row["apiTopLevelKeys"]:
                raise ValueError("Raw coalition API key inventory mismatch")
        verified.append("parsed_response_cache")
    else:
        unavailable.append("parsed_response_cache")
    for row in review["forms"]:
        path = raw_directory / row["documentFile"]
        if not path.exists():
            unavailable.append(row["filingUuid"])
            continue
        content = path.read_bytes()
        if (hashlib.sha256(content).hexdigest() != row["htmlSha256"]
                or parse_form(content.decode("utf-8")) != row["form"]):
            raise ValueError("Raw coalition HTML hash or parsed-field mismatch")
        verified.append(row["filingUuid"])
    return {"verified": verified, "unavailable": unavailable}
