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
| candidate-file-markers | pass | candidateProducts=13; candidateRows=3965; markerRows=3965; missingFiles=0; unmarkedFiles=0 | candidateProducts=13; missingFiles=0; unmarkedFiles=0 | Candidate-only source-product files retain candidateOnly=true, candidate_unreviewed, or equivalent manual-review markers. | Do not remove candidate markers until the matching manual promotion checklist is completed and the source-product/readiness reports are regenerated. |
| manual-adjudication-burden | pass | candidateProducts=13; candidateRows=3965; markerRows=3965; reviewedRows=0; reviewerDateGaps=205; minimumRowShortfalls=4; priorities=P1=7; P2=6 | candidateRows=markerRows; reviewedRows=0 while candidate gate is active | The remaining empirical work is measurable manual adjudication, not untracked missingness: candidate files identify source-product rows that must be reviewed before promotion. | Prioritize the largest P1/P2 candidate products, replace candidate markers with reviewed source rows, and rerun first-wave source-product, readiness, candidate-leakage, and artifact gates before strengthening claims. |
| candidate-review-triage | pass | triageRows=3864; priorities=P1-manual-review=2851; P2-manual-review=1012; P3-manual-review=1; evidenceClasses=3; riskFlags=6 | triageRows>0; P1-manual-review>0; invalidPriorities=0 | Entity-resolution and substitution candidate rows carry deterministic review-priority and linkage-evidence fields while remaining candidate-only. | Use P1 rows as the first manual adjudication queue; do not treat reviewPriorityScore as adjudicated match confidence. |
| source-product-status | pass | candidate_unreviewed=13; promotedCandidateProducts=0; invalidStatuses=0 | candidate_unreviewed=13; promotedCandidateProducts=0 | The source-product audit keeps candidate-only worklists out of ready source-product status. | Regenerate first-wave source products after manual review; do not edit report statuses by hand. |
| source-readiness-status | pass | targets=4; readyToEstimate=0; unblockedCandidateGates=0; missingBlockingProducts=0 | readyToEstimate=0; unblockedCandidateGates=0 | The first-wave readiness audit keeps candidate-only products from clearing estimation readiness. | Complete the manual adjudication checklists before changing any target to ready_to_estimate. |
| calibrated-claim-boundary | pass | calibratedPolicy=blocked; causalNotCleared=10; policyBlockedTargets=10; policyClearances=0 | calibratedPolicy=blocked; policyBlockedTargets>0; policyClearances=0 | Candidate-only source worklists do not clear calibrated policy-simulation claims. | Clear causal-calibration targets with reviewed source panels before strengthening policy-effect language. |
| summary | pass | checks=6; Failures=0 | Failures=0 | Candidate-only source-product worklists remain blocked from estimation and calibrated policy claims. | Keep this audit in the publication bundle and rerun it after every source-product or readiness edit. |

## Manual Adjudication Burden

- byTarget: comment-authenticity-and-uptake-effect:products=1,rows=80,markers=80; procurement-modification-causal-capture:products=5,rows=21,markers=21; substitution-elasticity:products=2,rows=1580,markers=1580; venue-shifting-detection-effect:products=5,rows=2284,markers=2284
- largestProducts: linked-actor-issue-venue-time=1500; actor-issue-time-spine=1500; canonical-actor-identifiers=659; substitution-comparison-groups=80; alias-resolution-audit-sample=80
- minimumRowShortfalls: sam-fpds-action-history-crosswalk:1/5000; gao-protest-overlay:17/25; sam-exclusion-overlay:1/25; procurement-offer-competition-enrichment:1/5000

## Candidate Review Triage

- evidenceClasses: shared-source-identifier-overlap=3819; cross-venue-name-overlap=44; same-venue-multi-source-name-overlap=1
- riskFlags: procurement-name-overlap-requires-UEI-review=2931; same-venue-only=2904; name-only-cross-venue=43; covered-position-proxy-not-person-movement=34; issue-crosswalk-unreviewed=5; committee-name-may-not-identify-actor-control=3
- missingPriorityFiles: none
- invalidPriorities: none

## Boundary

Passing this audit does not validate any candidate source product. It only shows that candidate-only files are still treated as manual-review worklists and cannot support ready-to-estimate or calibrated policy-effect claims.
