# Claim Posture Audit

This audit summarizes which claim posture is cleared by the current source panels, validation results, and generated paper bundle. It is not a substitute for peer review; it is a guardrail against letting the manuscript drift from a mechanism-model article into a calibrated policy-simulation claim.

## Gate Summary

| Gate | Status | Evidence | Claim boundary | Next action |
| --- | --- | --- | --- | --- |
| Mechanism-model article | cleared | 0 validation misses, 0 unknown validations, 1 weak source panels bounded by claim audit, 2 dependency claims not cleared | The manuscript can present a transparent mechanism model and synthetic stress tests under explicit source limits. | Keep empirical language tied to source moments, source gaps, and model diagnostics. |
| Empirical bridge | bounded | 2 source-gap validations and 1 thin, warning, fixture-only, or missing panels; 1 bounded claim dependencies | The bridge constrains plausible ranges and flags evidence gaps; it does not validate hidden-channel magnitudes. | Prioritize procurement benchmark/coding crosswalks, broaden nonprofit-routing beyond the top-EIN Schedule I slice, and add post-employment revolving-door overlays; broaden electoral-communication and public-financing rows as secondary coverage upgrades. |
| Calibrated policy-simulation claim | not_cleared | 2 P1 and 0 P2 calibration/source actions remain; 2 claim dependencies not cleared | The current artifact should not claim calibrated reform effects or representative national hidden-channel magnitudes. | Clear P1/P2 source gaps and rerun calibration before using calibrated policy-simulation language. |
| Reproducibility and layout bundle | cleared | layout failures=0, visual checklist=pass | The generated review bundle is reproducible when the paper artifact gate passes. | Rerun the full artifact gate after any source, table, figure, LaTeX, or package change. |

## Validation Counts

- Fit: `325`
- Partial: `18`
- Miss: `0`
- Source gap: `2`
- Unknown: `0`
- Not applicable: `13`

## Weak Source Panels

- Weak panels: `1`
- `Procurement modification risk` (thin): archived USAspending bulk rows are present, but modification incidence remains outside the benchmark until denominator and coding definitions are remapped; distinct-award share=0.1067, amount-weighted share=0.5955

## Claim-Source Dependencies

- Cleared claim dependencies: `7`
- Bounded claim dependencies: `1`
- Not-cleared claim dependencies: `2`
- `Hidden-channel magnitude` (bounded): Bounded by top-EIN Schedule I routing coverage and unobserved donor identities.
- `Procurement modification capture` (not_cleared): Not cleared because of weak panels: Procurement modification risk (thin).
- `Calibrated policy simulation` (not_cleared): Not cleared because of weak panels: Procurement modification risk (thin).

## P1/P2 Calibration Actions

- `procurementExPostModificationShare` (P1, direct-source-moment): use the archived USAspending bulk action-row, distinct-award, and amount-weighted modification diagnostics to remap the benchmark; add SAM/FPDS action-history exports only to crosswalk USAspending modification coding before treating modification incidence as calibrated
- `procurementRecipientTop3Share` (P1, direct-source-moment): use the archived USAspending bulk summary for public concentration diagnostics, then remap the top-contractor benchmark by award type, agency mix, and fiscal year before treating recipient concentration as calibrated
