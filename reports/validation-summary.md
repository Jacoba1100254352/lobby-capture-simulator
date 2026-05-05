# Validation Summary

Benchmark ranges are plausibility checks, not causal empirical claims.

- Fit: `56`
- Partial: `33`
- Miss: `31`
- Unknown: `0`

## Evidence Classes

- `benchmark`: fit `20`, partial `0`, miss `0`, unknown `0`
- `inferred`: fit `0`, partial `3`, miss `5`, unknown `0`
- `judgmental`: fit `0`, partial `1`, miss `3`, unknown `0`
- `observed`: fit `13`, partial `11`, miss `8`, unknown `0`
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
| lobby-capture-interactions.csv | lobbySpendPerContest | 0.1520-0.2060 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7359 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | voucherParticipation | 0.2240-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0018-0.0222 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4386-0.6354 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | averageDisclosureLag | 0.4386-0.6354 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | donorInfluenceGini | 0.1639-0.2061 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7359 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | largeDonorDependence | 0.6638-0.7359 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | darkMoneyDirectVisibility | 0.0000-0.5321 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0171-0.3890 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | commentReviewBurden | 0.1862-0.1954 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | templateCommentSaturation | 0.3107-0.3265 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentUniqueInformationShare | 0.1491-0.1534 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | technicalClaimCredibility | 0.5635-0.5799 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentSubstantiveUptake | 0.2990-0.3041 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | commentCompressionRate | 0.4137-0.4434 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | detectionRate | 0.0447-0.1760 | 0.05-0.21 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | regulatorQueueBacklog | 0.4041-0.4179 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | sanctionRate | 0.0013-0.0207 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0018-0.0222 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | procurementBias | 0.0018-0.0222 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | revolvingDoorInfluence | 0.0000-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-interactions.csv | voucherResidentParticipation | 0.0237-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | publicFinancingCandidateUptake | 0.2324-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | influencePreservationRate | 0.2989-0.4158 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | hiddenInfluenceShare | 0.0171-0.3890 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-interactions.csv | commentAuthenticity | 0.6296-0.6852 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-interactions.csv | venueSubstitutionRate | 0.0600-0.2001 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | lobbySpendPerContest | 0.1401-0.1641 | 0.01-5.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7348 | 0.10-0.95 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | constitutionalChallengeDelay | 0.0000-0.0000 | 0.00-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | voucherParticipation | 0.0640-0.8000 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0020-0.0071 | 0.00-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4419-0.6381 | 0.20-0.45 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | averageDisclosureLag | 0.4419-0.6381 | 0.01-0.90 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | donorInfluenceGini | 0.1683-0.1950 | 0.005-0.015 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7348 | 0.10-0.20 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | largeDonorDependence | 0.6638-0.7348 | 0.60-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | darkMoneyDirectVisibility | 0.0000-0.5319 | 0.02-0.10 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0183-0.3944 | 0.60-0.80 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | commentReviewBurden | 0.1885-0.1982 | 0.10-1.00 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | templateCommentSaturation | 0.3106-0.3267 | 0.05-0.80 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentUniqueInformationShare | 0.1478-0.1535 | 0.03-0.20 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | technicalClaimCredibility | 0.5666-0.5798 | 0.20-0.60 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentSubstantiveUptake | 0.2986-0.3033 | 0.01-0.35 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | commentCompressionRate | 0.4158-0.4443 | 0.50-0.99 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | detectionRate | 0.0586-0.1681 | 0.05-0.21 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | regulatorQueueBacklog | 0.4416-0.4555 | 0.50-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | sanctionRate | 0.0000-0.0157 | 0.003-0.015 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0020-0.0071 | 0.55-0.65 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | procurementBias | 0.0020-0.0071 | 0.25-0.40 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | revolvingDoorInfluence | 0.0000-0.0002 | 0.40-0.75 | miss | scenario range outside benchmark range |
| lobby-capture-sensitivity.csv | voucherResidentParticipation | 0.0125-0.0640 | 0.03-0.08 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | publicFinancingCandidateUptake | 0.1223-0.6808 | 0.25-0.95 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | influencePreservationRate | 0.3073-0.4183 | 0.20-1.50 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | hiddenInfluenceShare | 0.0183-0.3944 | 0.10-0.80 | partial | some scenario values overlap benchmark range |
| lobby-capture-sensitivity.csv | commentAuthenticity | 0.6266-0.6846 | 0.48-0.87 | fit | all scenario values inside benchmark range |
| lobby-capture-sensitivity.csv | venueSubstitutionRate | 0.0685-0.1977 | 0.10-0.70 | partial | some scenario values overlap benchmark range |
