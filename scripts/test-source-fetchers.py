#!/usr/bin/env python3
"""Exercise source-native JSON normalizers without network access."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "fixtures" / "source-native"


def main() -> int:
    fetchers = load_fetcher_module()
    assert_lda(fetchers)
    assert_fec(fetchers)
    assert_regulations(fetchers)
    assert_federal_register(fetchers)
    assert_usaspending(fetchers)
    assert_nyc_public_financing(fetchers)
    assert_nyc_intermediaries(fetchers)
    assert_irs_eo_bmf(fetchers)
    assert_irs_dark_money_capacity(fetchers)
    assert fetchers.redact_url("https://example.test/path?api_key=SECRET&x=1").endswith("api_key=REDACTED&x=1")
    print("Source-native parser fixture tests passed.")
    return 0


def load_fetcher_module():
    path = ROOT / "scripts" / "fetch-source-data.py"
    spec = importlib.util.spec_from_file_location("fetch_source_data", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_lda(fetchers) -> None:
    os.environ["LDA_DISCLOSURE_VISIBILITY_LAG"] = "0.32"
    payload = read_json("lda-filings.json")
    rows = fetchers.normalize_lda_records(payload["results"])
    assert rows == [
        {
            "client": "Example Platform Coalition",
            "registrant": "Example Advocacy LLC",
            "issueDomain": "technology",
            "amount": 3.0,
            "disclosureLag": 0.32,
            "coveredOfficialShare": 0.30,
        }
    ], rows


def assert_fec(fetchers) -> None:
    payload = read_json("fec-schedule-a.json")
    rows = fetchers.normalize_fec_contribution_records(payload["results"])
    assert rows[0] == {
        "source": "Clean Energy Executive",
        "recipient": "Clean Energy PAC",
        "issueDomain": "energy",
        "amount": 0.0075,
        "flowType": "PAC",
        "traceability": 0.78,
        "largeDonorShare": 0.38,
        "sourceRecordId": "",
        "sourceUrl": "",
        "committeeType": "recipient committee",
        "spendingPurpose": "contribution",
        "supportOppose": "",
        "disclosureLag": 0.28,
    }, rows[0]
    assert rows[1]["flowType"] == "SUPER_PAC", rows[1]
    assert rows[1]["issueDomain"] == "technology", rows[1]
    electioneering_payload = read_json("fec-electioneering.json")
    electioneering_rows = fetchers.normalize_fec_electioneering_records(electioneering_payload["results"])
    assert electioneering_rows == [
        {
            "source": "VOTE YES FOR A STRONG SOUTH DAKOTA",
            "recipient": "TRUMP, DONALD J.",
            "issueDomain": "democracy",
            "amount": 0.2525,
            "flowType": "ELECTIONEERING",
            "traceability": 0.50,
            "largeDonorShare": 0.74,
            "sourceRecordId": "4010820251127768002",
            "sourceUrl": "https://docquery.fec.gov/cgi-bin/fecimg/?202412139739894332",
            "committeeType": "electioneering communication",
            "spendingPurpose": "ADVERTISING PLACEMENT RELATED TO FOLLOW THE MONEY",
            "supportOppose": "G",
            "disclosureLag": 0.4383,
        }
    ], electioneering_rows
    communication_payload = read_json("fec-communication-costs.json")
    communication_rows = fetchers.normalize_fec_communication_cost_records(communication_payload["results"])
    assert communication_rows == [
        {
            "source": "CALIFORNIA LABOR FEDERATION, AFL-CIO",
            "recipient": "HARDER, JOSH",
            "issueDomain": "democracy",
            "amount": 0.0,
            "flowType": "COMMUNICATION_COST",
            "traceability": 0.64,
            "largeDonorShare": 0.66,
            "sourceRecordId": "F76020719518521",
            "sourceUrl": "https://docquery.fec.gov/pdf/185/201902050300265185/201902050300265185.pdf",
            "committeeType": "FOR EACH COMMUNICATION",
            "spendingPurpose": "MEMBERS",
            "supportOppose": "S",
            "disclosureLag": 0.7,
        }
    ], communication_rows


def assert_regulations(fetchers) -> None:
    payload = read_json("regulations-gov-documents.json")
    rows = fetchers.normalize_regulations_gov_payload(payload)
    assert rows == [
        {
            "docketId": "EPA-HQ-OAR-2026-0001",
            "issueDomain": "energy",
            "agency": "EPA",
            "commentVolume": 120,
            "genuineShare": 0.38,
            "templateShare": 0.46,
            "technicalClaimCredibility": 0.50,
            "authenticationShare": 0.32,
        }
    ], rows


def assert_federal_register(fetchers) -> None:
    payload = read_json("federal-register-documents.json")
    rows = fetchers.normalize_federal_register_payload(payload)
    assert rows == [
        {
            "docketId": "FR-2026-0001",
            "issueDomain": "finance",
            "agency": "securities-and-exchange-commission",
            "commentVolume": 120,
            "genuineShare": 0.38,
            "templateShare": 0.46,
            "technicalClaimCredibility": 0.50,
            "authenticationShare": 0.32,
        }
    ], rows


def assert_usaspending(fetchers) -> None:
    payload = read_json("usaspending-awards.json")
    transaction_payload = read_json("usaspending-transactions.json")
    os.environ["USASPENDING_ENRICH_AWARD_DETAILS"] = "0"
    os.environ["USASPENDING_ENRICH_TRANSACTIONS"] = "0"
    rows = fetchers.normalize_usaspending_records("", payload["results"])
    assert rows[0] == {
        "awardId": "EPW05049",
        "recipient": "CDM FEDERAL PROGRAMS CORPORATION",
        "agency": "Environmental Protection Agency",
        "subAgency": "Environmental Protection Agency",
        "awardType": "contract",
        "amount": 145.8637,
        "issueDomain": "procurement",
        "awardCount": 1,
        "uei": "",
        "piid": "EPW05049",
        "modificationNumber": "0",
        "actionDate": "",
        "competitionType": "unknown",
        "numberOfOffers": "0",
        "priceOnlyAward": "false",
        "exPostModification": "false",
        "protestFiled": "false",
        "exclusionFlag": "false",
        "firewallCovered": "false",
    }, rows[0]
    assert rows[1]["recipient"] == "LOCKHEED MARTIN SERVICES, LLC", rows[1]
    action_rows = fetchers.normalize_usaspending_transaction_records(payload["results"][0], {}, transaction_payload["results"])
    assert len(action_rows) == 2, action_rows
    assert action_rows[0]["modificationNumber"] == "0", action_rows[0]
    assert action_rows[0]["exPostModification"] == "false", action_rows[0]
    assert action_rows[1]["modificationNumber"] == "P00001", action_rows[1]
    assert action_rows[1]["exPostModification"] == "true", action_rows[1]
    assert action_rows[1]["amount"] == 25.0, action_rows[1]


def assert_nyc_public_financing(fetchers) -> None:
    payments = [
        {
            "ELECTION": "2025",
            "CANDID": "1001",
            "CANDNAME": "Example Reform Candidate",
            "TOTALPAY": "336498",
        }
    ]
    analysis = [
        {
            "CANDID": "1001",
            "net_cntns": "100000",
            "pubfnd_pmt": "336498",
            "max_amt": "2100",
        }
    ]
    rows = fetchers.normalize_nyc_public_financing_records(payments, analysis, "https://nyccfb.info/DataLibrary/2025_Payments.csv", "2025")
    assert rows == [
        {
            "source": "NYC Campaign Finance Board",
            "recipient": "Example Reform Candidate",
            "issueDomain": "democracy",
            "amount": 0.3365,
            "flowType": "PUBLIC_MATCH",
            "traceability": 0.96,
            "largeDonorShare": 0.0526,
            "sourceRecordId": "nyc-cfb-2025-1001",
            "sourceUrl": "https://nyccfb.info/DataLibrary/2025_Payments.csv",
            "committeeType": "municipal public matching funds",
            "spendingPurpose": "public funds payment",
            "supportOppose": "",
            "disclosureLag": 0.04,
        }
    ], rows


def assert_nyc_intermediaries(fetchers) -> None:
    records = [
        {
            "NAME": "Example Civic Intermediary",
            "AMNT": "2500",
            "CANDFIRST": "Ada",
            "CANDLAST": "Lovelace",
            "C_CODE": "IND",
        },
        {
            "NAME": "Example Civic Intermediary",
            "AMNT": "1500",
            "CANDFIRST": "Ada",
            "CANDLAST": "Lovelace",
            "C_CODE": "IND",
        },
    ]
    rows = fetchers.normalize_nyc_intermediary_records(records, "https://nyccfb.info/DataLibrary/2025_Intermediaries.csv")
    assert rows == [
        {
            "organization": "Example Civic Intermediary",
            "ein": "",
            "sourceType": "nyc-cfb-intermediary",
            "subsection": "campaign-intermediary",
            "issueDomain": "democracy",
            "revenue": 0.004,
            "politicalSpend": 0.004,
            "grantmaking": 0.0,
            "donorDisclosure": 0.72,
            "recipient": "Ada Lovelace",
            "sourceUrl": "https://nyccfb.info/DataLibrary/2025_Intermediaries.csv",
        }
    ], rows


def assert_irs_eo_bmf(fetchers) -> None:
    os.environ["IRS_EO_BMF_FILTERED_MAX_ROWS"] = "10"
    source_rows = [
        {
            "EIN": "123456789",
            "NAME": "Example Policy Association",
            "SUBSECTION": "06",
            "REVENUE_AMT": "2000000",
            "NTEE_CD": "",
            "FOUNDATION": "0",
            "_sourceUrl": "https://www.irs.gov/pub/irs-soi/eo_dc.csv",
        }
    ]
    rows = fetchers.normalize_irs_eo_bmf_records(source_rows)
    assert rows == [
        {
            "organization": "Example Policy Association",
            "ein": "123456789",
            "sourceType": "irs-eo-bmf-capacity",
            "subsection": "501(c)(6)",
            "issueDomain": "democracy",
            "revenue": 2.0,
            "politicalSpend": 0.036,
            "grantmaking": 0.008,
            "donorDisclosure": 0.32,
            "recipient": "",
            "sourceUrl": "https://www.irs.gov/pub/irs-soi/eo_dc.csv",
        }
    ], rows


def assert_irs_dark_money_capacity(fetchers) -> None:
    os.environ["IRS_EO_BMF_FILTERED_MAX_ROWS"] = "10"
    source_rows = [
        {
            "EIN": "987654321",
            "NAME": "Example Action Fund",
            "SUBSECTION": "04",
            "REVENUE_AMT": "5000000",
            "NTEE_CD": "",
            "_sourceUrl": "https://www.irs.gov/pub/irs-soi/eo_dc.csv",
        }
    ]
    rows = fetchers.normalize_irs_dark_money_capacity_records(source_rows)
    assert rows == [
        {
            "source": "Example Action Fund",
            "recipient": "Opaque issue-advocacy capacity",
            "issueDomain": "democracy",
            "amount": 0.06,
            "flowType": "DARK_MONEY",
            "traceability": 0.12,
            "largeDonorShare": 0.74,
            "sourceRecordId": "987654321",
            "sourceUrl": "https://www.irs.gov/pub/irs-soi/eo_dc.csv",
            "committeeType": "501(c)(4) capacity proxy",
            "spendingPurpose": "opaque nonprofit advocacy capacity proxy",
            "supportOppose": "",
            "disclosureLag": 0.55,
        }
    ], rows


def read_json(name: str):
    with (FIXTURES / name).open(encoding="utf-8") as source:
        return json.load(source)


if __name__ == "__main__":
    raise SystemExit(main())
