# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No enforcement | 0.1022 | 0.3813 | 0.0371 | 0.2272 | 0.2202 | 0.1941 | 0.0617 |
| No beneficial-owner disclosure | 0.1001 | 0.3000 | 0.0514 | 0.2596 | 0.2181 | 0.1850 | 0.5472 |
| No public advocate or blind review | 0.0558 | 0.2141 | -0.0018 | 0.1699 | 0.2513 | 0.1760 | 0.5421 |
| No public financing or vouchers | 0.0066 | 0.0306 | 0.0001 | 0.1742 | 0.2197 | 0.2045 | 0.5257 |
| No anti-astroturf authentication | 0.0040 | 0.0256 | -0.0083 | 0.1656 | 0.2492 | 0.1819 | 0.5207 |
| No cooling-off rules | -0.0021 | 0.0041 | -0.0056 | 0.1650 | 0.2206 | 0.2003 | 0.5205 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1708 | 0.1034 | 0.0817 | 1.0000 | 0.6722 | 0.3178 | 0.5102 |
| No enforcement | 0.2730 | 0.4847 | 0.1188 | 0.9978 | 0.6694 | 0.3275 | 0.3858 |
| No beneficial-owner disclosure | 0.2709 | 0.4034 | 0.1332 | 0.9989 | 0.6714 | 0.3213 | 0.4780 |
| No public financing or vouchers | 0.1773 | 0.1341 | 0.0818 | 0.9988 | 0.6733 | 0.3151 | 0.4382 |
| No cooling-off rules | 0.1687 | 0.1075 | 0.0761 | 1.0000 | 0.6707 | 0.3218 | 0.4647 |
| No anti-astroturf authentication | 0.1748 | 0.1291 | 0.0735 | 1.0000 | 0.6308 | 0.3256 | 0.4754 |
| No public advocate or blind review | 0.2266 | 0.3175 | 0.0799 | 0.9885 | 0.6687 | 0.3278 | 0.4527 |

## Interpretation Guardrail

The largest modeled distortion opening is `No enforcement`, with total-distortion change `0.1022`. This is a comparative simulation result, not a causal empirical estimate.
