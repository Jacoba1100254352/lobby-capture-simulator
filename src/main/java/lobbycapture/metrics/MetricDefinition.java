package lobbycapture.metrics;

import lobbycapture.util.Values;

public record MetricDefinition(String key, String label, MetricDirection direction, String note) {
    public enum MetricDirection {
        HIGHER_IS_BETTER,
        LOWER_IS_BETTER,
        DIAGNOSTIC
    }

    public static double higherIsBetter(double value) {
        return Values.clamp(value, 0.0, 1.0);
    }

    public static double lowerIsBetter(double value) {
        return 1.0 - Values.clamp(value, 0.0, 1.0);
    }

    public static double average(double... values) {
        if (values.length == 0) {
            return 0.0;
        }
        double sum = 0.0;
        for (double value : values) {
            sum += Values.clamp(value, 0.0, 1.0);
        }
        return sum / values.length;
    }
}

