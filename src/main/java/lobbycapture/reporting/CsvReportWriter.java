package lobbycapture.reporting;

import lobbycapture.metrics.ScenarioReport;

import java.util.List;
import java.util.Locale;

public final class CsvReportWriter {
    public String write(List<ScenarioReport> reports, ReportProvenance provenance) {
        StringBuilder builder = new StringBuilder();
        builder.append("generatedAt,seed,runs,contestsPerRun,scenarioKey,scenarioName,totalContests,capturedContests,antiCaptureReforms,enactedAntiCaptureReforms,directionalScore,captureControl,representation,reformFeasibility,captureRate,antiCaptureSuccess,avgCaptureIndex,avgPublicInterest,publicPreferenceDistortion,privateGainRatio,lobbySpendPerContest,clientFundingPerContest,donorInfluenceGini,averageDisclosureLag,defensiveReformSpendShare,captureReturnOnSpend,publicBenefitPerInfluenceDollar,directAccessShare,agendaAccessShare,informationDistortionShare,publicCampaignShare,litigationThreatShare,campaignFinanceShare,darkMoneyShare,revolvingDoorShare,defensiveChannelShare,detectionRate,sanctionRate,policyDistortion,regulatoryDrift,enforcementForbearance,procurementBias,darkMoneyTraceability,largeDonorDependence,voucherParticipation,publicFinancingShare,revolvingDoorInfluence,commentRecordDistortion,commentAuthenticity,templateCommentSaturation,technicalClaimCredibility,channelSwitchRate,evasionShiftRate,evasionPenaltyRate,legitimateAdvocacyChill,constitutionalChallengeDelay,administrativeCost\n");
        for (ScenarioReport report : reports) {
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
                    .append(format(report.antiCaptureSuccessRate())).append(',')
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
                    .append(format(report.largeDonorDependence())).append(',')
                    .append(format(report.voucherParticipationRate())).append(',')
                    .append(format(report.publicFinancingShare())).append(',')
                    .append(format(report.revolvingDoorInfluence())).append(',')
                    .append(format(report.commentRecordDistortion())).append(',')
                    .append(format(report.commentAuthenticity())).append(',')
                    .append(format(report.templateCommentSaturation())).append(',')
                    .append(format(report.technicalClaimCredibility())).append(',')
                    .append(format(report.channelSwitchRate())).append(',')
                    .append(format(report.evasionShiftRate())).append(',')
                    .append(format(report.evasionPenaltyRate())).append(',')
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
}
