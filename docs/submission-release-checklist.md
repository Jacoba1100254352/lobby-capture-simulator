# Submission Release Checklist

Use this before creating a journal submission archive or public release tag.

## Required State

- `git status --short` is clean before the final artifact build starts.
- `make paper-artifacts-check` passes.
- `git diff --exit-code` is clean after the artifact build.
- `reports/paper-layout-audit.md` reports `Failures: 0`, and `reports/manual-visual-audit.md` shows no `needs review` entries. `make paper-artifacts-check` enforces both conditions; a human final visual inspection is still recommended before submission.
- `reports/source-panel-inventory.md` has no unacknowledged source gap that contradicts the manuscript framing.
- `reports/validation-summary.md` and `reports/calibration-queue.md` are consistent with the manuscript's claim strength.
- `reports/final-human-readthrough.md` remains `pending` for review-bundle circulation and must be completed by a human reviewer for the exact current release tag before final journal submission.
- `reports/wiley-submission-form-readiness.md` reports mechanical upload status `ready`; the journal-specific author-guidelines row may remain `manual_required` until the final live submission check.
- `reports/reggov-guidelines-readiness.md` reports automated guideline status `ready_with_manual_live_check`; the live Regulation & Governance author-page refresh may remain `manual_required` until final submission.

## Archive Metadata

- Create a release tag for the exact commit used by the submission package.
- Create a GitHub release for the tag and attach the Wiley submission ZIP, Wiley PDF, and supplement PDF.
- Confirm `CITATION.cff`, `.zenodo.json`, `scripts/check-paper-artifacts.py`, and `paper/sections/submission-declarations.tex` all name the same release tag.
- If a Zenodo, OSF, or institutional archive DOI is created, record it in `paper/sections/submission-declarations.tex`; otherwise, the data availability statement should cite the GitHub release URL without saying that the archive is unfinished.
- Confirm the release archive includes normalized snapshots, report CSVs, generated tables, generated figure sources, generated PDF figures, the manuscript PDF, supplement PDF, and the Wiley submission archive.
- Confirm the Wiley submission archive includes `supporting-information/CITATION.cff` and `supporting-information/zenodo.json`.
- Confirm the Wiley submission archive includes `supporting-information/submission-package-manifest.json` and `.md`; `make paper-artifacts-check` must validate those checksums against the ZIP members.
- Confirm the Wiley submission archive includes `supporting-information/final-human-readthrough.md`; this file records final human editorial signoff and must not be marked complete for an older release tag.
- Confirm the Wiley submission archive includes `supporting-information/report-data/` with the generated CSV, Markdown, and manifest report files. `make paper-artifacts-check` byte-compares those package copies against the working tree.
- Confirm `reports/archive-handoff-manifest.{csv,json,md}` was regenerated after the submission ZIP was built; it records the DOI-deposit asset set and stable metadata checksums. Attach ignored `dist/release-asset-checksums.{csv,json,md}` to the GitHub release, or retain it with the DOI deposit record, for local release-machine PDF/ZIP checksums. Neither handoff file family is copied into the Wiley ZIP.
- Confirm `dist/lobby-capture-doi-deposit-package.zip`, `dist/doi-deposit-package-manifest.{json,md}`, and `dist/doi-deposit-package-checksum.{csv,json,md}` were regenerated after the archive handoff, Wiley form readiness, and Regulation & Governance guideline readiness reports. This package is a single-upload DOI handoff artifact; `reports/doi-deposit-readiness.md` remains outside it and verifies it after construction.
- Confirm the Wiley submission archive includes generated PDF graphics, SVG figure sources, and LaTeX figure wrappers under `figures/`.
- Confirm `reports/wiley-submission-form-readiness.{csv,md}` was regenerated after the final Wiley ZIP was built. This post-package report is intentionally not copied into the Wiley ZIP.
- Confirm `reports/reggov-guidelines-readiness.{csv,md}` was regenerated after the final Wiley upload-form audit. This post-package report is intentionally not copied into the Wiley ZIP.
- Do not archive private credentials or raw API payloads that cannot be redistributed.
- `make paper-artifacts-check` should fail if the submission declarations contain self-invalidating archive language such as `No external DOI` or `should be minted`.

## Source-Panel Guardrails

- Direct dark-money rows must remain separate from super PAC, Schedule E, electioneering, and communication-cost rows.
- Public-financing rows must remain separate from ordinary campaign receipts unless the manuscript explicitly reports an all-campaign denominator.
- Procurement reports must separate initial awards from post-award modifications.
- Fixture-only rows can support schema and mechanism tests, but cannot be described as representative empirical calibration.
