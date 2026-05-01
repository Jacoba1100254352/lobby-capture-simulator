# Lobby Capture Ablation Report

- Generated: `2026-05-01T14:58:42.837068Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0206 | 0.0206 | 0.9881 | 0.1774 | 0.4933 | 0.0001 | 0.1463 | 0.0278 |
| No enforcement | 0.0031 | 0.0031 | 0.9976 | 0.1813 | 0.4901 | 0.0001 | 0.1521 | 0.0006 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 1.0000 | 0.2457 | 0.4963 | 0.0001 | 0.1432 | 0.0000 |
| No public financing or vouchers | 0.0000 | 0.0000 | 0.9978 | 0.1761 | 0.5065 | 0.0001 | 0.1381 | 0.0000 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1750 | 0.5022 | 0.0001 | 0.1407 | 0.0000 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.1783 | 0.4944 | 0.0003 | 0.1386 | 0.0000 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.7151 | 0.0000 | 1.0000 | 0.2725 | 0.3924 | 0.4600 |
| No enforcement | 0.7250 | 0.0031 | 0.9976 | 0.2664 | 0.4014 | 0.3497 |
| No beneficial-owner disclosure | 0.7203 | 0.0000 | 1.0000 | 0.2661 | 0.4021 | 0.4048 |
| No public financing or vouchers | 0.6610 | 0.0000 | 0.9978 | 0.2721 | 0.3930 | 0.3864 |
| No cooling-off rules | 0.7199 | 0.0000 | 1.0000 | 0.2726 | 0.3921 | 0.4140 |
| No anti-astroturf authentication | 0.7188 | 0.0000 | 1.0000 | 0.2571 | 0.4014 | 0.4232 |
| No public advocate or blind review | 0.7242 | 0.0206 | 0.9881 | 0.2685 | 0.3984 | 0.3804 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0206`. This is a comparative simulation result, not a causal empirical estimate.
