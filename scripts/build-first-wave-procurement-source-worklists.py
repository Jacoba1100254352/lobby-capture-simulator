#!/usr/bin/env python3
"""Build candidate-only procurement source-product worklists.

These rows are not source evidence. They turn the remaining procurement
calibration blockers into concrete review artifacts while keeping the
first-wave source-product gate blocked until representative SAM/FPDS rows,
GAO protest linkage, SAM exclusion linkage, and procurement-firewall controls
are populated from reviewed source records.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "calibration" / "first-wave"
CANDIDATE_STATUS = "candidate_unreviewed_not_estimation_ready"
BOUNDARY = (
    "candidate-only procurement source-surface worklist; does not clear "
    "first-wave source-product, procurement-modification, or causal-calibration gates"
)
SOURCE_EXTRACTED_AT = "2026-06-18"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)

    write_csv(
        output / "sam-fpds-action-history-crosswalk.csv",
        [
            "piid",
            "uei",
            "agency",
            "subtier",
            "recipientName",
            "actionDate",
            "actionObligation",
            "modificationNumber",
            "actionType",
            "extentCompeted",
            "numberOfOffers",
            "usaspendingRecordId",
            "samRecordId",
            "crosswalkConfidence",
            "awardType",
            "naics",
            "psc",
            "sourceUrl",
            "notes",
            "candidateOnly",
            "candidateStatus",
        ],
        [
            {
                "piid": "candidate_unreviewed",
                "uei": "candidate_unreviewed",
                "agency": "candidate_unreviewed_multi_agency_environmental_strata",
                "subtier": "candidate_unreviewed",
                "recipientName": "candidate_unreviewed",
                "actionDate": "candidate_unreviewed",
                "actionObligation": "candidate_unreviewed",
                "modificationNumber": "candidate_unreviewed",
                "actionType": "candidate_unreviewed",
                "extentCompeted": "candidate_unreviewed",
                "numberOfOffers": "candidate_unreviewed",
                "usaspendingRecordId": "candidate_unreviewed",
                "samRecordId": "candidate_unreviewed",
                "crosswalkConfidence": "0.0000",
                "awardType": "candidate_unreviewed",
                "naics": "candidate_unreviewed",
                "psc": "candidate_unreviewed",
                "sourceUrl": "https://open.gsa.gov/api/contract-awards/",
                "notes": (
                    f"{BOUNDARY}; sourceExtractedAt={SOURCE_EXTRACTED_AT}; "
                    "replace this row with normalized SAM.gov Contract Awards or FPDS action-history rows, "
                    "including modification coding, competition fields, offer counts, and source identifiers"
                ),
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_STATUS,
            }
        ],
    )

    write_csv(
        output / "gao-protest-overlay.csv",
        [
            "protestId",
            "piid",
            "uei",
            "agency",
            "filedDate",
            "decisionDate",
            "outcome",
            "issueCodes",
            "sourceUrl",
            "docketNumber",
            "protesterName",
            "awardeeName",
            "notes",
            "candidateOnly",
            "candidateStatus",
        ],
        [
            {
                "protestId": "candidate_unreviewed_gao_recent_bid_protests",
                "piid": "candidate_unreviewed",
                "uei": "candidate_unreviewed",
                "agency": "candidate_unreviewed",
                "filedDate": "candidate_unreviewed",
                "decisionDate": "candidate_unreviewed",
                "outcome": "candidate_unreviewed",
                "issueCodes": "candidate_unreviewed",
                "sourceUrl": "https://www.gao.gov/legal/bid-protests/recent",
                "docketNumber": "candidate_unreviewed",
                "protesterName": "candidate_unreviewed",
                "awardeeName": "candidate_unreviewed",
                "notes": (
                    f"{BOUNDARY}; sourceExtractedAt={SOURCE_EXTRACTED_AT}; "
                    "GAO recent/search/docket surfaces must be reviewed and linked to PIID, UEI, agency, "
                    "vendor, filing date, decision date, outcome, and issue fields before promotion"
                ),
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_STATUS,
            }
        ],
    )

    write_csv(
        output / "sam-exclusion-overlay.csv",
        [
            "exclusionId",
            "uei",
            "recipientName",
            "exclusionType",
            "startDate",
            "endDate",
            "agency",
            "sourceUrl",
            "cause",
            "terminationDate",
            "notes",
            "candidateOnly",
            "candidateStatus",
        ],
        [
            {
                "exclusionId": "candidate_unreviewed_sam_exclusions",
                "uei": "candidate_unreviewed",
                "recipientName": "candidate_unreviewed",
                "exclusionType": "candidate_unreviewed",
                "startDate": "candidate_unreviewed",
                "endDate": "candidate_unreviewed",
                "agency": "candidate_unreviewed",
                "sourceUrl": "https://open.gsa.gov/api/exclusions-api/",
                "cause": "candidate_unreviewed",
                "terminationDate": "candidate_unreviewed",
                "notes": (
                    f"{BOUNDARY}; sourceExtractedAt={SOURCE_EXTRACTED_AT}; "
                    "replace with SAM.gov Exclusions API or public extract rows carrying UEI, exclusion type, "
                    "dates, agency, and source provenance"
                ),
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_STATUS,
            }
        ],
    )

    write_csv(
        output / "procurement-firewall-overlay.csv",
        [
            "firewallRuleId",
            "agency",
            "subtier",
            "awardType",
            "effectiveDate",
            "coveredOfficials",
            "controlType",
            "sourceUrl",
            "expirationDate",
            "coverageRule",
            "notes",
            "candidateOnly",
            "candidateStatus",
        ],
        [
            {
                "firewallRuleId": "candidate_unreviewed_far_part_3_procurement_integrity",
                "agency": "government-wide Federal Acquisition Regulation baseline",
                "subtier": "candidate_unreviewed",
                "awardType": "FAR-covered procurements",
                "effectiveDate": "candidate_unreviewed",
                "coveredOfficials": (
                    "contracting officers; source-selection officials; former officials; "
                    "contractor employees performing acquisition functions"
                ),
                "controlType": "procurement-integrity and personal-conflict controls",
                "sourceUrl": "https://www.acquisition.gov/far/part-3",
                "expirationDate": "candidate_unreviewed",
                "coverageRule": (
                    "candidate worklist row for FAR Part 3 procurement-integrity and conflict-control surfaces; "
                    "agency/subtier implementation, dates, award classes, and compliance evidence require review"
                ),
                "notes": (
                    f"{BOUNDARY}; sourceExtractedAt={SOURCE_EXTRACTED_AT}; "
                    "replace or supplement with dated agency acquisition-policy, firewall memorandum, "
                    "procurement-integrity, or inspector-general control rows before promotion"
                ),
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_STATUS,
            }
        ],
    )

    write_csv(
        output / "procurement-offer-competition-enrichment.csv",
        [
            "piid",
            "uei",
            "agency",
            "actionDate",
            "awardType",
            "extentCompeted",
            "numberOfOffers",
            "sourceSystem",
            "sourceRecordId",
            "sourceUrl",
            "crosswalkConfidence",
            "recipientName",
            "subtier",
            "actionObligation",
            "notes",
            "candidateOnly",
            "candidateStatus",
        ],
        [
            {
                "piid": "candidate_unreviewed",
                "uei": "candidate_unreviewed",
                "agency": "candidate_unreviewed_multi_agency_environmental_strata",
                "actionDate": "candidate_unreviewed",
                "awardType": "candidate_unreviewed",
                "extentCompeted": "candidate_unreviewed",
                "numberOfOffers": "candidate_unreviewed",
                "sourceSystem": "candidate_unreviewed",
                "sourceRecordId": "candidate_unreviewed",
                "sourceUrl": "https://open.gsa.gov/api/",
                "crosswalkConfidence": "0.0000",
                "recipientName": "candidate_unreviewed",
                "subtier": "candidate_unreviewed",
                "actionObligation": "candidate_unreviewed",
                "notes": (
                    f"{BOUNDARY}; sourceExtractedAt={SOURCE_EXTRACTED_AT}; "
                    "replace this row with normalized SAM/FPDS or USAspending rows carrying source-system "
                    "competition codes, offer counts, award type, action date, source identifiers, and "
                    "crosswalk confidence before conditioning procurement-modification diagnostics"
                ),
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_STATUS,
            }
        ],
    )

    for filename in (
        "sam-fpds-action-history-crosswalk.csv",
        "gao-protest-overlay.csv",
        "sam-exclusion-overlay.csv",
        "procurement-firewall-overlay.csv",
        "procurement-offer-competition-enrichment.csv",
    ):
        print(f"Wrote {output / filename}")
    return 0


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
