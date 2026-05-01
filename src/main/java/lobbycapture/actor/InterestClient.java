package lobbycapture.actor;

import lobbycapture.util.Values;

import java.util.Map;

public record InterestClient(
        String id,
        String sector,
        Map<String, Double> privateGainByPolicy,
        double regulatoryExposure,
        double procurementExposure,
        double enforcementExposure,
        double publicHarmExternality,
        double riskTolerance,
        double needForSecrecy,
        double reputationalRisk
) {
    public InterestClient {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        if (sector == null || sector.isBlank()) {
            throw new IllegalArgumentException("sector must not be blank.");
        }
        privateGainByPolicy = privateGainByPolicy == null ? Map.of() : Map.copyOf(privateGainByPolicy);
        Values.requireRange("regulatoryExposure", regulatoryExposure, 0.0, 1.0);
        Values.requireRange("procurementExposure", procurementExposure, 0.0, 1.0);
        Values.requireRange("enforcementExposure", enforcementExposure, 0.0, 1.0);
        Values.requireRange("publicHarmExternality", publicHarmExternality, 0.0, 1.0);
        Values.requireRange("riskTolerance", riskTolerance, 0.0, 1.0);
        Values.requireRange("needForSecrecy", needForSecrecy, 0.0, 1.0);
        Values.requireRange("reputationalRisk", reputationalRisk, 0.0, 1.0);
    }
}

