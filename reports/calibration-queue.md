# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `14`
- `direct-source-moment`: `3`
- `model-tuning`: `18`
- `scale-alignment`: `1`
- `scenario-coverage`: `15`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | model-tuning | lobby-capture-ablation.csv | `largeDonorDependence` | miss | 0.5765-0.5766 | 0.60-0.80 | fecLargeDonorWeightedShare=0.8692 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | direct-source-moment | source-moments.csv | `procurementAgencyTop1Share` | miss | 1.0000-1.0000 | 0.55-0.65 | procurementAgencyTop1Share=1.0000 | expand the procurement source panel beyond the EPA slice before treating agency concentration as representative |
| P1 | direct-source-moment | source-moments.csv | `procurementExPostModificationShare` | miss | 1.0000-1.0000 | 0.01-0.05 | procurementExPostModificationShare=1.0000 | fill SAM/FPDS modification fields and compare ex-post modification exposure against the procurement bridge target |
| P1 | direct-source-moment | source-moments.csv | `procurementRecipientTop3Share` | miss | 0.1723-0.1723 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | compare recipient concentration by agency, award type, and fiscal year rather than treating the EPA slice as a universal target |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.1458-0.3182 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.0581-0.5047 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0261-0.5174 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.1545-0.5021 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0296-0.5163 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.2315-0.4850 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-ablation.csv | `commentCompressionRate` | partial | 0.4533-0.5425 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.2776-0.8066 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | model-tuning | lobby-capture-portfolio.csv | `commentCompressionRate` | partial | 0.4525-0.5507 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.1272-0.3563 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.0725-0.5825 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | partial | 0.0480-0.4673 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-portfolio.csv | `detectionRate` | partial | 0.1706-0.4449 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | partial | 0.1257-0.4267 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | partial | 0.1458-0.3182 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.0581-0.5047 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | partial | 0.0261-0.5174 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | partial | 0.1545-0.5021 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | partial | 0.0296-0.5163 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1668-0.4754 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | partial | 0.5760-0.6615 | 0.60-0.80 | fecLargeDonorWeightedShare=0.8692 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | partial | 0.5765-0.6492 | 0.60-0.80 | fecLargeDonorWeightedShare=0.8692 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | model-tuning | lobby-capture-portfolio.csv | `largeDonorDependence` | partial | 0.5764-0.6466 | 0.60-0.80 | fecLargeDonorWeightedShare=0.8692 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | partial | 0.5765-0.6498 | 0.60-0.80 | fecLargeDonorWeightedShare=0.8692 | use source large-donor moments and scale campaign finance influence into report state |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0394-1.0000 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-ablation.csv | `publicFinancingCandidateUptake` | partial | 0.0878-0.5734 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.0756-0.6840 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.2462-0.6948 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.1170-0.6942 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.1363-0.6948 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6678 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0013-0.0250 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0003-0.0447 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0007-0.0347 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | partial | 0.0061-0.0412 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0005-0.0286 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0395-0.1554 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0063-0.1883 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0054-0.2112 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-portfolio.csv | `venueSubstitutionRate` | partial | 0.0382-0.1989 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0145-0.2036 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | benchmark-review | lobby-capture-ablation.csv | `voucherResidentParticipation` | partial | 0.0080-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `voucherResidentParticipation` | partial | 0.0080-0.0612 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `voucherResidentParticipation` | partial | 0.0094-0.0612 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `voucherResidentParticipation` | partial | 0.0125-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
