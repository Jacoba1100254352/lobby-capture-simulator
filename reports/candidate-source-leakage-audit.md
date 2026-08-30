# Candidate Source Leakage Audit

This generated audit verifies that candidate-only first-wave source-product worklists remain blocked from estimation readiness and calibrated policy-simulation claims.

## Summary

- Overall status: `pass`
- Failures: `0`
- Candidate marker state: `candidate_unreviewed`
- Required readiness boundary: `readyToEstimate=0`
- Required policy boundary: `calibratedPolicy=blocked`

## Checks

| Item | Status | Value | Threshold | Notes | Next action |
| --- | --- | --- | --- | --- | --- |
| candidate-file-markers | pass | candidateProducts=5; candidateRows=100; markerRows=100; missingFiles=0; unmarkedFiles=0 | candidateProducts>0; missingFiles=0; unmarkedFiles=0 | Candidate-only source-product files retain candidateOnly=true, candidate_unreviewed, or equivalent manual-review markers. | Do not remove candidate markers until the matching manual promotion checklist is completed and the source-product/readiness reports are regenerated. |
| manual-adjudication-burden | pass | candidateProducts=5; candidateRows=100; markerRows=100; reviewedRows=0; reviewerDateGaps=80; minimumRowShortfalls=4; priorities=P1=4; P2=1 | candidateRows=markerRows; reviewedRows=0 while candidate gate is active | The remaining empirical work is measurable manual adjudication, not untracked missingness: candidate files identify source-product rows that must be reviewed before promotion. | Prioritize the largest P1/P2 candidate products, replace candidate markers with reviewed source rows, and rerun first-wave source-product, readiness, candidate-leakage, and artifact gates before strengthening claims. |
| candidate-review-triage | pass | triageRows=0; priorities=none; evidenceClasses=0; riskFlags=0; candidateProductsWithoutPriority=5 | invalidPriorities=0; entity-resolution priority files have priority fields when candidate-active | Candidate rows with review-priority fields remain deterministic triage queues; remaining procurement or comment source-surface worklists may instead carry product-specific acquisition notes. | Use any P1 rows as the first manual adjudication queue; do not treat reviewPriorityScore as adjudicated match confidence. For candidate products without priority fields, use the product-level manual adjudication plan. |
| cross-venue-adjudication-boundary | pass | acceptedActors=491; acceptedRecords=1063; acceptedVenues=3; acceptedSourceSystems=3; heldActors=57; rejectedActors=519; readyToEstimate=0; policyClearances=0 | acceptedActors>0; acceptedRecords>0; readyToEstimate=0; policyClearances=0 | Reviewed cross-venue identifier evidence may coexist with candidate-only source products only when the broader source-readiness and calibrated-policy boundaries remain blocked. | Use the adjudication ledger as reviewed evidence for the first exact-ID slice, but keep candidate source products blocked until the full promotion checklist, source-readiness gate, leakage gate, and artifact gate pass. |
| source-product-status | pass | candidate_unreviewed=5; promotedCandidateProducts=0; invalidStatuses=0 | candidate_unreviewed>0; promotedCandidateProducts=0 | The source-product audit keeps candidate-only worklists out of ready source-product status. | Regenerate first-wave source products after manual review; do not edit report statuses by hand. |
| source-readiness-status | pass | targets=4; readyToEstimate=0; unblockedCandidateGates=0; missingBlockingProducts=0 | readyToEstimate=0; unblockedCandidateGates=0 | The first-wave readiness audit keeps candidate-only products from clearing estimation readiness. | Complete the manual adjudication checklists before changing any target to ready_to_estimate. |
| calibrated-claim-boundary | pass | calibratedPolicy=blocked; causalNotCleared=10; policyBlockedTargets=10; policyClearances=0 | calibratedPolicy=blocked; policyBlockedTargets>0; policyClearances=0 | Candidate-only source worklists do not clear calibrated policy-simulation claims. | Clear causal-calibration targets with reviewed source panels before strengthening policy-effect language. |
| summary | pass | checks=7; Failures=0 | Failures=0 | Candidate-only source-product worklists remain blocked from estimation and calibrated policy claims. | Keep this audit in the publication bundle and rerun it after every source-product or readiness edit. |

## Manual Adjudication Burden

- byTarget: comment-authenticity-and-uptake-effect:products=1,rows=80,markers=80; procurement-modification-causal-capture:products=4,rows=20,markers=20
- largestProducts: agency-response-final-rule-linkage=80; gao-protest-overlay=17; sam-fpds-action-history-crosswalk=1; sam-exclusion-overlay=1; procurement-offer-competition-enrichment=1
- minimumRowShortfalls: sam-fpds-action-history-crosswalk:1/5000; gao-protest-overlay:17/25; sam-exclusion-overlay:1/25; procurement-offer-competition-enrichment:1/5000

## Candidate Review Triage

- evidenceClasses: none
- riskFlags: none
- missingPriorityFiles: none
- invalidPriorities: none

## Cross-Venue Adjudication

- acceptedVenues: intermediary; opaque_nonprofit_or_dark_money; procurement
- acceptedSourceSystems: IRS/ProPublica dark-money bridge; Intermediary bridge; USAspending agency actions
- readyToEstimateTargets: none
- policyClearances: none
- boundaryFailures: none

## Boundary

Passing this audit does not validate any candidate source product. It only shows that candidate-only files are still treated as manual-review worklists and cannot support ready-to-estimate or calibrated policy-effect claims.
