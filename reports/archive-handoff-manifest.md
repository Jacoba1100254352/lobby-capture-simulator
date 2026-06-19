# Archive Handoff Manifest

This report records the release asset set and stable source-metadata checksums that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.

PDF and ZIP byte streams can differ across TeX and archive implementations. The release-machine checksums for those binary assets are written to `dist/release-asset-checksums.{csv,json,md}` and should be attached to the GitHub release or DOI deposit record.

## Summary

- Schema: `lobby-capture-archive-handoff-manifest-v1`
- Release tag: `paper-publication-readiness-2026-06-19-r204`
- Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/paper-publication-readiness-2026-06-19-r204
- Generated at: `2026-05-05T00:00:00Z`
- DOI status: not asserted by this manifest
- Release asset checksum file: `dist/release-asset-checksums.{csv,json,md}`
- Self-omission: archive-handoff manifest files are release aids and are not checksum rows.

## Primary Release Assets

- `lobby-capture-wiley-blinded-review.zip`
- `lobby-capture-wiley-submission.zip`
- `regulation-governance-wiley.pdf`
- `strategic-channel-substitution-regulatory-capture.pdf`
- `supplement.pdf`

## Checksums

| Path | Release asset | Role | DOI deposit | Checksum status | Bytes | SHA-256 |
| --- | --- | --- | --- | --- | ---: | --- |
| dist/lobby-capture-wiley-blinded-review.zip | lobby-capture-wiley-blinded-review.zip | wiley-blinded-review-archive | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| dist/lobby-capture-wiley-submission.zip | lobby-capture-wiley-submission.zip | wiley-submission-archive | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| paper/regulation-governance-wiley.pdf | regulation-governance-wiley.pdf | wiley-rendered-manuscript | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| paper/strategic-channel-substitution-regulatory-capture.pdf | strategic-channel-substitution-regulatory-capture.pdf | local-rendered-manuscript | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| paper/supplement.pdf | supplement.pdf | supporting-information-pdf | yes | release-asset-checksum-recorded-in-dist | see-dist-release-asset-checksums | `see-dist-release-asset-checksums` |
| CITATION.cff | - | citation-metadata | source-archive | tracked-source-verified | 1286 | `ef21a5539f268ea743829ff396af0b2e6e9a6321ea649b1dcd192bb3f9ce8dc3` |
| .zenodo.json | - | doi-deposit-metadata | source-archive | tracked-source-verified | 1490 | `66be521566e6173f4bfbcf144fb064a0ca007002086a8634b099c058f2d1b901` |
| reports/submission-readiness.md | - | submission-readiness-audit | source-archive | tracked-source-verified | 5027 | `0edaac2441256f12ce6c6f727d91e5a4fb8ba8c4998fcc669e538bc2d174f1e8` |
| reports/reviewer-risk-register.csv | - | reviewer-risk-register | source-archive | tracked-source-verified | 6984 | `73c56d18c1b8ffdc4786874ff92e69d56dc4fd08957919d2f8220ef75ef02f58` |
| reports/reviewer-risk-register.md | - | reviewer-risk-register | source-archive | tracked-source-verified | 8156 | `25cb9a07da4aa4394d682dedf52be0936f2c801bca37953a9807617801f74200` |
| reports/final-human-readthrough.md | - | manual-signoff-record | source-archive | tracked-source-verified | 7245 | `9ad52ae8ae80980825467718d4753af2af93661a55d9b9e06781e9846a62394d` |
| reports/final-human-readthrough-audit.csv | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 6894 | `38c98113b00622e8aa38ecc34973ce6241373fa2209dd6468a0d28250497f0aa` |
| reports/final-human-readthrough-audit.md | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 7861 | `c3935effbc0c4592ce70f29393625534352744237bde0d4431b86e8b9b7da3bd` |

## Archive Use

When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved the selected assets. Attach or retain `dist/release-asset-checksums.{csv,json,md}` from the release machine for byte-level PDF and ZIP verification. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, `reports/final-human-readthrough.md`, `reports/final-human-readthrough-audit.md`, and `reports/final-readthrough-evidence.md` so the DOI record can be tied back to the exact claim boundary, automated read-through evidence, and manual signoff state.

After this manifest is generated, `reports/doi-deposit-readiness.md` records whether the release metadata, asset checksums, DOI record, and human read-through state are ready for final journal submission.
