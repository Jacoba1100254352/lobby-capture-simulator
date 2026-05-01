package lobbycapture.simulation;

import lobbycapture.actor.Candidate;
import lobbycapture.actor.EnforcementAgency;
import lobbycapture.actor.InterestClient;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.actor.PublicOfficial;
import lobbycapture.actor.Regulator;
import lobbycapture.actor.WatchdogGroup;
import lobbycapture.arena.ContestOutcome;
import lobbycapture.budget.ContributionLedger;
import lobbycapture.calibration.CalibrationProfile;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.strategy.EvasionProfile;
import lobbycapture.strategy.InfluenceStrategy;
import lobbycapture.strategy.StrategyMemory;
import lobbycapture.util.Values;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public final class WorldState {
    private final WorldSpec spec;
    private final Random random;
    private final SimulationClock clock = new SimulationClock();
    private final ContributionLedger contributionLedger = new ContributionLedger();
    private final Map<String, Double> remainingBudgetByLobby = new HashMap<>();
    private final Map<String, StrategyMemory> memoryByLobby = new HashMap<>();
    private final Map<String, Double> clientFundingMultiplierByClient = new HashMap<>();
    private final Map<String, Double> regulatorAttentionByDomain = new HashMap<>();
    private final Map<String, Double> watchdogFocusByDomain = new HashMap<>();

    public WorldState(WorldSpec spec, long seed) {
        this.spec = spec;
        this.random = new Random(seed);
        for (LobbyOrganization organization : spec.lobbyOrganizations()) {
            remainingBudgetByLobby.put(organization.id(), organization.totalBudget());
            memoryByLobby.put(organization.id(), new StrategyMemory(organization.initialStrategy()));
        }
        for (InterestClient client : spec.clients()) {
            clientFundingMultiplierByClient.put(client.id(), 1.0);
        }
        for (Regulator regulator : spec.regulators()) {
            regulatorAttentionByDomain.merge(
                    regulator.domain(),
                    Values.clamp((0.45 * regulator.staffCapacity()) + (0.35 * regulator.commentProcessingCapacity())
                            + (0.20 * regulator.independence()), 0.0, 1.0),
                    Math::max
            );
        }
        double watchdogBase = spec.watchdogs().stream()
                .mapToDouble(watchdog -> (0.42 * watchdog.investigativeCapacity())
                        + (0.30 * watchdog.publicReach())
                        + (0.28 * watchdog.enforcementReferralSkill()))
                .average()
                .orElse(0.35);
        for (PolicyContest contest : spec.contestTemplates()) {
            watchdogFocusByDomain.putIfAbsent(contest.issueDomain(), Values.clamp(watchdogBase * 0.55, 0.0, 1.0));
        }
    }

    public ReformRegime reformRegime() {
        return spec.reformRegime();
    }

    public CalibrationProfile calibrationProfile() {
        return spec.calibrationProfile();
    }

    public EvasionProfile evasionProfile() {
        return spec.evasionProfile();
    }

    public double spendScale() {
        return spec.spendScale();
    }

    public double pressurePerSpend() {
        return spec.pressurePerSpend();
    }

    public double publicCampaignEffect() {
        return spec.publicCampaignEffect();
    }

    public double evasionFreedom() {
        return spec.evasionFreedom();
    }

    public boolean adaptiveStrategies() {
        return spec.adaptiveStrategies();
    }

    public List<LobbyOrganization> lobbyOrganizations() {
        return spec.lobbyOrganizations();
    }

    public List<InterestClient> clients() {
        return spec.clients();
    }

    public List<PublicOfficial> officials() {
        return spec.officials();
    }

    public List<Regulator> regulators() {
        return spec.regulators();
    }

    public List<WatchdogGroup> watchdogs() {
        return spec.watchdogs();
    }

    public List<Candidate> candidates() {
        return spec.candidates();
    }

    public List<EnforcementAgency> enforcementAgencies() {
        return spec.enforcementAgencies();
    }

    public Random random() {
        return random;
    }

    public SimulationClock clock() {
        return clock;
    }

    public ContributionLedger contributionLedger() {
        return contributionLedger;
    }

    public double remainingBudget(String lobbyId) {
        return remainingBudgetByLobby.getOrDefault(lobbyId, 0.0);
    }

    public double spendBudget(String lobbyId, double requested) {
        double remaining = remainingBudget(lobbyId);
        double spent = Math.min(remaining, requested);
        remainingBudgetByLobby.put(lobbyId, remaining - spent);
        return spent;
    }

    public void topUpBudget(String lobbyId, double amount) {
        remainingBudgetByLobby.merge(lobbyId, amount, Double::sum);
    }

    public StrategyMemory memoryFor(String lobbyId, InfluenceStrategy initialStrategy) {
        return memoryByLobby.computeIfAbsent(lobbyId, ignored -> new StrategyMemory(initialStrategy));
    }

    public double clientFundingMultiplier(String clientId) {
        return clientFundingMultiplierByClient.getOrDefault(clientId, 1.0);
    }

    public double regulatorAttention(String issueDomain) {
        return regulatorAttentionByDomain.getOrDefault(issueDomain, averageRegulatorAttention());
    }

    public double watchdogFocus(String issueDomain) {
        return watchdogFocusByDomain.getOrDefault(issueDomain, averageWatchdogFocus());
    }

    public double averageClientFundingMultiplier() {
        return average(clientFundingMultiplierByClient, 1.0);
    }

    public double averageRegulatorAttention() {
        return average(regulatorAttentionByDomain, 0.35);
    }

    public double averageWatchdogFocus() {
        return average(watchdogFocusByDomain, 0.25);
    }

    public void adaptInstitutions(ContestOutcome outcome) {
        if (!adaptiveStrategies()) {
            return;
        }
        PolicyContest contest = outcome.contest();
        adaptClients(contest, outcome);
        adaptRegulators(contest, outcome);
        adaptWatchdogs(contest, outcome);
    }

    private void adaptClients(PolicyContest contest, ContestOutcome outcome) {
        for (InterestClient client : clients()) {
            if (!clientAffected(client, contest)) {
                continue;
            }
            double old = clientFundingMultiplier(client.id());
            double captureReturn = outcome.captured() ? contest.privateGain() - (0.42 * client.publicHarmExternality()) : -0.05 * contest.privateGain();
            double reformReturn = contest.antiCaptureReform()
                    ? (outcome.antiCaptureReformEnacted() ? -0.18 : 0.16) * client.riskTolerance()
                    : 0.0;
            double sanctionDrag = outcome.sanctioned()
                    ? (0.20 + (0.20 * outcome.sanctionCost())) * (0.35 + client.reputationalRisk())
                    : 0.0;
            double delta = (0.08 * captureReturn) + reformReturn - sanctionDrag;
            clientFundingMultiplierByClient.put(client.id(), Values.clamp(old + delta, 0.55, 1.75));
        }
    }

    private void adaptRegulators(PolicyContest contest, ContestOutcome outcome) {
        double old = regulatorAttention(contest.issueDomain());
        double docketAlarm = (0.22 * contest.commentRecordDistortion()) + (0.10 * contest.docket().templateSaturation());
        double captureAlarm = outcome.captured() ? 0.16 : 0.0;
        double sanctionLearning = outcome.detected() ? 0.06 : 0.0;
        double quietDecay = outcome.captured() || contest.commentRecordDistortion() > 0.08 ? 0.0 : 0.025;
        regulatorAttentionByDomain.put(
                contest.issueDomain(),
                Values.clamp(old + docketAlarm + captureAlarm + sanctionLearning - quietDecay, 0.0, 1.0)
        );
    }

    private void adaptWatchdogs(PolicyContest contest, ContestOutcome outcome) {
        double old = watchdogFocus(contest.issueDomain());
        double opacityAlarm = (0.18 * contest.darkMoneyInfluence()) + (0.12 * contest.informationDistortion())
                + (0.10 * contest.commentRecordDistortion()) + (outcome.captured() ? 0.14 : 0.0);
        double referralLearning = outcome.detected() ? 0.05 : 0.0;
        double decay = opacityAlarm < 0.04 ? 0.02 : 0.0;
        watchdogFocusByDomain.put(
                contest.issueDomain(),
                Values.clamp(old + opacityAlarm + referralLearning - decay, 0.0, 1.0)
        );
    }

    private static boolean clientAffected(InterestClient client, PolicyContest contest) {
        return client.sector().equals(contest.issueDomain())
                || client.privateGainByPolicy().containsKey(contest.issueDomain())
                || (contest.antiCaptureReform() && client.privateGainByPolicy().containsKey("democracy"));
    }

    private static double average(Map<String, Double> values, double fallback) {
        if (values.isEmpty()) {
            return fallback;
        }
        return values.values().stream().mapToDouble(Double::doubleValue).average().orElse(fallback);
    }
}
