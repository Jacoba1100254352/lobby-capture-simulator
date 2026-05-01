package lobbycapture.reporting;

import lobbycapture.metrics.ScenarioReport;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.Scenario;
import lobbycapture.simulation.ScenarioCatalog;
import lobbycapture.simulation.Simulator;
import lobbycapture.strategy.InfluenceStrategy;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class SensitivityRunner {
    private final Simulator simulator = new Simulator();

    public List<ScenarioReport> run(int runs, int contestsPerRun, long seed) {
        List<ScenarioReport> reports = new ArrayList<>();
        long scenarioSeed = seed;
        for (Scenario scenario : scenarios()) {
            reports.add(simulator.run(scenario, runs, contestsPerRun, scenarioSeed));
            scenarioSeed += 701L;
        }
        return reports;
    }

    public void write(Path reportsDir, int runs, int contestsPerRun, long seed) throws IOException {
        Files.createDirectories(reportsDir);
        List<ScenarioReport> reports = run(runs, contestsPerRun, seed);
        ReportProvenance provenance = ReportProvenance.now(seed, runs, contestsPerRun);
        Files.writeString(reportsDir.resolve("lobby-capture-sensitivity.csv"), new CsvReportWriter().write(reports, provenance));
        Files.writeString(reportsDir.resolve("lobby-capture-sensitivity.md"), new MarkdownReportWriter().write("Lobby Capture Sensitivity Sweep", reports, provenance));
        ReportManifestWriter.write(
                reportsDir,
                "lobby-capture-sensitivity",
                "lobbycapture.Main --sensitivity --runs " + runs + " --contests " + contestsPerRun + " --seed " + seed,
                provenance,
                List.of("lobby-capture-sensitivity.csv", "lobby-capture-sensitivity.md")
        );
    }

    private static List<Scenario> scenarios() {
        List<Scenario> scenarios = new ArrayList<>();
        ReformRegime base = ReformRegime.fullBundle();
        double[] levels = {0.35, 0.65, 1.00, 1.25};
        for (double level : levels) {
            scenarios.add(ScenarioCatalog.sensitivityScenario(
                    key("enforcement", level),
                    "Sensitivity enforcement " + label(level),
                    base.withTuning("sensitivity enforcement " + label(level), 1.0, level, 1.0, 1.0),
                    0.35,
                    InfluenceStrategy.BALANCED
            ));
            scenarios.add(ScenarioCatalog.sensitivityScenario(
                    key("disclosure", level),
                    "Sensitivity disclosure " + label(level),
                    base.withTuning("sensitivity disclosure " + label(level), level, 1.0, 1.0, 1.0),
                    0.35,
                    InfluenceStrategy.BALANCED
            ));
            scenarios.add(ScenarioCatalog.sensitivityScenario(
                    key("public-financing", level),
                    "Sensitivity public financing " + label(level),
                    base.withTuning("sensitivity public financing " + label(level), 1.0, 1.0, level, 1.0),
                    0.35,
                    InfluenceStrategy.CAMPAIGN_FINANCE
            ));
            scenarios.add(ScenarioCatalog.sensitivityScenario(
                    key("cooling-off", level),
                    "Sensitivity cooling off " + label(level),
                    base.withTuning("sensitivity cooling off " + label(level), 1.0, 1.0, 1.0, level),
                    0.35,
                    InfluenceStrategy.REVOLVING_DOOR
            ));
        }
        double[] evasionLevels = {0.00, 0.30, 0.60, 0.90};
        for (double evasion : evasionLevels) {
            scenarios.add(ScenarioCatalog.sensitivityScenario(
                    key("evasion", evasion),
                    "Sensitivity evasion " + label(evasion),
                    base,
                    evasion,
                    InfluenceStrategy.BALANCED
            ));
        }
        return List.copyOf(scenarios);
    }

    private static String key(String family, double value) {
        return "sensitivity-" + family + "-" + label(value).replace('.', '-');
    }

    private static String label(double value) {
        return String.format(java.util.Locale.US, "%.2f", value);
    }
}
