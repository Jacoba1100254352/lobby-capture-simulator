# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `23`
- `direct-source-moment`: `20`
- `model-tuning`: `20`
- `scale-alignment`: `5`
- `scenario-coverage`: `15`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | scale-alignment | lobby-capture-ablation.csv | `averageDisclosureLag` | miss | 0.5283-0.5320 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | scale-alignment | lobby-capture-portfolio.csv | `averageDisclosureLag` | miss | 0.5263-0.6350 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | model-tuning | lobby-capture-ablation.csv | `largeDonorDependence` | miss | 0.6639-0.6640 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | miss | 0.6623-0.7485 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | miss | 0.6638-0.7342 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-portfolio.csv | `largeDonorDependence` | miss | 0.6638-0.7326 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | miss | 0.6638-0.7361 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0062-0.0521 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0062-0.0521 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0028-0.2188 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0028-0.2188 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0033-0.0936 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0033-0.0936 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-portfolio.csv | `procurementBias` | miss | 0.0040-0.0881 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-portfolio.csv | `procurementBias` | miss | 0.0040-0.0881 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0042-0.0740 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0042-0.0740 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | benchmark-review | lobby-capture-ablation.csv | `publicFinancingCandidateUptake` | miss | 0.0738-0.5594 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-ablation.csv | `regulatorQueueBacklog` | miss | 0.4751-0.4898 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-interactions.csv | `regulatorQueueBacklog` | miss | 0.4047-0.4219 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-portfolio.csv | `regulatorQueueBacklog` | miss | 0.4435-0.4596 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-sensitivity.csv | `regulatorQueueBacklog` | miss | 0.4431-0.4560 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P2 | model-tuning | lobby-capture-ablation.csv | `commentCompressionRate` | miss | 0.3699-0.4340 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-interactions.csv | `commentCompressionRate` | miss | 0.4193-0.4480 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-portfolio.csv | `commentCompressionRate` | miss | 0.3530-0.4554 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-sensitivity.csv | `commentCompressionRate` | miss | 0.4155-0.4484 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | benchmark-review | lobby-capture-ablation.csv | `darkMoneyDirectVisibility` | miss | 0.0000-0.0000 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `donorInfluenceGini` | miss | 0.1733-0.1977 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `donorInfluenceGini` | miss | 0.1648-0.2110 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-portfolio.csv | `donorInfluenceGini` | miss | 0.1691-0.2050 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `donorInfluenceGini` | miss | 0.1744-0.1974 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.0250-0.1467 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.0250-0.1467 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.0005-0.3146 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2638 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2638 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.0302-0.2511 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.0302-0.2511 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2704 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2704 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0002 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-campaign.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0165 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0006 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-portfolio.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0004 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0003 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | miss | 0.0151-0.1122 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | miss | 0.0000-0.0432 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | miss | 0.0000-0.0801 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | miss | 0.0000-0.0874 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `venueSubstitutionRate` | miss | 0.0000-0.0430 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | miss | 0.0000-0.0539 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.3735-0.6761 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-interactions.csv | `averageDisclosureLag` | partial | 0.4407-0.6372 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-sensitivity.csv | `averageDisclosureLag` | partial | 0.4431-0.6415 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.2228-0.6312 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | benchmark-review | lobby-capture-campaign.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5318 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5321 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5640 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5319 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.1184-0.3344 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.1228-0.6794 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | partial | 0.1027-0.5073 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-portfolio.csv | `detectionRate` | partial | 0.1588-0.4849 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | partial | 0.1467-0.5376 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | direct-source-moment | lobby-capture-campaign.csv | `donorInfluenceGini` | partial | 0.0000-0.4208 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.0005-0.3146 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1695-0.4647 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0000-0.9991 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.0616-0.5947 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.2325-0.6808 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.1030-0.6802 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.1223-0.6808 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.1171-0.5724 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0056-0.0944 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0081-0.1731 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0027-0.2113 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0052-0.1824 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | benchmark-review | lobby-capture-ablation.csv | `voucherResidentParticipation` | partial | 0.0080-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `voucherResidentParticipation` | partial | 0.0080-0.0584 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `voucherResidentParticipation` | partial | 0.0094-0.0612 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `voucherResidentParticipation` | partial | 0.0125-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
