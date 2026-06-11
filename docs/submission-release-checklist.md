# Submission Release Checklist

Use this before creating a journal submission archive or public release tag.

## Required State

- `git status --short` is clean before the final artifact build starts.
- `make paper-artifacts-check` passes.
- `git diff --exit-code` is clean after the artifact build.
- `reports/paper-layout-audit.md` reports `Failures: 0`, and `reports/manual-visual-audit.md` shows no `needs review` entries. `make paper-artifacts-check` enforces both conditions; a human final visual inspection is still recommended before submission.
- `reports/source-panel-inventory.md` has no unacknowledged source gap that contradicts the manuscript framing.
- `reports/validation-summary.md` and `reports/calibration-queue.md` are consistent with the manuscript's claim strength.

## Archive Metadata

- Create a release tag for the exact commit used by the submission package.
- Create a GitHub release for the tag and attach the Wiley submission ZIP, Wiley PDF, and supplement PDF.
- Confirm `CITATION.cff`, `.zenodo.json`, `scripts/check-paper-artifacts.py`, and `paper/sections/submission-declarations.tex` all name the same release tag.
- If a Zenodo, OSF, or institutional archive DOI is created, record it in `paper/sections/submission-declarations.tex`; otherwise, the data availability statement should cite the GitHub release URL without saying that the archive is unfinished.
- Confirm the release archive includes normalized snapshots, report CSVs, generated tables, generated figure sources, generated PDF figures, the manuscript PDF, supplement PDF, and the Wiley submission archive.
- Confirm the Wiley submission archive includes `supporting-information/CITATION.cff` and `supporting-information/zenodo.json`.
- Confirm the Wiley submission archive includes generated PDF graphics, SVG figure sources, and LaTeX figure wrappers under `figures/`.
- Do not archive private credentials or raw API payloads that cannot be redistributed.
- `make paper-artifacts-check` should fail if the submission declarations contain self-invalidating archive language such as `No external DOI` or `should be minted`.

## Source-Panel Guardrails

- Direct dark-money rows must remain separate from super PAC and Schedule E rows.
- Public-financing rows must remain separate from ordinary campaign receipts unless the manuscript explicitly reports an all-campaign denominator.
- Procurement reports must separate initial awards from post-award modifications.
- Fixture-only rows can support schema and mechanism tests, but cannot be described as representative empirical calibration.
