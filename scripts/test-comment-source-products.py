#!/usr/bin/env python3
"""Offline regressions for lossless comment normalization and cohort refresh."""

import csv
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "comment_products", Path(__file__).with_name("build-first-wave-comment-products.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUDIT_SPEC = importlib.util.spec_from_file_location(
    "comment_position_audit", Path(__file__).with_name("audit-empirical-expansion.py")
)
AUDIT = importlib.util.module_from_spec(AUDIT_SPEC)
AUDIT_SPEC.loader.exec_module(AUDIT)


PUBLISHER_SPEC = importlib.util.spec_from_file_location(
    "comment_publisher", Path(__file__).with_name("review-comment-publisher.py")
)
PUBLISHER = importlib.util.module_from_spec(PUBLISHER_SPEC)
PUBLISHER_SPEC.loader.exec_module(PUBLISHER)


class CommentPublisherTests(unittest.TestCase):
    def setUp(self):
        self.inventory = json.loads((AUDIT.DATA / "comment-publisher-inventory.json").read_text())
        self.followup = json.loads((AUDIT.DATA / "comment-publisher-warranty-review.json").read_text())

    def check(self, refresh=True):
        if refresh:
            for ledger in (self.inventory, self.followup):
                ledger["reviewFingerprint"] = PUBLISHER.fingerprint({
                    k: v for k, v in ledger.items() if k != "reviewFingerprint"})
        return PUBLISHER.validate(self.inventory, self.followup)

    def test_single_letter_is_not_forty_eight_independent_comments(self):
        result = self.check(False)
        self.assertEqual(result["publisherLetters"], 1)
        self.assertEqual(result["visuallyReviewedPages"], 28)
        self.assertEqual(result["inventoryEntries"], 48)
        self.assertEqual(result["entryKinds"], {
            "requested_action": 44, "conditional_request": 1, "retention_position": 3})
        self.assertEqual(result["warrantyEntriesReviewed"], 4)
        self.assertEqual(result["otherEntriesAwaitingAdjudication"], 44)
        self.assertEqual(result["verifiedDocketByteMatches"], 0)
        self.assertEqual(result["docketRateEligibleEntries"], 0)
        self.assertEqual(result["causalEffect"], "not_identified")

    def test_changed_review_requires_new_fingerprint(self):
        self.inventory["requests"][0]["label"] = "altered interpretation"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check(False)

    def test_missing_and_duplicate_requests_fail_even_with_new_hash(self):
        original = deepcopy(self.inventory)
        for entries in (original["requests"][:-1], original["requests"] + original["requests"][:1]):
            self.inventory = deepcopy(original)
            self.inventory["requests"] = entries
            self.inventory["requestFrameSha256"] = PUBLISHER.fingerprint(entries)
            with self.subTest(count=len(entries)), self.assertRaisesRegex(ValueError, "off-frame"):
                self.check()

    def test_page_coverage_and_request_join_cannot_be_inferred_from_ocr(self):
        original = deepcopy(self.inventory)
        for mutation in ("missing_page", "missing_link", "ocr_only"):
            self.inventory = deepcopy(original)
            if mutation == "missing_page":
                self.inventory["pageCoverage"].pop(17)
            elif mutation == "missing_link":
                self.inventory["pageCoverage"][17]["requestIds"] = []
            else:
                self.inventory["publisher"]["reviewMethod"] = "OCR_only"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check()

    def test_metadata_correspondence_does_not_clear_official_bytes(self):
        self.inventory["authentication"]["byteVersionMatch"] = "verified"
        with self.assertRaisesRegex(ValueError, "authentication"):
            self.check()

    def test_docket_size_title_and_attachment_order_are_checked(self):
        original = deepcopy(self.inventory)
        for key, value in (("docOrder", 2), ("docAbstract", "different filename"), ("fileFormats", [])):
            self.inventory = deepcopy(original)
            metadata = self.inventory["docketMetadata"]
            metadata["projection"]["attachment"][key] = value
            metadata["projectionSha256"] = PUBLISHER.fingerprint(metadata["projection"])
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check()

    def test_content_page_count_is_not_attachment_length(self):
        metadata = self.inventory["docketMetadata"]
        metadata["projection"]["pageCount"] = 28
        metadata["projectionSha256"] = PUBLISHER.fingerprint(metadata["projection"])
        with self.assertRaisesRegex(ValueError, "content page count"):
            self.check()

    def test_receipt_and_posting_dates_are_separate(self):
        metadata = self.inventory["docketMetadata"]
        metadata["projection"]["receiveDate"] = metadata["projection"]["postedDate"]
        metadata["projectionSha256"] = PUBLISHER.fingerprint(metadata["projection"])
        with self.assertRaisesRegex(ValueError, "chronology"):
            self.check()

    def test_retention_condition_and_indirectness_remain_explicit(self):
        original = deepcopy(self.inventory)
        for index, key in ((24, "kind"), (8, "kind"), (12, "interpretiveFlag")):
            self.inventory = deepcopy(original)
            self.inventory["requests"][index][key] = "requested_action" if key == "kind" else "none"
            self.inventory["requestFrameSha256"] = PUBLISHER.fingerprint(self.inventory["requests"])
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "classification"):
                self.check()

    def test_followup_cannot_silently_switch_inventory(self):
        self.followup["inventoryFrameSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "binding"):
            self.check()

    def test_warranty_frame_cannot_drop_or_duplicate_a_request(self):
        original = deepcopy(self.followup)
        for entries in (original["reviews"][:3], original["reviews"] + original["reviews"][:1]):
            self.followup = deepcopy(original)
            self.followup["reviews"] = entries
            with self.subTest(count=len(entries)), self.assertRaisesRegex(ValueError, "frame"):
                self.check()

    def test_cross_comment_or_original_page_swap_fails(self):
        original = deepcopy(self.followup)
        for key, value in (("citedCommentId", "EPA-HQ-OAR-2022-0985-1598"),
                           ("citedAttachmentOrder", 2), ("originalPdfPages", [15])):
            self.followup = deepcopy(original)
            self.followup["reviews"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "link mismatch"):
                self.check()

    def test_pdf_pages_not_footer_form_numbers_and_source_is_bound(self):
        original = deepcopy(self.followup)
        for key, value in (("sha256", "0" * 64), ("url", "https://example.org/unreviewed.pdf"),
                           ("reviewedPages", [{"pdfPage": 175, "printedPage": 29613}])):
            self.followup = deepcopy(original)
            self.followup["documents"]["final"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "document identity"):
                self.check()

    def test_shared_comparison_is_not_two_independent_policy_events(self):
        self.followup["ruleComparisons"] *= 2
        with self.assertRaisesRegex(ValueError, "multiply policy events"):
            self.check()

    def test_collective_reply_and_unresolved_process_are_not_acceptance(self):
        original = deepcopy(self.followup)
        for index in (0, 1, 2, 3):
            self.followup = deepcopy(original)
            self.followup["reviews"][index]["disposition"] = "fully_accepted"
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "disposition"):
                self.check()

    def test_unadjudicated_entries_cannot_become_nonresponses_or_causal_clearance(self):
        original = deepcopy(self.followup)
        for key, value in (("remainingEntriesStatus", "no_response"), ("docketRateEligible", True),
                           ("independentReviewStatus", "complete"), ("causalEffect", "identified"),
                           ("overallLetterResponseCodingComplete", True), ("currentLegalStatusAssessed", True)):
            self.followup = deepcopy(original)
            self.followup["boundary"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "boundary"):
                self.check()


class CommentTechnologyTests(unittest.TestCase):
    def setUp(self):
        self.inventory = json.loads((AUDIT.DATA / "comment-publisher-inventory.json").read_text())
        self.warranty = json.loads((AUDIT.DATA / "comment-publisher-warranty-review.json").read_text())
        self.technology = json.loads((AUDIT.DATA / "comment-publisher-technology-review.json").read_text())

    def check(self, refresh=True):
        if refresh:
            self.technology["reviewFingerprint"] = PUBLISHER.fingerprint({
                k: v for k, v in self.technology.items() if k != "reviewFingerprint"})
        return PUBLISHER.validate_all(self.inventory, self.warranty, self.technology)

    def test_nine_followups_extend_coverage_not_the_letter_or_comment_population(self):
        before = deepcopy((self.inventory, self.warranty, self.technology))
        result = self.check(False)
        self.assertEqual((self.inventory, self.warranty, self.technology), before)
        for key, value in {"publisherLetters": 1, "inventoryEntries": 48, "warrantyEntriesReviewed": 4,
                           "technologyEntriesReviewed": 9, "boundedResponseReviews": 13,
                           "otherEntriesAwaitingAdjudication": 35, "technologyScopedRuleComparisons": 2,
                           "technologySourceCautions": 3, "independentlyReviewedEntries": 0,
                           "verifiedDocketByteMatches": 0, "docketRateEligibleEntries": 0}.items():
            self.assertEqual(result[key], value)
        self.assertEqual(PUBLISHER.validate(self.inventory, self.warranty)["otherEntriesAwaitingAdjudication"], 44)

    def test_stale_fingerprint_and_inventory_binding_fail(self):
        self.technology["inventoryFrameSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check(False)
        with self.assertRaisesRegex(ValueError, "binding"):
            self.check()

    def test_missing_duplicate_or_warranty_request_cannot_expand_coverage(self):
        original = deepcopy(self.technology)
        for reviews in (original["reviews"][:-1], original["reviews"] * 2,
                        original["reviews"][:-1] + self.warranty["reviews"][:1]):
            self.technology = deepcopy(original)
            self.technology["reviews"] = reviews
            with self.subTest(count=len(reviews)), self.assertRaisesRegex(ValueError, "frame"):
                self.check()

    def test_targeted_selection_cannot_become_blinded(self):
        self.technology["selection"]["blinded"] = True
        with self.assertRaisesRegex(ValueError, "selection"):
            self.check()

    def test_document_identity_and_physical_page_mapping_are_required(self):
        original = deepcopy(self.technology)
        for key, value in (("url", "https://example.org/different.pdf"), ("sha256", "0" * 64),
                           ("reviewedPages", [{"pdfPage": 202, "printedPage": 26126}])):
            self.technology = deepcopy(original)
            self.technology["documents"]["proposal"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "identity/page"):
                self.check()

    def test_scope_completion_does_not_extend_to_unread_sections(self):
        self.technology["responseScopes"]["technology-neutrality"]["completeGeneralResponse"] = True
        with self.assertRaisesRegex(ValueError, "scope changed"):
            self.check()

    def test_cross_comment_original_page_and_response_link_swaps_fail(self):
        original = deepcopy(self.technology)
        for key, value in (("citedCommentId", "EPA-HQ-OAR-2022-0985-1598"),
                           ("citedAttachmentOrder", 2), ("originalPdfPages", [15]),
                           ("excerptPdfPages", [1411]), ("responseScopeIds", ["hydrogen"])):
            self.technology = deepcopy(original)
            self.technology["reviews"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "linkage"):
                self.check()

    def test_broad_analysis_program_mismatch_and_unknowns_are_not_full_acceptance(self):
        original = deepcopy(self.technology)
        for index in range(9):
            self.technology = deepcopy(original)
            self.technology["reviews"][index]["disposition"] = "fully_accepted"
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "coding/promotion"):
                self.check()

    def test_shared_comparisons_do_not_become_independent_events(self):
        self.technology["ruleComparisons"] *= 2
        with self.assertRaisesRegex(ValueError, "multiply policy events"):
            self.check()

    def test_generation_use_and_base_credit_boundaries(self):
        original = deepcopy(self.technology)
        for key, value in (("h2iceNewMultiplierFinalized", True), ("finalFcevLastGenerationModelYear", 2030),
                           ("finalMultiplierUseProhibitedFromModelYear", 2028),
                           ("baseCreditsShareMultiplierUseCutoff", True),
                           ("phase2DeficitResolutionException", False)):
            self.technology = deepcopy(original)
            self.technology["ruleComparisons"][0]["facts"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "comparison"):
                self.check()

    def test_neat_hydrogen_vehicle_and_engine_units_cannot_be_conflated(self):
        original = deepcopy(self.technology)
        for key, value in (("engineDefaultUnit", "g/ton-mile"), ("engineProgramSameAsVehicle", True),
                           ("allPollutantsZero", True), ("neatHydrogenOnly", False),
                           ("vehicleClauseUnchanged", False), ("engineDefaultOptional", False)):
            self.technology = deepcopy(original)
            self.technology["ruleComparisons"][1]["facts"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "conflation"):
                self.check()

    def test_source_discrepancies_are_retained_not_silently_repaired(self):
        self.technology["sourceCautions"].pop(0)
        with self.assertRaisesRegex(ValueError, "discrepancy"):
            self.check()

    def test_missing_review_does_not_clear_rates_causality_or_current_law(self):
        original = deepcopy(self.technology)
        for key, value in (("remainingEntriesStatus", "no_response"), ("independentReviewStatus", "complete"),
                           ("causalEffect", "identified"), ("docketRateEligible", True),
                           ("overallLetterResponseCodingComplete", True), ("simulatorRecalibrated", True),
                           ("currentLegalStatusAssessed", True)):
            self.technology = deepcopy(original)
            self.technology["boundary"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "boundary"):
                self.check()


class CommentInfrastructureTests(unittest.TestCase):
    def setUp(self):
        self.inventory = json.loads((AUDIT.DATA / "comment-publisher-inventory.json").read_text())
        self.warranty = json.loads((AUDIT.DATA / "comment-publisher-warranty-review.json").read_text())
        self.technology = json.loads((AUDIT.DATA / "comment-publisher-technology-review.json").read_text())
        self.infrastructure = json.loads((AUDIT.DATA / "comment-publisher-infrastructure-review.json").read_text())

    def check(self, refresh=True):
        if refresh:
            self.infrastructure["reviewFingerprint"] = PUBLISHER.fingerprint({
                k: v for k, v in self.infrastructure.items() if k != "reviewFingerprint"})
        return PUBLISHER.validate_all(self.inventory, self.warranty, self.technology, self.infrastructure)

    def test_seven_reviews_extend_coverage_without_changing_the_population_or_history(self):
        before = deepcopy((self.inventory, self.warranty, self.technology, self.infrastructure))
        result = self.check(False)
        self.assertEqual((self.inventory, self.warranty, self.technology, self.infrastructure), before)
        for key, value in {"publisherLetters": 1, "inventoryEntries": 48, "boundedResponseReviews": 20,
                           "infrastructureEntriesReviewed": 7, "otherEntriesAwaitingAdjudication": 28,
                           "infrastructurePreambleComparisons": 1, "infrastructureSourceCautions": 3,
                           "independentlyReviewedEntries": 0, "docketRateEligibleEntries": 0,
                           "verifiedDocketByteMatches": 0}.items():
            self.assertEqual(result[key], value)
        old = PUBLISHER.validate_all(self.inventory, self.warranty, self.technology)
        self.assertEqual(old["boundedResponseReviews"], 13)
        self.assertEqual(old["otherEntriesAwaitingAdjudication"], 35)

    def test_stale_fingerprint_and_binding_fail(self):
        self.infrastructure["inventoryFrameSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check(False)
        with self.assertRaisesRegex(ValueError, "binding"):
            self.check()

    def test_missing_duplicate_or_previously_reviewed_request_fails(self):
        original = deepcopy(self.infrastructure)
        for reviews in (original["reviews"][:-1], original["reviews"] * 2,
                        original["reviews"][:-1] + self.technology["reviews"][:1]):
            self.infrastructure = deepcopy(original)
            self.infrastructure["reviews"] = reviews
            with self.subTest(count=len(reviews)), self.assertRaisesRegex(ValueError, "frame"):
                self.check()

    def test_prior_outcome_exposure_and_rendered_originals_are_required(self):
        self.infrastructure["selection"]["blinded"] = True
        with self.assertRaisesRegex(ValueError, "selection"):
            self.check()
        self.infrastructure["selection"]["blinded"] = False
        self.infrastructure["publisherReview"]["method"] = "OCR_only"
        with self.assertRaisesRegex(ValueError, "visual scope"):
            self.check()

    def test_source_identity_and_page_mapping_fail_when_changed(self):
        original = deepcopy(self.infrastructure)
        for key, value in (("url", "https://example.org/different.pdf"), ("sha256", "0" * 64),
                           ("reviewedPages", [{"pdfPage": 42, "printedPage": 42}])):
            self.infrastructure = deepcopy(original)
            self.infrastructure["documents"]["final"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "identity/page"):
                self.check()

    def test_incomplete_general_response_cannot_pass(self):
        self.infrastructure["responseScopes"]["charging-other"]["pdfPages"] = [992]
        with self.assertRaisesRegex(ValueError, "scope changed"):
            self.check()

    def test_background_excerpt_cannot_replace_the_actual_public_purchase_request(self):
        self.infrastructure["reviews"][3]["excerptPdfPages"] = [987]
        with self.assertRaisesRegex(ValueError, "linkage"):
            self.check()

    def test_cross_comment_and_cross_scope_swaps_fail(self):
        original = deepcopy(self.infrastructure)
        for key, value in (("citedCommentId", "EPA-HQ-OAR-2022-0985-1555"),
                           ("citedAttachmentOrder", 2), ("matchedOriginalPdfPages", [26]),
                           ("responseScopeIds", ["implementation-coordination"])):
            self.infrastructure = deepcopy(original)
            self.infrastructure["reviews"][4][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "linkage"):
                self.check()

    def test_unresolved_specific_requests_cannot_become_full_acceptance_or_rejection(self):
        original = deepcopy(self.infrastructure)
        for index in range(7):
            for disposition in ("fully_accepted", "explicitly_rejected", "docket_wide_nonresponse"):
                self.infrastructure = deepcopy(original)
                self.infrastructure["reviews"][index]["disposition"] = disposition
                with self.subTest(index=index, code=disposition), self.assertRaisesRegex(ValueError, "coding/promotion"):
                    self.check()

    def test_preamble_commitment_is_not_implementation_causation_or_an_operative_clause(self):
        original = deepcopy(self.infrastructure)
        for key, value in (("comparisonType", "operative_clause_change"), ("individualAttribution", "identified"),
                           ("distinctPolicyChanges", 3)):
            self.infrastructure = deepcopy(original)
            self.infrastructure["ruleComparisons"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "preamble comparison"):
                self.check()

    def test_monitoring_baseline_calendar_qualifier_and_dashboard_limits_are_preserved(self):
        original = deepcopy(self.infrastructure)
        for key, value in (("proposalAlreadyDescribesMonitoring", False),
                           ("proposalAlreadySolicitsAdditionalInformationAndStakeholders", False),
                           ("finalDataCollectionStartCalendarYear", 2026), ("reportStartQualifier", "by"),
                           ("finalReportsEarliestCalendarYear", 2025), ("implementationVerified", True),
                           ("finalSelfAdjustingStandardsLinkage", True), ("allAssumptionsGuaranteed", True),
                           ("requestedDashboardAdoptedInReviewedPassages", True)):
            self.infrastructure = deepcopy(original)
            self.infrastructure["ruleComparisons"][0]["facts"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "preamble comparison"):
                self.check()

    def test_shared_monitoring_comparison_cannot_multiply_events(self):
        self.infrastructure["ruleComparisons"] *= 3
        with self.assertRaisesRegex(ValueError, "multiply policy events"):
            self.check()

    def test_attribution_scope_and_timeline_cautions_cannot_disappear(self):
        original = deepcopy(self.infrastructure)
        for index in range(3):
            self.infrastructure = deepcopy(original)
            self.infrastructure["sourceCautions"].pop(index)
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "source caution"):
                self.check()

    def test_unreviewed_entries_do_not_clear_rates_independence_or_current_status(self):
        original = deepcopy(self.infrastructure)
        for key, value in (("remainingEntriesStatus", "no_response"), ("independentReviewStatus", "complete"),
                           ("causalEffect", "identified"), ("docketRateEligible", True),
                           ("overallLetterResponseCodingComplete", True), ("simulatorRecalibrated", True),
                           ("currentLegalStatusAssessed", True), ("officialAttachmentByteMatch", "verified")):
            self.infrastructure = deepcopy(original)
            self.infrastructure["boundary"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "boundary"):
                self.check()


class CommentFollowupTests(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads((AUDIT.DATA / "comment-request-followups.json").read_text())
        self.baseline = json.loads((AUDIT.DATA / "comment-section-inventory-source.json").read_text())
        self.pilot = json.loads((AUDIT.DATA / "comment-response-document-source.json").read_text())

    def check(self, sources, refresh=True):
        if refresh:
            sources["reviewFingerprint"] = AUDIT.source_fingerprint(
                {k: v for k, v in sources.items() if k != "reviewFingerprint"})
        return AUDIT.comment_followup_diagnostics(sources, self.baseline, self.pilot)

    def test_followup_is_one_existing_request_not_four_new_observations(self):
        result = self.check(self.sources, refresh=False)
        self.assertEqual(result["followupReviews"], 1)
        self.assertEqual(result["baselineRequests"], 11)
        self.assertEqual(result["newIndependentRequests"], 0)
        self.assertEqual(result["crossSectionResponseLinks"], 1)
        self.assertEqual(result["requestFacets"], 4)
        self.assertEqual(result["disposition"], "partial_alignment_with_interim_flexibility")
        self.assertEqual(result["historicalFinalUseThroughModelYear"], 2032)
        self.assertTrue(result["proposalAlreadySolicitedOption"])
        self.assertEqual(result["causalEffect"], "not_identified")

    def test_baseline_change_or_followup_wording_requires_new_review(self):
        baseline = deepcopy(self.baseline)
        baseline["requests"][6]["disposition"] = "accepted"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            AUDIT.comment_followup_diagnostics(self.sources, baseline, self.pilot)
        sources = deepcopy(self.sources)
        sources["reviews"][0]["matchRationale"] = "different interpretation"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check(sources, refresh=False)

    def test_missing_or_duplicate_followup_fails(self):
        for rows in ([], self.sources["reviews"] * 2):
            sources = deepcopy(self.sources)
            sources["reviews"] = rows
            with self.subTest(count=len(rows)), self.assertRaisesRegex(ValueError, "frame"):
                self.check(sources)

    def test_cross_comment_attachment_and_request_swap_fail(self):
        for key, value in (("baselineRequestId", "s25-cummins-tractors"),
                           ("citedCommentId", "EPA-HQ-OAR-2022-0985-1598"),
                           ("attachmentOrder", 2), ("originalCitedPages", "167-168")):
            sources = deepcopy(self.sources)
            sources["reviews"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "identity"):
                self.check(sources)

    def test_rule_identity_and_visual_page_scope_are_bound(self):
        for kind in ("hash", "printed", "page", "facet"):
            sources = deepcopy(self.sources)
            if kind == "hash":
                sources["documents"]["final"]["pdfSha256"] = "0" * 64
            elif kind == "printed":
                sources["documents"]["final"]["reviewedPages"][0]["printedPage"] = 29775
            elif kind == "page":
                sources["reviews"][0]["responsePdfPages"] = [1432, 1433]
            else:
                sources["reviews"][0]["facets"][0]["evidencePdfPages"] = [338]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.check(sources)

    def test_cap_is_not_discount_and_interim_is_not_permanent(self):
        for facet in ("no_credit_discount", "program_life_duration"):
            sources = deepcopy(self.sources)
            next(f for f in sources["reviews"][0]["facets"] if f["facet"] == facet)["assessment"] = "fully_accepted"
            with self.subTest(facet=facet), self.assertRaisesRegex(ValueError, "facet"):
                self.check(sources)
        for key, value in (("historicalFinalUseThroughModelYear", 2035),
                           ("specifiedPre2027AdvancedTechnologyCreditsIncluded", False),
                           ("proposalWasAdoptedRule", True), ("proposalAlreadySolicitedOption", False)):
            sources = deepcopy(self.sources)
            sources["reviews"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "coding"):
                self.check(sources)

    def test_shared_response_cannot_be_promoted_to_individual_effect(self):
        for key, value in (("responseLink", "explicit_named_response"),
                           ("disposition", "fully_accepted"), ("addsIndependentRequest", True),
                           ("unchangedBaseline", False), ("originalAttachmentRead", True),
                           ("docketRateEligible", True), ("causalEffect", "identified"),
                           ("independentReviewStatus", "complete")):
            sources = deepcopy(self.sources)
            sources["reviews"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "coding"):
                self.check(sources)

    def test_facet_rows_must_not_be_dropped_or_counted_twice(self):
        for count in (3, 5):
            sources = deepcopy(self.sources)
            facets = sources["reviews"][0]["facets"]
            sources["reviews"][0]["facets"] = (facets[:3] if count == 3 else facets + facets[:1])
            with self.subTest(count=count), self.assertRaisesRegex(ValueError, "facet"):
                self.check(sources)


class CommentSectionTests(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads((AUDIT.DATA / "comment-section-inventory-source.json").read_text())
        self.pilot = json.loads((AUDIT.DATA / "comment-response-document-source.json").read_text())
        self.rows = AUDIT.read("comment-section-inventory.csv")

    def check(self, sources):
        return AUDIT.comment_section_diagnostics(AUDIT.comment_section_rows(sources), sources, self.pilot)

    def test_complete_section_is_not_a_docket_denominator(self):
        result = AUDIT.comment_section_diagnostics(self.rows, self.sources, self.pilot)
        self.assertEqual(result["organizationBlocks"], 7)
        self.assertEqual(result["requestRows"], 11)
        self.assertEqual(result["coveredSectionPdfPages"], 6)
        self.assertEqual(result["priorPilotOverlap"], 2)
        self.assertEqual(result["responseLinks"], {
            "explicit_named_response": 3, "section_resolution_only": 1,
            "no_request_specific_disposition": 3, "named_summary_collective_response": 4})
        self.assertEqual(result["conditionalFallbacks"], 1)
        self.assertEqual(result["docketRateEligibleRequests"], 0)
        self.assertEqual(result["independentlyReviewedRequests"], 0)
        self.assertEqual(result["causalEffect"], "not_identified")

    def test_missing_or_replaced_request_fails_even_with_new_projection(self):
        for kind in ("missing", "duplicate", "invented", "repeat_renamed"):
            sources = deepcopy(self.sources)
            if kind == "missing":
                sources["requests"].pop(2)
            elif kind == "invented":
                sources["requests"][2]["requestCode"] = "invented"
            else:
                sources["requests"].append(deepcopy(sources["requests"][2]))
                if kind == "repeat_renamed":
                    sources["requests"][-1]["requestId"] = "same-request-another-name"
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "requests"):
                self.check(sources)

    def test_organization_attachment_and_summary_frame_are_preserved(self):
        for kind in ("attachment", "identity", "omitted_summary"):
            sources = deepcopy(self.sources)
            if kind == "attachment":
                sources["organizationBlocks"][0]["attachmentOrder"] = 1
            elif kind == "identity":
                sources["organizationBlocks"][1]["citedCommentId"] = sources["organizationBlocks"][0]["citedCommentId"]
            else:
                sources["organizationBlocks"][1]["namedInSectionSummary"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.check(sources)

    def test_pages_and_pdf_identity_cannot_silently_change(self):
        for kind in ("hash", "section_gap", "printed", "request", "response"):
            sources = deepcopy(self.sources)
            if kind == "hash":
                sources["responseDocument"]["pdfSha256"] = "0" * 64
            elif kind == "section_gap":
                sources["responseDocument"]["reviewedSectionPdfPages"].remove(459)
            elif kind == "printed":
                sources["responseDocument"]["firstPrintedPage"] = 438
            elif kind == "request":
                sources["requests"][0]["requestPdfPages"] = [459]
            else:
                sources["requests"][0]["responsePdfPages"] = [463]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.check(sources)

    def test_changed_wording_invalidates_saved_review(self):
        for section, key in (("requests", "codingRationale"), ("organizationBlocks", "organization")):
            sources = deepcopy(self.sources)
            sources[section][0][key] = "different source interpretation"
            with self.subTest(section=section), self.assertRaisesRegex(ValueError, "fingerprint"):
                AUDIT.comment_section_diagnostics(self.rows, sources, self.pilot)

    def test_old_pilot_overlap_cannot_be_lost_or_reassigned(self):
        for kind in ("missing", "swapped"):
            sources = deepcopy(self.sources)
            sources["requests"][0]["priorPilotObservationId"] = (
                "" if kind == "missing" else "phase3-cummins-tractor-credit")
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.check(sources)

    def test_collective_response_does_not_create_independent_outcomes(self):
        sources = deepcopy(self.sources)
        sources["requests"][5]["responseGroupId"] = "independent-dtna-success"
        with self.assertRaisesRegex(ValueError, "independent outcomes"):
            self.check(sources)
        sources = deepcopy(self.sources)
        sources["requests"][1]["responseLink"] = "explicit_named_response"
        sources["requests"][1]["disposition"] = "clarified_existing_scope"
        with self.assertRaisesRegex(ValueError, "named response"):
            self.check(sources)

    def test_fallback_requires_same_organization_parent_and_remains_conditional(self):
        for parent in ("", "s25-paccar-delay", "s25-dtna-subcategory", "not-in-frame"):
            sources = deepcopy(self.sources)
            sources["requests"][8]["conditionalOnRequestId"] = parent
            with self.subTest(parent=parent), self.assertRaisesRegex(ValueError, "[Cc]onditional"):
                self.check(sources)

    def test_unresolved_request_cannot_invent_a_response_match(self):
        sources = deepcopy(self.sources)
        sources["requests"][6]["responseGroupId"] = "s25-collective-vocational"
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            self.check(sources)

    def test_appendix_comment_count_and_theme_incidences_reconcile(self):
        appendix = self.sources["appendixSelectionContext"]
        self.assertEqual(sum(r["comments"] for r in appendix["issueCountDistribution"]), 1011)
        self.assertEqual(sum(r["issues"] * r["comments"] for r in appendix["issueCountDistribution"]), 2533)
        self.assertEqual(sum(appendix["themeCounts"].values()), 2533)
        self.assertFalse(appendix["nonresponseDenominatorEligible"])
        for field, value in (("agencyReportedCommentsNotReproduced", 2533),
                             ("reportedThemeIncidences", 1011),
                             ("nonresponseDenominatorEligible", True), ("individualListReviewed", True)):
            sources = deepcopy(self.sources)
            sources["appendixSelectionContext"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Appendix"):
                self.check(sources)

    def test_docket_rates_causal_claims_and_independent_review_stay_uncleared(self):
        for key in ("originalAttachmentRead", "docketVersionMatch", "docketRateEligible",
                    "causalEffect", "regulatoryTextChangeAttribution"):
            sources = deepcopy(self.sources)
            sources["codebook"][key] = "promoted"
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(sources)
        sources = deepcopy(self.sources)
        sources["independentReviewStatus"] = "complete"
        with self.assertRaises(ValueError):
            self.check(sources)


class CommentResponseTests(unittest.TestCase):
    def setUp(self):
        self.rows = AUDIT.read("comment-response-document-pilot.csv")
        self.sources = json.loads((AUDIT.DATA / "comment-response-document-source.json").read_text())

    def refresh_fingerprints(self, rows, sources):
        for record in sources["records"]:
            record["sourceFingerprint"] = AUDIT.source_fingerprint(
                {k: v for k, v in record.items() if k != "sourceFingerprint"})
        by_id = {r["commentId"]: r for r in sources["records"]}
        for row in rows:
            row["reviewSourceFingerprint"] = AUDIT.source_fingerprint(sources)
            row["metadataFingerprint"] = by_id[row["commentId"]]["sourceFingerprint"]

    def test_two_named_responses_are_not_a_rate_or_causal_effect(self):
        result = AUDIT.comment_response_diagnostics(self.rows, self.sources)
        self.assertEqual(result["requestRows"], 2)
        self.assertEqual(result["submissions"], 2)
        self.assertEqual(result["dockets"], 1)
        self.assertEqual(result["explicitNamedResponses"], 2)
        self.assertEqual(result["dispositions"], {"clarified_existing_scope": 1, "disagreed_with_error_claim": 1})
        for key in ("originalAttachmentsRead", "rateEligibleRequests", "independentlyReviewedRequests"):
            self.assertEqual(result[key], 0)
        self.assertEqual(result["causalEffect"], "not_identified")

    def test_receipt_posting_and_original_attachment_orders_are_distinct(self):
        self.assertEqual([r["attributes"]["receiveDate"][:10] for r in self.sources["records"]], ["2023-06-16"] * 2)
        self.assertEqual([r["attributes"]["postedDate"][:10] for r in self.sources["records"]], ["2023-06-22", "2023-06-29"])
        self.assertEqual([r["attachmentOrder"] for r in self.rows], ["1", "2"])
        self.assertEqual(len(self.sources["records"][1]["attachments"]), 2)

    def test_empty_or_duplicate_observations_and_metadata_fail(self):
        for kind in ("empty", "row", "metadata", "renamed_request"):
            rows, sources = deepcopy(self.rows), deepcopy(self.sources)
            if kind == "empty":
                rows = []
            elif kind == "metadata":
                sources["records"].append(deepcopy(sources["records"][0]))
            else:
                rows.append(deepcopy(rows[0]))
                if kind == "renamed_request":
                    rows[-1]["observationId"] = "same-request-new-name"
                    sources["reviews"].append(deepcopy(sources["reviews"][0]))
                    sources["reviews"][-1]["observationId"] = rows[-1]["observationId"]
            self.refresh_fingerprints(rows, sources)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                AUDIT.comment_response_diagnostics(rows, sources)

    def test_changed_metadata_invalidates_review(self):
        for key in ("receiveDate", "postedDate", "title"):
            sources = deepcopy(self.sources)
            sources["records"][0]["attributes"][key] = "changed"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "fingerprint"):
                AUDIT.comment_response_diagnostics(self.rows, sources)

    def test_changed_pdf_hash_page_or_anchor_invalidates_review(self):
        for kind in ("rtc_hash", "page", "final_hash", "anchor", "selection"):
            sources = deepcopy(self.sources)
            if kind == "rtc_hash":
                sources["responseDocument"]["pdfSha256"] = "0" * 64
            elif kind == "page":
                sources["responseDocument"]["reviewedPages"][0]["printedPage"] = "3"
            elif kind == "final_hash":
                sources["ruleSources"]["final"]["pdfSha256"] = "1" * 64
            elif kind == "anchor":
                sources["reviews"][0]["responseAnchor"] = "different response"
            else:
                sources["selection"] = "different source population"
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "fingerprint"):
                AUDIT.comment_response_diagnostics(self.rows, sources)

    def test_cross_comment_join_fails_even_with_other_metadata_fingerprint(self):
        rows = deepcopy(self.rows)
        rows[0]["commentId"] = rows[1]["commentId"]
        rows[0]["metadataFingerprint"] = rows[1]["metadataFingerprint"]
        with self.assertRaisesRegex(ValueError, "identity"):
            AUDIT.comment_response_diagnostics(rows, self.sources)

    def test_allison_cover_letter_cannot_replace_cited_comment(self):
        rows, sources = deepcopy(self.rows), deepcopy(self.sources)
        rows[1]["attachmentOrder"] = "1"
        sources["reviews"][1]["attachmentOrder"] = 1
        self.refresh_fingerprints(rows, sources)
        with self.assertRaisesRegex(ValueError, "attachment identity/order"):
            AUDIT.comment_response_diagnostics(rows, sources)

    def test_attachment_url_order_and_comment_must_agree(self):
        rows, sources = deepcopy(self.rows), deepcopy(self.sources)
        sources["records"][1]["attachments"][1]["attributes"]["fileFormats"][0]["fileUrl"] = (
            "https://downloads.regulations.gov/EPA-HQ-OAR-2022-0985-1598/attachment_1.pdf")
        self.refresh_fingerprints(rows, sources)
        with self.assertRaisesRegex(ValueError, "URL/order/comment"):
            AUDIT.comment_response_diagnostics(rows, sources)

    def test_missing_dates_are_not_zeros_and_bad_chronology_fails(self):
        for value in (None, "", "2022-01-01T04:00:00Z", "2024-05-01T04:00:00Z"):
            rows, sources = deepcopy(self.rows), deepcopy(self.sources)
            sources["records"][0]["attributes"]["receiveDate"] = value
            self.refresh_fingerprints(rows, sources)
            with self.subTest(value=value), self.assertRaises(ValueError):
                AUDIT.comment_response_diagnostics(rows, sources)

    def test_rejects_unreviewed_pages_and_wrong_printed_page(self):
        for key, value in (("requestPdfPage", 0), ("requestPdfPage", 459), ("responsePrintedPage", "443")):
            rows, sources = deepcopy(self.rows), deepcopy(self.sources)
            sources["reviews"][0][key] = value
            rows[0][key] = str(value)
            self.refresh_fingerprints(rows, sources)
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, "page"):
                AUDIT.comment_response_diagnostics(rows, sources)

    def test_response_cannot_be_promoted_to_causal_uptake_or_independent_review(self):
        for key in ("unit", "requestRepresentation", "responseLink", "originalAttachmentRead",
                    "docketVersionMatch", "uptakeRateEligible", "causalEffect",
                    "regulatoryTextChangeAttribution", "independentReviewStatus"):
            rows = deepcopy(self.rows)
            rows[0][key] = "true"
            with self.subTest(key=key), self.assertRaises(ValueError):
                AUDIT.comment_response_diagnostics(rows, self.sources)

    def test_error_claim_rejection_cannot_be_recoded_as_acceptance(self):
        rows, sources = deepcopy(self.rows), deepcopy(self.sources)
        rows[1]["disposition"] = "clarified_existing_scope"
        sources["reviews"][1]["disposition"] = "clarified_existing_scope"
        self.refresh_fingerprints(rows, sources)
        with self.assertRaisesRegex(ValueError, "coding"):
            AUDIT.comment_response_diagnostics(rows, sources)

    def test_collective_text_change_does_not_clear_single_comment_causality(self):
        rows, sources = deepcopy(self.rows), deepcopy(self.sources)
        sources["regulatoryComparison"]["causalAttribution"] = "cummins"
        self.refresh_fingerprints(rows, sources)
        with self.assertRaisesRegex(ValueError, "attribution"):
            AUDIT.comment_response_diagnostics(rows, sources)


class CommentPositionTests(unittest.TestCase):
    def setUp(self):
        self.rows = AUDIT.read("comment-position-pilot.csv")
        self.sources = json.loads((AUDIT.DATA / "comment-position-source.json").read_text())

    def test_one_letter_two_positions_not_two_comments_or_uptake(self):
        result = AUDIT.comment_position_diagnostics(self.rows, self.sources)
        self.assertEqual(result["positionRows"], 2)
        self.assertEqual(result["publicLetters"], 1)
        self.assertEqual(result["candidateDocketSubmissions"], 1)
        self.assertEqual(result["alignedWithProposal"], 2)
        self.assertEqual(result["alignedWithFinalAction"], 2)
        self.assertEqual(result["changedActionsAtCodedScope"], 0)
        self.assertEqual(result["verifiedDocketVersionMatches"], 0)
        self.assertEqual(result["observedUptakeLinks"], 0)

    def test_source_metadata_preserves_receipt_posting_and_separate_submissions(self):
        records = self.sources["records"]
        self.assertEqual([len(record["attachments"]) for record in records], [1, 19])
        for record in records:
            self.assertEqual(record["attributes"]["receiveDate"][:10], "2024-09-18")
            self.assertEqual(record["attributes"]["postedDate"][:10], "2024-10-09")
        self.assertNotEqual(records[0]["commentId"], records[1]["commentId"])

    def test_rejects_duplicate_metadata_and_positions(self):
        for target in ("metadata", "positions", "renamed_position"):
            with self.subTest(target=target):
                sources, rows = deepcopy(self.sources), deepcopy(self.rows)
                if target == "metadata":
                    sources["records"].append(deepcopy(sources["records"][0]))
                else:
                    rows.append(deepcopy(rows[0]))
                    if target == "renamed_position":
                        rows[-1]["positionId"] = "different-id-same-issue"
                with self.assertRaises(ValueError):
                    AUDIT.comment_position_diagnostics(rows, sources)

    def test_rejects_changed_source_fingerprint_or_cross_comment_join(self):
        for field in ("receiveDate", "title"):
            sources = deepcopy(self.sources)
            sources["records"][0]["attributes"][field] = "changed"
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                AUDIT.comment_position_diagnostics(self.rows, sources)
        rows = deepcopy(self.rows)
        other = self.sources["records"][1]
        rows[0]["candidateCommentId"] = other["commentId"]
        rows[0]["metadataFingerprint"] = other["sourceFingerprint"]
        with self.assertRaisesRegex(ValueError, "identity"):
            AUDIT.comment_position_diagnostics(rows, self.sources)

    def test_agreement_cannot_promote_copy_to_uptake(self):
        for field in ("unit", "docketVersionMatch", "agencyResponseLink", "uptake",
                      "regulatoryTextChange", "independentReviewStatus"):
            rows = deepcopy(self.rows)
            rows[0][field] = "observed"
            with self.subTest(field=field), self.assertRaises(ValueError):
                AUDIT.comment_position_diagnostics(rows, self.sources)

    def test_new_copy_or_rule_source_invalidates_prior_position_review(self):
        for section, key, value in (("publicCopy", "htmlSha256", "0" * 64),
                                    ("proposed", "pdfPage", 46),
                                    ("final", "pdfSha256", "1" * 64)):
            sources = deepcopy(self.sources)
            target = sources[section] if section == "publicCopy" else sources["ruleSources"][section]
            target[key] = value
            with self.subTest(section=section), self.assertRaisesRegex(ValueError, "identity"):
                AUDIT.comment_position_diagnostics(self.rows, sources)

    def test_requires_chronology_and_source_page_provenance(self):
        for field, value in (("date", "2025-01-01"), ("pdfSha256", ""),
                             ("sourcePage", ""), ("pdfPage", 0)):
            sources = deepcopy(self.sources)
            sources["ruleSources"]["proposed"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                AUDIT.comment_position_diagnostics(self.rows, sources)


class CommentSourceTests(unittest.TestCase):
    def test_ordinary_letters_are_preserved(self):
        text = "Utah regional haze: enforce effective controls, transfer information."
        self.assertEqual(MODULE.public_comment_text(text), text)

    def test_html_breaks_entities_and_real_whitespace(self):
        self.assertEqual(
            MODULE.public_comment_text(" <p>Utah&#39;s\tplan</p><br /><br/> firm\r\n review\f\v "),
            "Utah's plan\nfirm\nreview",
        )

    def test_literal_backslash_letters_are_not_whitespace(self):
        self.assertEqual(MODULE.public_comment_text(r"first \t river \n final"), r"first \t river \n final")

    def test_cleaning_is_idempotent(self):
        clean = MODULE.public_comment_text("First<br/>river &amp; final\tcontrols")
        self.assertEqual(MODULE.public_comment_text(clean), clean)

    def test_preserves_cohort_order_and_rejects_bad_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cohort.csv"
            def write(rows):
                with path.open("w", newline="") as target:
                    writer = csv.writer(target)
                    writer.writerow(["docketId", "commentId"])
                    writer.writerows(rows)
            write([("docket", "b"), ("docket", "a")])
            self.assertEqual(MODULE.existing_comment_ids(path, "docket"), ["b", "a"])
            for rows in ([], [("docket", "")], [("docket", "a"), ("docket", "a")], [("other", "a")]):
                write(rows)
                with self.assertRaises(ValueError):
                    MODULE.existing_comment_ids(path, "docket")


if __name__ == "__main__":
    unittest.main()
