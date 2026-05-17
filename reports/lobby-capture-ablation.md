# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1241 | 0.3931 | 0.0600 | 0.2710 | 0.2162 | 0.4724 | 0.5346 |
| No enforcement | 0.0946 | 0.3578 | 0.0369 | 0.2313 | 0.2174 | 0.4753 | 0.0472 |
| No public advocate or blind review | 0.0510 | 0.2225 | -0.0040 | 0.1700 | 0.2484 | 0.4636 | 0.5206 |
| No public financing or vouchers | 0.0069 | 0.0363 | -0.0005 | 0.1775 | 0.2189 | 0.4722 | 0.5067 |
| No anti-astroturf authentication | -0.0003 | 0.0184 | -0.0090 | 0.1686 | 0.2416 | 0.4756 | 0.5038 |
| No cooling-off rules | -0.0068 | -0.0059 | -0.0071 | 0.1681 | 0.2193 | 0.4711 | 0.5010 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1812 | 0.1347 | 0.0848 | 1.0000 | 0.6705 | 0.3226 | 0.5014 |
| No enforcement | 0.2758 | 0.4925 | 0.1218 | 0.9989 | 0.6708 | 0.3243 | 0.3797 |
| No beneficial-owner disclosure | 0.3053 | 0.5278 | 0.1449 | 0.9977 | 0.6709 | 0.3246 | 0.4531 |
| No public financing or vouchers | 0.1881 | 0.1709 | 0.0843 | 0.9989 | 0.6711 | 0.3214 | 0.4296 |
| No cooling-off rules | 0.1745 | 0.1288 | 0.0777 | 1.0000 | 0.6726 | 0.3174 | 0.4543 |
| No anti-astroturf authentication | 0.1809 | 0.1531 | 0.0758 | 1.0000 | 0.6320 | 0.3231 | 0.4665 |
| No public advocate or blind review | 0.2322 | 0.3572 | 0.0808 | 0.9906 | 0.6719 | 0.3201 | 0.4312 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1241`. This is a comparative simulation result, not a causal empirical estimate.
