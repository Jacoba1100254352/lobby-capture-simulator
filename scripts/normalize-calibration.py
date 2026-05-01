#!/usr/bin/env python3
"""Normalize live calibration extracts into the simulator's fixture schemas."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


SCHEMAS = {
    "lda": {
        "fields": ["client", "registrant", "issueDomain", "amount", "disclosureLag", "coveredOfficialShare"],
        "aliases": {
            "client": ["client", "client_name", "clientname"],
            "registrant": ["registrant", "registrant_name", "registrantname"],
            "issueDomain": ["issueDomain", "issue", "issue_domain", "general_issue_code"],
            "amount": ["amount", "income", "expense", "lobbying_amount", "total"],
            "disclosureLag": ["disclosureLag", "disclosure_lag", "lag"],
            "coveredOfficialShare": ["coveredOfficialShare", "covered_official_share", "coveredofficialshare"],
        },
    },
    "fec": {
        "fields": ["source", "recipient", "issueDomain", "amount", "flowType", "traceability", "largeDonorShare"],
        "aliases": {
            "source": ["source", "committee_name", "contributor_name", "donor"],
            "recipient": ["recipient", "candidate_name", "recipient_name"],
            "issueDomain": ["issueDomain", "issue", "issue_domain", "sector"],
            "amount": ["amount", "contribution_receipt_amount", "disbursement_amount", "total"],
            "flowType": ["flowType", "flow_type", "funding_source"],
            "traceability": ["traceability", "traceability_score"],
            "largeDonorShare": ["largeDonorShare", "large_donor_share"],
        },
    },
    "regulatory": {
        "fields": [
            "docketId",
            "issueDomain",
            "agency",
            "commentVolume",
            "genuineShare",
            "templateShare",
            "technicalClaimCredibility",
            "authenticationShare",
        ],
        "aliases": {
            "docketId": ["docketId", "docket_id", "document_number"],
            "issueDomain": ["issueDomain", "issue", "issue_domain", "topic"],
            "agency": ["agency", "agency_id", "agency_name"],
            "commentVolume": ["commentVolume", "comment_count", "comment_count_posted", "comments"],
            "genuineShare": ["genuineShare", "genuine_share"],
            "templateShare": ["templateShare", "template_share"],
            "technicalClaimCredibility": ["technicalClaimCredibility", "technical_claim_credibility"],
            "authenticationShare": ["authenticationShare", "authentication_share"],
        },
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(SCHEMAS))
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    schema = SCHEMAS[args.kind]
    with args.input.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise SystemExit(f"{args.input} has no header row.")
        mapping = resolve_mapping(args.kind, reader.fieldnames, schema["aliases"])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=schema["fields"])
            writer.writeheader()
            for row in reader:
                writer.writerow({field: clean(row.get(source_name, "")) for field, source_name in mapping.items()})
    print(f"Wrote {args.output}")
    return 0


def resolve_mapping(kind: str, source_fields: list[str], aliases: dict[str, list[str]]) -> dict[str, str]:
    normalized = {normalize(field): field for field in source_fields}
    mapping: dict[str, str] = {}
    missing: list[str] = []
    for target, candidates in aliases.items():
        match = next((normalized[normalize(candidate)] for candidate in candidates if normalize(candidate) in normalized), None)
        if match is None:
            missing.append(target)
        else:
            mapping[target] = match
    if missing:
        available = ", ".join(source_fields)
        needed = ", ".join(missing)
        raise SystemExit(
            f"Cannot normalize {kind}: missing required fields [{needed}]. "
            f"Available source fields: {available}"
        )
    return mapping


def normalize(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def clean(value: str) -> str:
    return value.strip()


if __name__ == "__main__":
    sys.exit(main())
