# Submission Readiness Audit

This audit synthesizes the generated claim, validation, layout, visual, and policy-language gates into one submission decision surface. It does not replace peer review or a final human read-through.

## Overall Posture

- Status: `ready_for_mechanism_review`
- Evidence: open causal-calibration targets=10
- Submission implication: The review bundle is ready to circulate as a mechanism-model package with a bounded empirical bridge; it is not a calibrated policy-effect submission or a final journal-submission signoff.
- Next action: Before final journal submission, clear the final-journal-submission gate.

## Gate Summary

| Gate | Status | Evidence | Submission implication | Next action |
| --- | --- | --- | --- | --- |
| mechanism-manuscript | ready | 0 validation misses, 0 unknown validations, 0 unresolved coverage-gap source panels, 7 usable but source-limited support panels, 0 article-blocking dependency claims not cleared | The paper may be reviewed as a transparent mechanism-model article when this gate is ready. | Keep empirical language tied to source moments, source gaps, and model diagnostics. |
| empirical-bridge-scope | bounded | 0 source-gap validations, 0 unresolved weak-status panels, 7 usable but source-limited support panels; 5 bounded claim dependencies | Source rows constrain distributional anchors and validation gaps, not hidden-channel magnitudes. | Prioritize SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, nonprofit-routing beyond the top-EIN Schedule I slice, and post-employment revolving-door overlays; broaden electoral-communication and public-financing rows as secondary coverage upgrades. |
| calibrated-policy-claims | blocked | validation queue P1=0, P2=0; causal targets P1=4, P2=6; 1 claim dependencies not cleared; calibrated-policy dependency=not_cleared; open causal targets=10 | The package must not be described as estimating calibrated reform effects while this gate is blocked. | Clear the causal-calibration target matrix, add stronger source panels, and rerun validation before using calibrated policy-simulation language. |
| claim-source-dependencies | bounded | bounded dependencies=5; not-cleared dependencies=1 | Bounded claim families can support mechanism stress tests but not representative hidden-channel claims. | Keep the claim-source dependency audit in the submission bundle and clear bounded dependencies before stronger claims. |
| policy-language-audit | ready | overclaim or missing-boundary hits=0 | The manuscript and supplement should not contain unbounded causal, calibrated-policy, ranking, or representativeness language. | Revise flagged language and rerun the policy-claim audit. |
| layout-and-visual-audit | ready | layout failures=0; visual checklist=pass; latex unresolved=0 | Figures, tables, generated PDFs, and final LaTeX logs pass the automated layout, label-readability, and unresolved-log checks. | Inspect and rerun the visual/layout audits after any figure, table, or LaTeX change. |
| reproducible-review-bundle | ready | layout failures=0, visual checklist=pass | The release bundle is suitable for review only after the full paper artifact gate passes. | Rerun the full artifact gate after any source, table, figure, LaTeX, or package change. |
| final-journal-submission | manual_required | release metadata=present; DOI archive=not detected; human scholarly read-through=not signed off (release=paper-publication-readiness-2026-06-18-r171; status=pending; blocked=0; manual_required=18; checkedChecklistItems=3/17); live author-page refresh=ready: official URL recorded=https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html; record URL=matches; checked-by=present; checked-date=present; reviewed-release=paper-publication-readiness-2026-06-18-r171; expected-release=paper-publication-readiness-2026-06-18-r171; superseding-instructions=none | Final journal submission still requires archive, human editorial signoff; cleared external items=live author-page refresh; mechanism-review circulation can proceed without treating this gate as cleared. | mint or record a DOI archive, such as Zenodo or OSF; complete and sign off a human scholarly read-through in reports/final-human-readthrough.md |

## Claim Boundary

A `ready_for_mechanism_review` posture means the release can be read as a mechanism-model manuscript with bounded source bridges. It does not clear calibrated policy-effect claims, representative hidden-channel magnitudes, or final venue-specific editorial acceptance.

## Final Journal Submission Boundary

The `final-journal-submission` gate records external submission requirements that cannot be cleared by simulator tests alone: DOI archiving, a human scholarly read-through, and live Regulation & Governance author-page refresh. This gate is deliberately separate from mechanism-review readiness so the bundle can circulate for review without implying final journal-submission signoff.
