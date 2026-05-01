# Validation Plan

This project uses external data to constrain plausible ranges, not to claim causal estimates.

Initial validation targets:

- LDA filings: lobbying spending distributions, issue-domain mix, registrant/client concentration, covered official fields.
- FEC data: large donor dependence, PAC/independent expenditure pressure, lobbyist bundling, outside-spending concentration.
- Federal Register and Regulations.gov: rulemaking duration, docket/comment volume, agency/topic mix.
- Voteview and govinfo bill status: legislative attrition and coalition plausibility for legislative arenas.
- Seattle democracy vouchers and NYC public matching funds: voucher participation, public-funds share, donor-base broadening.
- USAspending: procurement-recipient concentration and agency spending exposure.

The first implementation stores benchmark metadata in `data/calibration/empirical-benchmarks.csv` and normalized fixture rows in `data/fixtures/`. The fixture scripts copy those rows into `data/raw/` so calibration behavior can be reproduced without network access.

Current calibration links:

- `normalized-lda-lobbying.csv` constrains issue funding scale, issue mix, and disclosure lag.
- `normalized-fec-campaign-finance.csv` constrains donor concentration, public-financing share, and traceability.
- `normalized-regulatory-dockets.csv` constrains docket volume, comment authenticity, template saturation, and technical-claim credibility.

These files are plausibility inputs. They should not be cited as causal estimates, and paper claims should distinguish three layers: observed distribution, model calibration choice, and simulated mechanism.
