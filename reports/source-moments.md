# Source Moments

These are direct moments from normalized calibration tables. They are source diagnostics, not causal estimates.

## Representativeness Warnings

- Snapshot FEC rows contain no DARK_MONEY or SUPER_PAC flow share; dark-money calibration still depends on benchmark and scenario assumptions.
- Snapshot FEC rows contain no public-match or democracy-voucher flow share; public-financing calibration still depends on external benchmarks.
- Snapshot revolving-door rows are tracked fixtures; they support schema and mechanism tests, not empirical calibration.
- Think-tank, association, and sponsored-expert intermediary routing is modeled but not yet anchored by a direct public-data panel.

| Scope | Source | Metric | Value | Evidence | Notes |
| --- | --- | --- | ---: | --- | --- |
| snapshot | lda | `ldaRows` | 121.0000 | observed | normalized LDA rows |
| snapshot | lda | `ldaTotalSpend` | 1.1295 | observed | sum of normalized LDA amount |
| snapshot | lda | `lobbyingClientTop1Share` | 0.3763 | observed | largest client share of normalized LDA amount |
| snapshot | lda | `lobbyingClientTop3Share` | 0.8898 | observed | top three clients share of normalized LDA amount |
| snapshot | lda | `lobbyingRegistrantTop3Share` | 0.8898 | observed | top three registrants share of normalized LDA amount |
| snapshot | lda | `lobbyingSectorTopShare` | 0.5551 | observed | largest issue-domain share of normalized LDA amount |
| snapshot | lda | `lobbyingDisclosureLagMean` | 1.0000 | observed | mean normalized LDA disclosure lag |
| snapshot | lda | `coveredOfficialShareMean` | 0.2000 | observed_proxy | mean share of covered-official contact visibility |
| snapshot | lda | `lobbyingClientHerfindahl` | 0.2885 | observed | client concentration Herfindahl over normalized LDA amount |
| snapshot | fec | `fecRows` | 600.0000 | observed | normalized OpenFEC rows |
| snapshot | fec | `fecTotalReceipts` | 926.7037 | observed | sum of normalized FEC amount |
| snapshot | fec | `fecDonorTop1Share` | 0.1467 | observed | largest donor share of normalized FEC amount |
| snapshot | fec | `fecDonorTop3Share` | 0.3747 | observed | top three donor share of normalized FEC amount |
| snapshot | fec | `fecDonorGini` | 0.6180 | observed | donor amount Gini across normalized FEC rows |
| snapshot | fec | `fecRecipientTop3Share` | 0.7665 | observed | top three recipient share of normalized FEC amount |
| snapshot | fec | `fecLargeDonorWeightedShare` | 0.9492 | observed_proxy | amount-weighted normalized large donor share |
| snapshot | fec | `moneyFlowTraceability` | 0.6200 | observed_proxy | amount-weighted traceability across all normalized FEC rows |
| snapshot | fec | `darkMoneyDirectVisibility` | 0.0000 | inferred | amount-weighted traceability among DARK_MONEY and SUPER_PAC rows |
| snapshot | fec | `darkMoneySourceShare` | 0.0000 | observed_proxy | DARK_MONEY and SUPER_PAC share of normalized FEC amount |
| snapshot | fec | `publicFinancingSourceShare` | 0.0000 | observed_proxy | public-match or voucher share of normalized FEC amount |
| snapshot | regulatory | `regulatoryRows` | 200.0000 | observed | normalized regulatory rows |
| snapshot | regulatory | `commentVolumeMean` | 119.7000 | observed_proxy | mean normalized comment volume |
| snapshot | regulatory | `commentVolumeTop1DocketShare` | 0.0752 | observed_proxy | largest docket share of normalized comments |
| snapshot | regulatory | `commentTemplateShareMean` | 0.4600 | observed_proxy | mean normalized template share |
| snapshot | regulatory | `commentAuthenticationShareMean` | 0.3200 | observed_proxy | mean normalized authentication share |
| snapshot | regulatory | `commentFloodingIndex` | 0.3072 | proxy | combined top-docket concentration, template share, and low-authentication pressure |
| snapshot | regulatory | `technicalClaimCredibilityMean` | 0.5000 | proxy | mean normalized technical claim credibility |
| snapshot | usaspending | `procurementRows` | 200.0000 | observed | normalized USAspending award rows |
| snapshot | usaspending | `procurementTotalAwards` | 4872.5023 | observed | sum of normalized USAspending award amount |
| snapshot | usaspending | `procurementRecipientTop1Share` | 0.0677 | observed | largest recipient share of normalized award amount |
| snapshot | usaspending | `procurementRecipientTop3Share` | 0.1723 | observed | top three recipients share of normalized award amount |
| snapshot | usaspending | `procurementRecipientHerfindahl` | 0.0250 | observed | recipient award-amount Herfindahl |
| snapshot | usaspending | `procurementAgencyTop1Share` | 1.0000 | observed | largest awarding agency share of normalized award amount |
| snapshot | usaspending | `procurementAgencyHerfindahl` | 1.0000 | observed | awarding-agency amount Herfindahl |
| snapshot | usaspending | `procurementSubAgencyTop3Share` | 1.0000 | observed | top three sub-agencies share of normalized award amount |
| snapshot | usaspending | `procurementAwardCount` | 200.0000 | observed | sum of normalized award or transaction counts |
| snapshot | revolving-door | `revolvingDoorRows` | 14.0000 | observed | normalized revolving-door rows |
| snapshot | revolving-door | `revolvingDoorFixtureShare` | 1.0000 | diagnostic | share of rows marked as tracked fixture rather than live/exported source |
| snapshot | revolving-door | `revolvingDoorFormerOfficialShare` | 0.7857 | observed_proxy | share of rows with former official role |
| snapshot | revolving-door | `revolvingDoorAgencyTop1Share` | 0.4286 | observed_proxy | largest agency share of normalized revolving-door rows |
| snapshot | revolving-door | `revolvingDoorCoolingOffUnderOneYearShare` | 0.5000 | observed_proxy | share of rows with cooling-off interval below one year |
| snapshot | revolving-door | `revolvingDoorCoolingOffMeanMonths` | 15.5714 | observed_proxy | mean cooling-off interval in months |
| snapshot | revolving-door | `revolvingDoorHighInfluenceShare` | 0.4286 | proxy | share of rows with high normalized influence |
| snapshot | revolving-door | `revolvingDoorInfluenceWeightedFormerOfficialShare` | 0.8781 | proxy | influence-weighted former-official share |
| snapshot | revolving-door | `revolvingDoorInfluenceMean` | 0.5507 | proxy | mean normalized influence share from source panel |
| fixture | lda | `ldaRows` | 4.0000 | observed | normalized LDA rows |
| fixture | lda | `ldaTotalSpend` | 30.5000 | observed | sum of normalized LDA amount |
| fixture | lda | `lobbyingClientTop1Share` | 0.2984 | observed | largest client share of normalized LDA amount |
| fixture | lda | `lobbyingClientTop3Share` | 0.8230 | observed | top three clients share of normalized LDA amount |
| fixture | lda | `lobbyingRegistrantTop3Share` | 0.8230 | observed | top three registrants share of normalized LDA amount |
| fixture | lda | `lobbyingSectorTopShare` | 0.2984 | observed | largest issue-domain share of normalized LDA amount |
| fixture | lda | `lobbyingDisclosureLagMean` | 0.4925 | observed | mean normalized LDA disclosure lag |
| fixture | lda | `coveredOfficialShareMean` | 0.2500 | observed_proxy | mean share of covered-official contact visibility |
| fixture | lda | `lobbyingClientHerfindahl` | 0.2580 | observed | client concentration Herfindahl over normalized LDA amount |
| fixture | fec | `fecRows` | 5.0000 | observed | normalized OpenFEC rows |
| fixture | fec | `fecTotalReceipts` | 20.8000 | observed | sum of normalized FEC amount |
| fixture | fec | `fecDonorTop1Share` | 0.3269 | observed | largest donor share of normalized FEC amount |
| fixture | fec | `fecDonorTop3Share` | 0.7356 | observed | top three donor share of normalized FEC amount |
| fixture | fec | `fecDonorGini` | 0.1981 | observed | donor amount Gini across normalized FEC rows |
| fixture | fec | `fecRecipientTop3Share` | 1.0000 | observed | top three recipient share of normalized FEC amount |
| fixture | fec | `fecLargeDonorWeightedShare` | 0.6081 | observed_proxy | amount-weighted normalized large donor share |
| fixture | fec | `moneyFlowTraceability` | 0.6648 | observed_proxy | amount-weighted traceability across all normalized FEC rows |
| fixture | fec | `darkMoneyDirectVisibility` | 0.4240 | inferred | amount-weighted traceability among DARK_MONEY and SUPER_PAC rows |
| fixture | fec | `darkMoneySourceShare` | 0.4087 | observed_proxy | DARK_MONEY and SUPER_PAC share of normalized FEC amount |
| fixture | fec | `publicFinancingSourceShare` | 0.2644 | observed_proxy | public-match or voucher share of normalized FEC amount |
| fixture | regulatory | `regulatoryRows` | 4.0000 | observed | normalized regulatory rows |
| fixture | regulatory | `commentVolumeMean` | 1147.5000 | observed_proxy | mean normalized comment volume |
| fixture | regulatory | `commentVolumeTop1DocketShare` | 0.3922 | observed_proxy | largest docket share of normalized comments |
| fixture | regulatory | `commentTemplateShareMean` | 0.4800 | observed_proxy | mean normalized template share |
| fixture | regulatory | `commentAuthenticationShareMean` | 0.3100 | observed_proxy | mean normalized authentication share |
| fixture | regulatory | `commentFloodingIndex` | 0.4888 | proxy | combined top-docket concentration, template share, and low-authentication pressure |
| fixture | regulatory | `technicalClaimCredibilityMean` | 0.4875 | proxy | mean normalized technical claim credibility |
| fixture | usaspending | `procurementRows` | 5.0000 | observed | normalized USAspending award rows |
| fixture | usaspending | `procurementTotalAwards` | 700.0000 | observed | sum of normalized USAspending award amount |
| fixture | usaspending | `procurementRecipientTop1Share` | 0.3429 | observed | largest recipient share of normalized award amount |
| fixture | usaspending | `procurementRecipientTop3Share` | 0.8143 | observed | top three recipients share of normalized award amount |
| fixture | usaspending | `procurementRecipientHerfindahl` | 0.2469 | observed | recipient award-amount Herfindahl |
| fixture | usaspending | `procurementAgencyTop1Share` | 1.0000 | observed | largest awarding agency share of normalized award amount |
| fixture | usaspending | `procurementAgencyHerfindahl` | 1.0000 | observed | awarding-agency amount Herfindahl |
| fixture | usaspending | `procurementSubAgencyTop3Share` | 0.8143 | observed | top three sub-agencies share of normalized award amount |
| fixture | usaspending | `procurementAwardCount` | 48.0000 | observed | sum of normalized award or transaction counts |
| fixture | revolving-door | `revolvingDoorRows` | 14.0000 | observed | normalized revolving-door rows |
| fixture | revolving-door | `revolvingDoorFixtureShare` | 1.0000 | diagnostic | share of rows marked as tracked fixture rather than live/exported source |
| fixture | revolving-door | `revolvingDoorFormerOfficialShare` | 0.7857 | observed_proxy | share of rows with former official role |
| fixture | revolving-door | `revolvingDoorAgencyTop1Share` | 0.4286 | observed_proxy | largest agency share of normalized revolving-door rows |
| fixture | revolving-door | `revolvingDoorCoolingOffUnderOneYearShare` | 0.5000 | observed_proxy | share of rows with cooling-off interval below one year |
| fixture | revolving-door | `revolvingDoorCoolingOffMeanMonths` | 15.5714 | observed_proxy | mean cooling-off interval in months |
| fixture | revolving-door | `revolvingDoorHighInfluenceShare` | 0.4286 | proxy | share of rows with high normalized influence |
| fixture | revolving-door | `revolvingDoorInfluenceWeightedFormerOfficialShare` | 0.8781 | proxy | influence-weighted former-official share |
| fixture | revolving-door | `revolvingDoorInfluenceMean` | 0.5507 | proxy | mean normalized influence share from source panel |
