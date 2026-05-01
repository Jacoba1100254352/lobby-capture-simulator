package lobbycapture.arena;

import lobbycapture.policy.ContestArena;

public final class EnforcementArena extends AbstractInfluenceArena {
    public EnforcementArena() {
        super(ContestArena.ENFORCEMENT, 0.20, 0.14, 0.05, 0.28, 0.16, 0.34);
    }
}

