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

public final class PortfolioRunner {
    private final Simulator simulator = new Simulator();

    public List<ScenarioReport> run(int runs, int contestsPerRun, long seed) {
        List<ScenarioReport> reports = new ArrayList<>();
        long scenarioSeed = seed;
        for (Scenario scenario : scenarios()) {
            reports.add(simulator.run(scenario, runs, contestsPerRun, scenarioSeed));
            scenarioSeed += 1_303L;
        }
        return reports;
    }

    public void write(Path reportsDir, int runs, int contestsPerRun, long seed) throws IOException {
        Files.createDirectories(reportsDir);
        List<ScenarioReport> reports = run(runs, contestsPerRun, seed);
        ReportProvenance provenance = ReportProvenance.now(seed, runs, contestsPerRun);
        Files.writeString(reportsDir.resolve("lobby-capture-portfolio.csv"), new CsvReportWriter().write(reports, provenance));
        Files.writeString(reportsDir.resolve("lobby-capture-portfolio.md"), markdown(reports, provenance));
        ReportManifestWriter.write(
                reportsDir,
                "lobby-capture-portfolio",
                "lobbycapture.Main --portfolio --runs " + runs + " --contests " + contestsPerRun + " --seed " + seed,
                provenance,
                List.of("lobby-capture-portfolio.csv", "lobby-capture-portfolio.md")
        );
    }

    private static List<Scenario> scenarios() {
        return List.of(
                portfolio("portfolio-meeting-logs", "Portfolio: machine-readable meeting logs", ReformRegime.machineReadableMeetingLogs(), 0.45, InfluenceStrategy.DIRECT_ACCESS),
                portfolio("portfolio-public-interest-funds", "Portfolio: public-interest representation funds", ReformRegime.publicInterestRepresentationFunds(), 0.35, InfluenceStrategy.INFORMATION_DISTORTION),
                portfolio("portfolio-randomized-audits", "Portfolio: randomized audits and sanctions", ReformRegime.randomizedAuditSanctions(), 0.40, InfluenceStrategy.BALANCED),
                portfolio("portfolio-comment-authenticity", "Portfolio: comment authenticity controls", ReformRegime.commentAuthenticityRules(), 0.50, InfluenceStrategy.INTERMEDIARY),
                portfolio("portfolio-procurement-firewalls", "Portfolio: procurement firewalls", ReformRegime.procurementFirewall(), 0.45, InfluenceStrategy.REVOLVING_DOOR),
                portfolio("portfolio-venue-detection", "Portfolio: venue-shifting detection", ReformRegime.venueShiftingDetection(), 0.65, InfluenceStrategy.INTERMEDIARY),
                portfolio("portfolio-hard-budgets", "Portfolio: hard lobbying budgets", ReformRegime.hardLobbyingBudgets(), 0.55, InfluenceStrategy.BALANCED),
                portfolio("portfolio-full-bundle", "Portfolio: full anti-capture bundle", ReformRegime.fullBundle(), 0.35, InfluenceStrategy.BALANCED),
                portfolio("portfolio-full-bundle-high-evasion", "Portfolio: full bundle under high evasion", ReformRegime.fullBundle(), 0.90, InfluenceStrategy.BALANCED)
        );
    }

    private static Scenario portfolio(String key, String name, ReformRegime reform, double evasionFreedom, InfluenceStrategy strategy) {
        return ScenarioCatalog.stressedSensitivityScenario(key, name, reform, evasionFreedom, strategy);
    }

    private static String markdown(List<ScenarioReport> reports, ReportProvenance provenance) {
        StringBuilder builder = new StringBuilder();
        builder.append(new MarkdownReportWriter().write("Reform Portfolio Screen", reports, provenance));
        builder.append("\n## Portfolio Dominance Screen\n\n");
        builder.append("The design loss below minimizes total influence distortion first, then hidden capture, substitution risk, administrative burden, and network opacity. It is a synthetic policy-design screen, not an empirical welfare estimate.\n\n");
        builder.append("| Rank | Portfolio | Design loss | Total dist. | Hidden cap. | Risk | Admin | Network opacity | Legibility |\n");
        builder.append("| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
        int rank = 1;
        for (ScenarioReport report : reports.stream().sorted(Comparator.comparing(PortfolioRunner::designLoss)).toList()) {
            builder.append("| ").append(rank++)
                    .append(" | ").append(report.scenarioName())
                    .append(" | ").append(CsvReportWriter.format(designLoss(report)))
                    .append(" | ").append(CsvReportWriter.format(report.totalInfluenceDistortion()))
                    .append(" | ").append(CsvReportWriter.format(report.hiddenCaptureIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.substitutionFailureRisk()))
                    .append(" | ").append(CsvReportWriter.format(report.administrativeCostIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.networkOpacityIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.networkLegibilityIndex()))
                    .append(" |\n");
        }
        return builder.toString();
    }

    private static double designLoss(ScenarioReport report) {
        return (0.32 * report.totalInfluenceDistortion())
                + (0.22 * report.hiddenCaptureIndex())
                + (0.18 * report.substitutionFailureRisk())
                + (0.12 * report.administrativeCostIndex())
                + (0.10 * report.networkOpacityIndex())
                + (0.06 * report.legitimateAdvocacyChillRate());
    }
}
