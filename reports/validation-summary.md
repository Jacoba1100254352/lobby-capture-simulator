# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `248`
- Partial: `35`
- Miss: `20`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `101`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `1`, partial `0`, miss `5`, unknown `0`
- `judgmental`: fit `2`, partial `3`, miss `0`, unknown `0`
- `observed`: fit `20`, partial `15`, miss `8`, unknown `0`
- `observed_proxy`: fit `20`, partial `0`, miss `1`, unknown `0`
- `proxy`: fit `40`, partial `15`, miss `6`, unknown `0`
- `sectoral`: fit `6`, partial `0`, miss `0`, unknown `0`
- `synthetic`: fit `58`, partial `2`, miss `0`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1394-0.2230 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6226-0.6228 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0294-0.0858 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.1034-0.4847 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0735-0.1332 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1687-0.2730 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1650-0.2596 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0902-0.0991 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0617-0.5472 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1428-0.1556 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.2615-0.4446 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5554-0.7385 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.3390-0.3591 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1499-0.3156 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1627-0.3998 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | crossVenueDetectionIndex | 0.4950-0.7538 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | participationProtectionIndex | 0.3432-0.6696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | speechRestrictionRisk | 0.1549-0.3223 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.3238-0.3289 | 0.20-0.45 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.3238-0.3289 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1760-0.2045 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6226-0.6228 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1393-0.2934 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.1598-0.2410 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3151-0.3278 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.1490-0.1527 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5745-0.5802 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.2187-0.3107 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.4526-0.5412 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.1866-0.5356 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.4750-0.4900 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0100-0.1956 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | voucherResidentParticipation | 0.0080-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingCandidateUptake | 0.0804-0.5660 | 0.57-0.86 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.2548-0.3467 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1393-0.2934 | 0.30-0.60 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.6308-0.6733 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.0397-0.1522 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | observedCaptureRate | 0.1034-0.4847 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenCaptureIndex | 0.0735-0.1332 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortion | 0.1687-0.2730 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | substitutionFailureRisk | 0.1650-0.2596 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryShare | 0.0902-0.0991 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalRulemakingDistortion | 0.1428-0.1556 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | enforcementCapacityIndex | 0.0617-0.5472 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | captureRateSeedStdDev | 0.0301-0.0579 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | totalInfluenceDistortionSeedStdDev | 0.0109-0.0210 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkOpacityIndex | 0.2615-0.4446 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | networkLegibilityIndex | 0.5554-0.7385 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | crossVenueDetectionIndex | 0.4950-0.7538 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | participationProtectionIndex | 0.3432-0.6696 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | speechRestrictionRisk | 0.1549-0.3223 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | intermediaryCentrality | 0.3390-0.3591 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementNetworkExposure | 0.1499-0.3156 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorBridgeIndex | 0.1627-0.3998 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentNetworkLoad | 0.1289-0.2003 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueShiftNetworkLoad | 0.1287-0.2724 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.1237-1.1317 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6212-0.7080 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7600 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0109-0.4244 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0219-0.9988 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0537-0.2027 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1344-0.4368 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1284-0.3462 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6383 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4547 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.2578-0.7218 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2782-0.7422 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.2339-0.3761 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0698-0.6890 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1198-0.6028 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | crossVenueDetectionIndex | 0.0803-0.7538 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | participationProtectionIndex | 0.0340-0.6696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | speechRestrictionRisk | 0.0250-0.4326 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.2322-0.4850 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.2322-0.4850 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.3986 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6212-0.7080 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0517-0.4804 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.1091-0.4010 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2092-0.5416 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.0884-0.1798 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.5296-0.5963 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.1760-0.3230 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.2774-0.7815 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.1575-0.9178 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.5716 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0116-0.2966 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | voucherResidentParticipation | 0.0080-0.0612 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingCandidateUptake | 0.0682-0.6768 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1726-0.4805 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0517-0.4804 | 0.30-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.5099-0.6865 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0055-0.1753 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | observedCaptureRate | 0.0219-0.9988 | 0.00-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenCaptureIndex | 0.0537-0.2027 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortion | 0.1344-0.4368 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | substitutionFailureRisk | 0.1284-0.3462 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryShare | 0.0800-0.1200 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalRulemakingDistortion | 0.0000-0.4547 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | enforcementCapacityIndex | 0.1260-0.6383 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | captureRateSeedStdDev | 0.0042-0.0667 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | totalInfluenceDistortionSeedStdDev | 0.0016-0.0259 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkOpacityIndex | 0.2578-0.7218 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | networkLegibilityIndex | 0.2782-0.7422 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | crossVenueDetectionIndex | 0.0803-0.7538 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | participationProtectionIndex | 0.0340-0.6696 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | speechRestrictionRisk | 0.0250-0.4326 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | intermediaryCentrality | 0.2339-0.3761 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementNetworkExposure | 0.0698-0.6890 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorBridgeIndex | 0.1198-0.6028 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentNetworkLoad | 0.0000-0.5226 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueShiftNetworkLoad | 0.0971-0.3806 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1527-0.6540 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6224-0.6934 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0089-0.1034 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0113-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0398-0.2001 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1228-0.3704 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.1065-0.3412 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0874-0.1020 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0956-0.6791 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1373-0.1528 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.1762-0.6335 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3665-0.8238 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.3348-0.3542 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1522-0.1680 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.1176-0.3781 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | crossVenueDetectionIndex | 0.0754-0.9403 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | participationProtectionIndex | 0.5055-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | speechRestrictionRisk | 0.2526-0.2857 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.2660-0.4069 | 0.20-0.45 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.2660-0.4069 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1635-0.2121 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6224-0.6934 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0259-0.5052 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1504-0.1703 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3108-0.3394 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1458-0.1537 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5729-0.5805 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.3089-0.3131 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.5228-0.5608 | 0.50-0.99 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.1093-0.6627 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4065-0.4230 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0107-0.3047 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2390-0.6874 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.2284-0.4034 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0259-0.5052 | 0.30-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6268-0.6867 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0055-0.2204 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | observedCaptureRate | 0.0113-0.7327 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenCaptureIndex | 0.0398-0.2001 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortion | 0.1228-0.3704 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | substitutionFailureRisk | 0.1065-0.3412 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryShare | 0.0874-0.1020 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalRulemakingDistortion | 0.1373-0.1528 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | enforcementCapacityIndex | 0.0956-0.6791 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | captureRateSeedStdDev | 0.0134-0.0764 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | totalInfluenceDistortionSeedStdDev | 0.0064-0.0274 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkOpacityIndex | 0.1762-0.6335 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | networkLegibilityIndex | 0.3665-0.8238 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | crossVenueDetectionIndex | 0.0754-0.9403 | 0.00-0.90 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | participationProtectionIndex | 0.5055-0.7327 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | speechRestrictionRisk | 0.2526-0.2857 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | intermediaryCentrality | 0.3348-0.3542 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementNetworkExposure | 0.1522-0.1680 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorBridgeIndex | 0.1176-0.3781 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentNetworkLoad | 0.1161-0.1412 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueShiftNetworkLoad | 0.0745-0.3151 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | lobbySpendPerContest | 0.1474-0.2952 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6226-0.6923 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | voucherParticipation | 0.0200-0.7600 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementBias | 0.0193-0.1020 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.0535-0.6257 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0749-0.1835 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.1530-0.3038 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.1648-0.3187 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0887-0.1020 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.2962-0.6625 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1383-0.1596 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.2299-0.4545 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.5455-0.7701 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.3382-0.3663 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1478-0.2791 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1381-0.3831 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | crossVenueDetectionIndex | 0.4210-0.8216 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | participationProtectionIndex | 0.1930-0.7184 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | speechRestrictionRisk | 0.0660-0.2696 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.3231-0.3947 | 0.20-0.45 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | averageDisclosureLag | 0.3231-0.3947 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | donorInfluenceGini | 0.1708-0.2025 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | largeDonorDependence | 0.6226-0.6923 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.1502-0.4705 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | commentReviewBurden | 0.1488-0.2570 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | templateCommentSaturation | 0.3201-0.3337 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentUniqueInformationShare | 0.1461-0.1514 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalClaimCredibility | 0.5715-0.5794 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentSubstantiveUptake | 0.2214-0.3205 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentCompressionRate | 0.4442-0.5524 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | detectionRate | 0.2192-0.6192 | 0.05-0.21 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | regulatorQueueBacklog | 0.4435-0.4599 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | sanctionRate | 0.0408-0.2424 | 0.003-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-portfolio.csv | voucherResidentParticipation | 0.0094-0.0612 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | publicFinancingCandidateUptake | 0.1096-0.6868 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | influencePreservationRate | 0.2506-0.3191 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenInfluenceShare | 0.1502-0.4705 | 0.30-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | commentAuthenticity | 0.6323-0.6789 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueSubstitutionRate | 0.0395-0.1950 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-portfolio.csv | observedCaptureRate | 0.0535-0.6257 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | hiddenCaptureIndex | 0.0749-0.1835 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortion | 0.1530-0.3038 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | substitutionFailureRisk | 0.1648-0.3187 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryShare | 0.0887-0.1020 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | technicalRulemakingDistortion | 0.1383-0.1596 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | enforcementCapacityIndex | 0.2962-0.6625 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | captureRateSeedStdDev | 0.0225-0.0695 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | totalInfluenceDistortionSeedStdDev | 0.0099-0.0218 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkOpacityIndex | 0.2299-0.4545 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | networkLegibilityIndex | 0.5455-0.7701 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | crossVenueDetectionIndex | 0.4210-0.8216 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | participationProtectionIndex | 0.1930-0.7184 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | speechRestrictionRisk | 0.0660-0.2696 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | intermediaryCentrality | 0.3382-0.3663 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | procurementNetworkExposure | 0.1478-0.2791 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | revolvingDoorBridgeIndex | 0.1381-0.3831 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | commentNetworkLoad | 0.1097-0.1856 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-portfolio.csv | venueShiftNetworkLoad | 0.1314-0.2909 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1426-0.2380 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6225-0.6940 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.0640-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0121-0.0842 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0205-0.5205 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0407-0.1925 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1248-0.3153 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.1092-0.3291 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0899-0.1022 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.1051-0.6432 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1438-0.1558 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.1782-0.6192 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3808-0.8218 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.3360-0.3515 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1521-0.1695 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.1173-0.3781 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | crossVenueDetectionIndex | 0.2478-0.8924 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | participationProtectionIndex | 0.4424-0.7327 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | speechRestrictionRisk | 0.2459-0.2857 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.2654-0.4003 | 0.20-0.45 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.2654-0.4003 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1678-0.1984 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6225-0.6940 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0288-0.4803 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.1526-0.1706 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3135-0.3330 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1478-0.1530 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5757-0.5802 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.3095-0.3131 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.5264-0.5569 | 0.50-0.99 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.1771-0.6557 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4432-0.4587 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0105-0.2410 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0125-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.1289-0.6874 | 0.57-0.86 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.2353-0.3452 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0288-0.4803 | 0.30-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6295-0.6837 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0145-0.1998 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | observedCaptureRate | 0.0205-0.5205 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenCaptureIndex | 0.0407-0.1925 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortion | 0.1248-0.3153 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | substitutionFailureRisk | 0.1092-0.3291 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryShare | 0.0899-0.1022 | 0.00-0.65 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalRulemakingDistortion | 0.1438-0.1558 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | enforcementCapacityIndex | 0.1051-0.6432 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | captureRateSeedStdDev | 0.0144-0.0750 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | totalInfluenceDistortionSeedStdDev | 0.0063-0.0232 | 0.00-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkOpacityIndex | 0.1782-0.6192 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | networkLegibilityIndex | 0.3808-0.8218 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | crossVenueDetectionIndex | 0.2478-0.8924 | 0.00-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | participationProtectionIndex | 0.4424-0.7327 | 0.00-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | speechRestrictionRisk | 0.2459-0.2857 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | intermediaryCentrality | 0.3360-0.3515 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementNetworkExposure | 0.1521-0.1695 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorBridgeIndex | 0.1173-0.3781 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentNetworkLoad | 0.1260-0.1449 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueShiftNetworkLoad | 0.0778-0.3044 | 0.00-0.85 | fit | all scenario values inside benchmark range |
| source-moments.csv | commentFloodingIndex | 0.3072-0.3072 | 0.00-1.00 | fit | source moment inside benchmark range |
| source-moments.csv | darkMoneyDirectVisibility | 0.0000-0.0000 | 0.00-0.10 | fit | source moment inside benchmark range |
| source-moments.csv | procurementAgencyTop1Share | 1.0000-1.0000 | 0.55-0.65 | miss | source moment outside benchmark range |
| source-moments.csv | procurementRecipientTop3Share | 0.1723-0.1723 | 0.25-0.40 | miss | source moment outside benchmark range |
| source-moments.csv | revolvingDoorInfluenceMean | 0.3400-0.3400 | 0.25-0.75 | fit | source moment inside benchmark range |
| source-moments.csv | commentFloodingIndex | 0.3072-0.3072 | 0.00-0.90 | fit | source moment inside benchmark range |
| source-moments.csv | procurementSingleBidShare | 0.2350-0.2350 | 0.10-0.25 | fit | source moment inside benchmark range |
| source-moments.csv | procurementExPostModificationShare | 1.0000-1.0000 | 0.01-0.05 | miss | source moment outside benchmark range |
