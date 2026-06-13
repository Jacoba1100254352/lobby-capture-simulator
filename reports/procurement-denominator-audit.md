# Procurement Denominator Audit

This audit explains the denominator behind procurement modification and concentration moments. It separates the active USAspending action panel from the optional SAM.gov Contract Awards route and from award-level bridge rows. The SAM.gov route supports synchronous non-adjacent offset page-index strata through `SAM_CONTRACT_AWARDS_OFFSET_STARTS` and asynchronous extract downloads through `SAM_CONTRACT_AWARDS_EXTRACT_MODE`; those rows strengthen the snapshot only when the resulting action-history panel is archived.

## Claim Boundary

The modification denominator is `usaspending-procurement-actions` with 28115 rows across 12 agencies. Its modified-action share is 0.4220; 8199 of 23819 distinct PIID/award identifiers have at least one modification (0.3442), with 1.4470 modified rows per modified award. The national concentration panel is `usaspending-procurement-national-actions` with 1500 rows across 17 agencies. In that panel, the largest agency accounts for 0.7153 of rows but 0.5889 of amount, and the largest recipient accounts for 0.1139 of amount. SAM.gov Contract Awards status is `missing` with 0 committed rows and promotion readiness `blocked`. The procurement-modification claim remains bounded until a representative SAM/FPDS action-history denominator is archived; the national panel improves concentration diagnostics but is not used as a representative modification-incidence denominator.

| Source | Status | Role | Rows | Agencies | Awards | Dates | PIID | UEI | Competition | Modified actions | Modified award share | Amt-wtd mod. | Promotion | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| usaspending-procurement-actions | ok | primary action denominator | 28115 | 12 | 23819 | 365d | 1.0000 | 1.0000 | 0.0000 | 0.4220 | 0.3442 | 0.6344 | not-applicable | bounded transaction/action diagnostics; not representative SAM/FPDS calibration |
| usaspending-procurement-national-actions | ok | national-volume concentration denominator | 1500 | 17 | 1343 | 365d | 1.0000 | 1.0000 | 0.0000 | 0.2533 | 0.1847 | 0.5907 | not-applicable | national USAspending action concentration diagnostic; not a modification-incidence denominator |
| sam-contract-awards | missing | optional SAM/FPDS-style action route | 0 | 0 | 0 | 0d | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | blocked | stronger source route only if active rows are archived in the frozen snapshot |
| usaspending-procurement-bridge | ok | multi-agency top-award bridge | 150 | 6 | 149 | n/a | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | not-applicable | concentration and competition diagnostic; not an action-history denominator |
| usaspending-awards | ok | EPA award-level surface | 200 | 1 | 198 | n/a | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | not-applicable | award identifier and competition surface; not an action-history denominator |
