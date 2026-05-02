package lobbycapture.metrics;

import lobbycapture.arena.ContestOutcome;
import lobbycapture.policy.CaptureScoring;
import lobbycapture.policy.CommentTriageModel;
import lobbycapture.policy.CommentTriageReport;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.WorldState;
import lobbycapture.strategy.ChannelAllocation;
import lobbycapture.util.Values;

public final class MetricsAccumulator {
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
    private double defensiveSpendSum;
    private double truePublicBenefitSum;
    private double policyDistortionSum;
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
    private double technicalClaimCredibilitySum;
    private double channelSwitchSum;
    private double evasionShiftSum;
    private double evasionPenaltySum;
    private double substitutionPressureSum;
    private double influencePreservationSum;
    private double hiddenInfluenceSum;
    private double transparencyGainSum;
    private double messengerSubstitutionSum;
    private double venueSubstitutionSum;
    private double clientFundingAdaptationSum;
    private double regulatorAttentionSum;
    private double regulatorQueueSum;
    private double watchdogFocusSum;
    private double watchdogBudgetConcentrationSum;
    private double adaptationSpeedSum;
    private double reformDecayPressureSum;
    private double administrativeCostSum;
    private ChannelAllocation allocationSum = ChannelAllocation.zero();

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
        donorInfluenceGiniSum += outcome.influenceResult().donorInfluenceGini();
        disclosureLagSum += outcome.influenceResult().averageDisclosureLag();
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
        largeDonorDependenceSum += ledgerLargeDonorDependence == 0.0
                ? Values.clamp(contest.campaignFinanceInfluence(), 0.0, 1.0)
                : ledgerLargeDonorDependence;
        voucherParticipationSum += reform.democracyVoucherStrength();
        voucherResidentParticipationSum += voucherResidentParticipation(reform, world.contributionLedger().publicFinancingSourceShare());
        publicFinancingShareSum += reform.publicFinancingStrength();
        publicFinancingCandidateUptakeSum += publicFinancingCandidateUptake(reform, ledgerLargeDonorDependence);
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
        channelSwitchSum += outcome.influenceResult().channelSwitches();
        evasionShiftSum += outcome.influenceResult().evasionShifts();
        evasionPenaltySum += outcome.evasionPenalty();
        substitutionPressureSum += outcome.influenceResult().substitutionPressure();
        influencePreservationSum += outcome.influenceResult().influencePreservationRate();
        hiddenInfluenceSum += outcome.influenceResult().hiddenInfluenceShare();
        transparencyGainSum += outcome.influenceResult().netTransparencyGain();
        messengerSubstitutionSum += outcome.influenceResult().messengerSubstitutionRate();
        venueSubstitutionSum += outcome.influenceResult().venueSubstitutionRate();
        clientFundingAdaptationSum += world.averageClientFundingMultiplier();
        regulatorAttentionSum += world.averageRegulatorAttention();
        regulatorQueueSum += world.averageRegulatorQueue();
        watchdogFocusSum += world.averageWatchdogFocus();
        watchdogBudgetConcentrationSum += world.watchdogBudgetConcentration();
        adaptationSpeedSum += world.lastAdaptationSpeed();
        reformDecayPressureSum += world.lastReformDecayPressure();
        administrativeCostSum += outcome.administrativeCost();
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
                captureIndexSum / total,
                publicInterestSum / total,
                publicPreferenceDistortionSum / total,
                privateGainRatioSum / total,
                totalSpendSum / total,
                clientFundingSum / total,
                donorInfluenceGiniSum / total,
                disclosureLagSum / total,
                totalSpend == 0.0 ? 0.0 : defensiveSpendSum / totalSpend,
                totalSpend == 0.0 ? 0.0 : captureIndexSum / totalSpend,
                totalSpend == 0.0 ? 0.0 : truePublicBenefitSum / totalSpend,
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.DIRECT_ACCESS),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.AGENDA_ACCESS),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.INFORMATION_DISTORTION),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.PUBLIC_CAMPAIGN),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.LITIGATION_THREAT),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.CAMPAIGN_FINANCE),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.DARK_MONEY),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.REVOLVING_DOOR),
                allocationSum.share(lobbycapture.strategy.InfluenceChannel.DEFENSIVE_REFORM),
                ratio(detectedCaptured, totalContests),
                ratio(sanctionedCaptured, totalContests),
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
                technicalClaimCredibilitySum / total,
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
                legitimateAdvocacyChill(),
                ratio(delayedByChallenge, totalContests),
                administrativeCostSum / total
        );
    }

    private double legitimateAdvocacyChill() {
        if (totalContests == 0) {
            return 0.0;
        }
        double lowSpendPressure = totalSpendSum / totalContests < 0.08 ? 0.08 : 0.0;
        return Values.clamp(lowSpendPressure + (administrativeCostSum / Math.max(1.0, totalContests) * 0.18), 0.0, 1.0);
    }

    private static double ratio(int numerator, int denominator) {
        return denominator == 0 ? 0.0 : (double) numerator / denominator;
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
}
