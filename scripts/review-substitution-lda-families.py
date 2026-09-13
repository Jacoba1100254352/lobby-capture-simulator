#!/usr/bin/env python3
"""Inspect candidate LDA families without choosing final versions or amounts."""

import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
SOURCE = DATA / "substitution-lda-family-review.json"
QUEUE = DATA / "substitution-lda-family-queue.csv"
GROUP_FIELDS = ("registrantApiId", "clientRelationshipId", "filingYear", "filingPeriod")
QUEUE_FIELDS = [*GROUP_FIELDS, "canonicalActorId", "primaryName", "filings", "filingUuids",
                "filingTypes", "amendmentLabeledFilings", "distinctSourceAmounts",
                "postingTimeTie", "latestPostingMissingWithEarlierAmount", "noActivityNonzero",
                "sourceFingerprint", "reviewStatus"]


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_lda():
    spec = importlib.util.spec_from_file_location("lda_family_source", ROOT / "scripts/build-substitution-historical-lda-panel.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidate_queue(metadata, catalog):
    """Group only the frozen acquisition frame; do not infer complete families."""
    lda = load_lda()
    if not metadata or len({r["filingUuid"] for r in metadata}) != len(metadata):
        raise ValueError("Missing or duplicate filing metadata")
    names = {r["value"]: r["name"] for r in catalog}
    if len(names) != len(catalog) or not {r["filingType"] for r in metadata} <= names.keys():
        raise ValueError("Duplicate or incomplete filing-type catalog")
    groups = defaultdict(list)
    for row in metadata:
        if row["sourceFingerprint"] != lda.metadata_fingerprint(row):
            raise ValueError("Stale filing metadata")
        if row["filingType"] not in {"RR", "RA"}:
            groups[tuple(row[f] for f in GROUP_FIELDS)].append(row)
    queue = []
    for key, rows in sorted(groups.items()):
        if len(rows) == 1:
            continue
        rows = sorted(rows, key=lambda row: row["filingUuid"])
        if any(len({r[f] for r in rows}) != 1 for f in ("clientApiId", "canonicalActorId", "periodStart", "periodEnd")):
            raise ValueError("Candidate family has conflicting identity or period boundaries")
        posted = [datetime.fromisoformat(r["dtPosted"]) for r in rows]
        if any(stamp.utcoffset() is None for stamp in posted):
            raise ValueError("Posting timestamp lacks an offset")
        latest = max(posted)
        amounts = {(field, Decimal(r[field])) for r in rows for field in ("incomeDollars", "expensesDollars") if r[field]}
        latest_missing = all(not r["incomeDollars"] and not r["expensesDollars"]
                             for r, stamp in zip(rows, posted) if stamp == latest)
        no_activity_nonzero = any("(No Activity)" in names[r["filingType"]]
                                 and any(r[f] and Decimal(r[f]) != 0 for f in ("incomeDollars", "expensesDollars"))
                                 for r in rows)
        queue.append({
            **dict(zip(GROUP_FIELDS, key)), "canonicalActorId": rows[0]["canonicalActorId"],
            "primaryName": rows[0]["primaryName"], "filings": str(len(rows)),
            "filingUuids": ";".join(r["filingUuid"] for r in rows),
            "filingTypes": ";".join(r["filingType"] for r in rows),
            "amendmentLabeledFilings": str(sum("Amendment" in names[r["filingType"]] for r in rows)),
            "distinctSourceAmounts": str(len(amounts)),
            "postingTimeTie": str(len(set(posted)) < len(posted)).lower(),
            "latestPostingMissingWithEarlierAmount": str(latest_missing and bool(amounts)).lower(),
            "noActivityNonzero": str(no_activity_nonzero).lower(),
            "sourceFingerprint": fingerprint([r["sourceFingerprint"] for r in rows]),
            "reviewStatus": "candidate_group_not_adjudicated",
        })
    counts = {
        "sourceFilings": len(metadata), "registrationRecordsExcluded": sum(r["filingType"] in {"RR", "RA"} for r in metadata),
        "candidateGroups": len(groups), "multiRecordGroups": len(queue),
        "singletonAmendmentGroups": sum(len(rows) == 1 and "Amendment" in names[rows[0]["filingType"]]
                                        for rows in groups.values()),
        "multiRecordFilings": sum(int(r["filings"]) for r in queue),
        "groupsWithoutAmendmentLabel": sum(r["amendmentLabeledFilings"] == "0" for r in queue),
        "groupsWithDifferentSourceAmounts": sum(int(r["distinctSourceAmounts"]) > 1 for r in queue),
        "groupsWithPostingTies": sum(r["postingTimeTie"] == "true" for r in queue),
        "groupsWithLatestMissingEarlierAmount": sum(r["latestPostingMissingWithEarlierAmount"] == "true" for r in queue),
        "groupsWithNoActivityNonzero": sum(r["noActivityNonzero"] == "true" for r in queue),
    }
    return queue, counts


def api_projection(record):
    """Retain only fields used in this review, with source-native labels."""
    return {
        **{k: record[k] for k in ("filing_uuid", "filing_type", "filing_type_display", "filing_year", "filing_period",
                                  "dt_posted", "income", "expenses", "expenses_method", "termination_date")},
        "registrant": {k: record["registrant"][k] for k in ("id", "name")},
        "client": {k: record["client"][k] for k in ("id", "client_id", "name")},
        "activities": [{"issueCode": activity["general_issue_code"], "description": activity["description"],
                        "governmentEntities": [dict(entity) for entity in activity["government_entities"]],
                        "lobbyists": [{k: person["lobbyist"][k] for k in ("id", "first_name", "last_name")}
                                      for person in activity["lobbyists"]]}
                       for activity in record["lobbying_activities"]],
    }


def validate_review(metadata, source, cover_source):
    if (source.get("schema") != "substitution-lda-family-review-v1"
            or source.get("reviewFingerprint") != fingerprint({k: v for k, v in source.items() if k != "reviewFingerprint"})
            or source.get("independentReviewStatus") != "pending" or not source.get("reviewer")):
        raise ValueError("Stale or unsupported family review")
    date.fromisoformat(source["reviewDate"])
    queue, counts = candidate_queue(metadata, source["filingTypeCatalog"]["entries"])
    if source["baselineMetadataSha256"] != hashlib.sha256((DATA / "substitution-lda-filing-metadata.csv").read_bytes()).hexdigest():
        raise ValueError("Family review baseline file changed")
    catalog = source["filingTypeCatalog"]
    if (catalog["url"] != "https://lda.gov/api/v1/constants/filing/filingtypes/"
            or not re_hash(catalog["responseSha256"]) or not catalog["scope"]):
        raise ValueError("Missing filing-type catalog provenance")
    query = source["query"]
    url = urlparse(query["url"])
    if (url.scheme != "https" or url.netloc != "lda.gov" or url.path != "/api/v1/filings/"
            or parse_qs(url.query) != {"registrant_id": ["74077"], "filing_year": ["2003"],
                                       "filing_period": ["mid_year"], "page_size": ["100"]}
            or query["count"] != 2 or query["next"] is not None or query["previous"] is not None
            or not re_hash(query["responseSha256"]) or not query["scope"]):
        raise ValueError("Family query scope or pagination changed")
    selected = {r["filingUuid"]: r for r in metadata if tuple(r[f] for f in GROUP_FIELDS) == ("74077", "12", "2003", "mid_year")}
    records = query["records"]
    if len(records) != 2 or {r["filing_uuid"] for r in records} != set(selected):
        raise ValueError("Family query membership mismatch")
    record_by_type = {}
    for record in records:
        row = selected[record["filing_uuid"]]
        expected = {"filing_uuid": row["filingUuid"], "filing_type": row["filingType"],
                    "filing_year": int(row["filingYear"]), "filing_period": row["filingPeriod"],
                    "dt_posted": row["dtPosted"], "income": row["incomeDollars"] or None,
                    "expenses": row["expensesDollars"] or None, "expenses_method": row["expensesMethod"] or None,
                    "termination_date": row["terminationDate"] or None,
                    "registrant": {"id": int(row["registrantApiId"]), "name": row["registrantName"]},
                    "client": {"id": int(row["clientApiId"]), "client_id": int(row["clientRelationshipId"]), "name": row["clientName"]}}
        if any(record[k] != value for k, value in expected.items()):
            raise ValueError("Family API projection differs from frozen metadata")
        if record["filing_type_display"] != dict((r["value"], r["name"]) for r in catalog["entries"])[record["filing_type"]]:
            raise ValueError("Family filing label differs from catalog")
        record_by_type[record["filing_type"]] = record
    if set(record_by_type) != {"MM", "MA"}:
        raise ValueError("Unexpected reviewed filing types")
    original, amendment = (record_by_type[k] for k in ("MM", "MA"))
    cover = next(r for r in cover_source["reviews"] if r["filingUuid"] == original["filing_uuid"])
    if source["originalCoverReviewFingerprint"] != cover_source["reviewFingerprint"]:
        raise ValueError("Stale original cover reference")
    documents = source["documents"]
    if {r["filingUuid"] for r in documents} != set(selected) or len(documents) != 2:
        raise ValueError("Missing or duplicate family document")
    images = {}
    for document in documents:
        if (document["url"] != selected[document["filingUuid"]]["filingDocumentUrl"]
                or not re_hash(document["pdfSha256"])):
            raise ValueError("Invalid source PDF provenance")
        pages = [p for image in document["images"] for p in image["pdfPages"]]
        if sorted(pages) != list(range(1, document["pdfPages"] + 1)):
            raise ValueError("Missing or overlapping embedded-page coverage")
        for image in document["images"]:
            if (image["imageId"] in images or not re_hash(image["pngSha256"])
                    or image["width"] != 1696 or image["height"] != 2200 or not image["scanIdentifier"]):
                raise ValueError("Invalid embedded-image provenance")
            images[image["imageId"]] = image
    original_document = next(d for d in documents if d["filingUuid"] == original["filing_uuid"])
    if original_document["pdfSha256"] != cover["pdfSha256"] or images["original-cover"]["pngSha256"] != cover["embeddedCoverPngSha256"]:
        raise ValueError("Original cover source mismatch")
    expected_images = {"original-cover": "cover", "original-tax": "activity", "original-energy": "activity",
                       "original-update": "information_update", "amendment-energy": "activity"}
    if set(images) != set(expected_images) or any(images[k]["kind"] != v for k, v in expected_images.items()):
        raise ValueError("Financial cover cannot be inferred from an issue/update page")
    original_energy, amended_energy = (images[k] for k in ("original-energy", "amendment-energy"))
    if (original_energy["issueCode"] != "ENG" or amended_energy["issueCode"] != "ENG"
            or original_energy["specificIssue"] != amended_energy["specificIssue"]
            or original_energy["governmentEntities"] != amended_energy["governmentEntities"]
            or original_energy["lobbyists"] != [] or amended_energy["lobbyists"] != ["Bert Kalisch"]
            or original_energy["scanIdentifier"] != amended_energy["underlyingScanIdentifier"]
            or original_energy["signatureDate"] != amended_energy["signatureDate"]):
        raise ValueError("Unsupported field-level amendment comparison")
    if (amended_energy["receiptDate"] != "2004-02-24" or amended_energy["receiptStamp"] != "04 FEB 24 AM 9:33"
            or amended_energy["receiptTimezone"] != "not_stated" or amended_energy["financialAmountFieldsPresent"] is not False
            or images["original-update"]["removedIssueCodes"] != ["TRA"]):
        raise ValueError("Unsupported date, financial field or removed-issue interpretation")
    mismatch = 0
    for record in (original, amendment):
        activities = {a["issueCode"]: a for a in record["activities"]}
        if len(activities) != len(record["activities"]) or set(activities) != ({"ENG", "TAX"} if record is original else {"ENG"}):
            raise ValueError("Activity membership differs from reviewed pages")
        api_names = {e["name"] for e in activities["ENG"]["governmentEntities"]}
        mismatch += api_names != set(original_energy["governmentEntities"])
        if ([p["first_name"] + " " + p["last_name"] for p in activities["ENG"]["lobbyists"]] != ["BERT KALISCH"]
                or activities["ENG"]["description"] is not None):
            raise ValueError("API lobbyist/description fields were changed to match the scans")
        if record is original and ({e["name"] for e in activities["TAX"]["governmentEntities"]}
                                   != set(images["original-tax"]["governmentEntities"])):
            raise ValueError("TAX contact comparison does not match")
    if mismatch != 2:
        raise ValueError("API/scanned ENG agency discrepancies changed")
    boundary = source["boundary"]
    required = {"historicalPacketComplete": False, "finalAmountDollars": None, "selectedFinalFilingUuid": None,
                "rawMetadataUnchanged": True, "agencyExposureCleared": False, "controlAssignmentCleared": False,
                "causalEffect": "not_identified"}
    if any(boundary.get(k) != v for k, v in required.items()) or not boundary["remainingRequirements"]:
        raise ValueError("Unsupported family amount, exposure or causal promotion")
    identity_counts = validate_identity_reviews(metadata, source["identityReviews"], source["identityQuery"])
    history_counts, mixed_groups = validate_nvg_history(metadata, source["nvgHistoryReview"], source["identityReviews"])
    for row in queue:
        if tuple(row[f] for f in GROUP_FIELDS) in mixed_groups:
            row["reviewStatus"] = "source_identity_conflict_not_mergeable"
    return queue, {**counts, "sourceReviewedGroups": 1 + len(mixed_groups), "apgaQueriedApiFilings": len(records),
                   "nvgQueryReturnedFilings": source["identityQuery"]["count"], "identityApiFilingsChecked": 2,
                   "apgaReviewedDistinctImages": len(images), "reviewedDistinctImages": len(images) + history_counts["nvgHistoryPdfCovers"],
                   "energyAgencyMismatches": mismatch,
                   **identity_counts, **history_counts, "finalVersionsSelected": 0, "causalEffect": "not_identified"}


def validate_identity_reviews(metadata, reviews, query):
    """Reject a false candidate family rather than remapping either raw record."""
    by_uuid = {r["filingUuid"]: r for r in metadata}
    expected = {"b53db4eb-a3e2-465a-91b4-51e10da90408", "cda90ce4-487d-415a-98d9-535be41f6b94"}
    if len(reviews) != 2 or {r["filingUuid"] for r in reviews} != expected:
        raise ValueError("Missing or duplicate client-identity review")
    if (query["url"] != "https://lda.gov/api/v1/filings/?registrant_id=76833&filing_year=2005&filing_period=year_end&page_size=100"
            or query["count"] != 14 or query["count"] != len(query["returnedFilingUuids"])
            or len(set(query["returnedFilingUuids"])) != query["count"] or not expected <= set(query["returnedFilingUuids"])
            or query["next"] is not None or query["previous"] is not None or not re_hash(query["responseSha256"])
            or len(query["selectedMetadata"]) != 2
            or {r["filingUuid"] for r in query["selectedMetadata"]} != expected
            or any(r != by_uuid[r["filingUuid"]] for r in query["selectedMetadata"])):
        raise ValueError("Client-identity query scope or source projection differs")
    different_client = suffix_mismatch = unlabelled_amendment = 0
    for review in reviews:
        row = by_uuid[review["filingUuid"]]
        if (review["sourceFingerprint"] != row["sourceFingerprint"]
                or review["url"] != row["filingDocumentUrl"]
                or not re_hash(review["pdfSha256"]) or not re_hash(review["pngSha256"])
                or review["pdfPages"] != 6 or review["coverPdfPages"] != [1, 2]
                or review["coverObjectId"] != "6 0" or review["imageSize"] != [1728, 2200]
                or review["reviewScope"] != "full_embedded_cover_only"):
            raise ValueError("Client-identity review source provenance mismatch")
        form = review["form"]
        if (form["year"] != int(row["filingYear"]) or form["period"] != row["filingPeriod"]
                or form["registrantName"] != "Nueva Vista Group, LLC"
                or form["incomeDollars"] != row["incomeDollars"] or form["clientSelf"] is not False
                or form["receiptDate"] != "2006-02-08" or form["faxDate"] != "2006-07-05"
                or form["receiptTimezone"] != "not_stated"):
            raise ValueError("Client-identity cover fields or dates differ")
        if form["amountDisclosure"] != ("at_least_threshold_rounded" if form["amendmentBoxChecked"] else "numeric_amount_threshold_boxes_unchecked"):
            raise ValueError("Source amount-category caveat changed")
        suffix_mismatch += form["senateId"] != row["registrantApiId"] + "-" + row["clientRelationshipId"]
        unlabelled_amendment += form["amendmentBoxChecked"] and row["filingType"] == "YY"
        if review["filingUuid"] == "cda90ce4-487d-415a-98d9-535be41f6b94":
            if (form["clientName"] != "America Votes" or form["senateId"] != "76833-330" or form["houseId"] != "35960015"
                    or form["amendmentBoxChecked"] is not False
                    or review["disposition"] != "different_client_not_eligible_for_aaj_attribution"):
                raise ValueError("Different-client filing cannot be assigned to AAJ")
            different_client += 1
        elif (form["clientName"] != "Association of Trial Lawyers of America" or form["senateId"] != "76833-113" or form["houseId"] != "35960005"
              or form["amendmentBoxChecked"] is not True
              or review["disposition"] != "historical_client_name_with_registration_and_type_conflicts"):
            raise ValueError("ATLA cover registration/amendment conflicts must remain explicit")
        if (review["rawRecordCorrected"] is not False or review["finalAmountSelected"] is not False
                or review["independentReviewStatus"] != "pending" or not review["remainingRequirements"]):
            raise ValueError("Unsupported identity-review promotion")
    return {"initialIdentityReviewedCovers": 2, "initialDifferentClientCovers": different_client,
            "initialRegistrationSuffixDiscrepancies": suffix_mismatch, "initialUnlabelledAmendedCovers": unlabelled_amendment}


def validate_nvg_history(metadata, history, initial_reviews):
    """Validate the frozen-frame review, not an exhaustive or corrected history."""
    selected = {r["filingUuid"]: r for r in metadata if r["registrantApiId"] == "76833"}
    records = history["records"]
    if (history["schema"] != "nvg-frozen-history-identity-review-v1"
            or history["independentReviewStatus"] != "pending" or not history["reviewer"] or not history["scope"]
            or len(selected) != 21 or len(records) != 21 or {r["filingUuid"] for r in records} != set(selected)):
        raise ValueError("NVG history review must cover the exact frozen 21-record frame")
    date.fromisoformat(history["reviewDate"])
    different = set()
    groups = defaultdict(list)
    pdf_count = html_count = year_conflicts = suffix_conflicts = missing_ids = 0
    by_uuid = {}
    for review in records:
        row = selected[review["filingUuid"]]
        form = review["form"]
        by_uuid[review["filingUuid"]] = review
        if (review["sourceFingerprint"] != row["sourceFingerprint"] or review["url"] != row["filingDocumentUrl"]
                or not re_hash(review["documentSha256"]) or not review["notes"]):
            raise ValueError("NVG history source provenance changed")
        if review["format"] == "pdf":
            pdf_count += 1
            if (review["reviewScope"] != "full_embedded_cover_identity_and_timing"
                    or not re_hash(review["coverPngSha256"]) or review["coverObjectId"] != "6 0"
                    or review["coverImageSize"] not in ([712, 969], [1696, 2200], [1728, 2200])
                    or review["coverPdfPages"] != ([1] if review["coverImageSize"] == [712, 969] else [1, 2])
                    or review["pdfPages"] not in {2, 3, 4, 6} or form["receiptTimezone"] != "not_stated"):
                raise ValueError("NVG PDF cover scope or provenance changed")
            date.fromisoformat(form["receiptDate"])
        elif review["format"] == "html":
            html_count += 1
            if (row["filingYear"] != "2008" or review["reviewScope"] != "html_fields_1_5_6_7_8_9_10"
                    or review["pdfPages"] is not None or review["coverPdfPages"] != []
                    or any(review[k] is not None for k in ("coverObjectId", "coverImageSize", "coverPngSha256"))
                    or form["receiptDate"] is not None or form["receiptTimezone"] != "not_reviewed"
                    or form["clientName"] != "AMERICAN ASSOCIATION FOR JUSTICE"
                    or form["senateId"] != "76833-330" or form["houseId"] != "359600005"):
                raise ValueError("Electronic HTML form is not an independently archived PDF scan")
        else:
            raise ValueError("Unsupported NVG source format")
        name = form["clientName"].upper()
        if name == "AMERICA VOTES":
            expected_disposition = "different_client_not_eligible_for_aaj_attribution"
            different.add(review["filingUuid"])
        elif "TRIAL LAWYERS OF AMERICA" in name:
            expected_disposition = "historical_name_identity_not_cleared"
        elif name in {"AMERICAN ASSN FOR JUSTICE", "AMERICAN ASSOCIATION FOR JUSTICE"}:
            expected_disposition = "matching_name_identity_not_cleared"
        else:
            raise ValueError("Unexpected NVG source client")
        if review["identityDisposition"] != expected_disposition:
            raise ValueError("NVG identity disposition cannot promote a historical actor link")
        if row["filingType"] in {"RR", "RA"}:
            if form["year"] is not None or form["period"] is not None:
                raise ValueError("Registration effective dates are not activity-report periods")
            date.fromisoformat(form["registrationEffectiveDate"])
        else:
            if form["period"] != row["filingPeriod"] or form["registrationEffectiveDate"] is not None:
                raise ValueError("NVG source period changed")
            year_conflicts += form["year"] != int(row["filingYear"])
            groups[tuple(row[f] for f in GROUP_FIELDS)].append(review["filingUuid"])
        missing_ids += form["senateId"] is None
        suffix_conflicts += form["senateId"] is not None and form["senateId"] != row["registrantApiId"] + "-" + row["clientRelationshipId"]
    expected_different = {"84474d21-427e-4bd8-aa25-79bc54c2bd5e", "8e4c1558-6449-4e73-bb00-5ec8a927f015",
                          "cda90ce4-487d-415a-98d9-535be41f6b94", "70676224-e4e0-4a06-8afb-ab7737eacae9",
                          "2d1c91a8-0d49-4121-a930-a8d0181a8396", "c19a316f-abef-42c0-a06c-05e6a46be749"}
    if different != expected_different or (pdf_count, html_count, year_conflicts, suffix_conflicts, missing_ids) != (17, 4, 2, 6, 5):
        raise ValueError("NVG identity, year or registration discrepancies changed")
    for initial in initial_reviews:
        reviewed = by_uuid[initial["filingUuid"]]
        if (reviewed["documentSha256"] != initial["pdfSha256"] or reviewed["coverPngSha256"] != initial["pngSha256"]
                or any(reviewed["form"][k] != initial["form"][k] for k in
                       ("registrantName", "clientName", "senateId", "houseId", "year", "period", "receiptDate", "amendmentBoxChecked"))):
            raise ValueError("NVG history differs from the corrected initial cover review")
    corrections = history["reviewCorrections"]
    if (len(corrections) != 1 or corrections[0]["filingUuid"] != "cda90ce4-487d-415a-98d9-535be41f6b94"
            or corrections[0]["previousValue"] != "35960005" or corrections[0]["correctedValue"] != "35960015"
            or not corrections[0]["reason"]):
        raise ValueError("Review transcription correction must remain explicit")
    boundary = {"rawMetadataUnchanged": True, "actorHistoriesCleared": False, "finalAmountsSelected": 0,
                "controlAssignmentCleared": False, "causalEffect": "not_identified"}
    if history["boundary"] != boundary:
        raise ValueError("Unsupported NVG history promotion")
    mixed = {key for key, uuids in groups.items() if different.intersection(uuids) and set(uuids) - different}
    return {"nvgHistoryReviewedFilings": len(records), "nvgHistoryPdfCovers": pdf_count,
            "nvgHistoryHtmlForms": html_count, "nvgDifferentClientFilings": len(different),
            "nvgDifferentClientActivityFilings": sum(selected[u]["filingType"] not in {"RR", "RA"} for u in different),
            "nvgMixedClientCandidateGroups": len(mixed), "nvgSourceYearDisagreements": year_conflicts,
            "nvgSourceSenateIdDisagreements": suffix_conflicts, "nvgSourceSenateIdBlank": missing_ids}, mixed


def re_hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def main():
    with (DATA / "substitution-lda-filing-metadata.csv").open(newline="", encoding="utf-8") as handle:
        metadata = list(csv.DictReader(handle))
    source = json.loads(SOURCE.read_text())
    cover_source = json.loads((DATA / "substitution-lda-date-reviews.json").read_text())
    queue, counts = validate_review(metadata, source, cover_source)
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        writer.writerows(queue)
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
