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
                portfolio("portfolio-transparency-first", "Portfolio: transparency-first baseline", ReformRegime.transparencyFirstBaseline(), 0.45, InfluenceStrategy.DIRECT_ACCESS),
                portfolio("portfolio-balanced-compliance", "Portfolio: balanced compliance core", ReformRegime.balancedComplianceCore(), 0.45, InfluenceStrategy.BALANCED),
                portfolio("portfolio-electoral-shield", "Portfolio: electoral substitution shield", ReformRegime.electoralSubstitutionShield(), 0.55, InfluenceStrategy.CAMPAIGN_FINANCE),
                portfolio("portfolio-rulemaking-integrity", "Portfolio: rulemaking integrity stack", ReformRegime.rulemakingIntegrityStack(), 0.50, InfluenceStrategy.INTERMEDIARY),
                portfolio("portfolio-procurement-hardening", "Portfolio: procurement hardening stack", ReformRegime.procurementHardeningStack(), 0.45, InfluenceStrategy.REVOLVING_DOOR),
                portfolio("portfolio-countervailing-representation", "Portfolio: countervailing representation stack", ReformRegime.countervailingRepresentationStack(), 0.35, InfluenceStrategy.INFORMATION_DISTORTION),
                portfolio("portfolio-high-deterrence", "Portfolio: high-deterrence enforcement stack", ReformRegime.highDeterrenceEnforcementStack(), 0.60, InfluenceStrategy.BALANCED),
                portfolio("portfolio-civil-liberties", "Portfolio: civil-liberties-constrained portfolio", ReformRegime.civilLibertiesConstrainedPortfolio(), 0.45, InfluenceStrategy.BALANCED),
                portfolio("portfolio-full-anti-substitution", "Portfolio: full anti-substitution portfolio", ReformRegime.fullAntiSubstitutionPortfolio(), 0.35, InfluenceStrategy.BALANCED),
                portfolio("portfolio-full-anti-substitution-high-evasion", "Portfolio: full anti-substitution under high evasion", ReformRegime.fullAntiSubstitutionPortfolio(), 0.90, InfluenceStrategy.BALANCED)
        );
    }

    private static Scenario portfolio(String key, String name, ReformRegime reform, double evasionFreedom, InfluenceStrategy strategy) {
        return ScenarioCatalog.stressedSensitivityScenario(key, name, reform, evasionFreedom, strategy);
    }

    private static String markdown(List<ScenarioReport> reports, ReportProvenance provenance) {
        StringBuilder builder = new StringBuilder();
        builder.append(new MarkdownReportWriter().write("Reform Portfolio Screen", reports, provenance));
        builder.append("\n## Portfolio Dominance Screen\n\n");
        builder.append("The design loss below minimizes total influence distortion first, then hidden capture, substitution risk, administrative burden, network opacity, legitimate-advocacy chill, and speech-restriction risk. It rewards cross-venue detection and participation protection. It is a synthetic policy-design screen, not an empirical welfare estimate.\n\n");
        builder.append("| Rank | Portfolio | Design loss | Total dist. | Hidden cap. | Risk | Admin | Network opacity | Venue det. | Participation | Speech risk |\n");
        builder.append("| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
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
                    .append(" | ").append(CsvReportWriter.format(report.crossVenueDetectionIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.participationProtectionIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.speechRestrictionRisk()))
                    .append(" |\n");
        }
        return builder.toString();
    }

    private static double designLoss(ScenarioReport report) {
        return Math.max(0.0,
                (0.30 * report.totalInfluenceDistortion())
                        + (0.20 * report.hiddenCaptureIndex())
                        + (0.16 * report.substitutionFailureRisk())
                        + (0.10 * report.administrativeCostIndex())
                        + (0.09 * report.networkOpacityIndex())
                        + (0.07 * report.legitimateAdvocacyChillRate())
                        + (0.06 * report.speechRestrictionRisk())
                        - (0.05 * report.crossVenueDetectionIndex())
                        - (0.03 * report.participationProtectionIndex())
        );
    }
}
