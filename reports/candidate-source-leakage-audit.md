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
| candidate-file-markers | pass | candidateProducts=13; candidateRows=3949; markerRows=3949; missingFiles=0; unmarkedFiles=0 | candidateProducts=13; missingFiles=0; unmarkedFiles=0 | Candidate-only source-product files retain candidateOnly=true, candidate_unreviewed, or equivalent manual-review markers. | Do not remove candidate markers until the matching manual promotion checklist is completed and the source-product/readiness reports are regenerated. |
| source-product-status | pass | candidate_unreviewed=13; promotedCandidateProducts=0; invalidStatuses=0 | candidate_unreviewed=13; promotedCandidateProducts=0 | The source-product audit keeps candidate-only worklists out of ready source-product status. | Regenerate first-wave source products after manual review; do not edit report statuses by hand. |
| source-readiness-status | pass | targets=4; readyToEstimate=0; unblockedCandidateGates=0; missingBlockingProducts=0 | readyToEstimate=0; unblockedCandidateGates=0 | The first-wave readiness audit keeps candidate-only products from clearing estimation readiness. | Complete the manual adjudication checklists before changing any target to ready_to_estimate. |
| calibrated-claim-boundary | pass | calibratedPolicy=blocked; causalNotCleared=10; policyBlockedTargets=10; policyClearances=0 | calibratedPolicy=blocked; policyBlockedTargets>0; policyClearances=0 | Candidate-only source worklists do not clear calibrated policy-simulation claims. | Clear causal-calibration targets with reviewed source panels before strengthening policy-effect language. |
| summary | pass | checks=4; Failures=0 | Failures=0 | Candidate-only source-product worklists remain blocked from estimation and calibrated policy claims. | Keep this audit in the publication bundle and rerun it after every source-product or readiness edit. |

## Boundary

Passing this audit does not validate any candidate source product. It only shows that candidate-only files are still treated as manual-review worklists and cannot support ready-to-estimate or calibrated policy-effect claims.
