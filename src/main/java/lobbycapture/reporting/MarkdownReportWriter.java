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
        builder.append("| Scenario | Directional | Capture rate | Anti-capture success | Defensive spend | Dark-money share | Client funding | Reg attention | Watchdog focus | Detection | Admin cost |\n");
        builder.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n");
        for (ScenarioReport report : reports.stream().sorted(Comparator.comparing(ScenarioReport::directionalScore).reversed()).toList()) {
            builder.append("| ").append(report.scenarioName())
                    .append(" | ").append(CsvReportWriter.format(report.directionalScore()))
                    .append(" | ").append(CsvReportWriter.format(report.captureRate()))
                    .append(" | ").append(CsvReportWriter.format(report.antiCaptureSuccessRate()))
                    .append(" | ").append(CsvReportWriter.format(report.defensiveReformSpendShare()))
                    .append(" | ").append(CsvReportWriter.format(report.darkMoneySpendShare()))
                    .append(" | ").append(CsvReportWriter.format(report.clientFundingPerContest()))
                    .append(" | ").append(CsvReportWriter.format(report.regulatorAttentionIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.watchdogFocusIndex()))
                    .append(" | ").append(CsvReportWriter.format(report.detectionRate()))
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
                    .append("`, evasion penalty: `")
                    .append(CsvReportWriter.format(evasion.evasionPenaltyRate()))
                    .append("`, anti-capture success: `")
                    .append(CsvReportWriter.format(evasion.antiCaptureSuccessRate()))
                    .append("`.\n");
        }
        appendSensitivityReadout(builder, reports);

        builder.append("\n## Interpretation Guardrail\n\n");
        builder.append("The metrics are comparative simulation outputs. Calibration files define plausibility bands; they do not make causal empirical claims.\n");
        return builder.toString();
    }

    private static void appendSensitivityReadout(StringBuilder builder, List<ScenarioReport> reports) {
        List<ScenarioReport> sensitivityReports = reports.stream()
                .filter(report -> report.scenarioKey().startsWith("sensitivity-"))
                .toList();
        if (sensitivityReports.isEmpty()) {
            return;
        }
        ScenarioReport bestDirectional = sensitivityReports.stream()
                .max(Comparator.comparing(ScenarioReport::directionalScore))
                .orElseThrow();
        ScenarioReport worstCapture = sensitivityReports.stream()
                .max(Comparator.comparing(ScenarioReport::captureRate))
                .orElseThrow();
        ScenarioReport highestEvasion = sensitivityReports.stream()
                .max(Comparator.comparing(ScenarioReport::darkMoneySpendShare))
                .orElseThrow();
        builder.append("\n## Sensitivity Readout\n\n");
        builder.append("- Highest directional score: `").append(bestDirectional.scenarioName())
                .append("` at `").append(CsvReportWriter.format(bestDirectional.directionalScore())).append("`.\n");
        builder.append("- Highest capture rate: `").append(worstCapture.scenarioName())
                .append("` at `").append(CsvReportWriter.format(worstCapture.captureRate())).append("`.\n");
        builder.append("- Highest dark-money share: `").append(highestEvasion.scenarioName())
                .append("` at `").append(CsvReportWriter.format(highestEvasion.darkMoneySpendShare())).append("`.\n");
    }

    private static ScenarioReport find(List<ScenarioReport> reports, String key) {
        return reports.stream().filter(report -> report.scenarioKey().equals(key)).findFirst().orElse(null);
    }
}
