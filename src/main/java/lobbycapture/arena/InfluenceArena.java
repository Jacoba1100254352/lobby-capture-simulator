package lobbycapture.arena;

import lobbycapture.policy.ContestArena;
import lobbycapture.simulation.WorldState;
import lobbycapture.strategy.InfluenceResult;

public interface InfluenceArena {
    ContestArena arenaType();

    ContestOutcome resolve(InfluenceResult influence, WorldState world);
}

