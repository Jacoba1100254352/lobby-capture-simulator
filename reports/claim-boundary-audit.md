# Claim Boundary Audit

This audit maps each empirical source panel to the strongest manuscript claim it can support. It is generated from `reports/source-panel-inventory.csv`, so source-coverage changes update the claim ledger before paper artifacts are rebuilt.

## Validation Status Summary

- Fit: `309`
- Partial: `34`
- Miss: `0`
- Source gap: `3`
- Unknown: `0`
- Not applicable: `11`

## Claim Rules

| Panel | Mechanism | Evidence | Status | Support level | Permitted claim boundary | Claim to avoid | Required next evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Direct dark money | Opaque donor routing and hidden electoral influence | proxy/thin | thin | limited | May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin. | Do not present as article-level calibration or validation of hidden-channel magnitude. | Add curated direct dark-money or nonprofit-routing rows where available; use IRS 501(c)(4)/(c)(6) rows only as opaque-capacity proxies and keep Schedule E, electioneering, and communication-cost rows separate. |
| Outside spending | Independent expenditure pressure outside candidate finance | direct | usable | stronger | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden OpenFEC Schedule E, electioneering communication, communication-cost, independent-expenditure, and spender/payee coverage. |
| Electoral communications | Electioneering and communication-cost channels outside ordinary receipts | direct | usable | stronger | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden OpenFEC electioneering and communication-cost coverage and keep these rows separate from direct dark-money evidence. |
| Public financing | Countervailing campaign finance and voucher/matching funds | direct when present | thin | limited | May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin. | Do not present as article-level calibration or validation of hidden-channel magnitude. | Add NYC matching-fund, Seattle voucher, and federal public-financing panels as direct program rows. |
| Intermediaries | Association, nonprofit, think-tank, and campaign-intermediary capacity | proxy | usable | stronger | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Expand NYC CFB intermediary and IRS EO BMF rows with IRS 8871/8872, Form 990 XML, association, think-tank, and grantmaking exports. |
| Revolving door | Post-government access, covered-position links, and cooling-off exposure | proxy/thin | thin | limited | May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin. | Do not present as article-level calibration or validation of hidden-channel magnitude. | Supplement LDA covered-position rows with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports. |
| Procurement identifiers | Vendor and award-path matching for procurement influence | direct identifier coverage | usable | stronger | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden SAM/FPDS and USAspending enrichment with PIID, UEI, action-date, modification, competition, exclusion, and protest fields. |
| Procurement concentration bridge | Multi-agency vendor and agency concentration diagnostics | direct top-award bridge | thin | limited | May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin. | Do not present as article-level calibration or validation of hidden-channel magnitude. | Replace the top-award bridge with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated. |
| Procurement action history | Transaction/action denominator for post-award modification incidence | direct action rows when present | usable | stronger | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden the USAspending action panel with representative SAM/FPDS action-history extracts before treating modification incidence as calibration-grade. |
| Procurement modification risk | Post-award modification and specification-change pressure | proxy/thin | warning | warning | May be used as a coverage warning and schema diagnostic; do not use the moment as a stable empirical rate. | Do not treat the warning metric as calibration-grade evidence. | Validate nonzero modification numbers against representative SAM/FPDS action histories and separate transaction-action incidence from award-level modification incidence. |

## Weak-Panel Gate

- Weak panels requiring explicit claim limits: `5`
- `Direct dark money` (thin): May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin.
- `Public financing` (thin): May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin.
- `Revolving door` (thin): May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin.
- `Procurement concentration bridge` (thin): May support source-aware plausibility checks only; magnitude claims must be phrased as proxy-backed or thin.
- `Procurement modification risk` (warning): May be used as a coverage warning and schema diagnostic; do not use the moment as a stable empirical rate.
