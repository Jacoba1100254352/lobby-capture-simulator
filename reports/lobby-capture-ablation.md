# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No enforcement | 0.0769 | 0.3125 | 0.0213 | 0.2364 | 0.2370 | 0.1927 | 0.0651 |
| No beneficial-owner disclosure | 0.0654 | 0.1994 | 0.0297 | 0.2596 | 0.2327 | 0.1876 | 0.5515 |
| No public advocate or blind review | 0.0636 | 0.2344 | 0.0023 | 0.2137 | 0.2690 | 0.1731 | 0.5549 |
| No anti-astroturf authentication | 0.0117 | 0.0463 | -0.0061 | 0.2063 | 0.2612 | 0.1725 | 0.5388 |
| No public financing or vouchers | 0.0108 | 0.0463 | 0.0010 | 0.2112 | 0.2337 | 0.1905 | 0.5409 |
| No cooling-off rules | 0.0089 | 0.0322 | 0.0009 | 0.2120 | 0.2342 | 0.1823 | 0.5388 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.2159 | 0.2472 | 0.0949 | 1.0000 | 0.6730 | 0.3163 | 0.5008 |
| No enforcement | 0.2929 | 0.5597 | 0.1162 | 0.9967 | 0.6699 | 0.3267 | 0.3680 |
| No beneficial-owner disclosure | 0.2814 | 0.4466 | 0.1246 | 0.9989 | 0.6719 | 0.3202 | 0.4653 |
| No public financing or vouchers | 0.2268 | 0.2934 | 0.0959 | 0.9989 | 0.6726 | 0.3178 | 0.4335 |
| No cooling-off rules | 0.2249 | 0.2794 | 0.0957 | 1.0000 | 0.6704 | 0.3231 | 0.4591 |
| No anti-astroturf authentication | 0.2277 | 0.2934 | 0.0888 | 1.0000 | 0.6281 | 0.3336 | 0.4726 |
| No public advocate or blind review | 0.2795 | 0.4816 | 0.0972 | 0.9860 | 0.6686 | 0.3289 | 0.4465 |

## Interpretation Guardrail

The largest modeled distortion opening is `No enforcement`, with total-distortion change `0.0769`. This is a comparative simulation result, not a causal empirical estimate.
