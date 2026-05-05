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
import java.util.Comparator;
import java.util.List;

public final class AblationRunner {
    private static final String BASELINE_KEY = "ablation-full-bundle";
    private final Simulator simulator = new Simulator();

    public List<ScenarioReport> run(int runs, int contestsPerRun, long seed) {
        List<ScenarioReport> reports = new ArrayList<>();
        long scenarioSeed = seed;
        for (Scenario scenario : scenarios()) {
            reports.add(simulator.run(scenario, runs, contestsPerRun, scenarioSeed));
            scenarioSeed += 503L;
        }
        return reports;
    }

    public void write(Path reportsDir, int runs, int contestsPerRun, long seed) throws IOException {
        Files.createDirectories(reportsDir);
        List<ScenarioReport> reports = run(runs, contestsPerRun, seed);
        ReportProvenance provenance = ReportProvenance.now(seed, runs, contestsPerRun);
        Files.writeString(reportsDir.resolve("lobby-capture-ablation.csv"), new CsvReportWriter().write(reports, provenance));
        Files.writeString(reportsDir.resolve("lobby-capture-ablation.md"), writeMarkdown(reports, provenance));
        ReportManifestWriter.write(
                reportsDir,
                "lobby-capture-ablation",
                "lobbycapture.Main --ablation --runs " + runs + " --contests " + contestsPerRun + " --seed " + seed,
                provenance,
                List.of("lobby-capture-ablation.csv", "lobby-capture-ablation.md")
        );
    }

    private static List<Scenario> scenarios() {
        ReformRegime base = ReformRegime.fullBundle();
        return List.of(
                ScenarioCatalog.ablationScenario(
                        BASELINE_KEY,
                        "Ablation baseline full bundle",
                        base,
                        0.35,
                        InfluenceStrategy.BALANCED
                ),
                ScenarioCatalog.ablationScenario(
                        "ablation-no-enforcement",
                        "No enforcement",
                        base.withoutEnforcement("full bundle without enforcement"),
                        0.35,
                        InfluenceStrategy.BALANCED
                ),
                ScenarioCatalog.ablationScenario(
                        "ablation-no-beneficial-owner-disclosure",
                        "No beneficial-owner disclosure",
                        base.withoutBeneficialOwnerDisclosure("full bundle without beneficial-owner disclosure"),
                        0.55,
                        InfluenceStrategy.DARK_MONEY
                ),
                ScenarioCatalog.ablationScenario(
                        "ablation-no-public-financing",
                        "No public financing or vouchers",
                        base.withoutPublicFinancing("full bundle without public financing or vouchers"),
                        0.35,
                        InfluenceStrategy.CAMPAIGN_FINANCE
                ),
                ScenarioCatalog.ablationScenario(
                        "ablation-no-cooling-off",
                        "No cooling-off rules",
                        base.withoutCoolingOff("full bundle without cooling-off rules"),
                        0.35,
                        InfluenceStrategy.REVOLVING_DOOR
                ),
                ScenarioCatalog.ablationScenario(
                        "ablation-no-anti-astroturf",
                        "No anti-astroturf authentication",
                        base.withoutAntiAstroturf("full bundle without anti-astroturf authentication"),
                        0.35,
                        InfluenceStrategy.INFORMATION_DISTORTION
                ),
                ScenarioCatalog.ablationScenario(
                        "ablation-no-public-advocate-blind-review",
                        "No public advocate or blind review",
                        base.withoutPublicAdvocateAndBlindReview("full bundle without public advocate or blind review"),
                        0.35,
                        InfluenceStrategy.BALANCED
                )
        );
    }

    private static String writeMarkdown(List<ScenarioReport> reports, ReportProvenance provenance) {
        ScenarioReport baseline = baseline(reports);
        StringBuilder builder = new StringBuilder();
        builder.append("# Lobby Capture Ablation Report\n\n");
        builder.append("- Generated: `").append(provenance.generatedAt()).append("`\n");
        builder.append("- Seed: `").append(provenance.seed()).append("`\n");
        builder.append("- Runs per scenario: `").append(provenance.runs()).append("`\n");
        builder.append("- Contests per run: `").append(provenance.contestsPerRun()).append("`\n");
        builder.append("- Baseline: `").append(baseline.scenarioName()).append("`\n\n");

        builder.append("## Distortion Opening Ranking\n\n");
        builder.append("| Removed component | Total distortion increase | Capture increase | Hidden capture increase | Substitution risk | Comment flooding | Donor Gini | Enforcement capacity |\n");
        builder.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
        for (ScenarioReport report : rankedAblations(reports, baseline)) {
            builder.append("| ").append(report.scenarioName())
                    .append(" | ").append(format(report.totalInfluenceDistortion() - baseline.totalInfluenceDistortion()))
                    .append(" | ").append(format(report.observedCaptureRate() - baseline.observedCaptureRate()))
                    .append(" | ").append(format(report.hiddenCaptureIndex() - baseline.hiddenCaptureIndex()))
                    .append(" | ").append(format(report.substitutionFailureRisk()))
                    .append(" | ").append(format(report.commentFloodingIndex()))
                    .append(" | ").append(format(report.donorInfluenceGini()))
                    .append(" | ").append(format(report.enforcementCapacityIndex()))
                    .append(" |\n");
        }

        builder.append("\n## Full Snapshot\n\n");
        builder.append("| Scenario | Total distortion | Observed capture | Hidden capture | Anti-capture success | Comment authenticity | Template saturation | Admin cost |\n");
        builder.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
        for (ScenarioReport report : reports) {
            builder.append("| ").append(report.scenarioName())
                    .append(" | ").append(format(report.totalInfluenceDistortion()))
                    .append(" | ").append(format(report.observedCaptureRate()))
                    .append(" | ").append(format(report.hiddenCaptureIndex()))
                    .append(" | ").append(format(report.antiCaptureSuccessRate()))
                    .append(" | ").append(format(report.commentAuthenticity()))
                    .append(" | ").append(format(report.templateCommentSaturation()))
                    .append(" | ").append(format(report.administrativeCostIndex()))
                    .append(" |\n");
        }

        ScenarioReport largestOpening = rankedAblations(reports, baseline).stream().findFirst().orElse(baseline);
        builder.append("\n## Interpretation Guardrail\n\n");
        builder.append("The largest modeled distortion opening is `")
                .append(largestOpening.scenarioName())
                .append("`, with total-distortion change `")
                .append(format(largestOpening.totalInfluenceDistortion() - baseline.totalInfluenceDistortion()))
                .append("`. This is a comparative simulation result, not a causal empirical estimate.\n");
        return builder.toString();
    }

    private static ScenarioReport baseline(List<ScenarioReport> reports) {
        return reports.stream()
                .filter(report -> report.scenarioKey().equals(BASELINE_KEY))
                .findFirst()
                .orElseThrow(() -> new IllegalStateException("Missing ablation baseline."));
    }

    private static List<ScenarioReport> rankedAblations(List<ScenarioReport> reports, ScenarioReport baseline) {
        return reports.stream()
                .filter(report -> !report.scenarioKey().equals(BASELINE_KEY))
                .sorted(Comparator.comparingDouble((ScenarioReport report) -> report.totalInfluenceDistortion() - baseline.totalInfluenceDistortion()).reversed())
                .toList();
    }

    private static String format(double value) {
        return CsvReportWriter.format(value);
    }
}
