# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `model-tuning`: `1`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P3 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | partial | 0.5796-0.6596 | 0.60-0.80 | fecLargeDonorWeightedShare=0.9457 | inspect remaining campaign/outside rows and tune allocation-to-source concentration only where high-end outside spending is intended |
