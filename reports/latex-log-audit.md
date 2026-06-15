# LaTeX Log Audit

This audit scans the final local manuscript, Wiley manuscript, and supplement LaTeX logs for unresolved compile state. Overfull and underfull boxes are reported for visual follow-up, but only unresolved errors, citations, references, missing logs, or rerun-required states block the artifact gate.

- Logs checked: `3`
- Unresolved states: `0`

| Document | Status | Unresolved | Overfull hbox | Max hbox pt | Overfull vbox | Max vbox pt | Underfull hbox | Underfull vbox |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| local-manuscript | pass | - | 0 | 0.0000 | 0 | 0.0000 | 17 | 0 |
| wiley-manuscript | pass | - | 0 | 0.0000 | 1 | 50.7244 | 30 | 8 |
| supplement | pass | - | 0 | 0.0000 | 0 | 0.0000 | 40 | 0 |
