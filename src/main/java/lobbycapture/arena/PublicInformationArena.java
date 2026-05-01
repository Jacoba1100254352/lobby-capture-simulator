package lobbycapture.arena;

import lobbycapture.policy.ContestArena;

public final class PublicInformationArena extends AbstractInfluenceArena {
    public PublicInformationArena() {
        super(ContestArena.PUBLIC_INFORMATION, 0.10, 0.28, 0.16, 0.06, 0.04, 0.90);
    }
}

