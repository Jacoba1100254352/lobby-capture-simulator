package lobbycapture.simulation;

import lobbycapture.actor.Candidate;
import lobbycapture.actor.EnforcementAgency;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.actor.PublicOfficial;
import lobbycapture.actor.Regulator;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.util.Values;

import java.util.List;

public record WorldSpec(
        String name,
        ReformRegime reformRegime,
        List<LobbyOrganization> lobbyOrganizations,
        List<PublicOfficial> officials,
        List<Regulator> regulators,
        List<Candidate> candidates,
        List<EnforcementAgency> enforcementAgencies,
        List<PolicyContest> contestTemplates,
        double spendScale,
        double pressurePerSpend,
        double publicCampaignEffect,
        double evasionFreedom,
        boolean adaptiveStrategies
) {
    public WorldSpec {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank.");
        }
        if (reformRegime == null) {
            throw new IllegalArgumentException("reformRegime must not be null.");
        }
        lobbyOrganizations = List.copyOf(lobbyOrganizations);
        officials = List.copyOf(officials);
        regulators = List.copyOf(regulators);
        candidates = List.copyOf(candidates);
        enforcementAgencies = List.copyOf(enforcementAgencies);
        contestTemplates = List.copyOf(contestTemplates);
        Values.requireRange("spendScale", spendScale, 0.0, 10.0);
        Values.requireRange("pressurePerSpend", pressurePerSpend, 0.0, 1.0);
        Values.requireRange("publicCampaignEffect", publicCampaignEffect, 0.0, 1.0);
        Values.requireRange("evasionFreedom", evasionFreedom, 0.0, 1.0);
    }
}

