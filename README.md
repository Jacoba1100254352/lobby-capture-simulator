# Lobby Capture Simulator

Standalone Java simulation focused on lobbying, money in politics, regulatory capture, and anti-capture reforms.

The current implementation is the first runnable slice of `PROJECT_PLAN.md`. It treats lobby organizations as strategic budget allocators across influence channels, then resolves outcomes in legislative, rulemaking, election, procurement, litigation, enforcement, and public-information arenas.

## Run

```sh
make test
make run ARGS="--list"
make run ARGS="--scenario reform-threat-mobilization --runs 10 --contests 30 --seed 7"
make campaign
make sensitivity
make ablation
make interactions
make source-moments
make validate
make calibration-queue
make snapshot-2024-env
make tables
make figures
make paper
```

`make campaign` writes:

- `reports/lobby-capture-campaign.csv`
- `reports/lobby-capture-campaign.md`

`make sensitivity` writes:

- `reports/lobby-capture-sensitivity.csv`
- `reports/lobby-capture-sensitivity.md`

`make ablation` writes:

- `reports/lobby-capture-ablation.csv`
- `reports/lobby-capture-ablation.md`

`make interactions` writes:

- `reports/lobby-capture-interactions.csv`
- `reports/lobby-capture-interactions.md`

Each report run also writes a `*.manifest.json` sidecar with seed, runs, contests, command, Java version, source Git state, and calibration checksum. `make validate` compares committed report snapshots against benchmark plausibility ranges and writes:

- `reports/validation-summary.csv`
- `reports/validation-summary.md`

Validation now also reads `data/calibration/parameter-map.csv`, which classifies targets as observed, inferred, proxy, sectoral, or judgmental. The parameter map is the bridge from the Deep Research reports to simulator metrics.

`make source-moments` writes direct diagnostics from normalized source tables:

- `reports/source-moments.csv`
- `reports/source-moments.md`

`make calibration-queue` classifies validation misses and partial overlaps into model-tuning, metric-split, source-moment, scenario-coverage, scale-alignment, or benchmark-review work.

The fetch scripts seed normalized local calibration data from tracked fixtures:

```sh
./scripts/fetch-lda.sh
./scripts/fetch-fec.sh
./scripts/fetch-regulatory.sh
```

Optional live normalization uses the same output schemas. You can pass an explicit local CSV/URL, or let the scripts query their upstream source-native APIs:

```sh
LDA_LIVE_CSV=/path/to/lda.csv ./scripts/fetch-lda.sh --live
FEC_LIVE_URL=https://example.org/fec.csv ./scripts/fetch-fec.sh --live
REGULATORY_LIVE_CSV=/path/to/dockets.csv ./scripts/fetch-regulatory.sh --live

LDA_API_KEY=... ./scripts/fetch-lda.sh --live
FEC_API_KEY=... ./scripts/fetch-fec.sh --live
REGULATIONS_API_KEY=... ./scripts/fetch-regulatory.sh --live
REGULATORY_SOURCE=federal-register ./scripts/fetch-regulatory.sh --live
```

The pinned 2024 EPA/ENV live runner is:

```sh
scripts/run-2024-env-live-snapshot.sh
```

It preserves raw public API payloads under ignored `data/raw/source-payloads/2024-env/`, writes normalized rows into `data/raw/`, runs the snapshot freezer, and emits source moments. If no personal API keys are configured it uses official public/demo access where possible and records rate-limit gaps in `data/snapshots/2024-env/live-run-status.csv`.

`make snapshot-2024-env` freezes the current normalized source rows under `data/snapshots/2024-env/` and writes a manifest for the first closed-window paper snapshot: 2024 LDA `ENV`, EPA Regulations.gov/Federal Register activity, and the 2024 FEC cycle. Live paper snapshots should run the source-native fetchers with those fixed filters before freezing.

`make tables` regenerates LaTeX table files under `paper/tables/` from the committed report CSV snapshots. `make figures` regenerates paper interaction figures under `paper/figures/`. `make paper` runs both generators before building the PDF. Table selection lives in `paper/tables.yml`, so paper row/column/caption edits do not require changing the generator.

The source-native fetcher has tiny checked-in JSON fixtures under `data/fixtures/source-native/`. `make test` verifies those parser paths without hitting the network. Live source requests retry transient `429` and `5xx` responses; tune with `SOURCE_FETCH_RETRIES` and `SOURCE_FETCH_BACKOFF_SECONDS`.

## Current Modeling Slice

The MVP answers a narrow question from the project plan:

> When organized interests face a meaningful anti-capture reform threat, do they shift from ordinary policy capture to defensive reform blocking, and which reforms remain effective after that adaptation?

It includes:

- finite disclosed, dark-money, legal, campaign, grassroots, and research budgets;
- explicit client funding and client-to-lobby money flows;
- adaptive channel selection, channel-return memory, per-client/per-domain funding multipliers, regulator attention queues, watchdog monitoring budgets, and reform-decay pressure;
- direct access, agenda access, information distortion, public campaigns, litigation threats, campaign finance, dark money, revolving-door access, and defensive reform spending;
- first-class rulemaking dockets, comment campaigns, authenticity, template saturation, and technical-claim credibility;
- comment-record triage with unique-information share, duplicate compression, review burden, procedural acknowledgment, and substantive uptake;
- split validation-facing source metrics for all-flow traceability, dark-money direct visibility, resident voucher participation, and candidate public-financing uptake;
- evasion profiles with dark-pool, litigation-funding, procurement-consultant, and revolving-door substitution pressure;
- an influence-substitution engine that reports hidden influence, preserved influence capacity, messenger substitution, venue substitution, and net transparency gain after reforms constrain a channel;
- arena-specific capture susceptibility;
- transparency, public financing, democracy vouchers, cooling-off, blind review, public advocates, enforcement, anti-astroturf systems, defensive-spend caps, and dark-money disclosure;
- raw and composite scenario metrics plus sensitivity, ablation, adaptation-speed, and reform-decay metrics.
- validation summaries and two-way reform interaction sweeps.

The formulas are stylized and comparative. Empirical files under `data/calibration/` and normalized fixtures under `data/fixtures/` are benchmark scaffolds, not causal estimates.
