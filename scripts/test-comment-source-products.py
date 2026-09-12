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
