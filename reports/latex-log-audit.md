# LaTeX Log Audit

This audit scans the final local manuscript, Wiley manuscript, and supplement LaTeX logs for unresolved compile state. Overfull and underfull boxes are reported for visual follow-up, but only unresolved errors, citations, references, missing logs, or rerun-required states block the artifact gate.

- Logs checked: `3`
- Unresolved states: `0`

| Document | Status | Unresolved | Overfull hbox | Max hbox pt | Overfull vbox | Max vbox pt | VBox pages | Visual follow-up | Underfull hbox | Underfull vbox |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: |
| local-manuscript | pass | - | 0 | 0.0000 | 0 | 0.0000 | - | not needed | 17 | 0 |
| wiley-manuscript | pass | - | 0 | 0.0000 | 1 | 50.7244 | 1 | p1:layout pass | 28 | 4 |
| supplement | pass | - | 0 | 0.0000 | 0 | 0.0000 | - | not needed | 42 | 0 |

## Box-Warning Follow-Up

Box warnings are typography diagnostics, not unresolved compile states. Overfull vbox warnings are paired with the generated PDF layout audit so a reviewer can see whether the affected rendered page passed visual-density checks.

- `wiley-manuscript` reports 1 overfull vbox warning(s), max `50.7244` pt, nearest output page(s) `1`; follow-up: p1:layout pass.
