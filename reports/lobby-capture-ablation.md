# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1207 | 0.3759 | 0.0586 | 0.2539 | 0.2163 | 0.4532 | 0.5312 |
| No enforcement | 0.0894 | 0.3322 | 0.0344 | 0.2124 | 0.2176 | 0.4509 | 0.0437 |
| No public advocate or blind review | 0.0448 | 0.1947 | -0.0047 | 0.1523 | 0.2490 | 0.4500 | 0.5173 |
| No public financing or vouchers | 0.0066 | 0.0328 | -0.0003 | 0.1603 | 0.2193 | 0.4556 | 0.5019 |
| No anti-astroturf authentication | -0.0024 | 0.0119 | -0.0093 | 0.1497 | 0.2424 | 0.4523 | 0.4980 |
| No cooling-off rules | -0.0072 | -0.0066 | -0.0069 | 0.1505 | 0.2198 | 0.4493 | 0.4964 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1676 | 0.1025 | 0.0733 | 1.0000 | 0.6709 | 0.3216 | 0.4999 |
| No enforcement | 0.2569 | 0.4347 | 0.1076 | 0.9989 | 0.6713 | 0.3224 | 0.3788 |
| No beneficial-owner disclosure | 0.2882 | 0.4784 | 0.1319 | 0.9978 | 0.6718 | 0.3219 | 0.4518 |
| No public financing or vouchers | 0.1742 | 0.1353 | 0.0730 | 0.9989 | 0.6708 | 0.3216 | 0.4271 |
| No cooling-off rules | 0.1604 | 0.0959 | 0.0664 | 1.0000 | 0.6719 | 0.3192 | 0.4535 |
| No anti-astroturf authentication | 0.1651 | 0.1144 | 0.0640 | 1.0000 | 0.6318 | 0.3231 | 0.4644 |
| No public advocate or blind review | 0.2124 | 0.2972 | 0.0686 | 0.9863 | 0.6731 | 0.3167 | 0.4287 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1207`. This is a comparative simulation result, not a causal empirical estimate.
