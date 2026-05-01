package lobbycapture.calibration;

import lobbycapture.metrics.ScenarioReport;

import java.util.List;

public final class EmpiricalValidator {
    public List<String> screen(ScenarioReport report) {
        return List.of(
                "Scenario " + report.scenarioKey() + " is currently simulation-only.",
                "Use data/calibration/empirical-benchmarks.csv to add metric-specific plausibility checks."
        );
    }
}

