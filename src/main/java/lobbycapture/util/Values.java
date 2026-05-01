package lobbycapture.util;

public final class Values {
    private Values() {
    }

    public static double clamp(double value, double min, double max) {
        if (Double.isNaN(value)) {
            throw new IllegalArgumentException("value must not be NaN.");
        }
        return Math.max(min, Math.min(max, value));
    }

    public static void requireRange(String name, double value, double min, double max) {
        if (Double.isNaN(value) || value < min || value > max) {
            throw new IllegalArgumentException(name + " must be between " + min + " and " + max + ".");
        }
    }

    public static double safeDivide(double numerator, double denominator) {
        return denominator == 0.0 ? 0.0 : numerator / denominator;
    }
}

