#!/usr/bin/env python3
"""Keep new source acquisitions distinct from identified substitution estimates."""

import importlib.util
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


class SourceExpansionTests(unittest.TestCase):
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
            ({"count": 2, "results": [], "next": "https://lda.gov/api/v1/filings/?page=2"}, ""),
            ({"count": 2, "results": [], "next": None}, ""),
            ({"count": 3, "results": [], "next": None}, ""),
        ]
        with patch.object(LDA, "fetch_json", side_effect=responses):
            _, summary = LDA.fetch_actor_rows(actor, ["2004", "2005"], page_size=1,
                max_pages=3, timeout=1, review_date="2026-09-12", generated_at="2026-09-12")
        self.assertEqual(summary["apiResultCount"], "5")

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
