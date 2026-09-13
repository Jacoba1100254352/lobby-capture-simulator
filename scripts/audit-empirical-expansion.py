#!/usr/bin/env python3
"""Profile new empirical evidence without promoting it into causal calibration."""

import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
REPORTS = ROOT / "reports"
FIELDS = ["item", "status", "evidence", "remainingRequirement"]


def read(name):
    with (DATA / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def lda_measurement_diagnostics(issue_rows, metadata, reviews, aliases):
    """Audit source measures at filing grain without constructing actor totals."""
    spec = importlib.util.spec_from_file_location("lda_measurement_source", ROOT / "scripts/build-substitution-historical-lda-panel.py")
    lda_source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lda_source)
    by_uuid = {r["filingUuid"]: r for r in metadata}
    if (not metadata or len(by_uuid) != len(metadata)
            or set(by_uuid) != {r["filingUuid"] for r in issue_rows}):
        raise ValueError("Missing, duplicate or off-panel LDA filing metadata")
    lda_source.validate_alias_reviews(aliases, metadata)
    alias_by_id = {r["aliasReviewId"]: r for r in aliases}
    if len(alias_by_id) != len(aliases):
        raise ValueError("Duplicate LDA alias review")
    overlap = defaultdict(set)
    for row in metadata:
        if row["sourceFingerprint"] != lda_source.metadata_fingerprint(row):
            raise ValueError("LDA projected-source fingerprint mismatch")
        income, expenses = (lda_source.dollar_value(row[f]) for f in ("incomeDollars", "expensesDollars"))
        kind = "both" if income and expenses else "income" if income else "expenses" if expenses else "neither"
        same_name = str(bool(row["clientName"]) and lda_source.normalize_name(row["clientName"]) == lda_source.normalize_name(row["registrantName"])).lower()
        if row["amountKind"] != kind or row["sameClientRegistrantName"] != same_name:
            raise ValueError("LDA measurement classification mismatch")
        if row["aliasReviewId"]:
            alias = alias_by_id.get(row["aliasReviewId"])
            if (alias is None or row["canonicalActorId"] != alias["canonicalActorId"]
                    or lda_source.normalize_name(row["clientName"]) != lda_source.normalize_name(alias["aliasName"])
                    or row["clientApiId"] != alias["clientApiId"]
                    or row["registrantApiId"] != alias["registrantApiId"]
                    or not alias["startYear"] <= row["filingYear"] <= alias["endYear"]):
                raise ValueError("LDA alias outside reviewed registration scope")
        elif lda_source.normalize_name(row["clientName"]) != lda_source.normalize_name(row["primaryName"]):
            raise ValueError("Unreviewed LDA actor alias")
        if row["filingType"] not in {"RR", "RA"}:
            overlap[(row["canonicalActorId"], row["periodStart"], row["periodEnd"])].add(kind)
    same_fields = ("canonicalActorId", "primaryName", "filingYear", "filingPeriod", "filingType",
        "periodStart", "periodEnd", "clientName", "registrantName", "dtPosted", "filingDocumentUrl")
    for row in issue_rows:
        source = by_uuid[row["filingUuid"]]
        if (any(row[field] != source[field] for field in same_fields)
                or row["activityAmount"] != lda_source.measurement_amount(source)
                or row["exposureGroup"] != "unassigned_design_candidate"):
            raise ValueError("LDA issue row differs from source measurement or claim boundary")
    seen = set()
    required = ("reviewId", "filingUuid", "sourceFingerprint", "pdfSha256", "pagesReviewed",
        "formRegistrantName", "formClientSelf", "formYear", "formPeriod", "formExpensesDollars",
        "formExpensesMethod", "formAmountDisclosure", "sourceUrl", "reviewer", "reviewDate",
        "reviewScope", "independentReviewStatus")
    methods = Counter()
    for review in reviews:
        if any(not review.get(field) for field in required) or review["filingUuid"] in seen:
            raise ValueError("Missing or duplicate LDA original-form review")
        source = by_uuid.get(review["filingUuid"])
        if (source is None or review["sourceFingerprint"] != source["sourceFingerprint"]
                or not re.fullmatch(r"[a-f0-9]{64}", review["pdfSha256"])
                or review["sourceUrl"] != source["filingDocumentUrl"]
                or review["formYear"] != source["filingYear"] or review["formPeriod"] != source["filingPeriod"]
                or source["amountKind"] != "expenses"
                or Decimal(lda_source.dollar_value(review["formExpensesDollars"])) != Decimal(source["expensesDollars"])
                or review["formExpensesMethod"] not in {"A", "B", "C"}
                or review["formClientSelf"] != "true"
                or review["formAmountDisclosure"] != "at_least_threshold_rounded"
                or review["reviewScope"] != "page_1_identity_amount_method_only"
                or review["independentReviewStatus"] != "pending"):
            raise ValueError("Stale or unsupported LDA original-form measurement review")
        date.fromisoformat(review["reviewDate"])
        methods[review["formExpensesMethod"]] += 1
        seen.add(review["filingUuid"])
    for alias in aliases:
        evidence = [r for r in reviews if r["sourceUrl"] == alias["sourceUrl"] and r["pdfSha256"] == alias["pdfSha256"]]
        if not evidence or any(by_uuid[r["filingUuid"]]["aliasReviewId"] != alias["aliasReviewId"] for r in evidence):
            raise ValueError("LDA alias lacks its source-bound original-form review")
    return {
        "filings": len(metadata), "amountKinds": dict(Counter(r["amountKind"] for r in metadata)),
        "expenseMethodMissing": sum(r["amountKind"] == "expenses" and not r["expensesMethod"] for r in metadata),
        "sourceZeroFilings": sum(any(r[f] and Decimal(r[f]) == 0 for f in ("incomeDollars", "expensesDollars")) for r in metadata),
        "incomeExpenseOverlapActorPeriods": sum({"income", "expenses"} <= kinds for kinds in overlap.values()),
        "aliasFilings": sum(bool(r["aliasReviewId"]) for r in metadata),
        "reviewedForms": len(reviews), "reviewedExpenseMethods": dict(methods),
    }


def lda_date_review_diagnostics(metadata, sources):
    """Reconcile selected covers without inventing corrected posting dates."""
    if (sources.get("schema") != "substitution-lda-date-reviews-v1"
            or sources.get("baselineMetadataFile") != "substitution-lda-filing-metadata.csv"
            or sources.get("independentReviewStatus") != "pending"
            or any(not sources.get(k) for k in ("reviewer", "selection", "sourceAuthentication"))
            or sources.get("reviewFingerprint") != source_fingerprint(
                {k: v for k, v in sources.items() if k != "reviewFingerprint"})):
        raise ValueError("Stale LDA date-review fingerprint or scope")
    date.fromisoformat(sources["reviewDate"])
    by_uuid = {r["filingUuid"]: r for r in metadata}
    expected = {r["filingUuid"] for r in metadata if r["dtPosted"][:10] < r["periodStart"]}
    reviews = sources["reviews"]
    if (len(by_uuid) != len(metadata) or not expected or len(reviews) != len(expected)
            or {r["filingUuid"] for r in reviews} != expected):
        raise ValueError("Missing, duplicate or off-frame LDA date review")
    spec = importlib.util.spec_from_file_location("lda_date_source", ROOT / "scripts/build-substitution-historical-lda-panel.py")
    lda_source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lda_source)
    documentation = sources["apiDocumentation"]
    if (documentation["url"] != "https://lda.gov/api/openapi/v1/"
            or not re.fullmatch(r"[a-f0-9]{64}", documentation["sha256"])
            or documentation["contentType"] != "YAML"
            or not documentation["reviewedLocations"] or not documentation["interpretation"]):
        raise ValueError("Missing LDA date-field documentation provenance")
    fixed_boundary = {
        "reviewScope": "full_embedded_cover_scan_only",
        "registrationMatch": "senate_registrant_and_client_relationship_components",
        "rawMetadataUnchanged": True, "correctedApiPostingDates": 0,
        "amendmentOrderingCleared": False, "amountAggregationCleared": False,
        "controlAssignmentCleared": False, "causalEffect": "not_identified",
    }
    boundary = sources["reviewBoundary"]
    if (any(boundary.get(k) != v for k, v in fixed_boundary.items())
            or not boundary["imageExtraction"] or not boundary["remainingRequirements"]):
        raise ValueError("Unsupported LDA date-review promotion")
    methods = Counter()
    censored = missing_termination = differing_names = 0
    for review in reviews:
        source = by_uuid[review["filingUuid"]]
        if (review["sourceFingerprint"] != source["sourceFingerprint"]
                or source["sourceFingerprint"] != lda_source.metadata_fingerprint(source)
                or any(not re.fullmatch(r"[a-f0-9]{64}", review[k]) for k in
                       ("responseSha256", "pdfSha256", "embeddedCoverPngSha256"))
                or not isinstance(review["pdfPages"], int) or review["pdfPages"] < 2
                or not review["scanIdentifier"]):
            raise ValueError("Stale LDA source or missing cover provenance")
        projection = {
            "filing_uuid": source["filingUuid"], "filing_type": source["filingType"],
            "filing_year": int(source["filingYear"]), "filing_period": source["filingPeriod"],
            "dt_posted": source["dtPosted"], "income": source["incomeDollars"] or None,
            "expenses": source["expensesDollars"] or None, "expenses_method": source["expensesMethod"] or None,
            "termination_date": source["terminationDate"] or None,
            "registrant": {"id": int(source["registrantApiId"]), "name": source["registrantName"]},
            "client": {"id": int(source["clientApiId"]), "client_id": int(source["clientRelationshipId"]), "name": source["clientName"]},
        }
        if review["apiProjection"] != projection:
            raise ValueError("LDA API projection differs from frozen metadata")
        form = review["form"]
        if (not form["registrantName"] or not form["houseId"] or not form["notes"]
                or form["senateId"] != source["registrantApiId"] + "-" + source["clientRelationshipId"]
                or form["year"] != int(source["filingYear"]) or form["period"] != source["filingPeriod"]
                or form["amendmentBoxChecked"] is not False
                or (form["period"], form["terminationBoxChecked"]) != {
                    "MM": ("mid_year", False), "YY": ("year_end", False),
                    "YT": ("year_end", True)}.get(source["filingType"])):
            raise ValueError("LDA cover registration, period or report-type mismatch")
        receipt = date.fromisoformat(form["receiptDate"])
        if (receipt <= date.fromisoformat(source["periodEnd"])
                or not form["receiptStamp"].startswith(receipt.strftime("%y %b %d").upper())
                or form["receiptTimezone"] != "not_stated"):
            raise ValueError("LDA receipt chronology, stamp or timezone mismatch")
        if form["terminationBoxChecked"]:
            if date.fromisoformat(form["terminationDate"]) > receipt:
                raise ValueError("Termination date follows receipt")
            missing_termination += not source["terminationDate"]
        elif form["terminationDate"] is not None:
            raise ValueError("Unchecked termination cannot supply a date")
        differing_names += lda_source.normalize_name(form["registrantName"]) != lda_source.normalize_name(source["registrantName"])
        if form["amountKind"] == "expenses":
            if (source["amountKind"] != "expenses" or form["clientSelf"] is not True
                    or form["clientName"] is not None or form["expensesMethod"] not in {"A", "B", "C"}
                    or form["reportedAmountDollars"] != source["expensesDollars"]
                    or form["amountDisclosure"] not in {"at_least_threshold_rounded", "numeric_amount_threshold_boxes_unchecked"}
                    or form["incomeUpperBoundExclusiveDollars"] is not None):
                raise ValueError("Unsupported reviewed expense amount or method")
            methods[form["expensesMethod"]] += 1
        elif form["amountKind"] == "income":
            if (source["amountKind"] != "income" or source["incomeDollars"] != "0.00"
                    or form["clientSelf"] is not False
                    or lda_source.normalize_name(form["clientName"]) != lda_source.normalize_name(source["clientName"])
                    or form["reportedAmountDollars"] is not None or form["expensesMethod"] is not None
                    or form["amountDisclosure"] != "less_than_threshold_censored"
                    or form["incomeUpperBoundExclusiveDollars"] != "10000.00"):
                raise ValueError("Censored income cannot become a point zero or expense")
            censored += 1
        else:
            raise ValueError("Unknown reviewed LDA amount kind")
    return {
        "postingBeforeCoveredPeriod": len(expected), "reviewedEmbeddedCovers": len(reviews),
        "receiptDatesAfterPeriod": len(reviews), "registrationComponentMatches": len(reviews),
        "differentRegistrantNames": differing_names, "reviewedExpenseMethods": dict(methods),
        "censoredIncomeDisclosures": censored, "sourceMissingTerminationDates": missing_termination,
        "correctedApiPostingDates": 0, "amendmentOrderingCleared": False,
        "controlAssignmentCleared": False, "causalEffect": "not_identified",
    }


def report_period_diagnostics(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["committeeId"]].append(row)
    overlaps = gaps = straddles = 0
    for periods in groups.values():
        through = None
        for row in sorted(periods, key=lambda r: (r["periodStart"], r["periodEnd"])):
            start, end = date.fromisoformat(row["periodStart"]), date.fromisoformat(row["periodEnd"])
            if end < start:
                raise ValueError("Reversed report period")
            if through is not None:
                overlaps += start <= through
                gaps += start > through + timedelta(days=1)
            through = max(through, end) if through else end
            # Periods crossing a half-year cannot be allocated using their totals.
            straddles += (start.year, start.month > 6) != (end.year, end.month > 6)
    return overlaps, gaps, straddles


def comment_position_diagnostics(rows, sources):
    """Keep public-copy agreement separate from verified submission uptake."""
    if sources.get("schema") != "comment-position-source-v1" or not rows:
        raise ValueError("Missing comment-position source product")
    records = sources["records"]
    by_id = {record["commentId"]: record for record in records}
    if not records or len(by_id) != len(records):
        raise ValueError("Missing or duplicate comment metadata")
    for record in records:
        fingerprint = hashlib.sha256(json.dumps(
            {key: value for key, value in record.items() if key != "sourceFingerprint"},
            sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if (fingerprint != record["sourceFingerprint"]
                or not re.fullmatch(r"[a-f0-9]{64}", record["responseSha256"])):
            raise ValueError("Comment metadata fingerprint mismatch")
        attrs = record["attributes"]
        if (not record["commentId"].startswith(attrs["docketId"] + "-")
                or record["requestUrl"] != "https://api.regulations.gov/v4/comments/"
                + record["commentId"] + "?include=attachments"):
            raise ValueError("Comment metadata identity mismatch")
        for field in ("receiveDate", "postedDate"):
            if attrs[field] is not None:
                date.fromisoformat(attrs[field][:10])
        attachments = record["attachments"]
        if len({item["id"] for item in attachments}) != len(attachments):
            raise ValueError("Duplicate comment attachment metadata")
        for item in attachments:
            for fmt in item["fileFormats"]:
                if not fmt["fileUrl"].startswith(
                        "https://downloads.regulations.gov/" + record["commentId"] + "/"):
                    raise ValueError("Attachment belongs to another comment")
    copy = sources["publicCopy"]
    if (copy["candidateCommentId"] not in by_id
            or copy["jointSubmissionCommentId"] not in by_id
            or copy["candidateCommentId"] == copy["jointSubmissionCommentId"]
            or copy["jointSubmissionContentsRead"] is not False
            or copy["docketVersionMatch"] != "not_established"
            or copy["independentReviewStatus"] != "pending"
            or not re.fullmatch(r"[a-f0-9]{64}", copy["htmlSha256"])
            or not copy["url"].startswith("https://protectnps.org/")):
        raise ValueError("Unsupported public-copy source or docket match")
    rules = sources["ruleSources"]
    review_source_fingerprint = hashlib.sha256(json.dumps(
        {key: sources[key] for key in ("publicCopy", "ruleSources")},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not rules["proposed"]["date"] < copy["letterDate"] < rules["final"]["date"]:
        raise ValueError("Comment-position chronology is invalid")
    for source in rules.values():
        if (not re.fullmatch(r"[a-f0-9]{64}", source["pdfSha256"])
                or not source["sourcePage"].isdigit()
                or not isinstance(source["pdfPage"], int) or source["pdfPage"] < 1
                or not source["section"] or not source["reviewScope"]
                or not source["url"].startswith("https://www.govinfo.gov/content/pkg/")):
            raise ValueError("Missing rule-page provenance")
        date.fromisoformat(source["date"])
        date.fromisoformat(source["visualReviewDate"])
    seen = set()
    seen_issues = set()
    for row in rows:
        issue_key = (row["copySourceId"], row["positionCode"])
        if not row["positionId"] or row["positionId"] in seen or issue_key in seen_issues:
            raise ValueError("Missing or duplicate public-copy position")
        seen.add(row["positionId"])
        seen_issues.add(issue_key)
        candidate = by_id.get(row["candidateCommentId"])
        if (candidate is None or row["candidateCommentId"] != copy["candidateCommentId"]
                or row["metadataFingerprint"] != candidate["sourceFingerprint"]
                or row["reviewSourceFingerprint"] != review_source_fingerprint
                or row["docketId"] != candidate["attributes"]["docketId"]
                or row["copySourceId"] != copy["sourceId"]):
            raise ValueError("Public-copy candidate identity mismatch")
        if (row["unit"] != "public_copy_issue"
                or any(row[field] != "not_established" for field in (
                    "docketVersionMatch", "agencyResponseLink", "uptake", "regulatoryTextChange"))
                or row["independentReviewStatus"] != "pending"
                or row["reviewer"] != copy["reviewer"] or row["reviewDate"] != copy["reviewDate"]
                or not row["copyReviewLocation"] or not row["claimBoundary"]):
            raise ValueError("Public-copy position must not be promoted to uptake")
        date.fromisoformat(row["reviewDate"])
        for field in ("positionCode", "proposedActionCode", "finalActionCode"):
            if row[field] not in {"partial_disapproval", "approve_monitoring"}:
                raise ValueError("Unsupported public-copy position code")
    return {
        "positionRows": len(rows), "publicLetters": len({r["copySourceId"] for r in rows}),
        "candidateDocketSubmissions": len({r["candidateCommentId"] for r in rows}),
        "alignedWithProposal": sum(r["positionCode"] == r["proposedActionCode"] for r in rows),
        "alignedWithFinalAction": sum(r["positionCode"] == r["finalActionCode"] for r in rows),
        "changedActionsAtCodedScope": sum(r["proposedActionCode"] != r["finalActionCode"] for r in rows),
        "verifiedDocketVersionMatches": 0, "observedUptakeLinks": 0,
    }


def source_fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def comment_response_diagnostics(rows, sources):
    """Audit saved documentary links, not original attachment bytes or causality."""
    if (sources.get("schema") != "comment-response-document-source-v1" or not rows
            or sources.get("unit") != "comment_request"
            or sources.get("independentReviewStatus") != "pending"):
        raise ValueError("Missing or unsupported comment-response pilot")
    review_date = date.fromisoformat(sources["reviewDate"])
    if any(not sources.get(key) for key in ("reviewer", "selection", "studyScope", "sourceAuthentication")):
        raise ValueError("Missing comment-response scope")
    rtc = sources["responseDocument"]
    if (rtc["datePrecision"] != "month" or not re.fullmatch(r"\d{4}-\d{2}", rtc["date"])
            or not isinstance(rtc["pdfPageCount"], int) or rtc["pdfPageCount"] < 1
            or not rtc["url"].startswith("https://www.epa.gov/system/files/documents/")
            or any(not rtc.get(key) for key in ("section", "excerptScope", "chronologyCaveat", "priorityCaveat"))):
        raise ValueError("Invalid response-document provenance")
    rtc_month_start = date.fromisoformat(rtc["date"] + "-01")
    rules = sources["ruleSources"]
    if set(rules) != {"proposed", "final", "correction"}:
        raise ValueError("Missing historical rule sources")
    rule_dates = {key: date.fromisoformat(value["date"]) for key, value in rules.items()}
    if not rule_dates["proposed"] < rtc_month_start < rule_dates["final"] < rule_dates["correction"] <= review_date:
        raise ValueError("Invalid historical rule chronology")
    for document in [rtc, *rules.values()]:
        if (not re.fullmatch(r"[a-f0-9]{64}", document["pdfSha256"])
                or not document["documentId"] or not document["reviewScope"]):
            raise ValueError("Missing reviewed PDF provenance")
        pages = document["reviewedPages"]
        if not pages or len({p["pdfPage"] for p in pages}) != len(pages):
            raise ValueError("Missing or duplicate reviewed PDF pages")
        for page in pages:
            if (type(page["pdfPage"]) is not int or page["pdfPage"] < 1
                    or not str(page["printedPage"]).isdigit() or int(page["printedPage"]) < 1
                    or (document is rtc and page["pdfPage"] > rtc["pdfPageCount"])):
                raise ValueError("Invalid reviewed PDF page")
        if document is not rtc and document["url"] != (
                "https://www.govinfo.gov/content/pkg/FR-" + document["date"]
                + "/pdf/" + document["documentId"] + ".pdf"):
            raise ValueError("Rule URL/date/identity mismatch")
    page_map = {p["pdfPage"]: p["printedPage"] for p in rtc["reviewedPages"]}
    comparison = sources["regulatoryComparison"]
    if (comparison["textDifferenceObserved"] is not True
            or comparison["tractorEligibility"] != "agency_clarifies_continuation"
            or comparison["causalAttribution"] != "not_established"
            or not comparison["interpretation"] or not comparison["correctionBoundary"]
            or any(page_map.get(p["pdfPage"]) != p["printedPage"] for p in comparison["collectiveResponsePages"])):
        raise ValueError("Unsupported regulatory text attribution")
    records = sources["records"]
    by_id = {record["commentId"]: record for record in records}
    if not records or len(by_id) != len(records):
        raise ValueError("Missing or duplicate response-pilot metadata")
    for record in records:
        if (record["sourceFingerprint"] != source_fingerprint(
                {k: v for k, v in record.items() if k != "sourceFingerprint"})
                or not re.fullmatch(r"[a-f0-9]{64}", record["responseSha256"])):
            raise ValueError("Response-pilot metadata fingerprint mismatch")
        attrs = record["attributes"]
        if (attrs["docketId"] != sources["docketId"] or attrs["agencyId"] != "EPA"
                or attrs["withdrawn"] is not False or not attrs["title"]
                or not record["commentId"].startswith(sources["docketId"] + "-")
                or record["metadataUrl"] != "https://api.regulations.gov/v4/comments/"
                + record["commentId"] + "?include=attachments"):
            raise ValueError("Response-pilot comment identity mismatch")
        for key in ("receiveDate", "postedDate"):
            if not isinstance(attrs.get(key), str) or not attrs[key]:
                raise ValueError("Missing comment receipt/posting date")
        received, posted = (date.fromisoformat(attrs[k][:10]) for k in ("receiveDate", "postedDate"))
        if not rule_dates["proposed"] <= received <= posted < rtc_month_start:
            raise ValueError("Invalid comment receipt/posting chronology")
        attachments = record["attachments"]
        if (not attachments or len({a["id"] for a in attachments}) != len(attachments)
                or len({a["attributes"]["docOrder"] for a in attachments}) != len(attachments)):
            raise ValueError("Missing or duplicate comment attachments")
        for attachment in attachments:
            attr = attachment["attributes"]
            order = attr["docOrder"]
            if type(order) is not int or order < 1 or not attr["fileFormats"]:
                raise ValueError("Invalid attachment order or formats")
            for fmt in attr["fileFormats"]:
                if (fmt["format"] != "pdf" or type(fmt["size"]) is not int or fmt["size"] <= 0
                        or fmt["fileUrl"] != "https://downloads.regulations.gov/"
                        + record["commentId"] + f"/attachment_{order}.pdf"):
                    raise ValueError("Attachment URL/order/comment mismatch")
    reviews = {r["observationId"]: r for r in sources["reviews"]}
    if (len(reviews) != len(sources["reviews"]) or len(rows) != len(reviews)
            or {r["observationId"] for r in rows} != set(reviews)):
        raise ValueError("Missing, duplicate or off-cohort response observations")
    expected_dispositions = {
        "tractor_credit_scope": "clarified_existing_scope",
        "lhd_calculation_error": "disagreed_with_error_claim",
    }
    fixed = {
        "unit": "comment_request", "requestRepresentation": "agency_reproduced_excerpt",
        "responseLink": "explicit_named_response", "originalAttachmentRead": "false",
        "docketVersionMatch": "not_established", "uptakeRateEligible": "false",
        "causalEffect": "not_identified", "regulatoryTextChangeAttribution": "not_established",
        "independentReviewStatus": "pending",
    }
    same_fields = ("commentId", "attachmentOrder", "attachmentId", "requestCode", "requestPdfPage",
                   "requestPrintedPage", "originalCitedPages", "responsePdfPage", "responsePrintedPage", "disposition")
    seen_requests = set()
    for row in rows:
        review = reviews[row["observationId"]]
        record = by_id.get(row["commentId"])
        if (record is None or row["metadataFingerprint"] != record["sourceFingerprint"]
                or row["reviewSourceFingerprint"] != source_fingerprint(sources)
                or row["docketId"] != sources["docketId"]
                or any(row[field] != str(review[field]) for field in same_fields)):
            raise ValueError("Stale response review fingerprint or identity")
        request_key = (row["commentId"], row["requestCode"])
        if request_key in seen_requests:
            raise ValueError("Duplicate comment request")
        seen_requests.add(request_key)
        if (any(row.get(field) != value for field, value in fixed.items())
                or row["reviewer"] != sources["reviewer"] or row["reviewDate"] != sources["reviewDate"]
                or review["originalAttachmentAccess"] != "HTTP_403"
                or review["disposition"] != expected_dispositions.get(review["requestCode"])
                or any(not review.get(key) for key in ("requestSummary", "responseSummary", "responseAnchor", "claimBoundary"))):
            raise ValueError("Unsupported response-pilot claim or coding")
        for prefix in ("request", "response"):
            if page_map.get(review[prefix + "PdfPage"]) != review[prefix + "PrintedPage"]:
                raise ValueError("Response review cites an unreviewed or mismatched page")
        if not re.fullmatch(r"[1-9]\d*(?:-[1-9]\d*)?", review["originalCitedPages"]):
            raise ValueError("Missing original page citation in agency excerpt")
        matches = [a for a in record["attachments"] if a["id"] == review["attachmentId"]
                   and a["attributes"]["docOrder"] == review["attachmentOrder"]]
        if len(matches) != 1:
            raise ValueError("Response review attachment identity/order mismatch")
    if set(by_id) != {r["commentId"] for r in rows}:
        raise ValueError("Off-cohort comment metadata")
    return {
        "requestRows": len(rows), "submissions": len(by_id), "dockets": len({r["docketId"] for r in rows}),
        "explicitNamedResponses": sum(r["responseLink"] == "explicit_named_response" for r in rows),
        "dispositions": dict(Counter(r["disposition"] for r in rows)),
        "originalAttachmentsRead": sum(r["originalAttachmentRead"] == "true" for r in rows),
        "rateEligibleRequests": sum(r["uptakeRateEligible"] == "true" for r in rows),
        "independentlyReviewedRequests": sum(r["independentReviewStatus"] == "complete" for r in rows),
        "causalEffect": "not_identified",
    }


def comment_section_rows(sources):
    """Project the reviewed section inventory, not a full-comment population."""
    blocks = {b["blockId"]: b for b in sources["organizationBlocks"]}
    document = sources["responseDocument"]
    offset = document["firstPdfPage"] - document["firstPrintedPage"]
    fingerprint = source_fingerprint(sources)
    rows = []
    for request in sources["requests"]:
        block = blocks[request["blockId"]]
        rows.append({
            "requestId": request["requestId"], "organizationBlockId": block["blockId"],
            "organization": block["organization"], "citedCommentId": block["citedCommentId"],
            "citedAttachmentOrder": str(block["attachmentOrder"]),
            **{key: request[key] for key in ("requestCode", "requestSummary", "originalCitedPages",
                "responseLink", "responseGroupId", "disposition", "codingRationale",
                "conditionalOnRequestId", "priorPilotObservationId")},
            "requestPdfPages": ";".join(map(str, request["requestPdfPages"])),
            "requestPrintedPages": ";".join(str(p - offset) for p in request["requestPdfPages"]),
            "responseReviewedPdfPages": ";".join(map(str, request["responsePdfPages"])),
            "unit": sources["unit"], "originalAttachmentRead": "false",
            "docketVersionMatch": "not_established", "docketRateEligible": "false",
            "causalEffect": "not_identified", "regulatoryTextChangeAttribution": "not_established",
            "sourceUrl": document["url"], "sourcePdfSha256": document["pdfSha256"],
            "reviewSourceFingerprint": fingerprint,
            **{key: sources[key] for key in ("reviewer", "reviewDate", "independentReviewStatus")},
        })
    return rows


def comment_section_diagnostics(rows, sources, pilot_sources):
    """Check retrospective excerpt coverage and coding boundaries, not causality."""
    if (sources.get("schema") != "comment-section-inventory-source-v1"
            or sources.get("unit") != "distinct_request_within_agency_selected_section"
            or sources.get("independentReviewStatus") != "pending"
            or sources.get("docketId") != pilot_sources["docketId"]
            or any(not sources.get(k) for k in ("reviewer", "selection", "studyScope",
                "sourceAuthentication", "remainingReview"))):
        raise ValueError("Missing section inventory provenance or claim boundary")
    date.fromisoformat(sources["reviewDate"])
    document = sources["responseDocument"]
    if (any(document[k] != pilot_sources["responseDocument"][k]
            for k in ("documentId", "url", "pdfSha256", "pdfPageCount", "section"))
            or document["reviewedSectionPdfPages"] != list(range(457, 463))
            or [document[k] for k in ("firstPdfPage", "lastPdfPage", "firstPrintedPage", "lastPrintedPage")]
                != [457, 462, 439, 444]
            or document["responsePdfPages"] != [461, 462]
            or document["fullDocumentReviewed"] is not False
            or not document["boundaryReview"] or not document["responseScope"]):
        raise ValueError("Incomplete section pages or mismatched response-document source")
    codebook = sources["codebook"]
    fixed = {"originalAttachmentRead": False, "docketVersionMatch": "not_established",
        "docketRateEligible": False, "causalEffect": "not_identified",
        "regulatoryTextChangeAttribution": "not_established"}
    if (any(codebook.get(k) != v for k, v in fixed.items())
            or any(not codebook.get(k) for k in ("version", "segmentation", "deduplication", "exclusions"))):
        raise ValueError("Unsupported section inventory claim or missing codebook")
    blocks = sources["organizationBlocks"]
    # Source-specific fixed frame, independently reviewable in the six PDF pages.
    block_frame = [("allison", "1657", 2), ("carb", "1591", 1), ("china", "1658", 2),
                   ("cummins", "1598", 1), ("dtna", "1555", 1), ("paccar", "1607", 1),
                   ("volvo", "1606", 1)]
    if [(b["blockId"], b["citedCommentId"], b["attachmentOrder"]) for b in blocks] != [
            (key, sources["docketId"] + "-" + suffix, order) for key, suffix, order in block_frame]:
        raise ValueError("Missing, duplicate or mismatched organization-block frame")
    by_block = {b["blockId"]: b for b in blocks}
    for block in blocks:
        if (not block["organization"] or not block["pdfPages"]
                or block["pdfPages"] != sorted(set(block["pdfPages"]))
                or not set(block["pdfPages"]) <= set(document["reviewedSectionPdfPages"])
                or block["namedInSectionSummary"] is not (block["blockId"] != "carb")):
            raise ValueError("Invalid organization-block pages or summary coverage")
    requests = sources["requests"]
    by_id = {r["requestId"]: r for r in requests}
    request_frame = {
        "allison": {"lhd_calculation_error"},
        "carb": {"require_ci_multipurpose_for_engineless_vehicles"},
        "china": {"explain_table_ii19_method_and_sources", "explain_international_comparability"},
        "cummins": {"tractor_credit_scope"},
        "dtna": {"allow_engineering_judgment_subcategory", "remove_zev_averaging_set_limits"},
        "paccar": {"retain_intended_use_subcategory", "conditional_delay_to_my2030"},
        "volvo": {"reevaluate_vocational_standard_setting", "reevaluate_zev_categorization"},
    }
    if (not requests or len(by_id) != len(requests)
            or {r["blockId"] for r in requests} != set(by_block)
            or {(r["blockId"], r["requestCode"]) for r in requests}
                != {(block, code) for block, codes in request_frame.items() for code in codes}
            or len({(r["blockId"], r["requestCode"]) for r in requests}) != len(requests)):
        raise ValueError("Missing or duplicate section requests")
    link_dispositions = {
        "explicit_named_response": {"disagreed_with_error_claim", "clarified_existing_scope", "explained_comparability_limit"},
        "named_summary_collective_response": {"consistent_with_collective_revision"},
        "section_resolution_only": {"inconsistent_with_described_resolution"},
        "no_request_specific_disposition": {"no_request_specific_disposition", "conditional_fallback_not_separately_resolved"},
    }
    pilot_reviews = {r["observationId"]: r for r in pilot_sources["reviews"]}
    prior_ids = []
    for request in requests:
        block = by_block[request["blockId"]]
        if (any(not request.get(k) for k in ("requestId", "requestCode", "requestSummary", "codingRationale"))
                or not request["requestPdfPages"]
                or request["requestPdfPages"] != sorted(set(request["requestPdfPages"]))
                or not set(request["requestPdfPages"]) <= set(block["pdfPages"])
                or not request["responsePdfPages"]
                or request["responsePdfPages"] != sorted(set(request["responsePdfPages"]))
                or not set(request["responsePdfPages"]) <= set(document["responsePdfPages"])
                or not re.fullmatch(r"[1-9]\d*(?:-[1-9]\d*)?(?:;[1-9]\d*(?:-[1-9]\d*)?)*", request["originalCitedPages"])):
            raise ValueError("Missing request coding or invalid reviewed page citation")
        link, disposition = request["responseLink"], request["disposition"]
        if (link not in codebook["responseLinkCodes"] or disposition not in codebook["dispositionCodes"]
                or disposition not in link_dispositions.get(link, set())
                or (link == "named_summary_collective_response" and not block["namedInSectionSummary"])):
            raise ValueError("Unsupported section response-link coding")
        if link == "explicit_named_response":
            expected = {"allison": "disagreed_with_error_claim", "cummins": "clarified_existing_scope",
                        "china": "explained_comparability_limit"}
            if (disposition != expected.get(block["blockId"])
                    or request["responseGroupId"] != "s25-" + block["blockId"]):
                raise ValueError("Section coding does not support an explicit named response")
        elif disposition == "no_request_specific_disposition":
            if request["responseGroupId"]:
                raise ValueError("Unresolved request cannot invent a matched response group")
        elif request["responseGroupId"] != "s25-collective-vocational":
            raise ValueError("Shared section response cannot become independent outcomes")
        parent_id = request["conditionalOnRequestId"]
        if parent_id:
            parent = by_id.get(parent_id)
            if (parent is None or parent_id == request["requestId"] or parent["conditionalOnRequestId"]
                    or parent["blockId"] != request["blockId"]
                    or disposition != "conditional_fallback_not_separately_resolved"):
                raise ValueError("Invalid conditional fallback parent or disposition")
        elif disposition == "conditional_fallback_not_separately_resolved":
            raise ValueError("Conditional fallback lacks its parent request")
        prior_id = request["priorPilotObservationId"]
        if prior_id:
            prior = pilot_reviews.get(prior_id)
            if (prior is None or block["citedCommentId"] != prior["commentId"]
                    or block["attachmentOrder"] != prior["attachmentOrder"]
                    or any(request[k] != prior[k] for k in ("requestCode", "originalCitedPages", "disposition"))
                    or prior["requestPdfPage"] not in request["requestPdfPages"]
                    or prior["responsePdfPage"] not in request["responsePdfPages"]):
                raise ValueError("Section request does not match prior pilot identity/coding")
            prior_ids.append(prior_id)
    if len(prior_ids) != len(pilot_reviews) or set(prior_ids) != set(pilot_reviews):
        raise ValueError("Prior pilot overlap must be retained exactly once")
    appendix = sources["appendixSelectionContext"]
    distribution = appendix["issueCountDistribution"]
    if (appendix["reviewedPages"] != [{"pdfPage": 2050, "printedPage": 2032}, {"pdfPage": 2051, "printedPage": 2033}]
            or appendix["individualListReviewed"] is not False
            or appendix["nonresponseDenominatorEligible"] is not False
            or not appendix["scope"] or not appendix["interpretation"] or not appendix["sourcePercentageCaveat"]
            or [r["issues"] for r in distribution] != [0, 1, 2, 3, 4]
            or any(type(r["comments"]) is not int or r["comments"] < 0 for r in distribution)
            or len(appendix["themeCounts"]) != 8
            or any(type(n) is not int or n < 0 for n in appendix["themeCounts"].values())
            or sum(r["comments"] for r in distribution) != appendix["agencyReportedCommentsNotReproduced"]
            or sum(r["issues"] * r["comments"] for r in distribution) != appendix["reportedThemeIncidences"]
            or sum(appendix["themeCounts"].values()) != appendix["reportedThemeIncidences"]):
        raise ValueError("Appendix selection counts or nonresponse boundary mismatch")
    if rows != comment_section_rows(sources):
        raise ValueError("Section CSV projection or review fingerprint mismatch")
    return {
        "organizationBlocks": len(blocks), "requestRows": len(rows),
        "coveredSectionPdfPages": len(document["reviewedSectionPdfPages"]),
        "priorPilotOverlap": len(prior_ids),
        "responseLinks": dict(Counter(r["responseLink"] for r in requests)),
        "dispositions": dict(Counter(r["disposition"] for r in requests)),
        "conditionalFallbacks": sum(bool(r["conditionalOnRequestId"]) for r in requests),
        "appendixCommentsNotReproduced": appendix["agencyReportedCommentsNotReproduced"],
        "appendixThemeIncidences": appendix["reportedThemeIncidences"],
        "docketRateEligibleRequests": 0, "independentlyReviewedRequests": 0,
        "causalEffect": "not_identified",
    }


def comment_followup_diagnostics(sources, baseline, pilot_sources):
    """Keep a later cross-section review separate from its original sample."""
    if (sources.get("schema") != "comment-request-followups-v1"
            or sources.get("baselineSourceFile") != "comment-section-inventory-source.json"
            or sources.get("baselineSourceFingerprint") != source_fingerprint(baseline)
            or sources.get("reviewFingerprint") != source_fingerprint(
                {k: v for k, v in sources.items() if k != "reviewFingerprint"})
            or sources.get("independentReviewStatus") != "pending"
            or any(not sources.get(k) for k in ("reviewer", "selection", "studyScope", "sourceAuthentication"))):
        raise ValueError("Stale follow-up fingerprint, baseline or review boundary")
    date.fromisoformat(sources["reviewDate"])
    documents = sources["documents"]
    expected_pages = {"response": [1425, 1426, 1430, 1431, 1432, 1433, 1434],
                      "proposed": [88], "final": [337, 351]}
    offsets = {"response": 18, "proposed": -25925, "final": -29439}
    if set(documents) != set(expected_pages):
        raise ValueError("Missing follow-up source documents")
    for key, document in documents.items():
        previous = (pilot_sources["responseDocument"] if key == "response"
                    else pilot_sources["ruleSources"][key])
        if (any(document[k] != previous[k] for k in ("documentId", "url", "pdfSha256"))
                or document["reviewedPages"] != [
                    {"pdfPage": p, "printedPage": p - offsets[key]} for p in expected_pages[key]]
                or not document["reviewScope"]
                or (key != "response" and document["date"] != previous["date"])):
            raise ValueError("Follow-up source identity or page mapping mismatch")
    reviews = sources["reviews"]
    if len(reviews) != 1 or reviews[0]["followupId"] != "s25-dtna-averaging-s1032":
        raise ValueError("Missing, duplicate or undeclared follow-up frame")
    review = reviews[0]
    base_by_id = {r["requestId"]: r for r in baseline["requests"]}
    base_request = base_by_id.get(review["baselineRequestId"])
    if base_request is None:
        raise ValueError("Follow-up request missing from baseline")
    block = next(b for b in baseline["organizationBlocks"] if b["blockId"] == base_request["blockId"])
    if (review["baselineRequestId"] != "s25-dtna-averaging"
            or review["citedCommentId"] != block["citedCommentId"]
            or review["attachmentOrder"] != block["attachmentOrder"]
            or review["requestCode"] != base_request["requestCode"]
            or review["baselineDisposition"] != base_request["disposition"]
            or review["baselineDisposition"] != "no_request_specific_disposition"
            or review["baselineSection"] != baseline["responseDocument"]["section"]
            or review["followupSection"] != documents["response"]["section"]
            or review["followupSection"] != "10.3.2 Averaging Set"
            or review["requestPdfPages"] != [1425, 1426]
            or review["summaryPdfPages"] != [1430, 1431, 1432]
            or review["responsePdfPages"] != [1432, 1433, 1434]
            or review["originalCitedPages"] != "74-75;171"):
        raise ValueError("Cross-section request identity, baseline or page mismatch")
    fixed = {
        "requestMatch": "same_cited_submission_attachment_and_requested_action",
        "responseLink": "named_summary_collective_response",
        "responseGroupId": "phase3-s1032-interim-transfer",
        "disposition": "partial_alignment_with_interim_flexibility",
        "proposalAlreadySolicitedOption": True, "proposalWasAdoptedRule": False,
        "historicalFinalUseThroughModelYear": 2032,
        "specifiedPre2027AdvancedTechnologyCreditsIncluded": True,
        "unchangedBaseline": True, "addsIndependentRequest": False,
        "originalAttachmentRead": False, "docketVersionMatch": "not_established",
        "docketRateEligible": False, "causalEffect": "not_identified",
        "regulatoryTextChangeAttribution": "not_established", "independentReviewStatus": "pending",
    }
    if (any(review.get(k) != v for k, v in fixed.items())
            or any(not review.get(k) for k in ("matchRationale", "responseSummary", "proposalContext", "remainingRequirements"))):
        raise ValueError("Unsupported follow-up scope, attribution or temporal coding")
    facets = review["facets"]
    expected_facets = {
        "vehicle_transfer_permission": "aligned_with_limited_vehicle_transfer",
        "program_life_duration": "narrower_time_limit",
        "traded_credit_eligibility": "aligned_subject_to_retained_restrictions",
        "no_credit_discount": "no_separate_discount_disposition_verified",
    }
    if len(facets) != len(expected_facets) or {f["facet"]: f["assessment"] for f in facets} != expected_facets:
        raise ValueError("Unsupported or duplicated follow-up facet assessment")
    for facet in facets:
        if (not facet["requested"] or not facet["observed"] or facet["evidenceDocument"] != "final"
                or not facet["evidencePdfPages"]
                or facet["evidencePdfPages"] != sorted(set(facet["evidencePdfPages"]))
                or not set(facet["evidencePdfPages"]) <= set(expected_pages["final"])):
            raise ValueError("Follow-up facet lacks reviewed clause evidence")
    return {
        "followupReviews": len(reviews), "baselineRequests": len(base_by_id),
        "newIndependentRequests": 0, "crossSectionResponseLinks": 1,
        "requestFacets": len(facets), "disposition": review["disposition"],
        "proposalAlreadySolicitedOption": review["proposalAlreadySolicitedOption"],
        "historicalFinalUseThroughModelYear": review["historicalFinalUseThroughModelYear"],
        "docketRateEligibleRequests": 0, "independentlyReviewedFollowups": 0,
        "causalEffect": "not_identified",
    }


def protest_linkage_diagnostics(rows, sources, frozen):
    """Verify a selected decision-to-award bridge, never a protest-rate frame."""
    review = sources["gaoReview"]
    expected = set(review["piids"])
    if not rows or len(rows) != len(expected) or {r["piid"] for r in rows} != expected:
        raise ValueError("Missing, duplicate or off-cohort protest award links")
    searches = [sources["awardSearch"], sources["transactionSearch"]]
    for search in searches:
        if search["response"]["page_metadata"]["hasNext"]:
            raise ValueError("Incomplete selected-award source pagination")
        records = search["response"]["results"]
        if len(records) != len(expected) or {r["Award ID"] for r in records} != expected:
            raise ValueError("Selected source does not contain one record per pilot award")
    awards = {r["Award ID"]: r for r in searches[0]["response"]["results"]}
    actions = {r["Award ID"]: r for r in searches[1]["response"]["results"]}
    details = {r["response"]["piid"]: r["response"] for r in sources["awardDetails"]}
    if len(sources["awardDetails"]) != len(expected) or set(details) != expected:
        raise ValueError("Missing or duplicate selected-award detail records")
    bulk_records = sources["bulkExtract"]["records"]
    if len(bulk_records) != len(expected) or {r["piid"] for r in bulk_records} != expected:
        raise ValueError("Missing or duplicate archived bulk extract records")
    bulk = {r["piid"]: r for r in bulk_records}
    def normalize_name(value):
        return re.sub(r"[^A-Z0-9]", "", value.upper())
    candidate_matches = 0
    for row in rows:
        piid = row["piid"]
        award, action, detail = awards[piid], actions[piid], details[piid]
        if (row["decisionFamilyId"] != review["decisionFamilyId"]
                or row["decisionDate"] != review["decisionDate"]
                or row["filedDate"] or review["filedDate"] is not None
                or row["sourceRetrievedDate"] != sources["retrievedDate"]
                or row["linkageStatus"] != "source_linked_not_estimation_ready"
                or row["independentReviewStatus"] != review["independentReviewStatus"]):
            raise ValueError("Protest provenance or claim boundary mismatch")
        for record in (award, action):
            if (row["uei"] != record["Recipient UEI"]
                    or row["agency"] != record["Awarding Agency"]
                    or row["awardeeName"] != record["Recipient Name"]
                    or row["usaspendingAwardKey"] != record["generated_internal_id"]):
                raise ValueError("Protest award identity mismatch")
        if (row["agency"] != review["agency"]
                or normalize_name(row["awardeeName"]) != normalize_name(review["awardeeName"])
                or row["uei"] != detail["recipient"]["recipient_uei"]
                or row["parentPiid"] != detail["parent_award"]["piid"]
                or row["awardingSubtierCode"] != detail["awarding_agency"]["subtier_agency"]["code"]
                or row["usaspendingAwardKey"] != detail["generated_unique_award_id"]):
            raise ValueError("Decision or parent-award identity mismatch")
        if (row["originalActionDate"] != action["Action Date"]
                or row["originalActionDate"] != detail["date_signed"]
                or not "2023-10-01" <= row["originalActionDate"] <= "2024-09-30"
                or row["modificationNumber"] != action["Mod"] or action["Mod"] != "0"
                or row["performanceStartDate"] != detail["period_of_performance"]["start_date"]):
            raise ValueError("Original-action timing or modification mismatch")
        for field, value in (
                ("actionObligationDollars", action["Transaction Amount"]),
                ("currentAwardTotalObligationDollars", detail["total_obligation"])):
            amount = Decimal(row[field])
            if not amount.is_finite() or amount != Decimal(str(value)):
                raise ValueError("Action versus current-award amount mismatch")
        archived = bulk[piid]
        if (archived["agency"] != row["agency"] or archived["uei"] != row["uei"]
                or archived["actionDate"] != row["originalActionDate"]
                or archived["modificationNumber"] != row["modificationNumber"]
                or Decimal(archived["amount"]) * 1_000_000 != Decimal(row["actionObligationDollars"])):
            raise ValueError("Archived bulk versus live original-action mismatch")
        matches = sum(r["agency"] == row["agency"] and r["piid"] == piid for r in frozen)
        if int(row["frozenCandidateMatches"]) != matches:
            raise ValueError("Stale frozen-panel candidate match count")
        candidate_matches += matches
    return len(rows), len({r["decisionFamilyId"] for r in rows}), candidate_matches


def docket_timing_rows(sources):
    """Normalize reviewed public fields without inventing a docket-to-PIID join."""
    review = sources["decisionReview"]
    reverse_aliases = {v: k for k, v in review["baseCaseDocketAliases"].items()}
    review_fingerprint = source_fingerprint({k: v for k, v in sources.items() if k != "records"})
    rows = []
    for record in sources["records"]:
        fields = record["fields"]
        case = reverse_aliases.get(fields["fileNumber"], fields["fileNumber"])
        areas = [r["serviceArea"] for r in review["serviceAreaFootnotes"] if case in r["caseNumbers"]]
        rows.append({
            "decisionFamilyId": review["decisionFamilyId"], "decisionCaseId": case,
            "docketFileNumber": fields["fileNumber"], "protesterNative": fields["protester"],
            "solicitationNumbersNative": fields["solicitationNumber"],
            "decisionServiceAreas": ";".join(areas),
            **{key: datetime.strptime(fields[key], "%b %d, %Y").date().isoformat()
               for key in ("filedDate", "decisionDate", "postedDate", "dueDate")},
            "docketOutcome": fields["outcome"], "piid": "",
            "awardTimingStatus": "docket_dates_only_award_mapping_unresolved",
            "sourceUrl": record["sourceUrl"], "sourceReviewDate": sources["reviewedDate"],
            "sourceFingerprint": source_fingerprint(record), "reviewFingerprint": review_fingerprint,
            "independentReviewStatus": sources["independentReviewStatus"],
        })
    return rows


def docket_timing_diagnostics(rows, sources, award_sources, bulk_manifest):
    """Validate the complete listed-case frame, not a population of protests."""
    if (sources.get("schema") != "gao-docket-timing-source-v1"
            or sources.get("captureMethod") != "public_browser_field_transcription"
            or sources.get("rawPageArchiveAvailable") is not False
            or sources.get("independentReviewStatus") != "pending"
            or not sources.get("reviewer") or not sources.get("captureScope")):
        raise ValueError("Docket source provenance or claim boundary mismatch")
    reviewed = date.fromisoformat(sources["reviewedDate"])
    review = sources["decisionReview"]
    award_review = award_sources["gaoReview"]
    if (any(review[key] != award_review[key] for key in ("decisionFamilyId", "sourceUrl", "decisionDate", "overallOutcome"))
            or review["supplementalOciDisposition"] != "dismissed"
            or review["originalActionDocketPairingStatus"] != "unresolved"):
        raise ValueError("Docket decision identity or claim boundary mismatch")
    sam = review["reportedSamCheck"]
    if (sam["underlyingRecordsRead"] is not False or sam["checkDate"] is not None
            or sam["historicalIntervalEligible"] is not False):
        raise ValueError("Decision-reported SAM check is not a historical interval")
    cases = review["caseNumbers"]
    if not cases or len(cases) != len(set(cases)) or any(not re.fullmatch(r"B-\d{6}(?:\.[2-9]\d*)?", c) for c in cases):
        raise ValueError("Missing, duplicate or invalid decision case frame")
    if review["sourceUrl"] != "https://www.gao.gov/products/" + ",".join(c.lower() for c in cases):
        raise ValueError("Decision case frame differs from linked decision")
    aliases = review["baseCaseDocketAliases"]
    if aliases != {c: c + ".1" for c in cases if "." not in c}:
        raise ValueError("Invalid source-specific base docket aliases")
    expected_ids = {aliases.get(c, c) for c in cases}
    records = sources["records"]
    if len(records) != len(cases) or {r["fields"]["fileNumber"] for r in records} != expected_ids:
        raise ValueError("Missing, duplicate or off-frame public docket records")
    area_rows = review["serviceAreaFootnotes"]
    if (len({r["serviceArea"] for r in area_rows}) != len(area_rows)
            or {r["footnote"] for r in area_rows} != {2, 3, 4, 5}
            or any(not r["caseNumbers"] or len(set(r["caseNumbers"])) != len(r["caseNumbers"])
                   or not set(r["caseNumbers"]) <= set(cases) for r in area_rows)
            or set().union(*(set(r["caseNumbers"]) for r in area_rows)) != set(cases)):
        raise ValueError("Incomplete or invalid decision service-area footnotes")
    for record in records:
        fields = record["fields"]
        if (record["sourceUrl"] != "https://www.gao.gov/docket/" + fields["fileNumber"].lower()
                or fields["decisionUrl"] != review["sourceUrl"] or fields["caseType"] != "Bid Protest"
                or fields["outcome"].lower() != review["overallOutcome"]
                or not fields["protester"] or not re.fullmatch(r"36C10X24R\d{4}(?:;36C10X24R\d{4})*", fields["solicitationNumber"])
                or fields["agency"] != "Department of Veterans Affairs : Department of Veterans Affairs"):
            raise ValueError("Docket identity, decision link or source field mismatch")
    expected_rows = docket_timing_rows(sources)
    if (len(rows) != len(cases) or len({r["docketFileNumber"] for r in rows}) != len(rows)
            or {r["docketFileNumber"] for r in rows} != expected_ids):
        raise ValueError("Missing, duplicate or off-frame normalized docket rows")
    by_id = {r["docketFileNumber"]: r for r in expected_rows}
    for row in rows:
        if row != by_id[row["docketFileNumber"]]:
            raise ValueError("Docket source fingerprint, normalized field or claim boundary mismatch")
        filed, decision, posted, due = (date.fromisoformat(row[k]) for k in ("filedDate", "decisionDate", "postedDate", "dueDate"))
        if (not filed <= decision <= posted <= reviewed or filed > due
                or row["decisionDate"] != review["decisionDate"]):
            raise ValueError("Docket chronology mismatch")
    details = sources["awardDescriptionChecks"]
    awards = {r["response"]["piid"]: r["response"] for r in award_sources["awardDetails"]}
    if len(details) != len(awards) or {r["fields"]["piid"] for r in details} != set(awards):
        raise ValueError("Missing or duplicate award-description checks")
    for record in details:
        fields = record["fields"]
        award = awards[fields["piid"]]
        candidate = record["explicitServiceAreaCandidate"]
        if (fields["generated_unique_award_id"] != award["generated_unique_award_id"]
                or fields["date_signed"] != award["date_signed"]
                or fields["last_modified_date"] != award["period_of_performance"]["last_modified_date"]
                or record["sourceUrl"] != "https://api.usaspending.gov/api/v2/awards/" + fields["generated_unique_award_id"] + "/"
                or record["retrievedDate"] != sources["reviewedDate"]
                or not re.fullmatch(r"[a-f0-9]{64}", record["rawResponseSha256"])
                or record["projectionOnly"] is not True
                or record["originalActionMappingVerified"] is not False
                or fields["solicitation_identifier"] is not None
                or candidate is not None and (candidate not in {r["serviceArea"] for r in area_rows} or candidate not in fields["description"])):
            raise ValueError("Unverified current-description award mapping or provenance")
    archive = sources["archiveFieldCheck"]
    strata = [r for r in bulk_manifest["strata"] if r["downloadFile"] == archive["sourcePath"]]
    if (len(strata) != 1 or strata[0]["zipSha256"] != archive["zipSha256"]
            or not archive["member"].startswith("Contracts_PrimeTransactions_")
            or len(archive["columns"]) != len(set(archive["columns"]))
            or {"solicitation_identifier", "transaction_description", "prime_award_base_transaction_description"} & set(archive["columns"])):
        raise ValueError("Archived field-check provenance or absent-column mismatch")
    extracted = archive["selectedOriginalActions"]
    if len(extracted) != len(awards) or {r["fields"]["award_id_piid"] for r in extracted} != set(awards):
        raise ValueError("Missing or duplicate archived original-action excerpts")
    for record in extracted:
        fields = record["fields"]
        award = awards[fields["award_id_piid"]]
        bulk = next(r for r in award_sources["bulkExtract"]["records"] if r["piid"] == fields["award_id_piid"])
        if (set(fields) != set(archive["columns"]) or record["csvRowIncludingHeader"] < 2
                or fields["parent_award_id_piid"] != award["parent_award"]["piid"]
                or fields["action_date"] != bulk["actionDate"]
                or fields["modification_number"] != bulk["modificationNumber"]
                or fields["recipient_uei"] != bulk["uei"]
                or fields["awarding_agency_name"] != bulk["agency"]
                or Decimal(fields["federal_action_obligation"]) != Decimal(bulk["amount"]) * 1_000_000):
            raise ValueError("Archived original-action identity or field mismatch")
    return {
        "expectedEntries": len(cases), "reviewedEntries": len(rows), "decisionFamilies": 1,
        "filingDates": dict(sorted(Counter(r["filedDate"] for r in rows).items())),
        "multiSolicitationEntries": sum(";" in r["solicitationNumbersNative"] for r in rows),
        "multiServiceAreaEntries": sum(";" in r["decisionServiceAreas"] for r in rows),
        "currentDescriptionCandidates": sum(r["explicitServiceAreaCandidate"] is not None for r in details),
        "awardSpecificDatesPromoted": 0, "historicalExclusionIntervalsPromoted": 0,
    }


def audit():
    findings = []
    def add(item, status, evidence, requirement):
        findings.append(dict(zip(FIELDS, (item, status, evidence, requirement))))
    lda = read("substitution-expanded-lda-panel.csv")
    if len({r["sourceRecordId"] for r in lda}) != len(lda):
        raise ValueError("Duplicate expanded LDA source-record keys")
    if any(r["exposureGroup"] != "unassigned_design_candidate" for r in lda):
        raise ValueError("Expanded acquisition must not assign treatment/control exposure")
    filings = {r["filingUuid"]: r for r in lda}
    periods = defaultdict(set)
    for row in filings.values():
        if row["filingType"] not in {"RA", "RR"} and row["periodEnd"] < "2007-09-14":
            periods[row["canonicalActorId"]].add((row["periodStart"], row["periodEnd"]))
    add("expanded-lda-history", "api_attribution_identity_unresolved",
        f"issueRows={len(lda)}; filingUUIDs={len(filings)}; actors={len(set(r['canonicalActorId'] for r in lda))}; years={','.join(sorted(set(r['filingYear'] for r in lda)))}; observedPrePeriodsByActor=" + ";".join(f"{a}:{len(p)}" for a,p in sorted(periods.items())),
        "Counts reflect source/API attribution, not validated actor histories. A reviewed NVG cover names America Votes despite API attribution to AAJ; that filing is ineligible for AAJ attribution, and the remaining NVG history needs review. Validate amendments and exact identities; pre-period counts are native reporting periods, not independent quarters or proof of completeness.")
    date_sources = json.loads((DATA / "substitution-lda-date-reviews.json").read_text(encoding="utf-8"))
    date_checks = lda_date_review_diagnostics(read("substitution-lda-filing-metadata.csv"), date_sources)
    add("lda-posting-date-anomaly", "source_reviewed_dates_not_orderable",
        "; ".join(f"{key}={value}" for key, value in date_checks.items()),
        "All three flagged covers now have full embedded-scan reviews and source-matched registration components. Receipt stamps, API posting dates and termination dates remain different fields. Two covers supply Method A observations; one income disclosure is below $10,000, not a point zero. Resolve source-date origins and complete filing/version families before ordering amendments, aggregating actor amounts or selecting comparable controls. Other dates and zeros are not cleared by this selected review; independent review remains pending.")
    measurement = lda_measurement_diagnostics(lda, read("substitution-lda-filing-metadata.csv"),
        read("substitution-lda-filing-reviews.csv"), read("substitution-lda-alias-reviews.csv"))
    add("lda-measurement-comparability", "source_measures_not_comparable_totals",
        "; ".join(f"{key}={value}" for key, value in measurement.items()),
        "Do not add organizational expenses to retained-firm income. Missing API accounting methods need original-form review; the reviewed Method A and Method C reports use different outcome definitions. Reviewed aliases restore only a specified registration, not exhaustive organization coverage. Null amounts remain blank. The separate date-review ledger codes one source zero as censored income; other source zeros remain unadjudicated. No actor spending total or matched control is validated by these checks.")
    spec = importlib.util.spec_from_file_location("lda_families", ROOT / "scripts/review-substitution-lda-families.py")
    family_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(family_module)
    family_sources = json.loads((DATA / "substitution-lda-family-review.json").read_text())
    family_queue, family_checks = family_module.validate_review(read("substitution-lda-filing-metadata.csv"), family_sources, date_sources)
    if family_queue != read("substitution-lda-family-queue.csv"):
        raise ValueError("LDA candidate-family queue is stale")
    add("lda-filing-family-review", "partial_field_review_not_final_versions",
        "; ".join(f"{key}={value}" for key, value in family_checks.items()),
        "The 22 multi-record groups are candidates, not complete families. APGA's amendment download has one issue image and no financial cover; both scanned ENG pages name FERC, unlike their API contact lists. A separate NVG cover pair identifies ATLA and America Votes although the API assigns both to AAJ. That candidate group is not mergeable; the America Votes filing is not eligible for AAJ attribution. The ATLA cover has a different registration suffix and a checked amendment box absent from the API type. Source indexing, the remaining NVG history, historical packet completeness and independent review remain unresolved. No final amount, whole-record replacement, corrected raw record, agency exposure or control assignment is promoted.")
    fec = read("substitution-fec-report-panel.csv")
    histories = read("substitution-fec-affiliation-history.csv")
    cohort = read("substitution-fec-acquisition-cohort.csv")
    if any(r["exposureGroup"] != "unassigned_design_candidate" for r in cohort):
        raise ValueError("FEC acquisition candidates must not assign treatment/control exposure")
    if not {r["canonicalActorId"] for r in cohort} <= {r["canonicalActorId"] for r in lda}:
        raise ValueError("FEC candidate actor absent from expanded LDA source")
    expected_histories = {(r["canonicalActorId"], r["committeeId"], str(year + year % 2)) for r in cohort for year in range(int(r["startYear"]), int(r["endYear"]) + 1)}
    if len(histories) != len(expected_histories) or {(r["canonicalActorId"], r["committeeId"], r["cycle"]) for r in histories} != expected_histories:
        raise ValueError("Missing, duplicate or off-cohort FEC historical affiliations")
    if len({(r['committeeId'], r['sourceRecordId']) for r in fec}) != len(fec):
        raise ValueError("Duplicate FEC filing keys")
    overlap, gaps, straddles = report_period_diagnostics(fec)
    missing = sum(r[field] == "" for r in fec for field in ("candidateContributionsDollars", "independentExpendituresDollars", "totalDisbursementsDollars"))
    add("alternate-channel-reports", "bounded_affiliation_candidate",
        f"reportRows={len(fec)}; committees={len(set(r['committeeId'] for r in fec))}; affiliationRows={len(histories)}; affiliationCycles={','.join(sorted({r['cycle'] for r in histories}))}; overlappingPeriods={overlap}; gapsBetweenReports={gaps}; halfYearStraddlingReports={straddles}; missingOutcomeCells={missing}",
        "Review historical sponsor links, form-specific measure definitions and report amendments. API amount formatting does not restore cents missing from source extraction. PAC availability does not establish comparable controls.")
    halfyears = read("substitution-fec-halfyear-panel.csv")
    coverage = read("substitution-fec-halfyear-coverage.csv")
    spec = importlib.util.spec_from_file_location("fec_coverage_audit", ROOT / "scripts/prepare-substitution-fec-periods.py")
    periods_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(periods_module)
    adjudications = read("substitution-fec-version-adjudications.csv")
    expected_halfyears, expected_coverage = periods_module.prepare_with_coverage(fec, cohort, adjudications)
    if halfyears != expected_halfyears or coverage != expected_coverage:
        raise ValueError("FEC prepared series or coverage ledger differs from raw-source reproduction")
    unresolved = [r for r in coverage if r["status"] != "observed_complete"]
    add("alternate-channel-coverage", "partial_outcome_coverage" if unresolved else "complete_source_periods_not_design",
        f"expectedCommitteeHalfYears={len(coverage)}; complete={len(halfyears)}; unresolvedOrMissing={len(unresolved)}; completeByCommittee=" + ";".join(f"{r['committeeId']}:{sum(h['committeeId'] == r['committeeId'] for h in halfyears)}" for r in cohort),
        "Keep all declared acquisition-frame periods visible; resolve Benefits Council versions, amounts and missing fields. AAJ 2008H2 uses a source-bound supplemental-loan-paperwork adjudication; independent review remains pending. Missing periods are not zero spending.")
    add("alternate-channel-halfyears", "observed_outcome_not_effect",
        f"completeHalfYears={len(halfyears)}; includedReportVersions={sum(int(r['reportCount']) for r in halfyears)}; sourceReviewedHalfYears={sum(bool(r['adjudicationIds']) for r in halfyears)}; eventClasses={dict(Counter(r['eventClass'] for r in halfyears))}",
        "Latest non-amended reports or explicit source-bound version adjudications, with no unresolved alternative version. Compare with native LDA periods after actor linkage and exposure validation; period completeness is not exhaustive source-image or causal validation.")
    corpus = read("comment-body-corpus.csv")
    if len({r['commentId'] for r in corpus}) != len(corpus):
        raise ValueError("Duplicate comment IDs")
    add("comment-corpus", "source_refreshed",
        f"rows={len(corpus)}; uniqueBodies={len(set(r['bodyText'] for r in corpus))}; emptyBodies={sum(not r['bodyText'] for r in corpus)}",
        "Verify receipt dates separately from posting dates and sample coverage before calculating docket-level rates.")
    pilot = read("comment-uptake-issue-pilot.csv")
    for row in pilot:
        if row["unit"] != "docket_issue" or row["commentId"] or row["responseSectionRead"] != "false":
            raise ValueError("Pilot must not pretend to contain individually linked or read RTC sections")
        if not row["sourcePage"] or not row["reviewDate"] or len(row["sourcePdfSha256"]) != 64:
            raise ValueError("Pilot source provenance missing")
    add("comment-uptake-pilot", "issue_level_only",
        f"observations={len(pilot)}; individualCommentLinks={sum(bool(r['commentId']) for r in pilot)}; changes=" + str(dict(Counter(r['disapprovalGroundChange'] for r in pilot))),
        "Retrieve full response document, link actual comments and complete independent coding review; do not compute an uptake rate from this purposive pilot.")
    position_sources = json.loads((DATA / "comment-position-source.json").read_text(encoding="utf-8"))
    positions = comment_position_diagnostics(read("comment-position-pilot.csv"), position_sources)
    add("comment-public-copy-positions", "policy_alignment_not_uptake",
        "; ".join(f"{key}={value}" for key, value in positions.items()),
        "Two positions belong to one purposefully selected public letter, not two independent comments. Verify the docket attachment version, trace agency responses and obtain independent review before coding uptake. Agreement with an unchanged proposed action does not identify comment influence or prove no effect.")
    response_sources = json.loads((DATA / "comment-response-document-source.json").read_text(encoding="utf-8"))
    responses = comment_response_diagnostics(read("comment-response-document-pilot.csv"), response_sources)
    add("comment-agency-reproduced-requests", "documented_responses_not_causal_uptake",
        "; ".join(f"{key}={value}" for key, value in responses.items()),
        "Separate purposive Phase 3 pilot, not the Utah corpus. EPA reproduces request excerpts and explicitly names the two commenters in responses; original submitted attachments and their version match remain unread/unverified. Complete independent review and define a sampling frame before estimating response rates. A collective method change and a later publication correction do not identify an individual comment's effect.")
    section_sources = json.loads((DATA / "comment-section-inventory-source.json").read_text(encoding="utf-8"))
    section = comment_section_diagnostics(read("comment-section-inventory.csv"), section_sources, response_sources)
    add("comment-section-request-inventory", "complete_section_excerpts_not_docket_population",
        "; ".join(f"{key}={value}" for key, value in section.items()),
        "Retrospective six-page Phase 3 inventory: independently review request segmentation, repeated/grouped responses, opposing positions and conditional fallback. Two requests overlap the prior pilot and must not be counted again. No request-specific disposition within this section is not docket-wide nonresponse. Appendix A's 1,011 non-reproduced comments and 2,533 theme incidences are different units, not a control or nonresponse denominator. Original submissions and a docket sampling frame remain unresolved; no causal effect is identified.")
    followup_sources = json.loads((DATA / "comment-request-followups.json").read_text(encoding="utf-8"))
    followup = comment_followup_diagnostics(followup_sources, section_sources, response_sources)
    add("comment-cross-section-followup", "documented_partial_alignment_not_individual_effect",
        "; ".join(f"{key}={value}" for key, value in followup.items()),
        "One targeted DTNA follow-up, not an additional request or expanded sample: section 10.3.2 supplies a named-summary/collective-response link, and the April 2024 clause confirms limited credit use through MY2032. The proposal already solicited the option. Preserve the original section-2.5 coding, distinguish caps from discounts, and independently review original-file identity and facet coding. No full acceptance, docket rate, individual effect or current regulatory-status claim is cleared.")
    protests = read("gao-protest-overlay.csv")
    reviewed = [r for r in protests if "Partial source-page review" in r["notes"]]
    add("gao-partial-adjudication", "not_award_linked",
        f"rows={len(protests)}; partiallyReviewed={len(reviewed)}; verifiedDecisionDates={sum(r['decisionDate'] != 'candidate_unreviewed' for r in protests)}",
        "Link decision-body dates and awarded PIID/UEI; a solicitation number is not a verified award key. No-match is not no-protest.")
    links = read("gao-award-linkage-pilot.csv")
    sources = json.loads((DATA / "gao-award-linkage-source.json").read_text(encoding="utf-8"))
    bulk_summary = json.loads((ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-bulk-summary.json").read_text(encoding="utf-8"))
    if (sources["bulkExtract"]["sourceSha256"] != bulk_summary["normalizedOutputSha256"]
            or sources["bulkExtract"]["sourceCreatedAt"] != bulk_summary["createdAt"]
            or sources["bulkExtract"]["sourceRowCount"] != bulk_summary["downloadedNormalizedRows"]):
        raise ValueError("Bulk pilot provenance differs from frozen bulk manifest")
    with (ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-actions.csv").open(newline="", encoding="utf-8") as source:
        frozen = list(csv.DictReader(source))
    linked, families, matches = protest_linkage_diagnostics(links, sources, frozen)
    partial_keys = Counter((r["agency"], r["piid"], r["modificationNumber"]) for r in frozen)
    add("procurement-frozen-frame", "selected_sample_partial_identifiers",
        f"rows={len(frozen)}; agencies={len({r['agency'] for r in frozen})}; actionDateRange={min(r['actionDate'] for r in frozen)}..{max(r['actionDate'] for r in frozen)}; repeatedPartialKeys={sum(n > 1 for n in partial_keys.values())}; rowsOnRepeatedPartialKeys={sum(n for n in partial_keys.values() if n > 1)}; exactDuplicateRows={len(frozen) - len({tuple(r.values()) for r in frozen})}",
        "Use the fiscal-year 2024 twelve-agency population, not a calendar-year EPA-only frame. Ranked page slices are not a probability sample. Preserve parent/subtier/source transaction identifiers and unrounded dollar obligations in the reconciliation source; repeated partial keys are not proven duplicate actions.")
    add("gao-time-aligned-award-pilot", "source_linked_not_estimation_ready",
        f"linkedAwards={linked}; consolidatedDecisions={families}; frozenPanelCandidateRows={matches}; archivedBulkMatches={len(sources['bulkExtract']['records'])}; observedOriginalActions={linked}; sourceVintage={sources['retrievedDate']}",
        "Obtain independent review, award-specific docket mappings and a representative award/protest frame. The separate ledger supplies dates for all 13 listed docket entries, not one verified filing date per award. Four awards in one selected consolidated decision are not four independent events; current award totals and latest offer fields are not original-action values.")
    docket_sources = json.loads((DATA / "gao-docket-timing-source.json").read_text(encoding="utf-8"))
    docket = docket_timing_diagnostics(read("gao-docket-timing-pilot.csv"), docket_sources, sources, bulk_summary)
    add("gao-docket-timing-pilot", "docket_timing_verified_award_mapping_unresolved",
        "; ".join(f"{key}={value}" for key, value in docket.items()),
        "Review original-action solicitation/service-area links and obtain independent coding review. Three docket entries list multiple solicitations and one spans four decision service areas. Current descriptions supply two candidates only; the archived export lacks description/solicitation columns. A GAO-reported SAM check has no verified date or underlying interval. No protest rate, award-specific timing or historical exclusion coverage is promoted.")
    spec = importlib.util.spec_from_file_location("bulk_frame", ROOT / "scripts/audit-procurement-bulk-frame.py")
    bulk_frame = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bulk_frame)
    bulk_profile = json.loads(bulk_frame.PROFILE.read_text(encoding="utf-8"))
    bulk = bulk_frame.validate_profile(bulk_profile, bulk_summary, bulk_frame.sha256(bulk_frame.MANIFEST))
    type_review = json.loads(bulk_frame.TYPE_REVIEW.read_text(encoding="utf-8"))
    reviewed_type = bulk_frame.validate_type_review(type_review, bulk_profile)
    add("procurement-archived-bulk-frame", "mixed_frame_missing_offers_not_sam_exclusions",
        f"archivedRows={bulk['rows']}; manifestStrata={len(bulk_profile['strata'])}; inclusiveDaysPerAgency={bulk_profile['inclusiveDaysPerAgency']}; childDescriptionRows={bulk['childDescriptionRows']}; blankAwardTypeRows={bulk['blankAwardTypeRows']}; missingOffersRows={bulk['missingOffersRows']}; explicitZeroOffersRows={bulk['zeroOffersRows']}; afterExclusionCompetitionRows={bulk['afterExclusionCompetitionRows']}; outsideDateRows={bulk['outsideDateRows']}; wrongAgencyRows={bulk['wrongAgencyRows']}; reviewedBlankTypeExample={reviewed_type}",
        "Saved-profile checks are not an independent re-scan of the ignored ZIPs. Reconcile native A/B/C/D actions separately from IDVs, retain unknown award types and missing offers, and obtain historical SAM status plus full action keys. Competition after exclusion of sources is not vendor debarment. Count/export drift remains unattributed.")
    add("overall", "not_identified",
        "New source history, PAC outcomes and issue-level comment coding exist; no provision-exposure control design, representative SAM export or historical exclusion overlay has cleared.",
        "Continue all three tracks. These findings are an interim source/design audit, not completion of the active empirical goal.")
    return findings


def main():
    rows = audit()
    REPORTS.mkdir(exist_ok=True)
    with (REPORTS / "empirical-expansion-audit.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Empirical expansion evidence audit", "", "Current committed source products; no causal-calibration promotion.", ""]
    for row in rows:
        lines.extend([f"## {row['item']}", "", f"Status: `{row['status']}`", "", row['evidence'], "", "Remaining: " + row['remainingRequirement'], ""])
    (REPORTS / "empirical-expansion-audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Audited {len(rows)} evidence/design checks; overall not identified.")


if __name__ == "__main__":
    main()
