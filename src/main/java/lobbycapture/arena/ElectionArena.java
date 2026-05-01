package lobbycapture.arena;

import lobbycapture.policy.ContestArena;

public final class ElectionArena extends AbstractInfluenceArena {
    public ElectionArena() {
        super(ContestArena.ELECTION, 0.14, 0.08, 0.34, 0.08, 0.04, 0.82);
    }
}

