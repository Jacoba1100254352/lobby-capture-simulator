# Lobby Capture Ablation Report

- Generated: `2026-05-05T00:00:00Z`
- Seed: `242`
- Runs per scenario: `40`
- Contests per run: `80`
- Baseline: `Ablation baseline full bundle`

## Distortion Opening Ranking

| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No beneficial-owner disclosure | 0.0684 | 0.1644 | 0.0353 | 0.1897 | 0.2351 | 0.1838 | 0.5296 |
| No enforcement | 0.0641 | 0.2100 | 0.0239 | 0.1618 | 0.2380 | 0.1802 | 0.0445 |
| No public advocate or blind review | 0.0363 | 0.1325 | -0.0034 | 0.1134 | 0.2755 | 0.1733 | 0.5253 |
| No public financing or vouchers | 0.0048 | 0.0181 | 0.0002 | 0.1204 | 0.2372 | 0.1972 | 0.5094 |
| No anti-astroturf authentication | 0.0023 | 0.0150 | -0.0053 | 0.1122 | 0.2651 | 0.1806 | 0.5069 |
| No cooling-off rules | 0.0020 | 0.0119 | -0.0009 | 0.1190 | 0.2376 | 0.1977 | 0.5073 |

## Full Snapshot

| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ablation baseline full bundle | 0.1284 | 0.0172 | 0.0455 | 1.0000 | 0.6735 | 0.3146 | 0.5008 |
| No enforcement | 0.1925 | 0.2272 | 0.0694 | 1.0000 | 0.6722 | 0.3189 | 0.3791 |
| No beneficial-owner disclosure | 0.1968 | 0.1816 | 0.0808 | 0.9978 | 0.6719 | 0.3189 | 0.4541 |
| No public financing or vouchers | 0.1332 | 0.0353 | 0.0457 | 0.9988 | 0.6720 | 0.3183 | 0.4280 |
| No cooling-off rules | 0.1304 | 0.0291 | 0.0446 | 1.0000 | 0.6720 | 0.3184 | 0.4557 |
| No anti-astroturf authentication | 0.1307 | 0.0322 | 0.0402 | 1.0000 | 0.6301 | 0.3266 | 0.4657 |
| No public advocate or blind review | 0.1647 | 0.1497 | 0.0422 | 0.9923 | 0.6704 | 0.3226 | 0.4327 |

## Interpretation Guardrail

The largest modeled distortion opening is `No beneficial-owner disclosure`, with total-distortion change `0.0684`. This is a comparative simulation result, not a causal empirical estimate.
