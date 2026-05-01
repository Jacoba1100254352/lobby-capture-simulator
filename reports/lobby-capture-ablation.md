# Lobby Capture Ablation Report

- Generated: `2026-05-01T22:59:09.421228Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0253 | 0.0253 | 0.9894 | 0.2620 | 0.4932 | 0.0098 | 0.1276 | 0.0341 |
| No enforcement | 0.0056 | 0.0056 | 0.9977 | 0.2824 | 0.4919 | 0.0089 | 0.1359 | 0.0006 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 1.0000 | 0.1463 | 0.4964 | 0.0086 | 0.1271 | 0.0000 |
| No public financing or vouchers | 0.0000 | 0.0000 | 0.9989 | 0.1311 | 0.5044 | 0.0089 | 0.1214 | 0.0000 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1221 | 0.5022 | 0.0089 | 0.1282 | 0.0000 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.2612 | 0.4943 | 0.0101 | 0.1215 | 0.0000 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.6681 | 0.0000 | 1.0000 | 0.2450 | 0.4312 | 0.4600 |
| No enforcement | 0.6751 | 0.0056 | 0.9977 | 0.2470 | 0.4283 | 0.3497 |
| No beneficial-owner disclosure | 0.6704 | 0.0000 | 1.0000 | 0.2409 | 0.4375 | 0.4048 |
| No public financing or vouchers | 0.6567 | 0.0000 | 0.9989 | 0.2428 | 0.4346 | 0.3864 |
| No cooling-off rules | 0.6725 | 0.0000 | 1.0000 | 0.2421 | 0.4359 | 0.4140 |
| No anti-astroturf authentication | 0.6711 | 0.0000 | 1.0000 | 0.2298 | 0.4405 | 0.4232 |
| No public advocate or blind review | 0.6732 | 0.0253 | 0.9894 | 0.2455 | 0.4306 | 0.3811 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0253`. This is a comparative simulation result, not a causal empirical estimate.
