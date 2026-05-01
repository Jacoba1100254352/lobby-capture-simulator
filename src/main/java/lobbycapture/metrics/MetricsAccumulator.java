package lobbycapture.metrics;

import lobbycapture.arena.ContestOutcome;
import lobbycapture.policy.CaptureScoring;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
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
    private double largeDonorDependenceSum;
    private double voucherParticipationSum;
    private double publicFinancingShareSum;
    private double revolvingDoorInfluenceSum;
    private double commentRecordDistortionSum;
    private double commentAuthenticitySum;
    private double templateCommentSaturationSum;
    private double technicalClaimCredibilitySum;
    private double channelSwitchSum;
    private double evasionShiftSum;
    private double evasionPenaltySum;
    private double administrativeCostSum;
    private ChannelAllocation allocationSum = ChannelAllocation.zero();

    public void add(ContestOutcome outcome, ReformRegime reform) {
        totalContests++;
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
        darkMoneyTraceabilitySum += Values.clamp(1.0 - contest.darkMoneyInfluence(), 0.0, 1.0);
        largeDonorDependenceSum += Values.clamp(contest.campaignFinanceInfluence(), 0.0, 1.0);
        voucherParticipationSum += reform.democracyVoucherStrength();
        publicFinancingShareSum += reform.publicFinancingStrength();
        revolvingDoorInfluenceSum += contest.revolvingDoorInfluence();
        commentRecordDistortionSum += contest.commentRecordDistortion();
        commentAuthenticitySum += contest.docket().authenticityShare();
        templateCommentSaturationSum += contest.docket().templateSaturation();
        technicalClaimCredibilitySum += contest.docket().technicalClaimCredibility();
        channelSwitchSum += outcome.influenceResult().channelSwitches();
        evasionShiftSum += outcome.influenceResult().evasionShifts();
        evasionPenaltySum += outcome.evasionPenalty();
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
                largeDonorDependenceSum / total,
                voucherParticipationSum / total,
                publicFinancingShareSum / total,
                revolvingDoorInfluenceSum / total,
                commentRecordDistortionSum / total,
                commentAuthenticitySum / total,
                templateCommentSaturationSum / total,
                technicalClaimCredibilitySum / total,
                channelSwitchSum / total,
                evasionShiftSum / total,
                evasionPenaltySum / total,
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
}
