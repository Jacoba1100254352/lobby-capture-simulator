# Paper

Build the draft with:

```sh
make paper
```

The paper is a submission-oriented draft under active validation. It should stay tied to reproducible report snapshots under `reports/` and should distinguish simulation calibration from causal empirical claims.

The primary submission target is **Regulation & Governance**. The local article entrypoint is `paper/main.tex`; the Wiley-template entrypoint is `paper/regulation-governance-wiley.tex`.

Useful paper commands:

```sh
make paper
make paper-word-count
make wiley-template
make wiley-tex-deps
make paper-wiley
make submission-package
make paper-artifacts
make paper-artifacts-check
```

`make paper` is the default reproducible build. `make wiley-template` downloads Wiley's official `WileyDesign.zip` bundle into ignored `paper/.wiley-template/`; `make wiley-tex-deps` installs the extra Wiley-template packages into the user TeX tree through `tlmgr --usermode`; `make paper-wiley` uses the Regulation & Governance/Wiley wrapper and ignored `paper/.wiley-build/` scratch files for template-local BibTeX compatibility. The Wiley build patches only the generated `.wiley-build/USG.cls` copy so the peer-review PDF does not render the generic template's sample journal artwork, Open Access badge, or placeholder DOI/footer. `make submission-package` writes a clean Wiley-oriented archive under `dist/`.

Use `make paper-artifacts` after manuscript, report, table, figure, or bibliography edits. It refreshes the report snapshots, validation outputs, generated tables, generated figures, local PDF, Wiley PDF, word count, and submission zip in one pass. Use `make paper-artifacts-check` before committing; it performs the same refresh and fails if tracked generated reports, tables, or figures are stale. The root PDFs and submission zip are ignored build artifacts, but this check guarantees they are regenerated locally and in CI whenever their inputs change.

Paper table selection is defined in `paper/tables.yml`; generated files in `paper/tables/` include a one-line provenance comment with the source report snapshot and config path. The current table set includes campaign, sensitivity, ablation, and interaction snapshots. `make figures` regenerates the channel-mix, evasion-sensitivity, scenario-tradeoff, and interaction-tradeoff SVG sources, Wiley-preferred PDF graphics, and LaTeX wrappers under `paper/figures/`. Inkscape must be available on `PATH` for SVG-to-PDF conversion.

The manuscript now carries the submission statements Wiley commonly expects for this kind of article: data/code availability, financial disclosure, conflicts of interest, and AI-use disclosure. The data/code statement names the GitHub repository, MIT License, source-snapshot limits, and submission-package command. Corresponding-author contact is taken from the local git configuration.

Report snapshots have adjacent `*.manifest.json` files, `make source-moments` writes direct source diagnostics, and `make validate` plus `make calibration-queue` write validation summaries and classified follow-up queues under `reports/`.
The draft follows the stage-and-channel framing in `docs/research/research-synthesis.md`, with `data/calibration/parameter-map.csv` acting as the parameter appendix scaffold.

Submission strategy details live in `docs/submission-strategy.md`.
