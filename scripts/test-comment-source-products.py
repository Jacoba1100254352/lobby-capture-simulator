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
