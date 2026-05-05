# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `18`
- `direct-source-moment`: `16`
- `model-tuning`: `14`
- `scale-alignment`: `4`
- `scenario-coverage`: `11`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | scale-alignment | lobby-capture-ablation.csv | `averageDisclosureLag` | miss | 0.5282-0.5342 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | model-tuning | lobby-capture-ablation.csv | `largeDonorDependence` | miss | 0.6638-0.6641 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | miss | 0.6623-0.7391 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | miss | 0.6637-0.7317 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | miss | 0.6637-0.7306 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0020-0.0076 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0020-0.0076 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0003-0.0740 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0003-0.0740 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0010-0.0013 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0010-0.0013 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0010-0.0012 | 0.55-0.65 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0010-0.0012 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | add USAspending-style top-recipient and top-agency concentration moments |
| P1 | benchmark-review | lobby-capture-ablation.csv | `regulatorQueueBacklog` | miss | 0.4710-0.4871 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-interactions.csv | `regulatorQueueBacklog` | miss | 0.4095-0.4367 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-sensitivity.csv | `regulatorQueueBacklog` | miss | 0.4558-0.4710 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P2 | model-tuning | lobby-capture-ablation.csv | `commentCompressionRate` | miss | 0.3648-0.4319 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-interactions.csv | `commentCompressionRate` | miss | 0.3973-0.4192 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | model-tuning | lobby-capture-sensitivity.csv | `commentCompressionRate` | miss | 0.3934-0.4114 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P2 | benchmark-review | lobby-capture-ablation.csv | `darkMoneyDirectVisibility` | miss | 0.0000-0.0000 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `donorInfluenceGini` | miss | 0.1796-0.2114 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `donorInfluenceGini` | miss | 0.1602-0.2193 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `donorInfluenceGini` | miss | 0.1703-0.2030 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.1053-0.2045 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.0301-0.3305 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0151-0.3319 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0164-0.3369 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0002 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.8000 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-campaign.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0018 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.8000 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0001 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.8000 | separate headcount share from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `revolvingDoorInfluence` | miss | 0.0000-0.0001 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.8000 | separate headcount share from modeled influence intensity |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.3735-0.6743 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-interactions.csv | `averageDisclosureLag` | partial | 0.4435-0.6451 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-sensitivity.csv | `averageDisclosureLag` | partial | 0.4468-0.6375 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.1970-0.5088 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-campaign.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5315 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5324 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `darkMoneyDirectVisibility` | partial | 0.0000-0.5319 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.0438-0.1838 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.0375-0.2163 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | direct-source-moment | lobby-capture-campaign.csv | `donorInfluenceGini` | partial | 0.0000-0.2692 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.0301-0.3305 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | partial | 0.0151-0.3319 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | partial | 0.0164-0.3369 | 0.10-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1852-0.4692 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-ablation.csv | `publicFinancingCandidateUptake` | partial | 0.0738-0.5594 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.0617-0.5947 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.2329-0.6807 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.2437-0.6808 | 0.25-0.95 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.1171-0.5568 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0003-0.0266 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0016-0.0172 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0007-0.0160 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0019-0.0133 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | benchmark-review | lobby-capture-campaign.csv | `technicalClaimCredibility` | partial | 0.5357-0.6013 | 0.20-0.60 |  | decide whether the benchmark applies to this scenario family |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0944-0.1305 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0309-0.1658 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0530-0.1710 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0599-0.1693 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | benchmark-review | lobby-capture-ablation.csv | `voucherResidentParticipation` | partial | 0.0080-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `voucherResidentParticipation` | partial | 0.0080-0.0584 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
