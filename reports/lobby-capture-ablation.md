# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1204 | 0.3750 | 0.0585 | 0.2539 | 0.2163 | 0.4538 | 0.5309 |
| No enforcement | 0.0893 | 0.3313 | 0.0344 | 0.2125 | 0.2176 | 0.4509 | 0.0435 |
| No public advocate or blind review | 0.0450 | 0.1950 | -0.0047 | 0.1524 | 0.2491 | 0.4500 | 0.5172 |
| No public financing or vouchers | 0.0068 | 0.0334 | -0.0003 | 0.1603 | 0.2193 | 0.4556 | 0.5019 |
| No anti-astroturf authentication | -0.0023 | 0.0122 | -0.0092 | 0.1498 | 0.2424 | 0.4523 | 0.4979 |
| No cooling-off rules | -0.0072 | -0.0069 | -0.0068 | 0.1506 | 0.2198 | 0.4492 | 0.4963 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1674 | 0.1019 | 0.0733 | 1.0000 | 0.6709 | 0.3216 | 0.4999 |
| No enforcement | 0.2567 | 0.4331 | 0.1076 | 0.9989 | 0.6713 | 0.3224 | 0.3788 |
| No beneficial-owner disclosure | 0.2878 | 0.4769 | 0.1318 | 0.9977 | 0.6718 | 0.3218 | 0.4518 |
| No public financing or vouchers | 0.1742 | 0.1353 | 0.0730 | 0.9989 | 0.6708 | 0.3216 | 0.4271 |
| No cooling-off rules | 0.1602 | 0.0950 | 0.0664 | 1.0000 | 0.6720 | 0.3189 | 0.4535 |
| No anti-astroturf authentication | 0.1651 | 0.1141 | 0.0640 | 1.0000 | 0.6317 | 0.3232 | 0.4644 |
| No public advocate or blind review | 0.2124 | 0.2969 | 0.0686 | 0.9863 | 0.6731 | 0.3167 | 0.4287 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1204`. This is a comparative simulation result, not a causal empirical estimate.
