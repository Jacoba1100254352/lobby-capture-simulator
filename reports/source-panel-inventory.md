# Source Panel Inventory

This inventory separates source coverage from simulated outcomes. A missing or thin panel is a validation gap, not evidence that the underlying form of influence is absent.

- Usable: `2`
- Thin: `1`
- Warning: `1`
- Missing: `3`

| Panel | Moment | Value | Status | Note | Next action |
| --- | --- | ---: | --- | --- | --- |
| Direct dark money | `darkMoneySourceShare` | 0.0000 | missing | no direct DARK_MONEY rows in the snapshot | Add explicit 501(c)(4), 501(c)(6), electioneering, or curated dark-money rows; keep Schedule E super PAC rows separate. |
| Outside spending | `outsideSpendingRows` | 400.0000 | usable | coverage is usable for mechanism diagnostics, subject to source-scope limits | Broaden OpenFEC Schedule E, electioneering communication, independent expenditure, and spender/payee coverage. |
| Public financing | `publicFinancingSourceShare` | 0.0016 | missing | public-financing rows are sparse or absent | Add Seattle voucher, NYC matching-fund, and federal public-financing panels as direct program rows. |
| Intermediaries | `intermediaryRows` | 6.0000 | missing | intermediary panel is too small for calibration | Replace fixture-sized intermediary rows with IRS 8871/8872, TEOS, Form 990 XML, association, think-tank, and grantmaking exports. |
| Revolving door | `revolvingDoorRows` | 284.0000 | thin | coverage is present but thin for article-level calibration | Supplement LDA covered-position rows with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports. |
| Procurement identifiers | `procurementKnownPiidShare` | 1.0000 | usable | coverage is usable for mechanism diagnostics, subject to source-scope limits | Broaden SAM/FPDS and USAspending enrichment with PIID, UEI, action-date, modification, competition, exclusion, and protest fields. |
| Procurement modification risk | `procurementExPostModificationShare` | 1.0000 | warning | modification proxy appears saturated or missing | Separate initial awards from post-award modifications and validate nonzero modification numbers against FPDS transactions. |
