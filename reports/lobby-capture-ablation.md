# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.1188 | 0.3747 | 0.0560 | 0.2632 | 0.2197 | 0.1893 | 0.5321 |
| No enforcement | 0.0932 | 0.3516 | 0.0350 | 0.2255 | 0.2219 | 0.1967 | 0.0465 |
| No public advocate or blind review | 0.0564 | 0.2350 | -0.0032 | 0.1680 | 0.2576 | 0.1738 | 0.5206 |
| No public financing or vouchers | 0.0074 | 0.0384 | -0.0004 | 0.1734 | 0.2224 | 0.1932 | 0.5059 |
| No anti-astroturf authentication | 0.0040 | 0.0281 | -0.0085 | 0.1659 | 0.2518 | 0.1936 | 0.5042 |
| No cooling-off rules | -0.0058 | -0.0038 | -0.0066 | 0.1644 | 0.2230 | 0.1917 | 0.5004 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1761 | 0.1241 | 0.0825 | 1.0000 | 0.6704 | 0.3227 | 0.5014 |
| No enforcement | 0.2693 | 0.4756 | 0.1175 | 0.9989 | 0.6708 | 0.3239 | 0.3799 |
| No beneficial-owner disclosure | 0.2949 | 0.4988 | 0.1385 | 0.9977 | 0.6720 | 0.3214 | 0.4532 |
| No public financing or vouchers | 0.1835 | 0.1625 | 0.0821 | 0.9989 | 0.6709 | 0.3215 | 0.4289 |
| No cooling-off rules | 0.1703 | 0.1203 | 0.0759 | 1.0000 | 0.6718 | 0.3192 | 0.4547 |
| No anti-astroturf authentication | 0.1802 | 0.1522 | 0.0739 | 1.0000 | 0.6318 | 0.3235 | 0.4668 |
| No public advocate or blind review | 0.2325 | 0.3591 | 0.0793 | 0.9906 | 0.6717 | 0.3205 | 0.4315 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.1188`. This is a comparative simulation result, not a causal empirical estimate.
