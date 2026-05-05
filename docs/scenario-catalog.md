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
- `enforced-cooling-off`
- `comment-authenticity-rules`
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
- `enforced-cooling-off`: pairs cooling-off periods with audit and sanction capacity.
- `comment-authenticity-rules`: targets comment flooding, template campaigns, and synthetic salience.
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
- The preferred synthetic reform comparison is the lowest total influence distortion, not the highest nominal reform success or lowest visible capture.
- Source calibration is currently strongest for LDA, FEC committee flows, Federal Register/Regulations.gov schemas, and USAspending award concentration. It remains weakest for dark-money source shares, public-financing source shares, and revolving-door panels.

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

`make validate` also writes `reports/substitution-audit.csv` and `reports/substitution-audit.md`. That audit compares each report row against an open-access or highest-visible-lobbying baseline and flags cases where observed capture falls but hidden influence, hidden capture, total distortion, or substitution-failure risk rises.
