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


SUPPLY_PAGES = {
    "response": [(p, p - 18) for p in [784, 791, 1637, 1667, *range(1670, 1682), 1690, 1691]],
    "proposal": [(44, 25969)],
    "final": [(59, 29498), (60, 29499)],
    "argonne": [(1, None), (3, None), (14, "x"), (94, 76), (103, 85), (104, 86)],
    "ria": [(1, None), (284, 259), (572, 547)],
}
SUPPLY_EXTRA_DOCS = {
    "argonne": ("75e1a3b01de0545418c8f7e034c0b4c5bd5339365e229ae89f7eacdf15e360e0",
                "https://publications.anl.gov/anlpubs/2024/03/187907.pdf", 3219953, 106, "ANL-24/06"),
    "ria": ("46e0d7944c94f3b83ffaa30c20d05d69f061a1c244a941e4e3f5e0c2f9043165",
            "https://nepis.epa.gov/Exe/ZyPDF.cgi?Dockey=P101A93R.pdf", 13228970, 961, "EPA-420-R-24-006"),
}
SUPPLY_FACTS = [
    {"proposalAlreadyDiscussedRecycling": True, "riaReportsAddedBatteryReplacementCosts": True,
     "replacementEqualsRecyclingOrDisposal": False, "requestedCostAdditionVerified": False,
     "allCostInputsAudited": False},
    {"epaReportsExpandedLithiumAnalysis": True,
     "weightedLithiumScenarioSource": "BMI_as_reproduced_by_EPA",
     "anlFigureII2AxisUnit": "thousand_tonnes", "anlFigureII2MinedLithiumBasis": "contained_LCE",
     "bmiFigureII3AxisUnit": "GWh_equivalent",
     "bmiProjectsIncluded": 153, "bmiProjectsExcluded": 177, "bmiScenarioLines": 3,
     "bmiRecyclingAssumption": "maximum_potential_conditional_on_demand",
     "anlCapacityUtilizationAssumption": 0.9, "anlTable13PermittingDelaysIncluded": False,
     "anlUncertaintySensitivities": "future_work", "statisticalConfidenceLevelsVerified": False,
     "fullRequestedMethodPackageVerified": False,
     "sourceForecastsValidatedAgainstRealizedProduction": False},
]


def validate_supply(inventory, ledger):
    """Protect reviewed documentary distinctions; not a substantive replication."""
    check_review(ledger, "comment-publisher-supply-review-v1")
    require(ledger["inventoryFile"] == "comment-publisher-inventory.json"
            and ledger["inventoryFrameSha256"] == inventory["requestFrameSha256"]
            and ledger["publisherSha256"] == inventory["publisher"]["sha256"] == PUBLISHER_SHA,
            "Supply review has stale inventory/source binding")
    ids = ["mema-1570-r10", "mema-1570-r11"]
    require([r["requestId"] for r in inventory["requests"] if r["topic"] == "supply_chain"] == ids,
            "Supply topic population changed")
    selection = ledger["selection"]
    require(selection["requestIds"] == ids
            and selection["mode"] == "complete_supply_chain_topic_in_frozen_letter"
            and selection["priorOutcomeExposure"] is True and selection["blinded"] is False
            and selection["scope"], "Supply selection/frame disclosure mismatch")
    visual = ledger["publisherReview"]
    require(visual["pdfPages"] == [7, 8] and visual["method"] == "rendered_pages_with_text_navigation"
            and visual["scope"], "Supply original visual scope mismatch")
    require(set(ledger["documents"]) == set(SUPPLY_PAGES), "Missing supply source document")
    for name, pairs in SUPPLY_PAGES.items():
        doc = ledger["documents"][name]
        digest, url = (SUPPLY_EXTRA_DOCS[name][:2] if name in SUPPLY_EXTRA_DOCS
                       else (SOURCE_DOCS[name][0], SOURCE_URLS[name]))
        require(doc["sha256"] == digest and doc["url"] == url and doc["scope"]
                and doc["reviewedPages"] == [{"pdfPage": p, "printedPage": n} for p, n in pairs],
                "Supply source identity/page mapping mismatch")
        if name in SUPPLY_EXTRA_DOCS:
            require((doc["byteSize"], doc["pageCount"], doc["reportNumber"]) == SUPPLY_EXTRA_DOCS[name][2:]
                    and doc["title"], "Supply additional source metadata mismatch")
    anl = ledger["documents"]["argonne"]
    require(anl["titlePageDate"] == "February 2024" and anl["responseCitationDate"] == "March 2024",
            "Supply printed date variants must remain separate")
    scope_spec = {
        "recycling-referral": ([791], True),
        "mineral-availability": (list(range(1670, 1682)), True),
        "mineral-security-recycling": ([1690, 1691], False),
    }
    require(set(ledger["responseScopes"]) == set(scope_spec), "Supply response scope missing")
    for key, (pages, complete) in scope_spec.items():
        scope = ledger["responseScopes"][key]
        require(scope["pdfPages"] == pages and scope["completeGeneralResponse"] is complete
                and scope["locator"], "Supply response scope mismatch")
    reviews = ledger["reviews"]
    require([r["requestId"] for r in reviews] == ids, "Supply review frame mismatch")
    rows = {r["requestId"]: r for r in inventory["requests"]}
    comparison_ids = ["recycling-and-replacement-distinction", "lithium-scenarios-and-uncertainty"]
    codings = [("reproduced_request_thematic_response", "recycling_disposal_cost_addition_not_verified"),
               ("reproduced_request_collective_response", "expanded_supply_scenarios_partial_method_alignment")]
    for i, r in enumerate(reviews):
        require(r["citedCommentId"] == COMMENT_ID and r["citedAttachmentOrder"] == 1
                and r["originalPdfPages"] == r["matchedOriginalPdfPages"] == rows[ids[i]]["pdfPages"]
                and r["excerptPdfPages"] == ([784, 1637] if i == 0 else [1637])
                and r["summaryPdfPages"] == ([1667] if i == 0 else [])
                and r["responseScopeIds"] == (list(scope_spec) if i == 0 else ["mineral-availability"])
                and r["excerptContentMatch"] == "selected_request_wording_and_original_page_citations_agree",
                "Supply original/excerpt/response linkage mismatch")
        require((r["responseLink"], r["disposition"]) == codings[i] and r["basis"]
                and r["analysisComparisonIds"] == [comparison_ids[i]]
                and r["independentReviewStatus"] == "pending" and r["individualCausalEffect"] == "not_identified",
                "Unsupported supply coding/promotion")
    comparisons = ledger["analysisComparisons"]
    require([c["comparisonId"] for c in comparisons] == comparison_ids,
            "Supply comparisons must not multiply requests or policy events")
    comparison_pages = [
        {"proposal": [44], "response": [791, 1690, 1691], "ria": [284, 572]},
        {"response": [1670, 1671, 1676], "final": [59, 60], "argonne": [14, 94, 103, 104]},
    ]
    assessments = ["specific_cost_addition_not_verified_in_reviewed_passages",
                   "partial_method_alignment_not_full_request_acceptance"]
    for i, c in enumerate(comparisons):
        require(c["requestIds"] == [ids[i]] and c["evidencePages"] == comparison_pages[i]
                and c["facts"] == SUPPLY_FACTS[i] and c["assessment"] == assessments[i] and c["basis"]
                and c["distinctPolicyChanges"] == "not_counted" and c["individualAttribution"] == "not_identified",
                "Unsupported supply analysis comparison")
    caution_spec = [
        ("replacement-is-not-recycling", ids[:1], "different_cost_components_preserved", "high",
         {"publisher": [7], "ria": [284, 572]}),
        ("scenarios-are-not-confidence-levels", ids[1:], "sources_units_and_uncertainty_preserved", "high",
         {"final": [59, 60], "argonne": [14, 94, 103, 104]}),
        ("source-reference-discrepancies", ids, "printed_source_references_preserved", "medium",
         {"response": [1671], "argonne": [3], "ria": [284, 572]}),
    ]
    require(len(ledger["sourceCautions"]) == len(caution_spec), "Missing supply source caution")
    for c, expected in zip(ledger["sourceCautions"], caution_spec):
        require(tuple(c[k] for k in ("cautionId", "requestIds", "status", "severity", "evidencePages")) == expected
                and c["finding"] and c["handling"], "Supply source caution changed")
    boundary = ledger["boundary"]
    require(all(boundary.get(k) == v for k, v in {
        "officialAttachmentByteMatch": "not_verified", "independentReviewStatus": "pending",
        "docketRateEligible": False, "overallLetterResponseCodingComplete": False,
        "currentLegalStatusAssessed": False, "causalEffect": "not_identified", "simulatorRecalibrated": False,
        "remainingEntriesStatus": "not_yet_adjudicated_not_nonresponse"}.items())
        and boundary["comparisonBoundary"] and boundary["unreviewedAnalysis"], "Unsupported supply claim boundary")
    return {"supplyEntriesReviewed": len(reviews),
            "supplyResponseLinks": dict(Counter(r["responseLink"] for r in reviews)),
            "supplyAnalysisComparisons": len(comparisons), "supplySourceCautions": len(caution_spec)}




INPUTS_PAGES = {
    "response": [
        {"pdfPage": 538, "printedPage": 520},
        {"pdfPage": 539, "printedPage": 521},
        {"pdfPage": 735, "printedPage": 717},
        {"pdfPage": 875, "printedPage": 857},
        {"pdfPage": 907, "printedPage": 889},
        {"pdfPage": 908, "printedPage": 890},
        {"pdfPage": 909, "printedPage": 891},
        {"pdfPage": 910, "printedPage": 892},
        {"pdfPage": 911, "printedPage": 893},
        {"pdfPage": 912, "printedPage": 894},
        {"pdfPage": 913, "printedPage": 895},
        {"pdfPage": 1045, "printedPage": 1027},
        {"pdfPage": 1176, "printedPage": 1158},
        {"pdfPage": 1177, "printedPage": 1159},
        {"pdfPage": 1283, "printedPage": 1265},
        {"pdfPage": 1296, "printedPage": 1278},
        {"pdfPage": 1297, "printedPage": 1279},
        {"pdfPage": 1298, "printedPage": 1280},
        {"pdfPage": 1299, "printedPage": 1281},
    ],
    "proposal": [{"pdfPage": 205, "printedPage": 26130}],
    "final": [{"pdfPage": 342, "printedPage": 29781}, {"pdfPage": 343, "printedPage": 29782}],
}
INPUTS_SCOPES = {
    "grid-demand-response-a": {"pdfPages": [1176, 1177], "completeGeneralResponse": True},
    "charging-infrastructure": {"pdfPages": [907, 908, 909, 910, 911, 912, 913], "completeGeneralResponse": True},
    "sales-distribution": {"pdfPages": [538, 539], "completeGeneralResponse": True},
    "adoption-source-distinction": {"pdfPages": [735], "completeGeneralResponse": False},
    "other-technologies": {"pdfPages": [1297, 1298, 1299], "completeGeneralResponse": True},
}
INPUTS_REVIEW_SPEC = [
    {
        "requestId": "mema-1570-r15",
        "citedCommentId": "EPA-HQ-OAR-2022-0985-1570",
        "citedAttachmentOrder": 1,
        "originalPdfPages": [9, 28],
        "matchedOriginalPdfPages": [9],
        "excerptPdfPages": [1045],
        "summaryPdfPages": [],
        "responseScopeIds": ["grid-demand-response-a"],
        "excerptContentMatch": "selected_request_wording_and_original_page_citations_agree",
        "responseLink": "reproduced_request_thematic_response",
        "disposition": "requested_study_considered_full_fleet_scope_distinguished",
        "analysisComparisonIds": ["atri-study-consideration"],
        "independentReviewStatus": "pending",
        "individualCausalEffect": "not_identified",
    },
    {
        "requestId": "mema-1570-r17",
        "citedCommentId": "EPA-HQ-OAR-2022-0985-1570",
        "citedAttachmentOrder": 1,
        "originalPdfPages": [10],
        "matchedOriginalPdfPages": [10],
        "excerptPdfPages": [875],
        "summaryPdfPages": [],
        "responseScopeIds": ["charging-infrastructure", "sales-distribution", "adoption-source-distinction"],
        "excerptContentMatch": "selected_request_wording_and_original_page_citations_agree",
        "responseLink": "reproduced_request_no_separate_disposition_in_reviewed_responses",
        "disposition": "act_bus_report_acquisition_not_verified",
        "analysisComparisonIds": ["bus-forecast-vs-other-model-updates"],
        "independentReviewStatus": "pending",
        "individualCausalEffect": "not_identified",
    },
    {
        "requestId": "mema-1570-r24",
        "citedCommentId": "EPA-HQ-OAR-2022-0985-1570",
        "citedAttachmentOrder": 1,
        "originalPdfPages": [13],
        "matchedOriginalPdfPages": [13],
        "excerptPdfPages": [1283],
        "summaryPdfPages": [1296],
        "responseScopeIds": ["other-technologies"],
        "excerptContentMatch": "selected_request_wording_and_original_page_citations_agree",
        "responseLink": "explicit_named_response",
        "disposition": "existing_off_cycle_pathway_not_default_input_refresh",
        "analysisComparisonIds": ["lightweighting-tables-and-approval-route"],
        "independentReviewStatus": "pending",
        "individualCausalEffect": "not_identified",
    },
    {
        "requestId": "mema-1570-r25",
        "citedCommentId": "EPA-HQ-OAR-2022-0985-1570",
        "citedAttachmentOrder": 1,
        "originalPdfPages": [13],
        "matchedOriginalPdfPages": [13],
        "excerptPdfPages": [1283],
        "summaryPdfPages": [1296],
        "responseScopeIds": ["other-technologies"],
        "excerptContentMatch": "selected_request_wording_and_original_page_citations_agree",
        "responseLink": "named_summary_collective_response",
        "disposition": "published_weight_input_values_retained_from_proposal",
        "analysisComparisonIds": ["lightweighting-tables-and-approval-route"],
        "independentReviewStatus": "pending",
        "individualCausalEffect": "not_identified",
    },
]
INPUTS_COMPARISON_SPEC = [
    {
        "comparisonId": "atri-study-consideration",
        "requestIds": ["mema-1570-r15"],
        "evidencePages": {"publisher": [9, 28], "response": [1045, 1176, 1177]},
        "assessment": "study_considered_not_full_fleet_estimates_adopted",
        "facts": {
            "requestedStudyCitedInAgencyResponse": True,
            "fullFleetScenarioDistinguished": True,
            "ruleImpactEstimateReplacedByAtriFullFleetNumbers": False,
            "fullRiaIncorporationVerified": False,
            "underlyingAtriStudyIndependentlyReviewed": False,
        },
        "distinctPolicyChanges": "not_counted",
        "individualAttribution": "not_identified",
    },
    {
        "comparisonId": "bus-forecast-vs-other-model-updates",
        "requestIds": ["mema-1570-r17"],
        "evidencePages": {"publisher": [10], "response": [538, 539, 735, 875, 907, 908, 909, 910, 911, 912, 913]},
        "assessment": "related_updates_do_not_verify_requested_report_acquisition",
        "facts": {
            "requestedProduct": "ACT Research Class 5-7 bus-market segmentation forecast",
            "actBusReportAcquisitionVerified": False,
            "actBusReportAcquisitionRejected": False,
            "salesDistributionSummaryNames": ["AVE", "MFN"],
            "salesDistributionSummaryNamesMema": False,
            "proposalSalesSource": "MOVES 3.Ra MY2019 weighted by 2019 production reports",
            "finalSalesSource": "MOVES 4.0 MY2021",
            "chassisCertifiedClass2b3Removed": True,
            "agencyReportedClass2b5SharePercent": {"proposal": 55, "final": 33},
            "agencyReportedClass8SharePercent": {"proposal": 28, "final": 42},
            "adoptionBinSourceChangedFromActResearchToNrelTempo": True,
            "busForecastAndAdoptionModelSameProduct": False,
            "underlyingModelReplicated": False,
        },
        "distinctPolicyChanges": "not_counted",
        "individualAttribution": "not_identified",
    },
    {
        "comparisonId": "lightweighting-tables-and-approval-route",
        "requestIds": ["mema-1570-r24", "mema-1570-r25"],
        "evidencePages": {
            "publisher": [13],
            "response": [1283, 1296, 1297, 1298, 1299],
            "proposal": [205],
            "final": [342, 343],
        },
        "assessment": "published_input_values_retained_existing_route_referred",
        "facts": {
            "namedResponseRefersExistingApprovalRoute": True,
            "agencyCitedProvision": "40 CFR 1037.520(e)(5)",
            "agencyReferredOffCycleProvision": "40 CFR 1037.610",
            "wheelLaterPhaseValuesChanged": 0,
            "nonwheelNumericRowsChanged": 0,
            "supplierConsultationVerified": False,
            "defaultInputRefreshVerified": False,
            "creditsAwardedVerified": False,
            "gemInputFilesExecuted": False,
            "historical2016TextCompared": False,
            "currentLegalStatusAssessed": False,
        },
        "distinctPolicyChanges": "not_counted",
        "individualAttribution": "not_identified",
    },
]
INPUTS_TABLES = {
    "comparisonId": "lightweighting-tables-and-approval-route",
    "wheel": {
        "tableNumber": 6,
        "units": "pounds_per_wheel",
        "proposalPhaseLabel": "Phase 2 and Phase 3",
        "finalPhaseLabel": "Phase 2 and later",
        "rows": [
            {"tireType": "wide_base_single", "material": "steel", "proposal": 84, "final": 84},
            {"tireType": "wide_base_single", "material": "aluminum", "proposal": 147, "final": 147},
            {
                "tireType": "wide_base_single",
                "material": "lightweight_aluminum_alloy",
                "proposal": 147,
                "final": 147,
            },
            {"tireType": "steer_or_dual_wide", "material": "high_strength_steel", "proposal": 8, "final": 8},
            {"tireType": "steer_or_dual_wide", "material": "aluminum", "proposal": 25, "final": 25},
            {
                "tireType": "steer_or_dual_wide",
                "material": "lightweight_aluminum_alloy",
                "proposal": 25,
                "final": 25,
            },
        ],
        "footnote": "The wide-base input includes reduced tire weight relative to dual-wide tires.",
    },
    "nonwheel": {
        "tableNumber": 8,
        "units": "pounds_per_vehicle_unless_otherwise_noted",
        "proposalPhaseLabel": "Phase 2 and Phase 3",
        "finalPhaseLabel": "Phase 2 and later",
        "rows": [
            {
                "component": "axle_hubs_non_drive",
                "material": "aluminum",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [40, 40],
                "final": [40, 40],
            },
            {
                "component": "axle_hubs_non_drive",
                "material": "high_strength_steel",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [5, 5],
                "final": [5, 5],
            },
            {
                "component": "axle_non_drive",
                "material": "aluminum",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [60, 60],
                "final": [60, 60],
            },
            {
                "component": "axle_non_drive",
                "material": "high_strength_steel",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [15, 15],
                "final": [15, 15],
            },
            {
                "component": "brake_drums_non_drive",
                "material": "aluminum",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [60, 60],
                "final": [60, 60],
            },
            {
                "component": "brake_drums_non_drive",
                "material": "high_strength_steel",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [42, 42],
                "final": [42, 42],
            },
            {
                "component": "axle_hubs_drive",
                "material": "aluminum",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [40, 80],
                "final": [40, 80],
            },
            {
                "component": "axle_hubs_drive",
                "material": "high_strength_steel",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [10, 20],
                "final": [10, 20],
            },
            {
                "component": "brake_drums_drive",
                "material": "aluminum",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [70, 140],
                "final": [70, 140],
            },
            {
                "component": "brake_drums_drive",
                "material": "high_strength_steel",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [37, 74],
                "final": [37, 74],
            },
            {
                "component": "suspension_brackets_hangers",
                "material": "aluminum",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [67, 100],
                "final": [67, 100],
            },
            {
                "component": "suspension_brackets_hangers",
                "material": "high_strength_steel",
                "columnGroups": ["light_and_medium", "heavy"],
                "proposal": [20, 30],
                "final": [20, 30],
            },
            {
                "component": "crossmember_cab",
                "material": "aluminum",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [10, 15, 15],
                "final": [10, 15, 15],
            },
            {
                "component": "crossmember_cab",
                "material": "high_strength_steel",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [2, 5, 5],
                "final": [2, 5, 5],
            },
            {
                "component": "crossmember_non_suspension",
                "material": "aluminum",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [15, 15, 15],
                "final": [15, 15, 15],
            },
            {
                "component": "crossmember_non_suspension",
                "material": "high_strength_steel",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [5, 5, 5],
                "final": [5, 5, 5],
            },
            {
                "component": "crossmember_suspension",
                "material": "aluminum",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [15, 25, 25],
                "final": [15, 25, 25],
            },
            {
                "component": "crossmember_suspension",
                "material": "high_strength_steel",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [6, 6, 6],
                "final": [6, 6, 6],
            },
            {
                "component": "driveshaft",
                "material": "aluminum",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [12, 40, 50],
                "final": [12, 40, 50],
            },
            {
                "component": "driveshaft",
                "material": "high_strength_steel",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [5, 10, 12],
                "final": [5, 10, 12],
            },
            {
                "component": "frame_rails",
                "material": "aluminum",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [120, 300, 440],
                "final": [120, 300, 440],
            },
            {
                "component": "frame_rails",
                "material": "high_strength_steel",
                "columnGroups": ["light", "medium", "heavy"],
                "proposal": [40, 40, 87],
                "final": [40, 40, 87],
            },
        ],
        "mergedCellMeaning": "The first twelve rows span the Light and Medium HDV columns; their shared value is not a missing or zero Medium cell.",
        "mediumAxleOverride": "For Medium HDV with 6x4 or 6x2 axle configurations, use Heavy HDV values.",
    },
    "scope": "All six later-phase wheel rows and all 22 nonwheel component/material rows visually compared, including both table footnotes. Phase 1 wheel values are not the Phase 3 comparison. Identical published values do not independently verify GEM implementation or the 2016 baseline.",
}
INPUTS_CAUTION_SPEC = [
    {
        "cautionId": "full-fleet-is-not-rule-impact",
        "requestIds": ["mema-1570-r15"],
        "evidencePages": {"publisher": [9, 28], "response": [1176, 1177]},
        "severity": "high",
        "status": "study_engagement_and_numeric_adoption_separated",
    },
    {
        "cautionId": "act-products-and-commenter-attribution",
        "requestIds": ["mema-1570-r17"],
        "evidencePages": {"publisher": [10], "response": [538, 539, 735, 875]},
        "severity": "high",
        "status": "requested_product_and_other_model_updates_separated",
    },
    {
        "cautionId": "approval-route-is-not-input-refresh",
        "requestIds": ["mema-1570-r24", "mema-1570-r25"],
        "evidencePages": {"publisher": [13], "response": [1296, 1298, 1299], "proposal": [205], "final": [342, 343]},
        "severity": "high",
        "status": "existing_route_retention_and_new_change_separated",
    },
    {
        "cautionId": "table-phase-and-merged-cell-scope",
        "requestIds": ["mema-1570-r24", "mema-1570-r25"],
        "evidencePages": {"proposal": [205], "final": [342, 343]},
        "severity": "medium",
        "status": "phase_labels_merged_cells_and_footnotes_preserved",
    },
]


def validate_inputs(inventory, ledger):
    """Check the frozen documentary reading, not independently authenticate it."""
    check_review(ledger, "comment-publisher-inputs-review-v1")
    require(ledger["inventoryFile"] == "comment-publisher-inventory.json"
            and ledger["inventoryFrameSha256"] == inventory["requestFrameSha256"]
            and ledger["publisherSha256"] == inventory["publisher"]["sha256"] == PUBLISHER_SHA,
            "Inputs review has stale inventory/source binding")
    ids = [r["requestId"] for r in INPUTS_REVIEW_SPEC]
    selection = ledger["selection"]
    require(selection["requestIds"] == ids
            and selection["mode"] == "targeted_study_and_lightweighting_followup"
            and selection["priorOutcomeExposure"] is True and selection["blinded"] is False
            and selection["scope"], "Inputs selection/frame disclosure mismatch")
    visual = ledger["publisherReview"]
    require(visual["pdfPages"] == [9, 10, 13, 28]
            and visual["method"] == "rendered_pages_with_text_navigation" and visual["scope"],
            "Inputs original visual scope mismatch")
    require(set(ledger["documents"]) == set(INPUTS_PAGES), "Missing inputs source document")
    for name, pages in INPUTS_PAGES.items():
        doc = ledger["documents"][name]
        require(doc["sha256"] == SOURCE_DOCS[name][0] and doc["url"] == SOURCE_URLS[name]
                and doc["reviewedPages"] == pages and doc["scope"],
                "Inputs source identity/page mapping mismatch")
    require(set(ledger["responseScopes"]) == set(INPUTS_SCOPES), "Inputs response scope missing")
    for name, expected in INPUTS_SCOPES.items():
        scope = ledger["responseScopes"][name]
        require(scope["pdfPages"] == expected["pdfPages"]
                and scope["completeGeneralResponse"] is expected["completeGeneralResponse"]
                and scope["locator"], "Inputs response scope mismatch")
    reviews = ledger["reviews"]
    require([r["requestId"] for r in reviews] == ids, "Inputs review frame mismatch")
    inventory_rows = {r["requestId"]: r for r in inventory["requests"]}
    for row, expected in zip(reviews, INPUTS_REVIEW_SPEC):
        require(row["originalPdfPages"] == inventory_rows[row["requestId"]]["pdfPages"]
                and all(row.get(k) == v for k, v in expected.items()) and row["basis"],
                "Unsupported inputs coding/linkage/promotion")
    comparisons = ledger["analysisComparisons"]
    require(len(comparisons) == len(INPUTS_COMPARISON_SPEC),
            "Inputs comparisons must not multiply requests or policy events")
    for comparison, expected in zip(comparisons, INPUTS_COMPARISON_SPEC):
        require(fingerprint({k: comparison.get(k) for k in expected}) == fingerprint(expected)
                and comparison["basis"], "Unsupported inputs analysis comparison")
    require(ledger["publishedTables"] == INPUTS_TABLES,
            "Inputs table values, phase, units or merged-cell scope changed")
    for table_name in ("wheel", "nonwheel"):
        table = ledger["publishedTables"][table_name]
        require(all(row["proposal"] == row["final"] for row in table["rows"]),
                "Inputs table comparison does not reproduce retention")
    cautions = ledger["sourceCautions"]
    require(len(cautions) == len(INPUTS_CAUTION_SPEC), "Missing inputs source caution")
    for caution, expected in zip(cautions, INPUTS_CAUTION_SPEC):
        require(all(caution.get(k) == v for k, v in expected.items())
                and caution["finding"] and caution["handling"], "Inputs source caution changed")
    boundary = ledger["boundary"]
    expected_boundary = {
        "officialAttachmentByteMatch": "not_verified", "independentReviewStatus": "pending",
        "docketRateEligible": False, "overallLetterResponseCodingComplete": False,
        "currentLegalStatusAssessed": False, "causalEffect": "not_identified",
        "simulatorRecalibrated": False, "remainingEntriesStatus": "not_yet_adjudicated_not_nonresponse",
    }
    require(fingerprint({k: boundary.get(k) for k in expected_boundary}) == fingerprint(expected_boundary)
            and boundary["comparisonBoundary"] and boundary["unreviewedAnalysis"],
            "Unsupported inputs claim boundary")
    return {"inputsEntriesReviewed": len(reviews),
            "inputsResponseLinks": dict(Counter(r["responseLink"] for r in reviews)),
            "inputsAnalysisComparisons": len(comparisons), "inputsSourceCautions": len(cautions)}


def validate_all(inventory, warranty, technology, infrastructure=None, timing=None, supply=None, inputs=None):
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
    if supply is not None:
        result.update(validate_supply(inventory, supply))
        ledgers.append(supply)
    if inputs is not None:
        result.update(validate_inputs(inventory, inputs))
        ledgers.append(inputs)
    ids = [r["requestId"] for ledger in ledgers for r in ledger["reviews"]]
    require(len(ids) == len(set(ids)), "Overlapping publisher follow-ups inflate review coverage")
    result["boundedResponseReviews"] = len(ids)
    result["otherEntriesAwaitingAdjudication"] = result["inventoryEntries"] - len(ids)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("publisher-pdf", "metadata-json", "response-pdf", "proposal-pdf", "final-pdf",
                 "argonne-pdf", "ria-pdf"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    inventory = json.loads((DATA / "comment-publisher-inventory.json").read_text())
    followup = json.loads((DATA / "comment-publisher-warranty-review.json").read_text())
    technology = json.loads((DATA / "comment-publisher-technology-review.json").read_text())
    infrastructure = json.loads((DATA / "comment-publisher-infrastructure-review.json").read_text())
    timing = json.loads((DATA / "comment-publisher-timing-review.json").read_text())
    supply = json.loads((DATA / "comment-publisher-supply-review.json").read_text())
    inputs = json.loads((DATA / "comment-publisher-inputs-review.json").read_text())
    result = validate_all(inventory, followup, technology, infrastructure, timing, supply, inputs)
    checked = []
    for name, digest in {"publisher_pdf": PUBLISHER_SHA,
            "metadata_json": inventory["docketMetadata"]["rawSha256"],
            **{k + "_pdf": v[0] for k, v in SOURCE_DOCS.items()},
            **{k + "_pdf": v[0] for k, v in SUPPLY_EXTRA_DOCS.items()}}.items():
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
