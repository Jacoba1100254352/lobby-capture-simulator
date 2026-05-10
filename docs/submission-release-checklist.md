# Submission Release Checklist

Use this before creating a journal submission archive or public release tag.

## Required State

- `git status --short` is clean before the final artifact build starts.
- `make paper-artifacts-check` passes.
- `git diff --exit-code` is clean after the artifact build.
- `reports/manual-visual-audit.md` has been reviewed and updated from `pending` to a real human-review status for every figure and table.
- `reports/source-panel-inventory.md` has no unacknowledged source gap that contradicts the manuscript framing.
- `reports/validation-summary.md` and `reports/calibration-queue.md` are consistent with the manuscript's claim strength.

## Archive Metadata

- Create a release tag for the exact commit used by the submission package.
- Create a Zenodo, OSF, or institutional archive for the release and record the DOI in `paper/sections/submission-declarations.tex`.
- Confirm the release archive includes normalized snapshots, report CSVs, generated tables, generated figure sources, generated PDF figures, the manuscript PDF, supplement PDF, and the Wiley submission archive.
- Do not archive private credentials or raw API payloads that cannot be redistributed.

## Source-Panel Guardrails

- Direct dark-money rows must remain separate from super PAC and Schedule E rows.
- Public-financing rows must remain separate from ordinary campaign receipts unless the manuscript explicitly reports an all-campaign denominator.
- Procurement reports must separate initial awards from post-award modifications.
- Fixture-only rows can support schema and mechanism tests, but cannot be described as representative empirical calibration.

