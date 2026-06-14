# Archive Handoff Manifest

This report records checksums for the release assets and metadata that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.

## Summary

- Schema: `lobby-capture-archive-handoff-manifest-v1`
- Release tag: `paper-publication-readiness-2026-06-13-r101`
- Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/paper-publication-readiness-2026-06-13-r101
- Generated at: `2026-05-05T00:00:00Z`
- DOI status: not asserted by this manifest
- Self-omission: archive-handoff manifest files are release aids and are not checksum rows.

## Primary Release Assets

- `lobby-capture-wiley-submission.zip`
- `regulation-governance-wiley.pdf`
- `strategic-channel-substitution-regulatory-capture.pdf`
- `supplement.pdf`

## Checksums

| Path | Release asset | Role | DOI deposit | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| dist/lobby-capture-wiley-submission.zip | lobby-capture-wiley-submission.zip | wiley-submission-archive | yes | 1799737 | `9dec9a2109d00717a3908ff0ab807e36df47fc89d38bad7d368929b5626298ea` |
| paper/regulation-governance-wiley.pdf | regulation-governance-wiley.pdf | wiley-rendered-manuscript | yes | 1000276 | `dc0572433c1149ddc296aacc5120e43dfef12d09c5fffa16e7c719e4c36cd93a` |
| paper/strategic-channel-substitution-regulatory-capture.pdf | strategic-channel-substitution-regulatory-capture.pdf | local-rendered-manuscript | yes | 395802 | `0954bb6d4797053d795d0dd1b5cef859237df708f69187589d3a5bbd97c57ee2` |
| paper/supplement.pdf | supplement.pdf | supporting-information-pdf | yes | 169610 | `5b7d655d33a37cd627bc2c193689ee115be975c15c6218555337a9c64da0ee1b` |
| CITATION.cff | - | citation-metadata | source-archive | 1286 | `3068e1457ac16304221142c859bda79f66c0b4cdea023802bf99f77fbc79898d` |
| .zenodo.json | - | doi-deposit-metadata | source-archive | 1490 | `d6b1926e5ac439c5a1e506f208edd94773af6944b0375ae99ee6c72034dc387a` |
| reports/submission-readiness.md | - | submission-readiness-audit | source-archive | 4469 | `f095a95571e1b66c8586a2a33e465537873ddf23ea5e306c596f514de53b4d0f` |
| reports/final-human-readthrough.md | - | manual-signoff-record | source-archive | 2930 | `aef4d8130e8eb04c986e65eab1204e0ac7115f31301080e7cbb2a4f4b8592adb` |

## Archive Use

When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved byte-identical assets. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record can be tied back to the exact claim boundary and manual signoff state.
