package lobbycapture.actor;

import lobbycapture.util.Values;

public record EnforcementAgency(
        String id,
        String jurisdiction,
        double independence,
        double budget,
        double staffCapacity,
        double auditProbability,
        double riskBasedAuditWeight,
        double detectionCapability,
        double sanctionSeverity,
        double politicalInterferenceRisk,
        double captureSusceptibility
) {
    public EnforcementAgency {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        Values.requireRange("independence", independence, 0.0, 1.0);
        Values.requireRange("budget", budget, 0.0, 1.0);
        Values.requireRange("staffCapacity", staffCapacity, 0.0, 1.0);
        Values.requireRange("auditProbability", auditProbability, 0.0, 1.0);
        Values.requireRange("riskBasedAuditWeight", riskBasedAuditWeight, 0.0, 1.0);
        Values.requireRange("detectionCapability", detectionCapability, 0.0, 1.0);
        Values.requireRange("sanctionSeverity", sanctionSeverity, 0.0, 1.0);
        Values.requireRange("politicalInterferenceRisk", politicalInterferenceRisk, 0.0, 1.0);
        Values.requireRange("captureSusceptibility", captureSusceptibility, 0.0, 1.0);
    }
}

