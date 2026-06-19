# Blinded Review Package Readiness

This audit checks the double-anonymized Regulation & Governance review package. The title page is allowed to contain author and correspondence information; the main manuscript, supplement, and inspectable review-facing sources are not.

## Summary

- Ready gates: `8`
- Blocked gates: `0`

## Gates

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| package-present | ready | exists=yes; readable=yes; encrypted=no; members=67 | Build the blinded review package before journal review upload. |
| expected-files | ready | missing=none | Keep anonymous main manuscript, supplement, title page, references, classes, figures, tables, and selected supporting information together. |
| upload-surface | ready | bytes=1693255; limit=524288000; unsupported members=none | Keep the blinded review ZIP within Wiley's upload size limit and free of unsupported executable/script formats. |
| source-redaction | ready | identifiers in review-facing source=none | Review-facing source files must not expose author, email, public repository, or release-tag identifiers. |
| rendered-redaction | ready | identifiers in review-facing PDFs=none | Review-facing PDFs must not expose author, email, public repository, or release-tag identifiers. |
| separate-title-page | ready | title-page files=yes; missing title-page metadata=none | Keep author and correspondence information only in separate title-page files. |
| manifest | ready | manifest failures=none | Keep the blinded package member manifest synchronized with ZIP bytes. |
| standalone-compile | ready | ready | The extracted blinded ZIP must compile its anonymous main manuscript, supplement, and title page. |
