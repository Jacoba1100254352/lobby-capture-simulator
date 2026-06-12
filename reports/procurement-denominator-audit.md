# Procurement Denominator Audit

This audit explains the denominator behind procurement modification and concentration moments. It separates the active USAspending action panel from the optional SAM.gov Contract Awards route and from award-level bridge rows.

## Claim Boundary

The active action denominator is `usaspending-procurement-actions` with 2399 rows across 12 agencies. Its modified-action share is 0.3297. SAM.gov Contract Awards status is `missing` with 0 committed rows. The procurement-modification claim remains bounded until a representative SAM/FPDS action-history denominator is archived.

| Source | Status | Role | Rows | Agencies | PIID | UEI | Initial | Modified | Amt-wtd mod. | Top agency | Top recipient | Boundary |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| usaspending-procurement-actions | ok | primary action denominator | 2399 | 12 | 1.0000 | 1.0000 | 0.6703 | 0.3297 | 0.6141 | 0.3866 | 0.1123 | bounded transaction/action diagnostics; not representative SAM/FPDS calibration |
| sam-contract-awards | missing | optional SAM/FPDS-style action route | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | stronger source route only if active rows are archived in the frozen snapshot |
| usaspending-procurement-bridge | ok | multi-agency top-award bridge | 150 | 6 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 0.5134 | 0.1196 | concentration and competition diagnostic; not an action-history denominator |
| usaspending-awards | ok | EPA award-level surface | 200 | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0668 | award identifier and competition surface; not an action-history denominator |
