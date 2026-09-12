#!/usr/bin/env python3
"""Offline regressions for lossless comment normalization and cohort refresh."""

import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "comment_products", Path(__file__).with_name("build-first-wave-comment-products.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


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
