#!/usr/bin/env python3
"""Validate a scoped paper-report review before reusing cross-endpoint flags.

The review recovers only most_recent, never amounts, dates, native form labels,
historical completeness, or a causal design. Saved projections are not raw HTTP
responses. PDF hashes bind the manual reading; they do not independently verify it.
"""

from datetime import date, datetime
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/calibration/first-wave/substitution-fec-paper-review.json"
BOUNDARY = {
    "appliedField": "mostRecent", "rawReportsUnchanged": True,
    "amountsPromoted": False, "datesCorrected": False,
    "historicalCompletenessCleared": False, "controlAssignmentCleared": False,
    "causalEffect": "not_identified",
}
# Form/line/column semantics, not the PDF page's ordinal position.
LOCATIONS = {
    "pac_contributions_period": ("F3X", 23, "A"),
    "independent_expenditures_period": ("F3X", 24, "A"),
    "total_disbursements_period": ("F3X", 31, "A"),
    "pac_contributions_ytd": ("F3X", 23, "B"),
    "form3_transfers_period": ("F3", 18, "A"),
    "form3_total_disbursements_period": ("F3", 22, "A"),
}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha256(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)


def validate_period_consistency(source, review):
    """Reconcile dated schedule rows without repairing the reported period."""
    document = next((d for d in review["documents"] if d["sourceRecordId"] == source["sourceRecordId"]), None)
    if (document is None or not source["reviewId"] or not source["reviewer"]
            or source["independentReviewStatus"] != "pending"
            or document["pagesReviewed"] != list(range(1, document["pdfPages"] + 1))
            or [p["pdfPage"] for p in document["pageInventory"]] != document["pagesReviewed"]):
        raise ValueError("FEC period consistency review requires a complete page inventory")
    date.fromisoformat(source["reviewDate"])
    expected_boundary = {"correctedPeriodEnd": None, "zeroActivityInHeaderGapEstablished": False,
                         "completePeriodVerified": False, "outcomePromotionCleared": False,
                         "independentExpendituresEstablished": False}
    if source["boundary"] != expected_boundary:
        raise ValueError("FEC period conflict does not authorize date, zero or outcome promotion")
    start, end = date.fromisoformat(document["periodStart"]), date.fromisoformat(document["periodEnd"])
    if (source["headerPeriodEnd"] != document["periodEnd"] or source["headerDatePdfPages"] != [1, 2, 3]
            or not set(source["headerDatePdfPages"]) <= set(document["pagesReviewed"])):
        raise ValueError("FEC conflicting header date provenance changed")
    transactions = source["transactions"]
    keys = [(r["pdfPage"], r["slot"]) for r in transactions]
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("Duplicate or empty FEC itemized transaction review")
    totals = {"receipt": Decimal(0), "disbursement": Decimal(0)}
    counts = {"receipt": 0, "disbursement": 0}
    after_header, dates = [], []
    page_kinds = {p["pdfPage"]: p["pageKind"] for p in document["pageInventory"]}
    for row in transactions:
        kind = row["kind"]
        if (kind not in totals or row["slot"] not in {"A", "B", "C"}
                or row["schedule"] != ("A" if kind == "receipt" else "B")
                or page_kinds.get(row["pdfPage"]) != ("schedule_a_receipts" if kind == "receipt" else "schedule_b_disbursements")
                or row["lineCheckbox"] not in ({"11c", None} if kind == "receipt" else {"23"})):
            raise ValueError("FEC transaction mixes receipt/disbursement grain or source location")
        value = Decimal(row["amountDollars"])
        event_date = date.fromisoformat(row["reportedDate"])
        if not value.is_finite() or value < 0 or event_date < start:
            raise ValueError("Invalid FEC itemized amount/date")
        totals[kind] += value
        counts[kind] += 1
        dates.append(event_date)
        if event_date > end:
            after_header.append(row)
    if not after_header:
        raise ValueError("FEC period-conflict review has no out-of-header transactions")
    reconciliation = source["summaryReconciliation"]
    observed = {o["field"]: o["valueDollars"] for o in document["observations"]}
    if (reconciliation["receiptsPdfPage"] != 2 or reconciliation["receiptsPrintedLine"] != "6c"
            or reconciliation["column"] != "A"
            or totals["receipt"] != Decimal(reconciliation["receiptsDollars"])
            or totals["disbursement"] != Decimal(observed["pac_contributions_period"])
            or reconciliation["taxesPdfPage"] != 4 or reconciliation["taxesPrintedLine"] != "29"
            or totals["disbursement"] + Decimal(reconciliation["taxesDollars"]) != Decimal(observed["total_disbursements_period"])
            or observed["independent_expenditures_period"] is not None
            or reconciliation["taxesItemizedInDownloadedPacket"] is not False):
        raise ValueError("FEC schedule/summary amounts or blank-field boundary do not reconcile")
    notice = source["priorNotice"]
    projection = notice["filingProjection"]
    report = next(r for r in review["reportProjections"] if r["sourceRecordId"] == source["sourceRecordId"])
    if (not sha256(notice["pdfSha256"]) or notice["pdfPages"] != 2 or notice["pagesReviewed"] != [1, 2]
            or notice["sourceUrl"] != projection["pdf_url"]
            or not notice["sourceUrl"].startswith("https://docquery.fec.gov/pdf/")
            or projection["beginning_image_number"] not in review["filingsQuery"]["beginningImageInventory"]
            or projection["committee_id"] != review["committeeId"] or projection["form_type"] != "FRQ"
            or projection["report_type"] != "Q1" or projection["report_year"] != start.year
            or projection["coverage_start_date"] != document["periodStart"]
            or projection["coverage_end_date"] != notice["requestedPeriodEnd"]
            or projection["receipt_date"][:10] != notice["letterDate"]
            or projection["pages"] != notice["pdfPages"]
            or not (max(dates) <= date.fromisoformat(notice["requestedPeriodEnd"])
                    < date.fromisoformat(notice["letterDate"]) < date.fromisoformat(report["receipt_date"][:10]))
            or notice["certifiesLaterReportCoverage"] is not False or notice["establishesEnforcementOutcome"] is not False):
        raise ValueError("FEC prior notice provenance or coverage/enforcement boundary invalid")
    return {"sourceRecordId": source["sourceRecordId"], "itemizedReceipts": counts["receipt"],
            "itemizedDisbursements": counts["disbursement"], "transactionsAfterHeaderEnd": len(after_header),
            "receiptTotalDollars": format(totals["receipt"], ".2f"),
            "contributionTotalDollars": format(totals["disbursement"], ".2f"),
            "minTransactionDate": min(dates).isoformat(), "maxTransactionDate": max(dates).isoformat(),
            "correctedPeriodEnd": None, "completePeriodVerified": False}


def validate_review(rows, review):
    """Return source-record version flags plus review diagnostics; mutate nothing."""
    if review.get("reviewFingerprint") != fingerprint({k: v for k, v in review.items() if k != "reviewFingerprint"}):
        raise ValueError("Stale FEC paper review fingerprint")
    if review["schemaVersion"] != 2 or review["boundary"] != BOUNDARY:
        raise ValueError("Unsupported FEC paper review promotion")
    if not review["reviewId"] or not review["reviewer"] or review["independentReviewStatus"] != "pending":
        raise ValueError("Missing FEC paper reviewer or independent-review boundary")
    date.fromisoformat(review["reviewDate"])
    committee, actor = review["committeeId"], review["canonicalActorId"]
    raw = [r for r in rows if r["committeeId"] == committee]
    raw_by_id = {r["sourceRecordId"]: r for r in raw}
    reports = review["reportProjections"]
    report_ids = [r["sourceRecordId"] for r in reports]
    if (not raw or len(raw) != len(raw_by_id) or len(report_ids) != len(set(report_ids))
            or set(report_ids) != set(raw_by_id)
            or any(r["canonicalActorId"] != actor for r in raw)):
        raise ValueError("FEC paper review must match the entire frozen committee frame")
    queries = review["reportQueries"]
    if len(queries) != len({q["year"] for q in queries}) or {q["year"] for q in queries} != {r["report_year"] for r in reports}:
        raise ValueError("FEC report query frame mismatch")
    for query in queries:
        expected = sorted(r["sourceRecordId"] for r in reports if r["report_year"] == query["year"])
        if (query["url"] != f"https://api.open.fec.gov/v1/committee/{committee}/reports/?year={query['year']}"
                or query["pagination"] != "all_pages_via_fetch_all"
                or query["count"] != len(expected) or query["sourceRecordIds"] != expected):
            raise ValueError("Incomplete FEC report query provenance")
    query = review["filingsQuery"]
    inventory = query["beginningImageInventory"]
    if (query["url"] != f"https://api.open.fec.gov/v1/filings/?committee_id={committee}"
            or query["pagination"] != "all_pages_via_fetch_all"
            or query["count"] != len(inventory) or len(set(inventory)) != len(inventory)
            or any(not re.fullmatch(r"\d+", image) for image in inventory)):
        raise ValueError("Incomplete or duplicate FEC filing inventory")
    for acquisition in (review["reportAcquisition"], query):
        timestamp = datetime.fromisoformat(acquisition["retrievedAt"])
        if timestamp.tzinfo is None or not sha256(acquisition["projectionFileSha256"]):
            raise ValueError("FEC acquisition timestamp or projection provenance missing")
    filings = review["matchedFilingProjections"]
    by_image = {r["beginning_image_number"]: r for r in filings}
    if (len(filings) != len(by_image) or len(filings) != len(reports)
            or set(by_image) != {r["beginning_image_number"] for r in reports}
            or not set(by_image) <= set(inventory)):
        raise ValueError("FEC report/filing join is not one-to-one and complete")
    spec = importlib.util.spec_from_file_location("fec_paper_normalizer", ROOT / "scripts/fetch-substitution-fec-reports.py")
    normalizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normalizer)
    decisions = {}
    for report in reports:
        key = report["sourceRecordId"]
        normalized = normalizer.normalize(report, actor, review["reportAcquisition"]["retrievedAt"])
        if any(normalized[f] != raw_by_id[key][f] for f in normalizer.FIELDS if f != "sourceRetrievedAt"):
            raise ValueError("Stale FEC report projection differs from frozen source")
        filing = by_image[report["beginning_image_number"]]
        for field in ("committee_id", "file_number", "report_year", "report_type", "amendment_indicator", "pdf_url"):
            if filing[field] != report[field]:
                raise ValueError("FEC joined filing identity/type mismatch")
        for field in ("coverage_start_date", "coverage_end_date", "receipt_date"):
            if (filing[field] or "")[:10] != (report[field] or "")[:10]:
                raise ValueError("FEC joined filing date mismatch")
        if (report["most_recent"] is not None or type(filing["most_recent"]) is not bool
                or type(report["is_amended"]) is not bool
                or filing["most_recent"] == report["is_amended"]):
            raise ValueError("FEC joined filing version flags absent or contradictory")
        decisions[key] = filing["most_recent"]

    documents = review["documents"]
    ids = [d["sourceRecordId"] for d in documents]
    if len(ids) != len(set(ids)) or not set(ids) <= set(report_ids):
        raise ValueError("FEC paper document review frame mismatch")
    missing_pages, form_mismatches, blank_fields = 0, 0, 0
    for document in documents:
        report = next(r for r in reports if r["sourceRecordId"] == document["sourceRecordId"])
        pages = document["pagesReviewed"]
        if (document["sourceUrl"] != report["pdf_url"] or not sha256(document["pdfSha256"])
                or not document["sourceUrl"].startswith("https://docquery.fec.gov/pdf/")
                or pages != sorted(set(pages)) or not pages
                or any(type(p) is not int or not 1 <= p <= document["pdfPages"] for p in pages)
                or document["coverPdfPage"] not in pages):
            raise ValueError("FEC PDF source/page provenance missing")
        if document["nativeForm"] not in {"F3", "F3X"}:
            raise ValueError("Unknown native FEC form")
        if document["periodStart"] != report["coverage_start_date"][:10] or document["periodEnd"] != report["coverage_end_date"][:10]:
            raise ValueError("Source paper period cannot be silently corrected")
        form_mismatches += document["nativeForm"] != by_image[report["beginning_image_number"]]["form_type"]
        absent = document["disbursementSummaryAbsentFromDownloadedPacket"]
        if type(absent) is not bool:
            raise ValueError("FEC missing-page claim must be explicit")
        if absent:
            page_map = document["pageInventory"]
            if (pages != list(range(1, document["pdfPages"] + 1))
                    or [p["pdfPage"] for p in page_map] != pages
                    or any(not p["pageKind"] or p["pageKind"] == "disbursement_summary" for p in page_map)):
                raise ValueError("FEC missing-page claim requires a complete packet inventory")
            missing_pages += 1
        for observation in document["observations"]:
            if (observation["pdfPage"] not in pages
                    or LOCATIONS.get(observation["field"]) != (document["nativeForm"], observation["printedLine"], observation["column"])
                    or observation["printedPage"] != 4 or absent):
                raise ValueError("FEC field location conflates form, line, column or PDF page")
            value = observation["valueDollars"]
            if observation["valueState"] == "blank":
                if value is not None:
                    raise ValueError("Blank FEC source field is not a numeric zero")
                blank_fields += 1
            elif observation["valueState"] != "reported_numeric" or value is None or not Decimal(value).is_finite():
                raise ValueError("Invalid FEC paper amount observation")
    letter = review["formCorrectionLetter"]
    if (not sha256(letter["pdfSha256"]) or not letter["sourceUrl"].startswith("https://docquery.fec.gov/pdf/")
            or letter["pagesReviewed"] != [1, 2] or letter["pdfPages"] != 2
            or letter["letterDate"] != "2009-05-15" or letter["requestedForm"] != "F3X"
            or letter["establishesEnforcementAction"] is not False):
        raise ValueError("FEC form-correction letter provenance/boundary missing")
    pairs = review["formCorrectionPairs"]
    paired_ids = [pair[field] for pair in pairs for field in ("originalRecordId", "amendmentRecordId")]
    if (len(paired_ids) != len(set(paired_ids))
            or {p["originalRecordId"] for p in pairs} != {key for key, flag in decisions.items() if not flag}
            or len(pairs) != len(letter["referencedPeriods"])):
        raise ValueError("FEC correction pairs are incomplete or duplicate")
    for pair in pairs:
        old, new = pair["originalRecordId"], pair["amendmentRecordId"]
        if old == new or decisions.get(old) is not False or decisions.get(new) is not True:
            raise ValueError("FEC correction pair contradicts source version flags")
        old_doc, new_doc = [next(d for d in documents if d["sourceRecordId"] == key) for key in (old, new)]
        if (old_doc["nativeForm"] != "F3" or new_doc["nativeForm"] != "F3X"
                or any(old_doc[f] != new_doc[f] for f in ("periodStart", "periodEnd"))
                or [old_doc["periodStart"], old_doc["periodEnd"]] not in letter["referencedPeriods"]):
            raise ValueError("FEC correction pair lacks matching native forms and periods")
    consistency = review["periodConsistencyReviews"]
    if len({r["sourceRecordId"] for r in consistency}) != len(consistency) or not {r["sourceRecordId"] for r in consistency} <= set(ids):
        raise ValueError("FEC period-consistency review frame mismatch")
    period_checks = [validate_period_consistency(r, review) for r in consistency]
    return decisions, {
        "reportRowsMatched": len(decisions), "filingInventoryRows": len(inventory),
        "filingsLatestTrue": sum(decisions.values()), "filingsLatestFalse": len(decisions) - sum(decisions.values()),
        "reportEndpointUnknownLatest": sum(r["most_recent"] is None for r in reports),
        "reviewedReportPdfs": len(documents), "nativeFormTypeDiscrepancies": form_mismatches,
        "packetsWithoutDisbursementSummary": missing_pages,
        "reviewedBlankAmountFields": blank_fields,
        "periodConflictReportIds": [r["sourceRecordId"] for r in period_checks],
        "transactionsAfterHeaderEnd": sum(r["transactionsAfterHeaderEnd"] for r in period_checks),
        "rawAmountsPromoted": 0, "datesCorrected": 0,
        "independentReviewStatus": review["independentReviewStatus"], "causalEffect": "not_identified",
    }
