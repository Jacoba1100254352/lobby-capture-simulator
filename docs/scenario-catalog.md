# Scenario Catalog

Current runnable scenarios:

- `open-access-lobbying`
- `budgeted-disclosed-lobbying`
- `low-salience-technical-rulemaking`
- `campaign-finance-dominant`
- `dark-money-dominant`
- `revolving-door-dominant`
- `intermediary-substitution`
- `real-time-transparency`
- `democracy-vouchers`
- `cooling-off-ban`
- `audit-and-sanctions`
- `hard-lobbying-budgets`
- `public-interest-representation-funds`
- `randomized-audit-sanctions`
- `machine-readable-meeting-logs`
- `hard-budget-substitution-stress`
- `visible-ban-dark-money-leakage`
- `opaque-network-substitution-frontier`
- `meeting-log-intermediary-leakage`
- `advisory-lobbying-substitution`
- `procurement-venue-shift-stress`
- `procurement-modification-capture-frontier`
- `outside-spending-disclosure-evasion`
- `public-finance-dark-money-frontier`
- `public-finance-outside-spending-leakage`
- `shadow-lobbying-maximum-stress`
- `enforced-cooling-off`
- `comment-authenticity-rules`
- `comment-authenticity-technical-substitution`
- `public-advocate-office`
- `procurement-firewalls`
- `venue-shifting-detection`
- `full-anti-capture-bundle`
- `bundle-with-evasion`
- `reform-threat-mobilization`

Each scenario uses the same core engine and changes the reform regime, channel incentives, arena mix, and lobby adaptation settings.

## Core Scenario Families

### Baseline and Disclosure

- `open-access-lobbying`: high-access, low-reform baseline with visible direct access, agenda pressure, and ordinary channel allocation. It is the high-capture reference case for the campaign snapshot.
- `budgeted-disclosed-lobbying`: a constrained baseline with disclosed spending, lower hidden influence, and partial reform success. It is useful for separating budget scarcity from strong anti-capture constraints.
- `real-time-transparency`: raises contact visibility and public backlash, reducing observed capture while preserving some hidden influence through substitution.

### Channel-Dominant Capture

- `low-salience-technical-rulemaking`: stresses technical complexity and weak public attention. It is the model's strongest visible-capture surface and should be interpreted as a rulemaking vulnerability stress case.
- `campaign-finance-dominant`: shifts influence toward campaign finance and donor concentration.
- `dark-money-dominant`: shifts influence toward opaque funding and disclosure avoidance.
- `revolving-door-dominant`: stresses post-government employment incentives and relationship-based access.
- `intermediary-substitution`: tests whether visible lobbying controls move influence into think tanks, associations, sponsored experts, and issue coalitions.

### Reform Instruments

- `democracy-vouchers`: stresses public financing, voucher participation, and donor-base broadening.
- `cooling-off-ban`: constrains revolving-door access and tests whether advisory or hidden channels substitute for direct post-employment influence.
- `audit-and-sanctions`: raises enforcement detection and sanction pressure.
- `hard-lobbying-budgets`: imposes strict spending caps and tests whether influence substitutes into less visible messengers.
- `public-interest-representation-funds`: funds countervailing advocates for technically complex rulemaking and legal asymmetry.
- `randomized-audit-sanctions`: uses randomized audits and strong sanctions to make evasion risk less predictable.
- `machine-readable-meeting-logs`: stresses real-time structured contact disclosure and meeting-log coverage.
- `hard-budget-substitution-stress`: makes visible lobbying caps bind while allowing high evasion freedom, so a lower observed-capture rate is treated as suspicious if hidden influence, intermediary routing, procurement exposure, venue shifts, or defensive spending rise.
- `visible-ban-dark-money-leakage`: treats a hard visible-lobbying cap as a failure candidate when influence moves to nonprofit issue ads, independent expenditures, association research, or litigation threats.
- `opaque-network-substitution-frontier`: uses machine-readable disclosure while stressing nonprofit, association, advisory, and venue-shift routes that remain difficult to connect.
- `meeting-log-intermediary-leakage`: tests whether structured meeting logs displace influence into association messengers, sponsored experts, advisory-committee gaps, and procurement side channels.
- `advisory-lobbying-substitution`: constrains formal contacts while leaving advisory, expert, association, and technical-consulting routes attractive.
- `procurement-venue-shift-stress`: tests whether influence migrates into vendor relationships, award design, and procurement-specific access when visible advocacy is constrained.
- `procurement-modification-capture-frontier`: targets post-award modifications, exclusion language, bid-protest leverage, and subaward eligibility after nominal procurement controls bind.
- `outside-spending-disclosure-evasion`: stresses campaign-finance substitution from disclosed channels into outside spending and delayed or less traceable electoral pressure.
- `public-finance-dark-money-frontier`: tests whether public financing and vouchers are offset by donor-network, nonprofit issue-ad, and independent-expenditure substitution.
- `public-finance-outside-spending-leakage`: separates candidate-side public-financing gains from independent expenditure and nonprofit messaging leakage.
- `shadow-lobbying-maximum-stress`: combines hard visible restrictions with high evasion freedom and weak channel legibility to expose failure modes hidden by low measured capture.
- `enforced-cooling-off`: pairs cooling-off periods with audit and sanction capacity.
- `comment-authenticity-rules`: targets comment flooding, template campaigns, and synthetic salience.
- `comment-authenticity-technical-substitution`: tests whether authenticity rules displace mass comments into sponsored expert filings, technical attachments, and consultant-written unique comments.
- `public-advocate-office`: tests public advocate and blind-review capacity as a direct counterweight to one-sided expertise.
- `procurement-firewalls`: targets vendor capture through contact controls, blind specification review, and procurement-specific sanctions.
- `venue-shifting-detection`: explicitly tracks movement across channels, messengers, and venues.
- `full-anti-capture-bundle`: combines transparency, public financing, cooling-off, anti-astroturf, public advocate, blind review, and enforcement controls.
- `bundle-with-evasion`: keeps the full bundle but gives organized interests greater freedom to preserve influence through opaque or substitute channels.
- `reform-threat-mobilization`: makes the anti-capture reform itself the target of defensive lobbying and litigation pressure.

## Interpretation Notes

- Scenarios are comparative stress tests, not calibrated policy forecasts.
- High-capture rows establish mechanism contrast; low-capture bundle rows show where the current parameterization saturates anti-capture success.
- Hidden-capture, total-distortion, hidden-influence, preserved-influence, venue-substitution, messenger-substitution, and evasion-shift columns should be read with capture rates. A low capture rate alone is not a model claim that the reform eliminates influence.
- Influence-network columns should be read as synthetic path diagnostics: network opacity, intermediary centrality, procurement exposure, revolving-door bridges, comment-network load, and venue-shift load identify where influence is moving when a reform changes visible lobbying.
- The preferred synthetic reform comparison is the lowest total influence distortion, not the highest nominal reform success or lowest visible capture.
- Source calibration is strongest for LDA, OpenFEC party-committee and Schedule E rows, NYC CFB public-financing/intermediary rows, Seattle Democracy Voucher rows, IRS EO BMF nonprofit-capacity rows, bounded IRS POFD Form 8872 rows for 527 political organizations, Federal Register/Regulations.gov schemas, USAspending award concentration, USAspending procurement bridge fields, the USAspending procurement action-panel parser, the opt-in SAM.gov Contract Awards parser, and LDA-derived covered-position revolving-door rows. OpenFEC electioneering and communication-cost rows are included in the pinned snapshot as a bounded electoral-communication bridge. Source calibration remains weakest for non-proxy direct dark-money routing, representative national public-financing coverage, archived representative SAM/FPDS action-level procurement histories, representative Form 990 intermediary routing, complete IRS 527 coverage beyond the bounded alphabetic slice, and representative personnel-movement revolving-door exports.

`make sensitivity` adds temporary sweep scenarios that are not listed by `--list`:

- enforcement strength at 0.10, 0.35, 0.80, and 1.25 times the full-bundle baseline;
- disclosure strength at 0.10, 0.35, 0.80, and 1.25 times the full-bundle baseline;
- public financing at 0.10, 0.35, 0.80, and 1.25 times the full-bundle baseline;
- cooling-off strength at 0.10, 0.35, 0.80, and 1.25 times the full-bundle baseline;
- evasion freedom at 0.00, 0.30, 0.60, and 0.90.

Sensitivity scenarios use the reform-heavy contest mix so defensive anti-reform spending, evasion, comments, client funding, and enforcement all remain active in the comparison.

`make ablation` adds reform-removal scenarios around the full anti-capture bundle:

- baseline full bundle;
- no enforcement;
- no beneficial-owner or dark-money disclosure;
- no public financing or democracy vouchers;
- no cooling-off rules;
- no anti-astroturf authentication;
- no public advocate or blind review.

The ablation report ranks removals by total-distortion increase and tracks observed capture, hidden capture, substitution risk, comment flooding, donor Gini, and enforcement capacity.

`make portfolio` adds a reform-portfolio screen around the stressed contest mix:

- transparency-first baseline;
- balanced compliance core;
- electoral substitution shield;
- rulemaking integrity stack;
- procurement hardening stack;
- countervailing representation stack;
- high-deterrence enforcement stack;
- civil-liberties-constrained portfolio;
- full anti-substitution portfolio;
- full anti-substitution portfolio under high evasion.

The portfolio report ranks candidate bundles by total influence distortion, hidden capture, substitution risk, administrative burden, network opacity, legitimate-advocacy chill, and speech-restriction risk, while rewarding cross-venue detection and participation protection. It is a design screen, not a welfare estimate.

`make mechanism-comparison` writes a three-row report comparing a visible single-channel baseline, a multi-channel model with substitution disabled, and the substitution-enabled model. This is the core mechanism comparison used by the paper.

`make validate` also writes `reports/substitution-audit.csv` and `reports/substitution-audit.md`. That audit compares each report row against an open-access or highest-visible-lobbying baseline and distinguishes distortion failures, hidden-capture warnings, hidden-influence warnings, substitution warnings, and channel-shift tradeoffs. Rows with visible capture reductions and only channel movement are classified separately as channel-shift tradeoffs.
