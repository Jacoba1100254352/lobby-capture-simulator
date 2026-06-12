# Procurement Denominator Audit

This audit explains the denominator behind procurement modification and concentration moments. It separates the active USAspending action panel from the optional SAM.gov Contract Awards route and from award-level bridge rows. The SAM.gov route supports synchronous non-adjacent offset page-index strata through `SAM_CONTRACT_AWARDS_OFFSET_STARTS` and asynchronous extract downloads through `SAM_CONTRACT_AWARDS_EXTRACT_MODE`; those rows strengthen the snapshot only when the resulting action-history panel is archived.

## Claim Boundary

The active action denominator is `usaspending-procurement-actions` with 28115 rows across 12 agencies. Its modified-action share is 0.4220; 8199 of 23819 distinct PIID/award identifiers have at least one modification (0.3442), with 1.4470 modified rows per modified award. The largest agency accounts for 0.0854 of rows but 0.4609 of amount, a row-to-amount gap of 0.3755. SAM.gov Contract Awards status is `missing` with 0 committed rows. The procurement-modification claim remains bounded until a representative SAM/FPDS action-history denominator is archived; the balanced row-count sample is useful for schema checks, but not volume-representative calibration.

| Source | Status | Role | Rows | Agencies | PIID | UEI | Initial actions | Modified actions | Modified award share | Rows/mod. award | Amt-wtd mod. | Top agency amount | Top agency rows | Top recipient amount | Boundary |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| usaspending-procurement-actions | ok | primary action denominator | 28115 | 12 | 1.0000 | 1.0000 | 0.5780 | 0.4220 | 0.3442 | 1.4470 | 0.6344 | 0.4609 | 0.0854 | 0.0812 | bounded transaction/action diagnostics; not representative SAM/FPDS calibration |
| sam-contract-awards | missing | optional SAM/FPDS-style action route | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | stronger source route only if active rows are archived in the frozen snapshot |
| usaspending-procurement-bridge | ok | multi-agency top-award bridge | 150 | 6 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0067 | 1.0000 | 0.5134 | 0.1667 | 0.1196 | concentration and competition diagnostic; not an action-history denominator |
| usaspending-awards | ok | EPA award-level surface | 200 | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0668 | award identifier and competition surface; not an action-history denominator |
