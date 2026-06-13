# Causal Calibration Targets

This audit names the independent causal evidence required before the project can claim calibrated reform effects or representative national hidden-channel magnitudes. The current manuscript can use these rows as a policy-simulation boundary, not as evidence that the model estimates causal effects.

## Summary

- Targets: `10`
- Blocking calibrated policy-simulation claims: `10`
- P1 targets: `4`
- P2 targets: `6`
- Cleared targets: `0`
- Policy claim status: `bounded`

## Target Matrix

| Target | Priority | Status | Estimand | Current support | Clearance criterion | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| hidden-donor-routing-magnitude | P1 | bounded_proxy_only | Share and concentration of concealed or indirectly traceable donor-linked money that reaches electoral, lobbying, or public-information channels | Bounded top-EIN Schedule I transfer rows, OpenFEC outside-spending rows, and opaque-capacity proxies | Representative routing rows spanning multiple organization classes with donor-linkage metadata or an explicit defensible missingness model | Broaden nonprofit-routing rows beyond the top-EIN slice and add donor-linkage or beneficial-owner coverage where public sources permit. |
| substitution-elasticity | P1 | open_design_needed | Change in alternate-channel spending, contact, or influence pressure after a disclosure, finance, access, or cooling-off reform binds | Synthetic mechanism comparison, sensitivity sweeps, and source moments for individual channels | At least one external quasi-experimental or panel design that estimates cross-channel substitution direction for a named reform family | Build a cross-source event panel around one reform shock and track visible, intermediary, dark-money, comment, and procurement channels by actor and issue. |
| procurement-modification-causal-capture | P1 | denominator_mapped_not_causal | Effect of lobbying/vendor-network exposure on post-award modification, protest, exclusion, single-bid, or firewall outcomes conditional on agency, award type, and contract size | USAspending bulk denominator crosswalk, action-row diagnostics, distinct-award diagnostics, amount-weighted diagnostics, and optional SAM importer | A reconciled SAM/FPDS action-history panel linked to exposure variables and at least one causal or matched comparison design | Crosswalk USAspending and SAM/FPDS modification codes, then add protest, exclusion, offer-count, and firewall overlays. |
| revolving-door-access-effect | P1 | bounded_proxy_only | Effect of covered-position or post-employment movement on access, venue choice, enforcement forbearance, or rule/procurement outcomes | LDA-derived covered-position rows and revolving-door proxy diagnostics | Documented personnel-movement panel with timing and outcome linkage, not only covered-position indicators | Add OGE, FACA, witness, or personnel-movement exports and preserve person-entity identifiers for linkage. |
| public-financing-countervailing-effect | P2 | local_program_panel_only | Effect of public financing participation on donor concentration, candidate dependence, spending mix, and modeled capture pressure | NYC matching-fund rows and Seattle voucher rows | Multi-program candidate-level panel with participant/non-participant comparison and donor-mix outcomes | Add state and local public-financing panels and link them to candidate finance and election context. |
| comment-authenticity-and-uptake-effect | P2 | bounded_source_moments | Effect of duplicate compression or authenticity screening on unique information, review burden, substantive uptake, and final rule movement | Regulations.gov/Federal Register schema rows, comment-volume concentration, and synthetic comment-triage diagnostics | Docket-level panel with observed duplicate clusters and agency response/final-rule linkage | Add docket corpora with duplicate/template detection and link comments to agency response text or final-rule changes. |
| enforcement-deterrence-effect | P2 | bounded_source_moments | Effect of audit probability, detection delay, sanction severity, or enforcement backlog on visible and hidden influence behavior | Reporting-error detection and campaign-sanction incidence benchmarks plus model enforcement diagnostics | Linked enforcement-outcome panel with actor-level behavior before and after audits, referrals, or sanctions | Add enforcement-event rows with actor identifiers, delay, penalty, and follow-on behavior measures. |
| meeting-disclosure-and-access-effect | P2 | open_source_panel_needed | Effect of meeting-log completeness and timeliness on access concentration, network opacity, and subsequent channel substitution | Synthetic network opacity and legibility diagnostics; no committed representative meeting-log panel | Observed meeting-log panel linked to actor networks and outcomes, with missingness or completeness diagnostics | Add one machine-readable meeting-log panel and preserve actor, issue, date, and outcome linkage fields. |
| intermediary-network-effect | P2 | bounded_proxy_only | Effect of intermediary centrality or sponsored-messenger routing on policy, comment, campaign, or procurement outcomes | NYC intermediary rows, IRS EO BMF capacity proxies, bounded IRS 527 rows, and top-EIN Schedule I rows | Representative intermediary network with routing, issue, and outcome linkage rather than capacity proxies alone | Broaden Form 990 XML and 527 coverage, separate capacity from transfer routing, and link intermediaries to submissions or spending. |
| venue-shifting-detection-effect | P2 | open_linkage_needed | Effect of cross-venue entity resolution and disclosure matching on detected substitution and total influence distortion | Synthetic cross-venue detection index and source-specific identifiers | Entity-resolution spine linking at least three venues with audited false-positive/false-negative handling | Build an identifier spine across LDA clients, FEC committees/spenders, docket submitters, vendors, and enforcement/protest actors. |

## Source Families

- `hidden-donor-routing-magnitude`: IRS Form 990 XML Schedule I/R; IRS 8871/8872; OpenFEC Schedule E, electioneering, and communication-cost rows; state campaign-finance exports; curated investigative or beneficial-owner datasets
- `substitution-elasticity`: State lobbying and campaign-finance reforms; municipal disclosure changes; LDA filings; OpenFEC spending; docket comment records; meeting logs; procurement action records
- `procurement-modification-causal-capture`: SAM.gov Contract Awards; FPDS/USAspending transaction history; GAO bid protests; SAM exclusions; agency procurement-integrity/firewall records; LDA client and issue records
- `revolving-door-access-effect`: OGE disclosures; LDA covered-position fields; LegiStorm/OpenSecrets career histories; FACA rosters; witness records; calendars and meeting logs where available
- `public-financing-countervailing-effect`: NYC CFB; Seattle Democracy Voucher data; state and municipal public-financing programs; OpenFEC candidate finance and election results
- `comment-authenticity-and-uptake-effect`: Regulations.gov; Federal Register; agency docket files; ACUS/agency mass-comment reports; FTC/FCC/EPA docket-specific corpora
- `enforcement-deterrence-effect`: FEC enforcement and audit data; OCE/ethics records; DOJ/FARA enforcement; agency enforcement databases; inspector-general reports
- `meeting-disclosure-and-access-effect`: Agency meeting logs; EU/UK/transparency registers for comparative panels; state or municipal contact registers; White House/agency visitor logs where available
- `intermediary-network-effect`: IRS Form 990 XML; Schedule I/R; IRS 527 filings; NYC CFB intermediaries; think-tank grant disclosures; docket submitter records
- `venue-shifting-detection-effect`: LDA; OpenFEC; Regulations.gov; Federal Register; USAspending/SAM; court/protest dockets; enforcement databases; meeting logs
