# Final Human Scholarly Read-Through

status: pending
signed-off-by:
signed-off-date:
reviewed-release: paper-publication-readiness-2026-06-19-r203
reviewed-commit:
doi-archive:
venue-target: Regulation & Governance
author-guidelines-url: https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html
author-guidelines-checked-by: Codex Playwright live browser check
author-guidelines-checked-date: 2026-06-19
author-guidelines-superseding-instructions: none

## Purpose

This file is the manual final-submission signoff record for the review bundle. It is intentionally separate from automated simulator, LaTeX, layout, visual, and reproducibility gates. The generated `reports/submission-readiness.md` audit can clear the `final-journal-submission` gate only after a DOI archive is recorded in the paper metadata, this file is completed for the current release tag, and the live Regulation & Governance author-page refresh is recorded here.

## Completion Rule

Leave `status` as `pending` until a human scholarly read-through has checked the exact release named in `reviewed-release`. To clear the human-read-through portion of the final-submission gate, update `status`, `signed-off-by`, `signed-off-date`, `reviewed-commit`, and `doi-archive` as appropriate after the final read-through. To clear the live author-page portion, record `author-guidelines-checked-by`, `author-guidelines-checked-date`, and set `author-guidelines-superseding-instructions` to `none` only if the live page has no journal-specific instruction requiring package changes. The automated audit also requires the reviewed release to match the current `CITATION.cff` release tag and the author-guidelines checked date to be on or after the current `CITATION.cff` release date.

## Live Regulation & Governance Author-Page Refresh

- [x] Open the live author page named in `author-guidelines-url` immediately before journal submission.
- [x] Confirm the target journal, article type, word limit, title-page expectations, disclosure expectations, supporting-information expectations, and LaTeX/package requirements still match the generated bundle.
- [x] Record checker, date, and superseding-instruction status in the fields above.

## Scholarly Read-Through Checklist

Before checking these items, review `reports/final-readthrough-evidence.md`. That generated packet maps each checkbox to current automated evidence and separates mechanical support from remaining editorial, DOI, and archive actions.

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
- [ ] Zenodo deposit preflight and any unpublished draft metadata match the signed-off release before a DOI record is published.
- [ ] References are complete enough for the target venue and do not contain placeholder or "planned validation" entries.
- [ ] AI Use Disclosure and declarations match journal expectations.
- [ ] The final release ZIP, PDFs, supplement, reports, and metadata match the signed-off release tag.

## Reviewer Notes

2026-06-15 live-author-page access attempt: Codex checked `author-guidelines-url` from the release machine. The official URL was reachable at the HTTP header level, but the fetched HTML body was a Cloudflare "Just a moment..." challenge and did not expose the journal-specific author-guideline text.

2026-06-18 live-author-page browser check carried forward for the r187 update: Codex used Playwright to load the official Regulation & Governance author page in a browser context. The page title was `Regulation & Governance` and the page exposed the journal-specific author guidelines, marked `Author Guidelines updated April 2025`. The check confirmed free-format first submission, double-anonymized review, at least three suggested reviewers, normal article submissions not normally accepted above 11,000 words, Research Forum limit of 6,000 words, preferred first-submission length of 8,000-10,000 words, abstract limit of 150 words, data sharing expected, LaTeX accepted with a peer-review PDF and source/supporting files, separate title-page/main-text/figure expectations, and separate supporting-information expectations. No superseding instruction was found that requires changing the generated review bundle. DOI archiving and human scholarly read-through signoff remain pending.

2026-06-19 r198-prep live-author-page refresh attempt: Codex opened the official `author-guidelines-url` with Playwright from the release machine. Wiley served a Cloudflare "Performing security verification" page titled `Just a moment...` and did not expose the journal-specific author-guideline text after an additional wait. The June 18 content check is therefore retained as historical evidence only; the generated audits now require the checked date to be on or after the current release date before the live author-page refresh gate can clear.

2026-06-19 live-author-page browser refresh: Codex opened the official `author-guidelines-url` with Playwright from the release machine. Wiley initially served a security-verification interstitial, then the browser session resolved to the `Regulation & Governance` author-guidelines page. The page exposed the journal-specific author-guideline contents and the `Author Guidelines updated April 2025` marker. The refresh confirmed the same relevant submission surface recorded on June 18: free-format first submission, double-anonymized review, suggested-reviewer expectations, original-article word-limit expectations, Research Forum limit, abstract limit, data-sharing expectations, title-page/main-text/figure file expectations, supporting-information expectations, and LaTeX/source-package compatibility. No superseding instruction was found that requires changing the generated review bundle. DOI archiving and human scholarly read-through signoff remain pending.

Record any final editorial changes requested before journal submission here. If changes are made after signoff, return `status` to `pending`, update `reviewed-release`, rerun `make paper-artifacts-check`, and repeat the read-through.
