# Final Human Scholarly Read-Through

status: pending
signed-off-by:
signed-off-date:
reviewed-release: paper-publication-readiness-2026-06-15-r114
reviewed-commit:
doi-archive:
venue-target: Regulation & Governance
author-guidelines-url: https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html
author-guidelines-checked-by:
author-guidelines-checked-date:
author-guidelines-superseding-instructions:

## Purpose

This file is the manual final-submission signoff record for the review bundle. It is intentionally separate from automated simulator, LaTeX, layout, visual, and reproducibility gates. The generated `reports/submission-readiness.md` audit can clear the `final-journal-submission` gate only after a DOI archive is recorded in the paper metadata, this file is completed for the current release tag, and the live Regulation & Governance author-page refresh is recorded here.

## Completion Rule

Leave `status` as `pending` until a human scholarly read-through has checked the exact release named in `reviewed-release`. To clear the human-read-through portion of the final-submission gate, update `status`, `signed-off-by`, `signed-off-date`, `reviewed-commit`, and `doi-archive` as appropriate after the final read-through. To clear the live author-page portion, record `author-guidelines-checked-by`, `author-guidelines-checked-date`, and set `author-guidelines-superseding-instructions` to `none` only if the live page has no journal-specific instruction requiring package changes. The automated audit also requires the reviewed release to match the current `CITATION.cff` release tag.

## Live Regulation & Governance Author-Page Refresh

- [ ] Open the live author page named in `author-guidelines-url` immediately before journal submission.
- [ ] Confirm the target journal, article type, word limit, title-page expectations, disclosure expectations, supporting-information expectations, and LaTeX/package requirements still match the generated bundle.
- [ ] Record checker, date, and superseding-instruction status in the fields above.

## Scholarly Read-Through Checklist

- [ ] Abstract states the mechanism-model contribution without implying calibrated policy-effect estimation.
- [ ] Introduction separates model assumptions, synthetic results, and empirical bridge scope.
- [ ] Literature positioning explains the regulatory-governance contribution relative to lobbying, capture, venue-shifting, and ABM validation work.
- [ ] Model specification is internally consistent with the ODD-style supplement and does not leave unresolved equations, parameters, or diagnostic definitions.
- [ ] Results describe synthetic mechanism behavior and do not present reform rankings as real-world policy estimates.
- [ ] Empirical bridge language is bounded to source moments, source-panel coverage, and validation-gap diagnostics.
- [ ] Tables and figures are referenced in order, readable in the Wiley PDF, and not duplicative or misleading.
- [ ] Limitations identify open source panels, causal-calibration targets, and construct-validity risks without self-rejecting submission language.
- [ ] Data and Code Availability names the exact release, repository, license, DOI archive if available, and excluded private/raw credentialed payloads.
- [ ] Archive-handoff manifest checksums match the final release assets and DOI-deposit asset set.
- [ ] References are complete enough for the target venue and do not contain placeholder or "planned validation" entries.
- [ ] AI Use Disclosure and declarations match journal expectations.
- [ ] The final release ZIP, PDFs, supplement, reports, and metadata match the signed-off release tag.

## Reviewer Notes

Record any final editorial changes requested before journal submission here. If changes are made after signoff, return `status` to `pending`, update `reviewed-release`, rerun `make paper-artifacts-check`, and repeat the read-through.
