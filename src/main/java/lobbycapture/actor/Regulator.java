package lobbycapture.actor;

import lobbycapture.util.Values;

public record Regulator(
        String id,
        String domain,
        double statutoryMandateStrength,
        double independence,
        double staffCapacity,
        double industryExpertiseDependence,
        double enforcementBudget,
        double commentProcessingCapacity,
        double captureVulnerability,
        double revolvingDoorFlow,
        double judicialReviewRisk
) {
    public Regulator {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        if (domain == null || domain.isBlank()) {
            throw new IllegalArgumentException("domain must not be blank.");
        }
        Values.requireRange("statutoryMandateStrength", statutoryMandateStrength, 0.0, 1.0);
        Values.requireRange("independence", independence, 0.0, 1.0);
        Values.requireRange("staffCapacity", staffCapacity, 0.0, 1.0);
        Values.requireRange("industryExpertiseDependence", industryExpertiseDependence, 0.0, 1.0);
        Values.requireRange("enforcementBudget", enforcementBudget, 0.0, 1.0);
        Values.requireRange("commentProcessingCapacity", commentProcessingCapacity, 0.0, 1.0);
        Values.requireRange("captureVulnerability", captureVulnerability, 0.0, 1.0);
        Values.requireRange("revolvingDoorFlow", revolvingDoorFlow, 0.0, 1.0);
        Values.requireRange("judicialReviewRisk", judicialReviewRisk, 0.0, 1.0);
    }
}

