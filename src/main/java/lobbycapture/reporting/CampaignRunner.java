package lobbycapture.reporting;

import lobbycapture.metrics.ScenarioReport;
import lobbycapture.simulation.Scenario;
import lobbycapture.simulation.ScenarioCatalog;
import lobbycapture.simulation.Simulator;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class CampaignRunner {
    private final Simulator simulator = new Simulator();

    public List<ScenarioReport> runAll(int runs, int contestsPerRun, long seed) {
        List<ScenarioReport> reports = new ArrayList<>();
        long scenarioSeed = seed;
        for (Scenario scenario : ScenarioCatalog.all()) {
            reports.add(simulator.run(scenario, runs, contestsPerRun, scenarioSeed));
            scenarioSeed += 1_009L;
        }
        return reports;
    }

    public void writeCampaign(Path reportsDir, int runs, int contestsPerRun, long seed) throws IOException {
        Files.createDirectories(reportsDir);
        List<ScenarioReport> reports = runAll(runs, contestsPerRun, seed);
        ReportProvenance provenance = ReportProvenance.now(seed, runs, contestsPerRun);
        Files.writeString(reportsDir.resolve("lobby-capture-campaign.csv"), new CsvReportWriter().write(reports, provenance));
        Files.writeString(reportsDir.resolve("lobby-capture-campaign.md"), new MarkdownReportWriter().write(reports, provenance));
        ReportManifestWriter.write(
                reportsDir,
                "lobby-capture-campaign",
                "lobbycapture.Main --campaign --runs " + runs + " --contests " + contestsPerRun + " --seed " + seed,
                provenance,
                List.of("lobby-capture-campaign.csv", "lobby-capture-campaign.md")
        );
    }
}
