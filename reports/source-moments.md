# Source Moments

These are direct moments from normalized calibration tables. They are source diagnostics, not causal estimates.

| Scope | Source | Metric | Value | Evidence | Notes |
| --- | --- | --- | ---: | --- | --- |
| snapshot | lda | `ldaRows` | 13.0000 | observed | normalized LDA rows |
| snapshot | lda | `ldaTotalSpend` | 0.0050 | observed | sum of normalized LDA amount |
| snapshot | lda | `lobbyingClientTop1Share` | 1.0000 | observed | largest client share of normalized LDA amount |
| snapshot | lda | `lobbyingClientTop3Share` | 1.0000 | observed | top three clients share of normalized LDA amount |
| snapshot | lda | `lobbyingRegistrantTop3Share` | 1.0000 | observed | top three registrants share of normalized LDA amount |
| snapshot | lda | `lobbyingSectorTopShare` | 1.0000 | observed | largest issue-domain share of normalized LDA amount |
| snapshot | lda | `lobbyingDisclosureLagMean` | 1.0000 | observed | mean normalized LDA disclosure lag |
| snapshot | fec | `fecRows` | 100.0000 | observed | normalized OpenFEC rows |
| snapshot | fec | `fecTotalReceipts` | 505.0783 | observed | sum of normalized FEC amount |
| snapshot | fec | `fecDonorTop1Share` | 0.2292 | observed | largest donor share of normalized FEC amount |
| snapshot | fec | `fecDonorTop3Share` | 0.5893 | observed | top three donor share of normalized FEC amount |
| snapshot | fec | `fecRecipientTop3Share` | 0.9086 | observed | top three recipient share of normalized FEC amount |
| snapshot | fec | `fecLargeDonorWeightedShare` | 0.9500 | observed_proxy | amount-weighted normalized large donor share |
| snapshot | fec | `moneyFlowTraceability` | 0.6200 | observed_proxy | amount-weighted traceability across all normalized FEC rows |
| snapshot | fec | `darkMoneyDirectVisibility` | 0.0000 | inferred | amount-weighted traceability among DARK_MONEY and SUPER_PAC rows |
| snapshot | fec | `darkMoneySourceShare` | 0.0000 | observed_proxy | DARK_MONEY and SUPER_PAC share of normalized FEC amount |
| snapshot | fec | `publicFinancingSourceShare` | 0.0000 | observed_proxy | public-match or voucher share of normalized FEC amount |
| snapshot | regulatory | `regulatoryRows` | 100.0000 | observed | normalized regulatory rows |
| snapshot | regulatory | `commentVolumeMean` | 118.2000 | observed_proxy | mean normalized comment volume |
| snapshot | regulatory | `commentVolumeTop1DocketShare` | 0.0102 | observed_proxy | largest docket share of normalized comments |
| snapshot | regulatory | `commentTemplateShareMean` | 0.4600 | observed_proxy | mean normalized template share |
| snapshot | regulatory | `commentAuthenticationShareMean` | 0.3200 | observed_proxy | mean normalized authentication share |
| snapshot | regulatory | `technicalClaimCredibilityMean` | 0.5000 | proxy | mean normalized technical claim credibility |
| snapshot | usaspending | `procurementRows` | 200.0000 | observed | normalized USAspending award rows |
| snapshot | usaspending | `procurementTotalAwards` | 4871.4339 | observed | sum of normalized USAspending award amount |
| snapshot | usaspending | `procurementRecipientTop1Share` | 0.0677 | observed | largest recipient share of normalized award amount |
| snapshot | usaspending | `procurementRecipientTop3Share` | 0.1723 | observed | top three recipients share of normalized award amount |
| snapshot | usaspending | `procurementAgencyTop1Share` | 1.0000 | observed | largest awarding agency share of normalized award amount |
| snapshot | usaspending | `procurementSubAgencyTop3Share` | 1.0000 | observed | top three sub-agencies share of normalized award amount |
| snapshot | usaspending | `procurementAwardCount` | 200.0000 | observed | sum of normalized award or transaction counts |
| snapshot | revolving-door | `revolvingDoorRows` | 5.0000 | observed | normalized revolving-door rows |
| snapshot | revolving-door | `revolvingDoorFormerOfficialShare` | 0.8000 | observed_proxy | share of rows with former official role |
| snapshot | revolving-door | `revolvingDoorAgencyTop1Share` | 0.6000 | observed_proxy | largest agency share of normalized revolving-door rows |
| snapshot | revolving-door | `revolvingDoorCoolingOffUnderOneYearShare` | 0.4000 | observed_proxy | share of rows with cooling-off interval below one year |
| snapshot | revolving-door | `revolvingDoorInfluenceMean` | 0.5460 | proxy | mean normalized influence share from source panel |
| fixture | lda | `ldaRows` | 4.0000 | observed | normalized LDA rows |
| fixture | lda | `ldaTotalSpend` | 30.5000 | observed | sum of normalized LDA amount |
| fixture | lda | `lobbyingClientTop1Share` | 0.2984 | observed | largest client share of normalized LDA amount |
| fixture | lda | `lobbyingClientTop3Share` | 0.8230 | observed | top three clients share of normalized LDA amount |
| fixture | lda | `lobbyingRegistrantTop3Share` | 0.8230 | observed | top three registrants share of normalized LDA amount |
| fixture | lda | `lobbyingSectorTopShare` | 0.2984 | observed | largest issue-domain share of normalized LDA amount |
| fixture | lda | `lobbyingDisclosureLagMean` | 0.4925 | observed | mean normalized LDA disclosure lag |
| fixture | fec | `fecRows` | 5.0000 | observed | normalized OpenFEC rows |
| fixture | fec | `fecTotalReceipts` | 20.8000 | observed | sum of normalized FEC amount |
| fixture | fec | `fecDonorTop1Share` | 0.3269 | observed | largest donor share of normalized FEC amount |
| fixture | fec | `fecDonorTop3Share` | 0.7356 | observed | top three donor share of normalized FEC amount |
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
| fixture | regulatory | `technicalClaimCredibilityMean` | 0.4875 | proxy | mean normalized technical claim credibility |
| fixture | usaspending | `procurementRows` | 5.0000 | observed | normalized USAspending award rows |
| fixture | usaspending | `procurementTotalAwards` | 700.0000 | observed | sum of normalized USAspending award amount |
| fixture | usaspending | `procurementRecipientTop1Share` | 0.3429 | observed | largest recipient share of normalized award amount |
| fixture | usaspending | `procurementRecipientTop3Share` | 0.8143 | observed | top three recipients share of normalized award amount |
| fixture | usaspending | `procurementAgencyTop1Share` | 1.0000 | observed | largest awarding agency share of normalized award amount |
| fixture | usaspending | `procurementSubAgencyTop3Share` | 0.8143 | observed | top three sub-agencies share of normalized award amount |
| fixture | usaspending | `procurementAwardCount` | 48.0000 | observed | sum of normalized award or transaction counts |
| fixture | revolving-door | `revolvingDoorRows` | 5.0000 | observed | normalized revolving-door rows |
| fixture | revolving-door | `revolvingDoorFormerOfficialShare` | 0.8000 | observed_proxy | share of rows with former official role |
| fixture | revolving-door | `revolvingDoorAgencyTop1Share` | 0.6000 | observed_proxy | largest agency share of normalized revolving-door rows |
| fixture | revolving-door | `revolvingDoorCoolingOffUnderOneYearShare` | 0.4000 | observed_proxy | share of rows with cooling-off interval below one year |
| fixture | revolving-door | `revolvingDoorInfluenceMean` | 0.5460 | proxy | mean normalized influence share from source panel |
