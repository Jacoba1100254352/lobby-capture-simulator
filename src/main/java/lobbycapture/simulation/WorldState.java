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
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

public final class WorldState {
    private final WorldSpec spec;
    private final Random random;
    private final SimulationClock clock = new SimulationClock();
    private final ContributionLedger contributionLedger = new ContributionLedger();
    private final Map<String, Double> remainingBudgetByLobby = new HashMap<>();
    private final Map<String, StrategyMemory> memoryByLobby = new HashMap<>();
    private final Map<String, Double> clientFundingMultiplierByClientDomain = new HashMap<>();
    private final Map<String, Double> regulatorAttentionByDomain = new HashMap<>();
    private final Map<String, Double> regulatorQueueByDomain = new HashMap<>();
    private final Map<String, Double> regulatorProcessingCapacityByDomain = new HashMap<>();
    private final Map<String, Double> watchdogFocusByDomain = new HashMap<>();
    private final double watchdogBudgetTotal;
    private double lastAdaptationSpeed;
    private double lastReformDecayPressure;

    public WorldState(WorldSpec spec, long seed) {
        this.spec = spec;
        this.random = new Random(seed);
        Set<String> domains = modelDomains();
        for (LobbyOrganization organization : spec.lobbyOrganizations()) {
            remainingBudgetByLobby.put(organization.id(), organization.totalBudget());
            memoryByLobby.put(organization.id(), new StrategyMemory(organization.initialStrategy()));
        }
        for (InterestClient client : spec.clients()) {
            for (String domain : domains) {
                if (clientAffectedByDomain(client, domain)) {
                    clientFundingMultiplierByClientDomain.put(clientDomainKey(client.id(), domain), 1.0);
                }
            }
        }
        for (Regulator regulator : spec.regulators()) {
            regulatorAttentionByDomain.merge(
                    regulator.domain(),
                    Values.clamp((0.45 * regulator.staffCapacity()) + (0.35 * regulator.commentProcessingCapacity())
                            + (0.20 * regulator.independence()), 0.0, 1.0),
                    Math::max
            );
            regulatorProcessingCapacityByDomain.merge(
                    regulator.domain(),
                    Values.clamp((0.62 * regulator.commentProcessingCapacity()) + (0.38 * regulator.staffCapacity()), 0.0, 1.0),
                    Math::max
            );
        }
        for (String domain : domains) {
            regulatorAttentionByDomain.putIfAbsent(domain, 0.35);
            regulatorProcessingCapacityByDomain.putIfAbsent(domain, 0.32);
            regulatorQueueByDomain.put(domain, Values.clamp(0.18 * (1.0 - regulatorProcessingCapacity(domain)), 0.0, 1.0));
        }
        double watchdogBase = spec.watchdogs().stream()
                .mapToDouble(watchdog -> (0.42 * watchdog.investigativeCapacity())
                        + (0.30 * watchdog.publicReach())
                        + (0.28 * watchdog.enforcementReferralSkill()))
                .average()
                .orElse(0.35);
        double perDomainWatchdogBudget = Values.clamp(watchdogBase * 0.55, 0.0, 1.0);
        for (String domain : domains) {
            watchdogFocusByDomain.putIfAbsent(domain, perDomainWatchdogBudget);
        }
        watchdogBudgetTotal = Math.max(0.10, perDomainWatchdogBudget * Math.max(1, domains.size()));
        normalizeWatchdogBudgets();
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
        String prefix = clientId + "::";
        return clientFundingMultiplierByClientDomain.entrySet().stream()
                .filter(entry -> entry.getKey().startsWith(prefix))
                .mapToDouble(Map.Entry::getValue)
                .average()
                .orElse(1.0);
    }

    public double clientFundingMultiplier(String clientId, String issueDomain) {
        return clientFundingMultiplierByClientDomain.getOrDefault(clientDomainKey(clientId, issueDomain), clientFundingMultiplier(clientId));
    }

    public double regulatorAttention(String issueDomain) {
        return regulatorAttentionByDomain.getOrDefault(issueDomain, averageRegulatorAttention());
    }

    public double regulatorQueue(String issueDomain) {
        return regulatorQueueByDomain.getOrDefault(issueDomain, averageRegulatorQueue());
    }

    public double regulatorProcessingCapacity(String issueDomain) {
        return regulatorProcessingCapacityByDomain.getOrDefault(issueDomain, averageRegulatorProcessingCapacity());
    }

    public double watchdogFocus(String issueDomain) {
        return watchdogFocusByDomain.getOrDefault(issueDomain, averageWatchdogFocus());
    }

    public double averageClientFundingMultiplier() {
        return average(clientFundingMultiplierByClientDomain, 1.0);
    }

    public double averageRegulatorAttention() {
        return average(regulatorAttentionByDomain, 0.35);
    }

    public double averageRegulatorQueue() {
        return average(regulatorQueueByDomain, 0.10);
    }

    public double averageRegulatorProcessingCapacity() {
        return average(regulatorProcessingCapacityByDomain, 0.32);
    }

    public double averageWatchdogFocus() {
        return average(watchdogFocusByDomain, 0.25);
    }

    public double watchdogBudgetConcentration() {
        double total = watchdogFocusByDomain.values().stream().mapToDouble(Double::doubleValue).sum();
        if (total <= 0.0) {
            return 0.0;
        }
        double max = watchdogFocusByDomain.values().stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
        return Values.clamp(max / total, 0.0, 1.0);
    }

    public double lastAdaptationSpeed() {
        return lastAdaptationSpeed;
    }

    public double lastReformDecayPressure() {
        return lastReformDecayPressure;
    }

    public void adaptInstitutions(ContestOutcome outcome) {
        if (!adaptiveStrategies()) {
            lastAdaptationSpeed = 0.0;
            lastReformDecayPressure = 0.0;
            return;
        }
        PolicyContest contest = outcome.contest();
        double movement = MetricAverage.of(
                adaptClients(contest, outcome),
                adaptRegulators(contest, outcome),
                adaptWatchdogs(contest, outcome)
        );
        lastAdaptationSpeed = Values.clamp((0.70 * lastAdaptationSpeed) + (0.30 * movement), 0.0, 1.0);
        lastReformDecayPressure = reformDecayPressure(outcome);
    }

    private double adaptClients(PolicyContest contest, ContestOutcome outcome) {
        double movement = 0.0;
        int changed = 0;
        String domain = contest.antiCaptureReform() ? "democracy" : contest.issueDomain();
        for (InterestClient client : clients()) {
            if (!clientAffected(client, contest)) {
                continue;
            }
            String key = clientDomainKey(client.id(), domain);
            double old = clientFundingMultiplierByClientDomain.getOrDefault(key, 1.0);
            double captureReturn = outcome.captured() ? contest.privateGain() - (0.42 * client.publicHarmExternality()) : -0.05 * contest.privateGain();
            double reformReturn = contest.antiCaptureReform()
                    ? (outcome.antiCaptureReformEnacted() ? -0.18 : 0.16) * client.riskTolerance()
                    : 0.0;
            double sanctionDrag = outcome.sanctioned()
                    ? (0.20 + (0.20 * outcome.sanctionCost())) * (0.35 + client.reputationalRisk())
                    : 0.0;
            double delta = (0.08 * captureReturn) + reformReturn - sanctionDrag;
            double updated = Values.clamp(old + delta, 0.55, 1.75);
            clientFundingMultiplierByClientDomain.put(key, updated);
            movement += Math.abs(updated - old);
            changed++;
        }
        return changed == 0 ? 0.0 : Values.clamp(movement / changed, 0.0, 1.0);
    }

    private double adaptRegulators(PolicyContest contest, ContestOutcome outcome) {
        double old = regulatorAttention(contest.issueDomain());
        double oldQueue = regulatorQueue(contest.issueDomain());
        double capacity = regulatorProcessingCapacity(contest.issueDomain());
        double commentVolumePressure = Values.clamp(contest.docket().totalComments() / 4_000.0, 0.0, 1.0);
        double workload = (0.24 * commentVolumePressure)
                + (0.26 * contest.docket().templateSaturation())
                + (0.20 * contest.commentRecordDistortion())
                + (0.12 * contest.technicalComplexity());
        double updatedQueue = Values.clamp(oldQueue + workload - (capacity * 0.20), 0.0, 1.0);
        regulatorQueueByDomain.put(contest.issueDomain(), updatedQueue);
        double docketAlarm = (0.22 * contest.commentRecordDistortion()) + (0.10 * contest.docket().templateSaturation());
        double captureAlarm = outcome.captured() ? 0.16 : 0.0;
        double sanctionLearning = outcome.detected() ? 0.06 : 0.0;
        double quietDecay = outcome.captured() || contest.commentRecordDistortion() > 0.08 ? 0.0 : 0.025;
        double queueConstraint = 1.0 - (0.35 * updatedQueue);
        double updated = Values.clamp(old + ((docketAlarm + captureAlarm + sanctionLearning) * queueConstraint) - quietDecay, 0.0, 1.0);
        regulatorAttentionByDomain.put(
                contest.issueDomain(),
                updated
        );
        return Values.clamp((Math.abs(updated - old) + Math.abs(updatedQueue - oldQueue)) / 2.0, 0.0, 1.0);
    }

    private double adaptWatchdogs(PolicyContest contest, ContestOutcome outcome) {
        double old = watchdogFocus(contest.issueDomain());
        double opacityAlarm = (0.18 * contest.darkMoneyInfluence()) + (0.12 * contest.informationDistortion())
                + (0.10 * contest.commentRecordDistortion()) + (outcome.captured() ? 0.14 : 0.0);
        double referralLearning = outcome.detected() ? 0.05 : 0.0;
        double decay = opacityAlarm < 0.04 ? 0.02 : 0.0;
        watchdogFocusByDomain.put(
                contest.issueDomain(),
                Values.clamp(old + opacityAlarm + referralLearning - decay, 0.0, 1.0)
        );
        normalizeWatchdogBudgets();
        return Values.clamp(Math.abs(watchdogFocus(contest.issueDomain()) - old), 0.0, 1.0);
    }

    private static boolean clientAffected(InterestClient client, PolicyContest contest) {
        return client.sector().equals(contest.issueDomain())
                || client.privateGainByPolicy().containsKey(contest.issueDomain())
                || (contest.antiCaptureReform() && client.privateGainByPolicy().containsKey("democracy"));
    }

    private static boolean clientAffectedByDomain(InterestClient client, String domain) {
        return client.sector().equals(domain)
                || client.privateGainByPolicy().containsKey(domain)
                || domain.equals("democracy");
    }

    private Set<String> modelDomains() {
        Set<String> domains = new HashSet<>();
        for (PolicyContest contest : spec.contestTemplates()) {
            domains.add(contest.issueDomain());
        }
        for (InterestClient client : spec.clients()) {
            domains.add(client.sector());
            domains.addAll(client.privateGainByPolicy().keySet());
        }
        for (Regulator regulator : spec.regulators()) {
            domains.add(regulator.domain());
        }
        domains.add("democracy");
        return domains;
    }

    private void normalizeWatchdogBudgets() {
        double total = watchdogFocusByDomain.values().stream().mapToDouble(Double::doubleValue).sum();
        if (total <= 0.0) {
            return;
        }
        double scale = watchdogBudgetTotal / total;
        for (Map.Entry<String, Double> entry : watchdogFocusByDomain.entrySet()) {
            entry.setValue(Values.clamp(entry.getValue() * scale, 0.0, 1.0));
        }
    }

    private double reformDecayPressure(ContestOutcome outcome) {
        if (!outcome.contest().antiCaptureReform()) {
            return 0.0;
        }
        double totalSpend = outcome.influenceResult().totalSpend();
        double defensiveShare = totalSpend == 0.0 ? 0.0 : outcome.influenceResult().defensiveSpend() / totalSpend;
        double evasion = outcome.influenceResult().evasionShifts() > 0 ? 1.0 : 0.0;
        double litigation = outcome.contest().litigationThreat();
        double reformBlocked = outcome.antiCaptureReformEnacted() ? 0.0 : 1.0;
        return Values.clamp((0.42 * defensiveShare) + (0.22 * evasion) + (0.18 * litigation) + (0.18 * reformBlocked), 0.0, 1.0);
    }

    private static String clientDomainKey(String clientId, String issueDomain) {
        return clientId + "::" + issueDomain;
    }

    private static double average(Map<String, Double> values, double fallback) {
        if (values.isEmpty()) {
            return fallback;
        }
        return values.values().stream().mapToDouble(Double::doubleValue).average().orElse(fallback);
    }

    private static final class MetricAverage {
        private MetricAverage() {
        }

        private static double of(double first, double second, double third) {
            return Values.clamp((first + second + third) / 3.0, 0.0, 1.0);
        }
    }
}
