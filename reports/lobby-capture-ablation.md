# Lobby Capture Ablation Report

- Generated: `2026-05-01T22:12:17.833799Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0266 | 0.0266 | 0.9883 | 0.2621 | 0.4930 | 0.0115 | 0.1523 | 0.0359 |
| No enforcement | 0.0078 | 0.0078 | 0.9977 | 0.2823 | 0.4923 | 0.0110 | 0.1684 | 0.0013 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 1.0000 | 0.1463 | 0.4964 | 0.0107 | 0.1562 | 0.0000 |
| No public financing or vouchers | 0.0000 | 0.0000 | 0.9989 | 0.1311 | 0.5044 | 0.0108 | 0.1496 | 0.0000 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1221 | 0.5022 | 0.0111 | 0.1541 | 0.0000 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.2613 | 0.4943 | 0.0121 | 0.1522 | 0.0000 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.6881 | 0.0000 | 1.0000 | 0.2725 | 0.3924 | 0.4600 |
| No enforcement | 0.6946 | 0.0078 | 0.9977 | 0.2648 | 0.4038 | 0.3497 |
| No beneficial-owner disclosure | 0.6901 | 0.0000 | 1.0000 | 0.2662 | 0.4020 | 0.4048 |
| No public financing or vouchers | 0.6524 | 0.0000 | 0.9989 | 0.2721 | 0.3930 | 0.3864 |
| No cooling-off rules | 0.6926 | 0.0000 | 1.0000 | 0.2725 | 0.3923 | 0.4140 |
| No anti-astroturf authentication | 0.6910 | 0.0000 | 1.0000 | 0.2570 | 0.4017 | 0.4232 |
| No public advocate or blind review | 0.6934 | 0.0266 | 0.9883 | 0.2694 | 0.3971 | 0.3813 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0266`. This is a comparative simulation result, not a causal empirical estimate.
