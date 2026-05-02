# Lobby Capture Ablation Report

- Generated: `2026-05-02T02:32:45.625417Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0225 | 0.0225 | 0.9860 | 0.2553 | 0.5162 | 0.0063 | 0.1239 | 0.1841 |
| No enforcement | 0.0041 | 0.0041 | 1.0000 | 0.2738 | 0.5195 | 0.0056 | 0.1209 | 0.0438 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 0.9988 | 0.1471 | 0.4977 | 0.0055 | 0.1432 | 0.1759 |
| No public financing or vouchers | 0.0000 | 0.0000 | 0.9989 | 0.1330 | 0.5098 | 0.0052 | 0.1357 | 0.1506 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1215 | 0.5033 | 0.0054 | 0.1322 | 0.1575 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.2591 | 0.4988 | 0.0069 | 0.1217 | 0.1566 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.6526 | 0.0000 | 1.0000 | 0.6278 | 0.4303 | 0.4739 |
| No enforcement | 0.6515 | 0.0041 | 1.0000 | 0.6268 | 0.4330 | 0.3531 |
| No beneficial-owner disclosure | 0.6545 | 0.0000 | 0.9988 | 0.6289 | 0.4276 | 0.4196 |
| No public financing or vouchers | 0.6402 | 0.0000 | 0.9989 | 0.6279 | 0.4300 | 0.3992 |
| No cooling-off rules | 0.6562 | 0.0000 | 1.0000 | 0.6276 | 0.4312 | 0.4272 |
| No anti-astroturf authentication | 0.6564 | 0.0000 | 1.0000 | 0.5860 | 0.4383 | 0.4362 |
| No public advocate or blind review | 0.6584 | 0.0225 | 0.9860 | 0.6240 | 0.4400 | 0.3935 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0225`. This is a comparative simulation result, not a causal empirical estimate.
