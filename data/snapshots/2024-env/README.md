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
- Dark-money bridge: configured source export rows or IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows; super PAC rows remain separate.
- USAspending fiscal year: 2024, Environmental Protection Agency awards.
- USAspending procurement bridge: multi-agency fiscal-year 2024 top-award rows for procurement concentration diagnostics, kept separate from the EPA calibration slice.
- USAspending procurement actions: transaction/action rows for modification-incidence diagnostics when present, kept separate from award rows and concentration rows.
- Revolving-door panel: licensed/source export or LDA covered-position derivation when available; fixture otherwise.
- Intermediary panel: NYC CFB intermediary rows, IRS EO BMF nonprofit/association capacity rows, IRS POFD Form 8872 527 political-organization rows, or configured nonprofit, 527, association, and think-tank export when available; fixture otherwise.

The current command freezes whatever normalized files are present under `data/raw/`. Live paper snapshots should first run the request templates in `manifest.json`, preserve raw payloads outside git when too large, normalize into the same schemas, and then rerun `make snapshot-2024-env`.

| Source | Rows | Status | Normalized file |
| --- | ---: | --- | --- |
| lda | 121 | live | `data/snapshots/2024-env/normalized/lda-lobbying.csv` |
| fec | 1269 | live | `data/snapshots/2024-env/normalized/fec-campaign-finance.csv` |
| public-financing | 135 | live | `data/snapshots/2024-env/normalized/public-financing.csv` |
| dark-money | 250 | live | `data/snapshots/2024-env/normalized/dark-money.csv` |
| regulatory | 200 | live | `data/snapshots/2024-env/normalized/regulatory-dockets.csv` |
| usaspending | 200 | live | `data/snapshots/2024-env/normalized/usaspending-awards.csv` |
| usaspending-procurement-bridge | 150 | live | `data/snapshots/2024-env/normalized/usaspending-procurement-bridge.csv` |
| usaspending-procurement-actions | 1200 | live | `data/snapshots/2024-env/normalized/usaspending-procurement-actions.csv` |
| revolving-door | 284 | live | `data/snapshots/2024-env/normalized/revolving-door.csv` |
| intermediary | 1353 | live | `data/snapshots/2024-env/normalized/intermediaries.csv` |

`live-run-status.csv` records which official live requests completed and which were blocked by public API limits or missing credentials.
