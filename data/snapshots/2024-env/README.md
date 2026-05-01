# 2024 EPA/ENV Snapshot

This directory is the reproducible closed-window snapshot scaffold for the first paper-grade validation slice.

Scope:

- Calendar window: 2024-01-01 through 2024-12-31.
- LDA issue code: ENV.
- Agency: EPA.
- FEC cycle: 2024, with the six national party committees as the first electoral-pressure panel.

The current command freezes whatever normalized files are present under `data/raw/`. Live paper snapshots should first run the request templates in `manifest.json`, preserve raw payloads outside git when too large, normalize into the same schemas, and then rerun `make snapshot-2024-env`.

| Source | Rows | Status | Normalized file |
| --- | ---: | --- | --- |
| lda | 13 | copied | `data/snapshots/2024-env/normalized/lda-lobbying.csv` |
| fec | 100 | copied | `data/snapshots/2024-env/normalized/fec-campaign-finance.csv` |
| regulatory | 100 | copied | `data/snapshots/2024-env/normalized/regulatory-dockets.csv` |

`live-run-status.csv` records which official live requests completed and which were blocked by public API limits or missing credentials.
