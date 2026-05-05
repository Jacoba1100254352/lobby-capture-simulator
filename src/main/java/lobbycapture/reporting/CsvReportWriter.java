package lobbycapture.reporting;

import lobbycapture.metrics.ScenarioReport;

import java.util.List;
import java.util.Locale;

public final class CsvReportWriter {
    public String write(List<ScenarioReport> reports, ReportProvenance provenance) {
        StringBuilder builder = new StringBuilder();
        builder.append("generatedAt,seed,runs,contestsPerRun,scenarioKey,scenarioName,totalContests,capturedContests,antiCaptureReforms,enactedAntiCaptureReforms,directionalScore,captureControl,representation,reformFeasibility,captureRate,captureRateLower95,captureRateUpper95,antiCaptureSuccess,antiCaptureSuccessLower95,antiCaptureSuccessUpper95,avgCaptureIndex,avgPublicInterest,publicPreferenceDistortion,privateGainRatio,lobbySpendPerContest,clientFundingPerContest,donorInfluenceGini,averageDisclosureLag,defensiveReformSpendShare,captureReturnOnSpend,publicBenefitPerInfluenceDollar,directAccessShare,agendaAccessShare,informationDistortionShare,publicCampaignShare,litigationThreatShare,campaignFinanceShare,darkMoneyShare,revolvingDoorShare,defensiveChannelShare,detectionRate,sanctionRate,policyDistortion,regulatoryDrift,enforcementForbearance,procurementBias,darkMoneyTraceability,darkMoneyDirectVisibility,largeDonorDependence,voucherParticipation,voucherResidentParticipation,publicFinancingShare,publicFinancingCandidateUptake,revolvingDoorInfluence,commentRecordDistortion,commentAuthenticity,templateCommentSaturation,commentUniqueInformationShare,commentReviewBurden,commentProceduralAckRate,commentSubstantiveUptake,commentCompressionRate,technicalClaimCredibility,channelSwitchRate,evasionShiftRate,evasionPenaltyRate,substitutionPressure,influencePreservationRate,hiddenInfluenceShare,netTransparencyGain,messengerSubstitutionRate,venueSubstitutionRate,clientFundingAdaptation,regulatorAttentionIndex,regulatorQueueBacklog,watchdogFocusIndex,watchdogBudgetConcentration,adaptationSpeed,reformDecayPressure,legitimateAdvocacyChill,constitutionalChallengeDelay,administrativeCost\n");
        for (ScenarioReport report : reports) {
            double[] captureInterval = wilsonInterval(report.capturedContests(), report.totalContests());
            double[] antiCaptureInterval = wilsonInterval(report.enactedAntiCaptureReforms(), report.antiCaptureReforms());
            builder.append(provenance.generatedAt()).append(',')
                    .append(provenance.seed()).append(',')
                    .append(provenance.runs()).append(',')
                    .append(provenance.contestsPerRun()).append(',')
                    .append(csv(report.scenarioKey())).append(',')
                    .append(csv(report.scenarioName())).append(',')
                    .append(report.totalContests()).append(',')
                    .append(report.capturedContests()).append(',')
                    .append(report.antiCaptureReforms()).append(',')
                    .append(report.enactedAntiCaptureReforms()).append(',')
                    .append(format(report.directionalScore())).append(',')
                    .append(format(report.captureControlScore())).append(',')
                    .append(format(report.representationScore())).append(',')
                    .append(format(report.reformFeasibilityScore())).append(',')
                    .append(format(report.captureRate())).append(',')
                    .append(format(captureInterval[0])).append(',')
                    .append(format(captureInterval[1])).append(',')
                    .append(format(report.antiCaptureSuccessRate())).append(',')
                    .append(format(antiCaptureInterval[0])).append(',')
                    .append(format(antiCaptureInterval[1])).append(',')
                    .append(format(report.averageCaptureIndex())).append(',')
                    .append(format(report.averagePublicInterestScore())).append(',')
                    .append(format(report.publicPreferenceDistortion())).append(',')
                    .append(format(report.privateGainRatio())).append(',')
                    .append(format(report.lobbySpendPerContest())).append(',')
                    .append(format(report.clientFundingPerContest())).append(',')
                    .append(format(report.donorInfluenceGini())).append(',')
                    .append(format(report.averageDisclosureLag())).append(',')
                    .append(format(report.defensiveReformSpendShare())).append(',')
                    .append(format(report.captureReturnOnSpend())).append(',')
                    .append(format(report.publicBenefitPerInfluenceDollar())).append(',')
                    .append(format(report.directAccessSpendShare())).append(',')
                    .append(format(report.agendaAccessSpendShare())).append(',')
                    .append(format(report.informationDistortionSpendShare())).append(',')
                    .append(format(report.publicCampaignSpendShare())).append(',')
                    .append(format(report.litigationThreatSpendShare())).append(',')
                    .append(format(report.campaignFinanceSpendShare())).append(',')
                    .append(format(report.darkMoneySpendShare())).append(',')
                    .append(format(report.revolvingDoorSpendShare())).append(',')
                    .append(format(report.defensiveChannelSpendShare())).append(',')
                    .append(format(report.detectionRate())).append(',')
                    .append(format(report.sanctionRate())).append(',')
                    .append(format(report.averagePolicyDistortion())).append(',')
                    .append(format(report.regulatoryDrift())).append(',')
                    .append(format(report.enforcementForbearanceRate())).append(',')
                    .append(format(report.procurementBiasIndex())).append(',')
                    .append(format(report.darkMoneyTraceability())).append(',')
                    .append(format(report.darkMoneyDirectVisibility())).append(',')
                    .append(format(report.largeDonorDependence())).append(',')
                    .append(format(report.voucherParticipationRate())).append(',')
                    .append(format(report.voucherResidentParticipation())).append(',')
                    .append(format(report.publicFinancingShare())).append(',')
                    .append(format(report.publicFinancingCandidateUptake())).append(',')
                    .append(format(report.revolvingDoorInfluence())).append(',')
                    .append(format(report.commentRecordDistortion())).append(',')
                    .append(format(report.commentAuthenticity())).append(',')
                    .append(format(report.templateCommentSaturation())).append(',')
                    .append(format(report.commentUniqueInformationShare())).append(',')
                    .append(format(report.commentReviewBurden())).append(',')
                    .append(format(report.commentProceduralAckRate())).append(',')
                    .append(format(report.commentSubstantiveUptake())).append(',')
                    .append(format(report.commentCompressionRate())).append(',')
                    .append(format(report.technicalClaimCredibility())).append(',')
                    .append(format(report.channelSwitchRate())).append(',')
                    .append(format(report.evasionShiftRate())).append(',')
                    .append(format(report.evasionPenaltyRate())).append(',')
                    .append(format(report.substitutionPressure())).append(',')
                    .append(format(report.influencePreservationRate())).append(',')
                    .append(format(report.hiddenInfluenceShare())).append(',')
                    .append(format(report.netTransparencyGain())).append(',')
                    .append(format(report.messengerSubstitutionRate())).append(',')
                    .append(format(report.venueSubstitutionRate())).append(',')
                    .append(format(report.clientFundingAdaptation())).append(',')
                    .append(format(report.regulatorAttentionIndex())).append(',')
                    .append(format(report.regulatorQueueBacklog())).append(',')
                    .append(format(report.watchdogFocusIndex())).append(',')
                    .append(format(report.watchdogBudgetConcentration())).append(',')
                    .append(format(report.adaptationSpeed())).append(',')
                    .append(format(report.reformDecayPressure())).append(',')
                    .append(format(report.legitimateAdvocacyChillRate())).append(',')
                    .append(format(report.constitutionalChallengeDelay())).append(',')
                    .append(format(report.administrativeCostIndex())).append('\n');
        }
        return builder.toString();
    }

    private static String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }

    static String format(double value) {
        return String.format(Locale.US, "%.4f", value);
    }

    static String formatWilsonInterval(int successes, int trials) {
        double[] interval = wilsonInterval(successes, trials);
        return "[" + format(interval[0]) + ", " + format(interval[1]) + "]";
    }

    private static double[] wilsonInterval(int successes, int trials) {
        if (trials <= 0) {
            return new double[]{0.0, 0.0};
        }
        double z = 1.959963984540054;
        double n = trials;
        double p = successes / n;
        double denominator = 1.0 + (z * z / n);
        double center = p + (z * z / (2.0 * n));
        double margin = z * Math.sqrt((p * (1.0 - p) / n) + (z * z / (4.0 * n * n)));
        return new double[]{
                Math.max(0.0, (center - margin) / denominator),
                Math.min(1.0, (center + margin) / denominator)
        };
    }
}
