package lobbycapture.calibration;

public record CalibrationBenchmark(
        String key,
        String source,
        String observable,
        String metric,
        double min,
        double max,
        String notes
) {
}

