# Scenario Catalog

Current runnable scenarios:

- `open-access-lobbying`
- `budgeted-disclosed-lobbying`
- `low-salience-technical-rulemaking`
- `campaign-finance-dominant`
- `dark-money-dominant`
- `revolving-door-dominant`
- `real-time-transparency`
- `democracy-vouchers`
- `cooling-off-ban`
- `audit-and-sanctions`
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

### Reform Instruments

- `democracy-vouchers`: stresses public financing, voucher participation, and donor-base broadening.
- `cooling-off-ban`: constrains revolving-door access and tests whether advisory or hidden channels substitute for direct post-employment influence.
- `audit-and-sanctions`: raises enforcement detection and sanction pressure.
- `full-anti-capture-bundle`: combines transparency, public financing, cooling-off, anti-astroturf, public advocate, blind review, and enforcement controls.
- `bundle-with-evasion`: keeps the full bundle but gives organized interests greater freedom to preserve influence through opaque or substitute channels.
- `reform-threat-mobilization`: makes the anti-capture reform itself the target of defensive lobbying and litigation pressure.

## Interpretation Notes

- Scenarios are comparative stress tests, not calibrated policy forecasts.
- High-capture rows establish mechanism contrast; low-capture bundle rows show where the current parameterization saturates anti-capture success.
- Hidden-influence, preserved-influence, venue-substitution, messenger-substitution, and evasion-shift columns should be read with capture rates. A low capture rate alone is not a model claim that the reform eliminates influence.
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

The ablation report ranks removals by capture-rate increase and tracks anti-capture success, dark-money share, defensive spending, comment distortion, donor Gini, and detection.
