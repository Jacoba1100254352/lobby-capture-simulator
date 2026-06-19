# DOI Deposit Readiness

This audit checks whether the release has the metadata, asset list, checksum handoff, and claim-boundary records needed for DOI deposition. It does not assert that a DOI has been minted.

## Summary

- Release tag: `paper-publication-readiness-2026-06-19-r207`
- Ready gates: `6`
- Manual-required gates: `3`
- Blocked gates: `0`
- Final journal-submission status: `manual_required`

## Gate Matrix

| Gate | Status | Evidence | Next action |
| --- | --- | --- | --- |
| release-metadata | ready | CITATION release=paper-publication-readiness-2026-06-19-r207; Zenodo related release=present | Use these metadata as the deposit record source. |
| primary-release-assets | ready | manifest assets=5; expected assets=5 | Deposit the primary assets listed in the archive handoff manifest. |
| release-asset-checksums | ready | checksum files=present; checksum asset rows=5 | Attach or retain dist/release-asset-checksums.* with the DOI record. |
| doi-deposit-package | ready | package=present; manifest=present; manifest members=37; zip members=39; primary assets=5/5; zip integrity=ok; package checksum=ok | Upload or retain dist/lobby-capture-doi-deposit-package.zip as the single archive handoff package when the repository-to-archive integration does not preserve release assets directly. |
| zenodo-preflight | ready | preflight rows=8; blocked=0; manual_required=3 | Run make zenodo-deposit-preflight before creating an unpublished Zenodo draft. |
| claim-boundary | ready | overall submission posture=ready_for_mechanism_review | Keep the DOI record description bounded to mechanism-model review unless policy-calibration gates later clear. |
| doi-record | manual_required | DOI=not recorded in citation, deposit metadata, or declarations | After minting a Zenodo, OSF, or journal-linked archive DOI, record it in CITATION.cff, .zenodo.json, submission declarations, and the final read-through record. |
| human-readthrough | manual_required | release=paper-publication-readiness-2026-06-19-r207; status=pending; blocked=0; manual_required=18; checkedChecklistItems=3/17 | Complete the final human scholarly read-through against the exact release tag before final journal submission. |
| final-journal-submission | manual_required | submission final gate=manual_required; doi=missing; human signoff=pending; live author-page refresh=ready | Do not treat the bundle as final-journal-submission ready until DOI, human signoff, and live author-page refresh are all recorded. |

## Deposit Asset Set

Upload or preserve these primary release assets with the DOI record, using `dist/release-asset-checksums.{csv,json,md}` for byte-level verification. If the archive workflow needs one file, use `dist/lobby-capture-doi-deposit-package.zip`, which bundles these assets with metadata and readiness reports:

- `lobby-capture-wiley-blinded-review.zip`
- `lobby-capture-wiley-submission.zip`
- `regulation-governance-wiley.pdf`
- `strategic-channel-substitution-regulatory-capture.pdf`
- `supplement.pdf`

The tagged source archive should also preserve `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, `reports/final-human-readthrough.md`, `reports/final-human-readthrough-audit.md`, and `reports/final-readthrough-evidence.md` so the DOI record remains tied to the release claim boundary, automated read-through evidence, and final signoff state.

## Post-Release Integrity Check

After the GitHub release assets are uploaded, run `make github-release-asset-audit` and retain the ignored `reports/github-release-asset-audit.{csv,md}` output with the DOI handoff record. That networked audit compares GitHub's uploaded asset sizes and SHA-256 digests against the local release-machine checksum manifests. It verifies upload integrity only; it does not assert that a DOI has been minted or that final journal-submission gates are cleared.
