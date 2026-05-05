# 2024 EPA/ENV Snapshot

This directory is the reproducible closed-window snapshot scaffold for the first paper-grade validation slice.

Scope:

- Calendar window: 2024-01-01 through 2024-12-31.
- LDA issue code: ENV.
- Agency: EPA.
- FEC cycle: 2024, with the six national party committees as the first electoral-pressure panel.
- USAspending fiscal year: 2024, Environmental Protection Agency awards.
- Revolving-door panel: licensed/source export when available; fixture otherwise.

The current command freezes whatever normalized files are present under `data/raw/`. Live paper snapshots should first run the request templates in `manifest.json`, preserve raw payloads outside git when too large, normalize into the same schemas, and then rerun `make snapshot-2024-env`.

| Source | Rows | Status | Normalized file |
| --- | ---: | --- | --- |
| lda | 121 | live | `data/snapshots/2024-env/normalized/lda-lobbying.csv` |
| fec | 600 | live | `data/snapshots/2024-env/normalized/fec-campaign-finance.csv` |
| regulatory | 200 | live | `data/snapshots/2024-env/normalized/regulatory-dockets.csv` |
| usaspending | 200 | live | `data/snapshots/2024-env/normalized/usaspending-awards.csv` |
| revolving-door | 5 | fixture | `data/snapshots/2024-env/normalized/revolving-door.csv` |

`live-run-status.csv` records which official live requests completed and which were blocked by public API limits or missing credentials.
