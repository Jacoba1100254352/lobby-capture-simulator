package lobbycapture.metrics;


import lobbycapture.arena.ContestOutcome;
import lobbycapture.policy.*;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.WorldState;
import lobbycapture.strategy.ChannelAllocation;
import lobbycapture.strategy.InfluenceChannel;
import lobbycapture.util.Values;

import java.util.ArrayList;
import java.util.List;


public final class MetricsAccumulator
{
	private final List<Double> runCaptureRates = new ArrayList<>();
	private final List<Double> runHiddenInfluenceShares = new ArrayList<>();
	private final List<Double> runTotalInfluenceDistortions = new ArrayList<>();
	private int totalContests;
	private int capturedContests;
	private int antiCaptureReforms;
	private int enactedAntiCaptureReforms;
	private int detectedCaptured;
	private int sanctionedCaptured;
	private int delayedByChallenge;
	private double captureIndexSum;
	private double publicInterestSum;
	private double publicPreferenceDistortionSum;
	private double privateGainRatioSum;
	private double totalSpendSum;
	private double clientFundingSum;
	private double donorInfluenceGiniSum;
	private double disclosureLagSum;
	private double lobbyingDisclosureLagSum;
	private double campaignDisclosureLagSum;
	private double defensiveSpendSum;
	private double truePublicBenefitSum;
	private double policyDistortionSum;
	private double hiddenCaptureIndexSum;
	private double totalInfluenceDistortionSum;
	private double substitutionRiskSum;
	private double regulatoryDriftSum;
	private double enforcementForbearanceSum;
	private double procurementBiasSum;
	private double darkMoneyTraceabilitySum;
	private double darkMoneyDirectVisibilitySum;
	private double largeDonorDependenceSum;
	private double voucherParticipationSum;
	private double voucherResidentParticipationSum;
	private double publicFinancingShareSum;
	private double publicFinancingCandidateUptakeSum;
	private double revolvingDoorInfluenceSum;
	private double commentRecordDistortionSum;
	private double commentAuthenticitySum;
	private double templateCommentSaturationSum;
	private double commentUniqueInformationSum;
	private double commentReviewBurdenSum;
	private double commentProceduralAckSum;
	private double commentSubstantiveUptakeSum;
	private double commentCompressionSum;
	private double commentFloodingSum;
	private double technicalClaimCredibilitySum;
	private double technicalRulemakingDistortionSum;
	private double channelSwitchSum;
	private double evasionShiftSum;
	private double evasionPenaltySum;
	private double substitutionPressureSum;
	private double influencePreservationSum;
	private double hiddenInfluenceSum;
	private double transparencyGainSum;
	private double messengerSubstitutionSum;
	private double venueSubstitutionSum;
	private double switchScoreEqualWeightSum;
	private double switchScoreAnonymityHeavySum;
	private double switchScoreEnforcementCostHeavySum;
	private double switchDisclosureCostSum;
	private double clientFundingAdaptationSum;
	private double regulatorAttentionSum;
	private double regulatorQueueSum;
	private double watchdogFocusSum;
	private double watchdogBudgetConcentrationSum;
	private double adaptationSpeedSum;
	private double reformDecayPressureSum;
	private double administrativeCostSum;
	private double legitimateAdvocacyChillSum;
	private double visibleLobbyingSpendSum;
	private double intermediarySpendSum;
	private double enforcementCapacitySum;
	private double reportingErrorDetectionSum;
	private double networkOpacitySum;
	private double donorNetworkConcentrationSum;
	private double intermediaryCentralitySum;
	private double officialAccessCentralitySum;
	private double procurementNetworkExposureSum;
	private double revolvingDoorBridgeSum;
	private double commentNetworkLoadSum;
	private double venueShiftNetworkLoadSum;
	private double networkLegibilitySum;
	private double crossVenueDetectionSum;
	private double participationProtectionSum;
	private double speechRestrictionRiskSum;
	private ChannelAllocation allocationSum = ChannelAllocation.zero();
	
	private static double legitimateAdvocacyChill(ContestOutcome outcome, ReformRegime reform) {
		return Values.clamp(
				(0.30 * reform.speechRestrictionRisk())
						+ (0.22 * reform.falsePositiveCost())
						+ (0.20 * outcome.administrativeCost())
						+ (0.10 * reform.antiAstroturfStrength())
						- (0.18 * reform.participationProtectionStrength()),
				0.0,
				1.0
		);
	}
	
	private static double ratio(int numerator, int denominator) {
		return denominator == 0 ? 0.0 : (double) numerator / denominator;
	}
	
	private static double hiddenCaptureIndex(ContestOutcome outcome, double totalSpend) {
		double defensiveShare = totalSpend == 0.0 ? 0.0 : outcome.influenceResult().defensiveSpend() / totalSpend;
		double privateUpside = Values.clamp(CaptureScoring.privateGainRatio(outcome.contest()) / 5.0, 0.0, 1.0);
		double hiddenCarrier = Values.clamp(
				(0.48 * outcome.influenceResult().hiddenInfluenceShare())
						+ (0.18 * outcome.influenceResult().influencePreservationRate())
						+ (0.14 * outcome.influenceResult().messengerSubstitutionRate())
						+ (0.10 * outcome.influenceResult().venueSubstitutionRate())
						+ (0.10 * defensiveShare),
				0.0,
				1.0
		);
		double capturePressure = Values.clamp(
				(0.34 * outcome.captureIndex())
						+ (0.20 * outcome.policyDistortion())
						+ (0.16 * privateUpside)
						+ (0.12 * outcome.enforcementForbearance())
						+ (0.10 * outcome.procurementBias())
						+ (0.08 * (outcome.captured() ? 1.0 : 0.0)),
				0.0,
				1.0
		);
		return Values.clamp(hiddenCarrier * (0.34 + (0.66 * capturePressure)), 0.0, 1.0);
	}
	
	private static double totalInfluenceDistortion(
			ContestOutcome outcome,
			double hiddenCaptureIndex,
			double commentFloodingIndex,
			double technicalRulemakingDistortion,
			double networkOpacity,
			double intermediaryCentrality,
			double procurementNetworkExposure,
			double venueShiftNetworkLoad
	) {
		return Values.clamp(
				(0.16 * (outcome.captured() ? 1.0 : 0.0))
						+ (0.16 * outcome.captureIndex())
						+ (0.15 * hiddenCaptureIndex)
						+ (0.12 * outcome.policyDistortion())
						+ (0.09 * outcome.influenceResult().hiddenInfluenceShare())
						+ (0.08 * outcome.influenceResult().influencePreservationRate())
						+ (0.07 * outcome.procurementBias())
						+ (0.06 * outcome.enforcementForbearance())
						+ (0.05 * commentFloodingIndex)
						+ (0.04 * technicalRulemakingDistortion)
						+ (0.04 * networkOpacity)
						+ (0.03 * intermediaryCentrality)
						+ (0.03 * procurementNetworkExposure)
						+ (0.03 * venueShiftNetworkLoad)
						+ (0.02 * outcome.administrativeCost()),
				0.0,
				1.0
		);
	}
	
	private static double substitutionRisk(
			ContestOutcome outcome,
			double hiddenCaptureIndex,
			double totalSpend,
			double networkOpacity,
			double venueShiftNetworkLoad
	) {
		double defensiveShare = totalSpend == 0.0 ? 0.0 : outcome.influenceResult().defensiveSpend() / totalSpend;
		return Values.clamp(
				(0.30 * hiddenCaptureIndex)
						+ (0.22 * outcome.influenceResult().hiddenInfluenceShare())
						+ (0.18 * outcome.influenceResult().influencePreservationRate())
						+ (0.12 * outcome.influenceResult().venueSubstitutionRate())
						+ (0.10 * outcome.influenceResult().messengerSubstitutionRate())
						+ (0.08 * defensiveShare)
						+ (0.06 * networkOpacity)
						+ (0.05 * venueShiftNetworkLoad),
				0.0,
				1.0
		);
	}
	
	private static double commentFloodingIndex(PolicyContest contest, CommentTriageReport triage) {
		return Values.clamp(
				(0.36 * triage.reviewBurden())
						+ (0.26 * contest.docket().templateSaturation())
						+ (0.18 * contest.commentRecordDistortion())
						+ (0.12 * (1.0 - triage.authenticationConfidence()))
						+ (0.08 * (1.0 - triage.duplicateCompressionRate())),
				0.0,
				1.0
		);
	}
	
	private static double technicalRulemakingDistortion(PolicyContest contest, CommentTriageReport triage) {
		if (contest.arena() != ContestArena.RULEMAKING && contest.arena() != ContestArena.PUBLIC_INFORMATION) {
			return 0.0;
		}
		return Values.clamp(
				(0.34 * contest.technicalComplexity())
						+ (0.22 * contest.informationDistortion())
						+ (0.18 * triage.recordDistortion())
						+ (0.14 * triage.reviewBurden())
						+ (0.12 * (1.0 - triage.substantiveUptakeRate())),
				0.0,
				1.0
		);
	}
	
	private static double enforcementCapacity(PolicyContest contest, WorldState world, ReformRegime reform) {
		return Values.clamp(
				(0.30 * reform.enforcementBudget())
						+ (0.22 * reform.auditRate())
						+ (0.18 * reform.sanctionSeverity())
						+ (0.18 * world.regulatorAttention(contest.issueDomain()))
						+ (0.12 * world.averageWatchdogFocus())
						- (0.18 * world.regulatorQueue(contest.issueDomain())),
				0.0,
				1.0
		);
	}

	private static double reportingErrorDetectionRate(
			ContestOutcome outcome,
			ReformRegime reform,
			ChannelAllocation allocation,
			double enforcementCapacity
	) {
		double regulatedLobbyingSurface = Values.clamp(
				(0.48 * allocation.share(InfluenceChannel.DIRECT_ACCESS))
						+ (0.24 * allocation.share(InfluenceChannel.AGENDA_ACCESS))
						+ (0.16 * allocation.share(InfluenceChannel.PUBLIC_CAMPAIGN))
						+ (0.12 * allocation.share(InfluenceChannel.INTERMEDIARY)),
				0.0,
				1.0
		);
		double disclosureFriction = Values.clamp(
				(0.56 * outcome.influenceResult().lobbyingDisclosureLag())
						+ (0.22 * (1.0 - reform.realTimeDisclosure()))
						+ (0.14 * (1.0 - reform.contactLogCoverage()))
						+ (0.08 * outcome.influenceResult().switchDisclosureCost()),
				0.0,
				1.0
		);
		double reportingErrorRisk = Values.clamp(
				0.035 + (0.12 * disclosureFriction) + (0.08 * regulatedLobbyingSurface),
				0.0,
				1.0
		);
		double detectionSurface = Values.clamp(
				(0.36 * enforcementCapacity)
						+ (0.24 * reform.auditRate())
						+ (0.20 * reform.contactLogCoverage())
						+ (0.12 * reform.disclosureStrength())
						+ (0.08 * reform.crossVenueDetectionStrength()),
				0.0,
				1.0
		);
		return Values.clamp(reportingErrorRisk * (0.46 + (0.72 * detectionSurface)), 0.0, 1.0);
	}
	
	private static double stdDev(List<Double> values) {
		if (values.size() < 2) {
			return 0.0;
		}
		double average = values.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
		double variance = values.stream()
		                        .mapToDouble(value -> {
			                        double delta = value - average;
			                        return delta * delta;
		                        })
		                        .sum() / (values.size() - 1);
		return Math.sqrt(variance);
	}
	
	private static double voucherResidentParticipation(ReformRegime reform, double publicFinancingSourceShare) {
		return Values.clamp(
				0.008
						+ (0.070 * reform.democracyVoucherStrength())
						+ (0.020 * publicFinancingSourceShare),
				0.0,
				1.0
		);
	}
	
	private static double publicFinancingCandidateUptake(ReformRegime reform, double largeDonorDependence) {
		return Values.clamp(
				0.18
						+ (0.68 * reform.publicFinancingStrength())
						+ (0.10 * reform.democracyVoucherStrength())
						- (0.16 * largeDonorDependence),
				0.0,
				1.0
		);
	}

	private static double largeDonorDependence(
			PolicyContest contest,
			WorldState world,
			ReformRegime reform,
			ChannelAllocation allocation,
			double ledgerLargeDonorDependence
	) {
		double ledgerEstimate = ledgerLargeDonorDependence == 0.0
				? Values.clamp(Math.max(contest.campaignFinanceInfluence(), contest.darkMoneyInfluence()), 0.0, 1.0)
				: ledgerLargeDonorDependence;
		double sourceEstimate = Values.clamp(
				(0.58 * world.calibratedLargeDonorShare(contest.issueDomain()))
						+ (0.42 * world.calibratedDonorConcentrationIndex(contest.issueDomain())),
				0.0,
				0.82
		);
		double moneyChannelShare = allocation.total() == 0.0
				? 0.0
				: allocation.share(InfluenceChannel.CAMPAIGN_FINANCE) + allocation.share(InfluenceChannel.DARK_MONEY);
		double moneyPressure = Values.clamp(
				(0.50 * moneyChannelShare)
						+ (0.25 * contest.campaignFinanceInfluence())
						+ (0.25 * contest.darkMoneyInfluence()),
				0.0,
				1.0
		);
		double publicFinancingCounterweight = Values.clamp(
				(0.55 * reform.publicFinancingStrength())
						+ (0.25 * reform.democracyVoucherStrength())
						+ (0.20 * reform.campaignFinanceCounterweight()),
				0.0,
				1.0
		);
		double sourceWeight = Values.clamp(
				0.15 + (0.60 * moneyPressure) - (0.35 * publicFinancingCounterweight),
				0.0,
				0.75
		);
		return Values.clamp(
				((1.0 - sourceWeight) * ledgerEstimate) + (sourceWeight * sourceEstimate),
				0.0,
				1.0
		);
	}
	
	private static double commentReviewCapacity(PolicyContest contest, WorldState world, ReformRegime reform) {
		return Values.clamp(
				0.30
						+ (0.28 * world.regulatorAttention(contest.issueDomain()))
						+ (0.16 * reform.blindReviewStrength())
						+ (0.14 * reform.publicAdvocateStrength())
						+ (0.12 * reform.antiAstroturfStrength())
						- (0.20 * world.regulatorQueue(contest.issueDomain())),
				0.0,
				1.0
		);
	}
	
	public void add(ContestOutcome outcome, WorldState world) {
		totalContests++;
		ReformRegime reform = world.reformRegime();
		PolicyContest contest = outcome.contest();
		if (outcome.captured()) {
			capturedContests++;
		}
		if (contest.antiCaptureReform()) {
			antiCaptureReforms++;
			if (outcome.antiCaptureReformEnacted()) {
				enactedAntiCaptureReforms++;
			}
		}
		if (outcome.detected()) {
			detectedCaptured++;
		}
		if (outcome.sanctioned()) {
			sanctionedCaptured++;
		}
		if (outcome.delayedByChallenge()) {
			delayedByChallenge++;
		}
		ChannelAllocation allocation = outcome.influenceResult().allocation();
		allocationSum = allocationSum.plus(allocation);
		double totalSpend = outcome.influenceResult().totalSpend();
		totalSpendSum += totalSpend;
		clientFundingSum += outcome.influenceResult().clientFunding();
		donorInfluenceGiniSum += Values.clamp(
				(0.45 * outcome.influenceResult().donorInfluenceGini())
						+ (0.55 * world.calibratedDonorConcentrationIndex(contest.issueDomain())),
				0.0,
				1.0
		);
		disclosureLagSum += outcome.influenceResult().averageDisclosureLag();
		lobbyingDisclosureLagSum += outcome.influenceResult().lobbyingDisclosureLag();
		campaignDisclosureLagSum += outcome.influenceResult().campaignDisclosureLag();
		defensiveSpendSum += outcome.influenceResult().defensiveSpend();
		captureIndexSum += outcome.captureIndex();
		publicInterestSum += outcome.publicInterestScore();
		publicPreferenceDistortionSum += contest.publicPreferenceDistortion();
		privateGainRatioSum += CaptureScoring.privateGainRatio(contest);
		truePublicBenefitSum += contest.truePublicBenefit();
		policyDistortionSum += outcome.policyDistortion();
		regulatoryDriftSum += outcome.regulatoryDrift();
		enforcementForbearanceSum += outcome.enforcementForbearance();
		procurementBiasSum += outcome.procurementBias();
		double ledgerTraceability = world.contributionLedger().averageTraceability();
		darkMoneyTraceabilitySum += ledgerTraceability == 0.0
				? Values.clamp(1.0 - contest.darkMoneyInfluence(), 0.0, 1.0)
				: ledgerTraceability;
		darkMoneyDirectVisibilitySum += world.contributionLedger().darkMoneyDirectVisibility();
		double ledgerLargeDonorDependence = world.contributionLedger().largeDonorDependence();
		double reportedLargeDonorDependence = largeDonorDependence(
				contest,
				world,
				reform,
				allocation,
				ledgerLargeDonorDependence
		);
		largeDonorDependenceSum += reportedLargeDonorDependence;
		voucherParticipationSum += reform.democracyVoucherStrength();
		voucherResidentParticipationSum += voucherResidentParticipation(reform, world.contributionLedger().publicFinancingSourceShare());
		publicFinancingShareSum += Values.clamp(
				(0.72 * reform.publicFinancingStrength())
						+ (0.28 * world.calibratedPublicFinancingSourceShare(contest.issueDomain())),
				0.0,
				1.0
		);
		publicFinancingCandidateUptakeSum += publicFinancingCandidateUptake(reform, reportedLargeDonorDependence);
		revolvingDoorInfluenceSum += contest.revolvingDoorInfluence();
		commentRecordDistortionSum += contest.commentRecordDistortion();
		templateCommentSaturationSum += contest.docket().templateSaturation();
		CommentTriageReport triage = CommentTriageModel.triage(contest.docket(), contest, reform, commentReviewCapacity(contest, world, reform));
		commentAuthenticitySum += triage.authenticationConfidence();
		commentUniqueInformationSum += triage.uniqueInformationShare();
		commentReviewBurdenSum += triage.reviewBurden();
		commentProceduralAckSum += triage.proceduralAckRate();
		commentSubstantiveUptakeSum += triage.substantiveUptakeRate();
		commentCompressionSum += triage.duplicateCompressionRate();
		technicalClaimCredibilitySum += contest.docket().technicalClaimCredibility();
		double commentFloodingIndex = commentFloodingIndex(contest, triage);
		double technicalRulemakingDistortion = technicalRulemakingDistortion(contest, triage);
		double enforcementCapacity = enforcementCapacity(contest, world, reform);
		double reportingErrorDetectionRate = reportingErrorDetectionRate(outcome, reform, allocation, enforcementCapacity);
		double hiddenCaptureIndex = hiddenCaptureIndex(outcome, totalSpend);
		var network = outcome.influenceResult().networkSnapshot();
		commentFloodingSum += commentFloodingIndex;
		technicalRulemakingDistortionSum += technicalRulemakingDistortion;
		enforcementCapacitySum += enforcementCapacity;
		reportingErrorDetectionSum += reportingErrorDetectionRate;
		networkOpacitySum += network.networkOpacityIndex();
		donorNetworkConcentrationSum += network.donorNetworkConcentration();
		intermediaryCentralitySum += network.intermediaryCentrality();
		officialAccessCentralitySum += network.officialAccessCentrality();
		procurementNetworkExposureSum += network.procurementNetworkExposure();
		revolvingDoorBridgeSum += network.revolvingDoorBridgeIndex();
		commentNetworkLoadSum += network.commentNetworkLoad();
		venueShiftNetworkLoadSum += network.venueShiftNetworkLoad();
		networkLegibilitySum += network.networkLegibilityIndex();
		hiddenCaptureIndexSum += hiddenCaptureIndex;
		totalInfluenceDistortionSum += totalInfluenceDistortion(
				outcome,
				hiddenCaptureIndex,
				commentFloodingIndex,
				technicalRulemakingDistortion,
				network.networkOpacityIndex(),
				network.intermediaryCentrality(),
				network.procurementNetworkExposure(),
				network.venueShiftNetworkLoad()
		);
		substitutionRiskSum += substitutionRisk(outcome, hiddenCaptureIndex, totalSpend, network.networkOpacityIndex(), network.venueShiftNetworkLoad());
		channelSwitchSum += outcome.influenceResult().channelSwitches();
		evasionShiftSum += outcome.influenceResult().evasionShifts();
		evasionPenaltySum += outcome.evasionPenalty();
		substitutionPressureSum += outcome.influenceResult().substitutionPressure();
		influencePreservationSum += outcome.influenceResult().influencePreservationRate();
		hiddenInfluenceSum += outcome.influenceResult().hiddenInfluenceShare();
		transparencyGainSum += outcome.influenceResult().netTransparencyGain();
		messengerSubstitutionSum += outcome.influenceResult().messengerSubstitutionRate();
		venueSubstitutionSum += outcome.influenceResult().venueSubstitutionRate();
		switchScoreEqualWeightSum += outcome.influenceResult().switchScoreEqualWeight();
		switchScoreAnonymityHeavySum += outcome.influenceResult().switchScoreAnonymityHeavy();
		switchScoreEnforcementCostHeavySum += outcome.influenceResult().switchScoreEnforcementCostHeavy();
		switchDisclosureCostSum += outcome.influenceResult().switchDisclosureCost();
		clientFundingAdaptationSum += world.averageClientFundingMultiplier();
		regulatorAttentionSum += world.averageRegulatorAttention();
		regulatorQueueSum += world.averageRegulatorQueue();
		watchdogFocusSum += world.averageWatchdogFocus();
		watchdogBudgetConcentrationSum += world.watchdogBudgetConcentration();
		adaptationSpeedSum += world.lastAdaptationSpeed();
		reformDecayPressureSum += world.lastReformDecayPressure();
		administrativeCostSum += outcome.administrativeCost();
		legitimateAdvocacyChillSum += legitimateAdvocacyChill(outcome, reform);
		crossVenueDetectionSum += reform.crossVenueDetectionStrength();
		participationProtectionSum += reform.participationProtectionStrength();
		speechRestrictionRiskSum += reform.speechRestrictionRisk();
		visibleLobbyingSpendSum += allocation.directAccess()
				+ allocation.agendaAccess()
				+ allocation.publicCampaign()
				+ allocation.campaignFinance();
		intermediarySpendSum += allocation.intermediary();
	}
	
	public void recordRun(MetricsAccumulator runMetrics) {
		if (runMetrics.totalContests == 0) {
			return;
		}
		runCaptureRates.add(runMetrics.captureRateValue());
		runHiddenInfluenceShares.add(runMetrics.hiddenInfluenceShareValue());
		runTotalInfluenceDistortions.add(runMetrics.totalInfluenceDistortionValue());
	}
	
	public ScenarioReport toReport(String scenarioKey, String scenarioName) {
		double totalSpend = totalSpendSum;
		double total = Math.max(1.0, totalContests);
		return new ScenarioReport(
				scenarioKey,
				scenarioName,
				totalContests,
				capturedContests,
				antiCaptureReforms,
				enactedAntiCaptureReforms,
				ratio(capturedContests, totalContests),
				ratio(enactedAntiCaptureReforms, antiCaptureReforms),
				ratio(capturedContests, totalContests),
				hiddenCaptureIndexSum / total,
				totalInfluenceDistortionSum / total,
				substitutionRiskSum / total,
				captureIndexSum / total,
				publicInterestSum / total,
				publicPreferenceDistortionSum / total,
				privateGainRatioSum / total,
				totalSpendSum / total,
				clientFundingSum / total,
				donorInfluenceGiniSum / total,
				disclosureLagSum / total,
				lobbyingDisclosureLagSum / total,
				campaignDisclosureLagSum / total,
				totalSpend == 0.0 ? 0.0 : defensiveSpendSum / totalSpend,
				totalSpend == 0.0 ? 0.0 : captureIndexSum / totalSpend,
				totalSpend == 0.0 ? 0.0 : truePublicBenefitSum / totalSpend,
				totalSpend == 0.0 ? 0.0 : visibleLobbyingSpendSum / totalSpend,
				allocationSum.share(InfluenceChannel.DIRECT_ACCESS),
				allocationSum.share(InfluenceChannel.AGENDA_ACCESS),
				allocationSum.share(InfluenceChannel.INFORMATION_DISTORTION),
				allocationSum.share(InfluenceChannel.PUBLIC_CAMPAIGN),
				allocationSum.share(InfluenceChannel.LITIGATION_THREAT),
				allocationSum.share(InfluenceChannel.CAMPAIGN_FINANCE),
				allocationSum.share(InfluenceChannel.DARK_MONEY),
				allocationSum.share(InfluenceChannel.REVOLVING_DOOR),
				allocationSum.share(InfluenceChannel.INTERMEDIARY),
				allocationSum.share(InfluenceChannel.DEFENSIVE_REFORM),
				ratio(detectedCaptured, totalContests),
				reportingErrorDetectionSum / total,
				ratio(sanctionedCaptured, totalContests),
				enforcementCapacitySum / total,
				policyDistortionSum / total,
				regulatoryDriftSum / total,
				enforcementForbearanceSum / total,
				procurementBiasSum / total,
				darkMoneyTraceabilitySum / total,
				darkMoneyDirectVisibilitySum / total,
				largeDonorDependenceSum / total,
				voucherParticipationSum / total,
				voucherResidentParticipationSum / total,
				publicFinancingShareSum / total,
				publicFinancingCandidateUptakeSum / total,
				revolvingDoorInfluenceSum / total,
				commentRecordDistortionSum / total,
				commentAuthenticitySum / total,
				templateCommentSaturationSum / total,
				commentUniqueInformationSum / total,
				commentReviewBurdenSum / total,
				commentProceduralAckSum / total,
				commentSubstantiveUptakeSum / total,
				commentCompressionSum / total,
				commentFloodingSum / total,
				technicalClaimCredibilitySum / total,
				technicalRulemakingDistortionSum / total,
				channelSwitchSum / total,
				evasionShiftSum / total,
				evasionPenaltySum / total,
				substitutionPressureSum / total,
				influencePreservationSum / total,
				hiddenInfluenceSum / total,
				transparencyGainSum / total,
				messengerSubstitutionSum / total,
				venueSubstitutionSum / total,
				clientFundingAdaptationSum / total,
				regulatorAttentionSum / total,
				regulatorQueueSum / total,
				watchdogFocusSum / total,
				watchdogBudgetConcentrationSum / total,
				adaptationSpeedSum / total,
				reformDecayPressureSum / total,
				legitimateAdvocacyChillSum / total,
				ratio(delayedByChallenge, totalContests),
				administrativeCostSum / total,
				stdDev(runCaptureRates),
				stdDev(runHiddenInfluenceShares),
				stdDev(runTotalInfluenceDistortions),
				networkOpacitySum / total,
				donorNetworkConcentrationSum / total,
				intermediaryCentralitySum / total,
				officialAccessCentralitySum / total,
				procurementNetworkExposureSum / total,
				revolvingDoorBridgeSum / total,
				commentNetworkLoadSum / total,
				venueShiftNetworkLoadSum / total,
				networkLegibilitySum / total,
				crossVenueDetectionSum / total,
				participationProtectionSum / total,
				speechRestrictionRiskSum / total,
				switchScoreEqualWeightSum / total,
				switchScoreAnonymityHeavySum / total,
				switchScoreEnforcementCostHeavySum / total,
				switchDisclosureCostSum / total
		);
	}
	
	private double captureRateValue() {
		return ratio(capturedContests, totalContests);
	}
	
	private double hiddenInfluenceShareValue() {
		return totalContests == 0 ? 0.0 : hiddenInfluenceSum / totalContests;
	}
	
	private double totalInfluenceDistortionValue() {
		return totalContests == 0 ? 0.0 : totalInfluenceDistortionSum / totalContests;
	}
}
