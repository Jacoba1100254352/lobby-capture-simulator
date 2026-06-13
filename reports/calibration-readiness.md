# Calibration Readiness Audit

This audit separates hard blockers for calibrated policy-simulation claims from non-blocking validation-scope work. It does not replace peer review or the claim-posture audit.

## Gate Summary

| Gate | Status | Evidence | Claim boundary | Next action |
| --- | --- | --- | --- | --- |
| mechanism-model-readiness | cleared | claimPosture=cleared; fit=326; partial=18; miss=0; unknown=0 | Mechanism-model manuscript claims can proceed when misses and unknowns are zero and claim posture is cleared. | Keep synthetic results framed as mechanism diagnostics under explicit source limits. |
| calibrated-policy-readiness | blocked | claimPosture=not_cleared; P0=0; P1=1; P2=0; misses=0; unknown=0; source_gaps=1 | Calibrated policy-simulation claims require all P0/P1/P2 calibration and source gaps to clear. | P1 procurementExPostModificationShare: broaden the bounded USAspending action panel with representative SAM/FPDS action histories that support transaction-row, distinct-award, and amount-weighted denominators before treating modification incidence as calibrated |
| soft-validation-scope | nonblocking | P3=18; benchmark-review=12; scenario-coverage=5; scenario-family-split=1 | P3 partials are validation-scope, scenario-family, or benchmark-review work; they do not by themselves clear or block calibrated empirical claims. | Resolve P3 rows by documenting benchmark scope, splitting scenario families, or adding targeted stress scenarios before treating them as calibration evidence. |
| source-gap-boundary | blocked | source_gaps=1; metrics=procurementExPostModificationShare | Source gaps identify evidence panels that cannot test a benchmark directly. | Do not upgrade bounded source moments into empirical validation without representative source rows. |

## Counts

- Validation fits: `326`
- Validation partials: `18`
- Validation misses: `0`
- Validation source gaps: `1`
- Validation unknowns: `0`
- Calibration P0: `0`
- Calibration P1: `1`
- Calibration P2: `0`
- Calibration P3: `18`

## P3 Work Queue

- `crossVenueDetectionIndex` in `lobby-capture-interactions.csv`: benchmark-review; treat as a synthetic portfolio capability until linked source coverage is measured
- `hiddenInfluenceShare` in `lobby-capture-campaign.csv`: scenario-coverage; add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor
- `hiddenInfluenceShare` in `lobby-capture-campaign.csv`: scenario-family-split; split baseline, substitution-stress, and extreme-stress scenarios before using this benchmark as a single calibration target
- `influencePreservationRate` in `lobby-capture-campaign.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `influencePreservationRate` in `lobby-capture-mechanism-comparison.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `observedCaptureRate` in `lobby-capture-campaign.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `observedCaptureRate` in `lobby-capture-mechanism-comparison.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `publicFinancingCandidateUptake` in `lobby-capture-campaign.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `publicFinancingCandidateUptake` in `lobby-capture-interactions.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `publicFinancingCandidateUptake` in `lobby-capture-mechanism-comparison.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `publicFinancingCandidateUptake` in `lobby-capture-portfolio.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `publicFinancingCandidateUptake` in `lobby-capture-sensitivity.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `regulatorQueueBacklog` in `lobby-capture-campaign.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `regulatorQueueBacklog` in `lobby-capture-mechanism-comparison.csv`: benchmark-review; decide whether the benchmark applies to this scenario family
- `venueSubstitutionRate` in `lobby-capture-ablation.csv`: scenario-coverage; add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor
- `venueSubstitutionRate` in `lobby-capture-campaign.csv`: scenario-coverage; add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor
- `venueSubstitutionRate` in `lobby-capture-interactions.csv`: scenario-coverage; add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor
- `venueSubstitutionRate` in `lobby-capture-sensitivity.csv`: scenario-coverage; add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor
