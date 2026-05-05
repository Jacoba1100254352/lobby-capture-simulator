# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `128`
- Partial: `34`
- Miss: `30`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `52`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `0`, partial `3`, miss `5`, unknown `0`
- `judgmental`: fit `0`, partial `1`, miss `3`, unknown `0`
- `observed`: fit `12`, partial `12`, miss `8`, unknown `0`
- `observed_proxy`: fit `8`, partial `5`, miss `7`, unknown `0`
- `proxy`: fit `29`, partial `12`, miss `3`, unknown `0`
- `sectoral`: fit `0`, partial `0`, miss `4`, unknown `0`
- `synthetic`: fit `27`, partial `1`, miss `0`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1389-0.1848 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0205-0.0596 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.1000-0.3522 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0838-0.1162 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1472-0.2096 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1651-0.2091 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0886-0.0992 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0529-0.5410 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentFloodingIndex | 0.2342-0.2716 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1439-0.1586 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5287-0.5315 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5287-0.5315 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1713-0.1997 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | darkMoneyDirectVisibility | 0.0000-0.0000 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1426-0.2379 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.1845-0.2728 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3164-0.3267 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.1489-0.1524 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5757-0.5804 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.2092-0.3055 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.3685-0.4346 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.1228-0.4331 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.4754-0.4936 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0041-0.1431 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0205-0.0596 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0205-0.0596 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorInfluence | 0.0001-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | voucherResidentParticipation | 0.0080-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingCandidateUptake | 0.0738-0.5594 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.3342-0.3976 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1426-0.2379 | 0.10-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.6309-0.6729 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.1049-0.1337 | 0.10-0.70 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.1000-0.3522 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0838-0.1162 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1472-0.2096 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1651-0.2091 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0886-0.0992 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentFloodingIndex | 0.2342-0.2716 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1439-0.1586 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0529-0.5410 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | captureRateSeedStdDev | 0.0289-0.0553 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortionSeedStdDev | 0.0109-0.0180 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.1239-1.0319 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7485 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0030-0.2795 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0153-0.9988 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0607-0.1826 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.0986-0.3682 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1263-0.2801 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6282 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentFloodingIndex | 0.2343-0.3481 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4691 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6783 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6783 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.4128 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7485 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7485 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | darkMoneyDirectVisibility | 0.0000-0.5318 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0655-0.3942 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.1334-0.4305 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2069-0.5405 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.0887-0.1803 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.5330-0.5956 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.1715-0.3155 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.2221-0.6392 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.0922-0.6569 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.5717 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0072-0.2256 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0030-0.2795 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0030-0.2795 | 0.25-0.40 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | revolvingDoorInfluence | 0.0001-0.0164 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | voucherResidentParticipation | 0.0080-0.0584 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingCandidateUptake | 0.0614-0.5947 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1852-0.5103 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0655-0.3942 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.5104-0.6875 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0341-0.1793 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0153-0.9988 | 0.00-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0607-0.1826 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.0986-0.3682 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1263-0.2801 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentFloodingIndex | 0.2343-0.3481 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4691 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6282 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | captureRateSeedStdDev | 0.0038-0.0739 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortionSeedStdDev | 0.0012-0.0246 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1533-0.4602 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7343 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0047-0.0811 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0180-0.5500 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0521-0.2002 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1074-0.2876 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.1191-0.3159 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0873-0.1017 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0954-0.6643 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentFloodingIndex | 0.2311-0.2402 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1414-0.1577 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4388-0.6403 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4388-0.6403 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1636-0.2093 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7343 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7343 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | darkMoneyDirectVisibility | 0.0000-0.5321 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0377-0.4649 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1713-0.1912 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3102-0.3402 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1457-0.1540 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5734-0.5815 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.3031-0.3077 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.4226-0.4493 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.1173-0.6347 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4048-0.4234 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0080-0.2400 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0047-0.0811 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0047-0.0811 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0001-0.0005 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2325-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.3025-0.4348 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0377-0.4649 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6297-0.6863 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0648-0.2195 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0180-0.5500 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0521-0.2002 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1074-0.2876 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.1191-0.3159 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0873-0.1017 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentFloodingIndex | 0.2311-0.2402 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1414-0.1577 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0954-0.6643 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | captureRateSeedStdDev | 0.0180-0.0689 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortionSeedStdDev | 0.0076-0.0243 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1439-0.1949 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7354 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.0640-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0084-0.0643 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0348-0.4629 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0529-0.1931 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1114-0.2727 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.1211-0.3063 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0882-0.1001 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.0970-0.6453 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentFloodingIndex | 0.2323-0.2386 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1473-0.1607 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4439-0.6372 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4439-0.6372 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1741-0.2052 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7354 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7354 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | darkMoneyDirectVisibility | 0.0000-0.5319 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0394-0.4478 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.1782-0.1919 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3099-0.3293 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1488-0.1540 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5738-0.5815 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.3038-0.3069 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.4199-0.4477 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.1452-0.5938 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4414-0.4543 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0043-0.2157 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0084-0.0643 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0084-0.0643 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0001-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0125-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.1223-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.3122-0.4186 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0394-0.4478 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6297-0.6827 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0734-0.2035 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0348-0.4629 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0529-0.1931 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1114-0.2727 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.1211-0.3063 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0882-0.1001 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentFloodingIndex | 0.2323-0.2386 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1473-0.1607 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.0970-0.6453 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | captureRateSeedStdDev | 0.0221-0.0555 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortionSeedStdDev | 0.0082-0.0209 | 0.00-0.35 | fit | all scenario values inside benchmark range |
