package lobbycapture.strategy;

import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.util.Values;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

public final class StrategyMemory {
    private final Map<InfluenceStrategy, Double> returns = new EnumMap<>(InfluenceStrategy.class);
    private final Map<String, Double> issueMultiplier = new HashMap<>();
    private InfluenceStrategy currentStrategy;
    private double budgetMultiplier = 1.0;
    private double reformThreat = 1.0;
    private int channelSwitches;
    private int evasionShifts;

    public StrategyMemory(InfluenceStrategy initialStrategy) {
        this.currentStrategy = initialStrategy;
    }

    public InfluenceStrategy currentStrategy() {
        return currentStrategy;
    }

    public double budgetMultiplier() {
        return budgetMultiplier;
    }

    public double issueMultiplier(String issueDomain) {
        return issueMultiplier.getOrDefault(issueDomain, 1.0);
    }

    public double reformThreat() {
        return reformThreat;
    }

    public int channelSwitches() {
        return channelSwitches;
    }

    public int evasionShifts() {
        return evasionShifts;
    }

    public void recordEvasionShift() {
        evasionShifts++;
    }

    public void recordReturn(InfluenceStrategy strategy, double signal, PolicyContest contest) {
        double current = returns.getOrDefault(strategy, 0.0);
        returns.put(strategy, (0.72 * current) + (0.28 * signal));
        budgetMultiplier = Values.clamp(budgetMultiplier + (0.08 * signal), 0.35, 2.50);
        String domain = contest.issueDomain();
        double issue = issueMultiplier.getOrDefault(domain, 1.0);
        issueMultiplier.put(domain, Values.clamp(issue + (0.10 * signal), 0.35, 2.75));
        if (contest.antiCaptureReform()) {
            reformThreat = Values.clamp(reformThreat + (signal > 0.0 ? 0.13 : -0.07), 0.45, 2.60);
        }
    }

    public void adapt(PolicyContest contest, boolean captured, boolean antiCaptureReformEnacted) {
        InfluenceStrategy next = nextStrategy(contest, captured, antiCaptureReformEnacted);
        if (next != currentStrategy) {
            channelSwitches++;
        }
        currentStrategy = next;
    }

    private InfluenceStrategy nextStrategy(PolicyContest contest, boolean captured, boolean antiCaptureReformEnacted) {
        InfluenceStrategy learnedBest = bestLearnedStrategy();
        if (contest.antiCaptureReform()) {
            return antiCaptureReformEnacted ? InfluenceStrategy.PUBLIC_CAMPAIGN : InfluenceStrategy.DEFENSIVE_REFORM;
        }
        if (learnedBest != null && captured) {
            return learnedBest;
        }
        if (contest.arena() == ContestArena.ELECTION) {
            return contest.darkMoneyInfluence() > contest.campaignFinanceInfluence()
                    ? InfluenceStrategy.DARK_MONEY
                    : InfluenceStrategy.CAMPAIGN_FINANCE;
        }
        if (contest.arena() == ContestArena.RULEMAKING && contest.technicalComplexity() >= 0.60) {
            return contest.salience() <= 0.50 ? InfluenceStrategy.INTERMEDIARY : InfluenceStrategy.INFORMATION_DISTORTION;
        }
        if (contest.arena() == ContestArena.LITIGATION || contest.legalVulnerability() >= 0.58) {
            return InfluenceStrategy.LITIGATION_THREAT;
        }
        if (contest.arena() == ContestArena.PUBLIC_INFORMATION && contest.commentRecordDistortion() >= 0.40) {
            return InfluenceStrategy.INTERMEDIARY;
        }
        if (contest.revolvingDoorInfluence() >= 0.42) {
            return InfluenceStrategy.REVOLVING_DOOR;
        }
        if (!captured && contest.salience() >= 0.62) {
            return InfluenceStrategy.PUBLIC_CAMPAIGN;
        }
        if (contest.privateGain() >= 0.58) {
            return InfluenceStrategy.DIRECT_ACCESS;
        }
        return learnedBest == null ? InfluenceStrategy.BALANCED : learnedBest;
    }

    private InfluenceStrategy bestLearnedStrategy() {
        InfluenceStrategy best = null;
        double bestReturn = -Double.MAX_VALUE;
        for (Map.Entry<InfluenceStrategy, Double> entry : returns.entrySet()) {
            if (entry.getValue() > bestReturn) {
                best = entry.getKey();
                bestReturn = entry.getValue();
            }
        }
        return bestReturn > 0.04 ? best : null;
    }
}
