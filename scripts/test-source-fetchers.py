#!/usr/bin/env python3
"""Exercise source-native JSON normalizers without network access."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "fixtures" / "source-native"


def main() -> int:
    fetchers = load_fetcher_module()
    assert_lda(fetchers)
    assert_fec(fetchers)
    assert_regulations(fetchers)
    assert_federal_register(fetchers)
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
    payload = read_json("lda-filings.json")
    rows = fetchers.normalize_lda_records(payload["results"])
    assert rows == [
        {
            "client": "Example Platform Coalition",
            "registrant": "Example Advocacy LLC",
            "issueDomain": "technology",
            "amount": 3.0,
            "disclosureLag": 0.45,
            "coveredOfficialShare": 0.30,
        }
    ], rows


def assert_fec(fetchers) -> None:
    payload = read_json("fec-schedule-a.json")
    rows = fetchers.normalize_fec_records(payload["results"])
    assert rows[0] == {
        "source": "Clean Energy Executive",
        "recipient": "Clean Energy PAC",
        "issueDomain": "energy",
        "amount": 0.0075,
        "flowType": "PAC",
        "traceability": 0.78,
        "largeDonorShare": 0.38,
    }, rows[0]
    assert rows[1]["flowType"] == "SUPER_PAC", rows[1]
    assert rows[1]["issueDomain"] == "technology", rows[1]


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


def read_json(name: str):
    with (FIXTURES / name).open(encoding="utf-8") as source:
        return json.load(source)


if __name__ == "__main__":
    raise SystemExit(main())
