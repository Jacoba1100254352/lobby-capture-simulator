package lobbycapture.calibration;

public record CalibrationTarget(
        String key,
        String source,
        String dataNeeded,
        String modelSurface,
        String use
) {
}

