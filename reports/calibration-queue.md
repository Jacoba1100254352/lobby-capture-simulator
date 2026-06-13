# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `12`
- `direct-source-moment`: `1`
- `scenario-coverage`: `5`
- `scenario-family-split`: `1`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | direct-source-moment | source-moments.csv | `procurementExPostModificationShare` | source_gap | 0.4220-0.4220 | 0.01-0.05 | procurementExPostModificationShare=0.4220 | broaden the bounded USAspending action panel with representative SAM/FPDS action histories or archived USAspending bulk transaction downloads that support transaction-row, distinct-award, and amount-weighted denominators before treating modification incidence as calibrated |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.3378-0.6708 | 0.60-0.80 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-family-split | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.2423-0.6708 | 0.30-0.60 |  | split baseline, substitution-stress, and extreme-stress scenarios before using this benchmark as a single calibration target |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1674-0.4727 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `influencePreservationRate` | partial | 0.0000-0.4256 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0094-1.0000 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `observedCaptureRate` | partial | 0.0000-0.8916 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.4675-0.6873 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.4683-0.7005 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `publicFinancingCandidateUptake` | partial | 0.5660-0.5791 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.4350-0.6978 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.4789-0.7005 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6674 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6686 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | partial | 0.0226-0.1373 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | partial | 0.0510-0.1772 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | partial | 0.0259-0.1853 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | partial | 0.0260-0.1720 | 0.10-0.70 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
