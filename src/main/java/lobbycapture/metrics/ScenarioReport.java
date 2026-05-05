package lobbycapture.metrics;

public record ScenarioReport(
        String scenarioKey,
        String scenarioName,
        int totalContests,
        int capturedContests,
        int antiCaptureReforms,
        int enactedAntiCaptureReforms,
        double captureRate,
        double antiCaptureSuccessRate,
        double observedCaptureRate,
        double hiddenCaptureIndex,
        double totalInfluenceDistortion,
        double substitutionFailureRisk,
        double averageCaptureIndex,
        double averagePublicInterestScore,
        double publicPreferenceDistortion,
        double privateGainRatio,
        double lobbySpendPerContest,
        double clientFundingPerContest,
        double donorInfluenceGini,
        double averageDisclosureLag,
        double defensiveReformSpendShare,
        double captureReturnOnSpend,
        double publicBenefitPerInfluenceDollar,
        double visibleLobbyingSpendShare,
        double directAccessSpendShare,
        double agendaAccessSpendShare,
        double informationDistortionSpendShare,
        double publicCampaignSpendShare,
        double litigationThreatSpendShare,
        double campaignFinanceSpendShare,
        double darkMoneySpendShare,
        double revolvingDoorSpendShare,
        double intermediarySpendShare,
        double defensiveChannelSpendShare,
        double detectionRate,
        double sanctionRate,
        double enforcementCapacityIndex,
        double averagePolicyDistortion,
        double regulatoryDrift,
        double enforcementForbearanceRate,
        double procurementBiasIndex,
        double darkMoneyTraceability,
        double darkMoneyDirectVisibility,
        double largeDonorDependence,
        double voucherParticipationRate,
        double voucherResidentParticipation,
        double publicFinancingShare,
        double publicFinancingCandidateUptake,
        double revolvingDoorInfluence,
        double commentRecordDistortion,
        double commentAuthenticity,
        double templateCommentSaturation,
        double commentUniqueInformationShare,
        double commentReviewBurden,
        double commentProceduralAckRate,
        double commentSubstantiveUptake,
        double commentCompressionRate,
        double commentFloodingIndex,
        double technicalClaimCredibility,
        double technicalRulemakingDistortion,
        double channelSwitchRate,
        double evasionShiftRate,
        double evasionPenaltyRate,
        double substitutionPressure,
        double influencePreservationRate,
        double hiddenInfluenceShare,
        double netTransparencyGain,
        double messengerSubstitutionRate,
        double venueSubstitutionRate,
        double clientFundingAdaptation,
        double regulatorAttentionIndex,
        double regulatorQueueBacklog,
        double watchdogFocusIndex,
        double watchdogBudgetConcentration,
        double adaptationSpeed,
        double reformDecayPressure,
        double legitimateAdvocacyChillRate,
        double constitutionalChallengeDelay,
        double administrativeCostIndex,
        double captureRateSeedStdDev,
        double hiddenInfluenceSeedStdDev,
        double totalInfluenceDistortionSeedStdDev
) {
    public double captureControlScore() {
        return MetricDefinition.average(
                MetricDefinition.lowerIsBetter(observedCaptureRate),
                MetricDefinition.lowerIsBetter(averageCaptureIndex),
                MetricDefinition.lowerIsBetter(hiddenCaptureIndex),
                MetricDefinition.lowerIsBetter(totalInfluenceDistortion),
                MetricDefinition.lowerIsBetter(substitutionFailureRisk),
                MetricDefinition.lowerIsBetter(privateGainRatio / 5.0),
                MetricDefinition.lowerIsBetter(publicPreferenceDistortion),
                MetricDefinition.lowerIsBetter(enforcementForbearanceRate),
                MetricDefinition.lowerIsBetter(evasionPenaltyRate),
                MetricDefinition.lowerIsBetter(hiddenInfluenceShare),
                MetricDefinition.lowerIsBetter(influencePreservationRate),
                MetricDefinition.lowerIsBetter(regulatorQueueBacklog),
                MetricDefinition.lowerIsBetter(reformDecayPressure),
                MetricDefinition.normalizeSigned(netTransparencyGain),
                regulatorAttentionIndex,
                watchdogFocusIndex,
                enforcementCapacityIndex,
                antiCaptureSuccessRate * MetricDefinition.lowerIsBetter(substitutionFailureRisk)
        );
    }

    public double distortionMinimizationScore() {
        return MetricDefinition.average(
                MetricDefinition.lowerIsBetter(totalInfluenceDistortion),
                MetricDefinition.lowerIsBetter(substitutionFailureRisk),
                MetricDefinition.lowerIsBetter(hiddenCaptureIndex),
                MetricDefinition.lowerIsBetter(administrativeCostIndex)
        );
    }

    public double representationScore() {
        return MetricDefinition.average(
                averagePublicInterestScore,
                MetricDefinition.lowerIsBetter(largeDonorDependence),
                MetricDefinition.lowerIsBetter(donorInfluenceGini),
                voucherResidentParticipation,
                publicFinancingCandidateUptake,
                commentUniqueInformationShare,
                commentSubstantiveUptake,
                MetricDefinition.lowerIsBetter(watchdogBudgetConcentration),
                MetricDefinition.lowerIsBetter(Math.abs(clientFundingAdaptation - 1.0)),
                MetricDefinition.lowerIsBetter(publicPreferenceDistortion)
        );
    }

    public double reformFeasibilityScore() {
        return MetricDefinition.average(
                MetricDefinition.lowerIsBetter(administrativeCostIndex),
                MetricDefinition.lowerIsBetter(legitimateAdvocacyChillRate),
                MetricDefinition.lowerIsBetter(constitutionalChallengeDelay),
                detectionRate
        );
    }

    public double directionalScore() {
        return MetricDefinition.average(captureControlScore(), representationScore(), reformFeasibilityScore(), distortionMinimizationScore());
    }
}
