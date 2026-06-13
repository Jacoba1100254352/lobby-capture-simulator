# Claim Boundary Audit

This audit maps each empirical source panel to the manuscript claim boundary it can support. It is generated from `reports/source-panel-inventory.csv`, so source-coverage and claim-strength changes update the claim ledger before paper artifacts are rebuilt. A usable source panel can still be proxy-bounded, denominator-bounded, program-bounded, or otherwise source-limited.

## Validation Status Summary

- Fit: `337`
- Partial: `0`
- Miss: `0`
- Source gap: `0`
- Unknown: `0`
- Not applicable: `21`

## Claim Rules

| Panel | Mechanism | Evidence | Status | Support level | Permitted claim boundary | Claim to avoid | Required next evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Direct dark money | Opaque donor routing and hidden electoral influence | direct/proxy gap | usable | direct-proxy-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Add curated direct dark-money or nonprofit-routing rows where available; use IRS 501(c)(4)/(c)(6) rows only as opaque-capacity proxies and keep Schedule E, electioneering, and communication-cost rows separate. |
| Outside spending | Independent expenditure pressure outside candidate finance | direct | usable | direct-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden OpenFEC Schedule E, electioneering communication, communication-cost, independent-expenditure, and spender/payee coverage. |
| Electoral communications | Electioneering and communication-cost channels outside ordinary receipts | direct | usable | direct-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden OpenFEC electioneering and communication-cost coverage and keep these rows separate from direct dark-money evidence. |
| Public financing | Countervailing campaign finance and voucher/matching funds | direct program rows when present | usable | program-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden NYC matching-fund and Seattle voucher rows with federal, state, and additional local public-financing panels before treating uptake as representative. |
| Intermediaries | Association, nonprofit, think-tank, and campaign-intermediary capacity | proxy | usable | proxy-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Expand NYC CFB intermediary and IRS EO BMF rows with IRS 8871/8872, Form 990 XML, association, think-tank, and grantmaking exports. |
| IRS 527 political organizations | Political-organization receipts and disbursements for campaign-adjacent intermediaries | direct observed 527 filings | usable | direct-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden beyond the default bounded IRS POFD alphabetic slice, preserve the electronic-filing scope note, and keep 527 political-organization rows separate from 501(c)(4)/(c)(6) hidden-donor evidence. |
| Revolving door | Post-government access, covered-position links, and cooling-off exposure | proxy/thin | usable | proxy-thin | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Supplement LDA covered-position rows with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports. |
| Procurement identifiers | Vendor and award-path matching for procurement influence | direct identifier coverage | usable | direct-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Broaden SAM/FPDS and USAspending enrichment with PIID, UEI, action-date, modification, competition, exclusion, and protest fields. |
| Procurement concentration panel | Multi-agency vendor and agency concentration diagnostics | denominator-mapped public bulk panel | usable | denominator-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Use the procurement benchmark crosswalk for aggregate, agency, award-type, and agency-award-type concentration diagnostics; retain SAM/FPDS exports for exclusions, protests, and coding overlays. |
| Procurement action history | Transaction/action denominator for post-award modification incidence | direct primary SAM/USAspending action rows when present | usable | conditional-direct | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Use the archived USAspending bulk summary for action-row, distinct-award, and amount-weighted denominators; add SAM/FPDS action-history extracts to crosswalk modification coding before treating modification incidence as calibration-grade. |
| Procurement modification risk | Post-award modification and specification-change pressure | denominator-mapped observed proxy | usable | denominator-bounded | May support mechanism diagnostics and distributional anchoring within the stated source scope. | Do not present as a causal estimate or nationally representative policy effect. | Use the procurement benchmark crosswalk for action-row, distinct-award, and amount-weighted denominators; add SAM/FPDS exports to reconcile coding before claiming causal procurement-modification effects. |

## Coverage-Gap Gate

- Thin, warning, fixture-only, or missing panels requiring explicit coverage limits: `0`

## Bounded-Evidence Gate

- Usable panels with proxy, denominator, program, or mixed evidence limits: `7`
- `Direct dark money` (direct-proxy-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Public financing` (program-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Intermediaries` (proxy-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Revolving door` (proxy-thin): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Procurement concentration panel` (denominator-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Procurement action history` (conditional-direct): May support mechanism diagnostics and distributional anchoring within the stated source scope.
- `Procurement modification risk` (denominator-bounded): May support mechanism diagnostics and distributional anchoring within the stated source scope.
