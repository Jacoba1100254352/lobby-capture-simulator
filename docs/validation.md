# Validation Plan

This project uses external data to constrain plausible ranges, not to claim causal estimates.

Initial validation targets:

- LDA filings: lobbying spending distributions, issue-domain mix, registrant/client concentration, covered official fields.
- FEC data: large donor dependence, PAC/independent expenditure pressure, lobbyist bundling, outside-spending concentration.
- Federal Register and Regulations.gov: rulemaking duration, docket/comment volume, agency/topic mix.
- Voteview and govinfo bill status: legislative attrition and coalition plausibility for legislative arenas.
- NYC public matching funds, Seattle democracy vouchers, and related programs: voucher participation, public-funds share, donor-base broadening.
- USAspending: procurement-recipient concentration and agency spending exposure.
- SAM/FPDS: contract-award identifiers, UEI/PIID matching, modifications, exclusions, and procurement-firewall stress tests.
- IRS EO BMF, IRS 8871/8872, and Form 990 XML: nonprofit, 527, association, think-tank, and intermediary panels, while preserving public-donor missingness.
- FACA, House witness disclosures, OGE, OpenSecrets, LegiStorm, and ProPublica-style panels: access, expert, intermediary, and revolving-door bridges where coverage and licensing allow.

The implementation stores benchmark metadata in `data/calibration/empirical-benchmarks.csv`, normalized fixture rows in `data/fixtures/`, source-native JSON parser fixtures in `data/fixtures/source-native/`, and the committed paper snapshot under `data/snapshots/2024-env/normalized/`. Report generation defaults to that committed snapshot so ignored `data/raw/` live-fetch outputs cannot alter paper artifacts unless `LOBBY_CAPTURE_CALIBRATION_DIR` is set explicitly.

The Deep Research reports are distilled into `docs/research/research-synthesis.md` and `data/calibration/parameter-map.csv`. The parameter map is the preferred place to add new empirical moments because it records a model metric, low/mid/high prior, evidence class, source report, model target, and implementation status.

Current calibration links:

- `normalized-lda-lobbying.csv` constrains issue funding scale, issue mix, and disclosure lag.
- `normalized-fec-campaign-finance.csv` constrains donor concentration, Schedule E outside-spending pressure, and traceability; `normalized-public-financing.csv` and `normalized-dark-money.csv` carry separate public-financing and opaque-capacity bridge rows.
- `normalized-regulatory-dockets.csv` constrains docket volume, comment authenticity, template saturation, and technical-claim credibility.
- `reports/source-moments.csv` records direct top-k concentration, traceability, direct dark-money visibility, Schedule E outside spending, public financing, comment-record, procurement bridge, intermediary, and revolving-door moments from the current snapshot and fixture baselines.

These files are plausibility inputs. They should not be cited as causal estimates, and paper claims should distinguish three layers: observed distribution, model calibration choice, and simulated mechanism.

The fetch scripts now have two modes:

- default mode copies tracked deterministic fixtures into `data/raw/` for snapshot preparation and local experiments;
- `--live` mode normalizes an explicit CSV path or URL into the same schema and fails if required columns are missing;
- source-native `--live` mode queries LDA, OpenFEC, Regulations.gov, Federal Register, USAspending, NYC CFB, IRS EO BMF, or LDA-derived covered-position revolving-door records when no explicit CSV/URL is supplied.

Expected live-mode environment variables are `LDA_LIVE_CSV` or `LDA_LIVE_URL`, `FEC_LIVE_CSV` or `FEC_LIVE_URL`, and `REGULATORY_LIVE_CSV` or `REGULATORY_LIVE_URL` for explicit-source normalization.

Source-native live variables:

- LDA: `LDA_API_BASE`, `LDA_API_KEY`, `LDA_YEAR`, `LDA_PERIOD`, `LDA_MAX_PAGES`, `LDA_DISCLOSURE_VISIBILITY_LAG`.
- FEC: `FEC_API_KEY`, `FEC_API_BASE`, `FEC_CYCLE`, `FEC_COMMITTEE_ID`, `FEC_INCLUDE_SCHEDULE_E`, `FEC_ONLY_SCHEDULE_E`, `FEC_SCHEDULE_E_MAX_PAGES`.
- Regulations.gov: `REGULATIONS_API_KEY`, `REGULATIONS_API_BASE`, `REGULATORY_AGENCY`, `REGULATORY_SEARCH_TERM`, `REGULATORY_DATE_FROM`, `REGULATORY_DATE_TO`.
- Federal Register: `REGULATORY_SOURCE=federal-register`, `FEDERAL_REGISTER_API_BASE`, `FEDERAL_REGISTER_TYPE`, `REGULATORY_SEARCH_TERM`, `REGULATORY_DATE_FROM`, `REGULATORY_DATE_TO`.
- Retry controls: `SOURCE_FETCH_RETRIES`, `SOURCE_FETCH_BACKOFF_SECONDS`.
- Raw-payload archive control: `SOURCE_RAW_DIR`.
- USAspending enrichment: `USASPENDING_ENRICH_AWARD_DETAILS`, `USASPENDING_ENRICH_TRANSACTIONS`, `USASPENDING_ENRICH_LIMIT`, `USASPENDING_TRANSACTION_LIMIT`.
- USAspending modification handling: `USASPENDING_TREAT_LATEST_TRANSACTION_AS_MODIFICATION=0` keeps award-level rows from being marked as ex-post modifications just because the latest enriched transaction is a modification; set it to `1` only for action-level stress tests.
- Public-financing bridge: `PUBLIC_FINANCING_SOURCE_NATIVE`, `NYC_CFB_DATA_BASE`, `NYC_CFB_ELECTION`, `NYC_CFB_PUBLIC_PAYMENTS_MAX_ROWS`, `NYC_CFB_FINANCIAL_ANALYSIS_MAX_ROWS`, plus `PUBLIC_FINANCING_LIVE_CSV` or `PUBLIC_FINANCING_LIVE_URL` for configured exports.
- Dark-money/opaque-capacity bridge: `DARK_MONEY_SOURCE_NATIVE`, `IRS_DARK_MONEY_BMF_STATES`, `IRS_DARK_MONEY_BMF_SUBSECTIONS`, `IRS_DARK_MONEY_CAPACITY_MAX_ROWS`, `IRS_DARK_MONEY_CAPACITY_OUTPUT_ROWS`, and capacity-rate controls. These rows are proxies for opaque nonprofit capacity, not direct donor observations.
- Intermediary bridge: `INTERMEDIARY_SOURCE_NATIVE`, `NYC_CFB_INTERMEDIARY_MAX_ROWS`, `IRS_EO_BMF_CSV_BASE`, `IRS_EO_BMF_STATES`, `IRS_EO_BMF_SUBSECTIONS`, `IRS_EO_BMF_MAX_ROWS`, `IRS_EO_BMF_FILTERED_MAX_ROWS`, and `IRS_EO_BMF_KEYWORDS`.
- Revolving-door bridge: `REVOLVING_DOOR_SOURCE_NATIVE`, `REVOLVING_DOOR_LDA_PAGE_SIZE`, `REVOLVING_DOOR_LDA_MAX_PAGES`.
- Optional curated overlays: `OPENSECRETS_API_KEY`, `FOLLOWTHEMONEY_API_KEY`, `PROPUBLICA_NONPROFIT_API_KEY`, and `LEGISTORM_API_KEY` are documented for richer source panels, but the current paper snapshot promotes only implemented source-native fetchers or explicitly configured normalized CSV/URL bridges.

The source-native normalizers are distributional bridges. `scripts/test-source-fetchers.py` verifies representative LDA, OpenFEC, Regulations.gov, Federal Register, USAspending, NYC CFB, and IRS EO BMF payloads against exact normalized rows before any live API output is used as a paper snapshot.

The source acquisition roadmap in `docs/source-data-roadmap.md` records the intended identifier spine and distinguishes direct observed sources from proxy and restricted overlays. New source panels should be added there before their moments are promoted into `data/calibration/parameter-map.csv`.

`make source-moments` writes `reports/source-moments.csv` plus `reports/source-moments.md`. It compares the current 2024 EPA/ENV normalized snapshot against the deterministic fixture baseline on source-level moments such as top-client share, top-donor share, amount-weighted traceability, direct dark-money visibility, Schedule E outside-spending source share, public-financing source share, comment-volume concentration, procurement single-bid and modification proxies, UEI/PIID coverage, intermediary donor disclosure, intermediary political-spend share, and revolving-door source-confidence diagnostics. `make source-panel-inventory` then writes `reports/source-panel-inventory.csv` and `.md`, classifying whether direct dark-money, outside-spending, public-financing, intermediary, revolving-door, and procurement panels are usable, thin, warning-level, or missing.

`make validate` compares committed report snapshots against both `data/calibration/empirical-benchmarks.csv` and implemented rows in `data/calibration/parameter-map.csv`. It writes `reports/validation-summary.csv` plus `reports/validation-summary.md`, including counts by evidence class and scope notes for scenario-specific benchmarks such as public-financing uptake, voucher participation, campaign-finance concentration, hidden substitution, cooling-off venue shifting, and procurement exposure. Source-moment rows can also be classified as `source_gap` when the available panel is too narrow or too proxy-backed to test the benchmark directly. Examples include EPA-only procurement rows against multi-agency concentration targets, award-level USAspending rows against ex-post modification benchmarks, and thin dark-money proxy rows against direct hidden-donor visibility targets. It also writes `reports/substitution-audit.csv` and `reports/substitution-audit.md`, which distinguish distortion failures, hidden-capture warnings, hidden-influence warnings, substitution warnings, and channel-shift tradeoffs. Pure movement into a different channel without a distortion increase is classified as a channel-shift tradeoff rather than a clean failure. Network metrics are included as synthetic path diagnostics: they currently validate bounds and mechanism direction, not observed network reconstruction. Current benchmark rows are deliberately broad plausibility bands; misses and source gaps should be read as calibration work queues, not model falsification.

`make portfolio` writes `reports/lobby-capture-portfolio.csv` plus `reports/lobby-capture-portfolio.md`. It screens reform bundles by total influence distortion, hidden capture, substitution risk, administrative burden, network opacity, legitimate-advocacy chill, speech-restriction risk, cross-venue detection, and participation protection.

`make calibration-queue` writes `reports/calibration-queue.csv` plus `reports/calibration-queue.md`. It classifies misses and partial overlaps as model tuning, metric splits, direct source moments, scenario coverage, scale alignment, or benchmark review.

The next paper-grade snapshot is fixed to a closed 2024 environmental slice:

- LDA: 2024 Q1-Q4 LD-2 activity reports, post-filtered to `ENV` and EPA-facing contacts where possible.
- FEC: 2024 cycle records for the six national party committees and Schedule E independent expenditures.
- Public financing and campaign intermediaries: NYC CFB public-funds payment and intermediary rows, or configured program exports.
- Opaque nonprofit capacity: IRS EO BMF 501(c)(4)/(c)(6) capacity rows or configured direct dark-money exports, kept separate from super PAC independent expenditures.
- Regulations.gov: EPA documents, dockets, and comments posted in 2024.
- Federal Register: EPA 2024 rules and proposed rules.
- USAspending/SAM/FPDS: EPA FY2024 awards, UEIs, PIIDs, competition fields, offer counts, and modification records where source access permits.
- Intermediaries and revolving door: NYC CFB intermediary rows, IRS EO BMF nonprofit/association rows, IRS 527/Form 990 rows where configured, plus LDA-derived covered-position revolving-door rows or a richer licensed/public personnel-access panel where configured.

Run `scripts/run-2024-env-live-snapshot.sh` to execute the pinned live slice. The runner preserves raw public API payloads under ignored `data/raw/source-payloads/2024-env/`, writes normalized rows under `data/raw/`, freezes `data/snapshots/2024-env/`, and records per-source status in `data/snapshots/2024-env/live-run-status.csv`.

The current committed 2024 EPA/ENV snapshot is regenerated from official endpoints and bridge sources using configured local API keys where required and no-key public CSV/API endpoints where available:

- LDA: 121 normalized 2024 `ENV` rows from the Senate LDA API.
- FEC: normalized 2024 OpenFEC rows, including six national party committee requests and Schedule E independent expenditures.
- Public financing: NYC CFB public-funds payment rows or configured program exports, stored as a separate bridge panel.
- Dark money/opaque capacity: IRS EO BMF 501(c)(4)/(c)(6) capacity proxy rows or configured direct dark-money exports, stored separately from ordinary FEC and Schedule E rows.
- Regulations.gov and Federal Register: 200 combined EPA 2024 regulatory rows.
- USAspending: EPA fiscal-year 2024 award rows with UEI/PIID coverage and award-detail competition fields where the source returns them; latest-transaction modifications are kept separate from award-level modification status unless explicitly enabled.
- Revolving door: 284 LDA-derived covered-position rows. This is source-native but narrower than a full post-employment panel.
- Intermediaries: NYC CFB intermediary rows plus IRS EO BMF nonprofit/association capacity rows by default; richer IRS 527/Form 990/OpenSecrets/ProPublica panels remain optional overlays.

The snapshot is stronger than the earlier public/demo run, but it is still not a representative empirical panel. Schedule E rows are separated from dark-money/opaque-capacity rows, and IRS EO BMF rows should be read as capacity proxies rather than observed hidden spending. NYC CFB public-financing and intermediary rows are direct local program records, not national estimates. Procurement remains EPA/USAspending-centered rather than a broad SAM/FPDS action-level panel. `reports/source-moments.md` records these representativeness warnings directly.

Run `make snapshot-2024-env` after any subsequent source-native fetches to freeze normalized rows under `data/snapshots/2024-env/` and write a machine-readable manifest with row counts, request templates, hashes, and Git state.
