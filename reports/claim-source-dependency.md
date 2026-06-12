# Claim-Source Dependency Audit

This audit maps manuscript claim families to the source panels and source moments they depend on. It is generated from `reports/source-panel-inventory.csv` and `reports/source-moments.csv` so empirical support cannot drift silently from the paper text.

## Summary

- Cleared claim families: `4`
- Bounded claim families: `3`
- Not-cleared claim families: `3`

| Claim family | Status | Source support | Permitted use | Claim to avoid | Next evidence |
| --- | --- | --- | --- | --- | --- |
| Lobbying disclosure surface | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Distributional anchor for visible lobbying concentration and disclosure timing. | Do not generalize beyond the 2024 EPA/ENV source slice. | Broaden issue codes and agencies after the environmental slice remains stable. |
| Visible electoral money | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Distributional anchor for observed receipts and independent-expenditure pressure. | Do not treat visible FEC rows as direct dark-money or hidden-donor evidence. | Add lobbyist bundling, broader electoral-communication coverage, and state/local overlays. |
| Rulemaking comments | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Distributional anchor for docket volume, template saturation, and comment-authenticity diagnostics. | Do not infer causal comment effects or full agency-wide comment quality. | Expand docket-level duplicate/authenticity checks and agency coverage. |
| Procurement identifiers | cleared | Source dependencies are usable for the stated mechanism or distributional diagnostic. | Schema and distributional anchor for award identifiers, competition fields, and vendor matching. | Do not use identifier coverage as evidence of post-award modification incidence. | Broaden SAM/FPDS fields and link exclusions, protests, and firewalls. |
| Strategic substitution mechanism | bounded | Bounded by weak panels: Direct dark money (thin), Revolving door (thin). | Mechanism tests and source-aware stress diagnostics for channel substitution. | Do not present hidden substitution magnitudes as empirically validated. | Replace thin hidden-channel panels with direct routing, personnel, and transaction exports. |
| Public-financing counterweight | bounded | Bounded by weak panels: Public financing (thin). | Thin program-row anchor for countervailing campaign-finance mechanisms. | Do not claim representative national public-financing uptake. | Add NYC, Seattle, federal, and additional local program rows with archived source files. |
| Revolving-door access | bounded | Bounded by weak panels: Revolving door (thin). | Proxy-backed stress diagnostics for covered-position and cooling-off exposure. | Do not treat LDA covered-position rows as representative post-employment movement. | Add OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports. |
| Hidden-channel magnitude | not_cleared | Not cleared because of weak panels: Direct dark money (thin), Revolving door (thin). | Missingness and proxy-gap diagnosis for hidden-channel mechanisms. | Do not treat bounded electoral-communication rows as hidden-donor or hidden-channel magnitude evidence. | Add direct hidden-donor or nonprofit-routing evidence plus broader electoral-communication coverage. |
| Procurement modification capture | not_cleared | Not cleared because of weak panels: Procurement concentration bridge (thin), Procurement modification risk (warning). | Coverage warning and schema check for modification and concentration pathways. | Do not claim calibrated national procurement-modification incidence or capture rates. | Populate representative SAM/FPDS action-level transaction denominators and validate modifications. |
| Calibrated policy simulation | not_cleared | Not cleared because of weak panels: Direct dark money (thin), Public financing (thin), Revolving door (thin), Procurement concentration bridge (thin), Procurement modification risk (warning). | Not cleared; the current article can only use mechanism diagnostics and bounded source moments. | Do not describe the artifact as a calibrated policy-effect simulator. | Clear the P1/P2 source gaps and rerun validation before using calibrated policy language. |

## Dependency Details

| Claim family | Strong dependencies | Weak dependencies | Moment checks |
| --- | --- | --- | --- |
| Lobbying disclosure surface | none | none | ldaRows=121 (ok); lobbyingClientTop3Share=0.8898 (ok) |
| Visible electoral money | Outside spending | none | fecRows=1269 (ok); outsideSpendingRows=919 (ok) |
| Rulemaking comments | none | none | regulatoryRows=200 (ok); commentTemplateShareMean=0.46 (ok); commentAuthenticationShareMean=0.32 (ok) |
| Procurement identifiers | Procurement identifiers | none | procurementRows=200 (ok); procurementKnownPiidShare=1 (ok); procurementSingleBidShare=0.235 (ok) |
| Strategic substitution mechanism | Outside spending; Intermediaries; Procurement identifiers | Direct dark money (thin); Revolving door (thin) | outsideSpendingRows=919 (ok); intermediaryRows=853 (ok); revolvingDoorRows=284 (ok) |
| Public-financing counterweight | none | Public financing (thin) | publicFinancingRows=132 (ok); publicFinancingSourceShare=0.0821 (ok) |
| Revolving-door access | none | Revolving door (thin) | revolvingDoorRows=284 (ok); revolvingDoorConfidenceMean=0.74 (ok) |
| Hidden-channel magnitude | Electoral communications | Direct dark money (thin); Revolving door (thin) | darkMoneySourceShare=0.0247 (ok); electoralCommunicationRows=269 (ok) |
| Procurement modification capture | Procurement action history | Procurement concentration bridge (thin); Procurement modification risk (warning) | procurementBridgeAgencyCount=6 (ok); procurementActionRows=1200 (ok); procurementExPostModificationShare=0.665 (ok) |
| Calibrated policy simulation | Electoral communications; Procurement action history | Direct dark money (thin); Public financing (thin); Revolving door (thin); Procurement concentration bridge (thin); Procurement modification risk (warning) | electoralCommunicationRows=269 (ok); procurementActionRows=1200 (ok) |
