# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1202 | 0.3747 | 0.0585 | 0.2539 | 0.2163 | 0.4071 | 0.5310 |
| No enforcement | 0.0892 | 0.3313 | 0.0344 | 0.2125 | 0.2176 | 0.4039 | 0.0435 |
| No public advocate or blind review | 0.0450 | 0.1956 | -0.0047 | 0.1524 | 0.2490 | 0.4034 | 0.5173 |
| No public financing or vouchers | 0.0064 | 0.0322 | -0.0004 | 0.1603 | 0.2193 | 0.4088 | 0.5018 |
| No anti-astroturf authentication | -0.0025 | 0.0116 | -0.0093 | 0.1498 | 0.2424 | 0.4051 | 0.4978 |
| No cooling-off rules | -0.0073 | -0.0075 | -0.0068 | 0.1506 | 0.2197 | 0.4024 | 0.4963 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1667 | 0.1019 | 0.0733 | 1.0000 | 0.6709 | 0.3216 | 0.4998 |
| No enforcement | 0.2559 | 0.4331 | 0.1076 | 0.9989 | 0.6713 | 0.3224 | 0.3788 |
| No beneficial-owner disclosure | 0.2870 | 0.4766 | 0.1317 | 0.9978 | 0.6719 | 0.3216 | 0.4517 |
| No public financing or vouchers | 0.1731 | 0.1341 | 0.0729 | 0.9989 | 0.6709 | 0.3216 | 0.4270 |
| No cooling-off rules | 0.1594 | 0.0944 | 0.0664 | 1.0000 | 0.6722 | 0.3184 | 0.4533 |
| No anti-astroturf authentication | 0.1643 | 0.1134 | 0.0640 | 1.0000 | 0.6318 | 0.3232 | 0.4643 |
| No public advocate or blind review | 0.2118 | 0.2975 | 0.0686 | 0.9863 | 0.6731 | 0.3166 | 0.4287 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1202`. This is a comparative simulation result, not a causal empirical estimate.
