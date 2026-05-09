# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.0710 | 0.1766 | 0.0355 | 0.1899 | 0.2194 | 0.1795 | 0.5306 |
| No enforcement | 0.0667 | 0.2213 | 0.0242 | 0.1623 | 0.2208 | 0.1809 | 0.0461 |
| No public advocate or blind review | 0.0375 | 0.1384 | -0.0034 | 0.1136 | 0.2548 | 0.1709 | 0.5262 |
| No public financing or vouchers | 0.0055 | 0.0206 | 0.0003 | 0.1207 | 0.2214 | 0.1980 | 0.5096 |
| No cooling-off rules | 0.0026 | 0.0144 | -0.0009 | 0.1193 | 0.2217 | 0.1960 | 0.5082 |
| No anti-astroturf authentication | 0.0025 | 0.0156 | -0.0053 | 0.1124 | 0.2509 | 0.1815 | 0.5074 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1296 | 0.0194 | 0.0455 | 1.0000 | 0.6736 | 0.3142 | 0.5013 |
| No enforcement | 0.1963 | 0.2406 | 0.0697 | 1.0000 | 0.6722 | 0.3190 | 0.3793 |
| No beneficial-owner disclosure | 0.2006 | 0.1959 | 0.0811 | 0.9978 | 0.6724 | 0.3178 | 0.4558 |
| No public financing or vouchers | 0.1351 | 0.0400 | 0.0458 | 0.9988 | 0.6717 | 0.3191 | 0.4288 |
| No cooling-off rules | 0.1322 | 0.0338 | 0.0447 | 1.0000 | 0.6718 | 0.3189 | 0.4562 |
| No anti-astroturf authentication | 0.1321 | 0.0350 | 0.0403 | 1.0000 | 0.6305 | 0.3256 | 0.4661 |
| No public advocate or blind review | 0.1671 | 0.1578 | 0.0422 | 0.9923 | 0.6705 | 0.3225 | 0.4338 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.0710`. This is a comparative simulation result, not a causal empirical estimate.
