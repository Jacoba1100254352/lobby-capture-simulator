# Revolving-Door Bridge Audit

This audit separates LDA covered-position access proxies from documented post-employment personnel-movement rows and from fixture rows.

## Claim Boundary

The committed revolving-door bridge contains 803 LDA-derived covered-position rows across 550 people, 202 organizations, and 6 agency or office labels. It contains 0 documented post-employment movement rows. The cooling-off-under-one-year diagnostic has 0 rows. Revolving-door magnitude and access-intensity claims remain bounded until OGE, FACA, witness, LegiStorm/OpenSecrets, ProPublica-style, or other documented personnel movement exports are archived.

| Source | Status | Evidence | Role | Rows | People | Orgs | Agencies | Top agency | Covered-position | Documented movement | Fixture | Under 1yr | Confidence | Influence | Boundary |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| lda-covered-position-access-proxy | ok | covered-position and cooling-off exposure proxy | source-native LDA covered-position derivation | 803 | 550 | 202 | 6 | 0.4919 | 803 | 0 | 0 | 0 | 0.7400 | 0.3400 | supports covered-position mechanism diagnostics; not representative post-employment movement |
| documented-post-employment-movement | not-present | direct post-employment movement evidence | documented personnel-movement export | 0 | 0 | 0 | 0 | 0.0000 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | required before claiming representative post-employment movement or access intensity |
| fixture-schema-rows | not-present | fixture | schema fixture fallback | 0 | 0 | 0 | 0 | 0.0000 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | schema and parser continuity only; not empirical calibration evidence |
| cooling-off-under-one-year | not-present | covered-position interval proxy | cooling-off interval diagnostic | 0 | 0 | 0 | 0 | 0.0000 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | use as a stress diagnostic, not a measured cooling-off violation rate |
| procurement-linked-roles | ok | role-text proxy | procurement-linked personnel bridge | 1 | 1 | 1 | 1 | 1.0000 | 1 | 0 | 0 | 0 | 0.7400 | 0.3400 | requires OGE, contract-office, or personnel-source overlays before procurement revolving-door claims |
