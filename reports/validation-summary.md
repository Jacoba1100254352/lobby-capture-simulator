# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `57`
- Partial: `32`
- Miss: `31`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `20`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `0`, partial `3`, miss `5`, unknown `0`
- `judgmental`: fit `0`, partial `1`, miss `3`, unknown `0`
- `observed`: fit `14`, partial `10`, miss `8`, unknown `0`
- `observed_proxy`: fit `8`, partial `4`, miss `8`, unknown `0`
- `proxy`: fit `15`, partial `14`, miss `3`, unknown `0`
- `sectoral`: fit `0`, partial `0`, miss `4`, unknown `0`

| Report | Metric | Observed | Benchmark | Status | Note |
| --- | --- | ---: | ---: | --- | --- |
| lobby-capture-ablation.csv | lobbySpendPerContest | 0.1297-0.1335 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6638-0.6641 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | voucherParticipation | 0.0000-0.6400 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0020-0.0076 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5282-0.5342 | 0.20-0.45 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | averageDisclosureLag | 0.5282-0.5342 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | donorInfluenceGini | 0.1796-0.2114 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6638-0.6641 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | largeDonorDependence | 0.6638-0.6641 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | darkMoneyDirectVisibility | 0.0000-0.0000 | 0.02-0.10 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1053-0.2045 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | commentReviewBurden | 0.1939-0.3027 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | templateCommentSaturation | 0.3129-0.3221 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentUniqueInformationShare | 0.1495-0.1528 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | technicalClaimCredibility | 0.5668-0.5782 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentSubstantiveUptake | 0.2009-0.3021 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentCompressionRate | 0.3648-0.4319 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | detectionRate | 0.0438-0.1838 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | regulatorQueueBacklog | 0.4710-0.4871 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | sanctionRate | 0.0003-0.0266 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0020-0.0076 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | procurementBias | 0.0020-0.0076 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | revolvingDoorInfluence | 0.0000-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-ablation.csv | voucherResidentParticipation | 0.0080-0.0528 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | publicFinancingCandidateUptake | 0.0738-0.5594 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-ablation.csv | influencePreservationRate | 0.3222-0.3931 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | hiddenInfluenceShare | 0.1053-0.2045 | 0.10-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | commentAuthenticity | 0.6318-0.6740 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-ablation.csv | venueSubstitutionRate | 0.0944-0.1305 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | lobbySpendPerContest | 0.0932-0.4719 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7391 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | voucherParticipation | 0.0000-0.7200 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0003-0.0740 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6743 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | averageDisclosureLag | 0.3735-0.6743 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | donorInfluenceGini | 0.0000-0.2692 | 0.005-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7391 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | largeDonorDependence | 0.6623-0.7391 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | darkMoneyDirectVisibility | 0.0000-0.5315 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0301-0.3305 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | commentReviewBurden | 0.2105-0.4511 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | templateCommentSaturation | 0.2012-0.5211 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentUniqueInformationShare | 0.0948-0.1824 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | technicalClaimCredibility | 0.5357-0.6013 | 0.20-0.60 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentSubstantiveUptake | 0.1662-0.2970 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | commentCompressionRate | 0.1970-0.5088 | 0.50-0.99 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | detectionRate | 0.0375-0.2163 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | regulatorQueueBacklog | 0.1171-0.5568 | 0.50-0.75 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | sanctionRate | 0.0016-0.0172 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0003-0.0740 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | procurementBias | 0.0003-0.0740 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | revolvingDoorInfluence | 0.0000-0.0018 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-campaign.csv | voucherResidentParticipation | 0.0080-0.0584 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | publicFinancingCandidateUptake | 0.0617-0.5947 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | influencePreservationRate | 0.1852-0.4692 | 0.20-1.50 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | hiddenInfluenceShare | 0.0301-0.3305 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-campaign.csv | commentAuthenticity | 0.5156-0.6813 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-campaign.csv | venueSubstitutionRate | 0.0309-0.1658 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1431-0.1650 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6637-0.7317 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0010-0.0013 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4435-0.6451 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4435-0.6451 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1602-0.2193 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6637-0.7317 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6637-0.7317 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | darkMoneyDirectVisibility | 0.0000-0.5324 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0151-0.3319 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1978-0.2052 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.2909-0.3092 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1535-0.1583 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5738-0.5805 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.2971-0.2994 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.3973-0.4192 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.0673-0.1587 | 0.05-0.21 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4095-0.4367 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0007-0.0160 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0010-0.0013 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0010-0.0013 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0000-0.0001 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2329-0.6807 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.2664-0.3531 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0151-0.3319 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6471-0.6916 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0530-0.1710 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1309-0.1357 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6637-0.7306 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0010-0.0012 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4468-0.6375 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4468-0.6375 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1703-0.2030 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6637-0.7306 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6637-0.7306 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | darkMoneyDirectVisibility | 0.0000-0.5319 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0164-0.3369 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.2042-0.2109 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.2913-0.3016 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1554-0.1582 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5750-0.5811 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.2960-0.2986 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.3934-0.4114 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.0752-0.1490 | 0.05-0.21 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4558-0.4710 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0019-0.0133 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0010-0.0012 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0010-0.0012 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0000-0.0001 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.2437-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.2675-0.3577 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0164-0.3369 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6496-0.6930 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0599-0.1693 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
