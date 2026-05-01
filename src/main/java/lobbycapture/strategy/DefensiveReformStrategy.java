package lobbycapture.strategy;

import lobbycapture.actor.LobbyOrganization;
import lobbycapture.policy.PolicyContest;
import lobbycapture.util.Values;

public final class DefensiveReformStrategy {
    private DefensiveReformStrategy() {
    }

    public static double spendIntent(LobbyOrganization group, PolicyContest contest) {
        double threat = (0.42 * contest.truePublicBenefit())
                + (0.34 * contest.perceivedPublicSupport())
                + (0.24 * contest.salience());
        return Values.clamp(group.defensiveMultiplier() * group.influenceIntensity() * group.reformThreatSensitivity() * threat, 0.0, 1.6);
    }
}

