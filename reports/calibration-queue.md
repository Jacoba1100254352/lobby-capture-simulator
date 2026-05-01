# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `15`
- `direct-source-moment`: `16`
- `metric-split`: `4`
- `model-tuning`: `23`
- `scale-alignment`: `4`
- `scenario-coverage`: `12`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | scale-alignment | lobby-capture-ablation.csv | `averageDisclosureLag` | miss | 0.5293-0.5341 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | metric-split | lobby-capture-ablation.csv | `commentAuthenticity` | miss | 0.2298-0.2470 | 0.48-0.87 | commentAuthenticationShareMean=0.3200 | separate all-comment authenticity from contacted/verified commenter coverage |
| P1 | metric-split | lobby-capture-campaign.csv | `commentAuthenticity` | miss | 0.1898-0.3828 | 0.48-0.87 | commentAuthenticationShareMean=0.3200 | separate all-comment authenticity from contacted/verified commenter coverage |
| P1 | metric-split | lobby-capture-interactions.csv | `commentAuthenticity` | miss | 0.2199-0.2329 | 0.48-0.87 | commentAuthenticationShareMean=0.3200 | separate all-comment authenticity from contacted/verified commenter coverage |
| P1 | metric-split | lobby-capture-sensitivity.csv | `commentAuthenticity` | miss | 0.2218-0.2331 | 0.48-0.87 | commentAuthenticationShareMean=0.3200 | separate all-comment authenticity from contacted/verified commenter coverage |
| P1 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | miss | 0.0000-0.0341 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P1 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | miss | 0.0000-0.0000 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | miss | 0.0000-0.0000 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P1 | model-tuning | lobby-capture-ablation.csv | `largeDonorDependence` | miss | 0.1800-0.1800 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | miss | 0.1800-0.3142 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | miss | 0.1800-0.3095 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | miss | 0.1800-0.3108 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0020-0.0084 | 0.55-0.65 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0020-0.0084 | 0.25-0.40 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0003-0.0760 | 0.55-0.65 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0003-0.0760 | 0.25-0.40 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0010-0.0013 | 0.55-0.65 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0010-0.0013 | 0.25-0.40 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0010-0.0012 | 0.55-0.65 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0010-0.0012 | 0.25-0.40 |  | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | benchmark-review | lobby-capture-interactions.csv | `regulatorQueueBacklog` | miss | 0.4411-0.4657 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P2 | model-tuning | lobby-capture-ablation.csv | `commentCompressionRate` | miss | 0.2747-0.3528 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | miss | 0.0944-0.3672 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-interactions.csv | `commentCompressionRate` | miss | 0.3550-0.3775 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-sensitivity.csv | `commentCompressionRate` | miss | 0.3554-0.3752 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-ablation.csv | `commentUniqueInformationShare` | miss | 0.2669-0.2739 | 0.03-0.20 |  | lower unique-information weight for template-heavy dockets |
| P2 | model-tuning | lobby-capture-campaign.csv | `commentUniqueInformationShare` | miss | 0.2270-0.3801 | 0.03-0.20 |  | lower unique-information weight for template-heavy dockets |
| P2 | model-tuning | lobby-capture-interactions.csv | `commentUniqueInformationShare` | miss | 0.2521-0.2621 | 0.03-0.20 |  | lower unique-information weight for template-heavy dockets |
| P2 | model-tuning | lobby-capture-sensitivity.csv | `commentUniqueInformationShare` | miss | 0.2532-0.2626 | 0.03-0.20 |  | lower unique-information weight for template-heavy dockets |
| P2 | benchmark-review | lobby-capture-ablation.csv | `darkMoneyDirectVisibility` | miss | 0.0000-0.0000 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `donorInfluenceGini` | miss | 0.1214-0.1359 | 0.005-0.015 | fecDonorTop3Share=0.5893 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `donorInfluenceGini` | miss | 0.1271-0.1573 | 0.005-0.015 | fecDonorTop3Share=0.5893 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `donorInfluenceGini` | miss | 0.1308-0.1514 | 0.005-0.015 | fecDonorTop3Share=0.5893 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.0024-0.0455 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.0024-0.0455 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.0000-0.1525 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0000-0.1100 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0000-0.1082 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0002 | 0.40-0.75 |  | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-campaign.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0019 | 0.40-0.75 |  | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0001 | 0.40-0.75 |  | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0001 | 0.40-0.75 |  | separate headcount share from modeled influence intensity |
| P2 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | miss | 0.0000-0.0000 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P2 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | miss | 0.0000-0.0000 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.3735-0.6736 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-interactions.csv | `averageDisclosureLag` | partial | 0.4411-0.6423 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-sensitivity.csv | `averageDisclosureLag` | partial | 0.4471-0.6393 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | benchmark-review | lobby-capture-ablation.csv | `commentSubstantiveUptake` | partial | 0.2563-0.3534 | 0.01-0.35 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5318 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5321 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5311 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.0000-0.1863 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | direct-source-moment | lobby-capture-campaign.csv | `donorInfluenceGini` | partial | 0.0000-0.2233 | 0.005-0.015 | fecDonorTop3Share=0.5893 | replace report-level proxy with top-k donor/client moments from source tables |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.0000-0.1525 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | partial | 0.0000-0.1100 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | partial | 0.0000-0.1082 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1898-0.4692 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | partial | 0.1800-0.3142 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | partial | 0.1800-0.3095 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | partial | 0.1800-0.3108 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9500 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | benchmark-review | lobby-capture-ablation.csv | `publicFinancingCandidateUptake` | partial | 0.1512-0.6368 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.1297-0.6720 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.1171-0.6039 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `regulatorQueueBacklog` | partial | 0.4736-0.5002 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0000-0.0191 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0000-0.0063 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0961-0.1292 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0309-0.1721 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0516-0.1740 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0602-0.1647 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | benchmark-review | lobby-capture-ablation.csv | `voucherResidentParticipation` | partial | 0.0080-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `voucherResidentParticipation` | partial | 0.0080-0.0584 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
