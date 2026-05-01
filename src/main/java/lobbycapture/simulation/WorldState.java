package lobbycapture.simulation;

import lobbycapture.actor.Candidate;
import lobbycapture.actor.EnforcementAgency;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.actor.PublicOfficial;
import lobbycapture.actor.Regulator;
import lobbycapture.reform.ReformRegime;
import lobbycapture.strategy.InfluenceStrategy;
import lobbycapture.strategy.StrategyMemory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public final class WorldState {
    private final WorldSpec spec;
    private final Random random;
    private final SimulationClock clock = new SimulationClock();
    private final Map<String, Double> remainingBudgetByLobby = new HashMap<>();
    private final Map<String, StrategyMemory> memoryByLobby = new HashMap<>();

    public WorldState(WorldSpec spec, long seed) {
        this.spec = spec;
        this.random = new Random(seed);
        for (LobbyOrganization organization : spec.lobbyOrganizations()) {
            remainingBudgetByLobby.put(organization.id(), organization.totalBudget());
            memoryByLobby.put(organization.id(), new StrategyMemory(organization.initialStrategy()));
        }
    }

    public ReformRegime reformRegime() {
        return spec.reformRegime();
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

    public List<PublicOfficial> officials() {
        return spec.officials();
    }

    public List<Regulator> regulators() {
        return spec.regulators();
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
}
