package lobbycapture.reporting;

import lobbycapture.metrics.ScenarioReport;

import java.util.Comparator;
import java.util.List;

public final class MarkdownReportWriter {
    public String write(List<ScenarioReport> reports, ReportProvenance provenance) {
        StringBuilder builder = new StringBuilder();
        builder.append("# Lobby Capture Campaign\n\n");
        builder.append("- Generated: `").append(provenance.generatedAt()).append("`\n");
        builder.append("- Seed: `").append(provenance.seed()).append("`\n");
        builder.append("- Runs per scenario: `").append(provenance.runs()).append("`\n");
        builder.append("- Contests per run: `").append(provenance.contestsPerRun()).append("`\n\n");

        builder.append("## Scenario Summary\n\n");
        builder.append("| Scenario | Directional | Capture rate | Anti-capture success | Defensive spend | Dark-money share | Detection | Admin cost |\n");
        builder.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
        for (ScenarioReport report : reports.stream().sorted(Comparator.comparing(ScenarioReport::directionalScore).reversed()).toList()) {
            builder.append("| ").append(report.scenarioName())
                    .append(" | ").append(CsvReportWriter.format(report.directionalScore()))
                    .append(" | ").append(CsvReportWriter.format(report.captureRate()))
                    .append(" | ").append(CsvReportWriter.format(report.antiCaptureSuccessRate()))
                    .append(" | ").append(CsvReportWriter.format(report.defensiveReformSpendShare()))
                    .append(" | ").append(CsvReportWriter.format(report.darkMoneySpendShare()))
                    .append(" | ").append(CsvReportWriter.format(report.detectionRate()))
                    .append(" | ").append(CsvReportWriter.format(report.administrativeCostIndex()))
                    .append(" |\n");
        }

        builder.append("\n## Defensive Reform Blocking\n\n");
        ScenarioReport reformThreat = find(reports, "reform-threat-mobilization");
        ScenarioReport fullBundle = find(reports, "full-anti-capture-bundle");
        ScenarioReport evasion = find(reports, "bundle-with-evasion");
        if (reformThreat != null) {
            builder.append("- `reform-threat-mobilization` defensive spend share: `")
                    .append(CsvReportWriter.format(reformThreat.defensiveReformSpendShare()))
                    .append("`, anti-capture success: `")
                    .append(CsvReportWriter.format(reformThreat.antiCaptureSuccessRate()))
                    .append("`, channel switch rate: `")
                    .append(CsvReportWriter.format(reformThreat.channelSwitchRate()))
                    .append("`.\n");
        }
        if (fullBundle != null) {
            builder.append("- `full-anti-capture-bundle` anti-capture success: `")
                    .append(CsvReportWriter.format(fullBundle.antiCaptureSuccessRate()))
                    .append("`, detection rate: `")
                    .append(CsvReportWriter.format(fullBundle.detectionRate()))
                    .append("`, capture rate: `")
                    .append(CsvReportWriter.format(fullBundle.captureRate()))
                    .append("`.\n");
        }
        if (evasion != null) {
            builder.append("- `bundle-with-evasion` dark-money share: `")
                    .append(CsvReportWriter.format(evasion.darkMoneySpendShare()))
                    .append("`, evasion shift rate: `")
                    .append(CsvReportWriter.format(evasion.evasionShiftRate()))
                    .append("`, anti-capture success: `")
                    .append(CsvReportWriter.format(evasion.antiCaptureSuccessRate()))
                    .append("`.\n");
        }

        builder.append("\n## Interpretation Guardrail\n\n");
        builder.append("The metrics are comparative simulation outputs. Calibration files define plausibility bands; they do not make causal empirical claims.\n");
        return builder.toString();
    }

    private static ScenarioReport find(List<ScenarioReport> reports, String key) {
        return reports.stream().filter(report -> report.scenarioKey().equals(key)).findFirst().orElse(null);
    }
}

