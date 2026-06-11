# Source Panel Inventory

This inventory separates source coverage from simulated outcomes. A missing or thin panel is a validation gap, not evidence that the underlying form of influence is absent.

- Usable: `3`
- Thin: `4`
- Warning: `1`
- Fixture-only: `1`
- Missing: `1`

| Panel | Mechanism constrained | Evidence | Moment | Snapshot | Fixture scaffold? | Status | Note | Next action |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| Direct dark money | Opaque donor routing and hidden electoral influence | proxy/thin | `darkMoneySourceShare` | 0.0249 | yes | thin | coverage is present but thin for article-level calibration | Add curated direct dark-money or nonprofit-routing rows where available; use IRS 501(c)(4)/(c)(6) rows only as opaque-capacity proxies and keep Schedule E, electioneering, and communication-cost rows separate. |
| Outside spending | Independent expenditure pressure outside candidate finance | direct | `outsideSpendingRows` | 650.0000 | no | usable | coverage is usable for mechanism diagnostics, subject to source-scope limits | Broaden OpenFEC Schedule E, electioneering communication, communication-cost, independent-expenditure, and spender/payee coverage. |
| Electoral communications | Electioneering and communication-cost channels outside ordinary receipts | direct | `electoralCommunicationRows` | 0.0000 | no | missing | no electioneering or communication-cost rows in the pinned snapshot | Enable the OpenFEC electioneering and communication-cost source-native fetchers in the next live snapshot and keep these rows separate from direct dark-money evidence. |
| Public financing | Countervailing campaign finance and voucher/matching funds | direct when present | `publicFinancingSourceShare` | 0.0830 | yes | thin | coverage is present but thin for article-level calibration | Add NYC matching-fund, Seattle voucher, and federal public-financing panels as direct program rows. |
| Intermediaries | Association, nonprofit, think-tank, and campaign-intermediary capacity | proxy | `intermediaryRows` | 853.0000 | yes | usable | coverage is usable for mechanism diagnostics, subject to source-scope limits | Expand NYC CFB intermediary and IRS EO BMF rows with IRS 8871/8872, Form 990 XML, association, think-tank, and grantmaking exports. |
| Revolving door | Post-government access, covered-position links, and cooling-off exposure | proxy/thin | `revolvingDoorRows` | 284.0000 | no | thin | coverage is present but thin for article-level calibration | Supplement LDA covered-position rows with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports. |
| Procurement identifiers | Vendor and award-path matching for procurement influence | direct identifier coverage | `procurementKnownPiidShare` | 1.0000 | yes | usable | coverage is usable for mechanism diagnostics, subject to source-scope limits | Broaden SAM/FPDS and USAspending enrichment with PIID, UEI, action-date, modification, competition, exclusion, and protest fields. |
| Procurement concentration bridge | Multi-agency vendor and agency concentration diagnostics | direct top-award bridge | `procurementBridgeAgencyCount` | 6.0000 | no | thin | multi-agency top-award bridge is present, but top-award sampling is not representative enough for calibration | Replace the top-award bridge with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated. |
| Procurement action history | Transaction/action denominator for post-award modification incidence | direct action rows when present | `procurementActionRows` | 0.0000 | yes | fixture-only | no USAspending/SAM/FPDS transaction/action rows in the pinned snapshot; fixture bridge is available but not article-level empirical coverage | Populate data/snapshots/2024-env/normalized/usaspending-procurement-actions.csv from USAspending/SAM/FPDS transaction rows before treating modification incidence as calibrated. |
| Procurement modification risk | Post-award modification and specification-change pressure | proxy/thin | `procurementExPostModificationShare` | 0.0000 | yes | warning | latest-transaction modification enrichment is available but an action-level transaction denominator is still absent | Populate the procurement action panel from USAspending/SAM/FPDS transaction rows and validate nonzero modification numbers against FPDS actions. |
