#!/usr/bin/env python3
"""Offline evidence-contract tests for the selected FY2024 GAO award bridge."""

import copy
import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("expansion", ROOT / "scripts/audit-empirical-expansion.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class LinkageTests(unittest.TestCase):
    def setUp(self):
        self.rows = audit.read("gao-award-linkage-pilot.csv")
        self.source = json.loads((audit.DATA / "gao-award-linkage-source.json").read_text())
        with (ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-actions.csv").open() as f:
            self.frozen = list(csv.DictReader(f))

    def check(self):
        return audit.protest_linkage_diagnostics(self.rows, self.source, self.frozen)

    def test_committed_evidence_reproduces_without_mutation(self):
        before = copy.deepcopy((self.rows, self.source, self.frozen))
        self.assertEqual(self.check(), (4, 1, 0))
        self.assertEqual((self.rows, self.source, self.frozen), before)

    def test_duplicate_or_missing_award_rejected(self):
        self.rows[-1] = self.rows[0].copy()
        with self.assertRaisesRegex(ValueError, "off-cohort"):
            self.check()

    def test_identity_and_parent_mismatches_rejected(self):
        for field in ("uei", "parentPiid", "usaspendingAwardKey", "awardingSubtierCode"):
            with self.subTest(field=field):
                original = self.rows[0][field]
                self.rows[0][field] = "WRONG"
                with self.assertRaisesRegex(ValueError, "identity mismatch"):
                    self.check()
                self.rows[0][field] = original

    def test_current_award_total_cannot_replace_action_obligation(self):
        self.rows[0]["actionObligationDollars"] = self.rows[0]["currentAwardTotalObligationDollars"]
        with self.assertRaisesRegex(ValueError, "amount mismatch"):
            self.check()

    def test_performance_start_cannot_replace_action_date(self):
        self.rows[0]["originalActionDate"] = self.rows[0]["performanceStartDate"]
        with self.assertRaisesRegex(ValueError, "timing"):
            self.check()

    def test_pagination_and_stale_panel_counts_rejected(self):
        self.source["transactionSearch"]["response"]["page_metadata"]["hasNext"] = True
        with self.assertRaisesRegex(ValueError, "pagination"):
            self.check()
        self.source["transactionSearch"]["response"]["page_metadata"]["hasNext"] = False
        self.frozen.append({"agency": self.rows[0]["agency"], "piid": self.rows[0]["piid"]})
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.check()

    def test_unsupported_filed_date_or_promotion_rejected(self):
        for field, value in (("filedDate", "2024-06-01"), ("linkageStatus", "estimation_ready")):
            original = self.rows[0][field]
            self.rows[0][field] = value
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                self.check()
            self.rows[0][field] = original

    def test_bulk_units_or_historical_identity_mismatch_rejected(self):
        self.source["bulkExtract"]["records"][0]["amount"] = "10000"
        with self.assertRaisesRegex(ValueError, "Archived bulk"):
            self.check()


class DocketTimingTests(unittest.TestCase):
    def setUp(self):
        self.rows = audit.read("gao-docket-timing-pilot.csv")
        self.source = json.loads((audit.DATA / "gao-docket-timing-source.json").read_text())
        self.awards = json.loads((audit.DATA / "gao-award-linkage-source.json").read_text())
        self.manifest = json.loads((ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-bulk-summary.json").read_text())

    def check(self):
        return audit.docket_timing_diagnostics(self.rows, self.source, self.awards, self.manifest)

    def test_complete_case_frame_and_date_counts_reproduce_without_mutation(self):
        before = copy.deepcopy((self.rows, self.source, self.awards, self.manifest))
        result = self.check()
        self.assertEqual(result["expectedEntries"], 13)
        self.assertEqual(result["reviewedEntries"], 13)
        self.assertEqual(result["decisionFamilies"], 1)
        self.assertEqual(result["filingDates"], {"2024-06-24": 6, "2024-06-26": 4, "2024-08-02": 3})
        self.assertEqual(result["multiSolicitationEntries"], 3)
        self.assertEqual(result["multiServiceAreaEntries"], 1)
        self.assertEqual(result["currentDescriptionCandidates"], 2)
        self.assertEqual(result["awardSpecificDatesPromoted"], 0)
        self.assertEqual(result["historicalExclusionIntervalsPromoted"], 0)
        self.assertEqual((self.rows, self.source, self.awards, self.manifest), before)
        self.rows.reverse()
        self.assertEqual(self.check(), result)

    def test_duplicate_missing_or_extra_normalized_rows_rejected(self):
        for changed in (self.rows[:-1], self.rows + [self.rows[0]], [self.rows[0]] * 13):
            with self.subTest(count=len(changed)), self.assertRaisesRegex(ValueError, "off-frame"):
                audit.docket_timing_diagnostics(changed, self.source, self.awards, self.manifest)

    def test_missing_source_cannot_shrink_denominator(self):
        self.source["records"].pop()
        self.rows.pop()
        with self.assertRaisesRegex(ValueError, "off-frame public"):
            self.check()

    def test_decision_heading_and_base_aliases_are_bound_to_source(self):
        self.source["decisionReview"]["caseNumbers"].pop()
        with self.assertRaisesRegex(ValueError, "case frame differs"):
            self.check()
        self.setUp()
        self.source["decisionReview"]["baseCaseDocketAliases"]["B-422689"] = "B-422689.2"
        with self.assertRaisesRegex(ValueError, "base docket aliases"):
            self.check()

    def test_source_native_names_and_many_to_many_scope_are_preserved(self):
        by_id = {r["docketFileNumber"]: r for r in self.rows}
        self.assertEqual(by_id["B-422690.1"]["protesterNative"], "Cardinal Health 200, Inc.")
        self.assertEqual(by_id["B-422690.2"]["solicitationNumbersNative"], "36C10X24R0007;36C10X24R0017")
        self.assertEqual(by_id["B-422693.3"]["decisionServiceAreas"], "VISN 8;VISN 19;VISN 22;OGA")
        by_id["B-422690.1"]["protesterNative"] = "Cardinal Health 200, LLC"
        with self.assertRaisesRegex(ValueError, "normalized field"):
            self.check()

    def test_changed_field_or_review_invalidates_fingerprints(self):
        for field in ("filedDate", "decisionDate", "postedDate", "dueDate", "sourceFingerprint", "reviewFingerprint"):
            with self.subTest(field=field):
                original = self.rows[0][field]
                self.rows[0][field] = "2024-01-01"
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    self.check()
                self.rows[0][field] = original
        self.source["captureScope"] += " Changed review."
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check()

    def test_invalid_source_chronology_rejected_even_after_regeneration(self):
        for field, value in (("filedDate", "Oct 1, 2024"), ("postedDate", "Sep 15, 2024"), ("dueDate", "Jun 1, 2024")):
            with self.subTest(field=field):
                self.setUp()
                self.source["records"][0]["fields"][field] = value
                self.rows = audit.docket_timing_rows(self.source)
                with self.assertRaisesRegex(ValueError, "chronology"):
                    self.check()

    def test_wrong_decision_link_rejected(self):
        self.source["records"][0]["fields"]["decisionUrl"] = "https://www.gao.gov/products/b-000001"
        self.rows = audit.docket_timing_rows(self.source)
        with self.assertRaisesRegex(ValueError, "decision link"):
            self.check()

    def test_unresolved_award_date_cannot_be_promoted(self):
        for field, value in (("piid", "36C10X24N0089"), ("awardTimingStatus", "estimation_ready"), ("independentReviewStatus", "complete")):
            with self.subTest(field=field):
                original = self.rows[0][field]
                self.rows[0][field] = value
                with self.assertRaisesRegex(ValueError, "claim boundary"):
                    self.check()
                self.rows[0][field] = original
        self.assertTrue(all(not r["filedDate"] for r in audit.read("gao-award-linkage-pilot.csv")))
        self.assertIsNone(self.awards["gaoReview"]["filedDate"])

    def test_overall_denial_cannot_erase_dismissed_issues(self):
        self.source["decisionReview"]["supplementalOciDisposition"] = "denied"
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            self.check()

    def test_reported_sam_check_cannot_become_historical_interval(self):
        for field, value in (("underlyingRecordsRead", True), ("checkDate", "2024-05-31"), ("historicalIntervalEligible", True)):
            with self.subTest(field=field):
                self.setUp()
                self.source["decisionReview"]["reportedSamCheck"][field] = value
                self.rows = audit.docket_timing_rows(self.source)
                with self.assertRaisesRegex(ValueError, "historical interval"):
                    self.check()

    def test_current_description_cannot_be_promoted_or_mapped_by_elimination(self):
        self.source["awardDescriptionChecks"][0]["originalActionMappingVerified"] = True
        self.rows = audit.docket_timing_rows(self.source)
        with self.assertRaisesRegex(ValueError, "current-description"):
            self.check()
        self.setUp()
        self.source["awardDescriptionChecks"][2]["explicitServiceAreaCandidate"] = "VISN 8"
        self.rows = audit.docket_timing_rows(self.source)
        with self.assertRaisesRegex(ValueError, "current-description"):
            self.check()

    def test_absent_archive_column_cannot_be_changed_to_empty_cell(self):
        self.source["archiveFieldCheck"]["columns"].append("solicitation_identifier")
        self.rows = audit.docket_timing_rows(self.source)
        with self.assertRaisesRegex(ValueError, "absent-column"):
            self.check()

    def test_archive_provenance_and_original_action_identity_rejected_on_drift(self):
        self.source["archiveFieldCheck"]["zipSha256"] = "0" * 64
        self.rows = audit.docket_timing_rows(self.source)
        with self.assertRaisesRegex(ValueError, "Archived field-check provenance"):
            self.check()
        self.setUp()
        self.source["archiveFieldCheck"]["selectedOriginalActions"][0]["fields"]["parent_award_id_piid"] = "WRONG"
        self.rows = audit.docket_timing_rows(self.source)
        with self.assertRaisesRegex(ValueError, "original-action identity"):
            self.check()


class OriginalActionTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads((audit.DATA / "gao-original-action-review.json").read_text())
        self.baseline = json.loads((audit.DATA / "gao-award-linkage-source.json").read_text())
        self.dockets = json.loads((audit.DATA / "gao-docket-timing-source.json").read_text())
        self.rows = audit.read("gao-docket-timing-pilot.csv")

    def check(self, rehash=False):
        if rehash:
            self.review["reviewFingerprint"] = audit.source_fingerprint(
                {k: v for k, v in self.review.items() if k != "reviewFingerprint"})
        return audit.original_action_diagnostics(self.review, self.baseline, self.dockets, self.rows)

    def test_complete_followup_and_many_to_many_links_reproduce(self):
        before = copy.deepcopy((self.review, self.baseline, self.dockets, self.rows))
        result, links = self.check()
        self.assertEqual(result["historyRows"], 26)
        self.assertEqual(result["reviewedAwards"], 4)
        self.assertEqual(result["explicitOriginalServiceAreas"], 2)
        self.assertEqual(result["amountBasedServiceAreaCandidates"], {"36C10X24N0088": "OGA", "36C10X24N0089": "VISN 8"})
        self.assertEqual(result["roundedPotentialValueMinusDecisionDollars"], {
            "36C10X24N0074": 0, "36C10X24N0088": 0, "36C10X24N0089": 0, "36C10X24N0108": -100})
        self.assertEqual(result["reportedOffersMinusTimelyProposals"], {"36C10X24N0089": -1})
        self.assertEqual(result["blankSolicitationIdentifiers"], 4)
        self.assertEqual(result["provisionalAwardDocketPairs"], 16)
        self.assertEqual(result["distinctLinkedDockets"], 13)
        self.assertEqual(result["originalReportedOffers"], {
            "36C10X24N0074": "4", "36C10X24N0088": "2",
            "36C10X24N0089": "4", "36C10X24N0108": "4"})
        self.assertEqual(sum(r["decisionCaseId"] == "B-422693.3" for r in links), 4)
        self.assertEqual({r["filedDate"] for r in links}, {"2024-06-24", "2024-06-26", "2024-08-02"})
        self.assertEqual((self.review, self.baseline, self.dockets, self.rows), before)

    def test_stale_projection_or_baseline_rejected(self):
        self.review["awards"][0]["originalProjection"]["number_of_offers_received"] = "0"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check()

    def test_missing_award_cannot_shrink_frame(self):
        self.review["awards"].pop()
        with self.assertRaisesRegex(ValueError, "off-frame"):
            self.check(rehash=True)

    def test_incomplete_history_rejected(self):
        self.review["awards"][0]["historyResponse"]["page_metadata"]["hasNext"] = True
        with self.assertRaisesRegex(ValueError, "pagination"):
            self.check(rehash=True)

    def test_duplicate_history_ids_rejected(self):
        history = self.review["awards"][0]["historyResponse"]["results"]
        history[-1] = history[0].copy()
        with self.assertRaisesRegex(ValueError, "transaction identity"):
            self.check(rehash=True)

    def test_later_modification_cannot_replace_original(self):
        self.review["awards"][0]["originalProjection"]["modification_number"] = "P00001"
        with self.assertRaisesRegex(ValueError, "substituted modification"):
            self.check(rehash=True)

    def test_current_totals_and_solicitation_dates_cannot_replace_action_values(self):
        row = self.review["awards"][0]["originalProjection"]
        for field, value in (("federal_action_obligation", "0.00"), ("action_date", row["solicitation_date"])):
            original = row[field]
            row[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "date, amount"):
                self.check(rehash=True)
            row[field] = original

    def test_generic_description_cannot_be_assigned_by_elimination(self):
        self.review["awards"][1]["explicitServiceArea"] = "OGA"
        with self.assertRaisesRegex(ValueError, "service-area assignment"):
            self.check(rehash=True)

    def test_native_blank_solicitation_cannot_be_filled_from_docket(self):
        self.review["awards"][0]["originalProjection"]["solicitation_identifier"] = "36C10X24R0014"
        with self.assertRaisesRegex(ValueError, "solicitation assignment"):
            self.check(rehash=True)

    def test_failed_download_is_not_an_empty_observation(self):
        self.review["awards"][0]["downloadStatus"]["status"] = "failed"
        with self.assertRaisesRegex(ValueError, "job provenance"):
            self.check(rehash=True)

    def test_unsupported_promotion_rejected(self):
        self.review["awardSpecificDatesPromoted"] = True
        with self.assertRaisesRegex(ValueError, "promotion"):
            self.check(rehash=True)

    def test_docket_date_must_match_saved_source(self):
        self.rows[0]["filedDate"] = "2024-05-31"
        with self.assertRaisesRegex(ValueError, "docket frame"):
            self.check()

    def test_negative_reported_offer_count_rejected(self):
        self.review["awards"][0]["originalProjection"]["number_of_offers_received"] = "-1"
        with self.assertRaisesRegex(ValueError, "offer count"):
            self.check(rehash=True)

    def test_value_candidate_requires_a_unique_rounded_match(self):
        self.review["awards"][1]["originalProjection"]["potential_total_value_of_award"] = "149280000.00"
        with self.assertRaisesRegex(ValueError, "service-area assignment"):
            self.check(rehash=True)

    def test_action_obligation_cannot_replace_potential_order_value(self):
        row = self.review["awards"][1]["originalProjection"]
        row["potential_total_value_of_award"] = row["federal_action_obligation"]
        with self.assertRaisesRegex(ValueError, "service-area assignment"):
            self.check(rehash=True)


if __name__ == "__main__":
    unittest.main()
