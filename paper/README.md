# Paper

Build the draft with:

```sh
make paper
```

The paper is intentionally a working draft. It should stay tied to reproducible report snapshots under `reports/` and should distinguish simulation calibration from causal empirical claims.

Paper table selection is defined in `paper/tables.yml`; generated files in `paper/tables/` include a one-line provenance comment with the source report snapshot and config path. The current table set includes campaign, sensitivity, ablation, and interaction snapshots. `make figures` also regenerates the interaction tradeoff figure under `paper/figures/`.

Report snapshots have adjacent `*.manifest.json` files, `make source-moments` writes direct source diagnostics, and `make validate` plus `make calibration-queue` write validation summaries and classified follow-up queues under `reports/`.
The draft follows the stage-and-channel framing in `docs/research/research-synthesis.md`, with `data/calibration/parameter-map.csv` acting as the parameter appendix scaffold.
