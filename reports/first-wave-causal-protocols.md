# First-Wave Causal Protocols

This report operationalizes the first-wave rows from `reports/causal-calibration-targets.md`. It does not clear calibrated policy-simulation claims. It specifies the minimum empirical designs needed before a later manuscript can move from mechanism checking toward source-anchored causal calibration.

## Summary

- Protocols: `4`
- Protocol-ready/source-pending rows: `4`
- Policy-simulation status: `not_cleared`

## Protocol Matrix

| Target | Unit | Treatment or shock | Comparison design | Primary outcomes |
| --- | --- | --- | --- | --- |
| substitution-elasticity | actor-issue-month or actor-issue-quarter | binding disclosure, access, finance, cooling-off, or venue-integrity reform affecting one actor/issue set before comparable alternatives | event-study or difference-in-differences panel with matched unaffected actors, issues, or jurisdictions | visible lobbying spend/contact, outside spending, docket submissions, procurement activity, intermediary routing, and hidden/substitution proxy load |
| procurement-modification-causal-capture | award-action, award-recipient-quarter, or agency-award-type panel | lobbying/vendor-network exposure before post-award actions or procurement-integrity reform exposure | matched award/action panel controlling for agency, award type, size, timing, competition, and recipient history | modification incidence, single-bid or limited-competition exposure, protest incidence, exclusion flags, firewall coverage, and amount-weighted modification load |
| comment-authenticity-and-uptake-effect | docket-comment, submitter-docket, or docket-rule stage | duplicate compression, authenticity rule, mass-comment campaign, or docket triage procedure affecting comment processing | treated/untreated docket comparison or before/after design around authentication, deduplication, or high-template campaign events | unique-information share, template saturation, technical-content share, review burden, agency-response uptake, and final-rule text movement |
| venue-shifting-detection-effect | canonical actor-issue-venue-time record | availability of cross-venue entity resolution, disclosure matching, or meeting-log linkage for an actor/issue set | linkage-yield and detection design comparing single-source diagnostics with linked multi-venue actor/issue panels | detected cross-venue movement, previously hidden actor overlap, network opacity, substitution-risk reclassification, and false-match rate |

## Linkage and Validity Checks

| Target | Linkage keys | Minimum sources | Falsification checks | Sensitivity checks |
| --- | --- | --- | --- | --- |
| substitution-elasticity | canonical actor id, issue code, client name, committee/spender id, docket id, UEI/recipient id, jurisdiction, and event date | LDA clients, OpenFEC spenders, Regulations.gov/Federal Register dockets, procurement vendors, meeting logs or nonprofit/intermediary rows | pre-trend tests, placebo reform dates, unaffected issue placebo rows, and actor types not plausibly exposed to the reform | alternative event windows, actor matching rules, issue-code coarsening, and exclusion of high-outlier spenders |
| procurement-modification-causal-capture | PIID, UEI, recipient name, agency, award type, action date, fiscal year, LDA client/issue, protest docket, and exclusion identifier | SAM.gov Contract Awards or FPDS action history, USAspending transaction rows, GAO protest rows, SAM exclusions, agency firewall records, and LDA client/issue rows | pre-award placebo modifications, low-discretion award classes, agencies without plausible exposure, and non-policy issue placebo links | row-weighted, distinct-award, and amount-weighted denominators; agency fixed effects; competition-field completeness thresholds |
| comment-authenticity-and-uptake-effect | docket id, comment id, submitter id/name, organization, issue terms, posted date, response section, rule id, and final-rule date | Regulations.gov comments, Federal Register rules, agency response text, duplicate/template clusters, authenticity fields where available, and technical-content labels | dockets without mass-comment exposure, non-substantive procedural comments, placebo response sections, and pre-campaign comment waves | duplicate-clustering thresholds, technical-content classifiers, response-text matching rules, and excluding late or withdrawn comments |
| venue-shifting-detection-effect | canonical actor id, aliases, client/registrant id, committee/spender id, docket submitter id, UEI/vendor id, meeting participant, issue code, and date | LDA, OpenFEC, Regulations.gov/Federal Register, USAspending/SAM, enforcement or protest rows, meeting logs, and audited alias tables | manual false-positive/false-negative samples, same-name different-entity traps, unrelated issue placebo links, and withheld-source validation | strict versus fuzzy matching, issue-window width, alias normalization rules, and venue subsets with and without meeting/procurement rows |

## Claim Boundary

| Target | Threat model | Claim-upgrade boundary | Clearance criterion |
| --- | --- | --- | --- |
| substitution-elasticity | simultaneous political shocks, endogenous reform adoption, entity-resolution errors, and unobserved private contacts | Can support a source-anchored substitution diagnostic for the named reform family; cannot establish national hidden-channel magnitudes alone. | At least one external quasi-experimental or panel design that estimates cross-channel substitution direction for a named reform family |
| procurement-modification-causal-capture | procurement coding inconsistency, unobserved contract complexity, reverse causality from troubled awards to lobbying, and missing protest/firewall data | Can strengthen procurement-domain capture-adjacent diagnostics; cannot justify broad calibrated capture effects without exposure timing and outcome linkage. | A reconciled SAM/FPDS action-history panel linked to exposure variables and at least one causal or matched comparison design |
| comment-authenticity-and-uptake-effect | missing comment bodies, bot or identity uncertainty, agency selection into authentication tools, and conflating volume with substantive influence | Can anchor rulemaking information-distortion mechanisms for observed dockets; cannot generalize to all agencies or hidden influence channels alone. | Docket-level panel with observed duplicate clusters and agency response/final-rule linkage |
| venue-shifting-detection-effect | entity-resolution bias, common-name collisions, missing private channels, and inflated substitution when issue codes are too broad | Can support a detection and measurement contribution for cross-venue substitution; cannot by itself prove that substitution changed outcomes. | Entity-resolution spine linking at least three venues with audited false-positive/false-negative handling |
