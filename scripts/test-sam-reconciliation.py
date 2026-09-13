#!/usr/bin/env python3
"""Synthetic SAM import regressions, not observations about real contract awards."""

import argparse
import copy
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FETCH = load("sam_reconciliation_fetch", "fetch-source-data.py")
AUDIT = load("sam_reconciliation_audit", "audit-sam-contract-awards-export.py")


def synthetic_record():
    return {
        "contractId": {"piid": "SYNTHETIC-ORDER", "subtier": {"code": "TEST"},
            "modificationNumber": "0", "transactionNumber": "0",
            "referencedIDVPiid": "SYNTHETIC-PARENT", "referencedIDVSubtier": {"code": "PARENT"}},
        "coreData": {"federalOrganization": {"contractingInformation": {
            "contractingDepartment": {"name": "SYNTHETIC AGENCY"}}}},
        "awardDetails": {
            "dates": {"dateSigned": "2024-05-31T00:00:00Z", "periodOfPerformanceStartDate": "2024-06-01"},
            "transactionData": {"approvedDate": "2024-06-03"},
            "dollars": {"actionObligation": "-12.34", "baseAndAllOptionsValue": "9999999"},
            "totalContractDollars": {"totalActionObligation": "111111"},
            "competitionInformation": {"numberOfOffersReceived": "4", "idvNumberOfOffersReceived": "6",
                "numberOfOffersSource": {"code": "F", "name": "This Action"},
                "extentCompeted": {"name": "FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES"}},
        },
    }


def normalize(record):
    return FETCH.normalize_sam_contract_award_records([record])[0]


class SamReconciliationTests(unittest.TestCase):
    def test_native_action_fields_take_precedence_without_mutation(self):
        record = synthetic_record()
        before = copy.deepcopy(record)
        row = normalize(record)
        self.assertEqual(record, before)
        self.assertEqual(row["actionDate"], "2024-05-31T00:00:00Z")
        self.assertEqual(row["actionDateSourcePath"], "awardDetails.dates.dateSigned")
        self.assertEqual(row["actionObligationDollars"], "-12.34")
        self.assertEqual(row["amount"], "-0.00001234")
        self.assertEqual(row["numberOfOffers"], "4")
        self.assertEqual(row["idvNumberOfOffersReceived"], "6")
        self.assertEqual(row["numberOfOffersSourceCode"], "F")
        self.assertEqual(row["numberOfOffersSourceName"], "This Action")

    def test_approval_performance_and_modified_dates_do_not_supply_action_date(self):
        record = synthetic_record()
        del record["awardDetails"]["dates"]["dateSigned"]
        record.update({"approvedDate": "2024-06-03", "Last Modified Date": "2026-09-13", "Award Date": "2024-06-01"})
        row = normalize(record)
        self.assertEqual(row["actionDate"], "")
        self.assertEqual(row["actionDateSourcePath"], "")
        self.assertEqual(AUDIT.raw_field_metrics(FETCH, [record])["rawActionDateCandidateShare"], 0)

    def test_totals_and_ceiling_do_not_supply_action_amount(self):
        record = synthetic_record()
        del record["awardDetails"]["dollars"]["actionObligation"]
        record.update({"Total Action Obligation": "111111", "totalDollarsObligated": "222222",
            "Current Total Value of Award": "333333"})
        row = normalize(record)
        self.assertEqual(row["amount"], "")
        self.assertEqual(row["actionObligationDollars"], "")
        self.assertEqual(AUDIT.raw_field_metrics(FETCH, [record])["rawAmountFieldShare"], 0)

    def test_missing_and_invalid_amounts_remain_distinct_from_explicit_zero(self):
        for value, expected in (("", ""), ("N/A", ""), ("NaN", ""), ("Infinity", ""),
                                ("0", "0"), ("0.01", "0.00000001"), ("-0.01", "-0.00000001")):
            with self.subTest(value=value):
                record = synthetic_record()
                record["awardDetails"]["dollars"]["actionObligation"] = value
                row = normalize(record)
                self.assertEqual(row["amount"], expected)
                self.assertEqual(AUDIT.export_metrics([row])["actionObligationShare"], int(expected != ""))

    def test_parent_offer_count_never_becomes_order_count(self):
        record = synthetic_record()
        del record["awardDetails"]["competitionInformation"]["numberOfOffersReceived"]
        row = normalize(record)
        self.assertEqual(row["numberOfOffers"], "")
        self.assertEqual(row["idvNumberOfOffersReceived"], "6")
        self.assertEqual(row["offersSourcePath"], "")

    def test_offers_remain_missing_when_provenance_is_available_without_count(self):
        record = synthetic_record()
        competition = record["awardDetails"]["competitionInformation"]
        del competition["numberOfOffersReceived"]
        competition["numberOfOffersSource"] = {"code": "B", "name": "IDC"}
        row = normalize(record)
        self.assertEqual(row["numberOfOffers"], "")
        self.assertEqual(row["numberOfOffersSourceCode"], "B")

    def test_explicit_zero_offers_is_observed_not_missing(self):
        self.assertEqual(AUDIT.known_offer_share([{"numberOfOffers": "0"}, {"numberOfOffers": ""}]), 0.5)
        self.assertEqual(AUDIT.known_offer_share([{"numberOfOffers": "-1"}, {"numberOfOffers": "1.5"}]), 0)

    def test_competition_exclusion_is_not_vendor_exclusion_evidence(self):
        row = normalize(synthetic_record())
        self.assertIn("EXCLUSION", row["competitionType"])
        self.assertEqual(row["exclusionFlag"], "false")
        self.assertEqual(row["exclusionEvidenceStatus"], "not_observed_in_contract_awards")

    def test_parent_competition_is_not_order_competition(self):
        record = synthetic_record()
        competition = record["awardDetails"]["competitionInformation"]
        del competition["extentCompeted"]
        competition["extentCompetedForReferencedIdv"] = {"name": "FULL AND OPEN COMPETITION"}
        self.assertEqual(normalize(record)["competitionType"], "unknown")

    def test_csv_aliases_do_not_reintroduce_forbidden_substitutions(self):
        raw = {"PIID": "SYNTHETIC-ORDER", "Approved Date": "2024-05-31",
            "Last Modified Date": "2024-09-30", "Total Action Obligation": "100",
            "Current Total Value of Award": "200", "IDV Number Of Offers Received": "6"}
        aliased = FETCH.sam_contract_awards_csv_record_aliases(raw)
        row = normalize(aliased)
        self.assertEqual((row["actionDate"], row["amount"], row["numberOfOffers"]), ("", "", ""))
        self.assertEqual(row["idvNumberOfOffersReceived"], "6")

    def test_missing_modification_is_not_an_observed_original_action(self):
        record = synthetic_record()
        del record["contractId"]["modificationNumber"]
        row = normalize(record)
        self.assertEqual(row["modificationNumber"], "")
        self.assertEqual(row["exPostModification"], "")

    def test_partial_key_cannot_collapse_distinct_transactions_or_parent_ids(self):
        records = [synthetic_record() for _ in range(3)]
        records[1]["contractId"]["transactionNumber"] = "1"
        records[2]["contractId"]["referencedIDVPiid"] = "ANOTHER-SYNTHETIC-PARENT"
        rows = FETCH.normalize_sam_contract_award_records(records + [copy.deepcopy(records[0])])
        self.assertEqual(len(FETCH.dedupe_usaspending_action_rows(rows)), 3)
        self.assertEqual(AUDIT.export_metrics(rows)["distinctAwardCount"], 2)

    def test_parsed_record_hash_is_order_independent_but_sensitive_to_source_changes(self):
        record = synthetic_record()
        reordered = dict(reversed(list(record.items())))
        self.assertEqual(normalize(record)["parsedRecordSha256"], normalize(reordered)["parsedRecordSha256"])
        reordered["additionalSourceField"] = "different revision"
        self.assertNotEqual(normalize(record)["parsedRecordSha256"], normalize(reordered)["parsedRecordSha256"])

    def test_csv_export_retains_cents_identity_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path, output = Path(tmp)/"source.json", Path(tmp)/"normalized.csv"
            input_path.write_text(json.dumps({"awardSummary": [synthetic_record()]}))
            FETCH.fetch_sam_contract_awards_export(input_path, output)
            with output.open() as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["amount"], "-0.00001234")
            self.assertEqual(row["actionObligationDollars"], "-12.34")
            self.assertEqual(row["transactionNumber"], "0")
            self.assertEqual(row["awardingSubtierCode"], "TEST")
            self.assertEqual(row["referencedIdvPiid"], "SYNTHETIC-PARENT")
            self.assertEqual(row["referencedIdvSubtierCode"], "PARENT")
            self.assertEqual(row["numberOfOffersSourceCode"], "F")

    def test_export_screen_blocks_missing_action_obligations_even_with_complete_totals(self):
        record = synthetic_record()
        del record["awardDetails"]["dollars"]["actionObligation"]
        metrics = AUDIT.export_metrics([normalize(record)])
        metrics.update(AUDIT.raw_field_metrics(FETCH, [record]))
        args = argparse.Namespace(min_rows=1, min_awards=1, min_agencies=1, min_date_span_days=0,
            min_piid_share=0, min_uei_share=0, min_action_date_share=0, min_competition_share=0)
        checks = {row["item"]:row for row in AUDIT.checklist_rows(args, metrics)}
        self.assertEqual(checks["promotion-readiness"]["status"], "blocked")
        self.assertEqual(checks["action-obligation-coverage"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
