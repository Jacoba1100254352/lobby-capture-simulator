#!/usr/bin/env python3
"""Keep new source acquisitions distinct from identified substitution estimates."""

import importlib.util
import json
import tempfile
from argparse import Namespace
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FEC = load("fec_expansion", "fetch-substitution-fec-reports.py")
LDA = load("lda_expansion", "build-substitution-historical-lda-panel.py")
PERIODS = load("fec_periods", "prepare-substitution-fec-periods.py")
AUDIT = load("source_measurement_audit", "audit-empirical-expansion.py")
FAMILIES = load("lda_families", "review-substitution-lda-families.py")


class LDAFamilyReviewTests(unittest.TestCase):
    def setUp(self):
        self.metadata = AUDIT.read("substitution-lda-filing-metadata.csv")
        self.source = json.loads(FAMILIES.SOURCE.read_text())
        self.cover = json.loads((AUDIT.DATA / "substitution-lda-date-reviews.json").read_text())

    def check(self, refresh=True):
        if refresh:
            self.source["reviewFingerprint"] = FAMILIES.fingerprint(
                {k: v for k, v in self.source.items() if k != "reviewFingerprint"})
        return FAMILIES.validate_review(self.metadata, self.source, self.cover)

    def test_complete_candidate_queue_preserves_source_and_no_final_version(self):
        before = deepcopy(self.metadata)
        queue, result = self.check(refresh=False)
        self.assertEqual(queue, AUDIT.read("substitution-lda-family-queue.csv"))
        expected = dict(candidateGroups=364, multiRecordGroups=22, multiRecordFilings=46,
                        groupsWithoutAmendmentLabel=10, groupsWithDifferentSourceAmounts=8,
                        groupsWithPostingTies=3, groupsWithLatestMissingEarlierAmount=2,
                        groupsWithNoActivityNonzero=1, singletonAmendmentGroups=1,
                        apgaQueriedApiFilings=2, nvgQueryReturnedFilings=14, identityApiFilingsChecked=2,
                        reviewedDistinctImages=7, apgaReviewedDistinctImages=5, energyAgencyMismatches=2,
                        sourceReviewedGroups=2, identityReviewedCovers=2, differentClientCovers=1,
                        registrationSuffixDiscrepancies=1, unlabelledAmendedCovers=1,
                        finalVersionsSelected=0)
        for key, value in expected.items():
            self.assertEqual(result[key], value, key)
        self.assertEqual(self.metadata, before)
        self.assertEqual(sum(r["reviewStatus"] == "source_identity_conflict_not_mergeable" for r in queue), 1)

    def test_stale_review_or_source_metadata_fails(self):
        self.source["codingNotes"] += " changed"
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.check(refresh=False)
        self.metadata[0]["incomeDollars"] = "0.00"
        with self.assertRaisesRegex(ValueError, "Stale filing"):
            self.check()

    def test_duplicate_metadata_and_missing_catalog_code_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            FAMILIES.candidate_queue(self.metadata + [self.metadata[0]], self.source["filingTypeCatalog"]["entries"])
        with self.assertRaisesRegex(ValueError, "catalog"):
            FAMILIES.candidate_queue(self.metadata, [r for r in self.source["filingTypeCatalog"]["entries"] if r["value"] != "MM"])

    def test_query_cannot_hide_pagination_or_drop_a_filing(self):
        original = deepcopy(self.source)
        for field, value in (("count", 3), ("next", "https://lda.gov/api/v1/filings/?page=2"),
                             ("records", self.source["query"]["records"][:1]),
                             ("url", "https://lda.gov/api/v1/filings/?registrant_id=74077")):
            self.source = deepcopy(original)
            self.source["query"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()

    def test_missing_amendment_amount_is_not_zero_or_original_amount(self):
        original = deepcopy(self.source)
        for value in ("0.00", "100000.00"):
            self.source = deepcopy(original)
            amended = next(r for r in self.source["query"]["records"] if r["filing_type"] == "MA")
            amended["expenses"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "projection"):
                self.check()

    def test_duplicate_pdf_pages_are_not_independent_images(self):
        self.source["documents"][1]["images"][0]["pdfPages"] = [1]
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.check()

    def test_issue_page_cannot_be_called_a_financial_cover(self):
        self.source["documents"][1]["images"][0]["kind"] = "cover"
        with self.assertRaisesRegex(ValueError, "Financial cover"):
            self.check()

    def test_energy_pair_retains_scan_identity_and_blank_to_filled_field(self):
        original = deepcopy(self.source)
        for field, value in (("underlyingScanIdentifier", "00000232929"), ("lobbyists", []),
                             ("receiptTimezone", "America/New_York"), ("financialAmountFieldsPresent", True)):
            self.source = deepcopy(original)
            self.source["documents"][1]["images"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()

    def test_api_contact_mismatch_is_not_silently_repaired(self):
        original = deepcopy(self.source)
        self.source["query"]["records"][0]["activities"][0]["governmentEntities"][-1]["name"] = "Federal Energy Regulatory Commission"
        with self.assertRaisesRegex(ValueError, "discrepancies"):
            self.check()
        self.source = original
        self.source["query"]["records"][0]["activities"][0]["lobbyists"] = []
        with self.assertRaisesRegex(ValueError, "lobbyist"):
            self.check()

    def test_family_review_does_not_clear_spending_exposure_or_causality(self):
        original = deepcopy(self.source)
        for key, value in (("historicalPacketComplete", True), ("finalAmountDollars", "100000.00"),
                           ("selectedFinalFilingUuid", "50ca0707-6dc1-43a0-9115-89ba56ffd0c7"),
                           ("agencyExposureCleared", True), ("controlAssignmentCleared", True),
                           ("causalEffect", "identified")):
            self.source = deepcopy(original)
            self.source["boundary"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "promotion"):
                self.check()

    def test_independent_review_cannot_be_self_declared_complete(self):
        self.source["independentReviewStatus"] = "complete"
        with self.assertRaises(ValueError):
            self.check()

    def test_different_client_is_not_a_mergeable_aaj_version(self):
        original = deepcopy(self.source)
        for field, value in (("clientName", "AMERICAN ASSOCIATION FOR JUSTICE"),
                             ("senateId", "76833-113"), ("amendmentBoxChecked", True)):
            self.source = deepcopy(original)
            self.source["identityReviews"][1]["form"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()

    def test_identity_query_cannot_promote_all_returned_filings(self):
        self.source["identityQuery"]["selectedMetadata"].append(deepcopy(self.source["identityQuery"]["selectedMetadata"][0]))
        with self.assertRaisesRegex(ValueError, "query scope"):
            self.check()

    def test_identity_conflicts_cannot_be_silently_corrected(self):
        self.source["identityReviews"][0]["rawRecordCorrected"] = True
        with self.assertRaisesRegex(ValueError, "promotion"):
            self.check()


class LDADateReviewTests(unittest.TestCase):
    def setUp(self):
        self.metadata = AUDIT.read("substitution-lda-filing-metadata.csv")
        self.sources = json.loads((AUDIT.DATA / "substitution-lda-date-reviews.json").read_text())

    def check(self, sources, refresh=True):
        if refresh:
            sources["reviewFingerprint"] = AUDIT.source_fingerprint(
                {k: v for k, v in sources.items() if k != "reviewFingerprint"})
        return AUDIT.lda_date_review_diagnostics(self.metadata, sources)

    def test_all_flagged_covers_reviewed_without_rewriting_metadata(self):
        original = deepcopy(self.metadata)
        result = self.check(self.sources, refresh=False)
        self.assertEqual(result["postingBeforeCoveredPeriod"], 3)
        self.assertEqual(result["reviewedEmbeddedCovers"], 3)
        self.assertEqual(result["registrationComponentMatches"], 3)
        self.assertEqual(result["differentRegistrantNames"], 2)
        self.assertEqual(result["reviewedExpenseMethods"], {"A": 2})
        self.assertEqual(result["censoredIncomeDisclosures"], 1)
        self.assertEqual(result["sourceMissingTerminationDates"], 1)
        self.assertEqual(result["correctedApiPostingDates"], 0)
        self.assertFalse(result["amendmentOrderingCleared"])
        self.assertEqual(self.metadata, original)

    def test_missing_duplicate_or_foreign_review_fails(self):
        for kind in ("missing", "duplicate", "foreign"):
            sources = deepcopy(self.sources)
            if kind == "missing":
                sources["reviews"].pop()
            elif kind == "duplicate":
                sources["reviews"].append(deepcopy(sources["reviews"][0]))
            else:
                sources["reviews"][0]["filingUuid"] = "foreign"
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "frame"):
                self.check(sources)

    def test_stale_source_or_changed_review_requires_revalidation(self):
        sources = deepcopy(self.sources)
        sources["reviews"][0]["form"]["notes"] = "Different reading"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.check(sources, refresh=False)
        self.metadata[0]["dtPosted"] = "1900-01-01T00:00:00-05:00"
        with self.assertRaises(ValueError):
            self.check(self.sources)

    def test_api_projection_is_not_a_corrected_source(self):
        for field, value in (("dt_posted", "2003-07-31T10:32:00-04:00"),
                             ("expenses_method", "A"), ("termination_date", "2003-07-31")):
            sources = deepcopy(self.sources)
            sources["reviews"][0]["apiProjection"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "projection"):
                self.check(sources)

    def test_receipt_stamp_period_and_registration_are_distinct(self):
        for field, value in (("receiptDate", "2003-07-30"), ("receiptTimezone", "America/New_York"),
                             ("period", "year_end"), ("senateId", "74077-90"),
                             ("amendmentBoxChecked", True), ("terminationDate", "2003-07-31")):
            sources = deepcopy(self.sources)
            sources["reviews"][0]["form"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(sources)

    def test_below_threshold_income_cannot_be_promoted_to_point_zero(self):
        for field, value in (("reportedAmountDollars", "0.00"), ("expensesMethod", "A"),
                             ("incomeUpperBoundExclusiveDollars", "0.00"),
                             ("amountDisclosure", "exact_zero"), ("clientSelf", True)):
            sources = deepcopy(self.sources)
            sources["reviews"][2]["form"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Censored"):
                self.check(sources)

    def test_review_does_not_clear_ordering_aggregation_or_controls(self):
        for field, value in (("correctedApiPostingDates", 3), ("amendmentOrderingCleared", True),
                             ("amountAggregationCleared", True), ("controlAssignmentCleared", True),
                             ("rawMetadataUnchanged", False), ("causalEffect", "identified")):
            sources = deepcopy(self.sources)
            sources["reviewBoundary"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "promotion"):
                self.check(sources)

    def test_full_image_provenance_and_independent_review_cannot_be_dropped(self):
        for field in ("pdfSha256", "embeddedCoverPngSha256", "responseSha256"):
            sources = deepcopy(self.sources)
            sources["reviews"][0][field] = ""
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "provenance"):
                self.check(sources)
        sources = deepcopy(self.sources)
        sources["independentReviewStatus"] = "complete"
        with self.assertRaises(ValueError):
            self.check(sources)


class SourceExpansionTests(unittest.TestCase):
    @staticmethod
    def lda_record(**overrides):
        return {"filing_uuid": "fixture-filing", "filing_year": 2003, "filing_type": "MM",
            "filing_period": "mid_year", "client": {"id": 12, "client_id": 3, "name": "ACTOR"},
            "registrant": {"id": 4, "name": "ACTOR"}, "income": None,
            "expenses": "12.34", "expenses_method": None, **overrides}

    def test_lda_measurement_preserves_null_zero_kind_and_precision(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        for income, expenses, kind, amount in [
            (None, "12.34", "expenses", "0.00001234"),
            (0, None, "income", "0.00000000"),
            (None, None, "neither", ""),
            ("0.00", "12.34", "both", ""),
        ]:
            row = LDA.filing_metadata(actor, self.lda_record(income=income, expenses=expenses), "2026-09-12")
            self.assertEqual(row["amountKind"], kind)
            self.assertEqual(row["expensesMethod"], "")
            self.assertEqual(LDA.measurement_amount(row), amount)
        for bad in ("NaN", "Infinity", "oops", -1):
            with self.assertRaises(ValueError):
                LDA.filing_metadata(actor, self.lda_record(expenses=bad), "2026-09-12")

    def test_lda_review_fingerprint_tracks_source_not_retrieval_date(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        row = LDA.filing_metadata(actor, self.lda_record(), "2026-09-12")
        self.assertEqual(LDA.metadata_fingerprint({**row, "retrievedDate": "2026-09-13"}), row["sourceFingerprint"])
        for field in ("expensesDollars", "expensesMethod", "registrantApiId", "clientApiId"):
            self.assertNotEqual(LDA.metadata_fingerprint({**row, field: "changed"}), row["sourceFingerprint"])

    def test_lda_alias_requires_exact_name_and_both_registration_ids(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        alias = {"canonicalActorId": "actor", "aliasName": "OLD NAME", "clientApiId": "12",
            "registrantApiId": "4", "aliasReviewId": "review", "startYear": "2003", "endYear": "2003"}
        valid = self.lda_record(client={"id": 12, "client_id": 3, "name": "OLD NAME"})
        candidates = [valid,
            self.lda_record(filing_uuid="other-client", client={"id": 99, "name": "OLD NAME"}),
            self.lda_record(filing_uuid="other-firm", client=valid["client"], registrant={"id": 99, "name": "FIRM"}),
            self.lda_record(filing_uuid="partial-name", client={"id": 12, "name": "OLD NAME AFFILIATE"})]
        responses = [({"results": [], "count": 0, "next": None}, ""),
            ({"results": candidates, "count": 4, "next": None}, "")]
        metadata = []
        with patch.object(LDA, "fetch_json", side_effect=responses):
            rows, _ = LDA.fetch_actor_rows(actor, ["2003"], page_size=100, max_pages=3,
                timeout=1, review_date="2026-09-12", generated_at="2026-09-12",
                aliases=[alias], metadata_rows=metadata)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["filingUuid"], "fixture-filing")
        self.assertIn("reviewed-exact-alias", rows[0]["evidenceRule"])
        self.assertEqual(metadata[0]["aliasReviewId"], "review")

    def test_lda_off_year_and_conflicting_uuid_fail(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        for records in ([self.lda_record(filing_year=2004)],
                [self.lda_record(), self.lda_record(expenses="99")]):
            with patch.object(LDA, "fetch_json", return_value=({"results": records, "count": len(records), "next": None}, "")):
                with self.assertRaises(ValueError):
                    LDA.fetch_actor_rows(actor, ["2003"], page_size=100, max_pages=3,
                        timeout=1, review_date="2026-09-12", generated_at="2026-09-12")

    def test_lda_cache_reuses_only_same_day_and_intact_public_responses(self):
        payload = {"count": 0, "results": [], "next": None}
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            with patch.object(LDA, "fetch_json", return_value=(payload, "")) as fetch:
                for _ in range(2):
                    self.assertEqual(LDA.cached_fetch_json("https://lda.gov/api/v1/filings/", 1, cache, "2026-09-12"), (payload, ""))
                self.assertEqual(fetch.call_count, 1)
                LDA.cached_fetch_json("https://lda.gov/api/v1/filings/", 1, cache, "2026-09-13")
                self.assertEqual(fetch.call_count, 2)
            path = next(cache.glob("2026-09-12-*.json"))
            content = json.loads(path.read_text())
            content["response"]["count"] = 9
            path.write_text(json.dumps(content))
            with self.assertRaisesRegex(ValueError, "provenance"):
                LDA.cached_fetch_json("https://lda.gov/api/v1/filings/", 1, cache, "2026-09-12")

    def test_lda_does_not_retry_auth_or_quota_failures(self):
        for status in (401, 403, 429):
            error = LDA.urllib.error.HTTPError("https://lda.gov/api/v1/filings/", status, "fixture", {}, None)
            with patch.object(LDA.urllib.request, "urlopen", side_effect=error) as request, patch.object(LDA.time, "sleep") as sleep:
                payload, message = LDA.fetch_json("https://lda.gov/api/v1/filings/", 1)
                self.assertIsNone(payload)
                self.assertIn(str(status), message)
                self.assertEqual(request.call_count, 1)
                sleep.assert_not_called()

    def measurement_case(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        record = self.lda_record(expenses="20000.00", filing_document_url="https://lda.gov/filings/public/filing/fixture/print/")
        source = LDA.filing_metadata(actor, record, "2026-09-12")
        rows = LDA.panel_rows_for_record(actor, record, "2026-09-12")
        LDA.mark_design_candidates(rows)
        rows[0]["activityAmount"] = LDA.measurement_amount(source)
        review = {
            "reviewId": "fixture-review", "filingUuid": source["filingUuid"], "sourceFingerprint": source["sourceFingerprint"],
            "pdfSha256": "0" * 64, "pagesReviewed": "1", "formRegistrantName": "ACTOR", "formClientSelf": "true",
            "formYear": "2003", "formPeriod": "mid_year", "formExpensesDollars": "20000.00", "formExpensesMethod": "A",
            "formAmountDisclosure": "at_least_threshold_rounded", "sourceUrl": source["filingDocumentUrl"],
            "reviewer": "fixture", "reviewDate": "2026-09-12", "reviewScope": "page_1_identity_amount_method_only",
            "independentReviewStatus": "pending",
        }
        return rows, source, review

    def test_lda_measurement_audit_keeps_method_review_separate(self):
        rows, source, review = self.measurement_case()
        result = AUDIT.lda_measurement_diagnostics(rows, [source], [review], [])
        self.assertEqual(result["reviewedExpenseMethods"], {"A": 1})
        self.assertEqual(result["expenseMethodMissing"], 1)
        self.assertEqual(source["expensesMethod"], "")
        self.assertEqual(result["incomeExpenseOverlapActorPeriods"], 0)

    def test_lda_audit_rejects_missing_duplicate_or_changed_sources(self):
        rows, source, review = self.measurement_case()
        for metadata in ([], [source, source], [{**source, "expensesDollars": "99"}]):
            with self.assertRaises(ValueError):
                AUDIT.lda_measurement_diagnostics(rows, metadata, [review], [])
        for field, value in (("activityAmount", "20000.00"), ("exposureGroup", "treated"), ("clientName", "OTHER")):
            with self.assertRaises(ValueError):
                AUDIT.lda_measurement_diagnostics([{**rows[0], field: value}], [source], [review], [])

    def test_lda_audit_rejects_stale_or_overstated_form_reviews(self):
        rows, source, review = self.measurement_case()
        for field, value in (("sourceFingerprint", "0" * 64), ("formExpensesDollars", "99"),
                ("formExpensesMethod", "unknown"), ("formClientSelf", "false"),
                ("reviewScope", "whole_report"), ("independentReviewStatus", "approved"), ("reviewer", "")):
            with self.assertRaises(ValueError):
                AUDIT.lda_measurement_diagnostics(rows, [source], [{**review, field: value}], [])
        with self.assertRaises(ValueError):
            AUDIT.lda_measurement_diagnostics(rows, [source], [review, review], [])

    @staticmethod
    def period_row(start="2006-01-01", end="2006-06-30", **overrides):
        return {"canonicalActorId": "a", "committeeId": "C00007450", "mostRecent": "true",
            "isAmended": "false", "periodStart": start, "periodEnd": end,
            "sourceRecordId": start, "candidateContributionsDollars": "12.34",
            "independentExpendituresDollars": "0.00", "totalDisbursementsDollars": "20.01", **overrides}

    @staticmethod
    def cohort(**overrides):
        return [{"canonicalActorId": "a", "committeeId": "C00007450", "startYear": "2006", "endYear": "2006", **overrides}]

    def supplement_case(self):
        parent = self.period_row(isAmended="true")
        supplement = self.period_row(sourceRecordId="supplement", mostRecent="none", amendmentIndicator="A", **{f: "" for f in PERIODS.MEASURES})
        review = {
            "adjudicationId": "fixture-review", "committeeId": parent["committeeId"],
            "canonicalActorId": "a", "periodStart": parent["periodStart"], "periodEnd": parent["periodEnd"],
            "retainedRecordId": parent["sourceRecordId"], "supplementRecordId": "supplement",
            "decision": "supplemental_loan_paperwork_only", "reviewer": "fixture", "reviewDate": "2026-09-12",
            "rationale": "Test fixture: supplement contains no replacement totals.",
            "retainedRecordFingerprint": PERIODS.record_fingerprint(parent),
            "supplementRecordFingerprint": PERIODS.record_fingerprint(supplement),
        }
        for prefix in ("retained", "supplement"):
            review.update({f"{prefix}SourceUrl": "https://docquery.fec.gov/pdf/fixture.pdf", f"{prefix}PdfSha256": "0" * 64, f"{prefix}PagesReviewed": "1"})
        return [parent, supplement], review

    def test_reviewed_supplement_recovers_period_without_mutating_source(self):
        raw, review = self.supplement_case()
        self.assertEqual(PERIODS.prepare_with_coverage(raw, self.cohort())[0], [])
        prepared, coverage = PERIODS.prepare_with_coverage(raw, self.cohort(), [review])
        self.assertEqual(len(prepared), 1)
        self.assertEqual(prepared[0]["selectionBasis"], "source_reviewed_supplement")
        self.assertEqual(prepared[0]["candidateContributionsDollars"], "12.34")
        self.assertEqual(prepared[0]["reportCount"], "1")
        self.assertEqual(coverage[0]["missingRawOutcomeCells"], "3")
        self.assertEqual(coverage[0]["latestReportCount"], "0")
        self.assertEqual(coverage[0]["eligibleReportCount"], "1")
        self.assertEqual(raw[0]["isAmended"], "true")
        self.assertEqual(raw[1]["mostRecent"], "none")

    def test_review_never_authorizes_an_unreviewed_alternative(self):
        raw, review = self.supplement_case()
        raw.append(self.period_row(sourceRecordId="new-alternative", mostRecent="none"))
        prepared, coverage = PERIODS.prepare_with_coverage(raw, self.cohort(), [review])
        self.assertEqual(prepared, [])
        self.assertEqual(coverage[0]["unknownVersionRecordIds"], "new-alternative")

    def test_stale_incomplete_or_duplicate_adjudication_aborts(self):
        raw, review = self.supplement_case()
        for changed in [{"reviewer": ""}, {"decision": "prefer_original"}, {"retainedPdfSha256": "bad"}, {"retainedRecordFingerprint": "0" * 64}, {"canonicalActorId": "other"}]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                PERIODS.prepare_with_coverage(raw, self.cohort(), [{**review, **changed}])
        with self.assertRaises(ValueError):
            PERIODS.prepare_with_coverage(raw, self.cohort(), [review, review])
        raw[0]["candidateContributionsDollars"] = "99.00"
        with self.assertRaisesRegex(ValueError, "stale"):
            PERIODS.prepare_with_coverage(raw, self.cohort(), [review])

    def test_expected_frame_retains_missing_halfyears_and_whole_committee(self):
        extra = self.cohort(canonicalActorId="b", committeeId="C00153171")
        prepared, coverage = PERIODS.prepare_with_coverage([self.period_row()], self.cohort() + extra)
        self.assertEqual(len(prepared), 1)
        self.assertEqual(len(coverage), 4)
        self.assertEqual([r["status"] for r in coverage], ["observed_complete", "missing_source", "missing_source", "missing_source"])
        self.assertTrue(all(r["acceptedReportCount"] == "0" for r in coverage[1:]))

    def test_unknown_alternative_blocks_otherwise_complete_period(self):
        raw = [self.period_row(), self.period_row(sourceRecordId="amendment", mostRecent="none")]
        prepared, coverage = PERIODS.prepare_with_coverage(raw, self.cohort())
        self.assertEqual(prepared, [])
        self.assertEqual(coverage[0]["reasonCodes"], "unresolved_version")
        self.assertEqual(coverage[0]["unknownVersionRecordIds"], "amendment")
        self.assertEqual(coverage[0]["latestReportCount"], "1")
        self.assertEqual(coverage[0]["acceptedReportCount"], "0")

    def test_known_superseded_unknown_latest_does_not_block(self):
        raw = [self.period_row(), self.period_row(sourceRecordId="old", mostRecent="none", isAmended="true")]
        prepared, coverage = PERIODS.prepare_with_coverage(raw, self.cohort())
        self.assertEqual(len(prepared), 1)
        self.assertEqual(coverage[0]["unknownVersionRecordIds"], "")

    def test_cross_halfyear_report_quarantines_both_intersections(self):
        raw = [self.period_row("2006-01-01", "2006-07-31")]
        prepared, coverage = PERIODS.prepare_with_coverage(raw, self.cohort())
        self.assertEqual(prepared, [])
        self.assertTrue(all(r["reasonCodes"] == "straddling_report" for r in coverage))

    def test_bad_partition_does_not_erase_valid_other_halfyear(self):
        bad = self.period_row(candidateContributionsDollars="")
        good = self.period_row("2006-07-01", "2006-12-31")
        prepared, coverage = PERIODS.prepare_with_coverage([bad, good], self.cohort())
        self.assertEqual([r["halfYear"] for r in prepared], ["2006H2"])
        self.assertEqual(coverage[0]["reasonCodes"], "missing_outcome")
        self.assertEqual(coverage[0]["missingRawOutcomeCells"], "1")
        for bad in [self.period_row(end="2006-03-31"), self.period_row(start="2006-03-01"), self.period_row(candidateContributionsDollars="NaN")]:
            prepared, coverage = PERIODS.prepare_with_coverage([bad, good], self.cohort())
            self.assertEqual(len(prepared), 1)
            self.assertEqual(coverage[0]["status"], "unresolved")

    def test_structural_errors_abort_instead_of_silent_partition_exclusion(self):
        for rows, cohort in [
            ([self.period_row(), self.period_row()], self.cohort()),
            ([self.period_row(mostRecent="maybe")], self.cohort()),
            ([self.period_row(canonicalActorId="other")], self.cohort()),
            ([self.period_row(start="2005-12-31")], self.cohort()),
            ([self.period_row(end="2005-12-31")], self.cohort()),
            ([self.period_row()], self.cohort() * 2),
            ([self.period_row()], self.cohort(endYear="2005")),
        ]:
            with self.subTest(rows=rows, cohort=cohort), self.assertRaises(ValueError):
                PERIODS.prepare_with_coverage(rows, cohort)

    def test_single_committee_requires_explicit_matching_actor(self):
        with self.assertRaises(ValueError):
            FEC.acquisition_members(Namespace(committee_id="C00153171", canonical_actor_id=None))
        members = FEC.acquisition_members(Namespace(committee_id="C00153171", canonical_actor_id="b", years=[2004]))
        self.assertEqual(members, [("b", "C00153171", [2004])])

    def test_cohort_fetch_failure_does_not_write_partial_snapshot(self):
        members = [("a", "C00007450", [2004]), ("b", "C00153171", [2004])]
        history = {"committee_id": "C00007450", "cycle": 2004, "name": "Fixture PAC"}
        report = {"committee_id": "C00007450", "report_year": 2004, "report_type": "MY", "file_number": 1,
            "coverage_start_date": "2004-01-01", "coverage_end_date": "2004-06-30"}
        with patch.object(FEC, "acquisition_members", return_value=members), \
                patch.object(FEC, "fetch_all", side_effect=[[history], [report], RuntimeError("acquisition failed")]), \
                patch.object(FEC, "write_rows") as writer, \
                patch.dict(FEC.os.environ, {"FEC_API_KEY": "fixture-not-a-real-key"}), \
                patch("sys.argv", ["fetch-substitution-fec-reports.py"]):
            with self.assertRaisesRegex(RuntimeError, "acquisition failed"):
                FEC.main()
            writer.assert_not_called()

    def test_cohort_acquires_each_cycle_once_and_preserves_actor_identity(self):
        def response(resource, params, key):
            committee = resource.split("/")[1]
            if "/history/" in resource:
                return [{"committee_id": committee, "cycle": int(resource.split("/")[3]), "name": "Fixture PAC"}]
            year = params["year"]
            return [{"committee_id": committee, "report_year": year, "report_type": "MY",
                "file_number": int(committee[1:]) * 10000 + year,
                "coverage_start_date": f"{year}-01-01", "coverage_end_date": f"{year}-06-30",
                "fed_candidate_committee_contributions_period": "12.34"}]
        members = [("a", "C00007450", [2003, 2004]), ("b", "C00153171", [2003, 2004])]
        with patch.object(FEC, "fetch_all", side_effect=response) as fetch:
            reports, histories = FEC.acquire(members, "fixture-not-a-real-key", "2026-09-12")
        self.assertEqual(fetch.call_count, 6)
        self.assertEqual(len(histories), 2)
        self.assertEqual(len(reports), 4)
        self.assertEqual({(r["canonicalActorId"], r["committeeId"]) for r in reports}, {("a", "C00007450"), ("b", "C00153171")})
        self.assertTrue(all(r["candidateContributionsDollars"] == "12.34" for r in reports))

    def test_halfyear_requires_coverage_and_latest_source_versions(self):
        def row(start, end, most_recent="true"):
            return {"canonicalActorId": "a", "committeeId": "C00007450", "mostRecent": most_recent,
                "isAmended": "false", "periodStart": start, "periodEnd": end,
                "sourceRecordId": start, "candidateContributionsDollars": "12.34",
                "independentExpendituresDollars": "0.00", "totalDisbursementsDollars": "20.01"}
        first = row("2006-01-01", "2006-03-31")
        second = row("2006-04-01", "2006-06-30")
        result, excluded = PERIODS.prepare([first, second, {**first, "mostRecent": "false"}])
        self.assertEqual(excluded, 1)
        self.assertEqual(result[0]["candidateContributionsDollars"], "24.68")
        self.assertEqual(result[0]["eventClass"], "pre")
        for invalid in ([first], [first, first, second], [first, {**second,"candidateContributionsDollars":""}], [first, {**second,"candidateContributionsDollars":"NaN"}], [row("2006-06-01","2006-07-01")]):
            with self.assertRaises(ValueError):
                PERIODS.prepare(invalid)

    def test_missing_is_not_zero_and_cents_survive(self):
        self.assertEqual(FEC.amount(None), "")
        self.assertEqual(FEC.amount(0), "0.00")
        self.assertEqual(FEC.amount("5133.50"), "5133.50")
        with self.assertRaises(ValueError):
            FEC.amount("NaN")

    def test_period_not_ytd_and_nullable_amendments(self):
        record = {
            "committee_id": "C00007450", "report_year": 2006, "report_type": "YE",
            "file_number": 269683, "coverage_start_date": "2006-11-28T00:00:00",
            "coverage_end_date": "2006-12-31T00:00:00", "amendment_chain": None,
            "fed_candidate_committee_contributions_period": 5133.50,
            "fed_candidate_committee_contributions_ytd": 207983.50,
        }
        row = FEC.normalize(record, "actor", "2026-09-12")
        self.assertEqual(row["candidateContributionsDollars"], "5133.50")
        self.assertEqual(row["totalDisbursementsDollars"], "")
        self.assertEqual(row["amendmentChain"], "")
        self.assertEqual(row["periodStart"], "2006-11-28")
        record["file_number"] = None
        record["beginning_image_number"] = "28039750585"
        image_row = FEC.normalize(record, "actor", "2026-09-12")
        self.assertEqual(image_row["fileNumber"], "")
        self.assertEqual(image_row["sourceRecordId"], "image:28039750585")
        record["coverage_end_date"] = "2006-01-01"
        with self.assertRaises(ValueError):
            FEC.normalize(record, "actor", "2026-09-12")

    def test_design_candidate_has_no_treatment_assignment(self):
        rows = [{"exposureGroup": "treated_hloga_lda_client", "notes": "old"}]
        LDA.mark_design_candidates(rows)
        self.assertEqual(rows[0]["exposureGroup"], "unassigned_design_candidate")
        self.assertIn("treatment/control exposure unassigned", rows[0]["notes"])

    def test_api_counts_sum_years_once_not_pages(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        responses = [
            ({"count": 2, "results": [{"filing_uuid": "a"}], "next": "https://lda.gov/api/v1/filings/?page=2"}, ""),
            ({"count": 2, "results": [{"filing_uuid": "b"}], "next": None}, ""),
            ({"count": 3, "results": [{"filing_uuid": key} for key in ("c", "d", "e")], "next": None}, ""),
        ]
        with patch.object(LDA, "fetch_json", side_effect=responses):
            _, summary = LDA.fetch_actor_rows(actor, ["2004", "2005"], page_size=1,
                max_pages=3, timeout=1, review_date="2026-09-12", generated_at="2026-09-12")
        self.assertEqual(summary["apiResultCount"], "5")

    def test_lda_incomplete_or_malformed_page_cannot_be_a_zero_match(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        for payload in ({"count": 1, "results": [], "next": None}, {"detail": "unexpected error"}):
            with patch.object(LDA, "fetch_json", return_value=(payload, "")), self.assertRaises(ValueError):
                LDA.fetch_actor_rows(actor, ["2003"], page_size=100, max_pages=3,
                    timeout=1, review_date="2026-09-12", generated_at="2026-09-12")

    def test_lda_refuses_partial_acquisition(self):
        actor = {"primaryName": "ACTOR", "canonicalActorId": "actor"}
        cases = [
            [(None, "request failed")],
            [({"count": 2, "results": [], "next": "https://lda.gov/api/v1/filings/?page=2"}, "")],
        ]
        for responses in cases:
            with patch.object(LDA, "fetch_json", side_effect=responses):
                with self.assertRaisesRegex(RuntimeError, "refusing partial"):
                    LDA.fetch_actor_rows(actor, ["2003"], page_size=1,
                        max_pages=1, timeout=1, review_date="2026-09-12", generated_at="2026-09-12")


if __name__ == "__main__":
    unittest.main()
