# First-Wave Procurement Source Acquisition

This report turns the open procurement-calibration risk into source-specific acquisition tasks. It is not source evidence and does not clear calibrated procurement-capture claims. Its role is to make the next public-source panels concrete enough that future promotion can be audited.

## Summary

- Acquisition products: `5`
- Source-evidence status: `acquisition_plan_only`
- Claim boundary: `procurement modification, protest, exclusion, competition, and firewall rows remain bounded diagnostics until linked source products pass the first-wave source-product and source-readiness gates`
- Product statuses: `candidate_unreviewed=5`
- SAM export audit handling: `local_time_bound` - live SAM export-audit results are local, quota-dependent, and not embedded in the committed acquisition report unless INCLUDE_LOCAL_SAM_EXPORT_AUDIT=1 is set

## Promotion Rule

A row in this report is only an acquisition instruction. To promote a procurement source product, populate the corresponding file under `data/calibration/first-wave/`, preserve source URLs and extraction dates, run `make first-wave-source-products`, run `make first-wave-source-readiness`, then run `make paper-artifacts-check`. A successful SAM export audit or source download is not enough unless the product-level schema, semantic gates, and claim boundaries also pass.

## Source Plan

| Product | Product gate | Preferred official source | Required linkage | Current blocker |
| --- | --- | --- | --- | --- |
| sam-fpds-action-history-crosswalk | candidate_unreviewed | SAM.gov Contract Awards export or keyed Contract Awards API, reconciled against USAspending transaction rows (https://open.gsa.gov/api/contract-awards/) | PIID, UEI, awarding agency/subtier, recipient, action date, obligation, modification number/type, competition or extent-competed code, number of offers, USAspending record ID, SAM record ID, and crosswalk confidence | SAM.gov quota or extract-token availability can block acquisition; partial or diagnostic exports must not be promoted. SAM export audit handling: live SAM export-audit results are local, quota-dependent, and not embedded in the committed acquisition report unless INCLUDE_LOCAL_SAM_EXPORT_AUDIT=1 is set |
| gao-protest-overlay | candidate_unreviewed | GAO Recent Bid Protest Decisions, GAO Search Decisions & Docket, and GAO Legal Products XML feed (https://www.gao.gov/legal/bid-protests/recent; https://www.gao.gov/rss/reportslegal.xml) | Protest ID or B-number, agency, filed date where available, decision date, outcome, issue codes, source URL, and manually reviewed PIID/UEI/vendor linkage when available | The GAO feed can discover recent bid-protest decisions and hints, but decision pages do not reliably expose PIID/UEI fields in a machine-readable way, so award/vendor linkage and outcome/issue coding remain manual review tasks. |
| sam-exclusion-overlay | candidate_unreviewed | SAM.gov Exclusions API and SAM.gov Entity/Exclusions Extracts Download API (https://open.gsa.gov/api/exclusions-api/) | Exclusion ID, UEI, recipient/entity name, exclusion type, activation/start date, termination/end date, excluding agency, and source URL | Official API quota and extract access must be managed; the preflight records access state only, and broad extracts still require field normalization and source-date preservation. |
| procurement-firewall-overlay | candidate_unreviewed | Agency procurement-integrity rules, firewall memoranda, acquisition-policy supplements, inspector-general reports, and official policy archives (https://www.acquisition.gov/far/) | Firewall rule ID, agency, subtier, award type, effective date, covered officials, control type, coverage rule, and source URL | No single public API provides agency firewall controls, so acquisition is a curated document-review task over official sources. |
| procurement-offer-competition-enrichment | candidate_unreviewed | SAM.gov Contract Awards and USAspending transaction/action records where offer-count and competition fields are exposed (https://open.gsa.gov/api/) | PIID, UEI, agency, action date, award type, extent-competed code, number of offers, source system, source-system record ID, source URL, and crosswalk confidence | No reviewed standalone offer/competition source product has been promoted yet; committed USAspending action rows remain denominator context until source-system competition fields clear the gate. |

## Acquisition Details

### sam-fpds-action-history-crosswalk

- Expected path: `data/calibration/first-wave/sam-fpds-action-history-crosswalk.csv`
- Source-product status: `candidate_unreviewed`
- Preferred official source: SAM.gov Contract Awards export or keyed Contract Awards API, reconciled against USAspending transaction rows (https://open.gsa.gov/api/contract-awards/)
- Fallback: USAspending public transaction download strata already documented by the repository; use only as a bounded denominator until SAM/FPDS-style action coding is reconciled
- Required linkage: PIID, UEI, awarding agency/subtier, recipient, action date, obligation, modification number/type, competition or extent-competed code, number of offers, USAspending record ID, SAM record ID, and crosswalk confidence
- Acquisition step: After SAM quota reset, request a representative Contract Awards export, record the emailed link with make sam-contract-awards-record-export-link, then run make sam-procurement-refresh.
- Promotion gate: Export audit must report promotion-readiness=candidate; then make first-wave-source-products, make first-wave-source-readiness, and make paper-artifacts-check must pass.
- Claim boundary: A SAM/FPDS action-history crosswalk can improve procurement denominator validity; it does not by itself estimate capture effects without exposure timing and comparison design.

### gao-protest-overlay

- Expected path: `data/calibration/first-wave/gao-protest-overlay.csv`
- Source-product status: `candidate_unreviewed`
- Preferred official source: GAO Recent Bid Protest Decisions, GAO Search Decisions & Docket, and GAO Legal Products XML feed (https://www.gao.gov/legal/bid-protests/recent; https://www.gao.gov/rss/reportslegal.xml)
- Fallback: Run make gao-protest-feed-preflight against the GAO Legal Products XML feed for ignored discovery, or make gao-protest-overlay-candidates to materialize likely protest rows into the tracked overlay with candidateOnly=true; the parser extracts B-numbers, decision dates, protester names, agency hints, awardee hints, coarse issue-code hints, and visible outcome language before source-page review
- Required linkage: Protest ID or B-number, agency, filed date where available, decision date, outcome, issue codes, source URL, and manually reviewed PIID/UEI/vendor linkage when available
- Acquisition step: Run make gao-protest-overlay-candidates to refresh the candidate-only GAO protest review queue, review the high-priority rows against official decision pages or PDFs, then manually link decisions to PIID, UEI or vendor, agency, filed date, outcome, and issue fields before promotion.
- Promotion gate: Each row needs a source URL plus PIID or vendor linkage; unmatched protests remain context rows and cannot clear the product gate.
- Claim boundary: GAO protest rows measure observed dispute outcomes; this source does not identify lobbying exposure or capture without linked award/action and actor records.

### sam-exclusion-overlay

- Expected path: `data/calibration/first-wave/sam-exclusion-overlay.csv`
- Source-product status: `candidate_unreviewed`
- Preferred official source: SAM.gov Exclusions API and SAM.gov Entity/Exclusions Extracts Download API (https://open.gsa.gov/api/exclusions-api/)
- Fallback: Run make sam-exclusions-preflight for a redacted quota/access check; use SAM_Exclusions_Public_Extract files from the official Entity/Exclusions Extracts API when a broad public extract is preferable
- Required linkage: Exclusion ID, UEI, recipient/entity name, exclusion type, activation/start date, termination/end date, excluding agency, and source URL
- Acquisition step: Run make sam-exclusions-preflight before source acquisition, then use the Exclusions API for targeted UEI/entity checks or the public exclusion extract for a broader panel; keep API keys in .env and archive only normalized public rows.
- Promotion gate: Rows must carry UEI linkage, timing, exclusion type, and source provenance; active-only or missing-date rows cannot clear the causal source gate.
- Claim boundary: Exclusions separate integrity-enforcement status from procurement outcomes; they are not proof of capture or corruption.

### procurement-firewall-overlay

- Expected path: `data/calibration/first-wave/procurement-firewall-overlay.csv`
- Source-product status: `candidate_unreviewed`
- Preferred official source: Agency procurement-integrity rules, firewall memoranda, acquisition-policy supplements, inspector-general reports, and official policy archives (https://www.acquisition.gov/far/)
- Fallback: Agency acquisition-policy pages and inspector-general/audit reports with source URLs and effective dates
- Required linkage: Firewall rule ID, agency, subtier, award type, effective date, covered officials, control type, coverage rule, and source URL
- Acquisition step: Start with the agencies represented in the action-history crosswalk, then encode dated procurement-integrity controls and coverage rules for the relevant award classes.
- Promotion gate: At least one dated control rule with agency and covered-official fields is required; generic policy descriptions without dates stay as notes.
- Claim boundary: Firewall rows represent observed institutional controls; they do not establish compliance or enforcement without audit or outcome linkage.

### procurement-offer-competition-enrichment

- Expected path: `data/calibration/first-wave/procurement-offer-competition-enrichment.csv`
- Source-product status: `candidate_unreviewed`
- Preferred official source: SAM.gov Contract Awards and USAspending transaction/action records where offer-count and competition fields are exposed (https://open.gsa.gov/api/)
- Fallback: Award-detail and latest-transaction fields from USAspending, retained as directional context when action-history fields are absent
- Required linkage: PIID, UEI, agency, action date, award type, extent-competed code, number of offers, source system, source-system record ID, source URL, and crosswalk confidence
- Acquisition step: Populate the standalone offer/competition enrichment product from SAM/FPDS or USAspending rows with observed source competition fields, then reconcile it with the action-history crosswalk.
- Promotion gate: The source-product gate requires at least 5,000 rows, at least 1,000 distinct PIIDs, at least six agencies, at least two competition codes, nonempty source provenance, and high offer-count coverage.
- Claim boundary: Competition enrichment supports controls and stratification; it is not an independent capture outcome.

## Official Source Notes

- GAO Recent Bid Protest Decisions and Search Decisions & Docket are the official protest-discovery surfaces; the GAO Legal Products XML feed can be used as a machine-readable discovery queue for new protest decisions. The local preflight extracts discovery hints only; `make gao-protest-overlay-candidates` can copy likely protest rows into `data/calibration/first-wave/gao-protest-overlay.csv` with `candidateOnly=true`, and those rows remain non-evidence until reviewed source-page and award/vendor linkages replace the candidate markers.
- SAM.gov Exclusions API returns public exclusion records in paginated JSON and can also initiate CSV/JSON extracts; the Entity/Exclusions Extracts API can download public exclusion extracts such as `SAM_Exclusions_Public_Extract` files. The local `make sam-exclusions-preflight` target records redacted quota/access state only and does not promote exclusion rows.
- SAM.gov Contract Awards remains the preferred source for Contract Awards action-history fields; USAspending transaction/action rows remain a bounded fallback until SAM/FPDS-style definitions are reconciled.
- SAM export next action: Record a fresh emailed SAM export link, run make sam-contract-awards-export-audit, and inspect reports/sam-contract-awards-export-audit.* before attempting promotion.
- Procurement firewall coverage is a document-review product, not an API product. Dated agency policies, acquisition supplements, firewall memoranda, and official audit reports must be encoded with source URLs and coverage rules.
