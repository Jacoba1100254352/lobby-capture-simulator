# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `41`
- Partial: `24`
- Miss: `55`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `16`, partial `0`, miss `4`, unknown `0`
- `inferred`: fit `0`, partial `0`, miss `8`, unknown `0`
- `judgmental`: fit `0`, partial `0`, miss `4`, unknown `0`
- `observed`: fit `11`, partial `7`, miss `14`, unknown `0`
- `observed_proxy`: fit `4`, partial `4`, miss `12`, unknown `0`
- `proxy`: fit `10`, partial `13`, miss `9`, unknown `0`
- `sectoral`: fit `0`, partial `0`, miss `4`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1320-0.1406 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.0002-0.0003 | 0.10-0.95 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0020-0.0083 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.4726-0.4735 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.4726-0.4735 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1496-0.1684 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.0002-0.0003 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.0002-0.0003 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | darkMoneyTraceability | 0.8395-0.8891 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.0024-0.0455 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.5672-0.6719 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3923-0.4038 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.2873-0.2930 | 0.03-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5437-0.5547 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.1616-0.2519 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.2505-0.3239 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.0000-0.0359 | 0.05-0.21 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.5469-0.5594 | 0.50-0.75 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0000-0.0209 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0020-0.0083 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0020-0.0083 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorInfluence | 0.0000-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingShare | 0.0000-0.6200 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.3305-0.4052 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.0024-0.0455 | 0.10-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.2570-0.2725 | 0.48-0.87 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.0961-0.1292 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.1051-0.6051 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.0002-0.0040 | 0.10-0.95 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0003-0.0765 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.5867 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.5867 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.2352 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.0002-0.0040 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.0002-0.0040 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | darkMoneyTraceability | 0.4426-0.8931 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0000-0.1517 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.3854-1.0000 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2121-0.6497 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.1610-0.3744 | 0.03-0.20 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.4775-0.5739 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.0036-0.2932 | 0.01-0.35 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.1163-0.3034 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.0000-0.2034 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.6157 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0000-0.0063 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0003-0.0765 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0003-0.0765 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorInfluence | 0.0000-0.0019 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingShare | 0.0000-0.6600 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1898-0.4692 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0000-0.1517 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.0943-0.3701 | 0.48-0.87 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0308-0.1721 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1442-0.1595 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.0003-0.0004 | 0.10-0.95 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0010-0.0013 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.3833-0.5816 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.3833-0.5816 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1472-0.1786 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.0003-0.0004 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.0003-0.0004 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | darkMoneyTraceability | 0.7378-0.9532 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0000-0.1100 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.5133-0.5496 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3567-0.3796 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.2994-0.3103 | 0.03-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5526-0.5601 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.2584-0.2748 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.2855-0.3103 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.0000-0.0000 | 0.05-0.21 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.5011-0.5202 | 0.50-0.75 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0000-0.0000 | 0.003-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0010-0.0013 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0010-0.0013 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0000-0.0001 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.03-0.08 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | publicFinancingShare | 0.2170-0.7750 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.2582-0.3538 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0000-0.1100 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.2805-0.2958 | 0.48-0.87 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0516-0.1740 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1323-0.1358 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.0002-0.0003 | 0.10-0.95 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0010-0.0012 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.3844-0.5816 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.3844-0.5816 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1500-0.1711 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.0002-0.0003 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.0002-0.0003 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | darkMoneyTraceability | 0.7367-0.9516 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0000-0.1082 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.5256-0.5485 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3607-0.3767 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.2990-0.3081 | 0.03-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5504-0.5589 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.2571-0.2702 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.2917-0.3041 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.0000-0.0000 | 0.05-0.21 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.5328-0.5557 | 0.50-0.75 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0000-0.0000 | 0.003-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0010-0.0012 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0010-0.0012 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0000-0.0001 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.2240-0.8000 | 0.03-0.08 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingShare | 0.2170-0.7750 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.2691-0.3475 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0000-0.1082 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.2825-0.2933 | 0.48-0.87 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0602-0.1647 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
