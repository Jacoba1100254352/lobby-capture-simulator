# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `12`
- `direct-source-moment`: `3`
- `model-tuning`: `15`
- `scale-alignment`: `1`
- `scenario-coverage`: `6`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | direct-source-moment | source-moments.csv | `procurementAgencyTop1Share` | source_gap | 0.6680-0.6680 | 0.55-0.65 | procurementAgencyTop1Share=0.6680 | replace the bounded USAspending concentration panel with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated |
| P1 | direct-source-moment | source-moments.csv | `procurementExPostModificationShare` | source_gap | 0.3111-0.3111 | 0.01-0.05 | procurementExPostModificationShare=0.3111 | broaden the bounded USAspending action panel with representative SAM/FPDS action histories before treating modification incidence as calibrated |
| P2 | direct-source-moment | source-moments.csv | `darkMoneyDirectVisibility` | source_gap | 0.2043-0.2043 | 0.00-0.10 | darkMoneyDirectVisibility=0.2043 | replace thin proxy rows with direct hidden-donor or nonprofit-routing source records; keep electioneering rows separate from hidden-donor evidence |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.2312-0.5230 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.3103-0.8318 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `commentCompressionRate` | partial | 0.4524-0.5853 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.1147-0.3413 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.0725-0.5613 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | partial | 0.0480-0.4380 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `detectionRate` | partial | 0.1016-0.3381 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-portfolio.csv | `detectionRate` | partial | 0.1465-0.3747 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | partial | 0.1162-0.3900 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.3378-0.6708 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.2423-0.6708 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1674-0.4727 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `influencePreservationRate` | partial | 0.0000-0.4256 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | partial | 0.5585-0.6923 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9457 | inspect remaining campaign/outside rows and tune allocation-to-source concentration only where high-end outside spending is intended |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0094-1.0000 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `observedCaptureRate` | partial | 0.0000-0.8916 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.4726-0.6889 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.4699-0.7028 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `publicFinancingCandidateUptake` | partial | 0.5673-0.5813 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.4397-0.7019 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.4834-0.7028 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6674 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6686 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0006-0.0219 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0006-0.0444 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0000-0.0293 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `sanctionRate` | partial | 0.0006-0.0188 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | partial | 0.0033-0.0310 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0005-0.0290 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0226-0.1373 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0510-0.1772 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0259-0.1853 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0260-0.1720 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
