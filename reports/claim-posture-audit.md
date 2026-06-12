# Claim Posture Audit

This audit summarizes which claim posture is cleared by the current source panels, validation results, and generated paper bundle. It is not a substitute for peer review; it is a guardrail against letting the manuscript drift from a mechanism-model article into a calibrated policy-simulation claim.

## Gate Summary

| Gate | Status | Evidence | Claim boundary | Next action |
| --- | --- | --- | --- | --- |
| Mechanism-model article | cleared | 0 validation misses, 0 unknown validations, 2 weak source panels bounded by claim audit, 3 dependency claims not cleared | The manuscript can present a transparent mechanism model and synthetic stress tests under explicit source limits. | Keep empirical language tied to source moments, source gaps, and model diagnostics. |
| Empirical bridge | bounded | 4 source-gap validations and 2 thin, warning, fixture-only, or missing panels; 1 bounded claim dependencies | The bridge constrains plausible ranges and flags evidence gaps; it does not validate hidden-channel magnitudes. | Prioritize direct dark-money rows, representative SAM/FPDS procurement action histories, and post-employment revolving-door overlays; broaden electoral-communication and public-financing rows as secondary coverage upgrades. |
| Calibrated policy-simulation claim | not_cleared | 4 P1 and 0 P2 calibration/source actions remain; 3 claim dependencies not cleared | The current artifact should not claim calibrated reform effects or representative national hidden-channel magnitudes. | Clear P1/P2 source gaps and rerun calibration before using calibrated policy-simulation language. |
| Reproducibility and layout bundle | cleared | layout failures=0, visual checklist=pass | The generated review bundle is reproducible when the paper artifact gate passes. | Rerun the full artifact gate after any source, table, figure, LaTeX, or package change. |

## Validation Counts

- Fit: `309`
- Partial: `34`
- Miss: `0`
- Source gap: `4`
- Unknown: `0`
- Not applicable: `11`

## Weak Source Panels

- Weak panels: `2`
- `Direct dark money` (fixture-only): no non-proxy direct DARK_MONEY routing rows in the snapshot; fixture bridge is available but not article-level empirical coverage
- `Procurement modification risk` (thin): stratified transaction-action rows are present, but modification incidence remains too high for calibration-grade national inference

## Claim-Source Dependencies

- Cleared claim dependencies: `6`
- Bounded claim dependencies: `1`
- Not-cleared claim dependencies: `3`
- `Strategic substitution mechanism` (bounded): Bounded by weak panels: Direct dark money (fixture-only).
- `Hidden-channel magnitude` (not_cleared): Not cleared because of weak panels: Direct dark money (fixture-only); missing moment thresholds: darkMoneyDirectRoutingRows<1.
- `Procurement modification capture` (not_cleared): Not cleared because of weak panels: Procurement modification risk (thin).
- `Calibrated policy simulation` (not_cleared): Not cleared because of weak panels: Direct dark money (fixture-only), Procurement modification risk (thin); missing moment thresholds: darkMoneyDirectRoutingRows<1.

## P1/P2 Calibration Actions

- `darkMoneyDirectRoutingRows` (P1, direct-source-moment): add non-proxy direct hidden-donor, transfer, or nonprofit-routing records; keep IRS EO BMF capacity proxies and electoral-communication rows separate
- `procurementAgencyTop1Share` (P1, direct-source-moment): replace the bounded USAspending concentration panel with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated
- `procurementExPostModificationShare` (P1, direct-source-moment): broaden the bounded USAspending action panel with representative SAM/FPDS action histories before treating modification incidence as calibrated
- `procurementRecipientTop3Share` (P1, direct-source-moment): compare recipient concentration against the bounded procurement concentration panel, then broaden by award type and fiscal year before treating it as calibrated
