# Claim Posture Audit

This audit summarizes which claim posture is cleared by the current source panels, validation results, and generated paper bundle. It is not a substitute for peer review; it is a guardrail against letting the manuscript drift from a mechanism-model article into a calibrated policy-simulation claim.

## Gate Summary

| Gate | Status | Evidence | Claim boundary | Next action |
| --- | --- | --- | --- | --- |
| Mechanism-model article | cleared | 0 validation misses, 0 unknown validations, 1 unresolved coverage-gap source panels, 7 usable but source-limited support panels, 0 article-blocking dependency claims not cleared | The manuscript can present a transparent mechanism model and synthetic stress tests under explicit source limits. | Keep empirical language tied to source moments, source gaps, and model diagnostics. |
| Empirical bridge | bounded | 0 source-gap validations, 1 unresolved weak-status panels, 7 usable but source-limited support panels; 5 bounded claim dependencies | The bridge constrains plausible ranges and flags evidence gaps; it does not validate hidden-channel magnitudes. | Prioritize SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, nonprofit-routing beyond the top-EIN Schedule I slice, and post-employment revolving-door overlays; broaden electoral-communication and public-financing rows as secondary coverage upgrades. |
| Calibrated policy-simulation claim | not_cleared | validation queue P1=0, P2=0; causal targets P1=4, P2=6; 1 claim dependencies not cleared; calibrated-policy dependency=not_cleared; open causal targets=10 | The current artifact should not claim calibrated reform effects or representative national hidden-channel magnitudes. | Clear the causal-calibration target matrix, add stronger source panels, and rerun validation before using calibrated policy-simulation language. |
| Reproducibility and layout bundle | cleared | layout failures=0, visual checklist=pass | The generated review bundle is reproducible when the paper artifact gate passes. | Rerun the full artifact gate after any source, table, figure, LaTeX, or package change. |

## Validation Counts

- Fit: `337`
- Partial: `0`
- Miss: `0`
- Source gap: `0`
- Unknown: `0`
- Not applicable: `21`

## Unresolved Coverage-Gap Source Panels

- Source panels with status thin, warning, fixture-only, or missing: `1`
- `OIRA EO 12866 meeting logs` (thin): EO 12866 meeting rows are present but too sparse for cross-agency access-concentration calibration; requestor-client disclosure share=0.4000, top-three requestor share=0.3000

## Usable But Source-Limited Support Panels

- Usable but source-limited support panels: `7`
- `Direct dark money` (direct-proxy-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Public financing` (program-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Intermediaries` (proxy-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Revolving door` (proxy-thin): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Procurement concentration panel` (denominator-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Procurement action history` (conditional-direct): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Procurement modification risk` (denominator-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.

## Claim-Source Dependencies

- Cleared claim dependencies: `4`
- Bounded claim dependencies: `5`
- Not-cleared claim dependencies: `1`
- `Strategic substitution mechanism` (bounded): Bounded by source-limited usable panels: Direct dark money (direct-proxy-bounded), Intermediaries (proxy-bounded), Revolving door (proxy-thin).
- `Public-financing counterweight` (bounded): Bounded by source-limited usable panels: Public financing (program-bounded).
- `Revolving-door access` (bounded): Bounded by source-limited usable panels: Revolving door (proxy-thin).
- `Hidden-channel magnitude` (bounded): Bounded by top-EIN Schedule I routing coverage and unobserved donor identities.
- `Procurement modification capture` (bounded): Denominator-mapped USAspending bulk rows support distributional diagnostics; SAM/FPDS coding reconciliation and causal capture validation remain future work.
- `Calibrated policy simulation` (not_cleared): Not cleared while 10 causal-calibration targets block policy simulation; current source panels support only mechanism diagnostics and bounded source moments.

## Causal Calibration Targets

- Blocking targets: `10`
- Blocking P1 targets: `4`
- Blocking P2 targets: `6`
- `hidden-donor-routing-magnitude` (P1, bounded_proxy_only): Broaden nonprofit-routing rows beyond the top-EIN slice and add donor-linkage or beneficial-owner coverage where public sources permit.
- `substitution-elasticity` (P1, open_design_needed): Build a cross-source event panel around one reform shock and track visible, intermediary, dark-money, comment, and procurement channels by actor and issue.
- `procurement-modification-causal-capture` (P1, denominator_mapped_not_causal): Crosswalk USAspending and SAM/FPDS modification codes, then add protest, exclusion, offer-count, and firewall overlays.
- `revolving-door-access-effect` (P1, bounded_proxy_only): Add OGE, FACA, witness, or personnel-movement exports and preserve person-entity identifiers for linkage.
- `public-financing-countervailing-effect` (P2, local_program_panel_only): Add state and local public-financing panels and link them to candidate finance and election context.
- `comment-authenticity-and-uptake-effect` (P2, bounded_source_moments): Add docket corpora with duplicate/template detection and link comments to agency response text or final-rule changes.
- Additional blocking targets: `4`; see `reports/causal-calibration-targets.md`.

## Validation-Queue P1/P2 Actions

- None. The validation-calibration queue is clear; calibrated policy-simulation remains blocked by the causal-calibration targets above.
