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

The Deep Research reports are distilled into `docs/research/research-synthesis.md` and `data/calibration/parameter-map.csv`. The parameter map is the preferred place to add new empirical moments because it records a model metric, low/mid/high prior, evidence class, source report, model target, and implementation status.

Current calibration links:

- `normalized-lda-lobbying.csv` constrains issue funding scale, issue mix, and disclosure lag.
- `normalized-fec-campaign-finance.csv` constrains donor concentration, public-financing share, and traceability.
- `normalized-regulatory-dockets.csv` constrains docket volume, comment authenticity, template saturation, and technical-claim credibility.
- `reports/source-moments.csv` records direct top-k concentration, traceability, public-financing, and comment-record moments from the current snapshot and fixture baselines.

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
- Raw-payload archive control: `SOURCE_RAW_DIR`.

The source-native normalizers are distributional bridges. `scripts/test-source-fetchers.py` verifies representative LDA, OpenFEC, Regulations.gov, and Federal Register JSON payloads against exact normalized rows before any live API output is used as a paper snapshot.

`make source-moments` writes `reports/source-moments.csv` plus `reports/source-moments.md`. It compares the current 2024 EPA/ENV normalized snapshot against the deterministic fixture baseline on source-level moments such as top-client share, top-donor share, amount-weighted traceability, dark-money direct visibility, public-financing source share, and comment-volume concentration.

`make validate` compares committed report snapshots against both `data/calibration/empirical-benchmarks.csv` and implemented rows in `data/calibration/parameter-map.csv`. It writes `reports/validation-summary.csv` plus `reports/validation-summary.md`, including counts by evidence class. Current benchmark rows are deliberately broad plausibility bands; misses should be read as calibration work queues, not model falsification.

`make calibration-queue` writes `reports/calibration-queue.csv` plus `reports/calibration-queue.md`. It classifies misses and partial overlaps as model tuning, metric splits, direct source moments, scenario coverage, scale alignment, or benchmark review.

The next paper-grade snapshot is fixed to a closed 2024 environmental slice:

- LDA: 2024 Q1-Q4 LD-2 activity reports, post-filtered to `ENV` and EPA-facing contacts where possible.
- FEC: 2024 cycle records for the six national party committees, with lobbyist bundled contributions as an optional auxiliary slice.
- Regulations.gov: EPA documents, dockets, and comments posted in 2024.
- Federal Register: EPA 2024 rules and proposed rules.

Run `scripts/run-2024-env-live-snapshot.sh` to execute the pinned live slice. The runner preserves raw public API payloads under ignored `data/raw/source-payloads/2024-env/`, writes normalized rows under `data/raw/`, freezes `data/snapshots/2024-env/`, and records per-source status in `data/snapshots/2024-env/live-run-status.csv`.

The current committed 2024 EPA/ENV snapshot was generated from official public endpoints on May 1, 2026 with public/demo access:

- LDA: 13 normalized 2024 `ENV` rows from the public Senate LDA API, filtered over the first three pages of each quarter.
- FEC: 100 normalized 2024 OpenFEC rows from four national party committees before the public `DEMO_KEY` hourly limit blocked the remaining two committee requests.
- Regulations.gov: public `DEMO_KEY` request was blocked by an upstream rate limit.
- Federal Register: 100 normalized EPA 2024 document rows from the public Federal Register API.

Run `make snapshot-2024-env` after any subsequent source-native fetches to freeze normalized rows under `data/snapshots/2024-env/` and write a machine-readable manifest with row counts, request templates, hashes, and Git state.
