package lobbycapture.simulation;

import java.util.Random;

public final class RandomSource {
    private final Random random;

    public RandomSource(long seed) {
        this.random = new Random(seed);
    }

    public Random random() {
        return random;
    }
}

