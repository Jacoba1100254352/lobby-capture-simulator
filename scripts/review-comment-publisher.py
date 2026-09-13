#!/usr/bin/env python3
"""Validate a frozen publisher-letter inventory and bounded thematic follow-ups.

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
TECHNOLOGY_PAGES = {
    "response": [80, 81, 108, 132, 133, 134, 1240, 1258, 1259, 1260, 1261, 1262, 1263,
                 1309, 1319, 1320, 1321, 1322, 1323, 1411, 1421, 1422, 1423,
                 1608, 1609, 1610, 1611, 1612],
    "proposal": [88, 97, 201],
    "final": [165, 166, 181, 182, 334, 335],
}
TECHNOLOGY_SCOPES = {
    "technology-neutrality": ([132, 133, 134], False),
    "alternative-fuels": ([1259, 1260, 1261, 1262, 1263], True),
    "hydrogen": ([1321, 1322, 1323], True),
    "multipliers": ([1421, 1422, 1423], True),
    "lifecycle": ([1608, 1609, 1610, 1611, 1612], True),
}
TECHNOLOGY_CODINGS = {
    1: ("named_summary_collective_response", "performance_based_approach_explained"),
    4: ("reproduced_request_collective_response", "compliance_pathways_explained_not_blanket_new_incentives"),
    5: ("reproduced_request_collective_response", "pathways_explained_requested_analysis_not_verified"),
    6: ("reproduced_request_collective_response", "specific_carb_program_not_separately_adjudicated"),
    7: ("reproduced_request_thematic_response", "lifecycle_basis_declined_broader_assessment_not_verified"),
    30: ("explicit_named_response", "new_h2ice_multiplier_declined_as_out_of_scope"),
    31: ("reproduced_request_collective_response", "fcev_generation_retained_as_proposed_with_use_limits"),
    32: ("named_summary_collective_response", "vehicle_zero_co2_clause_retained_as_proposed"),
    33: ("named_summary_no_separate_disposition_in_reviewed_section", "carb_engagement_not_separately_resolved"),
}
INFRASTRUCTURE_PAGES = {
    "response": [518, 519, 522, 523, 524, 875, 876, 877, 907, 908, 909, 910, 911,
                 912, 913, 987, 990, 991, 992, 993],
    "proposal": [9, 75],
    "final": [14, 41, 42, 43],
}
INFRASTRUCTURE_SCOPES = {
    "post-rule-monitoring": [518, 519],
    "implementation-coordination": [524],
    "charging-infrastructure": list(range(907, 914)),
    "charging-other": [991, 992, 993],
}
INFRASTRUCTURE_CODINGS = {
    2: ("reproduced_request_collective_response", "continued_coordination_committed_not_complete_priority_alignment"),
    3: ("reproduced_request_collective_response", "monitoring_committed_not_guaranteed_assumption_fulfillment"),
    14: ("reproduced_request_thematic_response", "existing_programs_described_increased_targets_not_verified"),
    16: ("named_summary_collective_response", "v2g_benefits_acknowledged_funding_criterion_not_verified"),
    18: ("reproduced_request_thematic_response", "monitoring_promised_dashboard_not_separately_resolved"),
    22: ("reproduced_request_thematic_response", "existing_standards_described_lifecycle_request_not_fully_resolved"),
    23: ("reproduced_request_no_separate_disposition_in_reviewed_responses", "cybersecurity_policy_not_separately_resolved"),
}
TIMING_PAGES = {
    "response": [235, 236, 244, 245, 246, 247, 248, 249],
    "proposal": [7, 8],
    "final": [11, 40],
}
TIMING_FACTS = {
    "proposalAlreadySolicitsMoreGradualAlternatives": True,
    "finalRetainsSome2027Standards": True,
    "finalDayCabStartModelYear": 2028,
    "finalHeavyVocationalStartModelYear": 2029,
    "finalSleeperStartModelYear": 2030,
    "sleeperStartChangedFromProposal": False,
    "uniformFourYearMinimumAdopted": False,
    "finalEarlyYearsLessStringentThanProposed": True,
    "all2032CategoriesLessStringent": False,
    "lightMediumVocationalAndDayCab2032MoreStringent": True,
    "heavyVocational2032LessStringent": True,
    "sleeper2032StringencyUnchanged": True,
    "operativeClauseChangeAssessed": False,
    "currentLegalStatusAssessed": False,
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


def validate_technology(inventory, ledger):
    """Protect this reviewed artifact, not independently authenticate its coding."""
    check_review(ledger, "comment-publisher-technology-review-v1")
    require(ledger["inventoryFile"] == "comment-publisher-inventory.json"
            and ledger["inventoryFrameSha256"] == inventory["requestFrameSha256"]
            and ledger["publisherSha256"] == inventory["publisher"]["sha256"] == PUBLISHER_SHA,
            "Technology review has stale inventory/source binding")
    expected_ids = [f"mema-1570-r{n:02d}" for n in TECHNOLOGY_CODINGS]
    selection = ledger["selection"]
    require(selection["requestIds"] == expected_ids
            and selection["mode"] == "targeted_technical_fuel_and_hydrogen_clusters"
            and selection["priorOutcomeExposure"] is True and selection["blinded"] is False
            and bool(selection["scope"]), "Technology selection/frame disclosure mismatch")
    require(set(ledger["documents"]) == set(TECHNOLOGY_PAGES), "Missing technology source document")
    for name, pages in TECHNOLOGY_PAGES.items():
        doc = ledger["documents"][name]
        offset = {"response": -18, "proposal": 25925, "final": 29439}[name]
        require(doc["sha256"] == SOURCE_DOCS[name][0] and doc["url"] == SOURCE_URLS[name]
                and doc["reviewedPages"] == [{"pdfPage": p, "printedPage": p + offset} for p in pages]
                and bool(doc["scope"]), "Technology source identity/page mapping mismatch")
    scopes = ledger["responseScopes"]
    require(set(scopes) == set(TECHNOLOGY_SCOPES), "Technology response scopes missing")
    for name, (pages, complete) in TECHNOLOGY_SCOPES.items():
        require(scopes[name]["pdfPages"] == pages and scopes[name]["completeGeneralResponse"] is complete
                and bool(scopes[name]["locator"]), "Technology reviewed response scope changed")
    reviews = ledger["reviews"]
    require([r["requestId"] for r in reviews] == expected_ids, "Technology review frame mismatch")
    rows = {r["requestId"]: r for r in inventory["requests"]}
    # Frozen source links include selected repeated wording, not whole-letter excerpt matches.
    links = [
        ([4, 5], [80, 81], [108], ["technology-neutrality"]),
        ([5, 6], [81, 1309], [], ["alternative-fuels", "hydrogen"]),
        ([5], [1240], [], ["alternative-fuels"]),
        ([5], [1240], [1258], ["alternative-fuels"]),
        ([5, 6], [81], [], ["alternative-fuels", "lifecycle", "hydrogen"]),
        ([14, 15], [1411], [1319], ["hydrogen", "multipliers"]),
        ([14, 15], [1309, 1411], [], ["multipliers"]),
        ([15], [1309], [1319], ["hydrogen", "multipliers"]),
        ([15], [1309], [1319], ["hydrogen"]),
    ]
    comparison_ids = [None] * 5 + ["advanced-multipliers-1037-150-p"] * 2 + [
        "neat-hydrogen-vehicles-1037-150-f", None]
    for r, codes, link, comparison_id in zip(reviews, TECHNOLOGY_CODINGS.values(), links, comparison_ids):
        require(r["citedCommentId"] == COMMENT_ID and r["citedAttachmentOrder"] == 1
                and r["originalPdfPages"] == rows[r["requestId"]]["pdfPages"]
                and tuple(r[k] for k in ("matchedOriginalPdfPages", "excerptPdfPages",
                    "summaryPdfPages", "responseScopeIds")) == link
                and r["excerptContentMatch"] == "selected_request_wording_and_original_page_citations_agree",
                "Technology original/excerpt/response linkage mismatch")
        require((r["responseLink"], r["disposition"]) == codes and r["ruleComparisonId"] == comparison_id
                and bool(r["basis"]) and r["independentReviewStatus"] == "pending"
                and r["individualCausalEffect"] == "not_identified", "Unsupported technology coding/promotion")
    comparisons = ledger["ruleComparisons"]
    require([c["comparisonId"] for c in comparisons] == [
        "advanced-multipliers-1037-150-p", "neat-hydrogen-vehicles-1037-150-f"],
        "Shared technology comparisons must not multiply policy events")
    expected_comparisons = [
        (["mema-1570-r30", "mema-1570-r31"], [201], [335], [88], [165, 166],
         "no_new_h2ice_multiplier_fcev_generation_retained_use_rules_changed", {
             "fcevMultiplier": 5.5, "proposalFcevLastGenerationModelYear": 2027,
             "finalFcevLastGenerationModelYear": 2027, "finalMultiplierUseProhibitedFromModelYear": 2030,
             "h2iceNewMultiplierFinalized": False, "phevBevGenerationDiffersFromProposal": True,
             "baseCreditsShareMultiplierUseCutoff": False, "phase2DeficitResolutionException": True}),
        (["mema-1570-r32"], [201], [334], [97], [181, 182],
         "scoped_vehicle_zero_co2_clause_unchanged_from_proposal", {
             "vehicleCO2Treatment": 0, "neatHydrogenOnly": True, "vehicleClauseUnchanged": True,
             "allPollutantsZero": False, "engineProgramSameAsVehicle": False, "engineDefaultValue": 3,
             "engineDefaultUnit": "g/hp-hr", "engineDefaultOptional": True,
             "engineValueSource": "final_preamble_not_independent_engine_clause_comparison"}),
    ]
    for c, expected in zip(comparisons, expected_comparisons):
        require(tuple(c[k] for k in ("requestIds", "proposalPdfPages", "finalPdfPages",
                    "proposalPreamblePdfPages", "finalPreamblePdfPages", "assessment", "facts")) == expected
                and c["individualAttribution"] == "not_identified" and c["distinctPolicyChanges"] == "not_counted"
                and bool(c["observedChange"]), "Unsupported technology comparison or unit/program conflation")
    cautions = ledger["sourceCautions"]
    expected_cautions = [
        ("renewable-diesel-program-summary", ["mema-1570-r06"], [5], [1240, 1258, 1260, 1261], [],
         "source_scope_mismatch_preserved", "high"),
        ("hydrogen-engine-unit", ["mema-1570-r32"], [15], [1423], [181, 182],
         "source_unit_discrepancy_preserved", "high"),
        ("lifecycle-section-crossreference", ["mema-1570-r07"], [5, 6], [1260, 1421, 1608], [],
         "source_crossreference_discrepancy_preserved", "medium"),
    ]
    require(len(cautions) == len(expected_cautions), "Missing technology source discrepancy")
    for c, expected in zip(cautions, expected_cautions):
        require(tuple(c[k] for k in ("cautionId", "requestIds", "publisherPdfPages", "responsePdfPages",
                    "finalPdfPages", "status", "severity")) == expected and c["finding"] and c["handling"],
                "Technology source discrepancy boundary changed")
    boundary = ledger["boundary"]
    require(all(boundary.get(k) == v for k, v in {
        "officialAttachmentByteMatch": "not_verified", "independentReviewStatus": "pending",
        "docketRateEligible": False, "overallLetterResponseCodingComplete": False,
        "currentLegalStatusAssessed": False, "causalEffect": "not_identified", "simulatorRecalibrated": False,
        "remainingEntriesStatus": "not_yet_adjudicated_not_nonresponse"}.items())
        and boundary["comparisonBoundary"] and boundary["unreviewedAnalysis"],
        "Unsupported technology review claim boundary")
    return {"technologyEntriesReviewed": len(reviews),
        "technologyResponseLinks": dict(Counter(r["responseLink"] for r in reviews)),
        "technologyScopedRuleComparisons": len(comparisons), "technologySourceCautions": len(cautions)}


def validate_infrastructure(inventory, ledger):
    """Validate the saved review contract, not the truth of manual adjudication."""
    check_review(ledger, "comment-publisher-infrastructure-review-v1")
    require(ledger["inventoryFile"] == "comment-publisher-inventory.json"
            and ledger["inventoryFrameSha256"] == inventory["requestFrameSha256"]
            and ledger["publisherSha256"] == inventory["publisher"]["sha256"] == PUBLISHER_SHA,
            "Infrastructure review has stale inventory/source binding")
    expected_ids = [f"mema-1570-r{n:02d}" for n in INFRASTRUCTURE_CODINGS]
    selection = ledger["selection"]
    require(selection["requestIds"] == expected_ids
            and selection["mode"] == "targeted_coordination_monitoring_funding_and_charger_standards"
            and selection["priorOutcomeExposure"] is True and selection["blinded"] is False
            and bool(selection["scope"]), "Infrastructure selection/frame disclosure mismatch")
    visual = ledger["publisherReview"]
    require(visual["pdfPages"] == [4, 9, 10, 11, 12, 23, 25, 26]
            and visual["method"] == "rendered_pages_with_text_navigation" and visual["scope"],
            "Infrastructure original visual scope mismatch")
    require(set(ledger["documents"]) == set(INFRASTRUCTURE_PAGES), "Missing infrastructure document")
    for name, pages in INFRASTRUCTURE_PAGES.items():
        doc = ledger["documents"][name]
        offset = {"response": -18, "proposal": 25925, "final": 29439}[name]
        require(doc["sha256"] == SOURCE_DOCS[name][0] and doc["url"] == SOURCE_URLS[name]
                and doc["reviewedPages"] == [{"pdfPage": p, "printedPage": p + offset} for p in pages]
                and doc["scope"], "Infrastructure source identity/page mapping mismatch")
    scopes = ledger["responseScopes"]
    require(set(scopes) == set(INFRASTRUCTURE_SCOPES), "Infrastructure response scopes missing")
    for name, pages in INFRASTRUCTURE_SCOPES.items():
        require(scopes[name]["pdfPages"] == pages and scopes[name]["completeGeneralResponse"] is True
                and scopes[name]["locator"], "Infrastructure reviewed response scope changed")
    reviews = ledger["reviews"]
    require([r["requestId"] for r in reviews] == expected_ids, "Infrastructure review frame mismatch")
    rows = {r["requestId"]: r for r in inventory["requests"]}
    links = [
        ([4], [522], [523, 524], ["implementation-coordination"]),
        ([4], [522], [523, 524], ["implementation-coordination", "post-rule-monitoring"]),
        ([9], [522, 523], [523, 524], ["implementation-coordination", "charging-infrastructure", "charging-other"]),
        ([10], [875], [990], ["charging-infrastructure", "charging-other"]),
        ([10], [875], [], ["charging-infrastructure", "charging-other", "post-rule-monitoring"]),
        ([11], [876], [990], ["charging-infrastructure", "charging-other"]),
        ([11, 12], [876, 877], [], ["charging-infrastructure", "charging-other"]),
    ]
    for r, number, codes, link in zip(reviews, INFRASTRUCTURE_CODINGS, INFRASTRUCTURE_CODINGS.values(), links):
        require(r["citedCommentId"] == COMMENT_ID and r["citedAttachmentOrder"] == 1
                and r["originalPdfPages"] == rows[r["requestId"]]["pdfPages"]
                and tuple(r[k] for k in ("matchedOriginalPdfPages", "excerptPdfPages",
                    "summaryPdfPages", "responseScopeIds")) == link
                and r["excerptContentMatch"] == "selected_request_wording_and_original_page_citations_agree"
                and r["supportingRationaleExcerptPdfPages"] == ([987] if number == 16 else []),
                "Infrastructure original/excerpt/response linkage mismatch")
        expected_comparison = "phase3-monitoring-preamble" if number in {2, 3, 18} else None
        require((r["responseLink"], r["disposition"]) == codes and r["ruleComparisonId"] == expected_comparison
                and r["basis"] and r["independentReviewStatus"] == "pending"
                and r["individualCausalEffect"] == "not_identified", "Unsupported infrastructure coding/promotion")
    comparisons = ledger["ruleComparisons"]
    require(len(comparisons) == 1, "Shared infrastructure comparison must not multiply policy events")
    c = comparisons[0]
    require(c["comparisonId"] == "phase3-monitoring-preamble"
            and c["requestIds"] == ["mema-1570-r02", "mema-1570-r03", "mema-1570-r18"]
            and c["comparisonType"] == "preamble_commitment_not_operative_clause"
            and c["proposalPdfPages"] == [9, 75] and c["finalPdfPages"] == [14, 41, 42, 43]
            and c["proposalLocator"] and c["finalLocator"] and c["observedChange"]
            and c["assessment"] == "existing_monitoring_and_solicitation_extended_to_specific_final_commitments"
            and c["distinctPolicyChanges"] == "not_counted" and c["individualAttribution"] == "not_identified"
            and c["facts"] == {
                "proposalAlreadyDescribesMonitoring": True,
                "proposalAlreadySolicitsAdditionalInformationAndStakeholders": True,
                "finalCommitsPeriodicReports": True, "finalDataCollectionStartCalendarYear": 2025,
                "finalReportsEarliestCalendarYear": 2026, "reportStartQualifier": "as_early_as",
                "finalAddressesCriticalMaterials": True, "finalNamesDOEAndDOTCoordination": True,
                "finalSelfAdjustingStandardsLinkage": False,
                "requestedDashboardAdoptedInReviewedPassages": "not_verified",
                "allAssumptionsGuaranteed": False, "implementationVerified": False,
                "operativeClauseChangeAssessed": False}, "Unsupported infrastructure preamble comparison")
    cautions = ledger["sourceCautions"]
    expected_cautions = [
        ("dashboard-versus-dtna-reporting", ["mema-1570-r18"], [10, 26], [875, 990, 991, 992],
         "different_commenter_and_instrument_preserved", "high"),
        ("charger-lifecycle-versus-efficiency", ["mema-1570-r22"], [11], [876, 987, 990, 992, 993],
         "source_scope_mismatch_preserved", "high"),
        ("corridor-phase-timeline", ["mema-1570-r14"], [9, 25, 26], [912, 991],
         "source_timeline_tension_not_adjudicated", "medium"),
    ]
    require(len(cautions) == len(expected_cautions), "Missing infrastructure source caution")
    for caution, expected in zip(cautions, expected_cautions):
        require(tuple(caution[k] for k in ("cautionId", "requestIds", "publisherPdfPages",
                    "responsePdfPages", "status", "severity")) == expected
                and caution["finding"] and caution["handling"], "Infrastructure source caution boundary changed")
    boundary = ledger["boundary"]
    require(all(boundary.get(k) == v for k, v in {
        "officialAttachmentByteMatch": "not_verified", "independentReviewStatus": "pending",
        "docketRateEligible": False, "overallLetterResponseCodingComplete": False,
        "currentLegalStatusAssessed": False, "causalEffect": "not_identified", "simulatorRecalibrated": False,
        "remainingEntriesStatus": "not_yet_adjudicated_not_nonresponse"}.items())
        and boundary["comparisonBoundary"] and boundary["unreviewedAnalysis"],
        "Unsupported infrastructure review claim boundary")
    return {"infrastructureEntriesReviewed": len(reviews),
        "infrastructureResponseLinks": dict(Counter(r["responseLink"] for r in reviews)),
        "infrastructurePreambleComparisons": len(comparisons), "infrastructureSourceCautions": len(cautions)}


def validate_timing(inventory, ledger):
    """Check saved source/coding invariants, not independent substantive review."""
    check_review(ledger, "comment-publisher-timing-review-v1")
    require(ledger["inventoryFile"] == "comment-publisher-inventory.json"
            and ledger["inventoryFrameSha256"] == inventory["requestFrameSha256"]
            and ledger["publisherSha256"] == inventory["publisher"]["sha256"] == PUBLISHER_SHA,
            "Timing review has stale inventory/source binding")
    expected_ids = ["mema-1570-r08", "mema-1570-r09"]
    require([r["requestId"] for r in inventory["requests"] if r["topic"] == "timing"] == expected_ids,
            "Timing topic population changed")
    selection = ledger["selection"]
    require(selection["requestIds"] == expected_ids
            and selection["mode"] == "complete_timing_topic_in_frozen_letter"
            and selection["priorOutcomeExposure"] is True and selection["blinded"] is False
            and selection["scope"], "Timing selection/frame disclosure mismatch")
    visual = ledger["publisherReview"]
    require(visual["pdfPages"] == [6, 7] and visual["method"] == "rendered_pages_with_text_navigation"
            and visual["scope"], "Timing original visual scope mismatch")
    require(set(ledger["documents"]) == set(TIMING_PAGES), "Missing timing source document")
    for name, pages in TIMING_PAGES.items():
        doc = ledger["documents"][name]
        offset = {"response": -18, "proposal": 25925, "final": 29439}[name]
        require(doc["sha256"] == SOURCE_DOCS[name][0] and doc["url"] == SOURCE_URLS[name]
                and doc["reviewedPages"] == [{"pdfPage": p, "printedPage": p + offset} for p in pages]
                and doc["scope"], "Timing source identity/page mapping mismatch")
    scopes = ledger["responseScopes"]
    require(set(scopes) == {"lead-time-and-stability"}
            and scopes["lead-time-and-stability"]["pdfPages"] == [245, 246, 247, 248, 249]
            and scopes["lead-time-and-stability"]["completeGeneralResponse"] is True
            and scopes["lead-time-and-stability"]["locator"], "Timing response scope mismatch")
    reviews = ledger["reviews"]
    require([r["requestId"] for r in reviews] == expected_ids, "Timing review frame mismatch")
    rows = {r["requestId"]: r for r in inventory["requests"]}
    codings = [
        ("reproduced_request_collective_response", "blanket_four_year_requirement_declined_category_specific_delays"),
        ("reproduced_request_no_separate_disposition_in_reviewed_response", "specific_transition_cost_addition_not_verified"),
    ]
    for index, (r, codes) in enumerate(zip(reviews, codings)):
        require(r["citedCommentId"] == COMMENT_ID and r["citedAttachmentOrder"] == 1
                and r["originalPdfPages"] == rows[r["requestId"]]["pdfPages"]
                and r["matchedOriginalPdfPages"] == ([6, 7] if index == 0 else [7])
                and r["excerptPdfPages"] == ([235, 236] if index == 0 else [236])
                and r["summaryPdfPages"] == [244, 245]
                and r["responseScopeIds"] == ["lead-time-and-stability"]
                and r["excerptContentMatch"] == "selected_request_wording_and_original_page_citations_agree",
                "Timing original/excerpt/response linkage mismatch")
        require((r["responseLink"], r["disposition"]) == codes
                and r["ruleComparisonId"] == ("phase3-category-timing-preamble" if index == 0 else None)
                and r["basis"] and r["independentReviewStatus"] == "pending"
                and r["individualCausalEffect"] == "not_identified", "Unsupported timing coding/promotion")
    require(reviews[0]["facets"] == {
        "claimedStatutoryMinimum": "rejected_in_collective_response_addressing_EMA",
        "uniformNoEarlierThan2028": "not_adopted_for_all_categories",
        "selectedCategoryDelays": "documented_in_final_preamble",
        "individualAttribution": "not_identified"}, "Timing facet or commenter conflation")
    require(reviews[1]["sourceCondition"] == "If EPA chooses to stay with MY2028"
            and reviews[1]["conditionInterpretation"] == "source_condition_ambiguous_not_repaired"
            and rows[expected_ids[1]]["kind"] == "conditional_request",
            "Timing conditional source wording must not be repaired")
    comparisons = ledger["ruleComparisons"]
    require(len(comparisons) == 1, "Timing comparison must not multiply policy events")
    c = comparisons[0]
    require(c["comparisonId"] == "phase3-category-timing-preamble" and c["requestIds"] == expected_ids[:1]
            and c["comparisonType"] == "published_preamble_descriptions_not_operative_clause_audit"
            and c["proposalPdfPages"] == [7, 8] and c["finalPdfPages"] == [11, 40]
            and c["proposalLocator"] and c["finalLocator"] and c["observedChange"]
            and c["assessment"] == "partial_category_timing_alignment_not_blanket_acceptance"
            and c["distinctPolicyChanges"] == "not_counted" and c["individualAttribution"] == "not_identified"
            and c["facts"] == TIMING_FACTS, "Unsupported timing preamble comparison")
    expected_cautions = [
        ("conditional-my2028", expected_ids[1:], [7], [236], "source_condition_ambiguous_not_repaired"),
        ("ema-is-not-mema", expected_ids[:1], [6, 7], [235, 236, 244, 245], "different_named_commenter_preserved"),
        ("timing-is-not-blanket-relaxation", expected_ids[:1], [6, 7], [248], "category_year_and_measure_distinctions_preserved"),
    ]
    require(len(ledger["sourceCautions"]) == len(expected_cautions), "Missing timing source caution")
    for caution, expected in zip(ledger["sourceCautions"], expected_cautions):
        require(tuple(caution[k] for k in ("cautionId", "requestIds", "publisherPdfPages",
                    "responsePdfPages", "status")) == expected and caution["severity"] == "high"
                and caution["finding"] and caution["handling"], "Timing source caution changed")
    boundary = ledger["boundary"]
    require(all(boundary.get(k) == v for k, v in {
        "officialAttachmentByteMatch": "not_verified", "independentReviewStatus": "pending",
        "docketRateEligible": False, "overallLetterResponseCodingComplete": False,
        "currentLegalStatusAssessed": False, "causalEffect": "not_identified", "simulatorRecalibrated": False,
        "remainingEntriesStatus": "not_yet_adjudicated_not_nonresponse"}.items())
        and boundary["comparisonBoundary"] and boundary["unreviewedAnalysis"],
        "Unsupported timing review claim boundary")
    return {"timingEntriesReviewed": len(reviews),
        "timingResponseLinks": dict(Counter(r["responseLink"] for r in reviews)),
        "timingPreambleComparisons": len(comparisons), "timingSourceCautions": len(expected_cautions)}


def validate_all(inventory, warranty, technology, infrastructure=None, timing=None):
    """Aggregate supplied follow-ups; omitted ledgers retain historical review scopes."""
    result = validate(inventory, warranty)
    result.update(validate_technology(inventory, technology))
    ledgers = [warranty, technology]
    if infrastructure is not None:
        result.update(validate_infrastructure(inventory, infrastructure))
        ledgers.append(infrastructure)
    if timing is not None:
        result.update(validate_timing(inventory, timing))
        ledgers.append(timing)
    ids = [r["requestId"] for ledger in ledgers for r in ledger["reviews"]]
    require(len(ids) == len(set(ids)), "Overlapping publisher follow-ups inflate review coverage")
    result["boundedResponseReviews"] = len(ids)
    result["otherEntriesAwaitingAdjudication"] = result["inventoryEntries"] - len(ids)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("publisher-pdf", "metadata-json", "response-pdf", "proposal-pdf", "final-pdf"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    inventory = json.loads((DATA / "comment-publisher-inventory.json").read_text())
    followup = json.loads((DATA / "comment-publisher-warranty-review.json").read_text())
    technology = json.loads((DATA / "comment-publisher-technology-review.json").read_text())
    infrastructure = json.loads((DATA / "comment-publisher-infrastructure-review.json").read_text())
    timing = json.loads((DATA / "comment-publisher-timing-review.json").read_text())
    result = validate_all(inventory, followup, technology, infrastructure, timing)
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
