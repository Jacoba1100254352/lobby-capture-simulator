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
make tables
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

`make tables` regenerates LaTeX table files under `paper/tables/` from the committed report CSV snapshots. `make paper` runs that table generator before building the PDF.

## Current Modeling Slice

The MVP answers a narrow question from the project plan:

> When organized interests face a meaningful anti-capture reform threat, do they shift from ordinary policy capture to defensive reform blocking, and which reforms remain effective after that adaptation?

It includes:

- finite disclosed, dark-money, legal, campaign, grassroots, and research budgets;
- explicit client funding and client-to-lobby money flows;
- adaptive channel selection, channel-return memory, client funding multipliers, regulator attention, and watchdog focus;
- direct access, agenda access, information distortion, public campaigns, litigation threats, campaign finance, dark money, revolving-door access, and defensive reform spending;
- first-class rulemaking dockets, comment campaigns, authenticity, template saturation, and technical-claim credibility;
- evasion profiles with dark-pool, litigation-funding, procurement-consultant, and revolving-door substitution pressure;
- arena-specific capture susceptibility;
- transparency, public financing, democracy vouchers, cooling-off, blind review, public advocates, enforcement, anti-astroturf systems, defensive-spend caps, and dark-money disclosure;
- raw and composite scenario metrics plus sensitivity, ablation, and adaptation metrics.

The formulas are stylized and comparative. Empirical files under `data/calibration/` and normalized fixtures under `data/fixtures/` are benchmark scaffolds, not causal estimates.
