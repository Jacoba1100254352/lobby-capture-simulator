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
        double directAccessSpendShare,
        double agendaAccessSpendShare,
        double informationDistortionSpendShare,
        double publicCampaignSpendShare,
        double litigationThreatSpendShare,
        double campaignFinanceSpendShare,
        double darkMoneySpendShare,
        double revolvingDoorSpendShare,
        double defensiveChannelSpendShare,
        double detectionRate,
        double sanctionRate,
        double averagePolicyDistortion,
        double regulatoryDrift,
        double enforcementForbearanceRate,
        double procurementBiasIndex,
        double darkMoneyTraceability,
        double largeDonorDependence,
        double voucherParticipationRate,
        double publicFinancingShare,
        double revolvingDoorInfluence,
        double commentRecordDistortion,
        double commentAuthenticity,
        double templateCommentSaturation,
        double commentUniqueInformationShare,
        double commentReviewBurden,
        double commentProceduralAckRate,
        double commentSubstantiveUptake,
        double commentCompressionRate,
        double technicalClaimCredibility,
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
        double administrativeCostIndex
) {
    public double captureControlScore() {
        return MetricDefinition.average(
                MetricDefinition.lowerIsBetter(captureRate),
                MetricDefinition.lowerIsBetter(averageCaptureIndex),
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
                antiCaptureSuccessRate
        );
    }

    public double representationScore() {
        return MetricDefinition.average(
                averagePublicInterestScore,
                MetricDefinition.lowerIsBetter(largeDonorDependence),
                MetricDefinition.lowerIsBetter(donorInfluenceGini),
                voucherParticipationRate,
                publicFinancingShare,
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
        return MetricDefinition.average(captureControlScore(), representationScore(), reformFeasibilityScore());
    }
}
