# Archive Handoff Manifest

This report records the release asset set and stable source-metadata checksums that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.

PDF and ZIP byte streams can differ across TeX and archive implementations. The release-machine checksums for those binary assets are written to `dist/release-asset-checksums.{csv,json,md}` and should be attached to the GitHub release or DOI deposit record.

## Summary

- Schema: `lobby-capture-archive-handoff-manifest-v1`
- Release tag: `paper-publication-readiness-2026-06-19-r208`
- Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/paper-publication-readiness-2026-06-19-r208
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
| CITATION.cff | - | citation-metadata | source-archive | tracked-source-verified | 1286 | `335866698e6f8cefc3298619d30dd28e843d7ea3efb966db217c3ff4bdde60b9` |
| .zenodo.json | - | doi-deposit-metadata | source-archive | tracked-source-verified | 1490 | `a38819c944511f279900e31169099d26a01e9a5e407fd0643d78867a288e002c` |
| reports/submission-readiness.md | - | submission-readiness-audit | source-archive | tracked-source-verified | 5027 | `0b83dbcaaa8cc69fb77f45be31ed85927659f8c6f5af7efba322fcaa0a04dbfa` |
| reports/reviewer-risk-register.csv | - | reviewer-risk-register | source-archive | tracked-source-verified | 7000 | `dd7de993e173da19ded2dfb1ded941f37d6da4ada90725e236aab1e98e64866e` |
| reports/reviewer-risk-register.md | - | reviewer-risk-register | source-archive | tracked-source-verified | 8172 | `b1061a0939c9e8bf17a6e4be510b13e221ddd5e439ceeea2e0f032f95adb97f8` |
| reports/final-human-readthrough.md | - | manual-signoff-record | source-archive | tracked-source-verified | 7245 | `eac77b6d6ae3c0ba2429b3378db3ab0687ef94fbe9aacd5fd4f219b76e1dbb8a` |
| reports/final-human-readthrough-audit.csv | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 6894 | `2a294e0439930f05bd8c4f27c05209dcb58ac15eb873ad4c8b76b64ea88ba7a6` |
| reports/final-human-readthrough-audit.md | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 7861 | `b7de36add24967bf1abc1e99e29fda8fd960099613dbffab00de57ebbc9abd6f` |

## Archive Use

When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved the selected assets. Attach or retain `dist/release-asset-checksums.{csv,json,md}` from the release machine for byte-level PDF and ZIP verification. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, `reports/final-human-readthrough.md`, `reports/final-human-readthrough-audit.md`, and `reports/final-readthrough-evidence.md` so the DOI record can be tied back to the exact claim boundary, automated read-through evidence, and manual signoff state.

After this manifest is generated, `reports/doi-deposit-readiness.md` records whether the release metadata, asset checksums, DOI record, and human read-through state are ready for final journal submission.
