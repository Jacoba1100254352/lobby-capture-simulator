package lobbycapture.simulation;

import lobbycapture.actor.Candidate;
import lobbycapture.actor.EnforcementAgency;
import lobbycapture.actor.InterestClient;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.actor.PublicOfficial;
import lobbycapture.actor.Regulator;
import lobbycapture.calibration.CalibrationProfile;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.strategy.EvasionProfile;
import lobbycapture.util.Values;

import java.util.List;

public record WorldSpec(
        String name,
        ReformRegime reformRegime,
        CalibrationProfile calibrationProfile,
        EvasionProfile evasionProfile,
        List<LobbyOrganization> lobbyOrganizations,
        List<InterestClient> clients,
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
        if (calibrationProfile == null) {
            throw new IllegalArgumentException("calibrationProfile must not be null.");
        }
        if (evasionProfile == null) {
            throw new IllegalArgumentException("evasionProfile must not be null.");
        }
        lobbyOrganizations = List.copyOf(lobbyOrganizations);
        clients = List.copyOf(clients);
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
