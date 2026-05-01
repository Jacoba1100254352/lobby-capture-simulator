package lobbycapture.arena;

import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.strategy.InfluenceResult;

public record ContestOutcome(
        PolicyContest contest,
        ContestArena arena,
        InfluenceResult influenceResult,
        boolean captured,
        boolean antiCaptureReformEnacted,
        boolean detected,
        boolean sanctioned,
        boolean delayedByChallenge,
        double captureIndex,
        double publicInterestScore,
        double policyDistortion,
        double regulatoryDrift,
        double enforcementForbearance,
        double procurementBias,
        double detectionProbability,
        double sanctionCost,
        double evasionPenalty,
        double administrativeCost,
        String reason
) {
}
