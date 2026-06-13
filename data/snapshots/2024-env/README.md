# 2024 EPA/ENV Snapshot

This directory is the reproducible closed-window snapshot scaffold for the first paper-grade validation slice.

Scope:

- Calendar window: 2024-01-01 through 2024-12-31.
- LDA issue code: ENV.
- Agency: EPA.
- FEC cycle: 2024, with the six national party committees as the first electoral-pressure panel.
- Outside-spending bridge: OpenFEC Schedule E independent expenditures.
- Electoral-communication bridge: OpenFEC electioneering communications and communication-cost rows when available.
- Public-financing bridge: NYC CFB public-funds payments, Seattle Democracy Voucher rows, or configured program export rows carried as a separate bridge panel.
- Dark-money bridge: configured source export rows, ProPublica/IRS Form 990 Schedule I nonprofit-routing transfer rows, or IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows; super PAC rows remain separate and nonprofit-routing rows do not identify underlying donors.
- USAspending fiscal year: 2024, Environmental Protection Agency awards.
- USAspending procurement bridge: multi-agency fiscal-year 2024 top-award rows for high-value procurement diagnostics, kept separate from the EPA calibration slice and action-panel denominator.
- USAspending procurement actions: expanded stratified 12-agency quarterly transaction/action rows for concentration and modification-incidence diagnostics when present, combining initial-action, high-value, and action-date strata and kept separate from award rows and top-award bridge rows.
- USAspending national procurement actions: no-agency-filtered fiscal-year 2024 transaction/action rows for national-volume agency and recipient concentration diagnostics, kept separate from modification-incidence denominators.
- USAspending bulk transaction summary: checksumed summary of the public download/count and download/transactions route when full normalized rows are archived outside git.
- SAM.gov Contract Awards: optional source-native action rows for PIID/UEI, competition, modification, award-date, and contracting-department diagnostics, kept separate from USAspending action rows so source provenance remains visible.
- Revolving-door panel: licensed/source export or LDA covered-position derivation when available; fixture otherwise.
- Intermediary panel: NYC CFB intermediary rows, IRS EO BMF nonprofit/association capacity rows, IRS POFD Form 8872 527 political-organization rows, or configured nonprofit, 527, association, and think-tank export when available; fixture otherwise.

The current command freezes whatever normalized files are present under `data/raw/`. Live paper snapshots should first run the request templates in `manifest.json`, preserve raw payloads outside git when too large, normalize into the same schemas, and then rerun `make snapshot-2024-env`.

| Source | Rows | Status | Normalized file |
| --- | ---: | --- | --- |
| lda | 121 | live | `data/snapshots/2024-env/normalized/lda-lobbying.csv` |
| fec | 1268 | live | `data/snapshots/2024-env/normalized/fec-campaign-finance.csv` |
| public-financing | 135 | live | `data/snapshots/2024-env/normalized/public-financing.csv` |
| dark-money | 330 | live | `data/snapshots/2024-env/normalized/dark-money.csv` |
| regulatory | 200 | live | `data/snapshots/2024-env/normalized/regulatory-dockets.csv` |
| usaspending | 200 | live | `data/snapshots/2024-env/normalized/usaspending-awards.csv` |
| usaspending-procurement-bridge | 150 | live | `data/snapshots/2024-env/normalized/usaspending-procurement-bridge.csv` |
| usaspending-procurement-actions | 28115 | live | `data/snapshots/2024-env/normalized/usaspending-procurement-actions.csv` |
| usaspending-procurement-national-actions | 1500 | live | `data/snapshots/2024-env/normalized/usaspending-procurement-national-actions.csv` |
| usaspending-procurement-bulk-summary | 6449101 | copied | `data/snapshots/2024-env/normalized/usaspending-procurement-bulk-summary.json` |
| sam-contract-awards | 0 | missing | `data/snapshots/2024-env/normalized/sam-contract-awards.csv` |
| revolving-door | 803 | live | `data/snapshots/2024-env/normalized/revolving-door.csv` |
| intermediary | 1353 | live | `data/snapshots/2024-env/normalized/intermediaries.csv` |

`live-run-status.csv` records which official live requests completed and which were blocked by public API limits or missing credentials.
