#!/usr/bin/env python3
"""Exercise source-native JSON normalizers without network access."""

from __future__ import annotations

import importlib.util
import gzip
import json
import os
from pathlib import Path
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "fixtures" / "source-native"


def main() -> int:
    fetchers = load_fetcher_module()
    assert_lda(fetchers)
    assert_fec(fetchers)
    assert_regulations(fetchers)
    assert_federal_register(fetchers)
    assert_usaspending(fetchers)
    assert_sam_contract_awards(fetchers)
    assert_nyc_public_financing(fetchers)
    assert_seattle_democracy_vouchers(fetchers)
    assert_nyc_intermediaries(fetchers)
    assert_irs_eo_bmf(fetchers)
    assert_irs_dark_money_capacity(fetchers)
    assert_propublica_nonprofit_routing(fetchers)
    assert_irs_527(fetchers)
    assert_curl_fallback_toggle(fetchers)
    redacted = fetchers.redact_url("https://example.test/path?api_key=SECRET&token=TEMP&x=1")
    assert redacted.endswith("api_key=REDACTED&token=REDACTED&x=1"), redacted
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
    direct_action_rows = fetchers.normalize_usaspending_direct_transaction_records(transaction_payload["results"])
    assert len(direct_action_rows) == 2, direct_action_rows
    assert direct_action_rows[0]["awardId"] == "EPW05049", direct_action_rows[0]
    assert direct_action_rows[0]["piid"] == "EPW05049", direct_action_rows[0]
    assert direct_action_rows[1]["modificationNumber"] == "P00001", direct_action_rows[1]
    assert direct_action_rows[1]["exPostModification"] == "true", direct_action_rows[1]
    os.environ["USASPENDING_DATE_FROM"] = "2024-01-15"
    os.environ["USASPENDING_DATE_TO"] = "2024-03-05"
    os.environ["USASPENDING_ACTION_PERIOD_BUCKETS"] = "monthly"
    assert fetchers.usaspending_action_periods() == [
        ("2024-01-15", "2024-01-31"),
        ("2024-02-01", "2024-02-29"),
        ("2024-03-01", "2024-03-05"),
    ]
    os.environ.pop("USASPENDING_ACTION_PERIOD_BUCKETS", None)
    os.environ["USASPENDING_PROCUREMENT_ACTIONS_PERIOD_BUCKETS"] = "monthly"
    assert fetchers.usaspending_action_periods() == [
        ("2024-01-15", "2024-01-31"),
        ("2024-02-01", "2024-02-29"),
        ("2024-03-01", "2024-03-05"),
    ]
    os.environ.pop("USASPENDING_PROCUREMENT_ACTIONS_PERIOD_BUCKETS", None)
    os.environ["USASPENDING_ACTION_PERIOD_BUCKETS"] = "quarterly"
    assert fetchers.usaspending_action_periods() == [
        ("2024-01-15", "2024-03-05"),
    ]
    os.environ["USASPENDING_DATE_FROM"] = "2024-02-15"
    os.environ["USASPENDING_DATE_TO"] = "2024-08-05"
    assert fetchers.usaspending_action_periods() == [
        ("2024-02-15", "2024-03-31"),
        ("2024-04-01", "2024-06-30"),
        ("2024-07-01", "2024-08-05"),
    ]
    os.environ["USASPENDING_ACTION_PERIOD_BUCKETS"] = "annual"
    assert fetchers.usaspending_action_periods() == [
        ("2024-02-15", "2024-08-05"),
    ]
    os.environ["USASPENDING_ACTION_PERIOD_BUCKETS"] = "weekly"
    try:
        fetchers.usaspending_action_periods()
    except SystemExit as exc:
        assert "USASPENDING_ACTION_PERIOD_BUCKETS" in str(exc), exc
    else:
        raise AssertionError("invalid USAspending action period bucket did not fail")
    os.environ["USASPENDING_ACTION_TRANSACTION_SORT_SPECS"] = "Mod:asc; Transaction Amount:desc; Action Date:sideways"
    os.environ["USASPENDING_ACTION_TRANSACTION_ORDER"] = "asc"
    assert fetchers.usaspending_action_transaction_sort_specs() == [
        ("Mod", "asc"),
        ("Transaction Amount", "desc"),
        ("Action Date", "asc"),
    ]
    os.environ.pop("USASPENDING_ACTION_TRANSACTION_SORT_SPECS", None)
    os.environ.pop("USASPENDING_ACTION_TRANSACTION_ORDER", None)
    os.environ["USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_SORT_SPECS"] = "Mod:asc; Transaction Amount:desc"
    os.environ["USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_ORDER"] = "desc"
    assert fetchers.usaspending_action_transaction_sort_specs() == [
        ("Mod", "asc"),
        ("Transaction Amount", "desc"),
    ]
    os.environ["USASPENDING_PROCUREMENT_ACTIONS_AGENCIES"] = "Environmental Protection Agency,Department of Energy"
    os.environ.pop("USASPENDING_AGENCIES", None)
    assert [agency["name"] for agency in fetchers.usaspending_agency_filters()] == [
        "Environmental Protection Agency",
    ]
    assert [agency["name"] for agency in fetchers.usaspending_agency_filters(allow_procurement_actions_alias=True)] == [
        "Environmental Protection Agency",
        "Department of Energy",
    ]
    os.environ["USASPENDING_AGENCIES"] = "ALL"
    assert fetchers.usaspending_agency_filters() == [{}]
    assert "agencies" not in fetchers.usaspending_filters("2023-10-01", "2024-09-30", {})
    os.environ.pop("USASPENDING_AGENCIES", None)
    os.environ["USASPENDING_PROCUREMENT_ACTIONS_AGENCIES"] = "ALL"
    assert fetchers.usaspending_agency_filters(allow_procurement_actions_alias=True) == [{}]
    for name in (
        "USASPENDING_DATE_FROM",
        "USASPENDING_DATE_TO",
        "USASPENDING_ACTION_PERIOD_BUCKETS",
        "USASPENDING_PROCUREMENT_ACTIONS_PERIOD_BUCKETS",
        "USASPENDING_ACTION_TRANSACTION_SORT_SPECS",
        "USASPENDING_ACTION_TRANSACTION_ORDER",
        "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_SORT_SPECS",
        "USASPENDING_PROCUREMENT_ACTIONS_TRANSACTION_ORDER",
        "USASPENDING_PROCUREMENT_ACTIONS_AGENCIES",
        "USASPENDING_AGENCIES",
    ):
        os.environ.pop(name, None)


def assert_sam_contract_awards(fetchers) -> None:
    payload = read_json("sam-contract-awards.json")
    records = fetchers.sam_contract_award_records(payload)
    assert len(records) == 2, records
    assert fetchers.sam_contract_awards_total_records(payload) == 2
    assert fetchers.sam_contract_awards_offset(0, 0, 100) == 0
    assert fetchers.sam_contract_awards_offset(0, 1, 100) == 1
    assert fetchers.sam_contract_awards_offset(10, 2, 25) == 12
    os.environ.pop("SAM_CONTRACT_AWARDS_OFFSET_STARTS", None)
    os.environ.pop("SAM_CONTRACT_AWARDS_OFFSET_START", None)
    assert fetchers.sam_contract_awards_offset_starts() == [0]
    os.environ["SAM_CONTRACT_AWARDS_OFFSET_START"] = "200"
    assert fetchers.sam_contract_awards_offset_starts() == [200]
    assert fetchers.sam_contract_awards_offsets(2, 50) == [200, 201]
    os.environ["SAM_CONTRACT_AWARDS_OFFSET_STARTS"] = "10,0,10,50"
    assert fetchers.sam_contract_awards_offset_starts() == [0, 10, 50]
    assert fetchers.sam_contract_awards_offsets(2, 100) == [0, 1, 10, 11, 50, 51]
    os.environ["SAM_CONTRACT_AWARDS_OFFSET_STARTS"] = "5000"
    try:
        fetchers.sam_contract_awards_offsets(1, 100)
    except SystemExit as exc:
        assert "offset * limit" in str(exc), exc
    else:
        raise AssertionError("SAM offset page index beyond the 400000-row window did not fail")
    os.environ["SAM_CONTRACT_AWARDS_OFFSET_STARTS"] = "bad"
    try:
        fetchers.sam_contract_awards_offset_starts()
    except SystemExit as exc:
        assert "SAM_CONTRACT_AWARDS_OFFSET_STARTS" in str(exc), exc
    else:
        raise AssertionError("invalid SAM offset starts did not fail")
    os.environ.pop("SAM_CONTRACT_AWARDS_OFFSET_STARTS", None)
    os.environ.pop("SAM_CONTRACT_AWARDS_OFFSET_START", None)
    for name in (
        "SAM_CONTRACT_AWARDS_PIID_SUBTIER_CODES",
        "SAM_CONTRACT_AWARDS_PIID_SUBTIER_NAMES",
        "SAM_CONTRACT_AWARDS_DEPARTMENT_CODES",
        "SAM_CONTRACT_AWARDS_AGENCIES",
        "USASPENDING_PROCUREMENT_ACTIONS_AGENCIES",
        "USASPENDING_AGENCIES",
        "USASPENDING_AGENCY",
    ):
        os.environ.pop(name, None)
    os.environ["SAM_CONTRACT_AWARDS_PIID_SUBTIER_CODES"] = "8000,4732"
    assert fetchers.sam_contract_awards_filters() == [("piidSubtierCode", "8000"), ("piidSubtierCode", "4732")]
    os.environ.pop("SAM_CONTRACT_AWARDS_PIID_SUBTIER_CODES", None)
    os.environ["SAM_CONTRACT_AWARDS_PIID_SUBTIER_NAMES"] = "NASA,Public Buildings Service"
    assert fetchers.sam_contract_awards_filters() == [
        ("piidSubtierName", "NASA"),
        ("piidSubtierName", "Public Buildings Service"),
    ]
    os.environ.pop("SAM_CONTRACT_AWARDS_PIID_SUBTIER_NAMES", None)
    os.environ["SAM_CONTRACT_AWARDS_DEPARTMENT_CODES"] = "9700,4700"
    assert fetchers.sam_contract_awards_filters() == [
        ("contractingDepartmentCode", "9700"),
        ("contractingDepartmentCode", "4700"),
    ]
    os.environ.pop("SAM_CONTRACT_AWARDS_DEPARTMENT_CODES", None)
    os.environ["SAM_CONTRACT_AWARDS_AGENCIES"] = "General Services Administration"
    assert fetchers.sam_contract_awards_filters() == [("contractingDepartmentName", "General Services Administration")]
    os.environ.pop("SAM_CONTRACT_AWARDS_AGENCIES", None)
    for name in (
        "SAM_CONTRACT_AWARDS_EXTRACT_MODE",
        "SAM_CONTRACT_AWARDS_EXTRACT_FORMAT",
        "SAM_CONTRACT_AWARDS_FORMAT",
        "SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID",
    ):
        os.environ.pop(name, None)
    assert fetchers.sam_contract_awards_extract_mode() is False
    os.environ["SAM_CONTRACT_AWARDS_EXTRACT_MODE"] = "1"
    assert fetchers.sam_contract_awards_extract_mode() is True
    assert fetchers.sam_contract_awards_extract_format() == "json"
    default_params = fetchers.sam_contract_awards_extract_params("KEY", "json")
    assert default_params["emailId"] == "Yes", default_params
    os.environ["SAM_CONTRACT_AWARDS_EXTRACT_FORMAT"] = "csv"
    os.environ["SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID"] = "yes"
    os.environ["SAM_CONTRACT_AWARDS_MODIFICATION_NUMBER"] = "0"
    params = fetchers.sam_contract_awards_extract_params("KEY", "csv")
    assert params["api_key"] == "KEY", params
    assert params["format"] == "csv", params
    assert params["emailId"] == "yes", params
    assert params["modificationNumber"] == "0", params
    assert "limit" not in params, params
    token_payload = read_json("sam-contract-awards-extract-token.json")
    download_url = fetchers.sam_contract_awards_download_url(token_payload, "KEY WITH SPACE")
    assert "REPLACE_WITH_API_KEY" not in download_url, download_url
    assert "KEY+WITH+SPACE" in download_url, download_url
    emailed_url = "https://api.sam.gov/contract-awards/v1/download?api_key=REPLACE_WITH_API_KEY&token=abc123"
    resolved_emailed_url = fetchers.sam_contract_awards_resolved_download_url(emailed_url, "KEY WITH SPACE")
    assert "REPLACE_WITH_API_KEY" not in resolved_emailed_url, resolved_emailed_url
    assert "KEY+WITH+SPACE" in resolved_emailed_url, resolved_emailed_url
    assert "token=abc123" in resolved_emailed_url, resolved_emailed_url
    os.environ.pop("SAM_API_KEY", None)
    try:
        fetchers.sam_contract_awards_resolved_download_url(emailed_url)
    except SystemExit as error:
        assert "SAM_API_KEY" in str(error), error
    else:
        raise AssertionError("placeholder SAM.gov download URL should require SAM_API_KEY")
    extract_payload = read_json("sam-contract-awards-extract-response.json")
    extract_records = fetchers.sam_contract_award_records(extract_payload)
    assert len(extract_records) == 2, extract_records
    extract_rows = fetchers.normalize_sam_contract_award_records(extract_records)
    assert extract_rows[0]["awardId"] == "80GSFC24C0001", extract_rows[0]
    assert extract_rows[0]["amount"] == 1.25, extract_rows[0]
    assert extract_rows[1]["modificationNumber"] == "P00002", extract_rows[1]
    assert extract_rows[1]["exPostModification"] == "true", extract_rows[1]
    csv_records = fetchers.sam_contract_awards_records_from_csv_or_message(
        "\n".join(
            [
                "PIID,Modification Number,Awardee Legal Business Name,Contracting Department Name,Contracting Subtier Name,Award or IDV Type,Action Obligation,Unique Entity ID,Date Signed,Extent Competed,Number Of Offers Received,Type Of Contract Pricing",
                "68HERH24C0002,P00003,CSV CONTRACTOR LLC,ENVIRONMENTAL PROTECTION AGENCY,ENVIRONMENTAL PROTECTION AGENCY,DEFINITIVE CONTRACT,750000,CSVUEI123456,2024-09-01,NOT COMPETED,1,FIRM FIXED PRICE",
            ]
        )
    )
    csv_rows = fetchers.normalize_sam_contract_award_records(csv_records)
    assert csv_rows[0]["recipient"] == "CSV CONTRACTOR LLC", csv_rows[0]
    assert csv_rows[0]["amount"] == 0.75, csv_rows[0]
    assert csv_rows[0]["competitionType"] == "NOT COMPETED", csv_rows[0]
    assert csv_rows[0]["numberOfOffers"] == "1", csv_rows[0]
    assert csv_rows[0]["exPostModification"] == "true", csv_rows[0]
    with tempfile.TemporaryDirectory() as tmp:
        export_path = Path(tmp) / "sam-contract-awards-export"
        export_path.write_text(
            "\n".join(
                [
                    "contractId.piid,modification_number,recipientName,contractingDepartmentName,contractingSubtierName,awardOrIDVTypeName,Federal Action Obligation,Recipient UEI,actionDate,extentCompetedName,numberOfOffers,typeOfContractPricingName",
                    "68HERH24C0004,P00004,MANUAL EXPORT CONTRACTOR,ENVIRONMENTAL PROTECTION AGENCY,EPA OFFICE,DEFINITIVE CONTRACT,1250000,EXPORTUEI1234,2024-09-15,FULL AND OPEN COMPETITION,5,FIRM FIXED PRICE",
                ]
            ),
            encoding="utf-8",
        )
        export_rows = fetchers.normalize_sam_contract_award_records(
            fetchers.sam_contract_awards_records_from_export_file(export_path)
        )
        assert export_rows[0]["awardId"] == "68HERH24C0004", export_rows[0]
        assert export_rows[0]["recipient"] == "MANUAL EXPORT CONTRACTOR", export_rows[0]
        assert export_rows[0]["amount"] == 1.25, export_rows[0]
        assert export_rows[0]["uei"] == "EXPORTUEI1234", export_rows[0]
        assert export_rows[0]["exPostModification"] == "true", export_rows[0]
        zip_path = Path(tmp) / "download-without-extension"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("ContractAwards.csv", export_path.read_text(encoding="utf-8"))
        zip_rows = fetchers.normalize_sam_contract_award_records(
            fetchers.sam_contract_awards_records_from_export_file(zip_path)
        )
        assert zip_rows == export_rows, zip_rows
    assert fetchers.sam_contract_awards_extract_message('{"message":"File generation is in progress."}') == "File generation is in progress."
    for name in (
        "SAM_CONTRACT_AWARDS_EXTRACT_MODE",
        "SAM_CONTRACT_AWARDS_EXTRACT_FORMAT",
        "SAM_CONTRACT_AWARDS_FORMAT",
        "SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID",
        "SAM_CONTRACT_AWARDS_MODIFICATION_NUMBER",
    ):
        os.environ.pop(name, None)
    rows = fetchers.normalize_sam_contract_award_records(records)
    assert rows[0] == {
        "awardId": "68HERH24F0001",
        "recipient": "EXAMPLE ENVIRONMENTAL CONTRACTOR LLC",
        "agency": "ENVIRONMENTAL PROTECTION AGENCY",
        "subAgency": "ENVIRONMENTAL PROTECTION AGENCY",
        "awardType": "DELIVERY ORDER",
        "amount": 2.5,
        "issueDomain": "procurement",
        "awardCount": 1,
        "uei": "ABCDEF123456",
        "piid": "68HERH24F0001",
        "modificationNumber": "0",
        "actionDate": "2024-03-15T11:39:06Z",
        "competitionType": "FULL AND OPEN COMPETITION",
        "numberOfOffers": "3",
        "priceOnlyAward": "false",
        "exPostModification": "false",
        "protestFiled": "false",
        "exclusionFlag": "false",
        "firewallCovered": "false",
    }, rows[0]
    assert rows[1]["amount"] == 0.5, rows[1]
    assert rows[1]["modificationNumber"] == "P00001", rows[1]
    assert rows[1]["competitionType"] == "NOT COMPETED", rows[1]
    assert rows[1]["numberOfOffers"] == "1", rows[1]
    assert rows[1]["priceOnlyAward"] == "true", rows[1]
    assert rows[1]["exPostModification"] == "true", rows[1]


def assert_curl_fallback_toggle(fetchers) -> None:
    previous = os.environ.get("SOURCE_FETCH_CURL_FALLBACK")
    try:
        os.environ["SOURCE_FETCH_CURL_FALLBACK"] = "0"
        assert fetchers.curl_fallback_enabled("GET", None) is False
        os.environ["SOURCE_FETCH_CURL_FALLBACK"] = "1"
        assert fetchers.curl_fallback_enabled("POST", None) is False
        assert fetchers.curl_fallback_enabled("GET", b"payload") is False
        assert fetchers.curl_fallback_enabled("GET", None) is (fetchers.shutil.which("curl") is not None)
    finally:
        if previous is None:
            os.environ.pop("SOURCE_FETCH_CURL_FALLBACK", None)
        else:
            os.environ["SOURCE_FETCH_CURL_FALLBACK"] = previous


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


def assert_seattle_democracy_vouchers(fetchers) -> None:
    with tempfile.TemporaryFile() as workbook:
        write_minimal_xlsx(
            workbook,
            "Web Program Data",
            [
                ["Voucher Number", "Participant", "Assigned Campaign", "Received Date", "Voucher Status", "Participant ID (Participant) (Contact)"],
                ["A00000001", "Resident One", "Example Voucher Candidate", "46103", "Redeemed", "100"],
                ["A00000002", "Resident Two", "Example Voucher Candidate", "46103", "Accepted", "101"],
                ["A00000003", "Resident Three", "Ignored Candidate", "46103", "Under Review", "102"],
                ["A00000004", "Resident Four", "Unassigned", "46103", "Redeemed", "103"],
            ],
        )
        workbook.seek(0)
        records = fetchers.xlsx_rows_from_file(workbook, "Web Program Data", 100)
    rows = fetchers.normalize_seattle_democracy_voucher_records(records, "https://www.seattle.gov/example.xlsx")
    assert rows == [
        {
            "source": "Seattle Democracy Voucher Program",
            "recipient": "Example Voucher Candidate",
            "issueDomain": "democracy",
            "amount": 0.0001,
            "flowType": "DEMOCRACY_VOUCHER",
            "traceability": 0.98,
            "largeDonorShare": 0.04,
            "sourceRecordId": "seattle-dvp-9d90f961eb",
            "sourceUrl": "https://www.seattle.gov/example.xlsx",
            "committeeType": "municipal democracy vouchers",
            "spendingPurpose": "2 accepted or redeemed vouchers",
            "supportOppose": "",
            "disclosureLag": 0.08,
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


def assert_propublica_nonprofit_routing(fetchers) -> None:
    html = read_text("propublica-schedule-i.html")
    assert fetchers.decode_response_text(gzip.compress(html.encode("utf-8")), "gzip") == html
    organization = {
        "name": "Example Policy Association",
        "ein": "123456789",
        "subsection_code": "6",
        "tax_period": "202412",
    }
    rows = fetchers.normalize_propublica_schedule_i_rows(
        organization,
        html,
        "https://projects.propublica.org/nonprofits/full_text/202499999999999999/IRS990ScheduleI",
    )
    assert rows == [
        {
            "source": "Example Policy Association",
            "recipient": "Example Research Institute",
            "issueDomain": "technology",
            "amount": 0.12,
            "flowType": "DARK_MONEY",
            "traceability": 0.08,
            "largeDonorShare": 0.58,
            "sourceRecordId": "123456789-202412-schedule-i-1",
            "sourceUrl": "https://projects.propublica.org/nonprofits/full_text/202499999999999999/IRS990ScheduleI",
            "committeeType": "501(c)(6) Schedule I nonprofit routing",
            "spendingPurpose": "TECHNOLOGY POLICY RESEARCH",
            "supportOppose": "",
            "disclosureLag": 0.48,
        }
    ], rows
    assert fetchers.propublica_recipient_is_specific("SEE ATTACHED SCHEDULE") is False
    assert fetchers.propublica_recipient_is_specific("Example Research Institute") is True


def assert_irs_527(fetchers) -> None:
    os.environ["IRS_POFD_OUTPUT_ROWS"] = "10"
    source_rows = [
        {
            "formId": "123",
            "periodBegin": "20240101",
            "periodEnd": "20240201",
            "organization": "Example Policy Action Fund",
            "ein": "123456789",
            "state": "DC",
            "scheduleAIndicator": "0",
            "totalContributions": "120000",
            "scheduleBIndicator": "0",
            "totalExpenditures": "50000",
            "insertDateTime": "2024-02-03 10:00:00",
            "purpose": "policy campaign",
            "sourceUrl": "https://forms.irs.gov/app/pod/dataDownload/dataAG",
        },
        {
            "formId": "124",
            "periodBegin": "20240202",
            "periodEnd": "20240301",
            "organization": "Example Policy Action Fund",
            "ein": "123456789",
            "state": "DC",
            "scheduleAIndicator": "1",
            "totalContributions": "20000",
            "scheduleBIndicator": "0",
            "totalExpenditures": "30000",
            "insertDateTime": "2024-03-03 10:00:00",
            "purpose": "policy campaign",
            "sourceUrl": "https://forms.irs.gov/app/pod/dataDownload/dataAG",
        },
    ]
    rows = fetchers.normalize_irs_pofd_8872_records(source_rows)
    assert rows == [
        {
            "organization": "Example Policy Action Fund",
            "ein": "123456789",
            "sourceType": "irs-pofd-8872",
            "subsection": "527",
            "issueDomain": "democracy",
            "revenue": 0.17,
            "politicalSpend": 0.05,
            "grantmaking": 0.0,
            "donorDisclosure": 0.72,
            "recipient": "DC",
            "sourceUrl": "https://forms.irs.gov/app/pod/dataDownload/dataAG",
        },
        {
            "organization": "Example Policy Action Fund",
            "ein": "123456789",
            "sourceType": "irs-pofd-8872",
            "subsection": "527",
            "issueDomain": "democracy",
            "revenue": 0.05,
            "politicalSpend": 0.03,
            "grantmaking": 0.0,
            "donorDisclosure": 0.66,
            "recipient": "DC",
            "sourceUrl": "https://forms.irs.gov/app/pod/dataDownload/dataAG",
        },
    ], rows


def read_json(name: str):
    with (FIXTURES / name).open(encoding="utf-8") as source:
        return json.load(source)


def read_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def write_minimal_xlsx(destination, sheet_name: str, rows: list[list[str]]) -> None:
    shared: list[str] = []
    shared_index: dict[str, int] = {}

    def shared_id(value: str) -> int:
        if value not in shared_index:
            shared_index[value] = len(shared)
            shared.append(value)
        return shared_index[value]

    sheet_rows = []
    for row_index, row in enumerate(rows, 1):
        cells = []
        for column_index, value in enumerate(row):
            reference = f"{xlsx_column(column_index)}{row_index}"
            cells.append(f'<c r="{reference}" t="s"><v>{shared_id(value)}</v></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    shared_items = "".join(f"<si><t>{xml_escape(value)}</t></si>" for value in shared)
    with zipfile.ZipFile(destination, "w") as archive:
        archive.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>""")
        archive.writestr("xl/workbook.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="{xml_escape(sheet_name)}" sheetId="1" r:id="rId1"/></sheets>
</workbook>""")
        archive.writestr("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""")
        archive.writestr("xl/sharedStrings.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared)}" uniqueCount="{len(shared)}">{shared_items}</sst>""")
        archive.writestr("xl/worksheets/sheet1.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{"".join(sheet_rows)}</sheetData>
</worksheet>""")


def xlsx_column(index: int) -> str:
    value = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        value = chr(ord("A") + remainder) + value
    return value


def xml_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


if __name__ == "__main__":
    raise SystemExit(main())
