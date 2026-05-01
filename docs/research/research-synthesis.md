# Deep Research Synthesis

This note distills the six Deep Research reports supplied in May 2026 into project decisions for the Lobby Capture Simulator. The reports are source notes, not direct empirical identification. Their shared design lesson is that organized interests adapt across channels: reforms usually change the price, route, visibility, and timing of influence before they eliminate influence.

## Source Reports

- `deep-research-report.md`: rulemaking comments, comment manipulation, comment triage, and Regulations.gov/Federal Register validation ideas.
- `deep-research-report1.md`: anti-capture reform mechanisms, practical parameter ranges, and common evasion routes.
- `deep-research-report2.md`: reproducible 2024 validation snapshot protocol.
- `deep-research-report3.md`: empirical calibration ranges for money, rulemaking, enforcement, procurement, and revolving-door variables.
- `deep-research-report4.md`: influence substitution taxonomy and reporting requirements.
- `deep-research-report5.md`: literature map, paper framing, and original contribution.

## Model Consequences

The simulator should keep capture as a vector of stage-specific influence rather than a binary captured/not-captured state. The most important dimensions are agenda access, information quality, donor dependence, administrative discretion, enforcement forbearance, procurement favoritism, rulemaking record distortion, and post-office access.

Rulemaking comments should be treated as an information-processing problem. Raw comment volume is a noisy salience signal. Evidence quality should come from unique information, technical credibility, source confidence, and agency triage capacity. Duplicate and fake comments should increase public-record distortion and review burden without proportionally increasing substantive information.

Reforms should operate on portfolios. Public financing changes candidate dependence but can trigger outside-spending substitution. Disclosure improves observability but needs verification, cross-checking, and enforcement. Lobbying bans and cooling-off rules often create shadow lobbying unless advisory and behind-the-scenes work are covered. Anti-astroturf systems should compress duplicates and reduce fraud while preserving a channel for legitimate anonymous or low-resource participation.

The simulator's original contribution should be dynamic substitution after reform. The key reported outcome is not only whether capture fell, but how much influence capacity survived, where it moved, and whether the new route is more or less observable.

## Implementation Priorities

1. Keep `data/calibration/parameter-map.csv` as the translation layer from research priors to simulator moments.
2. Expand validation from broad plausibility bands to typed benchmarks: observed, inferred, proxy, and judgmental.
3. Model comments as layered records: unique information, organized technical comments, templates, and false-attribution shells.
4. Add substitution metrics to every report: pressure to switch, hidden influence, influence preserved, messenger substitution, venue substitution, and net transparency change.
5. Use a closed 2024 EPA/ENV snapshot as the first paper-grade validation slice before adding health, transportation, or multi-agency panels.
6. Reframe the paper around stages and channels: capture theory, influence mechanisms, institutional arenas, reforms/enforcement, simulation, calibration, and institutional design.

## Evidence Discipline

The reports repeatedly warn against overclaiming. Public financing evidence is stronger on participation and fundraising composition than downstream policy outcomes. Comment-system evidence is stronger on manipulation and processing burdens than causal policy effects. Disclosure evidence is stronger on observability than deterrence. Procurement and revolving-door evidence is strong in particular sectors, but not always generalizable. The model and paper should label parameters by evidence quality and use sensitivity analysis where evidence is proxy-based.
