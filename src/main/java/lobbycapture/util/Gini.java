package lobbycapture.util;

import java.util.Collection;

public final class Gini {
    private Gini() {
    }

    public static double of(Collection<Double> values) {
        if (values.isEmpty()) {
            return 0.0;
        }
        double[] sorted = values.stream().mapToDouble(Double::doubleValue).sorted().toArray();
        double sum = 0.0;
        for (double value : sorted) {
            sum += value;
        }
        if (sum == 0.0) {
            return 0.0;
        }
        double weighted = 0.0;
        for (int index = 0; index < sorted.length; index++) {
            weighted += (index + 1) * sorted[index];
        }
        return Values.clamp(((2.0 * weighted) / (sorted.length * sum)) - ((double) (sorted.length + 1) / sorted.length), 0.0, 1.0);
    }
}

