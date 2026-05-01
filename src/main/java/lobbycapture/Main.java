package lobbycapture;

import lobbycapture.metrics.ScenarioReport;
import lobbycapture.reporting.AblationRunner;
import lobbycapture.reporting.CampaignRunner;
import lobbycapture.reporting.InteractionRunner;
import lobbycapture.reporting.SensitivityRunner;
import lobbycapture.simulation.Scenario;
import lobbycapture.simulation.ScenarioCatalog;
import lobbycapture.simulation.Simulator;

import java.nio.file.Path;
import java.util.List;
import java.util.Locale;

public final class Main {
    private Main() {
    }

    public static void main(String[] args) throws Exception {
        Options options = Options.parse(args);
        if (options.help) {
            printHelp();
            return;
        }
        if (options.list) {
            for (Scenario scenario : ScenarioCatalog.all()) {
                System.out.println(scenario.key() + " - " + scenario.name());
            }
            return;
        }
        if (options.campaign) {
            new CampaignRunner().writeCampaign(Path.of("reports"), options.runs, options.contests, options.seed);
            System.out.println("Wrote reports/lobby-capture-campaign.csv");
            System.out.println("Wrote reports/lobby-capture-campaign.md");
            return;
        }
        if (options.sensitivity) {
            new SensitivityRunner().write(Path.of("reports"), options.runs, options.contests, options.seed);
            System.out.println("Wrote reports/lobby-capture-sensitivity.csv");
            System.out.println("Wrote reports/lobby-capture-sensitivity.md");
            return;
        }
        if (options.ablation) {
            new AblationRunner().write(Path.of("reports"), options.runs, options.contests, options.seed);
            System.out.println("Wrote reports/lobby-capture-ablation.csv");
            System.out.println("Wrote reports/lobby-capture-ablation.md");
            return;
        }
        if (options.interactions) {
            new InteractionRunner().write(Path.of("reports"), options.runs, options.contests, options.seed);
            System.out.println("Wrote reports/lobby-capture-interactions.csv");
            System.out.println("Wrote reports/lobby-capture-interactions.md");
            return;
        }
        Scenario scenario = ScenarioCatalog.require(options.scenarioKey);
        ScenarioReport report = new Simulator().run(scenario, options.runs, options.contests, options.seed);
        printSummary(report);
    }

    private static void printSummary(ScenarioReport report) {
        System.out.println("scenario=" + report.scenarioKey());
        System.out.println("name=" + report.scenarioName());
        System.out.println("totalContests=" + report.totalContests());
        System.out.println("capturedContests=" + report.capturedContests());
        System.out.println("captureRate=" + format(report.captureRate()));
        System.out.println("antiCaptureSuccessRate=" + format(report.antiCaptureSuccessRate()));
        System.out.println("defensiveReformSpendShare=" + format(report.defensiveReformSpendShare()));
        System.out.println("darkMoneySpendShare=" + format(report.darkMoneySpendShare()));
        System.out.println("channelSwitchRate=" + format(report.channelSwitchRate()));
        System.out.println("evasionShiftRate=" + format(report.evasionShiftRate()));
        System.out.println("hiddenInfluenceShare=" + format(report.hiddenInfluenceShare()));
        System.out.println("influencePreservationRate=" + format(report.influencePreservationRate()));
        System.out.println("commentUniqueInformationShare=" + format(report.commentUniqueInformationShare()));
        System.out.println("commentReviewBurden=" + format(report.commentReviewBurden()));
        System.out.println("detectionRate=" + format(report.detectionRate()));
        System.out.println("directionalScore=" + format(report.directionalScore()));
    }

    private static void printHelp() {
        System.out.println("""
                Lobby Capture Simulator

                Usage:
                  make run ARGS="--list"
                  make run ARGS="--scenario reform-threat-mobilization --runs 10 --contests 30 --seed 7"
                  make campaign
                  make sensitivity
                  make ablation
                  make interactions

                Options:
                  --list                 List scenarios.
                  --scenario KEY         Scenario key to run.
                  --runs N               Number of independent runs. Default: 10.
                  --contests N           Contests per run. Default: 40.
                  --seed N               Random seed. Default: 1.
                  --campaign             Run all scenarios and write reports.
                  --sensitivity          Sweep reform strengths and evasion freedom.
                  --ablation             Remove each full-bundle reform component in turn.
                  --interactions         Run two-way reform interaction sweeps.
                  --help                 Show this help.
                """);
    }

    private static String format(double value) {
        return String.format(Locale.US, "%.4f", value);
    }

    private record Options(
            String scenarioKey,
            int runs,
            int contests,
            long seed,
            boolean list,
            boolean campaign,
            boolean sensitivity,
            boolean ablation,
            boolean interactions,
            boolean help
    ) {
        private static Options parse(String[] args) {
            String scenario = "reform-threat-mobilization";
            int runs = 10;
            int contests = 40;
            long seed = 1L;
            boolean list = false;
            boolean campaign = false;
            boolean sensitivity = false;
            boolean ablation = false;
            boolean interactions = false;
            boolean help = false;
            List<String> arguments = List.of(args);
            for (int index = 0; index < arguments.size(); index++) {
                String arg = arguments.get(index);
                switch (arg) {
                    case "--scenario" -> scenario = requireValue(arguments, ++index, arg);
                    case "--runs" -> runs = Integer.parseInt(requireValue(arguments, ++index, arg));
                    case "--contests" -> contests = Integer.parseInt(requireValue(arguments, ++index, arg));
                    case "--seed" -> seed = Long.parseLong(requireValue(arguments, ++index, arg));
                    case "--list" -> list = true;
                    case "--campaign" -> campaign = true;
                    case "--sensitivity" -> sensitivity = true;
                    case "--ablation" -> ablation = true;
                    case "--interactions" -> interactions = true;
                    case "--help", "-h" -> help = true;
                    default -> throw new IllegalArgumentException("Unknown argument: " + arg);
                }
            }
            if (runs <= 0 || contests <= 0) {
                throw new IllegalArgumentException("--runs and --contests must be positive.");
            }
            return new Options(scenario, runs, contests, seed, list, campaign, sensitivity, ablation, interactions, help);
        }

        private static String requireValue(List<String> arguments, int index, String option) {
            if (index >= arguments.size()) {
                throw new IllegalArgumentException(option + " requires a value.");
            }
            return arguments.get(index);
        }
    }
}
