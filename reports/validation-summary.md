# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `247`
- Partial: `32`
- Miss: `51`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `105`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `0`, partial `4`, miss `6`, unknown `0`
- `judgmental`: fit `0`, partial `1`, miss `4`, unknown `0`
- `observed`: fit `15`, partial `18`, miss `12`, unknown `0`
- `observed_proxy`: fit `20`, partial `0`, miss `10`, unknown `0`
- `proxy`: fit `44`, partial `7`, miss `14`, unknown `0`
- `sectoral`: fit `5`, partial `0`, miss `5`, unknown `0`
- `synthetic`: fit `58`, partial `2`, miss `0`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1316-0.1653 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0062-0.0521 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.0172-0.2272 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0402-0.0808 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1284-0.1968 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1122-0.1897 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0838-0.0974 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0445-0.5296 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentFloodingIndex | 0.2351-0.2755 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1475-0.1613 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.2502-0.4493 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5507-0.7498 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.2977-0.3181 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1388-0.2912 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1409-0.3841 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | crossVenueDetectionIndex | 0.4950-0.7538 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | participationProtectionIndex | 0.3432-0.6696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | speechRestrictionRisk | 0.1549-0.3223 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5283-0.5320 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5283-0.5320 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1733-0.1977 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6639-0.6640 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | darkMoneyDirectVisibility | 0.0000-0.0000 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.0250-0.1467 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.1855-0.2860 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3146-0.3266 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.1472-0.1517 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5669-0.5794 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.2040-0.3047 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.3699-0.4340 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.1184-0.3344 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.4751-0.4898 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0056-0.0944 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0062-0.0521 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0062-0.0521 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorInfluence | 0.0001-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | voucherResidentParticipation | 0.0080-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingCandidateUptake | 0.0738-0.5594 | 0.57-0.86 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.2363-0.3254 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.0250-0.1467 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.6301-0.6735 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.0000-0.0432 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.0172-0.2272 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0402-0.0808 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1284-0.1968 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1122-0.1897 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0838-0.0974 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentFloodingIndex | 0.2351-0.2755 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1475-0.1613 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0445-0.5296 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | captureRateSeedStdDev | 0.0135-0.0500 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortionSeedStdDev | 0.0059-0.0159 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.2502-0.4493 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5507-0.7498 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | crossVenueDetectionIndex | 0.4950-0.7538 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | participationProtectionIndex | 0.3432-0.6696 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | speechRestrictionRisk | 0.1549-0.3223 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.2977-0.3181 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1388-0.2912 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1409-0.3841 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentNetworkLoad | 0.1296-0.2159 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueShiftNetworkLoad | 0.1049-0.2253 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.1233-1.1250 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7485 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0028-0.2188 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0000-0.9991 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0378-0.1542 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1104-0.4162 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1045-0.2976 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6247 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentFloodingIndex | 0.2371-0.3482 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4694 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.2334-0.7120 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2880-0.7666 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.1934-0.3340 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0626-0.5531 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1005-0.6584 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | crossVenueDetectionIndex | 0.0803-0.7538 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | participationProtectionIndex | 0.0340-0.6696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | speechRestrictionRisk | 0.0250-0.4326 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6761 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6761 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.4208 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7485 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7485 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | darkMoneyDirectVisibility | 0.0000-0.5318 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0005-0.3146 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.1278-0.4224 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2076-0.5409 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.0886-0.1801 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.5361-0.5975 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.1705-0.3158 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.2228-0.6312 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.1228-0.6794 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.5724 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0081-0.1731 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0028-0.2188 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0028-0.2188 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorInfluence | 0.0001-0.0165 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | voucherResidentParticipation | 0.0080-0.0584 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingCandidateUptake | 0.0616-0.5947 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1695-0.4647 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0005-0.3146 | 0.30-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.5102-0.6923 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0000-0.0801 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0000-0.9991 | 0.00-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0378-0.1542 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1104-0.4162 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1045-0.2976 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentFloodingIndex | 0.2371-0.3482 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4694 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6247 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | captureRateSeedStdDev | 0.0000-0.0642 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortionSeedStdDev | 0.0014-0.0203 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.2334-0.7120 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2880-0.7666 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | crossVenueDetectionIndex | 0.0803-0.7538 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | participationProtectionIndex | 0.0340-0.6696 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | speechRestrictionRisk | 0.0250-0.4326 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.1934-0.3340 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0626-0.5531 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1005-0.6584 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentNetworkLoad | 0.0000-0.5224 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueShiftNetworkLoad | 0.0782-0.3577 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1523-0.6072 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7342 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0033-0.0936 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0000-0.6940 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0317-0.1138 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1142-0.3395 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.0926-0.2386 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0857-0.1011 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0748-0.6685 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentFloodingIndex | 0.2330-0.2404 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1415-0.1593 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.1613-0.6275 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3725-0.8387 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.2890-0.3161 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1364-0.1527 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.0995-0.3605 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | crossVenueDetectionIndex | 0.0754-0.9403 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | participationProtectionIndex | 0.5055-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | speechRestrictionRisk | 0.2526-0.2857 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4407-0.6372 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4407-0.6372 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1648-0.2110 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7342 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7342 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | darkMoneyDirectVisibility | 0.0000-0.5321 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0000-0.2638 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1748-0.1916 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3116-0.3345 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1474-0.1533 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5651-0.5808 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.2990-0.3068 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.4193-0.4480 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.1027-0.5073 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4047-0.4219 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0027-0.2113 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0033-0.0936 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0033-0.0936 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0001-0.0006 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2325-0.6808 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.2156-0.3775 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0000-0.2638 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6279-0.6845 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0000-0.0874 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0000-0.6940 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0317-0.1138 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1142-0.3395 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.0926-0.2386 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0857-0.1011 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentFloodingIndex | 0.2330-0.2404 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1415-0.1593 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0748-0.6685 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | captureRateSeedStdDev | 0.0000-0.0765 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortionSeedStdDev | 0.0048-0.0227 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.1613-0.6275 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3725-0.8387 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | crossVenueDetectionIndex | 0.0754-0.9403 | 0.00-0.90 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | participationProtectionIndex | 0.5055-0.7327 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | speechRestrictionRisk | 0.2526-0.2857 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.2890-0.3161 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1364-0.1527 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.0995-0.3605 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentNetworkLoad | 0.1216-0.1408 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueShiftNetworkLoad | 0.0668-0.2566 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | lobbySpendPerContest | 0.1411-0.2656 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7326 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | voucherParticipation | 0.0200-0.7600 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0040-0.0881 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.0037-0.5188 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0418-0.1052 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.1196-0.2611 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.1126-0.2162 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0849-0.0983 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.2917-0.6442 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentFloodingIndex | 0.2289-0.2834 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1436-0.1621 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.2194-0.4386 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.5614-0.7806 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.2991-0.3206 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1372-0.2522 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1168-0.3610 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | crossVenueDetectionIndex | 0.4210-0.8216 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | participationProtectionIndex | 0.1930-0.7184 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | speechRestrictionRisk | 0.0660-0.2696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.5263-0.6350 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.5263-0.6350 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | donorInfluenceGini | 0.1691-0.2050 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7326 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6638-0.7326 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | darkMoneyDirectVisibility | 0.0000-0.5640 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.0302-0.2511 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | commentReviewBurden | 0.1712-0.2851 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | templateCommentSaturation | 0.3118-0.3285 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentUniqueInformationShare | 0.1474-0.1526 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalClaimCredibility | 0.5693-0.5791 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentSubstantiveUptake | 0.2139-0.3135 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentCompressionRate | 0.3530-0.4554 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | detectionRate | 0.1588-0.4849 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | regulatorQueueBacklog | 0.4435-0.4596 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | sanctionRate | 0.0151-0.1122 | 0.003-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0040-0.0881 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0040-0.0881 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorInfluence | 0.0001-0.0004 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | voucherResidentParticipation | 0.0094-0.0612 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | publicFinancingCandidateUptake | 0.1030-0.6802 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | influencePreservationRate | 0.2296-0.3098 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.0302-0.2511 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | commentAuthenticity | 0.6358-0.6817 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueSubstitutionRate | 0.0000-0.0430 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.0037-0.5188 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0418-0.1052 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.1196-0.2611 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.1126-0.2162 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0849-0.0983 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentFloodingIndex | 0.2289-0.2834 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1436-0.1621 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.2917-0.6442 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | captureRateSeedStdDev | 0.0072-0.0658 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortionSeedStdDev | 0.0053-0.0195 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.2194-0.4386 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.5614-0.7806 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | crossVenueDetectionIndex | 0.4210-0.8216 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | participationProtectionIndex | 0.1930-0.7184 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | speechRestrictionRisk | 0.0660-0.2696 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.2991-0.3206 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1372-0.2522 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1168-0.3610 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentNetworkLoad | 0.1132-0.1868 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueShiftNetworkLoad | 0.0947-0.2200 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1409-0.2197 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7361 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.0640-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0042-0.0740 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0005-0.3933 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0317-0.1146 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1148-0.2555 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.0930-0.2306 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0888-0.0971 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.0877-0.6324 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentFloodingIndex | 0.2339-0.2380 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1481-0.1598 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.1642-0.6136 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3864-0.8358 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.2934-0.3095 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1392-0.1571 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.0999-0.3606 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | crossVenueDetectionIndex | 0.2478-0.8924 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | participationProtectionIndex | 0.4424-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | speechRestrictionRisk | 0.2459-0.2857 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4431-0.6415 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4431-0.6415 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1744-0.1974 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7361 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7361 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | darkMoneyDirectVisibility | 0.0000-0.5319 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0000-0.2704 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.1735-0.1937 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3099-0.3298 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1481-0.1527 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5672-0.5794 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.2990-0.3055 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.4155-0.4484 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.1467-0.5376 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4431-0.4560 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0052-0.1824 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0042-0.0740 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0042-0.0740 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0001-0.0003 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0125-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.1223-0.6808 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.2235-0.3239 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0000-0.2704 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6261-0.6842 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0000-0.0539 | 0.10-0.70 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0005-0.3933 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0317-0.1146 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1148-0.2555 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.0930-0.2306 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0888-0.0971 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentFloodingIndex | 0.2339-0.2380 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1481-0.1598 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.0877-0.6324 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | captureRateSeedStdDev | 0.0026-0.0515 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortionSeedStdDev | 0.0044-0.0161 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.1642-0.6136 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3864-0.8358 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | crossVenueDetectionIndex | 0.2478-0.8924 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | participationProtectionIndex | 0.4424-0.7327 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | speechRestrictionRisk | 0.2459-0.2857 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.2934-0.3095 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1392-0.1571 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.0999-0.3606 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentNetworkLoad | 0.1234-0.1433 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueShiftNetworkLoad | 0.0681-0.2378 | 0.00-0.85 | fit | all scenario values inside benchmark range |
