# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No enforcement | 0.0612 | 0.2522 | 0.0169 | 0.1984 | 0.2375 | 0.1863 | 0.0529 |
| No public advocate or blind review | 0.0409 | 0.1819 | -0.0015 | 0.1691 | 0.2716 | 0.1713 | 0.5410 |
| No beneficial-owner disclosure | 0.0377 | 0.1222 | 0.0245 | 0.2091 | 0.2342 | 0.1859 | 0.5334 |
| No public financing or vouchers | 0.0076 | 0.0338 | 0.0004 | 0.1771 | 0.2354 | 0.1997 | 0.5254 |
| No cooling-off rules | 0.0042 | 0.0253 | -0.0014 | 0.1749 | 0.2358 | 0.1914 | 0.5231 |
| No anti-astroturf authentication | -0.0012 | 0.0134 | -0.0080 | 0.1651 | 0.2631 | 0.1723 | 0.5197 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1484 | 0.1000 | 0.0918 | 1.0000 | 0.6718 | 0.3190 | 0.4845 |
| No enforcement | 0.2096 | 0.3522 | 0.1087 | 0.9979 | 0.6718 | 0.3204 | 0.3597 |
| No beneficial-owner disclosure | 0.1861 | 0.2222 | 0.1162 | 0.9978 | 0.6729 | 0.3164 | 0.4411 |
| No public financing or vouchers | 0.1560 | 0.1338 | 0.0922 | 0.9988 | 0.6723 | 0.3177 | 0.4126 |
| No cooling-off rules | 0.1526 | 0.1253 | 0.0904 | 1.0000 | 0.6717 | 0.3192 | 0.4396 |
| No anti-astroturf authentication | 0.1472 | 0.1134 | 0.0838 | 0.9989 | 0.6309 | 0.3254 | 0.4460 |
| No public advocate or blind review | 0.1893 | 0.2819 | 0.0902 | 0.9817 | 0.6691 | 0.3267 | 0.4204 |

## Interpretation Guardrail

The largest modeled distortion opening is `No enforcement`, with total-distortion change `0.0612`. This is a comparative simulation result, not a causal empirical estimate.
