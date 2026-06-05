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
		double substitutionRisk,
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
		double totalInfluenceDistortionSeedStdDev,
		double networkOpacityIndex,
		double donorNetworkConcentration,
		double intermediaryCentrality,
		double officialAccessCentrality,
		double procurementNetworkExposure,
		double revolvingDoorBridgeIndex,
		double commentNetworkLoad,
		double venueShiftNetworkLoad,
		double networkLegibilityIndex,
		double crossVenueDetectionIndex,
		double participationProtectionIndex,
		double speechRestrictionRisk,
		double switchScoreEqualWeight,
		double switchScoreAnonymityHeavy,
		double switchScoreEnforcementCostHeavy,
		double switchDisclosureCost
)
{
	public double captureControlScore() {
		return MetricDefinition.average(
				MetricDefinition.lowerIsBetter(observedCaptureRate),
				MetricDefinition.lowerIsBetter(averageCaptureIndex),
				MetricDefinition.lowerIsBetter(hiddenCaptureIndex),
				MetricDefinition.lowerIsBetter(totalInfluenceDistortion),
				MetricDefinition.lowerIsBetter(substitutionRisk),
				MetricDefinition.lowerIsBetter(privateGainRatio / 5.0),
				MetricDefinition.lowerIsBetter(publicPreferenceDistortion),
				MetricDefinition.lowerIsBetter(enforcementForbearanceRate),
				MetricDefinition.lowerIsBetter(evasionPenaltyRate),
				MetricDefinition.lowerIsBetter(hiddenInfluenceShare),
				MetricDefinition.lowerIsBetter(influencePreservationRate),
				MetricDefinition.lowerIsBetter(regulatorQueueBacklog),
				MetricDefinition.lowerIsBetter(reformDecayPressure),
				MetricDefinition.normalizeSigned(netTransparencyGain),
				crossVenueDetectionIndex,
				regulatorAttentionIndex,
				watchdogFocusIndex,
				enforcementCapacityIndex,
				antiCaptureSuccessRate * MetricDefinition.lowerIsBetter(substitutionRisk)
		);
	}
	
	public double distortionMinimizationScore() {
		return MetricDefinition.average(
				MetricDefinition.lowerIsBetter(totalInfluenceDistortion),
				MetricDefinition.lowerIsBetter(substitutionRisk),
				MetricDefinition.lowerIsBetter(hiddenCaptureIndex),
				MetricDefinition.lowerIsBetter(networkOpacityIndex),
				MetricDefinition.lowerIsBetter(venueShiftNetworkLoad),
				MetricDefinition.lowerIsBetter(speechRestrictionRisk),
				MetricDefinition.lowerIsBetter(administrativeCostIndex),
				crossVenueDetectionIndex
		);
	}

	public double designLoss() {
		return Math.max(
				0.0,
				(0.30 * totalInfluenceDistortion)
						+ (0.20 * hiddenCaptureIndex)
						+ (0.16 * substitutionRisk)
						+ (0.10 * administrativeCostIndex)
						+ (0.09 * networkOpacityIndex)
						+ (0.07 * legitimateAdvocacyChillRate)
						+ (0.06 * speechRestrictionRisk)
						- (0.05 * crossVenueDetectionIndex)
							- (0.03 * participationProtectionIndex)
		);
	}

	public double distortionObservedComponent() {
		return (0.16 * observedCaptureRate) + (0.16 * averageCaptureIndex);
	}

	public double distortionHiddenSubstitutionComponent() {
		return (0.15 * hiddenCaptureIndex)
				+ (0.09 * hiddenInfluenceShare)
				+ (0.08 * influencePreservationRate);
	}

	public double distortionInformationProcurementComponent() {
		return (0.12 * averagePolicyDistortion)
				+ (0.07 * procurementBiasIndex)
				+ (0.05 * commentFloodingIndex)
				+ (0.04 * technicalRulemakingDistortion);
	}

	public double distortionNetworkVenueComponent() {
		return (0.04 * networkOpacityIndex)
				+ (0.03 * intermediaryCentrality)
				+ (0.03 * procurementNetworkExposure)
				+ (0.03 * venueShiftNetworkLoad);
	}

	public double distortionProcessBurdenComponent() {
		return (0.06 * enforcementForbearanceRate) + (0.02 * administrativeCostIndex);
	}

	public double distortionRawComponentSum() {
		return distortionObservedComponent()
				+ distortionHiddenSubstitutionComponent()
				+ distortionInformationProcurementComponent()
				+ distortionNetworkVenueComponent()
				+ distortionProcessBurdenComponent();
	}

	public double representationScore() {
		return MetricDefinition.average(
				averagePublicInterestScore,
				MetricDefinition.lowerIsBetter(largeDonorDependence),
				MetricDefinition.lowerIsBetter(donorInfluenceGini),
				voucherResidentParticipation,
				publicFinancingCandidateUptake,
				participationProtectionIndex,
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
				MetricDefinition.lowerIsBetter(speechRestrictionRisk),
				participationProtectionIndex,
				detectionRate
		);
	}
	
	public double directionalScore() {
		return MetricDefinition.average(captureControlScore(), representationScore(), reformFeasibilityScore(), distortionMinimizationScore());
	}
}
