#!/usr/bin/env python3
"""Write the first-wave procurement source acquisition playbook.

This report is a source-acquisition control, not source evidence. It names the
official public surfaces and linkage requirements for the procurement overlays
that remain necessary before procurement-modification capture can move from a
bounded diagnostic to an empirical or causal claim.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


REPORTS = Path("reports")
FIRST_WAVE_SOURCE_PRODUCTS = REPORTS / "first-wave-source-products.csv"

SOURCE_ROWS = [
    {
        "productKey": "sam-fpds-action-history-crosswalk",
        "expectedPath": "data/calibration/first-wave/sam-fpds-action-history-crosswalk.csv",
        "preferredOfficialSource": "SAM.gov Contract Awards export or keyed Contract Awards API, reconciled against USAspending transaction rows",
        "officialSourceUrl": "https://open.gsa.gov/api/contract-awards/",
        "fallbackSource": "USAspending public transaction download strata already documented by the repository; use only as a bounded denominator until SAM/FPDS-style action coding is reconciled",
        "requiredLinkage": "PIID, UEI, awarding agency/subtier, recipient, action date, obligation, modification number/type, competition or extent-competed code, number of offers, USAspending record ID, SAM record ID, and crosswalk confidence",
        "acquisitionStep": "After SAM quota reset, request a representative Contract Awards export, record the emailed link with make sam-contract-awards-record-export-link, then run make sam-procurement-refresh.",
        "promotionGate": "Export audit must report promotion-readiness=candidate; then make first-wave-source-products, make first-wave-source-readiness, and make paper-artifacts-check must pass.",
        "claimBoundary": "A SAM/FPDS action-history crosswalk can improve procurement denominator validity; it does not by itself estimate capture effects without exposure timing and comparison design.",
        "currentBlocker": "SAM.gov quota or extract-token availability can block acquisition; partial or diagnostic exports must not be promoted.",
    },
    {
        "productKey": "gao-protest-overlay",
        "expectedPath": "data/calibration/first-wave/gao-protest-overlay.csv",
        "preferredOfficialSource": "GAO Recent Bid Protest Decisions, GAO Search Decisions & Docket, and GAO Legal Products XML feed",
        "officialSourceUrl": "https://www.gao.gov/legal/bid-protests/recent",
        "fallbackSource": "GAO Legal Products XML feed for discovery, then decision pages or PDFs for extracted fields",
        "requiredLinkage": "Protest ID or B-number, agency, filed date where available, decision date, outcome, issue codes, source URL, and manually reviewed PIID/UEI/vendor linkage when available",
        "acquisitionStep": "Build a GAO protest worklist from recent/search/feed surfaces, extract decision metadata, then manually link decisions to PIID, UEI, vendor, agency, and issue fields before promotion.",
        "promotionGate": "Each row needs a source URL plus PIID or vendor linkage; unmatched protests remain context rows and cannot clear the product gate.",
        "claimBoundary": "GAO protest rows measure observed dispute outcomes; this source does not identify lobbying exposure or capture without linked award/action and actor records.",
        "currentBlocker": "GAO decision surfaces do not reliably expose PIID/UEI fields in a machine-readable way, so award/vendor linkage is a manual review task.",
    },
    {
        "productKey": "sam-exclusion-overlay",
        "expectedPath": "data/calibration/first-wave/sam-exclusion-overlay.csv",
        "preferredOfficialSource": "SAM.gov Exclusions API and SAM.gov Entity/Exclusions Extracts Download API",
        "officialSourceUrl": "https://open.gsa.gov/api/exclusions-api/",
        "fallbackSource": "SAM_Exclusions_Public_Extract files from the official Entity/Exclusions Extracts API",
        "requiredLinkage": "Exclusion ID, UEI, recipient/entity name, exclusion type, activation/start date, termination/end date, excluding agency, and source URL",
        "acquisitionStep": "Use the Exclusions API for targeted UEI/entity checks or the public exclusion extract for a broader panel; keep API keys in .env and archive only normalized public rows.",
        "promotionGate": "Rows must carry UEI linkage, timing, exclusion type, and source provenance; active-only or missing-date rows cannot clear the causal source gate.",
        "claimBoundary": "Exclusions separate integrity-enforcement status from procurement outcomes; they are not proof of capture or corruption.",
        "currentBlocker": "Official API quota and extract access must be managed; broad extracts require field normalization and source-date preservation.",
    },
    {
        "productKey": "procurement-firewall-overlay",
        "expectedPath": "data/calibration/first-wave/procurement-firewall-overlay.csv",
        "preferredOfficialSource": "Agency procurement-integrity rules, firewall memoranda, acquisition-policy supplements, inspector-general reports, and official policy archives",
        "officialSourceUrl": "https://www.acquisition.gov/far/",
        "fallbackSource": "Agency acquisition-policy pages and inspector-general/audit reports with source URLs and effective dates",
        "requiredLinkage": "Firewall rule ID, agency, subtier, award type, effective date, covered officials, control type, coverage rule, and source URL",
        "acquisitionStep": "Start with the agencies represented in the action-history crosswalk, then encode dated procurement-integrity controls and coverage rules for the relevant award classes.",
        "promotionGate": "At least one dated control rule with agency and covered-official fields is required; generic policy descriptions without dates stay as notes.",
        "claimBoundary": "Firewall rows represent observed institutional controls; they do not establish compliance or enforcement without audit or outcome linkage.",
        "currentBlocker": "No single public API provides agency firewall controls, so acquisition is a curated document-review task over official sources.",
    },
    {
        "productKey": "procurement-offer-competition-enrichment",
        "expectedPath": "data/calibration/first-wave/procurement-offer-competition-enrichment.csv",
        "preferredOfficialSource": "SAM.gov Contract Awards and USAspending transaction/action records where offer-count and competition fields are exposed",
        "officialSourceUrl": "https://open.gsa.gov/api/",
        "fallbackSource": "Award-detail and latest-transaction fields from USAspending, retained as directional context when action-history fields are absent",
        "requiredLinkage": "PIID, UEI, agency, action date, award type, extent-competed code, number of offers, source system, source-system record ID, source URL, and crosswalk confidence",
        "acquisitionStep": "Populate the standalone offer/competition enrichment product from SAM/FPDS or USAspending rows with observed source competition fields, then reconcile it with the action-history crosswalk.",
        "promotionGate": "The source-product gate requires at least 5,000 rows, at least 1,000 distinct PIIDs, at least six agencies, at least two competition codes, nonempty source provenance, and high offer-count coverage.",
        "claimBoundary": "Competition enrichment supports controls and stratification; it is not an independent capture outcome.",
        "currentBlocker": "No reviewed standalone offer/competition source product has been promoted yet; committed USAspending action rows remain denominator context until source-system competition fields clear the gate.",
    },
]


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    product_status = source_product_status()
    rows = []
    for row in SOURCE_ROWS:
        status_row = product_status.get(row["productKey"], {})
        rows.append(
            {
                "productKey": row["productKey"],
                "expectedPath": row["expectedPath"],
                "sourceProductStatus": status_row.get("productStatus", "not_in_source_product_gate"),
                "requirementLevel": status_row.get("requirementLevel", "supporting"),
                "priority": status_row.get("priority", "P1"),
                "minimumRows": status_row.get("minimumRows", ""),
                **row,
            }
        )

    write_csv(REPORTS / "first-wave-procurement-source-acquisition.csv", rows)
    write_markdown(REPORTS / "first-wave-procurement-source-acquisition.md", rows)
    print("Wrote reports/first-wave-procurement-source-acquisition.csv")
    print("Wrote reports/first-wave-procurement-source-acquisition.md")
    return 0


def source_product_status() -> dict[str, dict[str, str]]:
    if not FIRST_WAVE_SOURCE_PRODUCTS.exists():
        return {}
    with FIRST_WAVE_SOURCE_PRODUCTS.open(newline="", encoding="utf-8") as source:
        return {row.get("productKey", ""): row for row in csv.DictReader(source)}


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "productKey",
        "expectedPath",
        "sourceProductStatus",
        "requirementLevel",
        "priority",
        "minimumRows",
        "preferredOfficialSource",
        "officialSourceUrl",
        "fallbackSource",
        "requiredLinkage",
        "acquisitionStep",
        "promotionGate",
        "claimBoundary",
        "currentBlocker",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["sourceProductStatus"] for row in rows)
    lines = [
        "# First-Wave Procurement Source Acquisition",
        "",
        "This report turns the open procurement-calibration risk into source-specific acquisition tasks. It is not source evidence and does not clear calibrated procurement-capture claims. Its role is to make the next public-source panels concrete enough that future promotion can be audited.",
        "",
        "## Summary",
        "",
        f"- Acquisition products: `{len(rows)}`",
        "- Source-evidence status: `acquisition_plan_only`",
        "- Claim boundary: `procurement modification, protest, exclusion, competition, and firewall rows remain bounded diagnostics until linked source products pass the first-wave source-product and source-readiness gates`",
        f"- Product statuses: `{format_counts(status_counts)}`",
        "",
        "## Promotion Rule",
        "",
        "A row in this report is only an acquisition instruction. To promote a procurement source product, populate the corresponding file under `data/calibration/first-wave/`, preserve source URLs and extraction dates, run `make first-wave-source-products`, run `make first-wave-source-readiness`, then run `make paper-artifacts-check`. A successful SAM export audit or source download is not enough unless the product-level schema, semantic gates, and claim boundaries also pass.",
        "",
        "## Source Plan",
        "",
        "| Product | Product gate | Preferred official source | Required linkage | Current blocker |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {product} | {status} | {source} | {linkage} | {blocker} |".format(
                product=md(row["productKey"]),
                status=md(row["sourceProductStatus"]),
                source=md(f"{row['preferredOfficialSource']} ({row['officialSourceUrl']})"),
                linkage=md(row["requiredLinkage"]),
                blocker=md(row["currentBlocker"]),
            )
        )
    lines.extend(
        [
            "",
            "## Acquisition Details",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### {row['productKey']}",
                "",
                f"- Expected path: `{row['expectedPath']}`",
                f"- Source-product status: `{row['sourceProductStatus']}`",
                f"- Preferred official source: {row['preferredOfficialSource']} ({row['officialSourceUrl']})",
                f"- Fallback: {row['fallbackSource']}",
                f"- Required linkage: {row['requiredLinkage']}",
                f"- Acquisition step: {row['acquisitionStep']}",
                f"- Promotion gate: {row['promotionGate']}",
                f"- Claim boundary: {row['claimBoundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Official Source Notes",
            "",
            "- GAO Recent Bid Protest Decisions and Search Decisions & Docket are the official protest-discovery surfaces; the GAO Legal Products XML feed can be used as a machine-readable discovery queue for new protest decisions.",
            "- SAM.gov Exclusions API returns public exclusion records in paginated JSON and can also initiate CSV/JSON extracts; the Entity/Exclusions Extracts API can download public exclusion extracts such as `SAM_Exclusions_Public_Extract` files.",
            "- SAM.gov Contract Awards remains the preferred source for Contract Awards action-history fields; USAspending transaction/action rows remain a bounded fallback until SAM/FPDS-style definitions are reconciled.",
            "- Procurement firewall coverage is a document-review product, not an API product. Dated agency policies, acquisition supplements, firewall memoranda, and official audit reports must be encoded with source URLs and coverage rules.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def format_counts(counts: Counter[str]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
