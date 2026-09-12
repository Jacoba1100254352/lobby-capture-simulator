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


if __name__ == "__main__":
    unittest.main()
