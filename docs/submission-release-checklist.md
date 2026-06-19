# Submission Release Checklist

Use this before creating a journal submission archive or public release tag.

## Required State

- `git status --short` is clean before the final artifact build starts.
- `make paper-artifacts-check` passes.
- `git diff --exit-code` is clean after the artifact build.
- `reports/paper-layout-audit.md` reports `Failures: 0`, and `reports/manual-visual-audit.md` shows no `needs review` entries. `make paper-artifacts-check` enforces both conditions; a human final visual inspection is still recommended before submission.
- `reports/source-panel-inventory.md` has no unacknowledged source gap that contradicts the manuscript framing.
- `reports/validation-summary.md` and `reports/calibration-queue.md` are consistent with the manuscript's claim strength.
- `reports/reviewer-risk-register.md` reports `bounded_for_mechanism_review` and contains no empty evidence, claim-boundary, or next-action fields. Its bounded and open-calibration rows should match the claim-source dependency and causal-calibration target reports.
- `reports/final-human-readthrough.md` remains `pending` for review-bundle circulation and must be completed by a human reviewer for the exact current release tag before final journal submission. `reports/final-human-readthrough-audit.md` should show no `blocked` rows; unchecked scholarly items may remain `manual_required` until final submission signoff.
- `reports/wiley-submission-form-readiness.md` reports mechanical upload status `ready`; the journal-specific author-guidelines row may remain `manual_required` until the final live submission check.
- `reports/blinded-review-package-readiness.md` reports the double-anonymized package status `ready`: anonymous main manuscript and supplement, separate title page, redacted review-facing source/PDF text, synchronized manifest, and standalone extraction compile.
- `reports/reggov-guidelines-readiness.md` reports whether the Regulation & Governance/Wiley guideline surface is ready for the current release. If the live author-page refresh is not recorded, or if the recorded checked date predates the current `CITATION.cff` release date, it remains `ready_with_manual_live_check`; if it is recorded for the current release with no superseding instructions, the guideline status may be `ready`. Final submission still cannot clear until DOI archiving and human scholarly read-through signoff are complete.

## Archive Metadata

- Create a release tag for the exact commit used by the submission package.
- Create a GitHub release for the tag and attach the blinded review ZIP, Wiley submission ZIP, Wiley PDF, local manuscript PDF, supplement PDF, DOI package, and release/readiness aids printed by `make github-release-upload-paths`.
- Confirm `CITATION.cff`, `.zenodo.json`, `scripts/check-paper-artifacts.py`, and `paper/sections/submission-declarations.tex` all name the same release tag.
- If a Zenodo, OSF, or institutional archive DOI is created, record it in `paper/sections/submission-declarations.tex`; otherwise, the data availability statement should cite the GitHub release URL without saying that the archive is unfinished.
- Immediately before final submission, open the live Regulation & Governance author page and record the checker, date, URL, and superseding-instruction status in `reports/final-human-readthrough.md`; the recorded checked date must be on or after the current release date.
- Confirm the release archive includes normalized snapshots, report CSVs, generated tables, generated figure sources, generated PDF figures, the manuscript PDF, supplement PDF, the Wiley submission archive, and the blinded review archive.
- Confirm the Wiley submission archive includes `supporting-information/CITATION.cff` and `supporting-information/zenodo.json`.
- Confirm the Wiley submission archive includes `supporting-information/submission-package-manifest.json` and `.md`; `make paper-artifacts-check` must validate those checksums against the ZIP members.
- Confirm the Wiley submission archive includes `supporting-information/final-human-readthrough.md`, `supporting-information/final-human-readthrough-audit.md`, and `supporting-information/final-readthrough-evidence.md`; these files record final human editorial signoff, the structured audit that prevents a stale or incomplete signoff from clearing, and the automated evidence mapped to each scholarly read-through item.
- Confirm the Wiley submission archive includes `supporting-information/reviewer-risk-register.md`; it records likely reviewer objections, current responses, evidence boundaries, and unresolved actions.
- Confirm the Wiley submission archive includes `supporting-information/report-data/` with the generated CSV, Markdown, and manifest report files. `make paper-artifacts-check` byte-compares those package copies against the working tree.
- Confirm `reports/archive-handoff-manifest.{csv,json,md}` was regenerated after the submission ZIP was built; it records the DOI-deposit asset set and stable metadata checksums. Attach ignored `dist/release-asset-checksums.{csv,json,md}` to the GitHub release, or retain it with the DOI deposit record, for local release-machine PDF/ZIP checksums. Neither handoff file family is copied into the Wiley ZIP.
- After uploading the GitHub release assets and waiting for CI, run `make release-postflight`. This networked post-release handoff writes ignored GitHub asset and CI audit reports, then refreshes `reports/external-finalization-checklist.{csv,md}` so the local DOI/journal/procurement-source handoff state matches the current release tag.
- Confirm `dist/lobby-capture-doi-deposit-package.zip`, `dist/doi-deposit-package-manifest.{json,md}`, and `dist/doi-deposit-package-checksum.{csv,json,md}` were regenerated after the archive handoff, Wiley form readiness, and Regulation & Governance guideline readiness reports. This package is a single-upload DOI handoff artifact; `reports/doi-deposit-readiness.md` remains outside it and verifies it after construction.
- Confirm `reports/zenodo-deposit-preflight.{csv,md}` and ignored `dist/zenodo-deposit-metadata.json` were regenerated after the DOI package. If using Zenodo directly, set `ZENODO_ACCESS_TOKEN` in `.env`, run `make zenodo-deposit-draft` to create or update an unpublished draft, then run `make zenodo-deposit-upload` only after checking that the draft metadata is correct. These targets do not publish the Zenodo record.
- After an archive DOI is reserved or minted, set `ARCHIVE_DOI` in `.env` and run `make record-doi-archive` before rerunning `make paper-artifacts-check`. This records the DOI in the citation metadata, Zenodo metadata, manuscript declarations, and final read-through record without signing off the human read-through.
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
