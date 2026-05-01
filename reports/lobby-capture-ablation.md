# Lobby Capture Ablation Report

- Generated: `2026-05-01T14:44:20.334651Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Capture Opening Ranking

| Removed component | Capture increase | Capture rate | Anti-capture success | Dark-money share | Defensive spend | Comment distortion | Donor Gini | Detection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No public advocate or blind review | 0.0378 | 0.0378 | 0.9825 | 0.1766 | 0.5095 | 0.0001 | 0.1450 | 0.0506 |
| No enforcement | 0.0178 | 0.0178 | 0.9955 | 0.1823 | 0.4952 | 0.0001 | 0.1624 | 0.0019 |
| No public financing or vouchers | 0.0006 | 0.0006 | 0.9978 | 0.1760 | 0.5060 | 0.0001 | 0.1432 | 0.0006 |
| No beneficial-owner disclosure | 0.0000 | 0.0000 | 1.0000 | 0.2457 | 0.4963 | 0.0001 | 0.1485 | 0.0000 |
| No cooling-off rules | 0.0000 | 0.0000 | 1.0000 | 0.1750 | 0.5022 | 0.0001 | 0.1463 | 0.0000 |
| No anti-astroturf authentication | 0.0000 | 0.0000 | 1.0000 | 0.1783 | 0.4944 | 0.0003 | 0.1454 | 0.0000 |

## Full Snapshot

| Scenario | Directional | Capture rate | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.7618 | 0.0000 | 1.0000 | 0.2725 | 0.3924 | 0.4600 |
| No enforcement | 0.7695 | 0.0178 | 0.9955 | 0.2664 | 0.4014 | 0.3498 |
| No beneficial-owner disclosure | 0.7659 | 0.0000 | 1.0000 | 0.2661 | 0.4021 | 0.4048 |
| No public financing or vouchers | 0.6969 | 0.0006 | 0.9978 | 0.2721 | 0.3930 | 0.3865 |
| No cooling-off rules | 0.7662 | 0.0000 | 1.0000 | 0.2726 | 0.3921 | 0.4140 |
| No anti-astroturf authentication | 0.7644 | 0.0000 | 1.0000 | 0.2571 | 0.4014 | 0.4232 |
| No public advocate or blind review | 0.7695 | 0.0378 | 0.9825 | 0.2722 | 0.3927 | 0.3830 |

## Interpretation Guardrail

The largest modeled capture opening is `No public advocate or blind review`, with capture-rate change `0.0378`. This is a comparative simulation result, not a causal empirical estimate.
