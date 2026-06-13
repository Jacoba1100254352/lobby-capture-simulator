# Calibration Readiness Audit

This audit separates hard blockers for calibrated policy-simulation claims from non-blocking validation-scope work. It does not replace peer review or the claim-posture audit.

## Gate Summary

| Gate | Status | Evidence | Claim boundary | Next action |
| --- | --- | --- | --- | --- |
| mechanism-model-readiness | cleared | claimPosture=cleared; fit=337; partial=0; miss=0; unknown=0 | Mechanism-model manuscript claims can proceed when misses and unknowns are zero and claim posture is cleared. | Keep synthetic results framed as mechanism diagnostics under explicit source limits. |
| empirical-bridge-readiness | bounded | claimPosture=bounded; 0 source-gap validations, 0 thin, warning, fixture-only, or missing panels, 7 bounded-support source panels; 3 bounded claim dependencies | Empirical bridge rows can support distributional anchors and validation-gap diagnostics; bounded status means stronger hidden-channel, procurement-capture, or policy-effect claims remain outside scope. | Clear bounded claim-source dependencies before describing the empirical bridge as fully cleared. |
| calibrated-policy-readiness | blocked | claimPosture=not_cleared; validation_queue P0=0; validation_queue P1=0; validation_queue P2=0; misses=0; unknown=0; source_gaps=0; causal_targets P1=4; causal_targets P2=6; open_causal_targets=10 | Calibrated policy-simulation claims require both the validation-calibration queue and the independent causal-calibration target matrix to clear. | Clear the causal-calibration target matrix and add stronger source panels before using calibrated policy-simulation language. |
| soft-validation-scope | cleared | P3=0; none | P3 partials are validation-scope, scenario-family, or benchmark-review work; they do not by themselves clear or block calibrated empirical claims. | Resolve P3 rows by documenting benchmark scope, splitting scenario families, or adding targeted stress scenarios before treating them as calibration evidence. |
| source-gap-boundary | cleared | source_gaps=0 | Source gaps identify evidence panels that cannot test a benchmark directly. | Do not upgrade bounded source moments into empirical validation without representative source rows. |

## Counts

- Validation fits: `337`
- Validation partials: `0`
- Validation misses: `0`
- Validation source gaps: `0`
- Validation unknowns: `0`
- Validation-queue P0: `0`
- Validation-queue P1: `0`
- Validation-queue P2: `0`
- Validation-queue P3: `0`
- Open causal calibration targets: `10`
- Open causal P1 targets: `4`
- Open causal P2 targets: `6`

## P3 Work Queue

- No P3 calibration-scope rows remain.
