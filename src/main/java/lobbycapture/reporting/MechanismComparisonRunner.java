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


public final class MechanismComparisonRunner
{
	private final Simulator simulator = new Simulator();
	
	public List<ScenarioReport> runAll(int runs, int contestsPerRun, long seed) {
		List<ScenarioReport> reports = new ArrayList<>();
		long scenarioSeed = seed;
		for (Scenario scenario : ScenarioCatalog.mechanismComparison()) {
			reports.add(simulator.run(scenario, runs, contestsPerRun, scenarioSeed));
			scenarioSeed += 1_009L;
		}
		return reports;
	}
	
	public void write(Path reportsDir, int runs, int contestsPerRun, long seed) throws IOException {
		Files.createDirectories(reportsDir);
		List<ScenarioReport> reports = runAll(runs, contestsPerRun, seed);
		ReportProvenance provenance = ReportProvenance.now(seed, runs, contestsPerRun);
		Files.writeString(reportsDir.resolve("lobby-capture-mechanism-comparison.csv"), new CsvReportWriter().write(reports, provenance));
		Files.writeString(reportsDir.resolve("lobby-capture-mechanism-comparison.md"), markdown(reports, provenance));
		ReportManifestWriter.write(
				reportsDir,
				"lobby-capture-mechanism-comparison",
				"lobbycapture.Main --mechanism-comparison --runs " + runs + " --contests " + contestsPerRun + " --seed " + seed,
				provenance,
				List.of("lobby-capture-mechanism-comparison.csv", "lobby-capture-mechanism-comparison.md")
		);
	}
	
	private static String markdown(List<ScenarioReport> reports, ReportProvenance provenance) {
		StringBuilder builder = new StringBuilder();
		builder.append("# Mechanism Comparison\n\n");
		builder.append("This report compares the same reform family under three model modes: a visible single-channel baseline, a multi-channel model with substitution disabled, and the current multi-channel substitution model. It is a mechanism check, not an empirical policy estimate.\n\n");
		builder.append("- Generated at: `").append(provenance.generatedAt()).append("`\n");
		builder.append("- Seed: `").append(provenance.seed()).append("`\n");
		builder.append("- Runs: `").append(provenance.runs()).append("`\n");
		builder.append("- Contests per run: `").append(provenance.contestsPerRun()).append("`\n\n");
		builder.append("| Model mode | Capture | Capture SD | Hidden influence | Hidden SD | Hidden capture | Total distortion | Distortion SD | Substitution risk |\n");
		builder.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
		for (ScenarioReport report : reports) {
			builder.append("| ").append(report.scenarioName())
			       .append(" | ").append(CsvReportWriter.format(report.observedCaptureRate()))
			       .append(" | ").append(CsvReportWriter.format(report.captureRateSeedStdDev()))
			       .append(" | ").append(CsvReportWriter.format(report.hiddenInfluenceShare()))
			       .append(" | ").append(CsvReportWriter.format(report.hiddenInfluenceSeedStdDev()))
			       .append(" | ").append(CsvReportWriter.format(report.hiddenCaptureIndex()))
			       .append(" | ").append(CsvReportWriter.format(report.totalInfluenceDistortion()))
			       .append(" | ").append(CsvReportWriter.format(report.totalInfluenceDistortionSeedStdDev()))
			       .append(" | ").append(CsvReportWriter.format(report.substitutionRisk()))
			       .append(" |\n");
		}
		return builder.toString();
	}
}
