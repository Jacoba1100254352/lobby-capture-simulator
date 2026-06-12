# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `12`
- `direct-source-moment`: `3`
- `model-tuning`: `7`
- `scenario-coverage`: `5`
- `scenario-family-split`: `1`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | direct-source-moment | source-moments.csv | `procurementAgencyTop1Share` | source_gap | 0.4609-0.4609 | 0.55-0.65 | procurementAgencyTop1Share=0.4609 | replace the bounded USAspending concentration panel with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated |
| P1 | direct-source-moment | source-moments.csv | `procurementExPostModificationShare` | source_gap | 0.4220-0.4220 | 0.01-0.05 | procurementExPostModificationShare=0.4220 | broaden the bounded USAspending action panel with representative SAM/FPDS action histories that support transaction-row, distinct-award, and amount-weighted denominators before treating modification incidence as calibrated |
| P1 | direct-source-moment | source-moments.csv | `procurementRecipientTop3Share` | source_gap | 0.1876-0.1876 | 0.25-0.40 | procurementRecipientTop3Share=0.1876 | compare recipient concentration against the bounded procurement concentration panel, then broaden by award type and fiscal year before treating it as calibrated |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.3378-0.6708 | 0.60-0.80 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-family-split | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.2423-0.6708 | 0.30-0.60 |  | split baseline, substitution-stress, and extreme-stress scenarios before using this benchmark as a single calibration target |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1674-0.4727 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `influencePreservationRate` | partial | 0.0000-0.4256 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | partial | 0.5576-0.6916 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9457 | inspect remaining campaign/outside rows and tune allocation-to-source concentration only where high-end outside spending is intended |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0094-1.0000 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `observedCaptureRate` | partial | 0.0000-0.8916 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.4728-0.6890 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.4701-0.7029 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `publicFinancingCandidateUptake` | partial | 0.5675-0.5814 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.4399-0.7020 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.4836-0.7029 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6674 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6686 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0006-0.0219 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0006-0.0444 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0000-0.0293 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-mechanism-comparison.csv | `sanctionRate` | partial | 0.0006-0.0188 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | partial | 0.0033-0.0310 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0005-0.0290 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0226-0.1373 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0510-0.1772 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0259-0.1853 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0260-0.1720 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
