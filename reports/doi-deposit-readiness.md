# DOI Deposit Readiness

This audit checks whether the release has the metadata, asset list, checksum handoff, and claim-boundary records needed for DOI deposition. It does not assert that a DOI has been minted.

## Summary

- Release tag: `paper-publication-readiness-2026-06-14-r113`
- Ready gates: `5`
- Manual-required gates: `3`
- Blocked gates: `0`
- Final journal-submission status: `manual_required`

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| release-metadata | ready | CITATION release=paper-publication-readiness-2026-06-14-r113; Zenodo related release=present | Use these metadata as the deposit record source. |
| primary-release-assets | ready | manifest assets=4; expected assets=4 | Deposit the primary assets listed in the archive handoff manifest. |
| release-asset-checksums | ready | checksum files=present; checksum asset rows=4 | Attach or retain dist/release-asset-checksums.* with the DOI record. |
| doi-deposit-package | ready | package=present; manifest=present; manifest members=20; zip members=22; primary assets=4/4; zip integrity=ok; package checksum=ok | Upload or retain dist/lobby-capture-doi-deposit-package.zip as the single archive handoff package when the repository-to-archive integration does not preserve release assets directly. |
| claim-boundary | ready | overall submission posture=ready_for_mechanism_review | Keep the DOI record description bounded to mechanism-model review unless policy-calibration gates later clear. |
| doi-record | manual_required | DOI=not recorded in citation, deposit metadata, or declarations | After minting a Zenodo, OSF, or journal-linked archive DOI, record it in CITATION.cff, .zenodo.json, submission declarations, and the final read-through record. |
| human-readthrough | manual_required | status=pending; reviewed-release=paper-publication-readiness-2026-06-14-r113; expected-release=paper-publication-readiness-2026-06-14-r113; signer=missing; date=missing; commit=missing | Complete the final human scholarly read-through against the exact release tag before final journal submission. |
| final-journal-submission | manual_required | submission final gate=manual_required; doi=missing; human signoff=pending | Do not treat the bundle as final-journal-submission ready until DOI and human signoff are both recorded. |

## Deposit Asset Set

Upload or preserve these primary release assets with the DOI record, using `dist/release-asset-checksums.{csv,json,md}` for byte-level verification. If the archive workflow needs one file, use `dist/lobby-capture-doi-deposit-package.zip`, which bundles these assets with metadata and readiness reports:

- `lobby-capture-wiley-submission.zip`
- `regulation-governance-wiley.pdf`
- `strategic-channel-substitution-regulatory-capture.pdf`
- `supplement.pdf`

The tagged source archive should also preserve `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record remains tied to the release claim boundary.
