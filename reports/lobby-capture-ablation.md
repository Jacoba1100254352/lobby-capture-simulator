# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1241 | 0.3931 | 0.0601 | 0.2711 | 0.2198 | 0.4652 | 0.5348 |
| No enforcement | 0.0949 | 0.3603 | 0.0369 | 0.2312 | 0.2220 | 0.4665 | 0.0476 |
| No public advocate or blind review | 0.0521 | 0.2253 | -0.0038 | 0.1703 | 0.2574 | 0.4555 | 0.5212 |
| No public financing or vouchers | 0.0083 | 0.0416 | -0.0003 | 0.1776 | 0.2222 | 0.4661 | 0.5079 |
| No anti-astroturf authentication | 0.0007 | 0.0216 | -0.0092 | 0.1682 | 0.2519 | 0.4637 | 0.5053 |
| No cooling-off rules | -0.0060 | -0.0013 | -0.0070 | 0.1682 | 0.2226 | 0.4637 | 0.5027 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1830 | 0.1397 | 0.0850 | 1.0000 | 0.6716 | 0.3200 | 0.5018 |
| No enforcement | 0.2779 | 0.5000 | 0.1219 | 0.9989 | 0.6710 | 0.3240 | 0.3801 |
| No beneficial-owner disclosure | 0.3071 | 0.5328 | 0.1451 | 0.9965 | 0.6709 | 0.3247 | 0.4534 |
| No public financing or vouchers | 0.1914 | 0.1813 | 0.0847 | 0.9989 | 0.6713 | 0.3209 | 0.4304 |
| No cooling-off rules | 0.1771 | 0.1384 | 0.0780 | 1.0000 | 0.6731 | 0.3161 | 0.4548 |
| No anti-astroturf authentication | 0.1837 | 0.1613 | 0.0758 | 1.0000 | 0.6308 | 0.3261 | 0.4678 |
| No public advocate or blind review | 0.2351 | 0.3650 | 0.0812 | 0.9895 | 0.6713 | 0.3216 | 0.4322 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1241`. This is a comparative simulation result, not a causal empirical estimate.
