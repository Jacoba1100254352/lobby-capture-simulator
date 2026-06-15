# Zenodo Deposit Preflight

This report prepares the Zenodo DOI deposit payload for the release. It is an offline preflight by default and does not assert that a DOI has been minted.

## Summary

- Title: `Lobby Capture Simulator: Strategic Channel Substitution in Regulatory Capture`
- Version: `paper-publication-readiness-2026-06-15-r120`
- Metadata file: `dist/zenodo-deposit-metadata.json`
- Zenodo API target: `https://sandbox.zenodo.org/api`
- Official API documentation: https://developers.zenodo.org/
- Ready gates: `5`
- Manual-required gates: `3`
- Blocked gates: `0`

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| metadata-json | ready | title=present; creators=1; version=paper-publication-readiness-2026-06-15-r120; expected=paper-publication-readiness-2026-06-15-r120; license=mit-license | Keep .zenodo.json and CITATION.cff synchronized before DOI deposit. |
| api-target | ready | apiBase=https://sandbox.zenodo.org/api; docs=https://developers.zenodo.org/ | Use sandbox for rehearsal; switch to https://zenodo.org/api only for the final DOI draft. |
| token | manual_required | ZENODO_ACCESS_TOKEN=missing | Set ZENODO_ACCESS_TOKEN in .env only when creating an unpublished draft deposit. |
| doi-package | ready | package=present; bytes=3430366; checksum=ok | Run make doi-deposit-package before a Zenodo upload. |
| archive-manifest | ready | releaseTag=paper-publication-readiness-2026-06-15-r120; expected=paper-publication-readiness-2026-06-15-r120 | Regenerate the archive handoff manifest before a DOI upload. |
| claim-boundary | ready | overall=ready_for_mechanism_review; policy-language=ready | Keep the Zenodo description bounded to mechanism-model review until calibrated policy gates clear. |
| doi-record | manual_required | DOI=not recorded yet | After Zenodo reserves or mints a DOI, record it in CITATION.cff, .zenodo.json, the paper declarations, and final-human-readthrough.md. |
| human-readthrough | manual_required | final-human-readthrough status=pending | Do not publish the Zenodo record as the final journal submission archive until the human read-through is signed off. |

## Networked Draft Workflow

The safe default target only writes local metadata and this preflight report. To create an unpublished Zenodo draft, set `ZENODO_ACCESS_TOKEN` in `.env` and run `make zenodo-deposit-draft`. To upload the DOI deposit package to that unpublished draft, run `make zenodo-deposit-upload`. This workflow does not publish the Zenodo record.
