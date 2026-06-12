# Dark-Money Bridge Audit

This audit separates proxy capacity rows from adjacent observed electoral and intermediary rows. It is a guardrail against treating opaque nonprofit capacity, Super PAC spending, electioneering, communication-cost, or IRS 527 rows as direct hidden-donor routing evidence.

## Claim Boundary

The committed dark-money bridge contains 250 IRS EO BMF capacity-proxy rows, including 58 501(c)(4) rows and 192 501(c)(6) rows. It contains 0 direct hidden-donor routing rows. Adjacent observed panels include 400 Super PAC rows, 268 electioneering or communication-cost rows, and 500 IRS 527 political-organization rows. Hidden-channel magnitude claims remain not cleared until direct routing, donor, transfer, or nonprofit-expenditure records are archived.

| Source | Status | Evidence | Role | Rows | Amount | Share | Traceability | Donor disclosure | Direct routing | Proxy rows | C4 | C6 | Distinct sources | Boundary |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| dark-money-capacity-proxy | ok | proxy | IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity bridge | 250 | 26.0062 | 0.0274 | 0.2043 | 0.0000 | 0 | 250 | 58 | 192 | 250 | capacity proxy for opaque nonprofit advocacy; not direct hidden-donor routing |
| openfec-super-pac | ok | direct outside-spending | OpenFEC Schedule E independent-expenditure pressure | 400 | 7.9978 | 0.0084 | 0.5628 | 0.0000 | 0 | 0 | 0 | 0 | 53 | observable outside spending; not direct dark-money or hidden-donor evidence |
| openfec-electoral-communications | ok | direct electoral-communication | OpenFEC electioneering and communication-cost bridge | 268 | 11.8253 | 0.0125 | 0.5238 | 0.0000 | 0 | 0 | 0 | 0 | 33 | observable electoral communications; adjacent evidence, not hidden-donor routing |
| irs-527-political-organizations | ok | direct 527 filings | IRS POFD Form 8872 political-organization filings | 500 | 857.0814 | 0.9030 | 0.0000 | 0.7148 | 0 | 0 | 0 | 0 | 126 | campaign-adjacent intermediary evidence; keep separate from 501(c)(4)/(c)(6) dark-money evidence |
| nonprofit-association-capacity | ok | proxy | IRS EO BMF nonprofit and association capacity rows | 500 | 42.3069 | 0.0446 | 0.0000 | 0.5958 | 0 | 500 | 34 | 128 | 500 | organizational capacity proxy; not routing, donor, or expenditure evidence |
| nyc-cfb-campaign-intermediaries | ok | direct local intermediary | NYC CFB campaign-intermediary rows | 353 | 3.9024 | 0.0041 | 0.0000 | 0.7177 | 0 | 0 | 0 | 0 | 340 | direct local campaign-intermediary records; not national hidden-channel magnitude evidence |
