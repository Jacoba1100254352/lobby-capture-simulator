# Regulation & Governance Guideline Readiness

This audit checks the locally verifiable Regulation & Governance and Wiley submission requirements for the generated manuscript bundle. It intentionally does not replace the final live journal author-page check.

## Summary

- Automated guideline status: `ready_with_manual_live_check`
- Ready gates: `9`
- Manual-required gates: `1`
- Blocked gates: `0`
- Preferred word range checked: `8,000-10,000` words including abstract, references, endnotes, tables, and figures
- Manuscript declarations checked: Data and Code Availability; AI Use Disclosure; funding; conflict of interest

## Source Notes

- Official Regulation & Governance author page: https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html
- Wiley submission help: https://authors.wiley.com/help/submitting-your-manuscript.html
- Wiley LaTeX template guidance: https://authors.wiley.com/author-resources/Journal-Authors/Prepare/latex-template.html
- Wiley AI guidelines: https://www.wiley.com/en-us/publish/article/ai-guidelines/
- Wiley supporting-information guidance: https://authors.wiley.com/author-resources/Journal-Authors/Prepare/manuscript-preparation-guidelines.html/supporting-information.html

The live Regulation & Governance author page should be opened immediately before final submission because journal-specific instructions can supersede generic Wiley guidance.

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| journal-target-and-article-type | ready | local title=yes; Wiley title=yes; journal metadata=yes; article type=yes; target comment=yes | Keep the Wiley wrapper targeted to Regulation & Governance as an original article. |
| word-limit | ready | approximate words=8074; Regulation & Governance reported preferred range=8000-10000 | Revise the manuscript if the approximate count falls outside the reported preferred range. |
| abstract-and-keywords | ready | local abstract=yes; local keywords=yes; Wiley abstract=yes; Wiley keywords=yes | Retain extractable abstract and keyword metadata in both local and Wiley wrappers. |
| title-page-metadata | ready | local author=yes; local affiliation=yes; local country=yes; local email=yes; Wiley author=yes; Wiley address=yes; Wiley correspondence=yes | Keep author name, affiliation, country, correspondence, and email metadata present. |
| data-code-availability | ready | statement=yes; repository=yes; release tag=yes; license=yes; credential/raw exclusion=yes; snapshot path=yes | Maintain repository, release, license, private-credential, and source-snapshot details. |
| ai-funding-conflict-disclosures | ready | AI disclosure=yes; human responsibility=yes; AI no fabrication=yes; funding statement=yes; Wiley funding metadata=yes; conflict statement=yes | Keep AI use, human responsibility, funding, and conflict statements in the manuscript. |
| figures-and-tables | ready | PDF figures=6; SVG sources=6; figure wrappers=6; table files=17; ZIP PDF figures=6; ZIP table files=17 | Retain generated PDF graphics, reproducible SVG sources, LaTeX wrappers, and table files. |
| supporting-information | ready | supplement.tex=yes; supplement.pdf=yes; supporting-information/ODD-model.md=yes; supporting-information/scenario-catalog.md=yes; supporting-information/validation-plan.md=yes; supporting-information/source-data-roadmap.md=yes; supporting-information/submission-readiness.md=yes; supporting-information/final-human-readthrough.md=yes; report-data files=69 | Keep supplement files, ODD model, scenario catalog, validation plan, source roadmap, and report data in the package. |
| latex-submission-files | ready | exists=yes; readable=yes; encrypted=no; members=181; strategic-channel-substitution-regulatory-capture.tex=yes; strategic-channel-substitution-regulatory-capture.pdf=yes; references.bib=yes; USG.cls=yes; lettersp.sty=yes; wileyNJD-Chicago.bst=yes; supporting-information/submission-package-manifest.json=yes; supporting-information/submission-package-manifest.md=yes; Wiley form ready gates=7 | Keep the ZIP, root .tex, compiled PDF, bibliography, class/style files, figures, tables, and package manifest together. |
| live-reggov-author-page-refresh | manual_required | official URL recorded=https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html; record URL=matches; checked-by=present; checked-date=present; reviewed-release=paper-publication-readiness-2026-06-15-r127; expected-release=paper-publication-readiness-2026-06-15-r127; superseding-instructions=not-cleared: not cleared - HTTP HEAD returned 200 for the official author page, but the fetched body returned a Cloudflare JavaScript challenge rather than author-guideline content; human br... | Complete the live journal author-page browser review and replace the recorded non-clearance reason with none only if no superseding instructions require package changes. |

## Interpretation

A `ready_with_manual_live_check` status means the repository satisfies the checks that can be made from committed files and the generated Wiley package. It does not mean the journal submission is complete: DOI archiving, human final read-through, and live Regulation & Governance author-page refresh remain separate final-submission controls.
