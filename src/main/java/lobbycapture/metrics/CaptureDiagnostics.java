package lobbycapture.metrics;

public record CaptureDiagnostics(
        double capturePressure,
        double reformControl,
        double publicBacklash,
        double enforcementRisk
) {
}

