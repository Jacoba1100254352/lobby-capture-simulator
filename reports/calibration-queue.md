# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `22`
- `direct-source-moment`: `20`
- `model-tuning`: `20`
- `scale-alignment`: `5`
- `scenario-coverage`: `12`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | scale-alignment | lobby-capture-ablation.csv | `averageDisclosureLag` | miss | 0.5270-0.5329 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | scale-alignment | lobby-capture-portfolio.csv | `averageDisclosureLag` | miss | 0.5256-0.6390 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | model-tuning | lobby-capture-portfolio.csv | `detectionRate` | miss | 0.4110-0.7147 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | miss | 0.2181-0.7043 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P1 | model-tuning | lobby-capture-ablation.csv | `largeDonorDependence` | miss | 0.6638-0.6640 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | miss | 0.6623-0.7482 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | miss | 0.6637-0.7340 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-portfolio.csv | `largeDonorDependence` | miss | 0.6638-0.7329 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | miss | 0.6638-0.7360 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0461-0.0886 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0461-0.0886 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0125-0.3752 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0189-0.0987 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0189-0.0987 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-portfolio.csv | `procurementBias` | miss | 0.0509-0.0997 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-portfolio.csv | `procurementBias` | miss | 0.0509-0.0997 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0260-0.0811 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0260-0.0811 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | benchmark-review | lobby-capture-ablation.csv | `regulatorQueueBacklog` | miss | 0.4804-0.4951 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-interactions.csv | `regulatorQueueBacklog` | miss | 0.4065-0.4271 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-portfolio.csv | `regulatorQueueBacklog` | miss | 0.4514-0.4639 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-sensitivity.csv | `regulatorQueueBacklog` | miss | 0.4435-0.4583 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P2 | model-tuning | lobby-capture-ablation.csv | `commentCompressionRate` | miss | 0.3778-0.4396 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-interactions.csv | `commentCompressionRate` | miss | 0.4218-0.4492 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-portfolio.csv | `commentCompressionRate` | miss | 0.3765-0.4490 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-sensitivity.csv | `commentCompressionRate` | miss | 0.4239-0.4490 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | benchmark-review | lobby-capture-ablation.csv | `darkMoneyDirectVisibility` | miss | 0.0000-0.0000 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `donorInfluenceGini` | miss | 0.1693-0.1927 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `donorInfluenceGini` | miss | 0.1618-0.2053 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-portfolio.csv | `donorInfluenceGini` | miss | 0.1629-0.2022 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `donorInfluenceGini` | miss | 0.1666-0.1993 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.1433-0.2392 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.0657-0.3935 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0389-0.4588 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.1604-0.4599 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0392-0.4561 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0003 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-campaign.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0168 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0006 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-portfolio.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0010 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0003 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | separate headcount share from modeled influence intensity |
| P2 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | miss | 0.0780-0.3053 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.3735-0.6748 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-interactions.csv | `averageDisclosureLag` | partial | 0.4396-0.6437 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-sensitivity.csv | `averageDisclosureLag` | partial | 0.4390-0.6379 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.2257-0.6414 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-campaign.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5321 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5321 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5301 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5319 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.1769-0.6238 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.1719-0.9856 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | partial | 0.1147-0.7153 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | direct-source-moment | lobby-capture-campaign.csv | `donorInfluenceGini` | partial | 0.0000-0.4025 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.0657-0.3935 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | partial | 0.0389-0.4588 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | partial | 0.0392-0.4561 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1894-0.5092 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.1356-0.9988 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | partial | 0.0125-0.3752 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P3 | benchmark-review | lobby-capture-ablation.csv | `publicFinancingCandidateUptake` | partial | 0.0738-0.5594 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.0616-0.5947 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.2325-0.6808 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.1175-0.5594 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.1223-0.6808 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.1171-0.5715 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0084-0.2313 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0122-0.3466 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0100-0.2907 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0124-0.2800 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0342-0.1791 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0675-0.2158 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-portfolio.csv | `venueSubstitutionRate` | partial | 0.0724-0.2091 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0738-0.2069 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | benchmark-review | lobby-capture-ablation.csv | `voucherResidentParticipation` | partial | 0.0080-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `voucherResidentParticipation` | partial | 0.0080-0.0584 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `voucherResidentParticipation` | partial | 0.0101-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `voucherResidentParticipation` | partial | 0.0125-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
