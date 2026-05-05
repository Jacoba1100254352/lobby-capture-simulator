package lobbycapture.reporting;

import lobbycapture.metrics.ScenarioReport;

import java.util.Comparator;
import java.util.List;

public final class MarkdownReportWriter {
    public String write(List<ScenarioReport> reports, ReportProvenance provenance) {
        return write("Lobby Capture Campaign", reports, provenance);
    }

    public String write(String title, List<ScenarioReport> reports, ReportProvenance provenance) {
        StringBuilder builder = new StringBuilder();
        builder.append("# ").append(title).append("\n\n");
        builder.append("- Generated: `").append(provenance.generatedAt()).append("`\n");
        builder.append("- Seed: `").append(provenance.seed()).append("`\n");
        builder.append("- Runs per scenario: `").append(provenance.runs()).append("`\n");
        builder.append("- Contests per run: `").append(provenance.contestsPerRun()).append("`\n\n");

        builder.append("## Scenario Summary\n\n");
        builder.append("| Scenario | Total distortion | Observed capture | Capture 95% CI | Hidden capture | Substitution risk | Hidden influence | Intermediary share | Defensive spend | Comment flood | Enforcement capacity | Admin cost |\n");
        builder.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
        for (ScenarioReport report : reports.stream().sorted(Comparator.comparing(ScenarioReport::totalInfluenceDistortion)).toList()) {
            builder.append("| ").append(report.scenarioName())
                    .append(" | ").append(CsvReportWriter.format(report.totalInfluenceDistortion()))
                    .append(" | ").append(CsvReportWriter.format(report.observedCaptureRate()))
                    .append(" | ").append(CsvReportWriter.formatWilsonInterval(report.capturedContests(), report.totalContests()))
                    .append(" | ").append(CsvReportWriter.format(report.hiddenCaptureIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.substitutionFailureRisk()))
                    .append(" | ").append(CsvReportWriter.format(report.hiddenInfluenceShare()))
                    .append(" | ").append(CsvReportWriter.format(report.intermediarySpendShare()))
                    .append(" | ").append(CsvReportWriter.format(report.defensiveReformSpendShare()))
                    .append(" | ").append(CsvReportWriter.format(report.commentFloodingIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.enforcementCapacityIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.administrativeCostIndex()))
                    .append(" |\n");
        }

        ScenarioReport reformThreat = find(reports, "reform-threat-mobilization");
        ScenarioReport fullBundle = find(reports, "full-anti-capture-bundle");
        ScenarioReport evasion = find(reports, "bundle-with-evasion");
        if (reformThreat != null || fullBundle != null || evasion != null) {
            builder.append("\n## Defensive Reform Blocking\n\n");
        }
        if (reformThreat != null) {
            builder.append("- `reform-threat-mobilization` defensive spend share: `")
                    .append(CsvReportWriter.format(reformThreat.defensiveReformSpendShare()))
                    .append("`, anti-capture success: `")
                    .append(CsvReportWriter.format(reformThreat.antiCaptureSuccessRate()))
                    .append("`, channel switch rate: `")
                    .append(CsvReportWriter.format(reformThreat.channelSwitchRate()))
                    .append("`, hidden influence: `")
                    .append(CsvReportWriter.format(reformThreat.hiddenInfluenceShare()))
                    .append("`, substitution failure risk: `")
                    .append(CsvReportWriter.format(reformThreat.substitutionFailureRisk()))
                    .append("`.\n");
        }
        if (fullBundle != null) {
            builder.append("- `full-anti-capture-bundle` anti-capture success: `")
                    .append(CsvReportWriter.format(fullBundle.antiCaptureSuccessRate()))
                    .append("`, detection rate: `")
                    .append(CsvReportWriter.format(fullBundle.detectionRate()))
                    .append("`, total distortion: `")
                    .append(CsvReportWriter.format(fullBundle.totalInfluenceDistortion()))
                    .append("`.\n");
        }
        if (evasion != null) {
            builder.append("- `bundle-with-evasion` dark-money share: `")
                    .append(CsvReportWriter.format(evasion.darkMoneySpendShare()))
                    .append("`, evasion shift rate: `")
                    .append(CsvReportWriter.format(evasion.evasionShiftRate()))
                    .append("`, evasion penalty: `")
                    .append(CsvReportWriter.format(evasion.evasionPenaltyRate()))
                    .append("`, influence preserved: `")
                    .append(CsvReportWriter.format(evasion.influencePreservationRate()))
                    .append("`, substitution failure risk: `")
                    .append(CsvReportWriter.format(evasion.substitutionFailureRisk()))
                    .append("`.\n");
        }
        appendSubstitutionReadout(builder, reports);
        appendSensitivityReadout(builder, reports);

        builder.append("\n## Interpretation Guardrail\n\n");
        builder.append("Empirical claims are limited to source-moment diagnostics and validation ranges. Synthetic findings are generated by the simulator. Design recommendations are speculative until stronger public-data bridges validate the substitution and hidden-capture mechanisms.\n");
        return builder.toString();
    }

    private static void appendSubstitutionReadout(StringBuilder builder, List<ScenarioReport> reports) {
        ScenarioReport openAccess = find(reports, "open-access-lobbying");
        if (openAccess == null) {
            return;
        }
        List<ScenarioReport> risky = reports.stream()
                .filter(report -> !report.scenarioKey().equals(openAccess.scenarioKey()))
                .filter(report -> report.observedCaptureRate() < openAccess.observedCaptureRate()
                        && (report.hiddenInfluenceShare() > openAccess.hiddenInfluenceShare()
                        || report.totalInfluenceDistortion() > openAccess.totalInfluenceDistortion()
                        || report.substitutionFailureRisk() > openAccess.substitutionFailureRisk()))
                .sorted(Comparator.comparing(ScenarioReport::substitutionFailureRisk).reversed())
                .limit(5)
                .toList();
        if (risky.isEmpty()) {
            return;
        }
        builder.append("\n## Substitution-Failure Readout\n\n");
        builder.append("Lower observed capture is flagged as a possible failure when hidden influence, total distortion, or substitution risk rises relative to open access.\n\n");
        builder.append("| Scenario | Capture change | Hidden change | Distortion change | Substitution risk |\n");
        builder.append("| --- | ---: | ---: | ---: | ---: |\n");
        for (ScenarioReport report : risky) {
            builder.append("| ").append(report.scenarioName())
                    .append(" | ").append(CsvReportWriter.format(report.observedCaptureRate() - openAccess.observedCaptureRate()))
                    .append(" | ").append(CsvReportWriter.format(report.hiddenInfluenceShare() - openAccess.hiddenInfluenceShare()))
                    .append(" | ").append(CsvReportWriter.format(report.totalInfluenceDistortion() - openAccess.totalInfluenceDistortion()))
                    .append(" | ").append(CsvReportWriter.format(report.substitutionFailureRisk()))
                    .append(" |\n");
        }
    }

    private static void appendSensitivityReadout(StringBuilder builder, List<ScenarioReport> reports) {
        List<ScenarioReport> sensitivityReports = reports.stream()
                .filter(report -> report.scenarioKey().startsWith("sensitivity-"))
                .toList();
        if (sensitivityReports.isEmpty()) {
            return;
        }
        ScenarioReport bestDistortion = sensitivityReports.stream()
                .min(Comparator.comparing(ScenarioReport::totalInfluenceDistortion))
                .orElseThrow();
        ScenarioReport worstCapture = sensitivityReports.stream()
                .max(Comparator.comparing(ScenarioReport::observedCaptureRate))
                .orElseThrow();
        ScenarioReport highestSubstitutionRisk = sensitivityReports.stream()
                .max(Comparator.comparing(ScenarioReport::substitutionFailureRisk))
                .orElseThrow();
        builder.append("\n## Sensitivity Readout\n\n");
        builder.append("- Lowest total distortion: `").append(bestDistortion.scenarioName())
                .append("` at `").append(CsvReportWriter.format(bestDistortion.totalInfluenceDistortion())).append("`.\n");
        builder.append("- Highest capture rate: `").append(worstCapture.scenarioName())
                .append("` at `").append(CsvReportWriter.format(worstCapture.observedCaptureRate())).append("`.\n");
        builder.append("- Highest substitution failure risk: `").append(highestSubstitutionRisk.scenarioName())
                .append("` at `").append(CsvReportWriter.format(highestSubstitutionRisk.substitutionFailureRisk())).append("`.\n");
    }

    private static ScenarioReport find(List<ScenarioReport> reports, String key) {
        return reports.stream().filter(report -> report.scenarioKey().equals(key)).findFirst().orElse(null);
    }
}
