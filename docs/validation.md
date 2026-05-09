# Validation Plan

This project uses external data to constrain plausible ranges, not to claim causal estimates.

Initial validation targets:

- LDA filings: lobbying spending distributions, issue-domain mix, registrant/client concentration, covered official fields.
- FEC data: large donor dependence, PAC/independent expenditure pressure, lobbyist bundling, outside-spending concentration.
- Federal Register and Regulations.gov: rulemaking duration, docket/comment volume, agency/topic mix.
- Voteview and govinfo bill status: legislative attrition and coalition plausibility for legislative arenas.
- Seattle democracy vouchers and NYC public matching funds: voucher participation, public-funds share, donor-base broadening.
- USAspending: procurement-recipient concentration and agency spending exposure.
- SAM/FPDS: contract-award identifiers, UEI/PIID matching, modifications, exclusions, and procurement-firewall stress tests.
- IRS 8871/8872, TEOS, and Form 990 XML: nonprofit, 527, association, think-tank, and intermediary panels, while preserving public-donor missingness.
- FACA, House witness disclosures, OGE, OpenSecrets, LegiStorm, and ProPublica-style panels: access, expert, intermediary, and revolving-door bridges where coverage and licensing allow.

The implementation stores benchmark metadata in `data/calibration/empirical-benchmarks.csv`, normalized fixture rows in `data/fixtures/`, source-native JSON parser fixtures in `data/fixtures/source-native/`, and the committed paper snapshot under `data/snapshots/2024-env/normalized/`. Report generation defaults to that committed snapshot so ignored `data/raw/` live-fetch outputs cannot alter paper artifacts unless `LOBBY_CAPTURE_CALIBRATION_DIR` is set explicitly.

The Deep Research reports are distilled into `docs/research/research-synthesis.md` and `data/calibration/parameter-map.csv`. The parameter map is the preferred place to add new empirical moments because it records a model metric, low/mid/high prior, evidence class, source report, model target, and implementation status.

Current calibration links:

- `normalized-lda-lobbying.csv` constrains issue funding scale, issue mix, and disclosure lag.
- `normalized-fec-campaign-finance.csv` constrains donor concentration, Schedule E outside-spending pressure, public-financing share, and traceability.
- `normalized-regulatory-dockets.csv` constrains docket volume, comment authenticity, template saturation, and technical-claim credibility.
- `reports/source-moments.csv` records direct top-k concentration, traceability, direct dark-money visibility, Schedule E outside spending, public financing, comment-record, procurement bridge, intermediary, and revolving-door moments from the current snapshot and fixture baselines.

These files are plausibility inputs. They should not be cited as causal estimates, and paper claims should distinguish three layers: observed distribution, model calibration choice, and simulated mechanism.

The fetch scripts now have two modes:

- default mode copies tracked deterministic fixtures into `data/raw/` for snapshot preparation and local experiments;
- `--live` mode normalizes an explicit CSV path or URL into the same schema and fails if required columns are missing;
- source-native `--live` mode queries LDA, OpenFEC, Regulations.gov, Federal Register, USAspending, or LDA-derived covered-position revolving-door records when no explicit CSV/URL is supplied.

Expected live-mode environment variables are `LDA_LIVE_CSV` or `LDA_LIVE_URL`, `FEC_LIVE_CSV` or `FEC_LIVE_URL`, and `REGULATORY_LIVE_CSV` or `REGULATORY_LIVE_URL` for explicit-source normalization.

Source-native live variables:

- LDA: `LDA_API_BASE`, `LDA_API_KEY`, `LDA_YEAR`, `LDA_PERIOD`, `LDA_MAX_PAGES`.
- FEC: `FEC_API_KEY`, `FEC_API_BASE`, `FEC_CYCLE`, `FEC_COMMITTEE_ID`, `FEC_INCLUDE_SCHEDULE_E`, `FEC_ONLY_SCHEDULE_E`, `FEC_SCHEDULE_E_MAX_PAGES`.
- Regulations.gov: `REGULATIONS_API_KEY`, `REGULATIONS_API_BASE`, `REGULATORY_AGENCY`, `REGULATORY_SEARCH_TERM`, `REGULATORY_DATE_FROM`, `REGULATORY_DATE_TO`.
- Federal Register: `REGULATORY_SOURCE=federal-register`, `FEDERAL_REGISTER_API_BASE`, `FEDERAL_REGISTER_TYPE`, `REGULATORY_SEARCH_TERM`, `REGULATORY_DATE_FROM`, `REGULATORY_DATE_TO`.
- Retry controls: `SOURCE_FETCH_RETRIES`, `SOURCE_FETCH_BACKOFF_SECONDS`.
- Raw-payload archive control: `SOURCE_RAW_DIR`.
- USAspending enrichment: `USASPENDING_ENRICH_AWARD_DETAILS`, `USASPENDING_ENRICH_TRANSACTIONS`, `USASPENDING_ENRICH_LIMIT`, `USASPENDING_TRANSACTION_LIMIT`.
- Public-financing bridge: `PUBLIC_FINANCING_LIVE_CSV` or `PUBLIC_FINANCING_LIVE_URL`.
- Revolving-door bridge: `REVOLVING_DOOR_SOURCE_NATIVE`, `REVOLVING_DOOR_LDA_PAGE_SIZE`, `REVOLVING_DOOR_LDA_MAX_PAGES`.

The source-native normalizers are distributional bridges. `scripts/test-source-fetchers.py` verifies representative LDA, OpenFEC, Regulations.gov, Federal Register, and USAspending JSON payloads against exact normalized rows before any live API output is used as a paper snapshot.

The source acquisition roadmap in `docs/source-data-roadmap.md` records the intended identifier spine and distinguishes direct observed sources from proxy and restricted overlays. New source panels should be added there before their moments are promoted into `data/calibration/parameter-map.csv`.

`make source-moments` writes `reports/source-moments.csv` plus `reports/source-moments.md`. It compares the current 2024 EPA/ENV normalized snapshot against the deterministic fixture baseline on source-level moments such as top-client share, top-donor share, amount-weighted traceability, direct dark-money visibility, Schedule E outside-spending source share, public-financing source share, comment-volume concentration, procurement single-bid and modification proxies, UEI/PIID coverage, intermediary donor disclosure, intermediary political-spend share, and revolving-door source-confidence diagnostics. `make source-panel-inventory` then writes `reports/source-panel-inventory.csv` and `.md`, classifying whether direct dark-money, outside-spending, public-financing, intermediary, revolving-door, and procurement panels are usable, thin, warning-level, or missing.

`make validate` compares committed report snapshots against both `data/calibration/empirical-benchmarks.csv` and implemented rows in `data/calibration/parameter-map.csv`. It writes `reports/validation-summary.csv` plus `reports/validation-summary.md`, including counts by evidence class and scope notes for scenario-specific benchmarks such as public-financing uptake, voucher participation, campaign-finance concentration, hidden substitution, cooling-off venue shifting, and procurement exposure. It also writes `reports/substitution-audit.csv` and `reports/substitution-audit.md`, which flag possible reform failures only when observed capture falls while hidden influence, hidden capture, total distortion, or substitution-failure risk rises. Pure movement into a different channel without a distortion increase is classified as a substitution tradeoff rather than a clean failure. Network metrics are included as synthetic path diagnostics: they currently validate bounds and mechanism direction, not observed network reconstruction. Current benchmark rows are deliberately broad plausibility bands; misses should be read as calibration work queues, not model falsification.

`make portfolio` writes `reports/lobby-capture-portfolio.csv` plus `reports/lobby-capture-portfolio.md`. It screens reform bundles by total influence distortion, hidden capture, substitution risk, administrative burden, network opacity, legitimate-advocacy chill, speech-restriction risk, cross-venue detection, and participation protection.

`make calibration-queue` writes `reports/calibration-queue.csv` plus `reports/calibration-queue.md`. It classifies misses and partial overlaps as model tuning, metric splits, direct source moments, scenario coverage, scale alignment, or benchmark review.

The next paper-grade snapshot is fixed to a closed 2024 environmental slice:

- LDA: 2024 Q1-Q4 LD-2 activity reports, post-filtered to `ENV` and EPA-facing contacts where possible.
- FEC: 2024 cycle records for the six national party committees, Schedule E independent expenditures, and configured public-financing bridge rows.
- Regulations.gov: EPA documents, dockets, and comments posted in 2024.
- Federal Register: EPA 2024 rules and proposed rules.
- USAspending/SAM/FPDS: EPA FY2024 awards, UEIs, PIIDs, competition fields, offer counts, and modification records where source access permits.
- Intermediaries and revolving door: IRS nonprofit/527 rows plus LDA-derived covered-position revolving-door rows or a richer licensed/public personnel-access panel where configured.

Run `scripts/run-2024-env-live-snapshot.sh` to execute the pinned live slice. The runner preserves raw public API payloads under ignored `data/raw/source-payloads/2024-env/`, writes normalized rows under `data/raw/`, freezes `data/snapshots/2024-env/`, and records per-source status in `data/snapshots/2024-env/live-run-status.csv`.

The current committed 2024 EPA/ENV snapshot was regenerated from official endpoints and bridge fixtures on May 8, 2026 using the configured local API keys where required:

- LDA: 121 normalized 2024 `ENV` rows from the Senate LDA API.
- FEC: 1003 normalized 2024 OpenFEC and bridge rows, including six national party committee requests, Schedule E independent expenditures, and public-financing bridge rows.
- Regulations.gov and Federal Register: 200 combined EPA 2024 regulatory rows.
- USAspending: 200 EPA fiscal-year 2024 award rows with UEI/PIID coverage and award-detail/transaction-derived competition or modification proxies where the source returns them.
- Revolving door: 284 LDA-derived covered-position rows. This is source-native but narrower than a full post-employment panel.
- Intermediaries: 6 tracked fixture rows for nonprofit, 527, association, and think-tank schema continuity because no representative IRS/OpenSecrets/ProPublica panel is configured yet.

The snapshot is stronger than the earlier public/demo run, but it is still not a representative empirical panel. Schedule E rows are separated from direct dark-money rows, so the current direct dark-money source share remains zero even though outside-spending pressure is now present. Public-financing rows are bridge rows rather than a representative national panel, procurement remains EPA/USAspending-centered rather than a broad SAM/FPDS panel, and the intermediary file remains a fixture. `reports/source-moments.md` records these representativeness warnings directly.

Run `make snapshot-2024-env` after any subsequent source-native fetches to freeze normalized rows under `data/snapshots/2024-env/` and write a machine-readable manifest with row counts, request templates, hashes, and Git state.
