# Wiley Submission Form Readiness

This audit checks Wiley Research Exchange upload mechanics for the generated LaTeX submission bundle. It does not replace a live journal-specific author-guidelines check.

## Summary

- Mechanical upload status: `ready`
- Ready gates: `7`
- Manual-required gates: `1`
- Blocked gates: `0`

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| submission-archive-present | ready | exists=yes; readable=yes; encrypted=no; members=163 | Upload the ZIP only if it opens without encryption or structural errors. |
| upload-size | ready | combined upload bytes=3008600; limit=524288000 | Keep the LaTeX ZIP, compiled PDF, and supplement below Wiley's 500 MB combined-file limit. |
| filename-length | ready | long upload names=0; long ZIP member names=0; limit=256 | Rename files before upload if any upload file or ZIP member exceeds Wiley's file-name limit. |
| root-latex-and-pdf | ready | missing root files=none | Keep the main .tex file and compiled peer-review PDF at the ZIP root. |
| supporting-files | ready | missing support files=none; missing directories=none | Retain bibliography, class/style files, figures, tables, declarations, and supporting-information manifests. |
| unsupported-upload-formats | ready | unsupported upload files=none; unsupported ZIP members=none | Remove executable or script-format files before upload. |
| data-and-ai-statements | ready | data availability=yes; license=yes; private/raw exclusion=yes; AI disclosure=yes; AI no data fabrication=yes; funding=yes; conflicts=yes | Keep data/code availability, excluded-credentials language, AI use disclosure, funding, and conflict statements in the manuscript. |
| journal-specific-author-guidelines | manual_required | strategy reminder=yes; DOI checklist reminder=yes; manual journal-specific author-guidelines refresh required | Before live submission, re-check the Regulation & Governance author page because Wiley says journal-specific instructions override generic Wiley guidance. |

## Upload Notes

Wiley guidance says LaTeX submissions may use a ZIP archive containing the root `.tex`, compiled PDF, bibliography, classes/packages, figures, tables, and supporting files. It also asks authors to provide a single compiled PDF for peer review and to avoid unsupported executable or script upload formats.

The journal-specific author-guidelines gate remains manual because Regulation & Governance instructions may override generic Wiley guidance at live submission time.
