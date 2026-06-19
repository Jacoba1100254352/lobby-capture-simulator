# Archive Handoff Manifest

This report records the release asset set and stable source-metadata checksums that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.

PDF and ZIP byte streams can differ across TeX and archive implementations. The release-machine checksums for those binary assets are written to `dist/release-asset-checksums.{csv,json,md}` and should be attached to the GitHub release or DOI deposit record.

## Summary

- Schema: `lobby-capture-archive-handoff-manifest-v1`
- Release tag: `paper-publication-readiness-2026-06-18-r184`
- Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/paper-publication-readiness-2026-06-18-r184
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
| CITATION.cff | - | citation-metadata | source-archive | tracked-source-verified | 1286 | `7ed00ec6c87c3421d62b18da973e2f231cdfce76acd312681c6340ba35a0ad90` |
| .zenodo.json | - | doi-deposit-metadata | source-archive | tracked-source-verified | 1490 | `d326a70bb32bfa0710cbdfc5d5d89ad5ff1a33f6d3ad2d54ffd65cbc79276dba` |
| reports/submission-readiness.md | - | submission-readiness-audit | source-archive | tracked-source-verified | 4989 | `52cfd942e242c3a548ad658224b0fd4ea7d6d62835d75e00ab6ef68203ac6b81` |
| reports/reviewer-risk-register.csv | - | reviewer-risk-register | source-archive | tracked-source-verified | 6954 | `2ec3f65be278a901ba52f120b51e172c3443189ec35e6bd2c24d82069b3d7b4b` |
| reports/reviewer-risk-register.md | - | reviewer-risk-register | source-archive | tracked-source-verified | 8126 | `57265c7748ca53590657b872ea35d78cc7b0c68c68a3fec492a85749876b53fe` |
| reports/final-human-readthrough.md | - | manual-signoff-record | source-archive | tracked-source-verified | 5629 | `60e2e130c2c88e1ea37830eec0824b96107a8515ad5b143fe80f7b4991e4ace7` |
| reports/final-human-readthrough-audit.csv | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 6874 | `334a07a00a643bf1b0f058b7652ed2c18d17043155d53fdcaac3be862144e443` |
| reports/final-human-readthrough-audit.md | - | final-human-readthrough-audit | source-archive | tracked-source-verified | 7841 | `2701cb4bc7c10a40607adce5fd20454d7bcac842e818d67b2b10660513db456e` |

## Archive Use

When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved the selected assets. Attach or retain `dist/release-asset-checksums.{csv,json,md}` from the release machine for byte-level PDF and ZIP verification. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, `reports/final-human-readthrough.md`, `reports/final-human-readthrough-audit.md`, and `reports/final-readthrough-evidence.md` so the DOI record can be tied back to the exact claim boundary, automated read-through evidence, and manual signoff state.

After this manifest is generated, `reports/doi-deposit-readiness.md` records whether the release metadata, asset checksums, DOI record, and human read-through state are ready for final journal submission.
