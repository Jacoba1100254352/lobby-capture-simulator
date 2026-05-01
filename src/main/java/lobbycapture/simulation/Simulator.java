package lobbycapture.simulation;

import lobbycapture.arena.ContestOutcome;
import lobbycapture.arena.ElectionArena;
import lobbycapture.arena.EnforcementArena;
import lobbycapture.arena.InfluenceArena;
import lobbycapture.arena.LegislativeArena;
import lobbycapture.arena.LitigationArena;
import lobbycapture.arena.ProcurementArena;
import lobbycapture.arena.PublicInformationArena;
import lobbycapture.arena.RulemakingArena;
import lobbycapture.metrics.MetricsAccumulator;
import lobbycapture.metrics.ScenarioReport;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.strategy.InfluenceResult;
import lobbycapture.strategy.LobbyAllocationEngine;
import lobbycapture.util.Values;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public final class Simulator {
    private final Map<ContestArena, InfluenceArena> arenas = new EnumMap<>(ContestArena.class);
    private final LobbyAllocationEngine lobbying = new LobbyAllocationEngine();

    public Simulator() {
        register(new LegislativeArena());
        register(new RulemakingArena());
        register(new ElectionArena());
        register(new ProcurementArena());
        register(new LitigationArena());
        register(new EnforcementArena());
        register(new PublicInformationArena());
    }

    public ScenarioReport run(Scenario scenario, int runs, int contestsPerRun, long seed) {
        MetricsAccumulator metrics = new MetricsAccumulator();
        for (int run = 0; run < runs; run++) {
            WorldState world = new WorldState(scenario.worldSpec(), seed + (run * 10_007L));
            for (int index = 0; index < contestsPerRun; index++) {
                PolicyContest contest = nextContest(scenario.worldSpec().contestTemplates(), world.random(), run, index);
                InfluenceResult influence = lobbying.apply(contest, world);
                ContestOutcome outcome = arenas.get(influence.contest().arena()).resolve(influence, world);
                metrics.add(outcome, world.reformRegime());
                lobbying.observe(outcome, world);
                world.clock().advance();
            }
        }
        return metrics.toReport(scenario.key(), scenario.name());
    }

    private void register(InfluenceArena arena) {
        arenas.put(arena.arenaType(), arena);
    }

    private static PolicyContest nextContest(List<PolicyContest> templates, Random random, int run, int index) {
        PolicyContest template = templates.get(random.nextInt(templates.size()));
        double publicBenefit = jitter(template.truePublicBenefit(), random, 0.08);
        double perceivedSupport = jitter(template.perceivedPublicSupport(), random, 0.10);
        double trueSupport = jitter(template.truePublicSupport(), random, 0.08);
        double privateGain = jitter(template.privateGain(), random, 0.09);
        double harm = jitter(template.concentratedHarm(), random, 0.07);
        double complexity = jitter(template.technicalComplexity(), random, 0.06);
        double salience = jitter(template.salience(), random, 0.08);
        PolicyContest contest = PolicyContest.of(
                template.id() + "-" + run + "-" + index,
                template.title(),
                template.issueDomain(),
                template.arena(),
                template.antiCaptureReform(),
                publicBenefit,
                perceivedSupport,
                trueSupport,
                privateGain,
                harm,
                complexity,
                salience
        ).withDocket(template.docket());
        return contest.withInfluence(
                template.lobbyPressure(),
                perceivedSupport,
                publicBenefit,
                privateGain,
                template.publicAdvocatePressure(),
                template.watchdogPressure(),
                template.informationDistortion(),
                template.commentRecordDistortion(),
                template.darkMoneyInfluence(),
                template.revolvingDoorInfluence(),
                template.campaignFinanceInfluence(),
                template.litigationThreat()
        );
    }

    private static double jitter(double value, Random random, double range) {
        return Values.clamp(value + ((random.nextDouble() - 0.5) * 2.0 * range), 0.0, 1.0);
    }
}
