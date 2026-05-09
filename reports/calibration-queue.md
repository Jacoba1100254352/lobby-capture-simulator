# Calibration Queue

This queue classifies validation misses and partial overlaps into concrete follow-up actions.

## Category Counts

- `benchmark-review`: `19`
- `direct-source-moment`: `22`
- `model-tuning`: `18`
- `scale-alignment`: `5`
- `scenario-coverage`: `15`

| Priority | Category | Report | Metric | Status | Observed | Benchmark | Source Moment | Action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| P1 | scale-alignment | lobby-capture-ablation.csv | `averageDisclosureLag` | miss | 0.5281-0.5319 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | scale-alignment | lobby-capture-portfolio.csv | `averageDisclosureLag` | miss | 0.5276-0.6357 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P1 | model-tuning | lobby-capture-ablation.csv | `largeDonorDependence` | miss | 0.6639-0.6640 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-campaign.csv | `largeDonorDependence` | miss | 0.6623-0.7484 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-interactions.csv | `largeDonorDependence` | miss | 0.6638-0.7346 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-portfolio.csv | `largeDonorDependence` | miss | 0.6638-0.7325 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | model-tuning | lobby-capture-sensitivity.csv | `largeDonorDependence` | miss | 0.6638-0.7366 | 0.10-0.20 | fecLargeDonorWeightedShare=0.9492 | use source large-donor moments and scale campaign finance influence into report state |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0085-0.0558 | 0.55-0.65 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-ablation.csv | `procurementBias` | miss | 0.0085-0.0558 | 0.25-0.40 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0035-0.2372 | 0.55-0.65 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-campaign.csv | `procurementBias` | miss | 0.0035-0.2372 | 0.25-0.40 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0044-0.0965 | 0.55-0.65 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-interactions.csv | `procurementBias` | miss | 0.0044-0.0965 | 0.25-0.40 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-portfolio.csv | `procurementBias` | miss | 0.0052-0.0894 | 0.55-0.65 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-portfolio.csv | `procurementBias` | miss | 0.0052-0.0894 | 0.25-0.40 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0053-0.0785 | 0.55-0.65 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | lobby-capture-sensitivity.csv | `procurementBias` | miss | 0.0053-0.0785 | 0.25-0.40 | procurementAmountWeightedSingleBidShare=0.0000 | use USAspending/SAM/FPDS bridge moments for single-bid awards, ex-post modifications, UEI/PIID coverage, and recipient concentration |
| P1 | direct-source-moment | source-moments.csv | `procurementExPostModificationShare` | miss | 0.0000-0.0000 | 0.01-0.05 | procurementExPostModificationShare=0.0000 | fill SAM/FPDS modification fields and compare ex-post modification exposure against the procurement bridge target |
| P1 | direct-source-moment | source-moments.csv | `procurementSingleBidShare` | miss | 0.0000-0.0000 | 0.10-0.25 | procurementSingleBidShare=0.0000 | fill SAM/FPDS competition fields and compare single-bid exposure against the procurement bridge target |
| P1 | benchmark-review | lobby-capture-ablation.csv | `publicFinancingCandidateUptake` | miss | 0.0738-0.5594 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-ablation.csv | `regulatorQueueBacklog` | miss | 0.4739-0.4896 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-interactions.csv | `regulatorQueueBacklog` | miss | 0.4043-0.4224 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-portfolio.csv | `regulatorQueueBacklog` | miss | 0.4430-0.4592 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P1 | benchmark-review | lobby-capture-sensitivity.csv | `regulatorQueueBacklog` | miss | 0.4415-0.4554 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P2 | benchmark-review | source-moments.csv | `darkMoneyDirectVisibility` | miss | 0.0000-0.0000 | 0.02-0.10 |  | decide whether the benchmark applies to this scenario family |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `donorInfluenceGini` | miss | 0.1709-0.1980 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `donorInfluenceGini` | miss | 0.1634-0.2152 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-portfolio.csv | `donorInfluenceGini` | miss | 0.1705-0.2079 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `donorInfluenceGini` | miss | 0.1741-0.2012 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.0249-0.1463 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `hiddenInfluenceShare` | miss | 0.0249-0.1463 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | miss | 0.0006-0.3146 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2668 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2668 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.0302-0.2529 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `hiddenInfluenceShare` | miss | 0.0302-0.2529 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2704 | 0.60-0.80 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `hiddenInfluenceShare` | miss | 0.0000-0.2704 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P2 | direct-source-moment | lobby-capture-ablation.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0002 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | replace fixture rows with a documented personnel/export panel and keep headcount share separate from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-campaign.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0165 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | replace fixture rows with a documented personnel/export panel and keep headcount share separate from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-interactions.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0006 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | replace fixture rows with a documented personnel/export panel and keep headcount share separate from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-portfolio.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0004 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | replace fixture rows with a documented personnel/export panel and keep headcount share separate from modeled influence intensity |
| P2 | direct-source-moment | lobby-capture-sensitivity.csv | `revolvingDoorInfluence` | miss | 0.0001-0.0003 | 0.40-0.75 | revolvingDoorFormerOfficialShare=0.7857 | replace fixture rows with a documented personnel/export panel and keep headcount share separate from modeled influence intensity |
| P2 | model-tuning | lobby-capture-portfolio.csv | `sanctionRate` | miss | 0.0155-0.1184 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P2 | scenario-coverage | lobby-capture-ablation.csv | `venueSubstitutionRate` | miss | 0.0000-0.0432 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-campaign.csv | `venueSubstitutionRate` | miss | 0.0000-0.0801 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-interactions.csv | `venueSubstitutionRate` | miss | 0.0000-0.0883 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-portfolio.csv | `venueSubstitutionRate` | miss | 0.0000-0.0433 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P2 | scenario-coverage | lobby-capture-sensitivity.csv | `venueSubstitutionRate` | miss | 0.0000-0.0540 | 0.10-0.70 |  | add cooling-off and advisory-lobbying stress cases |
| P3 | scale-alignment | lobby-capture-campaign.csv | `averageDisclosureLag` | partial | 0.3735-0.6761 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-interactions.csv | `averageDisclosureLag` | partial | 0.4405-0.6378 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | scale-alignment | lobby-capture-sensitivity.csv | `averageDisclosureLag` | partial | 0.4424-0.6418 | 0.20-0.45 |  | separate current-public-visibility lag from historical age of archived filings |
| P3 | model-tuning | lobby-capture-ablation.csv | `commentCompressionRate` | partial | 0.4526-0.5358 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | model-tuning | lobby-capture-campaign.csv | `commentCompressionRate` | partial | 0.2753-0.7876 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | model-tuning | lobby-capture-portfolio.csv | `commentCompressionRate` | partial | 0.4390-0.5452 | 0.50-0.99 | commentTemplateShareMean=0.4600 | raise compression under anti-astroturf and duplicate-detection tooling |
| P3 | benchmark-review | lobby-capture-interactions.csv | `crossVenueDetectionIndex` | partial | 0.0754-0.9403 | 0.00-0.90 |  | treat as a synthetic portfolio capability until linked source coverage is measured |
| P3 | model-tuning | lobby-capture-ablation.csv | `detectionRate` | partial | 0.1184-0.3503 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-campaign.csv | `detectionRate` | partial | 0.1244-0.6856 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-interactions.csv | `detectionRate` | partial | 0.1047-0.5093 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-portfolio.csv | `detectionRate` | partial | 0.1588-0.5029 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `detectionRate` | partial | 0.1500-0.5505 | 0.05-0.21 |  | increase detection response under enforcement-heavy regimes |
| P3 | direct-source-moment | lobby-capture-campaign.csv | `donorInfluenceGini` | partial | 0.0000-0.4150 | 0.005-0.015 | fecDonorTop3Share=0.3747 | replace report-level proxy with top-k donor/client moments from source tables |
| P3 | scenario-coverage | lobby-capture-campaign.csv | `hiddenInfluenceShare` | partial | 0.0006-0.3146 | 0.30-0.60 |  | add stress cases where reforms bind enough to force hidden substitution |
| P3 | benchmark-review | lobby-capture-campaign.csv | `influencePreservationRate` | partial | 0.1671-0.4647 | 0.20-1.50 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `observedCaptureRate` | partial | 0.0000-0.9988 | 0.00-0.80 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `publicFinancingCandidateUptake` | partial | 0.0616-0.5947 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `publicFinancingCandidateUptake` | partial | 0.2324-0.6808 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `publicFinancingCandidateUptake` | partial | 0.1030-0.6802 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `publicFinancingCandidateUptake` | partial | 0.1223-0.6808 | 0.57-0.86 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `regulatorQueueBacklog` | partial | 0.1171-0.5721 | 0.50-0.75 |  | decide whether the benchmark applies to this scenario family |
| P3 | model-tuning | lobby-capture-ablation.csv | `sanctionRate` | partial | 0.0050-0.0978 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-campaign.csv | `sanctionRate` | partial | 0.0078-0.1831 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-interactions.csv | `sanctionRate` | partial | 0.0033-0.2127 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | model-tuning | lobby-capture-sensitivity.csv | `sanctionRate` | partial | 0.0057-0.1833 | 0.003-0.015 |  | raise sanction incidence after detection or narrow benchmark to campaign filer cases |
| P3 | benchmark-review | lobby-capture-ablation.csv | `voucherResidentParticipation` | partial | 0.0080-0.0528 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-campaign.csv | `voucherResidentParticipation` | partial | 0.0080-0.0584 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-interactions.csv | `voucherResidentParticipation` | partial | 0.0237-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-portfolio.csv | `voucherResidentParticipation` | partial | 0.0094-0.0612 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
| P3 | benchmark-review | lobby-capture-sensitivity.csv | `voucherResidentParticipation` | partial | 0.0125-0.0640 | 0.03-0.08 |  | decide whether the benchmark applies to this scenario family |
