# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `12`
- `direct-source-moment`: `4`
- `model-tuning`: `15`
- `scale-alignment`: `1`
- `scenario-coverage`: `10`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | direct-source-moment | source-moments.csv | `procurementAgencyTop1Share` | source_gap | 1.0000-1.0000 | 0.55-0.65 | procurementAgencyTop1Share=1.0000 | expand the procurement source panel beyond the EPA slice before treating agency concentration as representative |
| P1 | direct-source-moment | source-moments.csv | `procurementExPostModificationShare` | source_gap | 0.0000-0.0000 | 0.01-0.05 | procurementExPostModificationShare=0.0000 | fill SAM/FPDS modification fields and compare ex-post modification exposure against the procurement bridge target |
| P1 | direct-source-moment | source-moments.csv | `procurementRecipientTop3Share` | source_gap | 0.1723-0.1723 | 0.25-0.40 | procurementRecipientTop3Share=0.1723 | compare recipient concentration by agency, award type, and fiscal year rather than treating the EPA slice as a universal target |
| P2 | direct-source-moment | source-moments.csv | `darkMoneyDirectVisibility` | source_gap | 0.2028-0.2028 | 0.00-0.10 | darkMoneyDirectVisibility=0.2028 | replace thin proxy rows with direct hidden-donor, electioneering, or nonprofit-routing source records |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.2422-0.4791 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0096-0.4638 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-mechanism-comparison.csv | `hiddenInfluenceShare` | miss | 0.0000-0.3886 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.1211-0.4273 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0118-0.4547 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.2312-0.4850 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.3103-0.8318 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `commentCompressionRate` | partial | 0.4524-0.5855 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.1153-0.3400 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.0725-0.5550 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | partial | 0.0480-0.4380 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `detectionRate` | partial | 0.1016-0.3369 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-portfolio.csv | `detectionRate` | partial | 0.1465-0.3743 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | partial | 0.1162-0.3905 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.2422-0.4791 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1674-0.4727 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `influencePreservationRate` | partial | 0.0000-0.4256 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | partial | 0.5702-0.6427 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9485 | inspect remaining campaign/outside rows and tune allocation-to-source concentration only where high-end outside spending is intended |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0094-1.0000 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `observedCaptureRate` | partial | 0.0000-0.8916 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.4708-0.6877 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.4684-0.7012 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `publicFinancingCandidateUptake` | partial | 0.5658-0.5798 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.4381-0.7003 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.4818-0.7012 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6676 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6686 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0006-0.0222 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0006-0.0444 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0000-0.0293 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `sanctionRate` | partial | 0.0006-0.0184 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | partial | 0.0033-0.0310 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0005-0.0290 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0226-0.1374 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0510-0.1694 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0259-0.1847 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0260-0.1728 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
