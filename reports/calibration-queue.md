# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `7`
- `scenario-coverage`: `1`
- `scenario-family-split`: `1`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.3378-0.6708 | 0.60-0.80 |  | add or isolate higher-pressure substitution scenarios so the scoped validation family reaches the benchmark floor |
| P3 | scenario-family-split | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.2423-0.6708 | 0.30-0.60 |  | split baseline, substitution-stress, and extreme-stress scenarios before using this benchmark as a single calibration target |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.4675-0.6873 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.4683-0.7005 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `publicFinancingCandidateUptake` | partial | 0.5660-0.5791 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.4350-0.6978 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.4789-0.7005 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6674 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-mechanism-comparison.csv | `regulatorQueueBacklog` | partial | 0.2361-0.6686 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
