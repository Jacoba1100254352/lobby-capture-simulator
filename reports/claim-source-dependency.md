# Claim-Source Dependency Audit

This audit maps manuscript claim families to the source panels and source moments they depend on. It is generated from `reports/source-panel-inventory.csv` and `reports/source-moments.csv` so empirical support cannot drift silently from the paper text.

## Summary

- Cleared claim families: `7`
- Bounded claim families: `1`
- Not-cleared claim families: `2`

| Claim family | Status | Source support | Permitted use | Claim to avoid | Next evidence |
| --- | --- | --- | --- | --- | --- |
| Lobbying disclosure surface | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Distributional anchor for visible lobbying concentration and disclosure timing. | Do not generalize beyond the 2024 EPA/ENV source slice. | Broaden issue codes and agencies after the environmental slice remains stable. |
| Visible electoral money | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Distributional anchor for observed receipts and independent-expenditure pressure. | Do not treat visible FEC rows as direct dark-money or hidden-donor evidence. | Add lobbyist bundling, broader electoral-communication coverage, and state/local overlays. |
| Rulemaking comments | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Distributional anchor for docket volume, template saturation, and comment-authenticity diagnostics. | Do not infer causal comment effects or full agency-wide comment quality. | Expand docket-level duplicate/authenticity checks and agency coverage. |
| Procurement identifiers | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Schema and distributional anchor for award identifiers, competition fields, and vendor matching. | Do not use identifier coverage as evidence of post-award modification incidence. | Broaden SAM/FPDS fields and link exclusions, protests, and firewalls. |
| Strategic substitution mechanism | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Mechanism tests and source-aware stress diagnostics for channel substitution. | Do not present hidden substitution magnitudes as empirically validated. | Broaden bounded nonprofit-routing, personnel, and transaction exports. |
| Public-financing counterweight | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Bounded local-program anchor for countervailing campaign-finance mechanisms. | Do not claim representative national public-financing uptake. | Add federal, state, and additional local program rows with archived source files. |
| Revolving-door access | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Proxy-backed stress diagnostics for covered-position and cooling-off exposure. | Do not treat LDA covered-position rows as representative post-employment movement. | Add OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports. |
| Hidden-channel magnitude | bounded | Bounded by top-EIN Schedule I routing coverage and unobserved donor identities. | Bounded nonprofit-routing and missingness diagnostics for hidden-channel mechanisms. | Do not treat the top-EIN Schedule I slice or bounded electoral-communication rows as representative hidden-channel magnitude or donor-identity evidence. | Broaden nonprofit-routing, direct donor, and electoral-communication coverage beyond the current top-EIN slice. |
| Procurement modification capture | not_cleared | Not cleared because of weak panels: Procurement modification risk (thin). | Coverage warning and schema check for modification and concentration pathways. | Do not claim calibrated national procurement-modification incidence or capture rates. | Populate representative SAM/FPDS action-level transaction denominators and validate modifications. |
| Calibrated policy simulation | not_cleared | Not cleared because of weak panels: Procurement modification risk (thin). | Not cleared; the current article can only use mechanism diagnostics and bounded source moments. | Do not describe the artifact as a calibrated policy-effect simulator. | Clear the P1/P2 source gaps and rerun validation before using calibrated policy language. |

## Dependency Details

| Claim family | Strong dependencies | Weak dependencies | Moment checks |
| --- | --- | --- | --- |
| Lobbying disclosure surface | none | none | ldaRows=121 (ok); lobbyingClientTop3Share=0.8898 (ok) |
| Visible electoral money | Outside spending | none | fecRows=1268 (ok); outsideSpendingRows=998 (ok) |
| Rulemaking comments | none | none | regulatoryRows=200 (ok); commentTemplateShareMean=0.46 (ok); commentAuthenticationShareMean=0.32 (ok) |
| Procurement identifiers | Procurement identifiers | none | procurementRows=200 (ok); procurementKnownPiidShare=1 (ok); procurementSingleBidShare=0.235 (ok) |
| Strategic substitution mechanism | Direct dark money; Outside spending; Intermediaries; IRS 527 political organizations; Revolving door; Procurement identifiers | none | outsideSpendingRows=998 (ok); intermediaryRows=1353 (ok); intermediary527Rows=500 (ok); revolvingDoorRows=803 (ok) |
| Public-financing counterweight | Public financing | none | publicFinancingRows=135 (ok); publicFinancingProgramCount=2 (ok) |
| Revolving-door access | Revolving door | none | revolvingDoorRows=803 (ok); revolvingDoorConfidenceMean=0.74 (ok) |
| Hidden-channel magnitude | Direct dark money; Electoral communications; Revolving door | none | darkMoneyDirectRoutingRows=80 (ok); electoralCommunicationRows=268 (ok) |
| Procurement modification capture | Procurement concentration panel; Procurement action history | Procurement modification risk (thin) | procurementConcentrationPanelAgencyCount=12 (ok); procurementActionRows=2399 (ok); procurementExPostModificationShare=0.3297 (ok); procurementModifiedAwardShare=0.2269 (ok) |
| Calibrated policy simulation | Direct dark money; Electoral communications; Public financing; IRS 527 political organizations; Revolving door; Procurement concentration panel; Procurement action history | Procurement modification risk (thin) | darkMoneyDirectRoutingRows=80 (ok); electoralCommunicationRows=268 (ok); intermediary527Rows=500 (ok); procurementActionRows=2399 (ok) |
