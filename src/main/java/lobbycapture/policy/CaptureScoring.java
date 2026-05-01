package lobbycapture.policy;

import lobbycapture.util.Values;

public final class CaptureScoring {
    private CaptureScoring() {
    }

    public static double captureRisk(PolicyContest contest) {
        if (contest.antiCaptureReform()) {
            return 0.0;
        }
        double positivePressure = Math.max(0.0, contest.lobbyPressure());
        double weakPublicValue = 1.0 - publicInterestScore(contest);
        double opaqueInfluence = (0.50 * contest.darkMoneyInfluence()) + (0.30 * contest.revolvingDoorInfluence())
                + (0.20 * contest.campaignFinanceInfluence());
        return Values.clamp(
                (0.32 * positivePressure)
                        + (0.25 * contest.privateGain())
                        + (0.20 * weakPublicValue)
                        + (0.15 * contest.informationDistortion())
                        + (0.08 * opaqueInfluence),
                0.0,
                1.0
        );
    }

    public static double publicInterestScore(PolicyContest contest) {
        return Values.clamp(
                (0.52 * contest.truePublicBenefit())
                        + (0.28 * contest.perceivedPublicSupport())
                        + (0.12 * (1.0 - contest.concentratedHarm()))
                        + (0.08 * contest.publicAdvocatePressure()),
                0.0,
                1.0
        );
    }

    public static double privateGainRatio(PolicyContest contest) {
        return Values.clamp(contest.privateGain() / Math.max(0.15, contest.truePublicBenefit()), 0.0, 5.0);
    }
}

