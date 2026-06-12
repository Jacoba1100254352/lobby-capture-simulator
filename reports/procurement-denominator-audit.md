# Procurement Denominator Audit

This audit explains the denominator behind procurement modification and concentration moments. It separates the active USAspending action panel from the optional SAM.gov Contract Awards route and from award-level bridge rows. The SAM.gov route supports non-adjacent offset strata through `SAM_CONTRACT_AWARDS_OFFSET_STARTS`; those rows strengthen the snapshot only when the resulting action-history panel is archived.

## Claim Boundary

The active action denominator is `usaspending-procurement-actions` with 2399 rows across 12 agencies. Its modified-action share is 0.3297; 467 of 2058 distinct PIID/award identifiers have at least one modification (0.2269), with 1.6938 modified rows per modified award. The largest agency accounts for 0.0834 of rows but 0.3866 of amount, a row-to-amount gap of 0.3032. SAM.gov Contract Awards status is `missing` with 0 committed rows. The procurement-modification claim remains bounded until a representative SAM/FPDS action-history denominator is archived; the balanced row-count sample is useful for schema checks, but not volume-representative calibration.

| Source | Status | Role | Rows | Agencies | PIID | UEI | Initial actions | Modified actions | Modified award share | Rows/mod. award | Amt-wtd mod. | Top agency amount | Top agency rows | Top recipient amount | Boundary |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| usaspending-procurement-actions | ok | primary action denominator | 2399 | 12 | 1.0000 | 1.0000 | 0.6703 | 0.3297 | 0.2269 | 1.6938 | 0.6141 | 0.3866 | 0.0834 | 0.1123 | bounded transaction/action diagnostics; not representative SAM/FPDS calibration |
| sam-contract-awards | missing | optional SAM/FPDS-style action route | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | stronger source route only if active rows are archived in the frozen snapshot |
| usaspending-procurement-bridge | ok | multi-agency top-award bridge | 150 | 6 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0067 | 1.0000 | 0.5134 | 0.1667 | 0.1196 | concentration and competition diagnostic; not an action-history denominator |
| usaspending-awards | ok | EPA award-level surface | 200 | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0668 | award identifier and competition surface; not an action-history denominator |
