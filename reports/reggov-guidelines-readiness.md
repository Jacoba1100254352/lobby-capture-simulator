# Regulation & Governance Guideline Readiness

This audit checks the locally verifiable Regulation & Governance and Wiley submission requirements for the generated manuscript bundle. It intentionally does not replace the final live journal author-page check.

## Summary

- Automated guideline status: `ready`
- Ready gates: `12`
- Manual-required gates: `0`
- Blocked gates: `0`
- Preferred word range checked: `preferred 8,000-10,000; normal upper limit 11,000` words including abstract, references, endnotes, tables, and figures
- Research Forum word limit noted: `6000` words
- Abstract limit checked: `150` words
- Manuscript declarations checked: Data and Code Availability; AI Use Disclosure; funding; conflict of interest
- Supporting-information checks include Wiley's clear-labeling and 10 MB per-file guidance

## Source Notes

- Official Regulation & Governance author page: https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html
- Wiley submission help: https://authors.wiley.com/help/submitting-your-manuscript.html
- Wiley LaTeX template guidance: https://authors.wiley.com/author-resources/Journal-Authors/Prepare/latex-template.html
- Wiley AI guidelines: https://www.wiley.com/en-us/publish/article/ai-guidelines/
- Wiley supporting-information guidance: https://authors.wiley.com/author-resources/Journal-Authors/Prepare/manuscript-preparation-guidelines.html/supporting-information.html

The live Regulation & Governance author page records free-format first submission, double-anonymized review, at least three suggested reviewers, expected data sharing, LaTeX/PDF/source upload rules, and separate figure/supporting-information expectations. It should still be opened immediately before final submission because journal-specific instructions can change.

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| journal-target-and-article-type | ready | local title=yes; Wiley title=yes; journal metadata=yes; article type=yes; target comment=yes | Keep the Wiley wrapper targeted to Regulation & Governance as an original article. |
| word-limit | ready | approximate words=8502; preferred range=8000-10000; within preferred=yes; normal upper limit=11000; Research Forum limit=6000 | Keep the manuscript in the preferred range when feasible and below the normal upper limit. |
| abstract-and-keywords | ready | local abstract=yes; local keywords=yes; Wiley abstract=yes; Wiley keywords=yes; abstract words <= 150=yes; abstract words=99 | Retain extractable abstract and keyword metadata in both local and Wiley wrappers. |
| title-page-metadata | ready | local author=yes; local affiliation=yes; local country=yes; local email=yes; Wiley author=yes; Wiley address=yes; Wiley correspondence=yes | Keep author name, affiliation, country, correspondence, and email metadata present. |
| double-anonymized-review-package | ready | zip exists=yes; ready gates=8/8; blocked/missing gates=none | Keep the separate blinded review ZIP compiled, redacted, and paired with a separate title page. |
| data-code-availability | ready | statement=yes; repository=yes; release tag=yes; license=yes; credential/raw exclusion=yes; snapshot path=yes | Maintain repository, release, license, private-credential, and source-snapshot details. |
| ai-funding-conflict-disclosures | ready | AI disclosure=yes; human responsibility=yes; AI no fabrication=yes; funding statement=yes; Wiley funding metadata=yes; conflict statement=yes | Keep AI use, human responsibility, funding, and conflict statements in the manuscript. |
| figures-and-tables | ready | PDF figures=6; SVG sources=6; figure wrappers=6; table files=19; ZIP PDF figures=6; ZIP table files=19 | Retain generated PDF graphics, reproducible SVG sources, LaTeX wrappers, and table files. |
| supporting-information | ready | supplement.tex=yes; supplement.pdf=yes; supporting-information/ODD-model.md=yes; supporting-information/scenario-catalog.md=yes; supporting-information/validation-plan.md=yes; supporting-information/source-data-roadmap.md=yes; supporting-information/submission-readiness.md=yes; supporting-information/final-human-readthrough.md=yes; supporting-information/final-human-readthrough-audit.md=yes; supporting-information/final-readthrough-evidence.md=yes; report-data files=89 | Keep supplement files, ODD model, scenario catalog, validation plan, source roadmap, and report data in the package. |
| supporting-information-format-size | ready | supporting members=171; largest=within-limit; limit=10485760; oversized=none; unlabeled=none | Keep every supporting-information member clearly labeled and at or below Wiley's 10 MB per-file guidance. |
| latex-submission-files | ready | exists=yes; readable=yes; encrypted=no; members=228; strategic-channel-substitution-regulatory-capture.tex=yes; strategic-channel-substitution-regulatory-capture.pdf=yes; references.bib=yes; USG.cls=yes; lettersp.sty=yes; wileyNJD-Chicago.bst=yes; supporting-information/submission-package-manifest.json=yes; supporting-information/submission-package-manifest.md=yes; Wiley form ready gates=7 | Keep the ZIP, root .tex, compiled PDF, bibliography, class/style files, figures, tables, and package manifest together. |
| live-reggov-author-page-refresh | ready | official URL recorded=https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html; record URL=matches; checked-by=present; checked-date=2026-06-19; release-date=2026-06-19; stale=no; reviewed-release=paper-publication-readiness-2026-06-19-r204; expected-release=paper-publication-readiness-2026-06-19-r204; superseding-instructions=none | Keep the recorded live author-page check with the final signoff. |

## Interpretation

A `ready` guideline status means the repository satisfies the checked Regulation & Governance/Wiley format surface for this release, including the recorded live author-page refresh. It does not mean the journal submission is complete: DOI archiving and human final read-through remain separate final-submission controls, and the live author page should still be checked again immediately before submission.
