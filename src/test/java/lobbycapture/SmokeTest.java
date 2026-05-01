package lobbycapture;

import lobbycapture.metrics.ScenarioReport;
import lobbycapture.reporting.AblationRunner;
import lobbycapture.reporting.CampaignRunner;
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
        List<ScenarioReport> sensitivity = new SensitivityRunner().run(1, 10, 15L);
        List<ScenarioReport> ablation = new AblationRunner().run(3, 30, 242L);

        require(open.totalContests() == 120, "open scenario should run all contests");
        require(open.lobbySpendPerContest() > 0.0, "lobbying should spend in baseline");
        require(open.clientFundingPerContest() > 0.0, "clients should replenish lobbying budgets");
        require(open.clientFundingAdaptation() > 0.0, "client funding adaptation should be reported");
        require(open.regulatorAttentionIndex() > 0.0, "regulator attention should be reported");
        require(open.watchdogFocusIndex() > 0.0, "watchdog focus should be reported");
        require(open.commentAuthenticity() >= 0.0 && open.commentAuthenticity() <= 1.0, "comment authenticity should stay bounded");
        require(reformThreat.defensiveReformSpendShare() > 0.20, "reform threat should trigger defensive spending");
        require(bundle.antiCaptureSuccessRate() >= reformThreat.antiCaptureSuccessRate(), "full bundle should preserve at least as much reform success as reform threat case");
        require(evasion.darkMoneySpendShare() >= bundle.darkMoneySpendShare(), "evasion scenario should shift toward dark money");
        require(evasion.evasionPenaltyRate() >= 0.0, "evasion penalty should stay non-negative");
        require(sensitivity.size() == 20, "sensitivity runner should cover reform and evasion sweeps");
        require(ablation.size() == 7, "ablation runner should cover baseline plus six removals");
        require(ablation.stream().anyMatch(report -> report.scenarioKey().equals("ablation-full-bundle")), "ablation runner should include a baseline");
        require(largestAblationOpening(ablation) > 0.0, "stressed ablation should expose at least one capture opening");
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

            verifyReport(reports.resolve("lobby-capture-campaign.csv"), reports.resolve("lobby-capture-campaign.md"));
            verifyReport(reports.resolve("lobby-capture-sensitivity.csv"), reports.resolve("lobby-capture-sensitivity.md"));
            verifyReport(reports.resolve("lobby-capture-ablation.csv"), reports.resolve("lobby-capture-ablation.md"));
        } finally {
            deleteRecursively(reports);
        }
    }

    private static void verifyReport(Path csv, Path markdown) throws IOException {
        String csvText = Files.readString(csv);
        String markdownText = Files.readString(markdown);
        require(csvText.contains("clientFundingAdaptation,regulatorAttentionIndex,watchdogFocusIndex"), csv + " should report adaptive state");
        require(csvText.lines().count() > 1, csv + " should contain report rows");
        require(markdownText.contains("Generated"), markdown + " should include provenance");
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
                .mapToDouble(report -> report.captureRate() - baseline.captureRate())
                .max()
                .orElse(0.0);
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
