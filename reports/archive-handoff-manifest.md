# Archive Handoff Manifest

This report records the release asset set and stable source-metadata checksums that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.

PDF and ZIP byte streams can differ across TeX and archive implementations. The release-machine checksums for those binary assets are written to `dist/release-asset-checksums.{csv,json,md}` and should be attached to the GitHub release or DOI deposit record.

## Summary

- Schema: `lobby-capture-archive-handoff-manifest-v1`
- Release tag: `paper-publication-readiness-2026-06-19-r200`
- Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/paper-publication-readiness-2026-06-19-r200
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
| CITATION.cff | - | citation-metadata | source-archive | tracked-source-verified | 1286 | `3286aff7ef8167e97744d83240cc4e57b25f3de34bd5eaeef16ea61b1e253682` |
| .zenodo.json | - | doi-deposit-metadata | source-archive | tracked-source-verified | 1490 | `77ad50761a77203b8850c4732a50520ad294101ca58af77b20a4046c7c62efa4` |
| reports/submission-readiness.md | - | submission-readiness-audit | source-archive | tracked-source-verified | 5114 | `6e098856eaa456f41a47acc3d640cae72b51a7c366e9c0ac547d01252f9197fa` |
| reports/reviewer-risk-register.csv | - | reviewer-risk-register | source-archive | tracked-source-verified | 7024 | `ccfcb65372d4e36dcbb520a74da78bf0396ec56e657b7f7a2ea7e83477e70ced` |
| reports/reviewer-risk-register.md | - | reviewer-risk-register | source-archive | tracked-source-verified | 8196 | `c7589acfa0eacf235e643da7fc68d8ad9a129e9bb19bdf45b5d0446352f914b4` |
| reports/final-human-readthrough.md | - | manual-signoff-record | source-archive | tracked-source-verified | 6276 | `bfe952e2482baf051d60d6f69ae60ab6bf35f736995fa0f1675c32d255852334` |
| reports/final-human-readthrough-audit.csv | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 6905 | `a8d2b218fdd5b2b56038ee8a5ae8b3b4688d289db91b764af394f347f4f2ef9a` |
| reports/final-human-readthrough-audit.md | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 7871 | `796d03bcd64447789ef13c8ebb8871bb992d8d3631048eaeff5092a2c33758c6` |

## Archive Use

When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved the selected assets. Attach or retain `dist/release-asset-checksums.{csv,json,md}` from the release machine for byte-level PDF and ZIP verification. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, `reports/final-human-readthrough.md`, `reports/final-human-readthrough-audit.md`, and `reports/final-readthrough-evidence.md` so the DOI record can be tied back to the exact claim boundary, automated read-through evidence, and manual signoff state.

After this manifest is generated, `reports/doi-deposit-readiness.md` records whether the release metadata, asset checksums, DOI record, and human read-through state are ready for final journal submission.
