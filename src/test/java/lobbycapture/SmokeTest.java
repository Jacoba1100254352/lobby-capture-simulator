package lobbycapture;

import lobbycapture.metrics.ScenarioReport;
import lobbycapture.simulation.ScenarioCatalog;
import lobbycapture.simulation.Simulator;

public final class SmokeTest {
    private SmokeTest() {
    }

    public static void main(String[] args) {
        Simulator simulator = new Simulator();
        ScenarioReport open = simulator.run(ScenarioCatalog.require("open-access-lobbying"), 4, 30, 11L);
        ScenarioReport reformThreat = simulator.run(ScenarioCatalog.require("reform-threat-mobilization"), 4, 30, 12L);
        ScenarioReport bundle = simulator.run(ScenarioCatalog.require("full-anti-capture-bundle"), 4, 30, 13L);
        ScenarioReport evasion = simulator.run(ScenarioCatalog.require("bundle-with-evasion"), 4, 30, 14L);

        require(open.totalContests() == 120, "open scenario should run all contests");
        require(open.lobbySpendPerContest() > 0.0, "lobbying should spend in baseline");
        require(reformThreat.defensiveReformSpendShare() > 0.20, "reform threat should trigger defensive spending");
        require(bundle.antiCaptureSuccessRate() >= reformThreat.antiCaptureSuccessRate(), "full bundle should preserve at least as much reform success as reform threat case");
        require(evasion.darkMoneySpendShare() >= bundle.darkMoneySpendShare(), "evasion scenario should shift toward dark money");
        require(bundle.directionalScore() >= 0.0 && bundle.directionalScore() <= 1.0, "directional score should stay bounded");
        System.out.println("Smoke tests passed.");
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}

