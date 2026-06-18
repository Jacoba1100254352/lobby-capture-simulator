# First-Wave Procurement Source Acquisition

This report turns the open procurement-calibration risk into source-specific acquisition tasks. It is not source evidence and does not clear calibrated procurement-capture claims. Its role is to make the next public-source panels concrete enough that future promotion can be audited.

## Summary

- Acquisition products: `5`
- Source-evidence status: `acquisition_plan_only`
- Claim boundary: `procurement modification, protest, exclusion, competition, and firewall rows remain bounded diagnostics until linked source products pass the first-wave source-product and source-readiness gates`
- Product statuses: `missing_required=4; not_in_source_product_gate=1`

## Promotion Rule

A row in this report is only an acquisition instruction. To promote a procurement source product, populate the corresponding file under `data/calibration/first-wave/`, preserve source URLs and extraction dates, run `make first-wave-source-products`, run `make first-wave-source-readiness`, then run `make paper-artifacts-check`. A successful SAM export audit or source download is not enough unless the product-level schema, semantic gates, and claim boundaries also pass.

## Source Plan

| Product | Product gate | Preferred official source | Required linkage | Current blocker |
| --- | --- | --- | --- | --- |
| sam-fpds-action-history-crosswalk | missing_required | SAM.gov Contract Awards export or keyed Contract Awards API, reconciled against USAspending transaction rows (https://open.gsa.gov/api/contract-awards/) | PIID, UEI, awarding agency/subtier, recipient, action date, obligation, modification number/type, competition or extent-competed code, number of offers, USAspending record ID, SAM record ID, and crosswalk confidence | SAM.gov quota or extract-token availability can block acquisition; partial or diagnostic exports must not be promoted. |
| gao-protest-overlay | missing_required | GAO Recent Bid Protest Decisions, GAO Search Decisions & Docket, and GAO Legal Products XML feed (https://www.gao.gov/legal/bid-protests/recent) | Protest ID or B-number, agency, filed date where available, decision date, outcome, issue codes, source URL, and manually reviewed PIID/UEI/vendor linkage when available | GAO decision surfaces do not reliably expose PIID/UEI fields in a machine-readable way, so award/vendor linkage is a manual review task. |
| sam-exclusion-overlay | missing_required | SAM.gov Exclusions API and SAM.gov Entity/Exclusions Extracts Download API (https://open.gsa.gov/api/exclusions-api/) | Exclusion ID, UEI, recipient/entity name, exclusion type, activation/start date, termination/end date, excluding agency, and source URL | Official API quota and extract access must be managed; broad extracts require field normalization and source-date preservation. |
| procurement-firewall-overlay | missing_required | Agency procurement-integrity rules, firewall memoranda, acquisition-policy supplements, inspector-general reports, and official policy archives (https://www.acquisition.gov/far/) | Firewall rule ID, agency, subtier, award type, effective date, covered officials, control type, coverage rule, and source URL | No single public API provides agency firewall controls, so acquisition is a curated document-review task over official sources. |
| procurement-offer-competition-enrichment | not_in_source_product_gate | SAM.gov Contract Awards and USAspending transaction/action records where offer-count and competition fields are exposed (https://open.gsa.gov/api/) | PIID, UEI, extent-competed code, number of offers, award type, action date, obligation, agency, and source-system record ID | Committed USAspending action rows have weak competition-field coverage, so SAM/FPDS export promotion remains the preferred path. |

## Acquisition Details

### sam-fpds-action-history-crosswalk

- Expected path: `data/calibration/first-wave/sam-fpds-action-history-crosswalk.csv`
- Source-product status: `missing_required`
- Preferred official source: SAM.gov Contract Awards export or keyed Contract Awards API, reconciled against USAspending transaction rows (https://open.gsa.gov/api/contract-awards/)
- Fallback: USAspending public transaction download strata already documented by the repository; use only as a bounded denominator until SAM/FPDS-style action coding is reconciled
- Required linkage: PIID, UEI, awarding agency/subtier, recipient, action date, obligation, modification number/type, competition or extent-competed code, number of offers, USAspending record ID, SAM record ID, and crosswalk confidence
- Acquisition step: After SAM quota reset, request a representative Contract Awards export, record the emailed link with make sam-contract-awards-record-export-link, then run make sam-procurement-refresh.
- Promotion gate: Export audit must report promotion-readiness=candidate; then make first-wave-source-products, make first-wave-source-readiness, and make paper-artifacts-check must pass.
- Claim boundary: A SAM/FPDS action-history crosswalk can improve procurement denominator validity; it does not by itself estimate capture effects without exposure timing and comparison design.

### gao-protest-overlay

- Expected path: `data/calibration/first-wave/gao-protest-overlay.csv`
- Source-product status: `missing_required`
- Preferred official source: GAO Recent Bid Protest Decisions, GAO Search Decisions & Docket, and GAO Legal Products XML feed (https://www.gao.gov/legal/bid-protests/recent)
- Fallback: GAO Legal Products XML feed for discovery, then decision pages or PDFs for extracted fields
- Required linkage: Protest ID or B-number, agency, filed date where available, decision date, outcome, issue codes, source URL, and manually reviewed PIID/UEI/vendor linkage when available
- Acquisition step: Build a GAO protest worklist from recent/search/feed surfaces, extract decision metadata, then manually link decisions to PIID, UEI, vendor, agency, and issue fields before promotion.
- Promotion gate: Each row needs a source URL plus PIID or vendor linkage; unmatched protests remain context rows and cannot clear the product gate.
- Claim boundary: GAO protest rows measure observed dispute outcomes; this source does not identify lobbying exposure or capture without linked award/action and actor records.

### sam-exclusion-overlay

- Expected path: `data/calibration/first-wave/sam-exclusion-overlay.csv`
- Source-product status: `missing_required`
- Preferred official source: SAM.gov Exclusions API and SAM.gov Entity/Exclusions Extracts Download API (https://open.gsa.gov/api/exclusions-api/)
- Fallback: SAM_Exclusions_Public_Extract files from the official Entity/Exclusions Extracts API
- Required linkage: Exclusion ID, UEI, recipient/entity name, exclusion type, activation/start date, termination/end date, excluding agency, and source URL
- Acquisition step: Use the Exclusions API for targeted UEI/entity checks or the public exclusion extract for a broader panel; keep API keys in .env and archive only normalized public rows.
- Promotion gate: Rows must carry UEI linkage, timing, exclusion type, and source provenance; active-only or missing-date rows cannot clear the causal source gate.
- Claim boundary: Exclusions separate integrity-enforcement status from procurement outcomes; they are not proof of capture or corruption.

### procurement-firewall-overlay

- Expected path: `data/calibration/first-wave/procurement-firewall-overlay.csv`
- Source-product status: `missing_required`
- Preferred official source: Agency procurement-integrity rules, firewall memoranda, acquisition-policy supplements, inspector-general reports, and official policy archives (https://www.acquisition.gov/far/)
- Fallback: Agency acquisition-policy pages and inspector-general/audit reports with source URLs and effective dates
- Required linkage: Firewall rule ID, agency, subtier, award type, effective date, covered officials, control type, coverage rule, and source URL
- Acquisition step: Start with the agencies represented in the action-history crosswalk, then encode dated procurement-integrity controls and coverage rules for the relevant award classes.
- Promotion gate: At least one dated control rule with agency and covered-official fields is required; generic policy descriptions without dates stay as notes.
- Claim boundary: Firewall rows represent observed institutional controls; they do not establish compliance or enforcement without audit or outcome linkage.

### procurement-offer-competition-enrichment

- Expected path: `data/calibration/first-wave/sam-fpds-action-history-crosswalk.csv`
- Source-product status: `not_in_source_product_gate`
- Preferred official source: SAM.gov Contract Awards and USAspending transaction/action records where offer-count and competition fields are exposed (https://open.gsa.gov/api/)
- Fallback: Award-detail and latest-transaction fields from USAspending, retained as directional context when action-history fields are absent
- Required linkage: PIID, UEI, extent-competed code, number of offers, award type, action date, obligation, agency, and source-system record ID
- Acquisition step: Treat offer-count and competition enrichment as part of the SAM/FPDS crosswalk so modification rates can be conditioned on competition exposure.
- Promotion gate: Competition fields must remain source-system specific and cannot be imputed silently across SAM/FPDS and USAspending definitions.
- Claim boundary: Competition enrichment supports controls and stratification; it is not an independent capture outcome.

## Official Source Notes

- GAO Recent Bid Protest Decisions and Search Decisions & Docket are the official protest-discovery surfaces; the GAO Legal Products XML feed can be used as a machine-readable discovery queue for new protest decisions.
- SAM.gov Exclusions API returns public exclusion records in paginated JSON and can also initiate CSV/JSON extracts; the Entity/Exclusions Extracts API can download public exclusion extracts such as `SAM_Exclusions_Public_Extract` files.
- SAM.gov Contract Awards remains the preferred source for Contract Awards action-history fields; USAspending transaction/action rows remain a bounded fallback until SAM/FPDS-style definitions are reconciled.
- Procurement firewall coverage is a document-review product, not an API product. Dated agency policies, acquisition supplements, firewall memoranda, and official audit reports must be encoded with source URLs and coverage rules.
