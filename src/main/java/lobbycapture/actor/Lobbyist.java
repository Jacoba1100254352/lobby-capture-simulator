package lobbycapture.actor;

import lobbycapture.util.Values;

public record Lobbyist(
        String id,
        String employerId,
        double issueExpertise,
        double legalExpertise,
        boolean priorPublicRole,
        int coolingOffRemaining,
        double personalAccessNetwork,
        double complianceRisk,
        double expectedRevolvingDoorValue
) {
    public Lobbyist {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        if (employerId == null || employerId.isBlank()) {
            throw new IllegalArgumentException("employerId must not be blank.");
        }
        Values.requireRange("issueExpertise", issueExpertise, 0.0, 1.0);
        Values.requireRange("legalExpertise", legalExpertise, 0.0, 1.0);
        if (coolingOffRemaining < 0) {
            throw new IllegalArgumentException("coolingOffRemaining must not be negative.");
        }
        Values.requireRange("personalAccessNetwork", personalAccessNetwork, 0.0, 1.0);
        Values.requireRange("complianceRisk", complianceRisk, 0.0, 1.0);
        Values.requireRange("expectedRevolvingDoorValue", expectedRevolvingDoorValue, 0.0, 1.0);
    }
}

