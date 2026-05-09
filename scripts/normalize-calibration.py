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
        "fields": [
            "source",
            "recipient",
            "issueDomain",
            "amount",
            "flowType",
            "traceability",
            "largeDonorShare",
            "sourceRecordId",
            "sourceUrl",
            "committeeType",
            "spendingPurpose",
            "supportOppose",
            "disclosureLag",
        ],
        "aliases": {
            "source": ["source", "committee_name", "contributor_name", "donor"],
            "recipient": ["recipient", "candidate_name", "recipient_name"],
            "issueDomain": ["issueDomain", "issue", "issue_domain", "sector"],
            "amount": ["amount", "contribution_receipt_amount", "disbursement_amount", "total"],
            "flowType": ["flowType", "flow_type", "funding_source"],
            "traceability": ["traceability", "traceability_score"],
            "largeDonorShare": ["largeDonorShare", "large_donor_share"],
            "sourceRecordId": ["sourceRecordId", "source_record_id", "transaction_id", "image_number", "id"],
            "sourceUrl": ["sourceUrl", "source_url", "url"],
            "committeeType": ["committeeType", "committee_type", "committee_type_full", "spender_type"],
            "spendingPurpose": ["spendingPurpose", "spending_purpose", "expenditure_description", "purpose"],
            "supportOppose": ["supportOppose", "support_oppose", "support_oppose_indicator"],
            "disclosureLag": ["disclosureLag", "disclosure_lag", "lag"],
        },
        "optional": {
            "sourceRecordId": "",
            "sourceUrl": "",
            "committeeType": "unknown",
            "spendingPurpose": "",
            "supportOppose": "",
            "disclosureLag": "0.28",
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
    "usaspending": {
        "fields": [
            "awardId",
            "recipient",
            "agency",
            "subAgency",
            "awardType",
            "amount",
            "issueDomain",
            "awardCount",
            "uei",
            "piid",
            "modificationNumber",
            "actionDate",
            "competitionType",
            "numberOfOffers",
            "priceOnlyAward",
            "exPostModification",
            "firewallCovered",
        ],
        "aliases": {
            "awardId": ["awardId", "award_id", "award number", "Award ID"],
            "recipient": ["recipient", "recipient_name", "Recipient Name"],
            "agency": ["agency", "awarding_agency", "Awarding Agency"],
            "subAgency": ["subAgency", "sub_agency", "awarding_sub_agency", "Awarding Sub Agency"],
            "awardType": ["awardType", "award_type", "Award Type"],
            "amount": ["amount", "award_amount", "Award Amount", "obligation"],
            "issueDomain": ["issueDomain", "issue", "issue_domain", "sector"],
            "awardCount": ["awardCount", "award_count", "transaction_count", "count"],
            "uei": ["uei", "recipient_uei", "Recipient UEI", "UEI"],
            "piid": ["piid", "PIID", "procurementInstrumentIdentifier", "Award ID"],
            "modificationNumber": [
                "modificationNumber",
                "modification_number",
                "award_modification_amendment_number",
                "Modification Number",
            ],
            "actionDate": ["actionDate", "action_date", "Action Date"],
            "competitionType": ["competitionType", "competition_type", "extent_competed", "Extent Competed"],
            "numberOfOffers": ["numberOfOffers", "number_of_offers_received", "Number of Offers"],
            "priceOnlyAward": ["priceOnlyAward", "price_only_award", "Price Only Award"],
            "exPostModification": ["exPostModification", "ex_post_modification", "is_modification"],
            "firewallCovered": ["firewallCovered", "firewall_covered", "covered_by_firewall"],
        },
        "optional": {
            "uei": "",
            "piid": "",
            "modificationNumber": "0",
            "actionDate": "",
            "competitionType": "unknown",
            "numberOfOffers": "0",
            "priceOnlyAward": "false",
            "exPostModification": "false",
            "firewallCovered": "false",
        },
    },
    "revolving-door": {
        "fields": [
            "person",
            "organization",
            "sector",
            "agency",
            "formerOfficialRole",
            "coolingOffMonths",
            "sourceType",
            "influenceShare",
            "sourceRecordId",
            "sourceUrl",
            "positionType",
            "confidence",
        ],
        "aliases": {
            "person": ["person", "name", "lobbyist_name"],
            "organization": ["organization", "employer", "client", "firm"],
            "sector": ["sector", "issueDomain", "issue_domain", "industry"],
            "agency": ["agency", "former_agency", "government_agency"],
            "formerOfficialRole": ["formerOfficialRole", "former_official_role", "revolving_door_role", "previous_position"],
            "coolingOffMonths": ["coolingOffMonths", "cooling_off_months", "months_since_service"],
            "sourceType": ["sourceType", "source_type", "source"],
            "influenceShare": ["influenceShare", "influence_share", "share", "weight"],
            "sourceRecordId": ["sourceRecordId", "source_record_id", "record_id", "id"],
            "sourceUrl": ["sourceUrl", "source_url", "url"],
            "positionType": ["positionType", "position_type", "role_type", "panel"],
            "confidence": ["confidence", "confidence_score", "match_confidence"],
        },
        "optional": {
            "sourceRecordId": "",
            "sourceUrl": "",
            "positionType": "unknown",
            "confidence": "0.50",
        },
    },
    "intermediary": {
        "fields": [
            "organization",
            "ein",
            "sourceType",
            "subsection",
            "issueDomain",
            "revenue",
            "politicalSpend",
            "grantmaking",
            "donorDisclosure",
            "recipient",
            "sourceUrl",
        ],
        "aliases": {
            "organization": ["organization", "name", "org_name"],
            "ein": ["ein", "EIN", "tax_id"],
            "sourceType": ["sourceType", "source_type", "source", "form"],
            "subsection": ["subsection", "section", "tax_status"],
            "issueDomain": ["issueDomain", "issue", "issue_domain", "sector"],
            "revenue": ["revenue", "total_revenue", "amount"],
            "politicalSpend": ["politicalSpend", "political_spend", "political_expenditures"],
            "grantmaking": ["grantmaking", "grants", "grants_paid"],
            "donorDisclosure": ["donorDisclosure", "donor_disclosure", "donor_visibility", "traceability"],
            "recipient": ["recipient", "grantee", "payee"],
            "sourceUrl": ["sourceUrl", "source_url", "url"],
        },
        "optional": {
            "sourceUrl": "",
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
        mapping = resolve_mapping(args.kind, reader.fieldnames, schema)
        defaults = schema.get("optional", {})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=schema["fields"])
            writer.writeheader()
            for row in reader:
                writer.writerow(
                    {
                        field: clean(row.get(source_name, defaults.get(field, ""))) if source_name else defaults.get(field, "")
                        for field, source_name in mapping.items()
                    }
                )
    print(f"Wrote {args.output}")
    return 0


def resolve_mapping(kind: str, source_fields: list[str], schema: dict[str, object]) -> dict[str, str]:
    aliases = schema["aliases"]
    optional = schema.get("optional", {})
    normalized = {normalize(field): field for field in source_fields}
    mapping: dict[str, str] = {}
    missing: list[str] = []
    for target, candidates in aliases.items():
        match = next((normalized[normalize(candidate)] for candidate in candidates if normalize(candidate) in normalized), None)
        if match is None:
            if target in optional:
                mapping[target] = ""
            else:
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
