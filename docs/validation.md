# Validation Plan

This project uses external data to constrain plausible ranges, not to claim causal estimates.

Initial validation targets:

- LDA filings: lobbying spending distributions, issue-domain mix, registrant/client concentration, covered official fields.
- FEC data: large donor dependence, PAC/independent expenditure pressure, lobbyist bundling, outside-spending concentration.
- Federal Register and Regulations.gov: rulemaking duration, docket/comment volume, agency/topic mix.
- Voteview and govinfo bill status: legislative attrition and coalition plausibility for legislative arenas.
- Seattle democracy vouchers and NYC public matching funds: voucher participation, public-funds share, donor-base broadening.
- USAspending: procurement-recipient concentration and agency spending exposure.

The first implementation stores benchmark metadata in `data/calibration/empirical-benchmarks.csv`; importers should be added only after the model surfaces they constrain are stable.

