# Lobby Capture Ablation Report

- Generated: `2026-05-01T15:26:27.801638Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0250 | 0.0250 | 0.9882 | 0.1770 | 0.4927 | 0.0001 | 0.1552 | 0.0344 |
| No enforcement | 0.0059 | 0.0059 | 0.9977 | 0.1812 | 0.4926 | 0.0001 | 0.1681 | 0.0009 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 1.0000 | 0.2457 | 0.4963 | 0.0001 | 0.1562 | 0.0000 |
| No public financing or vouchers | 0.0000 | 0.0000 | 0.9978 | 0.1761 | 0.5065 | 0.0001 | 0.1495 | 0.0000 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1750 | 0.5022 | 0.0001 | 0.1541 | 0.0000 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.1783 | 0.4944 | 0.0003 | 0.1522 | 0.0000 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.7209 | 0.0000 | 1.0000 | 0.2725 | 0.3924 | 0.4600 |
| No enforcement | 0.7307 | 0.0059 | 0.9977 | 0.2649 | 0.4037 | 0.3497 |
| No beneficial-owner disclosure | 0.7257 | 0.0000 | 1.0000 | 0.2661 | 0.4021 | 0.4048 |
| No public financing or vouchers | 0.6744 | 0.0000 | 0.9978 | 0.2721 | 0.3930 | 0.3864 |
| No cooling-off rules | 0.7256 | 0.0000 | 1.0000 | 0.2726 | 0.3921 | 0.4140 |
| No anti-astroturf authentication | 0.7240 | 0.0000 | 1.0000 | 0.2571 | 0.4014 | 0.4232 |
| No public advocate or blind review | 0.7281 | 0.0250 | 0.9882 | 0.2686 | 0.3982 | 0.3811 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0250`. This is a comparative simulation result, not a causal empirical estimate.
