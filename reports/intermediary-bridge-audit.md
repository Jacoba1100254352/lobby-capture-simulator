# Intermediary Bridge Audit

This audit separates local campaign-intermediary records, nonprofit and association capacity proxies, IRS 527 political-organization filings, and Form 990 nonprofit-routing evidence in the committed 2024 snapshot.

## Claim Boundary

The committed intermediary bridge contains 353 NYC CFB campaign-intermediary rows, 500 IRS EO BMF nonprofit/association capacity rows, and 500 IRS POFD Form 8872 political-organization rows. It contains 0 Form 990 nonprofit-routing rows. Intermediary-substitution magnitude claims remain bounded until representative Form 990, grantmaking, vendor, donor, association, or think-tank routing records are archived; the current bridge is not representative nonprofit routing evidence.

## Source Split

| Source | Evidence | Rows | Direct routing rows | Capacity proxy rows | 527 rows | Form 990 rows | Political spend share | Grantmaking share | Claim boundary |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| nyc-cfb-campaign-intermediaries | direct local intermediary | 353 | 0 | 0 | 0 | 0 | 0.0043 | 0.0000 | direct local campaign-intermediary records; not national nonprofit routing or hidden-channel magnitude evidence |
| irs-eo-bmf-nonprofit-capacity | proxy | 500 | 0 | 500 | 0 | 0 | 0.0468 | 1.0000 | organizational capacity proxy; not Form 990 routing, donor, grant-network, or expenditure evidence |
| irs-527-political-organizations | direct 527 filings | 500 | 0 | 0 | 500 | 0 | 0.9488 | 0.0000 | campaign-adjacent political-organization evidence; keep separate from 501(c)(4)/(c)(6) hidden-donor evidence |
| form990-nonprofit-routing | direct nonprofit routing | 0 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | required before claiming representative nonprofit routing, grant networks, or think-tank/association money paths |
| association-capacity | proxy | 128 | 0 | 128 | 0 | 0 | 0.0298 | 0.3402 | trade-association capacity proxy; not membership, donor, grant-routing, or direct advocacy-expenditure evidence |
| social-welfare-capacity | proxy | 34 | 0 | 34 | 0 | 0 | 0.0084 | 0.0691 | opaque social-welfare capacity proxy; not direct hidden spending or donor routing |
| think-tank-charitable-capacity | proxy | 338 | 0 | 338 | 0 | 0 | 0.0086 | 0.5908 | charitable or think-tank capacity proxy; not donor, grant-routing, or sponsored-research flow evidence |
