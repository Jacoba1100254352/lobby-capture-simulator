# Lobby Capture Ablation Report

- Generated: `2026-05-05T02:16:27.262865Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0222 | 0.0222 | 0.9860 | 0.2554 | 0.5160 | 0.0050 | 0.1832 | 0.1838 |
| No enforcement | 0.0041 | 0.0041 | 1.0000 | 0.2738 | 0.5195 | 0.0045 | 0.1796 | 0.0438 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 0.9988 | 0.1471 | 0.4977 | 0.0043 | 0.2114 | 0.1759 |
| No public financing or vouchers | 0.0000 | 0.0000 | 0.9989 | 0.1330 | 0.5098 | 0.0042 | 0.2017 | 0.1506 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1215 | 0.5033 | 0.0043 | 0.1964 | 0.1575 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.2591 | 0.4988 | 0.0056 | 0.1831 | 0.1566 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.6500 | 0.0000 | 1.0000 | 0.6727 | 0.3162 | 0.4739 |
| No enforcement | 0.6490 | 0.0041 | 1.0000 | 0.6740 | 0.3131 | 0.3531 |
| No beneficial-owner disclosure | 0.6517 | 0.0000 | 0.9988 | 0.6732 | 0.3151 | 0.4196 |
| No public financing or vouchers | 0.6374 | 0.0000 | 0.9989 | 0.6740 | 0.3129 | 0.3992 |
| No cooling-off rules | 0.6536 | 0.0000 | 1.0000 | 0.6724 | 0.3172 | 0.4272 |
| No anti-astroturf authentication | 0.6539 | 0.0000 | 1.0000 | 0.6318 | 0.3221 | 0.4362 |
| No public advocate or blind review | 0.6557 | 0.0222 | 0.9860 | 0.6716 | 0.3191 | 0.3935 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0222`. This is a comparative simulation result, not a causal empirical estimate.
