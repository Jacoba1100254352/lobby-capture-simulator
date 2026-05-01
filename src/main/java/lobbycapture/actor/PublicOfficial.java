package lobbycapture.actor;

import lobbycapture.util.Values;

public record PublicOfficial(
        String id,
        String role,
        String institution,
        double ideology,
        double donorDependence,
        double technicalInformationNeed,
        double staffCapacity,
        double postGovernmentSalaryAttraction,
        double ethicsResistance,
        double publicInterestCommitment,
        double captureSusceptibility,
        double watchdogRiskSensitivity
) {
    public PublicOfficial {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        Values.requireRange("ideology", ideology, -1.0, 1.0);
        Values.requireRange("donorDependence", donorDependence, 0.0, 1.0);
        Values.requireRange("technicalInformationNeed", technicalInformationNeed, 0.0, 1.0);
        Values.requireRange("staffCapacity", staffCapacity, 0.0, 1.0);
        Values.requireRange("postGovernmentSalaryAttraction", postGovernmentSalaryAttraction, 0.0, 1.0);
        Values.requireRange("ethicsResistance", ethicsResistance, 0.0, 1.0);
        Values.requireRange("publicInterestCommitment", publicInterestCommitment, 0.0, 1.0);
        Values.requireRange("captureSusceptibility", captureSusceptibility, 0.0, 1.0);
        Values.requireRange("watchdogRiskSensitivity", watchdogRiskSensitivity, 0.0, 1.0);
    }
}

