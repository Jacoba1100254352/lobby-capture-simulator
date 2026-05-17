# 2024 EPA/ENV Snapshot

This directory is the reproducible closed-window snapshot scaffold for the first paper-grade validation slice.

Scope:

- Calendar window: 2024-01-01 through 2024-12-31.
- LDA issue code: ENV.
- Agency: EPA.
- FEC cycle: 2024, with the six national party committees as the first electoral-pressure panel.
- Outside-spending bridge: OpenFEC Schedule E independent expenditures when available.
- Public-financing bridge: configured public-financing source or fixture rows carried as a separate bridge panel.
- Direct dark-money bridge: documented 501(c)(4), 501(c)(6), electioneering, or source-export rows when available; super PAC rows remain separate.
- USAspending fiscal year: 2024, Environmental Protection Agency awards.
- Revolving-door panel: licensed/source export or LDA covered-position derivation when available; fixture otherwise.
- Intermediary panel: nonprofit, 527, association, and think-tank export when available; fixture otherwise.

The current command freezes whatever normalized files are present under `data/raw/`. Live paper snapshots should first run the request templates in `manifest.json`, preserve raw payloads outside git when too large, normalize into the same schemas, and then rerun `make snapshot-2024-env`.

| Source | Rows | Status | Normalized file |
| --- | ---: | --- | --- |
| lda | 121 | live | `data/snapshots/2024-env/normalized/lda-lobbying.csv` |
| fec | 1003 | partial-live | `data/snapshots/2024-env/normalized/fec-campaign-finance.csv` |
| public-financing | 3 | fixture | `data/snapshots/2024-env/normalized/public-financing.csv` |
| dark-money | 0 | missing | `data/snapshots/2024-env/normalized/dark-money.csv` |
| regulatory | 200 | live | `data/snapshots/2024-env/normalized/regulatory-dockets.csv` |
| usaspending | 200 | live | `data/snapshots/2024-env/normalized/usaspending-awards.csv` |
| revolving-door | 284 | live | `data/snapshots/2024-env/normalized/revolving-door.csv` |
| intermediary | 6 | fixture | `data/snapshots/2024-env/normalized/intermediaries.csv` |

`live-run-status.csv` records which official live requests completed and which were blocked by public API limits or missing credentials.
