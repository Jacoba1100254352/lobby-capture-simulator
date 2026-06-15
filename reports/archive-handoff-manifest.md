# Archive Handoff Manifest

This report records the release asset set and stable source-metadata checksums that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.

PDF and ZIP byte streams can differ across TeX and archive implementations. The release-machine checksums for those binary assets are written to `dist/release-asset-checksums.{csv,json,md}` and should be attached to the GitHub release or DOI deposit record.

## Summary

- Schema: `lobby-capture-archive-handoff-manifest-v1`
- Release tag: `paper-publication-readiness-2026-06-15-r125`
- Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/paper-publication-readiness-2026-06-15-r125
- Generated at: `2026-05-05T00:00:00Z`
- DOI status: not asserted by this manifest
- Release asset checksum file: `dist/release-asset-checksums.{csv,json,md}`
- Self-omission: archive-handoff manifest files are release aids and are not checksum rows.

## Primary Release Assets

- `lobby-capture-wiley-submission.zip`
- `regulation-governance-wiley.pdf`
- `strategic-channel-substitution-regulatory-capture.pdf`
- `supplement.pdf`

## Checksums

| Path | Release asset | Role | DOI deposit | Checksum status | Bytes | SHA-256 |
| --- | --- | --- | --- | --- | ---: | --- |
| dist/lobby-capture-wiley-submission.zip | lobby-capture-wiley-submission.zip | wiley-submission-archive | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| paper/regulation-governance-wiley.pdf | regulation-governance-wiley.pdf | wiley-rendered-manuscript | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| paper/strategic-channel-substitution-regulatory-capture.pdf | strategic-channel-substitution-regulatory-capture.pdf | local-rendered-manuscript | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| paper/supplement.pdf | supplement.pdf | supporting-information-pdf | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| CITATION.cff | - | citation-metadata | source-archive | tracked-source-verified | 1286 | `83e0693360c5e26a80a221201562f0e16039f5b9352a9bcfe2a9e5993d27a0a4` |
| .zenodo.json | - | doi-deposit-metadata | source-archive | tracked-source-verified | 1490 | `f6fd5f3cb7cbb568744b93c213af73f6bfa63d26611dbff096f196d06d21b04e` |
| reports/submission-readiness.md | - | submission-readiness-audit | source-archive | tracked-source-verified | 5183 | `ac852783731854f733963924319393db1d9c477e1b9a2968d23e91b485e5b77f` |
| reports/final-human-readthrough.md | - | manual-signoff-record | source-archive | tracked-source-verified | 4767 | `c720c63d35bdf1ef3ab143593665713e42f0a5590f6df03de522493a3f8c0ed3` |

## Archive Use

When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved the selected assets. Attach or retain `dist/release-asset-checksums.{csv,json,md}` from the release machine for byte-level PDF and ZIP verification. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record can be tied back to the exact claim boundary and manual signoff state.

After this manifest is generated, `reports/doi-deposit-readiness.md` records whether the release metadata, asset checksums, DOI record, and human read-through state are ready for final journal submission.
