package lobbycapture;

import lobbycapture.metrics.ScenarioReport;
import lobbycapture.reporting.AblationRunner;
import lobbycapture.reporting.CampaignRunner;
import lobbycapture.reporting.InteractionRunner;
import lobbycapture.reporting.SensitivityRunner;
import lobbycapture.simulation.ScenarioCatalog;
import lobbycapture.simulation.Simulator;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class SmokeTest {
    private SmokeTest() {
    }

    public static void main(String[] args) throws IOException {
        Simulator simulator = new Simulator();
        ScenarioReport open = simulator.run(ScenarioCatalog.require("open-access-lobbying"), 4, 30, 11L);
        ScenarioReport reformThreat = simulator.run(ScenarioCatalog.require("reform-threat-mobilization"), 4, 30, 12L);
        ScenarioReport bundle = simulator.run(ScenarioCatalog.require("full-anti-capture-bundle"), 4, 30, 13L);
        ScenarioReport evasion = simulator.run(ScenarioCatalog.require("bundle-with-evasion"), 4, 30, 14L);
        ScenarioReport intermediary = simulator.run(ScenarioCatalog.require("intermediary-substitution"), 4, 30, 17L);
        List<ScenarioReport> sensitivity = new SensitivityRunner().run(1, 10, 15L);
        List<ScenarioReport> interactions = new InteractionRunner().run(1, 10, 16L);
        List<ScenarioReport> ablation = new AblationRunner().run(3, 30, 242L);

        require(open.totalContests() == 120, "open scenario should run all contests");
        require(open.lobbySpendPerContest() > 0.0, "lobbying should spend in baseline");
        require(open.clientFundingPerContest() > 0.0, "clients should replenish lobbying budgets");
        require(open.clientFundingAdaptation() > 0.0, "client funding adaptation should be reported");
        require(open.regulatorAttentionIndex() > 0.0, "regulator attention should be reported");
        require(open.regulatorQueueBacklog() >= 0.0, "regulator queue backlog should be reported");
        require(open.watchdogFocusIndex() > 0.0, "watchdog focus should be reported");
        require(open.watchdogBudgetConcentration() > 0.0, "watchdog budget concentration should be reported");
        require(open.adaptationSpeed() >= 0.0, "adaptation speed should be reported");
        require(open.reformDecayPressure() >= 0.0, "reform decay pressure should be reported");
        require(open.commentAuthenticity() >= 0.0 && open.commentAuthenticity() <= 1.0, "comment authenticity should stay bounded");
        require(open.commentUniqueInformationShare() >= 0.0 && open.commentUniqueInformationShare() <= 1.0, "comment unique information should stay bounded");
        require(open.commentReviewBurden() >= 0.0 && open.commentReviewBurden() <= 1.0, "comment review burden should stay bounded");
        require(open.darkMoneyDirectVisibility() >= 0.0 && open.darkMoneyDirectVisibility() <= 1.0, "dark-money visibility should stay bounded");
        require(open.voucherResidentParticipation() >= 0.0 && open.voucherResidentParticipation() <= 1.0, "voucher participation should stay bounded");
        require(open.publicFinancingCandidateUptake() >= 0.0 && open.publicFinancingCandidateUptake() <= 1.0, "public financing uptake should stay bounded");
        require(open.substitutionPressure() >= 0.0 && open.substitutionPressure() <= 1.0, "substitution pressure should stay bounded");
        require(open.hiddenInfluenceShare() >= 0.0 && open.hiddenInfluenceShare() <= 1.0, "hidden influence should stay bounded");
        require(open.observedCaptureRate() == open.captureRate(), "observed capture should mirror binomial capture rate");
        require(open.hiddenCaptureIndex() >= 0.0 && open.hiddenCaptureIndex() <= 1.0, "hidden capture should stay bounded");
        require(open.totalInfluenceDistortion() >= 0.0 && open.totalInfluenceDistortion() <= 1.0, "total influence distortion should stay bounded");
        require(open.substitutionFailureRisk() >= 0.0 && open.substitutionFailureRisk() <= 1.0, "substitution failure risk should stay bounded");
        require(open.enforcementCapacityIndex() >= 0.0 && open.enforcementCapacityIndex() <= 1.0, "enforcement capacity should stay bounded");
        require(open.commentFloodingIndex() >= 0.0 && open.commentFloodingIndex() <= 1.0, "comment flooding should stay bounded");
        require(open.technicalRulemakingDistortion() >= 0.0 && open.technicalRulemakingDistortion() <= 1.0, "technical rulemaking distortion should stay bounded");
        require(open.captureRateSeedStdDev() >= 0.0, "multi-seed capture robustness should be reported");
        require(open.totalInfluenceDistortionSeedStdDev() >= 0.0, "multi-seed distortion robustness should be reported");
        require(open.netTransparencyGain() >= -1.0 && open.netTransparencyGain() <= 1.0, "net transparency gain should stay bounded");
        require(reformThreat.defensiveReformSpendShare() > 0.20, "reform threat should trigger defensive spending");
        require(bundle.captureRate() <= reformThreat.captureRate(), "full bundle should reduce capture relative to reform threat case");
        require(evasion.darkMoneySpendShare() >= bundle.darkMoneySpendShare(), "evasion scenario should shift toward dark money");
        require(evasion.evasionPenaltyRate() >= 0.0, "evasion penalty should stay non-negative");
        require(intermediary.intermediarySpendShare() > 0.0, "intermediary scenario should route influence through intermediaries");
        require(intermediary.substitutionFailureRisk() >= 0.0, "intermediary substitution risk should be reported");
        require(sensitivity.size() == 20, "sensitivity runner should cover reform and evasion sweeps");
        require(interactions.size() == 24, "interaction runner should cover two-way reform sweeps");
        require(ablation.size() == 7, "ablation runner should cover baseline plus six removals");
        require(ablation.stream().anyMatch(report -> report.scenarioKey().equals("ablation-full-bundle")), "ablation runner should include a baseline");
        require(largestAblationOpening(ablation) > 0.0, "stressed ablation should expose at least one distortion opening");
        require(bundle.directionalScore() >= 0.0 && bundle.directionalScore() <= 1.0, "directional score should stay bounded");
        verifyReportModes();
        System.out.println("Smoke tests passed.");
    }

    private static void verifyReportModes() throws IOException {
        Path reports = Files.createTempDirectory("lobby-capture-reports");
        try {
            new CampaignRunner().writeCampaign(reports, 1, 5, 91L);
            new SensitivityRunner().write(reports, 1, 5, 92L);
            new AblationRunner().write(reports, 1, 5, 93L);
            new InteractionRunner().write(reports, 1, 5, 94L);

            verifyReport(reports.resolve("lobby-capture-campaign.csv"), reports.resolve("lobby-capture-campaign.md"), reports.resolve("lobby-capture-campaign.manifest.json"));
            verifyReport(reports.resolve("lobby-capture-sensitivity.csv"), reports.resolve("lobby-capture-sensitivity.md"), reports.resolve("lobby-capture-sensitivity.manifest.json"));
            verifyReport(reports.resolve("lobby-capture-ablation.csv"), reports.resolve("lobby-capture-ablation.md"), reports.resolve("lobby-capture-ablation.manifest.json"));
            verifyReport(reports.resolve("lobby-capture-interactions.csv"), reports.resolve("lobby-capture-interactions.md"), reports.resolve("lobby-capture-interactions.manifest.json"));
        } finally {
            deleteRecursively(reports);
        }
    }

    private static void verifyReport(Path csv, Path markdown, Path manifest) throws IOException {
        String csvText = Files.readString(csv);
        String markdownText = Files.readString(markdown);
        String manifestText = Files.readString(manifest);
        require(csvText.contains("commentUniqueInformationShare,commentReviewBurden,commentProceduralAckRate,commentSubstantiveUptake,commentCompressionRate,commentFloodingIndex"), csv + " should report comment triage state");
        require(csvText.contains("darkMoneyTraceability,darkMoneyDirectVisibility,largeDonorDependence,voucherParticipation,voucherResidentParticipation,publicFinancingShare,publicFinancingCandidateUptake"), csv + " should report split source-state metrics");
        require(csvText.contains("observedCaptureRate,hiddenCaptureIndex,totalInfluenceDistortion,substitutionFailureRisk"), csv + " should report capture and distortion splits");
        require(csvText.contains("visibleLobbyingSpendShare,directAccessShare,agendaAccessShare,informationDistortionShare,publicCampaignShare,litigationThreatShare,campaignFinanceShare,darkMoneyShare,revolvingDoorShare,intermediaryShare"), csv + " should report visible and intermediary spend state");
        require(csvText.contains("substitutionPressure,influencePreservationRate,hiddenInfluenceShare,netTransparencyGain,messengerSubstitutionRate,venueSubstitutionRate"), csv + " should report substitution state");
        require(csvText.contains("clientFundingAdaptation,regulatorAttentionIndex,regulatorQueueBacklog,watchdogFocusIndex,watchdogBudgetConcentration,adaptationSpeed,reformDecayPressure"), csv + " should report adaptive state");
        require(csvText.lines().count() > 1, csv + " should contain report rows");
        require(markdownText.contains("Generated"), markdown + " should include provenance");
        require(manifestText.contains("\"gitCommit\""), manifest + " should include git provenance");
        require(manifestText.contains("\"calibrationChecksum\""), manifest + " should include calibration checksum");
    }

    private static void deleteRecursively(Path root) throws IOException {
        try (var paths = Files.walk(root)) {
            for (Path path : paths.sorted((left, right) -> right.compareTo(left)).toList()) {
                Files.deleteIfExists(path);
            }
        }
    }

    private static double largestAblationOpening(List<ScenarioReport> reports) {
        ScenarioReport baseline = reports.stream()
                .filter(report -> report.scenarioKey().equals("ablation-full-bundle"))
                .findFirst()
                .orElseThrow();
        return reports.stream()
                .filter(report -> !report.scenarioKey().equals("ablation-full-bundle"))
                .mapToDouble(report -> report.totalInfluenceDistortion() - baseline.totalInfluenceDistortion())
                .max()
                .orElse(0.0);
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
