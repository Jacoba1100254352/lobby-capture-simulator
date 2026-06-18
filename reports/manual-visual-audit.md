# Visual Review Checklist

This report complements the scripted layout audit. Figure rows check generated SVG label boxes for overlap, bounds, and leader-line coverage where callout labels exist. It is still worth doing a final human visual inspection before submission.

## Current Automated Layout Summary

- Pages checked: `54`
- Failures: `0`

## Figure Checks

| Figure source | Labels distinct | Labels near/reference point | Labels visible | Readable in PDF | Float whitespace acceptable | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `channel_mix.tex` | n/a | n/a | n/a | scripted pass | layout pass | no point-callout labels in this figure |
| `evasion_sensitivity.tex` | scripted pass | scripted pass | scripted pass | scripted pass | layout pass | 2 label boxes; 2 leader lines |
| `interaction_tradeoffs.tex` | scripted pass | scripted pass | scripted pass | scripted pass | layout pass | 4 label boxes; 4 leader lines |
| `model_architecture.tex` | n/a | n/a | n/a | scripted pass | layout pass | no point-callout labels in this figure |
| `scenario_tradeoffs.tex` | scripted pass | scripted pass | scripted pass | scripted pass | layout pass | 12 label boxes; 12 leader lines |
| `substitution_warning_map.tex` | scripted pass | scripted pass | scripted pass | scripted pass | layout pass | 10 label boxes; 10 leader lines |

## Table Checks

| Table source | Fits page/column | Text readable | Caption close to table | No excessive white space | Notes |
| --- | --- | --- | --- | --- | --- |
| `ablation_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `apparent_failure_ranking.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `campaign_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `claim_source_dependency.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `composite_weights.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `diagnostic_variant_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `distortion_decomposition.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `experiment_design.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `first_wave_causal_protocols.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `full_campaign_appendix.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `interaction_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `mechanism_comparison.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `portfolio_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `sensitivity_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `substitution_warning_ranking.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `switch_rule_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |
| `validation_gap_snapshot.tex` | layout pass | layout pass | layout pass | layout pass |  |

## Review Standard

- Every point label in scatter or tradeoff figures should be distinct, non-overlapping, completely visible, and connected to the intended point by proximity or a leader line.
- Figure pages should include enough surrounding readable text that a float does not create a mostly blank page.
- Tables should avoid unreadable shrinkage; if a table requires extreme compression, move detail to the supplement or split the table.
- The final review should be rerun after any change to generated reports, tables, figures, LaTeX wrappers, or journal template files.
