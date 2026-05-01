# Validation Plan

This project uses external data to constrain plausible ranges, not to claim causal estimates.

Initial validation targets:

- LDA filings: lobbying spending distributions, issue-domain mix, registrant/client concentration, covered official fields.
- FEC data: large donor dependence, PAC/independent expenditure pressure, lobbyist bundling, outside-spending concentration.
- Federal Register and Regulations.gov: rulemaking duration, docket/comment volume, agency/topic mix.
- Voteview and govinfo bill status: legislative attrition and coalition plausibility for legislative arenas.
- Seattle democracy vouchers and NYC public matching funds: voucher participation, public-funds share, donor-base broadening.
- USAspending: procurement-recipient concentration and agency spending exposure.

The implementation stores benchmark metadata in `data/calibration/empirical-benchmarks.csv`, normalized fixture rows in `data/fixtures/`, and source-native JSON parser fixtures in `data/fixtures/source-native/`. The fixture scripts copy normalized rows into `data/raw/` so calibration behavior can be reproduced without network access.

Current calibration links:

- `normalized-lda-lobbying.csv` constrains issue funding scale, issue mix, and disclosure lag.
- `normalized-fec-campaign-finance.csv` constrains donor concentration, public-financing share, and traceability.
- `normalized-regulatory-dockets.csv` constrains docket volume, comment authenticity, template saturation, and technical-claim credibility.

These files are plausibility inputs. They should not be cited as causal estimates, and paper claims should distinguish three layers: observed distribution, model calibration choice, and simulated mechanism.

The fetch scripts now have two modes:

- default mode copies tracked deterministic fixtures into `data/raw/`;
- `--live` mode normalizes an explicit CSV path or URL into the same schema and fails if required columns are missing;
- source-native `--live` mode queries LDA, OpenFEC, Regulations.gov, or Federal Register when no explicit CSV/URL is supplied.

Expected live-mode environment variables are `LDA_LIVE_CSV` or `LDA_LIVE_URL`, `FEC_LIVE_CSV` or `FEC_LIVE_URL`, and `REGULATORY_LIVE_CSV` or `REGULATORY_LIVE_URL` for explicit-source normalization.

Source-native live variables:

- LDA: `LDA_API_BASE`, `LDA_API_KEY`, `LDA_YEAR`, `LDA_PERIOD`, `LDA_MAX_PAGES`.
- FEC: `FEC_API_KEY`, `FEC_API_BASE`, `FEC_CYCLE`, `FEC_COMMITTEE_ID`.
- Regulations.gov: `REGULATIONS_API_KEY`, `REGULATIONS_API_BASE`, `REGULATORY_AGENCY`, `REGULATORY_SEARCH_TERM`, `REGULATORY_DATE_FROM`, `REGULATORY_DATE_TO`.
- Federal Register: `REGULATORY_SOURCE=federal-register`, `FEDERAL_REGISTER_API_BASE`, `FEDERAL_REGISTER_TYPE`, `REGULATORY_SEARCH_TERM`, `REGULATORY_DATE_FROM`, `REGULATORY_DATE_TO`.
- Retry controls: `SOURCE_FETCH_RETRIES`, `SOURCE_FETCH_BACKOFF_SECONDS`.

The source-native normalizers are distributional bridges. `scripts/test-source-fetchers.py` verifies representative LDA, OpenFEC, Regulations.gov, and Federal Register JSON payloads against exact normalized rows before any live API output is used as a paper snapshot.
