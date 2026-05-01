package lobbycapture;

import lobbycapture.arena.ContestOutcome;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.Docket;
import lobbycapture.policy.PolicyContest;
import lobbycapture.simulation.ScenarioCatalog;
import lobbycapture.simulation.WorldState;
import lobbycapture.strategy.ChannelAllocation;
import lobbycapture.strategy.InfluenceResult;
import lobbycapture.strategy.InfluenceStrategy;

import java.util.List;

public final class AdaptationTest {
    private AdaptationTest() {
    }

    public static void main(String[] args) {
        verifiesClientFundingMemoryByDomain();
        verifiesRegulatorQueuePressure();
        verifiesWatchdogBudgetReallocation();
        verifiesReformDecayPressure();
        System.out.println("Adaptation tests passed.");
    }

    private static void verifiesClientFundingMemoryByDomain() {
        WorldState world = world();
        double energyBefore = world.clientFundingMultiplier("energy-producers", "energy");
        double democracyBefore = world.clientFundingMultiplier("energy-producers", "democracy");

        world.adaptInstitutions(outcome(energyContest(), true, false, false, 0));

        require(world.clientFundingMultiplier("energy-producers", "energy") > energyBefore, "energy funding memory should increase after capture returns");
        require(world.clientFundingMultiplier("energy-producers", "democracy") == democracyBefore, "domain-specific memory should not update unrelated domains");
    }

    private static void verifiesRegulatorQueuePressure() {
        WorldState world = world();
        PolicyContest contest = energyContest();
        double queueBefore = world.regulatorQueue("energy");

        world.adaptInstitutions(outcome(contest, true, false, true, 0));

        require(world.regulatorQueue("energy") > queueBefore, "rulemaking workload should increase regulator queue backlog");
        require(inRange(world.regulatorAttention("energy")), "regulator attention should stay bounded");
    }

    private static void verifiesWatchdogBudgetReallocation() {
        WorldState world = world();
        double concentrationBefore = world.watchdogBudgetConcentration();

        world.adaptInstitutions(outcome(technologyContest(), true, false, true, 0));

        require(world.watchdogBudgetConcentration() > concentrationBefore, "watchdog monitoring should concentrate toward high-opacity domains");
        require(inRange(world.watchdogFocus("technology")), "watchdog focus should stay bounded");
    }

    private static void verifiesReformDecayPressure() {
        WorldState world = world();
        PolicyContest reform = reformContest();

        world.adaptInstitutions(outcome(reform, false, true, false, 1));

        require(world.lastReformDecayPressure() > 0.20, "blocked reform with evasion should create reform-decay pressure");
        require(world.lastAdaptationSpeed() > 0.0, "anti-capture contest should move adaptive state");
    }

    private static WorldState world() {
        return new WorldState(ScenarioCatalog.require("reform-threat-mobilization").worldSpec(), 123L);
    }

    private static PolicyContest energyContest() {
        return PolicyContest.of(
                        "test-energy-rule",
                        "Energy rule test",
                        "energy",
                        ContestArena.RULEMAKING,
                        false,
                        0.50,
                        0.36,
                        0.58,
                        0.92,
                        0.62,
                        0.86,
                        0.34
                )
                .withDocket(new Docket("test-energy-docket", "energy", "energy-agency", 400, 1_200, 900, 0.34, 0.24))
                .withInfluence(0.40, 0.32, 0.44, 0.94, 0.12, 0.16, 0.48, 0.44, 0.52, 0.30, 0.22, 0.36);
    }

    private static PolicyContest technologyContest() {
        return PolicyContest.of(
                        "test-tech-rule",
                        "Technology opacity test",
                        "technology",
                        ContestArena.PUBLIC_INFORMATION,
                        false,
                        0.48,
                        0.30,
                        0.62,
                        0.90,
                        0.60,
                        0.82,
                        0.46
                )
                .withDocket(new Docket("test-tech-docket", "technology", "tech-agency", 250, 1_000, 1_100, 0.28, 0.18))
                .withInfluence(0.42, 0.28, 0.44, 0.92, 0.10, 0.18, 0.66, 0.50, 0.72, 0.24, 0.24, 0.32);
    }

    private static PolicyContest reformContest() {
        return PolicyContest.of(
                        "test-reform",
                        "Disclosure reform test",
                        "democracy",
                        ContestArena.LEGISLATIVE,
                        true,
                        0.78,
                        0.64,
                        0.72,
                        0.14,
                        0.06,
                        0.50,
                        0.76
                )
                .withDocket(new Docket("test-reform-docket", "democracy", "ethics-office", 150, 220, 180, 0.52, 0.42))
                .withInfluence(-0.22, 0.42, 0.70, 0.12, 0.36, 0.38, 0.32, 0.26, 0.40, 0.18, 0.30, 0.54);
    }

    private static ContestOutcome outcome(
            PolicyContest contest,
            boolean captured,
            boolean antiCaptureReform,
            boolean detected,
            int evasionShifts
    ) {
        InfluenceStrategy strategy = antiCaptureReform ? InfluenceStrategy.DEFENSIVE_REFORM : InfluenceStrategy.BALANCED;
        double defensiveSpend = antiCaptureReform ? 0.72 : 0.0;
        InfluenceResult influence = new InfluenceResult(
                contest,
                ChannelAllocation.forStrategy(strategy, 1.0),
                1.0,
                defensiveSpend,
                0.12,
                0.22,
                0.38,
                1,
                evasionShifts,
                List.of()
        );
        return new ContestOutcome(
                contest,
                contest.arena(),
                influence,
                captured,
                false,
                detected,
                detected,
                false,
                captured ? 0.78 : 0.22,
                captured ? 0.24 : 0.72,
                captured ? 0.62 : 0.20,
                captured ? 0.54 : 0.14,
                captured ? 0.48 : 0.12,
                captured ? 0.42 : 0.10,
                detected ? 0.66 : 0.18,
                detected ? 0.34 : 0.0,
                evasionShifts > 0 ? 0.24 : 0.02,
                0.18,
                "test outcome"
        );
    }

    private static boolean inRange(double value) {
        return value >= 0.0 && value <= 1.0;
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
