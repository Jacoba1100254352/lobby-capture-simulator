package lobbycapture.reform;

import lobbycapture.policy.PolicyContest;
import lobbycapture.util.Values;

public final class TransparencySystem {
    private final ReformRegime regime;

    public TransparencySystem(ReformRegime regime) {
        this.regime = regime;
    }

    public PolicyContest applyBacklash(PolicyContest contest) {
        double captureBacklash = regime.transparencyStrength() * contest.captureRisk() * Math.max(0.0, contest.lobbyPressure());
        double support = contest.antiCaptureReform()
                ? contest.perceivedPublicSupport() + captureBacklash * 0.24
                : contest.perceivedPublicSupport() - captureBacklash * 0.18;
        return contest.withInfluence(
                contest.lobbyPressure() * (1.0 - (0.28 * regime.transparencyStrength())),
                Values.clamp(support, 0.0, 1.0),
                contest.truePublicBenefit(),
                contest.privateGain(),
                contest.publicAdvocatePressure(),
                contest.watchdogPressure(),
                contest.informationDistortion(),
                contest.commentRecordDistortion(),
                contest.darkMoneyInfluence() * (1.0 - (0.30 * regime.darkMoneyDisclosureStrength())),
                contest.revolvingDoorInfluence(),
                contest.campaignFinanceInfluence(),
                contest.litigationThreat()
        );
    }
}

