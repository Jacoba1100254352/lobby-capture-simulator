# Final Read-Through Evidence

This generated packet maps each unchecked scholarly read-through item to current automated evidence. It is a reviewer aid, not a human signoff.

## Summary

- Overall status: `manual_required`
- Status counts: `automated_support_present=12`; `external_manual_required=2`; `manual_required=1`
- Human signoff remains controlled by `reports/final-human-readthrough.md`.

## Evidence Matrix

| Item | Status | Automated evidence | Evidence files | Remaining human action |
| --- | --- | --- | --- | --- |
| scholarly-readthrough-checklist-01 | automated_support_present | policy overclaim hits=0; abstract mechanism language=yes; abstract bounded-language signal=yes | paper/strategic-channel-substitution-regulatory-capture.tex; paper/regulation-governance-wiley.tex; reports/policy-claim-language-audit.md | Confirm the abstract reads as a mechanism-model contribution, not a calibrated policy-effect claim. |
| scholarly-readthrough-checklist-02 | automated_support_present | mechanism=ready; empiricalBridge=bounded; calibratedPolicy=blocked | reports/submission-readiness.md; paper/sections/reggov-body.tex | Read the introduction for rhetorical separation of assumptions, synthetic findings, and empirical bridge limits. |
| scholarly-readthrough-checklist-03 | automated_support_present | literatureAuditReady=8; literatureAuditPartial=0; literatureAuditBlocked=0 | reports/literature-positioning-audit.md; paper/sections/reggov-body.tex; paper/references.bib | Judge whether the audited literature coverage is persuasive and sufficiently developed for the target venue. |
| scholarly-readthrough-checklist-04 | automated_support_present | latexLogsPass=yes; missingSpecArtifacts=none | docs/odd-model.md; paper/tables/composite_weights.tex; paper/tables/switch_rule_snapshot.tex; reports/latex-log-audit.md | Compare the main-text model description against the ODD supplement and generated diagnostic tables. |
| scholarly-readthrough-checklist-05 | automated_support_present | policy overclaim hits=0; calibratedPolicyGate=not_cleared | reports/policy-claim-language-audit.md; reports/claim-posture-audit.md; reports/substitution-audit.md | Read result prose for overinterpretation despite the mechanical language audit passing. |
| scholarly-readthrough-checklist-06 | automated_support_present | empiricalBridge=bounded; sourceLimitedPanels=7; candidateLeakageFailures=0 | reports/claim-posture-audit.md; reports/source-panel-inventory.md; reports/source-capability-audit.md; reports/candidate-source-leakage-audit.md | Check that the manuscript describes the bridge as bounded source support rather than validation of hidden-channel magnitudes. |
| scholarly-readthrough-checklist-07 | automated_support_present | layoutVisualGate=ready; latexLogsPass=yes; structureFailures=0 | reports/paper-layout-audit.md; reports/paper-structure-audit.md; reports/manual-visual-audit.md; reports/latex-log-audit.md | Visually inspect the Wiley PDF one last time, especially figure placement and table readability. |
| scholarly-readthrough-checklist-08 | automated_support_present | limitationsSection=yes; openCausalTargets=10; targetLanguage=yes | paper/sections/reggov-body.tex; reports/causal-calibration-targets.md; reports/reviewer-risk-register.md | Judge whether the limitations are specific and candid without sounding like a self-rejection. |
| scholarly-readthrough-checklist-09 | external_manual_required | dataCodeGate=ready; doiRecorded=no | paper/sections/submission-declarations.tex; reports/reggov-guidelines-readiness.md; CITATION.cff; .zenodo.json | Record the DOI once minted; before then, verify the statement keeps DOI absence explicit. |
| scholarly-readthrough-checklist-10 | automated_support_present | primaryAssets=5/5; releaseAssetChecksumRows=5 | reports/archive-handoff-manifest.md; dist/release-asset-checksums.md | Use the checksum files during archive deposition and record the final DOI afterward. |
| scholarly-readthrough-checklist-11 | external_manual_required | metadataPresent=yes; unpublishedDraft=manual_not_asserted_by_this_packet | .zenodo.json; CITATION.cff; reports/archive-handoff-manifest.md | Run Zenodo preflight/draft/upload only after a token is configured and the final release is frozen. |
| scholarly-readthrough-checklist-12 | automated_support_present | placeholderPhrases=none; latexLogsPass=yes; referenceAuditReady=68; referenceAuditAdvisory=0; referenceAuditBlocked=0 | paper/references.bib; reports/reference-integrity-audit.md; reports/latex-log-audit.md | Perform a human bibliography adequacy check for venue fit and scholarly completeness. |
| scholarly-readthrough-checklist-13 | automated_support_present | aiDisclosure=yes; wileyDataAiGate=ready | paper/sections/submission-declarations.tex; reports/wiley-submission-form-readiness.md | Confirm the disclosure matches the final journal form wording before submission. |
| scholarly-readthrough-checklist-14 | automated_support_present | reviewBundle=ready; latexSubmissionFiles=ready; releaseTag=paper-publication-readiness-2026-06-19-r206; archiveReleaseTag=paper-publication-readiness-2026-06-19-r206; doiReleaseMetadata=matches | CITATION.cff; reports/archive-handoff-manifest.md; reports/doi-deposit-readiness.md; reports/submission-readiness.md; reports/reggov-guidelines-readiness.md; dist/lobby-capture-wiley-submission.zip; dist/lobby-capture-wiley-blinded-review.zip | After any edit, rerun the full artifact gate and repeat this read-through evidence check. |

## Boundary

`automated_support_present` means the generated reports provide useful support for the checklist item. It does not mean the item is checked or signed.
`manual_editorial_review_required`, `manual_review_required`, and `external_manual_required` all require human action before final journal submission.
