package lobbycapture.simulation;

public final class SimulationClock {
    private int tick;

    public int tick() {
        return tick;
    }

    public void advance() {
        tick++;
    }
}

