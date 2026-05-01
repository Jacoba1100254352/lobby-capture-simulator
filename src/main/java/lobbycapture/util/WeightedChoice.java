package lobbycapture.util;

import java.util.List;
import java.util.Random;
import java.util.function.ToDoubleFunction;

public final class WeightedChoice {
    private WeightedChoice() {
    }

    public static <T> T choose(List<T> values, ToDoubleFunction<T> weight, Random random) {
        if (values.isEmpty()) {
            throw new IllegalArgumentException("values must not be empty.");
        }
        double total = 0.0;
        for (T value : values) {
            total += Math.max(0.0, weight.applyAsDouble(value));
        }
        if (total == 0.0) {
            return values.get(random.nextInt(values.size()));
        }
        double cursor = random.nextDouble() * total;
        for (T value : values) {
            cursor -= Math.max(0.0, weight.applyAsDouble(value));
            if (cursor <= 0.0) {
                return value;
            }
        }
        return values.get(values.size() - 1);
    }
}

