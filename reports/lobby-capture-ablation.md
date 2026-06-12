# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1204 | 0.3753 | 0.0585 | 0.2538 | 0.2162 | 0.4468 | 0.5312 |
| No enforcement | 0.0893 | 0.3319 | 0.0344 | 0.2124 | 0.2176 | 0.4431 | 0.0437 |
| No public advocate or blind review | 0.0450 | 0.1953 | -0.0047 | 0.1523 | 0.2491 | 0.4424 | 0.5173 |
| No public financing or vouchers | 0.0066 | 0.0328 | -0.0003 | 0.1603 | 0.2193 | 0.4478 | 0.5020 |
| No anti-astroturf authentication | -0.0025 | 0.0116 | -0.0093 | 0.1497 | 0.2424 | 0.4445 | 0.4980 |
| No cooling-off rules | -0.0073 | -0.0075 | -0.0069 | 0.1505 | 0.2198 | 0.4417 | 0.4962 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1676 | 0.1028 | 0.0733 | 1.0000 | 0.6709 | 0.3216 | 0.4999 |
| No enforcement | 0.2569 | 0.4347 | 0.1076 | 0.9989 | 0.6713 | 0.3224 | 0.3788 |
| No beneficial-owner disclosure | 0.2880 | 0.4781 | 0.1318 | 0.9978 | 0.6719 | 0.3216 | 0.4518 |
| No public financing or vouchers | 0.1742 | 0.1356 | 0.0730 | 0.9989 | 0.6708 | 0.3216 | 0.4271 |
| No cooling-off rules | 0.1602 | 0.0953 | 0.0664 | 1.0000 | 0.6721 | 0.3187 | 0.4535 |
| No anti-astroturf authentication | 0.1651 | 0.1144 | 0.0640 | 1.0000 | 0.6318 | 0.3231 | 0.4644 |
| No public advocate or blind review | 0.2125 | 0.2981 | 0.0686 | 0.9863 | 0.6730 | 0.3168 | 0.4287 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1204`. This is a comparative simulation result, not a causal empirical estimate.
