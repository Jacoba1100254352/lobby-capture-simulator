# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `241`
- Partial: `30`
- Miss: `49`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `101`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `0`, partial `0`, miss `6`, unknown `0`
- `judgmental`: fit `2`, partial `3`, miss `0`, unknown `0`
- `observed`: fit `15`, partial `18`, miss `14`, unknown `0`
- `observed_proxy`: fit `20`, partial `0`, miss `10`, unknown `0`
- `proxy`: fit `40`, partial `7`, miss `14`, unknown `0`
- `sectoral`: fit `5`, partial `0`, miss `5`, unknown `0`
- `synthetic`: fit `58`, partial `2`, miss `0`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1314-0.1688 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0085-0.0558 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.0194-0.2406 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0403-0.0811 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1296-0.2006 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1124-0.1899 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0837-0.0973 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0461-0.5306 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1445-0.1547 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.2553-0.4545 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5455-0.7447 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.3354-0.3553 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1470-0.3051 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1879-0.4293 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | crossVenueDetectionIndex | 0.4950-0.7538 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | participationProtectionIndex | 0.3432-0.6696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | speechRestrictionRisk | 0.1549-0.3223 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5281-0.5319 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5281-0.5319 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1709-0.1980 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.0249-0.1463 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.1654-0.2535 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3142-0.3256 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.1475-0.1520 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5672-0.5798 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.2138-0.3112 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.4526-0.5358 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.1184-0.3503 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.4739-0.4896 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0050-0.0978 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0085-0.0558 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0085-0.0558 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorInfluence | 0.0001-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | voucherResidentParticipation | 0.0080-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingCandidateUptake | 0.0738-0.5594 | 0.57-0.86 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.2364-0.3257 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.0249-0.1463 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.6305-0.6736 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.0000-0.0432 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.0194-0.2406 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0403-0.0811 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1296-0.2006 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1124-0.1899 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0837-0.0973 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1445-0.1547 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0461-0.5306 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | captureRateSeedStdDev | 0.0150-0.0520 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortionSeedStdDev | 0.0061-0.0167 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.2553-0.4545 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5455-0.7447 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | crossVenueDetectionIndex | 0.4950-0.7538 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | participationProtectionIndex | 0.3432-0.6696 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | speechRestrictionRisk | 0.1549-0.3223 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.3354-0.3553 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1470-0.3051 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1879-0.4293 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentNetworkLoad | 0.1301-0.2160 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueShiftNetworkLoad | 0.1049-0.2252 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.1224-1.1300 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7484 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0035-0.2372 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0000-0.9988 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0379-0.1543 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1116-0.4172 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1048-0.2979 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1261-0.6257 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4546 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.2379-0.7170 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2830-0.7621 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.2285-0.3727 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0692-0.5712 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1408-0.6923 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | crossVenueDetectionIndex | 0.0803-0.7538 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | participationProtectionIndex | 0.0340-0.6696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | speechRestrictionRisk | 0.0250-0.4326 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6761 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6761 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.4150 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7484 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7484 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0006-0.3146 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.1049-0.4040 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2076-0.5414 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.0885-0.1801 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.5360-0.5999 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.1760-0.3234 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.2753-0.7876 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.1244-0.6856 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.5721 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0078-0.1831 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0035-0.2372 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0035-0.2372 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorInfluence | 0.0001-0.0165 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | voucherResidentParticipation | 0.0080-0.0584 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingCandidateUptake | 0.0616-0.5947 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1671-0.4647 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0006-0.3146 | 0.30-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.5100-0.6919 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0000-0.0801 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0000-0.9988 | 0.00-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0379-0.1543 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1116-0.4172 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1048-0.2979 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4546 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1261-0.6257 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | captureRateSeedStdDev | 0.0000-0.0660 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortionSeedStdDev | 0.0016-0.0236 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.2379-0.7170 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2830-0.7621 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | crossVenueDetectionIndex | 0.0803-0.7538 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | participationProtectionIndex | 0.0340-0.6696 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | speechRestrictionRisk | 0.0250-0.4326 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.2285-0.3727 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0692-0.5712 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1408-0.6923 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentNetworkLoad | 0.0000-0.5225 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueShiftNetworkLoad | 0.0781-0.3577 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1523-0.6212 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7346 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0044-0.0965 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0000-0.7027 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0317-0.1145 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1149-0.3425 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.0928-0.2399 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0857-0.1015 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0759-0.6684 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1384-0.1551 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.1661-0.6322 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3678-0.8339 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.3248-0.3549 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1468-0.1622 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.1386-0.4055 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | crossVenueDetectionIndex | 0.0754-0.9403 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | participationProtectionIndex | 0.5055-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | speechRestrictionRisk | 0.2526-0.2857 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4405-0.6378 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4405-0.6378 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1634-0.2152 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7346 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7346 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0000-0.2668 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1529-0.1703 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3092-0.3396 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1459-0.1542 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5649-0.5811 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.3054-0.3125 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.5202-0.5619 | 0.50-0.99 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.1047-0.5093 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4043-0.4224 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0033-0.2127 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0044-0.0965 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0044-0.0965 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0001-0.0006 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2324-0.6808 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.2156-0.3803 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0000-0.2668 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6279-0.6845 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0000-0.0883 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0000-0.7027 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0317-0.1145 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1149-0.3425 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.0928-0.2399 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0857-0.1015 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1384-0.1551 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0759-0.6684 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | captureRateSeedStdDev | 0.0000-0.0755 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortionSeedStdDev | 0.0052-0.0239 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.1661-0.6322 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3678-0.8339 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | crossVenueDetectionIndex | 0.0754-0.9403 | 0.00-0.90 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | participationProtectionIndex | 0.5055-0.7327 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | speechRestrictionRisk | 0.2526-0.2857 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.3248-0.3549 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1468-0.1622 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.1386-0.4055 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentNetworkLoad | 0.1206-0.1420 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueShiftNetworkLoad | 0.0667-0.2571 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | lobbySpendPerContest | 0.1411-0.2712 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7325 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | voucherParticipation | 0.0200-0.7600 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0052-0.0894 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.0037-0.5302 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0418-0.1062 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.1204-0.2648 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.1129-0.2174 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0849-0.0987 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.2918-0.6472 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1401-0.1573 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.2244-0.4446 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.5554-0.7756 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.3369-0.3595 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1463-0.2643 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1584-0.4069 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | crossVenueDetectionIndex | 0.4210-0.8216 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | participationProtectionIndex | 0.1930-0.7184 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | speechRestrictionRisk | 0.0660-0.2696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.5276-0.6357 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.5276-0.6357 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | donorInfluenceGini | 0.1705-0.2079 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7325 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7325 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.0302-0.2529 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | commentReviewBurden | 0.1537-0.2610 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | templateCommentSaturation | 0.3118-0.3297 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentUniqueInformationShare | 0.1470-0.1522 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalClaimCredibility | 0.5695-0.5794 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentSubstantiveUptake | 0.2208-0.3193 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentCompressionRate | 0.4390-0.5452 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | detectionRate | 0.1588-0.5029 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | regulatorQueueBacklog | 0.4430-0.4592 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | sanctionRate | 0.0155-0.1184 | 0.003-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0052-0.0894 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0052-0.0894 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorInfluence | 0.0001-0.0004 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | voucherResidentParticipation | 0.0094-0.0612 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | publicFinancingCandidateUptake | 0.1030-0.6802 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | influencePreservationRate | 0.2295-0.3091 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.0302-0.2529 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | commentAuthenticity | 0.6363-0.6817 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueSubstitutionRate | 0.0000-0.0433 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.0037-0.5302 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0418-0.1062 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.1204-0.2648 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.1129-0.2174 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0849-0.0987 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1401-0.1573 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.2918-0.6472 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | captureRateSeedStdDev | 0.0072-0.0640 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortionSeedStdDev | 0.0053-0.0205 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.2244-0.4446 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.5554-0.7756 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | crossVenueDetectionIndex | 0.4210-0.8216 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | participationProtectionIndex | 0.1930-0.7184 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | speechRestrictionRisk | 0.0660-0.2696 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.3369-0.3595 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1463-0.2643 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1584-0.4069 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentNetworkLoad | 0.1127-0.1859 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueShiftNetworkLoad | 0.0948-0.2202 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1409-0.2211 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7366 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.0640-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0053-0.0785 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0010-0.4086 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0317-0.1152 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1161-0.2601 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.0932-0.2311 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0890-0.0971 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.0887-0.6324 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1440-0.1547 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.1691-0.6185 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3815-0.8309 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.3311-0.3480 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1474-0.1670 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.1389-0.4063 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | crossVenueDetectionIndex | 0.2478-0.8924 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | participationProtectionIndex | 0.4424-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | speechRestrictionRisk | 0.2459-0.2857 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4424-0.6418 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4424-0.6418 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1741-0.2012 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7366 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7366 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0000-0.2704 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.1532-0.1731 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3103-0.3304 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1477-0.1526 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5674-0.5799 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.3055-0.3118 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.5218-0.5529 | 0.50-0.99 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.1500-0.5505 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4415-0.4554 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0057-0.1833 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0053-0.0785 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0053-0.0785 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0001-0.0003 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0125-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.1223-0.6808 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.2230-0.3217 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0000-0.2704 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6259-0.6843 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0000-0.0540 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0010-0.4086 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0317-0.1152 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1161-0.2601 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.0932-0.2311 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0890-0.0971 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1440-0.1547 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.0887-0.6324 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | captureRateSeedStdDev | 0.0036-0.0560 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortionSeedStdDev | 0.0045-0.0177 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.1691-0.6185 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3815-0.8309 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | crossVenueDetectionIndex | 0.2478-0.8924 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | participationProtectionIndex | 0.4424-0.7327 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | speechRestrictionRisk | 0.2459-0.2857 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.3311-0.3480 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1474-0.1670 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.1389-0.4063 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentNetworkLoad | 0.1236-0.1426 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueShiftNetworkLoad | 0.0678-0.2378 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| source-moments.csv | commentFloodingIndex | 0.3072-0.3072 | 0.00-1.00 | fit | source moment inside benchmark range |
| source-moments.csv | darkMoneyDirectVisibility | 0.0000-0.0000 | 0.02-0.10 | miss | source moment outside benchmark range |
| source-moments.csv | commentFloodingIndex | 0.3072-0.3072 | 0.00-0.90 | fit | source moment inside benchmark range |
| source-moments.csv | procurementSingleBidShare | 0.0000-0.0000 | 0.10-0.25 | miss | source moment outside benchmark range |
| source-moments.csv | procurementExPostModificationShare | 0.0000-0.0000 | 0.01-0.05 | miss | source moment outside benchmark range |
