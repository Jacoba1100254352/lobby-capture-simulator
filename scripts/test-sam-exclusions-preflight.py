#!/usr/bin/env python3
"""Offline acquisition regressions using synthetic SAM Exclusions v4 responses."""

import argparse
import copy
from email.message import Message
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sam_exclusions_probe", ROOT / "scripts/probe-sam-exclusions.py")
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def synthetic_entity():
    # Field structure follows the public GSA v4 example; every value is synthetic.
    return {
        "exclusionDetails": {
            "classificationType": "Firm", "exclusionType": "SYNTHETIC TYPE",
            "exclusionProgram": "SYNTHETIC PROGRAM",
            "excludingAgencyName": "SYNTHETIC AGENCY", "excludingAgencyCode": "TEST",
        },
        "exclusionIdentification": {"ueiSAM": "SYNTHETIC001", "entityName": "SYNTHETIC PRIMARY | ENTITY"},
        "exclusionActions": {"listOfActions": [
            {"createDate": "01-04-2024", "updateDate": "02-05-2024", "activateDate": "01-02-2024",
             "terminationDate": None, "terminationType": "Indefinite", "recordStatus": "Active"},
            {"createDate": "03-04-2024", "updateDate": "04-05-2024", "activateDate": "03-02-2024",
             "terminationDate": "12-31-2024", "terminationType": "Definite", "recordStatus": "Active"},
        ]},
        "exclusionOtherInformation": {
            "references": {"referencesList": [{"exclusionName": "SYNTHETIC REFERENCE", "type": "Cross-Reference"}]},
            "moreLocations": [{"ueiSAM": "SYNTHETIC002", "exclusionName": "SYNTHETIC OTHER LOCATION"}],
        },
    }


def preflight(payload):
    response = io.BytesIO(json.dumps(payload).encode())
    response.headers = Message()
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    args = argparse.Namespace(base_url="", query="", page=0, page_size=1, timeout_seconds=1)
    with patch.object(PROBE, "urlopen", return_value=response) as request:
        result = PROBE.run_preflight(args, {"SAM_API_KEY": "SYNTHETIC-TEST-ONLY"})
    assert request.call_count == 1
    return result


class SamExclusionsPreflightTests(unittest.TestCase):
    def test_native_response_is_decoded_as_entities_not_empty(self):
        entity = synthetic_entity()
        payload = {"totalRecords": 99, "excludedEntity": [entity]}
        before = copy.deepcopy(payload)
        row, samples = preflight(payload)
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["records"], "1")  # Page count, not totalRecords or action count.
        self.assertEqual(len(samples), 1)
        self.assertEqual(payload, before)
        self.assertIn("REDACTED", row["endpoint"])
        self.assertNotIn("SYNTHETIC-TEST-ONLY", json.dumps(row))

    def test_unknown_or_malformed_response_is_not_an_observed_empty_page(self):
        for payload in ({}, {"message": "upstream error"}, {"results": []}, [],
                        {"excludedEntity": None}, {"excludedEntity": {}},
                        {"excludedEntity": [None]},
                        {"metadata": {"records": [synthetic_entity()]}}):
            with self.subTest(payload=payload):
                row, samples = preflight(payload)
                self.assertEqual(row["status"], "unavailable")
                self.assertIn("response shape", row["notes"])
                self.assertEqual(samples, [])

    def test_native_empty_page_does_not_fall_through_to_unrelated_records(self):
        row, samples = preflight({"totalRecords": 0, "excludedEntity": [],
                                  "metadata": {"records": [synthetic_entity()]}})
        self.assertEqual(row["status"], "empty")
        self.assertEqual(row["records"], "0")
        self.assertEqual(samples, [])

    def test_primary_fields_use_their_native_sections(self):
        entity = synthetic_entity()
        sample = PROBE.sample_record(entity)
        self.assertEqual(sample["uei"], "SYNTHETIC001")
        self.assertEqual(sample["recipientName"], "SYNTHETIC PRIMARY | ENTITY")
        self.assertEqual(sample["classificationType"], "Firm")
        self.assertEqual(sample["exclusionType"], "SYNTHETIC TYPE")
        self.assertEqual(sample["exclusionProgram"], "SYNTHETIC PROGRAM")
        self.assertEqual(sample["agency"], "SYNTHETIC AGENCY")
        self.assertEqual(sample["exclusionId"], "")
        del entity["exclusionIdentification"]["ueiSAM"]
        del entity["exclusionDetails"]["exclusionType"]
        sample = PROBE.sample_record(entity)
        self.assertEqual(sample["uei"], "")  # A different location's UEI cannot fill it.
        self.assertEqual(sample["exclusionType"], "")  # Firm is classification, not exclusion type.

    def test_action_history_preserves_each_action_and_missing_termination(self):
        entity = synthetic_entity()
        before = copy.deepcopy(entity)
        actions = PROBE.sample_record(entity)["actions"]
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["activateDate"], "01-02-2024")
        self.assertEqual(actions[0]["createDate"], "01-04-2024")
        self.assertEqual(actions[0]["updateDate"], "02-05-2024")
        self.assertEqual(actions[0]["terminationDate"], "")
        self.assertEqual(actions[0]["terminationType"], "Indefinite")
        self.assertEqual(actions[1]["activateDate"], "03-02-2024")
        self.assertEqual(actions[1]["terminationDate"], "12-31-2024")
        self.assertEqual(entity, before)

    def test_unreturned_actions_and_activation_are_not_filled_from_other_dates(self):
        entity = synthetic_entity()
        del entity["exclusionActions"]["listOfActions"][0]["activateDate"]
        self.assertEqual(PROBE.sample_record(entity)["actions"][0]["activateDate"], "")
        del entity["exclusionActions"]
        entity["startDate"] = "SYNTHETIC UNRELATED DATE"
        sample = PROBE.sample_record(entity)
        self.assertEqual(sample["actions"], [])
        row, samples = preflight({"excludedEntity": [entity]})
        self.assertEqual(row["status"], "ok")  # includeSections may omit action information.
        self.assertEqual(samples[0]["actions"], [])

    def test_malformed_native_sections_are_unavailable(self):
        for section, value in (("exclusionDetails", []), ("exclusionIdentification", "bad"),
                               ("exclusionActions", []), ("exclusionActions", {"listOfActions": {}}),
                               ("exclusionActions", {"listOfActions": [None]})):
            entity = synthetic_entity()
            entity[section] = value
            with self.subTest(section=section, value=value):
                row, samples = preflight({"excludedEntity": [entity]})
                self.assertEqual(row["status"], "unavailable")
                self.assertEqual(samples, [])

    def test_page_validation_covers_entities_beyond_the_display_sample(self):
        entities = [synthetic_entity() for _ in range(6)]
        row, samples = preflight({"excludedEntity": entities})
        self.assertEqual(row["records"], "6")
        self.assertEqual(len(samples), 5)
        entities[-1]["exclusionIdentification"]["ueiSAM"] = {"unexpected": "object"}
        row, samples = preflight({"excludedEntity": entities})
        self.assertEqual(row["status"], "unavailable")
        self.assertEqual(samples, [])

    def test_markdown_keeps_action_rows_separate_and_explains_historical_limit(self):
        row, samples = preflight({"excludedEntity": [synthetic_entity()]})
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "preflight.md"
            PROBE.write_markdown(output, row, samples)
            content = output.read_text()
        self.assertIn("SYNTHETIC PRIMARY \\| ENTITY", content)
        self.assertIn("| 1 | 1 | 01-04-2024 | 02-05-2024 | 01-02-2024 |  | Indefinite | Active |", content)
        self.assertIn("| 1 | 2 | 03-04-2024 | 04-05-2024 | 03-02-2024 | 12-31-2024 | Definite | Active |", content)
        self.assertIn("only active records", content)
        self.assertIn("not historical exclusion intervals", content)
        self.assertNotIn("SYNTHETIC OTHER LOCATION", content)


if __name__ == "__main__":
    unittest.main()
