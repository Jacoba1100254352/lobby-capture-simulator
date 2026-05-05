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
import java.util.Locale;

public final class InteractionRunner {
    private final Simulator simulator = new Simulator();

    public List<ScenarioReport> run(int runs, int contestsPerRun, long seed) {
        List<ScenarioReport> reports = new ArrayList<>();
        long scenarioSeed = seed;
        for (Scenario scenario : scenarios()) {
            reports.add(simulator.run(scenario, runs, contestsPerRun, scenarioSeed));
            scenarioSeed += 907L;
        }
        return reports;
    }

    public void write(Path reportsDir, int runs, int contestsPerRun, long seed) throws IOException {
        Files.createDirectories(reportsDir);
        List<ScenarioReport> reports = run(runs, contestsPerRun, seed);
        ReportProvenance provenance = ReportProvenance.now(seed, runs, contestsPerRun);
        Files.writeString(reportsDir.resolve("lobby-capture-interactions.csv"), new CsvReportWriter().write(reports, provenance));
        Files.writeString(reportsDir.resolve("lobby-capture-interactions.md"), new MarkdownReportWriter().write("Lobby Capture Interaction Sweep", reports, provenance));
        ReportManifestWriter.write(
                reportsDir,
                "lobby-capture-interactions",
                "lobbycapture.Main --interactions --runs " + runs + " --contests " + contestsPerRun + " --seed " + seed,
                provenance,
                List.of("lobby-capture-interactions.csv", "lobby-capture-interactions.md")
        );
    }

    private static List<Scenario> scenarios() {
        List<Scenario> scenarios = new ArrayList<>();
        ReformRegime base = ReformRegime.fullBundle();
        double[] levels = {0.10, 0.80, 1.25};
        for (double enforcement : levels) {
            for (double disclosure : levels) {
                scenarios.add(ScenarioCatalog.stressedSensitivityScenario(
                        key("enforcement-disclosure", enforcement, disclosure),
                        "Interaction enforcement " + label(enforcement) + " disclosure " + label(disclosure),
                        base.withTuning("interaction enforcement/disclosure", disclosure, enforcement, 1.0, 1.0),
                        0.35,
                        InfluenceStrategy.BALANCED
                ));
            }
        }
        double[] financingLevels = {0.35, 0.80, 1.25};
        double[] evasionLevels = {0.00, 0.45, 0.90};
        for (double financing : financingLevels) {
            for (double evasion : evasionLevels) {
                scenarios.add(ScenarioCatalog.stressedSensitivityScenario(
                        key("financing-evasion", financing, evasion),
                        "Interaction public financing " + label(financing) + " evasion " + label(evasion),
                        base.withTuning("interaction public financing/evasion", 1.0, 1.0, financing, 1.0),
                        evasion,
                        InfluenceStrategy.CAMPAIGN_FINANCE
                ));
            }
        }
        InfluenceStrategy[] strategies = {InfluenceStrategy.BALANCED, InfluenceStrategy.REVOLVING_DOOR};
        for (double cooling : levels) {
            for (InfluenceStrategy strategy : strategies) {
                scenarios.add(ScenarioCatalog.stressedSensitivityScenario(
                        "interaction-cooling-" + label(cooling).replace('.', '-') + "-" + strategy.name().toLowerCase(Locale.US).replace('_', '-'),
                        "Interaction cooling " + label(cooling) + " strategy " + strategy.name().toLowerCase(Locale.US).replace('_', '-'),
                        base.withTuning("interaction cooling/strategy", 1.0, 1.0, 1.0, cooling),
                        0.35,
                        strategy
                ));
            }
        }
        return List.copyOf(scenarios);
    }

    private static String key(String family, double first, double second) {
        return "interaction-" + family + "-" + label(first).replace('.', '-') + "-" + label(second).replace('.', '-');
    }

    private static String label(double value) {
        return String.format(Locale.US, "%.2f", value);
    }
}
