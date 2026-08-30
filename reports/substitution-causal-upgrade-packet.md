# Substitution Causal Upgrade Packet

This generated packet consolidates the open substitution-elasticity causal-calibration target, HLOGA reform-shock anchor, reviewed exact-ID actor-time slice, treated/control comparison-assignment rows, meeting/contact missingness boundary, and remaining effect-estimation blockers. It is a handoff control, not effect evidence, and it does not clear calibrated policy-simulation or causal substitution-elasticity claims.

## Summary

- Generated at: `2026-06-19T00:00:00Z`
- Release tag: `paper-publication-readiness-2026-06-19-r208`
- Release date: `2026-06-19`
- Target: `substitution-elasticity`
- Target status: `open_design_needed`
- Policy-claim status: `not_cleared`
- Blocks calibrated policy simulation: `yes`
- Protocol status: `protocol_ready_source_pending`
- Source readiness: `source_products_ready_substitution_design_only`
- Source-product gate: `schema_gate_ready`
- Source-product statuses: `schema_ready=3; text_ready=1`
- Candidate worklists, not evidence: `0`
- Reviewed, design, or missing-channel boundary products, not effect evidence: `4`
- Effect-model and falsification gate: `effect_model_and_falsification_gates_not_cleared`
- Overall claim boundary: `mechanism stress tests and qualitative substitution warnings only; no causal substitution-elasticity estimate clears from this packet`

## Current Claim Boundary

- Current support: Synthetic mechanism comparison, sensitivity sweeps, and source moments for individual channels
- Permitted use: Mechanism stress tests and qualitative substitution warnings
- Allowed current claim: The current manuscript may use this target for mechanism stress tests and qualitative substitution warnings only, under the stated source and design limits.
- Barred claim: Do not claim that current evidence estimates the change in alternate-channel spending, contact, or influence pressure after a disclosure, finance, access, or cooling-off reform binds or clears calibrated policy-simulation effects.
- Claim-upgrade trigger: Upgrade only after: At least one external quasi-experimental or panel design that estimates cross-channel substitution direction for a named reform family
- Clearance criterion: At least one external quasi-experimental or panel design that estimates cross-channel substitution direction for a named reform family

## Causal Design Requirements

- Unit of analysis: actor-issue-month or actor-issue-quarter
- Treatment or shock: binding disclosure, access, finance, cooling-off, or venue-integrity reform affecting one actor/issue set before comparable alternatives
- Comparison design: event-study or difference-in-differences panel with matched unaffected actors, issues, or jurisdictions
- Primary outcomes: visible lobbying spend/contact, outside spending, docket submissions, procurement activity, intermediary routing, and hidden/substitution proxy load
- Linkage keys: canonical actor id, issue code, client name, committee/spender id, docket id, UEI/recipient id, jurisdiction, and event date
- Minimum sources: LDA clients, OpenFEC spenders, Regulations.gov/Federal Register dockets, procurement vendors, meeting logs or nonprofit/intermediary rows
- Falsification checks: pre-trend tests, placebo reform dates, unaffected issue placebo rows, and actor types not plausibly exposed to the reform
- Sensitivity checks: alternative event windows, actor matching rules, issue-code coarsening, and exclusion of high-outlier spenders
- Threat model: simultaneous political shocks, endogenous reform adoption, entity-resolution errors, and unobserved private contacts

## Shock-Window Consistency

- Reform event: hloga-2007-federal-lobbying-disclosure treatmentStartDate=2007-09-14
- Actor-time source window: 2007-01-01 to 2024-12-31 (2770 dated rows)
- Actor-time pre/post coverage: preRows=458; postRows=2176
- Assignment coverage: treatedOrExposedRows=41; comparisonOrControlRows=30; excludedRows=499
- Estimation consequence: shock-window and assignment scaffolds are present; estimation still depends on the source-readiness, leakage, falsification, and artifact gates.
- Historical source-access probe: not run; optional live diagnostic target is `make substitution-historical-source-access`.

## Effect-Model Diagnostic Result

- Overall diagnostic gate: `effect_model_and_falsification_gates_not_cleared`
- Primary descriptive contrast: estimate=`-0.289940`; actor-bootstrap 95% interval=`[-1.237307, 0.343357]`; status=`diagnostic_only`
- Pre-trend diagnostic: estimate=`0.450966`; status=`not_testable_as_trend`
- Clean placebo diagnostic: estimate=`0.450966`; status=`does_not_reassure`
- Leave-one-actor diagnostic: range=`[-0.343165, 0.111013]`; status=`failed`
- Interpretation: the source-ready panel is sufficient to run the first descriptive estimator, but treatment/source confounding, incompatible outcome semantics, issue-code mismatch, two clean pre quarters, non-independent placebo evidence, interval uncertainty, and a leave-one-actor sign reversal keep the effect-model and falsification gates closed.
- Detailed packet: `reports/substitution-estimation-diagnostics.md`
- Claim consequence: `diagnostic preparation and failure-mode evidence only; no causal HLOGA effect or cross-channel substitution elasticity`

## Promotion Dependency Matrix

| Product | Design role | Status | Rows | Shortfall | Evidence gate | Required linkage | Promotion requirement |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| named reform-shock event file | reform_shock_design_anchor | schema_ready | 1 | 0 | schema_ready_design_anchor_not_effect_evidence | reformEventId; eventName; jurisdiction; policyDomain; reformType; eventDate; treatmentStartDate; affectedActorRule; affectedIssueRule; comparisonRule; sourceUrl; sourceExtractedAt | Retain the HLOGA source provenance, but do not treat a dated reform row as effect evidence; the row is not observed substitution evidence; provision-specific treatment windows and matched actor-issue outcomes must be adjudicated first. |
| canonical actor-issue-time spine across at least three venues | cross_channel_outcome_spine | schema_ready | 2770 | 0 | reviewed_treated_control_actor_time_panel_source_ready_not_effect_clearance | canonicalActorId; issueCode; periodStart; periodEnd; venue; activityType; activityMeasure; activityAmount; sourceSystem; sourceRecordId; exposureGroup; reformEventId | The actor-time spine now preserves reviewed exact-ID source links, observed HLOGA pre/post treated LDA rows, and Colorado state-lobbying control rows. It is a source-ready design input, not effect evidence; estimation still requires the pre-specified model, falsification checks, sensitivity checks, and review before any claim upgrade. |
| pre/post comparison groups for exposed and unaffected actors or jurisdictions | treated_and_comparison_assignment | schema_ready | 570 | 0 | reviewed_treated_control_assignment_source_ready_not_effect_clearance | reformEventId; canonicalActorId; issueCode; comparisonGroup; matchingVariables; prePeriodStart; prePeriodEnd; postPeriodStart; postPeriodEnd | The assignment file now separates treated federal LDA clients, Colorado unaffected-jurisdiction controls, and excluded rows with observed pre/post source windows. It clears the source-product design gate only; effect estimation and calibrated policy claims remain barred until model and falsification results are reviewed. |
| meeting-log or contact-register panel, or explicit missing-channel design note | access_channel_missingness_boundary | text_ready | 74 | 0 | missing_channel_design_note_not_estimation_panel | text terms: meeting; missing; substitution | Keep this as an omitted-channel boundary unless a broader machine-readable meeting/contact panel with actor, issue, date, source-record, completeness, and outcome linkage fields is added. |

## Manual Review Queue

| Product | Candidate rows | Reviewed rows | First review focus | Promotion blockers |
| --- | ---: | ---: | --- | --- |
| named reform-shock event file | 0 |  | Retain source provenance, rerun the source-product and source-readiness gates after edits, and keep the claim boundary attached before using this product in a protocol. | Required schema columns, field-level quality checks, and semantic gates pass. |
| canonical actor-issue-time spine across at least three venues | 0 |  | Retain source provenance, rerun the source-product and source-readiness gates after edits, and keep the claim boundary attached before using this product in a protocol. | Required schema columns, field-level quality checks, and semantic gates pass. |
| pre/post comparison groups for exposed and unaffected actors or jurisdictions | 0 |  | Retain source provenance, rerun the source-product and source-readiness gates after edits, and keep the claim boundary attached before using this product in a protocol. | Required schema columns, field-level quality checks, and semantic gates pass. |
| meeting-log or contact-register panel, or explicit missing-channel design note | 0 |  | Retain source provenance, rerun the source-product and source-readiness gates after edits, and keep the claim boundary attached before using this product in a protocol. | Text source product contains the required missing-channel design terms. |

## Candidate Leakage Boundary

- Manual-adjudication burden: candidateProducts=5; candidateRows=100; markerRows=100; reviewedRows=0; reviewerDateGaps=80; minimumRowShortfalls=4; priorities=P1=4; P2=1
- Candidate-review triage: triageRows=0; priorities=none; evidenceClasses=0; riskFlags=0; candidateProductsWithoutPriority=5
- Leakage boundary: The remaining empirical work is measurable manual adjudication, not untracked missingness: candidate files identify source-product rows that must be reviewed before promotion.
- Interpretation: actor-issue-time rows now contain reviewed exact-ID source links plus observed treated and control pre/post rows, and comparison-group rows separate treated, control, and excluded assignments. They are source-ready design inputs, not effect estimates. The first estimator and falsification packet now exists, but its structural, pre-trend, placebo, uncertainty, and leave-one-actor gates do not clear effect or calibrated policy claims.

## Access-Channel Missingness

The meeting/contact note clears only a design-note requirement. It records that private or semi-private access is mostly unobserved, that the thin public meeting surface is not a representative contact-register panel, and that future substitution designs must compare excluded, latent, LDA-proxied, and thin-public-meeting sensitivity cases before any stronger claim.

## Regeneration Rule

After any source-product edit, rerun `make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan substitution-estimation-diagnostics substitution-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check`. A HLOGA reform-shock row, an actor-time refresh, or a comparison-group refresh is not enough unless the source-product, readiness, estimator, falsification, sensitivity, leakage, and artifact gates all pass.
