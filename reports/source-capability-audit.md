# Source Capability Audit

This audit separates implemented live-source routes from the empirical support actually present in the committed 2024 snapshot. It is a process guardrail: an implemented importer does not support manuscript claims unless the frozen snapshot contains usable rows and the claim ledger permits the claim. Direct hidden-donor and SAM/FPDS action-history routes remain especially important claim boundaries.

## Summary

- active-representative: `1`
- active-usable: `5`
- implemented-not-promoted: `1`
- planned-overlay: `1`
- quota-blocked: `1`

## Key implemented routes

- Direct dark-money routing: configured `DARK_MONEY_LIVE_CSV`/`DARK_MONEY_LIVE_URL`, ProPublica Schedule I nonprofit-routing rows, and IRS EO BMF opaque-capacity proxies remain separate evidence classes.
- SAM/FPDS action-history route: downloaded `SAM_CONTRACT_AWARDS_LIVE_CSV`/`SAM_CONTRACT_AWARDS_LIVE_URL` exports, including SAM.gov emailed `api_key=REPLACE_WITH_API_KEY` download links, or keyed `SAM_API_KEY` runs can use `SAM_CONTRACT_AWARDS_EXTRACT_MODE` for asynchronous extracts and `SAM_CONTRACT_AWARDS_OFFSET_STARTS` for non-adjacent synchronous page-index strata.
- SAM.gov Exclusions route: `make sam-exclusions-preflight` records redacted quota/access/sample-shape status for the exclusion-overlay acquisition path, but no exclusion rows support claims until a reviewed calibration CSV is promoted.
- USAspending procurement route: no-key action, national action, and bulk-summary panels remain separate from SAM.gov Contract Awards rows so procurement provenance is auditable.
- Revolving-door route: LDA covered-position rows support exposure diagnostics, but documented post-employment movement still requires an additional personnel source.

| Capability | Snapshot source | Rows | Panel status | Capability status | Snapshot quality | Snapshot plan | Needed for | Next action |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| direct-dark-money-routing | dark-money (ok) | 330 | usable | active-usable | not-applicable | normalized IRS EO BMF opaque-capacity proxy rows written; ProPublica Nonprofit Explorer Schedule I nonprofit-routing rows appended | Hidden-channel magnitude and calibrated policy-simulation claims | Broaden nonprofit-routing beyond the bounded top-EIN Schedule I slice and keep these transfer rows separate from Schedule E, electioneering, communication-cost, IRS BMF capacity proxies, and hidden-donor identity claims. |
| sam-contract-awards-action-history | sam-contract-awards (quota_blocked) | 0 | usable | quota-blocked | blocked | SAM.gov quota blocked until 2026-Jun-20 00:00:00+0000 UTC; mode=1; format=json; filterCount=12; pageSize=100; maxPages=1; offsetPageStarts=0+10+50; fallback=USAspending action rows | Procurement modification capture and calibrated policy-simulation claims | Use the archived USAspending bulk summary for public modification diagnostics; add a SAM/FPDS pull or configured export to crosswalk modification coding, exclusions, offer counts, protests, and firewalls. |
| sam-exclusions-overlay | not-promoted (not-promoted) | 0 | not-promoted | implemented-not-promoted | not-applicable | No active committed rows. | Procurement integrity controls and exclusion overlays for procurement modification causal-calibration claims | After SAM quota resets, run make sam-exclusions-preflight, then populate reviewed sam-exclusion-overlay rows with UEI, recipient, exclusion type, dates, agency, cause, and source provenance before rerunning first-wave gates. |
| usaspending-stratified-action-panel | usaspending-procurement-actions (ok) | 28103 | usable | active-usable | not-applicable | normalized USAspending procurement action rows written after SAM fallback | Bounded procurement concentration and modification diagnostics | Broaden beyond the selected 12-agency quarterly stress panel before treating modification incidence as calibration-grade. |
| usaspending-national-action-panel | usaspending-procurement-national-actions (ok) | 1500 | usable | active-usable | not-applicable | normalized national-volume USAspending procurement action rows written; agencyFilter=ALL; periodBuckets=annual; pageSize=100; maxPages=5; sortSpecs=Transaction Amount:desc;Mod:asc;Action Date:asc | Stronger public procurement concentration diagnostics | Use this no-key national-volume panel as a fallback concentration diagnostic; prefer the archived bulk summary when present and keep modification incidence blocked on benchmark/coding reconciliation. |
| usaspending-bulk-transaction-download-panel | usaspending-procurement-bulk-summary (present) | 6449101 | usable | active-representative | not-applicable | Active rows are present in the frozen snapshot. | Procurement modification denominator robustness and calibrated policy-simulation claim review | Use the compact frozen summary for public transaction-history diagnostics; archive the full normalized CSV/ZIP payloads externally only when full byte-for-byte reproduction is required. |
| lda-covered-position-revolving-door | revolving-door (ok) | 803 | usable | active-usable | not-applicable | derived normalized covered-position rows from LDA source | Revolving-door access mechanism diagnostics | Supplement with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel-movement exports before claiming representative post-employment movement. |
| irs-527-political-organizations | intermediary (ok) | 1353 | usable | active-usable | not-applicable | NYC CFB intermediary rows; IRS EO BMF nonprofit/association capacity rows; IRS POFD Form 8872 527 rows | Intermediary and campaign-adjacent substitution diagnostics | Broaden beyond the bounded alphabetic slice while preserving 527 rows as distinct from 501(c)(4)/(c)(6) dark-money evidence. |
| licensed-access-overlays | not-promoted (not-promoted) | 0 | not-promoted | planned-overlay | not-applicable | No active committed rows. | Representative hidden-channel, intermediary, and personnel-movement validation | Implement importer-specific schemas only after licensing and export fields are fixed enough to preserve reproducibility. |
