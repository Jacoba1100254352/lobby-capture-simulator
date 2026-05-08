# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `221`
- Partial: `37`
- Miss: `42`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `90`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `0`, partial `4`, miss `6`, unknown `0`
- `judgmental`: fit `0`, partial `1`, miss `4`, unknown `0`
- `observed`: fit `15`, partial `12`, miss `13`, unknown `0`
- `observed_proxy`: fit `20`, partial `6`, miss `9`, unknown `0`
- `proxy`: fit `47`, partial `13`, miss `5`, unknown `0`
- `sectoral`: fit `5`, partial `0`, miss `5`, unknown `0`
- `synthetic`: fit `44`, partial `1`, miss `0`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1534-0.2363 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6638-0.6640 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0461-0.0886 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.2472-0.5597 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0888-0.1246 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.2159-0.2929 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.2063-0.2596 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0898-0.1000 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0651-0.5549 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentFloodingIndex | 0.2327-0.2690 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1460-0.1601 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.3238-0.4938 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5062-0.6762 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.3057-0.3286 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1399-0.2870 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1356-0.3766 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5270-0.5329 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5270-0.5329 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1693-0.1927 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6638-0.6640 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6638-0.6640 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | darkMoneyDirectVisibility | 0.0000-0.0000 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1433-0.2392 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.1784-0.2643 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3163-0.3336 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.1465-0.1524 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5731-0.5798 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.2108-0.3061 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.3778-0.4396 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.1769-0.6238 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.4804-0.4951 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0084-0.2313 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0461-0.0886 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0461-0.0886 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorInfluence | 0.0001-0.0003 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | voucherResidentParticipation | 0.0080-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingCandidateUptake | 0.0738-0.5594 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.3353-0.4021 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1433-0.2392 | 0.10-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.6281-0.6730 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.1038-0.1343 | 0.10-0.70 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.2472-0.5597 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0888-0.1246 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.2159-0.2929 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.2063-0.2596 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0898-0.1000 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentFloodingIndex | 0.2327-0.2690 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1460-0.1601 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0651-0.5549 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | captureRateSeedStdDev | 0.0454-0.0654 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortionSeedStdDev | 0.0140-0.0219 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.3238-0.4938 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5062-0.6762 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.3057-0.3286 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1399-0.2870 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1356-0.3766 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentNetworkLoad | 0.1309-0.2072 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueShiftNetworkLoad | 0.2932-0.3582 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.1301-1.1316 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7482 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0125-0.3752 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.1356-0.9988 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0659-0.1828 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1695-0.4231 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1671-0.3278 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6471 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentFloodingIndex | 0.2335-0.3485 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4694 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.3232-0.7181 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2819-0.6768 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.1934-0.3339 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0622-0.5488 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1017-0.6586 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6748 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6748 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.4025 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7482 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7482 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | darkMoneyDirectVisibility | 0.0000-0.5321 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0657-0.3935 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.1408-0.4207 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2103-0.5426 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.0882-0.1795 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.5329-0.5962 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.1704-0.3152 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.2257-0.6414 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.1719-0.9856 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.5715 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0122-0.3466 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0125-0.3752 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0125-0.3752 | 0.25-0.40 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | revolvingDoorInfluence | 0.0001-0.0168 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | voucherResidentParticipation | 0.0080-0.0584 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingCandidateUptake | 0.0616-0.5947 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1894-0.5092 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0657-0.3935 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.5095-0.6815 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0342-0.1791 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.1356-0.9988 | 0.00-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0659-0.1828 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1695-0.4231 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1671-0.3278 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentFloodingIndex | 0.2335-0.3485 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4694 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6471 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | captureRateSeedStdDev | 0.0042-0.0614 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortionSeedStdDev | 0.0015-0.0206 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.3232-0.7181 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2819-0.6768 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.1934-0.3339 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0622-0.5488 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1017-0.6586 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentNetworkLoad | 0.0000-0.5228 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueShiftNetworkLoad | 0.1689-0.4326 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1571-0.6137 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6637-0.7340 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0189-0.0987 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0640-0.7133 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0534-0.2030 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1512-0.3494 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.1466-0.3623 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0865-0.1016 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.1108-0.6785 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentFloodingIndex | 0.2306-0.2402 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1411-0.1571 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.2407-0.6409 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3591-0.7593 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.2934-0.3157 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1340-0.1535 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.0998-0.3539 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4396-0.6437 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4396-0.6437 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1618-0.2053 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6637-0.7340 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6637-0.7340 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | darkMoneyDirectVisibility | 0.0000-0.5321 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0389-0.4588 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1725-0.1892 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3094-0.3424 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1450-0.1542 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5720-0.5812 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.3038-0.3082 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.4218-0.4492 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.1147-0.7153 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4065-0.4271 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0100-0.2907 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0189-0.0987 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0189-0.0987 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0001-0.0006 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2325-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.3125-0.4311 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0389-0.4588 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6282-0.6850 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0675-0.2158 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0640-0.7133 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0534-0.2030 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1512-0.3494 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.1466-0.3623 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0865-0.1016 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentFloodingIndex | 0.2306-0.2402 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1411-0.1571 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.1108-0.6785 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | captureRateSeedStdDev | 0.0275-0.0718 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortionSeedStdDev | 0.0108-0.0267 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.2407-0.6409 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3591-0.7593 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.2934-0.3157 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1340-0.1535 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.0998-0.3539 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentNetworkLoad | 0.1224-0.1412 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueShiftNetworkLoad | 0.2068-0.4556 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | lobbySpendPerContest | 0.1666-0.4183 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7329 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | voucherParticipation | 0.0300-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0509-0.0997 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.2686-0.6461 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0950-0.2044 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.2231-0.3500 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.2095-0.3622 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0851-0.1016 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.3540-0.6319 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentFloodingIndex | 0.2325-0.2707 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1498-0.1620 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.3266-0.5190 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.4810-0.6734 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.2970-0.3165 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1450-0.2514 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1469-0.3709 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.5256-0.6390 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.5256-0.6390 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | donorInfluenceGini | 0.1629-0.2022 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7329 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7329 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | darkMoneyDirectVisibility | 0.0000-0.5301 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.1604-0.4599 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | commentReviewBurden | 0.1722-0.2536 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | templateCommentSaturation | 0.3171-0.3358 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentUniqueInformationShare | 0.1463-0.1522 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalClaimCredibility | 0.5697-0.5795 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentSubstantiveUptake | 0.2296-0.3072 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentCompressionRate | 0.3765-0.4490 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | detectionRate | 0.4110-0.7147 | 0.05-0.21 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | regulatorQueueBacklog | 0.4514-0.4639 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | sanctionRate | 0.0780-0.3053 | 0.003-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0509-0.0997 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0509-0.0997 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorInfluence | 0.0001-0.0010 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | voucherResidentParticipation | 0.0101-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | publicFinancingCandidateUptake | 0.1175-0.5594 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | influencePreservationRate | 0.3262-0.4302 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.1604-0.4599 | 0.10-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentAuthenticity | 0.6254-0.6716 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueSubstitutionRate | 0.0724-0.2091 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.2686-0.6461 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0950-0.2044 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.2231-0.3500 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.2095-0.3622 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0851-0.1016 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentFloodingIndex | 0.2325-0.2707 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1498-0.1620 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.3540-0.6319 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | captureRateSeedStdDev | 0.0439-0.0608 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortionSeedStdDev | 0.0137-0.0210 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.3266-0.5190 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.4810-0.6734 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.2970-0.3165 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1450-0.2514 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1469-0.3709 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentNetworkLoad | 0.1065-0.1837 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueShiftNetworkLoad | 0.2936-0.4532 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1505-0.2379 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7360 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.0640-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0260-0.0811 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0952-0.5781 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0540-0.2020 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1579-0.3443 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.1480-0.3601 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0891-0.1023 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.1099-0.6573 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentFloodingIndex | 0.2321-0.2373 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1454-0.1568 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.2436-0.6365 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3635-0.7564 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.2956-0.3144 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1323-0.1519 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.0994-0.3548 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4390-0.6379 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4390-0.6379 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1666-0.1993 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7360 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7360 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | darkMoneyDirectVisibility | 0.0000-0.5319 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0392-0.4561 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.1725-0.1853 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3155-0.3302 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1486-0.1525 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5739-0.5798 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.3044-0.3073 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.4239-0.4490 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.2181-0.7043 | 0.05-0.21 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4435-0.4583 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0124-0.2800 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0260-0.0811 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0260-0.0811 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0001-0.0003 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0125-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.1223-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.3146-0.4253 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0392-0.4561 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6282-0.6812 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0738-0.2069 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0952-0.5781 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0540-0.2020 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1579-0.3443 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.1480-0.3601 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0891-0.1023 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentFloodingIndex | 0.2321-0.2373 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1454-0.1568 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.1099-0.6573 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | captureRateSeedStdDev | 0.0362-0.0758 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortionSeedStdDev | 0.0126-0.0242 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.2436-0.6365 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3635-0.7564 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.2956-0.3144 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1323-0.1519 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.0994-0.3548 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentNetworkLoad | 0.1278-0.1420 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueShiftNetworkLoad | 0.2123-0.4518 | 0.00-0.85 | fit | all scenario values inside benchmark range |
