#!/usr/bin/env python3
"""Offline manifest, row-semantics and archive-isolation regression tests."""

import copy
import csv
from datetime import date
import importlib.util
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bulk_frame", ROOT / "scripts/audit-procurement-bulk-frame.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FrameTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(audit.MANIFEST.read_text())
        self.saved = json.loads(audit.PROFILE.read_text())
        self.row = json.loads((ROOT / "data/calibration/first-wave/procurement-bulk-type-review.json").read_text())["archive"]["row"]

    def validate(self):
        return audit.validate_profile(self.saved, self.manifest, audit.sha256(audit.MANIFEST))

    def profile(self, rows):
        return audit.profile_rows(rows, "Environmental Protection Agency", date(2023, 10, 1), date(2023, 12, 31))

    def test_committed_profile_and_leap_day(self):
        before = copy.deepcopy(self.saved)
        total = self.validate()
        self.assertEqual(total["rows"], 6449101)
        self.assertEqual(audit.check_manifest(self.manifest), 366)
        self.assertEqual(self.saved, before)

    def test_gap_and_overlap_rejected(self):
        for change in ("2023-12-30", "2024-01-01"):
            with self.subTest(change=change):
                self.manifest["strata"][0]["endDate"] = change
                with self.assertRaisesRegex(ValueError, "gap or overlap"):
                    audit.check_manifest(self.manifest)

    def test_duplicate_and_unsafe_paths_rejected(self):
        for path in (self.manifest["strata"][1]["downloadFile"], "../outside.zip", "/tmp/outside.zip"):
            self.manifest["strata"][0]["downloadFile"] = path
            with self.assertRaisesRegex(ValueError, "archive path"):
                audit.check_manifest(self.manifest)

    def test_manifest_counts_cannot_silently_drift(self):
        self.manifest["plannedTransactionRows"] += 1
        with self.assertRaisesRegex(ValueError, "aggregate counts"):
            audit.check_manifest(self.manifest)

    def test_blanks_zero_and_exclusion_procedure_stay_distinct(self):
        blank = dict(self.row, number_of_offers_received="", modification_number="")
        zero = dict(self.row, number_of_offers_received="0", extent_competed="FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES")
        result = self.profile([blank, zero])
        self.assertEqual((result["missingOffersRows"], result["zeroOffersRows"], result["missingModificationRows"]), (1, 1, 1))
        self.assertEqual(result["blankAwardTypeRows"], 2)
        self.assertEqual(result["childDescriptionRows"], 0)
        self.assertEqual(result["afterExclusionCompetitionRows"], 1)
        self.assertNotIn("historicalExclusionRows", result)

    def test_exact_cents_and_signed_actions(self):
        result = self.profile([dict(self.row, federal_action_obligation=value) for value in ("0.10", "0.20", "-0.10", "0.00")])
        self.assertEqual(result["netObligationDollars"], "0.20")
        self.assertEqual(result["absoluteObligationDollars"], "0.40")
        self.assertEqual(result["obligationSignRows"], {"negative": 1, "positive": 2, "zero": 1})

    def test_bad_money_shape_and_date_rejected(self):
        for field, value in (("federal_action_obligation", ""), ("federal_action_obligation", "NaN"), ("federal_action_obligation", "0.001"), ("number_of_offers_received", "-1"), ("action_date", "bad"), ("award_type", None)):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.profile([dict(self.row, **{field: value})])

    def test_outside_frame_is_counted_not_dropped(self):
        result = self.profile([dict(self.row, action_date="2024-01-01", awarding_agency_name="Wrong agency")])
        self.assertEqual((result["rows"], result["outsideDateRows"], result["wrongAgencyRows"]), (1, 1, 1))

    def test_archive_excludes_subawards_and_checks_hash(self):
        text = StringIO()
        writer = csv.DictWriter(text, audit.FIELDS)
        writer.writeheader()
        writer.writerow(self.row)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.zip"
            with zipfile.ZipFile(path, "w") as target:
                target.writestr("Contracts_PrimeTransactions_1.csv", text.getvalue())
                target.writestr("Contracts_Subawards.csv", "unrelated,invalid\n1,2\n")
            stratum = dict(self.manifest["strata"][0], normalizedRows="1", zipSha256=audit.sha256(path))
            result = audit.scan_archive(path, stratum)
            self.assertEqual(result["profile"]["rows"], 1)
            stratum["zipSha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "hash differs"):
                audit.scan_archive(path, stratum)

    def test_stale_profile_total_and_fingerprint_rejected(self):
        self.saved["total"]["rows"] += 1
        with self.assertRaisesRegex(ValueError, "total mismatch"):
            self.validate()
        self.saved["total"]["rows"] -= 1
        self.saved["profileFingerprint"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.validate()

    def test_category_and_money_changes_rejected(self):
        row = self.saved["strata"][0]["profile"]
        row["awardTypeRows"][""] = -1
        with self.assertRaisesRegex(ValueError, "category count"):
            self.validate()
        self.saved = json.loads(audit.PROFILE.read_text())
        self.saved["strata"][0]["profile"]["netObligationDollars"] = "NaN"
        with self.assertRaisesRegex(ValueError, "money partitions"):
            self.validate()

    def test_type_review_preserves_identity_and_pending_scope(self):
        review = json.loads(audit.TYPE_REVIEW.read_text())
        self.assertEqual(audit.validate_type_review(review, self.saved), "IDV_B_B")
        for field, value in (("piid", "WRONG"), ("category", "contract"), ("recipient_uei", "WRONG")):
            changed = copy.deepcopy(review)
            changed["awardDetail"]["projection"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "identity or scope"):
                audit.validate_type_review(changed, self.saved)
        review["independentReview"] = "complete"
        with self.assertRaisesRegex(ValueError, "identity or scope"):
            audit.validate_type_review(review, self.saved)

    def test_collector_semantics_match_documented_legacy_risks(self):
        spec = importlib.util.spec_from_file_location("collector", ROOT / "scripts/audit-usaspending-transaction-download-strata.py")
        collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(collector)
        raw = dict(self.row, number_of_offers_received="", extent_competed="FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES")
        normalized = collector.normalized_row(raw)
        self.assertEqual(normalized["numberOfOffers"], "0")
        self.assertEqual(normalized["awardType"], "contract")
        self.assertEqual(normalized["exclusionFlag"], "true")
        self.assertEqual((normalized["protestFiled"], normalized["firewallCovered"]), ("false", "false"))
        self.assertTrue(any(code.startswith("IDV_") for code in collector.CONTRACT_AWARD_TYPES))
        self.assertEqual(tuple(collector.DOWNLOAD_COLUMNS), audit.FIELDS)


if __name__ == "__main__":
    unittest.main()
