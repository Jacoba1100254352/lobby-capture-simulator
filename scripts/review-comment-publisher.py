#!/usr/bin/env python3
"""Validate a frozen publisher-letter inventory and bounded warranty follow-up.

Offline checks protect identities, grain and claim boundaries. They cannot
authenticate an unread docket PDF or independently adjudicate manual coding.
Optional local source files additionally verify the archived bytes.
"""

import argparse
from collections import Counter
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
COMMENT_ID = "EPA-HQ-OAR-2022-0985-1570"
PUBLISHER_SHA = "e6f6c3c34594d69654b4375e29896175b3057f4c6a0c987e141ac229f10d0159"
SOURCE_DOCS = {
    "response": ("4ce468a6ea85ede970b8189dab82b0ab5112692abcc1f684a585f563b6b4ab8e",
                 [(1461, 1443), (1466, 1448), (1467, 1449), (1468, 1450)]),
    "proposal": ("30f6f81aadc5313a4762e4234f93a4d937f83c5db75ec2607eb68ce028affc1a",
                 [(199, 26124), (200, 26125)]),
    "final": ("9d1b9a74a8528e36b7783ddfacf9b3089f484225431b1496324b5d5d2963eb94",
              [(174, 29613), (175, 29614), (333, 29772)]),
}
SOURCE_URLS = {
    "response": "https://www.epa.gov/system/files/documents/2024-03/420r24007.pdf",
    "proposal": "https://www.govinfo.gov/content/pkg/FR-2023-04-27/pdf/2023-07955.pdf",
    "final": "https://www.govinfo.gov/content/pkg/FR-2024-04-22/pdf/2024-06809.pdf",
}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_review(ledger, schema):
    require(ledger.get("schema") == schema, "Publisher review schema mismatch")
    require(ledger.get("reviewFingerprint") == fingerprint({
        k: v for k, v in ledger.items() if k != "reviewFingerprint"}), "Stale publisher review fingerprint")
    require(bool(ledger.get("reviewer")), "Missing publisher reviewer")
    date.fromisoformat(ledger["reviewDate"])


def metadata_projection(raw):
    attrs = raw["data"]["attributes"]
    attachments = raw["included"]
    require(len(attachments) == 1, "Unexpected publisher attachment frame")
    attachment = attachments[0]
    return {
        "commentId": raw["data"]["id"],
        **{key: attrs[key] for key in ("title", "docketId", "commentOnDocumentId", "documentType",
             "receiveDate", "postmarkDate", "postedDate", "modifyDate", "withdrawn", "pageCount")},
        "attachment": {"id": attachment["id"], **{key: attachment["attributes"][key]
            for key in ("docAbstract", "docOrder", "fileFormats", "modifyDate")}},
    }


def validate(inventory, followup):
    check_review(inventory, "comment-publisher-inventory-v1")
    publisher = inventory["publisher"]
    require(inventory["commentId"] == COMMENT_ID and inventory["attachmentOrder"] == 1,
            "Publisher comment/attachment identity mismatch")
    require(publisher["sha256"] == PUBLISHER_SHA and publisher["bytes"] == 6264676
            and publisher["pdfPageCount"] == 28 and publisher["reviewedPdfPages"] == list(range(1, 29))
            and publisher["reviewMethod"] == "rendered_pages_with_OCR_navigation"
            and bool(publisher["textExtractionWarning"]), "Publisher source or visual coverage mismatch")
    metadata = inventory["docketMetadata"]
    projection = metadata["projection"]
    require(metadata["projectionSha256"] == fingerprint(projection), "Stale metadata projection fingerprint")
    attachment = projection["attachment"]
    formats = attachment["fileFormats"]
    require(projection["commentId"] == COMMENT_ID and projection["docketId"] == "EPA-HQ-OAR-2022-0985"
            and projection["commentOnDocumentId"] == "EPA-HQ-OAR-2022-0985-1423"
            and projection["documentType"] == "Public Submission" and projection["withdrawn"] is False
            and attachment["id"] == "0900006485b3e60c" and attachment["docOrder"] == 1,
            "Publisher metadata identity mismatch")
    require(len(formats) == 1 and formats[0] == {
        "fileUrl": f"https://downloads.regulations.gov/{COMMENT_ID}/attachment_1.pdf",
        "format": "pdf", "size": publisher["bytes"]}, "Publisher metadata byte size/attachment mismatch")
    require(urlparse(publisher["url"]).netloc == "www.mema.org"
            and Path(unquote(urlparse(publisher["url"]).path)).stem == attachment["docAbstract"],
            "Publisher filename and metadata title mismatch")
    require(projection["pageCount"] == 1 and metadata["pageCountMeaning"] == "content_file_not_attachment",
            "Metadata content page count must not replace attachment length")
    receive, postmark, posted = [datetime.fromisoformat(projection[k].replace("Z", "+00:00"))
                              for k in ("receiveDate", "postmarkDate", "postedDate")]
    require(receive == postmark and receive.date() == date.fromisoformat(publisher["letterDate"])
            and receive < posted, "Publisher receipt/posting chronology mismatch")
    require(inventory["authentication"] == {
        "publisherFileRead": True, "metadataTitleAndSizeAgree": True, "officialAttachmentRead": False,
        "officialAttachmentHttpStatus": 403, "byteVersionMatch": "not_verified",
        "historicalArchiveTimeVerified": False}, "Unsupported publisher authentication promotion")
    selection = inventory["selection"]
    require(selection["mode"] == "access_led_single_publisher_case" and selection["priorOutcomeExposure"] is True
            and all(selection[k] for k in ("priorExposureScope", "sequence", "population"))
            and selection["baselineProductsUnchanged"] == ["comment-body-corpus.csv",
                "comment-response-document-pilot.csv", "comment-section-inventory.csv"],
            "Publisher selection or baseline boundary changed")
    rows = inventory["requests"]
    ids = [r["requestId"] for r in rows]
    require(ids == [f"mema-1570-r{n:02d}" for n in range(1, 49)], "Missing, duplicate or off-frame publisher request")
    require(inventory["requestFrameSha256"] == fingerprint(rows), "Stale request frame fingerprint")
    for number, row in enumerate(rows, 1):
        require(all(isinstance(row[k], str) and row[k].strip() for k in ("label", "locator", "topic")),
                "Missing publisher request coding")
        pages = row["pdfPages"]
        require(pages and pages == sorted(set(pages)) and all(type(p) is int and 1 <= p <= 28 for p in pages),
                "Invalid publisher request page")
        expected_kind = "retention_position" if number in {25, 31, 32} else (
            "conditional_request" if number == 9 else "requested_action")
        expected_flag = "indirect_request" if number == 13 else (
            "source_condition_ambiguous" if number == 9 else "none")
        require(row["kind"] == expected_kind and row["interpretiveFlag"] == expected_flag,
                "Publisher retention/conditional/indirect classification changed")
    coverage = inventory["pageCoverage"]
    require([r["pdfPage"] for r in coverage] == list(range(1, 29)), "Publisher page coverage incomplete")
    for page in coverage:
        require(page["requestIds"] == [r["requestId"] for r in rows if page["pdfPage"] in r["pdfPages"]]
                and page["reviewStatus"] == "visually_reviewed" and bool(page["role"]),
                "Publisher page-to-request linkage mismatch")
    segmentation = inventory["segmentation"]
    require(all(segmentation[k] for k in ("rule", "retentionRule", "conditionalRule", "indirectRule",
                "facetRule", "exclusions")), "Missing publisher segmentation decisions")
    require(all(set(group) <= set(ids) and len(group) == len(set(group))
                for group in segmentation["relatedActions"]), "Invalid related publisher actions")
    require(inventory["boundary"] == {
        "independentReviewStatus": "pending", "docketRateEligible": False, "causalEffect": "not_identified",
        "originalDocketVersionVerified": False, "simulatorRecalibrated": False,
        "responseCodingStatusAtFrameFreeze": "not_yet_coded",
        "missingResponseMeaning": "not_searched_or_not_adjudicated_never_no_response"},
        "Unsupported publisher inventory promotion")

    check_review(followup, "comment-publisher-warranty-review-v1")
    require(followup["inventoryFile"] == "comment-publisher-inventory.json"
            and followup["inventoryFrameSha256"] == inventory["requestFrameSha256"]
            and followup["publisherSha256"] == publisher["sha256"], "Warranty review has stale inventory/source binding")
    require(bool(followup["selection"]), "Missing warranty selection disclosure")
    require(set(followup["documents"]) == set(SOURCE_DOCS), "Missing warranty comparison document")
    for name, (digest, pairs) in SOURCE_DOCS.items():
        doc = followup["documents"][name]
        require(doc["sha256"] == digest and doc["url"] == SOURCE_URLS[name] and doc["reviewedPages"] == [
            {"pdfPage": p, "printedPage": n} for p, n in pairs] and bool(doc["scope"]),
            "Warranty document identity or page mapping mismatch")
    reviews = followup["reviews"]
    warranty_ids = [f"mema-1570-r{n}" for n in range(26, 30)]
    require([r["requestId"] for r in reviews] == warranty_ids
            and [r["requestId"] for r in rows if r["topic"] == "warranty"] == warranty_ids,
            "Warranty follow-up frame mismatch")
    expected = [
        ("explicit_named_response", "agency_says_existing_provision_addresses_concern", [], None),
        ("named_collective_referral", "clarification_with_broader_component_scope", [174, 175], "warranty-components-1037-120-c"),
        ("named_collective_referral", "blanket_exclusion_not_supported_by_reviewed_rule", [174, 175], "warranty-components-1037-120-c"),
        ("no_separate_disposition_in_reviewed_passages", "supplier_list_process_not_separately_resolved", [174, 175], None),
    ]
    for index, (review, codes) in enumerate(zip(reviews, expected)):
        require(review["citedCommentId"] == COMMENT_ID and review["citedAttachmentOrder"] == 1
                and review["originalPdfPages"] == ([13, 14] if index == 0 else [14])
                and review["excerptPdfPages"] == [1461] and review["summaryPdfPages"] == [1466]
                and review["responsePdfPages"] == [1467, 1468]
                and review["excerptContentMatch"] == "request_wording_and_original_page_citation_agree",
                "Warranty original/excerpt/response link mismatch")
        require(tuple(review[k] for k in ("responseLink", "disposition", "finalPreamblePdfPages", "ruleComparisonId")) == codes
                and bool(review["basis"]) and review["independentReviewStatus"] == "pending"
                and review["individualCausalEffect"] == "not_identified", "Unsupported warranty disposition/promotion")
    comparisons = followup["ruleComparisons"]
    require(len(comparisons) == 1, "Shared warranty comparison must not multiply policy events")
    comparison = comparisons[0]
    require(comparison["comparisonId"] == "warranty-components-1037-120-c"
            and comparison["requestIds"] == ["mema-1570-r27", "mema-1570-r28"]
            and comparison["proposalPdfPages"] == [199, 200] and comparison["finalPdfPages"] == [333]
            and comparison["assessment"] == "broad_coverage_in_both_versions_with_text_reorganization"
            and comparison["distinctPolicyChanges"] == "not_counted"
            and comparison["individualAttribution"] == "not_identified" and bool(comparison["observedChange"]),
            "Unsupported warranty rule comparison")
    boundary = followup["boundary"]
    require(all(boundary.get(k) == v for k, v in {
        "officialAttachmentByteMatch": "not_verified", "independentReviewStatus": "pending",
        "docketRateEligible": False, "overallLetterResponseCodingComplete": False,
        "currentLegalStatusAssessed": False, "causalEffect": "not_identified",
        "remainingEntriesStatus": "not_yet_adjudicated_not_nonresponse"}.items())
        and bool(boundary["comparisonBoundary"]), "Unsupported warranty follow-up claim boundary")
    return {"publisherLetters": 1, "visuallyReviewedPages": len(coverage), "inventoryEntries": len(rows),
        "entryKinds": dict(Counter(r["kind"] for r in rows)), "warrantyEntriesReviewed": len(reviews),
        "otherEntriesAwaitingAdjudication": len(rows) - len(reviews),
        "warrantyResponseLinks": dict(Counter(r["responseLink"] for r in reviews)),
        "metadataSizeTitleMatches": 1, "verifiedDocketByteMatches": 0,
        "independentlyReviewedEntries": 0, "docketRateEligibleEntries": 0, "causalEffect": "not_identified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("publisher-pdf", "metadata-json", "response-pdf", "proposal-pdf", "final-pdf"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    inventory = json.loads((DATA / "comment-publisher-inventory.json").read_text())
    followup = json.loads((DATA / "comment-publisher-warranty-review.json").read_text())
    result = validate(inventory, followup)
    checked = []
    for name, digest in {"publisher_pdf": PUBLISHER_SHA,
            "metadata_json": inventory["docketMetadata"]["rawSha256"],
            **{k + "_pdf": v[0] for k, v in SOURCE_DOCS.items()}}.items():
        path = getattr(args, name)
        if path is not None:
            payload = path.read_bytes()
            require(hashlib.sha256(payload).hexdigest() == digest, f"Archived source bytes mismatch: {name}")
            if name == "metadata_json":
                require(metadata_projection(json.loads(payload)) == inventory["docketMetadata"]["projection"],
                        "Archived metadata does not reproduce projection")
            checked.append(name)
    print(json.dumps({"findings": result, "sourceBytesVerifiedThisRun": checked}, indent=2))


if __name__ == "__main__":
    main()
