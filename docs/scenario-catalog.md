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

`make sensitivity` adds temporary sweep scenarios that are not listed by `--list`:

- enforcement strength at 0.35, 0.65, 1.00, and 1.25 times the full-bundle baseline;
- disclosure strength at 0.35, 0.65, 1.00, and 1.25 times the full-bundle baseline;
- public financing at 0.35, 0.65, 1.00, and 1.25 times the full-bundle baseline;
- cooling-off strength at 0.35, 0.65, 1.00, and 1.25 times the full-bundle baseline;
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
