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
        double channelSwitchRate,
        double evasionShiftRate,
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
                antiCaptureSuccessRate
        );
    }

    public double representationScore() {
        return MetricDefinition.average(
                averagePublicInterestScore,
                MetricDefinition.lowerIsBetter(largeDonorDependence),
                voucherParticipationRate,
                publicFinancingShare,
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

