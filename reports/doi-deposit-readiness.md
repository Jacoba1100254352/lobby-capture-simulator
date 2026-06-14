# DOI Deposit Readiness

This audit checks whether the release has the metadata, asset list, checksum handoff, and claim-boundary records needed for DOI deposition. It does not assert that a DOI has been minted.

## Summary

- Release tag: `paper-publication-readiness-2026-06-14-r109`
- Ready gates: `4`
- Manual-required gates: `3`
- Blocked gates: `0`
- Final journal-submission status: `manual_required`

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| release-metadata | ready | CITATION release=paper-publication-readiness-2026-06-14-r109; Zenodo related release=present | Use these metadata as the deposit record source. |
| primary-release-assets | ready | manifest assets=4; expected assets=4 | Deposit the primary assets listed in the archive handoff manifest. |
| release-asset-checksums | ready | checksum files=present; checksum asset rows=4 | Attach or retain dist/release-asset-checksums.* with the DOI record. |
| claim-boundary | ready | overall submission posture=ready_for_mechanism_review | Keep the DOI record description bounded to mechanism-model review unless policy-calibration gates later clear. |
| doi-record | manual_required | DOI=not recorded in citation, deposit metadata, or declarations | After minting a Zenodo, OSF, or journal-linked archive DOI, record it in CITATION.cff, .zenodo.json, submission declarations, and the final read-through record. |
| human-readthrough | manual_required | status=pending; reviewed-release=paper-publication-readiness-2026-06-14-r109; expected-release=paper-publication-readiness-2026-06-14-r109; signer=missing; date=missing; commit=missing | Complete the final human scholarly read-through against the exact release tag before final journal submission. |
| final-journal-submission | manual_required | submission final gate=manual_required; doi=missing; human signoff=pending | Do not treat the bundle as final-journal-submission ready until DOI and human signoff are both recorded. |

## Deposit Asset Set

Upload or preserve these primary release assets with the DOI record, using `dist/release-asset-checksums.{csv,json,md}` for byte-level verification:

- `lobby-capture-wiley-submission.zip`
- `regulation-governance-wiley.pdf`
- `strategic-channel-substitution-regulatory-capture.pdf`
- `supplement.pdf`

The tagged source archive should also preserve `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record remains tied to the release claim boundary.
