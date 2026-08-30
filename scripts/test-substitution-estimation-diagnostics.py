#!/usr/bin/env python3
"""Focused tests for the no-claim substitution diagnostic estimator."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).with_name("estimate-substitution-diagnostics.py")
SPEC = importlib.util.spec_from_file_location("substitution_diagnostics", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not import {SCRIPT}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

PACKET_SCRIPT = Path(__file__).with_name("write-substitution-causal-upgrade-packet.py")
PACKET_SPEC = importlib.util.spec_from_file_location(
    "substitution_causal_upgrade_packet",
    PACKET_SCRIPT,
)
if PACKET_SPEC is None or PACKET_SPEC.loader is None:
    raise RuntimeError(f"Could not import {PACKET_SCRIPT}")
PACKET_MODULE = importlib.util.module_from_spec(PACKET_SPEC)
sys.modules[PACKET_SPEC.name] = PACKET_MODULE
PACKET_SPEC.loader.exec_module(PACKET_MODULE)


PERIODS = (
    ("2007", "mid_year", "2007-01-01", "2007-06-30"),
    ("2007", "year_end", "2007-07-01", "2007-12-31"),
    ("2008", "first_quarter", "2008-01-01", "2008-03-31"),
    ("2008", "second_quarter", "2008-04-01", "2008-06-30"),
    ("2008", "third_quarter", "2008-07-01", "2008-09-30"),
    ("2008", "fourth_quarter", "2008-10-01", "2008-12-31"),
)

CONTROL_DATES = (
    "2007-02-15",
    "2007-05-15",
    "2007-08-15",
    "2007-11-15",
    "2008-02-15",
    "2008-05-15",
    "2008-08-15",
    "2008-11-15",
)


class SubstitutionDiagnosticsTests(unittest.TestCase):
    def test_optional_historical_diagnostics_do_not_change_reproducible_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reports = Path(temp_dir) / "reports"
            reports.mkdir()
            (reports / "substitution-historical-source-access.csv").write_text(
                "item,status,coverageRole,observedCount\n"
                "accepted-actor-lda-api-probe,prepost_probe_observed,,\n"
                "lda-api-period-count,observed,pre_hloga,12\n",
                encoding="utf-8",
            )
            with (
                mock.patch.object(PACKET_MODULE, "REPORTS", reports),
                mock.patch.dict(
                    os.environ,
                    {PACKET_MODULE.OPTIONAL_HISTORICAL_DIAGNOSTICS_ENV: ""},
                ),
            ):
                reproducible = PACKET_MODULE.historical_source_access_summary()
            self.assertEqual(
                "not run; optional live diagnostic target is "
                "`make substitution-historical-source-access`.",
                reproducible,
            )

            with (
                mock.patch.object(PACKET_MODULE, "REPORTS", reports),
                mock.patch.dict(
                    os.environ,
                    {PACKET_MODULE.OPTIONAL_HISTORICAL_DIAGNOSTICS_ENV: "1"},
                ),
            ):
                optional = PACKET_MODULE.historical_source_access_summary()
            self.assertIn("ran optional live diagnostic", optional)
            self.assertIn("pre-HLOGA rows=12", optional)

    def test_preparation_and_requested_diagnostics(self) -> None:
        lda_rows = []
        for actor_index in range(2):
            actor = f"treated-{actor_index}"
            for period_index, (year, period, start, end) in enumerate(PERIODS):
                lda_rows.append(
                    lda_row(
                        actor,
                        f"{actor}-{period}",
                        year,
                        period,
                        start,
                        end,
                        amount=0.10 + actor_index * 0.02 + period_index * 0.01,
                    )
                )

        duplicate_issue = dict(lda_rows[0])
        duplicate_issue["issueCode"] = "lda-second-issue"
        duplicate_issue["sourceRecordId"] = duplicate_issue["filingUuid"] + "|lda-second-issue|2"
        lda_rows.append(duplicate_issue)

        amendment = dict(lda_rows[2])
        amendment["filingUuid"] = "treated-0-first-quarter-amendment"
        amendment["filingType"] = "1A"
        amendment["dtPosted"] = "2008-07-10T12:00:00-04:00"
        amendment["activityAmount"] = "0.2500"
        amendment["sourceRecordId"] = amendment["filingUuid"] + "|lda-test|1"
        lda_rows.append(amendment)

        registration = dict(lda_rows[2])
        registration["filingUuid"] = "treated-0-registration"
        registration["filingType"] = "RR"
        registration["activityAmount"] = "0.0000"
        registration["sourceRecordId"] = registration["filingUuid"] + "|lda-test|1"
        lda_rows.append(registration)

        control_rows = []
        for actor_index in range(3):
            actor = f"control-{actor_index}"
            for date_index, source_date in enumerate(CONTROL_DATES):
                control_rows.append(
                    control_row(
                        actor,
                        source_date,
                        amount=5_000 + actor_index * 100 + date_index * 10,
                    )
                )
        control_rows.append(dict(control_rows[0]))

        panel_rows, preparation = MODULE.prepare_panel(lda_rows, control_rows)
        self.assertEqual(40, len(panel_rows))
        self.assertEqual(15, preparation["ldaInputRows"])
        self.assertEqual(14, preparation["ldaUniqueFilingUuids"])
        self.assertEqual(1, preparation["ldaIssueRowsCollapsed"])
        self.assertEqual(1, preparation["ldaRegistrationFilingsExcluded"])
        self.assertEqual(1, preparation["ldaSupersededFilingsExcluded"])
        self.assertEqual(12, preparation["ldaSelectedFilings"])
        self.assertEqual(25, preparation["controlInputRows"])
        self.assertEqual(1, preparation["controlRepeatedReceiptRowsExcluded"])
        self.assertEqual(1, preparation["controlRepeatedReceiptKeyGroups"])
        self.assertEqual(0, preparation["controlReportMetadataConflictGroups"])
        self.assertEqual(24, preparation["controlSelectedTransactions"])
        self.assertEqual(2, preparation["treatedIssueCodeCount"])
        self.assertEqual(1, preparation["controlIssueCodeCount"])
        self.assertEqual(0, preparation["sharedIssueCodeCount"])

        diagnostics, event_rows, leave_rows, estimates = MODULE.analyze_panel(
            panel_rows,
            preparation,
            {
                "generatedAt": "2026-06-19T00:00:00Z",
                "releaseTag": "fixture",
                "releaseDate": "2026-06-19",
            },
            bootstrap_reps=100,
            seed=1234,
        )
        families = {row["diagnosticFamily"] for row in diagnostics}
        self.assertTrue(
            {
                "estimate",
                "pretrend",
                "placebo",
                "window_sensitivity",
                "leave_one_actor",
                "overall",
            }.issubset(families)
        )
        rows_by_id = {row["diagnosticId"]: row for row in diagnostics}
        self.assertEqual(
            MODULE.OVERALL_NOT_CLEARED,
            rows_by_id["overall_effect_model_and_falsification_gate"]["status"],
        )
        self.assertEqual(
            "fail",
            rows_by_id["treatment_source_system_separation"]["gateResult"],
        )
        self.assertEqual(
            "not_testable_as_trend",
            rows_by_id["single_interval_pretrend_check"]["status"],
        )
        self.assertIn(
            "treatedIssueCodes=2; controlIssueCodes=1; sharedIssueCodes=0",
            rows_by_id["actor_issue_unit_comparability"]["evidence"],
        )
        self.assertEqual(8, len(event_rows))
        self.assertEqual(5, len(leave_rows))
        self.assertIn("primary_actor_quarter_did", estimates)

        with tempfile.TemporaryDirectory() as temp_dir:
            figure = Path(temp_dir) / "diagnostic.svg"
            MODULE.write_specification_figure(figure, estimates)
            text = figure.read_text(encoding="utf-8")
            self.assertIn("<svg", text)
            self.assertIn("HLOGA diagnostic specification contrasts", text)
            self.assertIn("diagnostic values are not causal effects", text)


def lda_row(
    actor: str,
    filing_uuid: str,
    year: str,
    period: str,
    start: str,
    end: str,
    *,
    amount: float,
) -> dict[str, str]:
    filing_type = {
        "mid_year": "MM",
        "year_end": "YY",
        "first_quarter": "Q1",
        "second_quarter": "Q2",
        "third_quarter": "Q3",
        "fourth_quarter": "Q4",
    }[period]
    return {
        "canonicalActorId": actor,
        "primaryName": actor.upper(),
        "ldaClientId": actor + "-client",
        "filingUuid": filing_uuid,
        "filingYear": year,
        "filingPeriod": period,
        "filingType": filing_type,
        "dtPosted": f"{year}-12-01T12:00:00-05:00",
        "registrantName": actor.upper() + " REGISTRANT",
        "issueCode": "lda-test",
        "periodStart": start,
        "periodEnd": end,
        "activityAmount": f"{amount:.4f}",
        "sourceSystem": "Official LDA API",
        "sourceRecordId": filing_uuid + "|lda-test|1",
    }


def control_row(actor: str, source_date: str, *, amount: float) -> dict[str, str]:
    amount_millions = amount / 1_000_000.0
    return {
        "canonicalActorId": actor,
        "primaryName": actor.upper(),
        "stateClientKey": actor.upper(),
        "stateClientName": actor.upper(),
        "lobbyistName": actor.upper() + " LOBBYIST",
        "primaryLobbyistId": actor + "-lobbyist",
        "annualLobbyistRegistrationId": actor + "-registration",
        "sourceDate": source_date,
        "periodStart": source_date,
        "issueCode": "co-state-test",
        "activityMeasure": f"{amount:.4f}",
        "activityAmount": f"{amount_millions:.8f}",
        "sourceSystem": "Colorado Secretary of State lobbyist income data",
        "sourceRecordId": actor + "|" + source_date,
    }


if __name__ == "__main__":
    unittest.main()
