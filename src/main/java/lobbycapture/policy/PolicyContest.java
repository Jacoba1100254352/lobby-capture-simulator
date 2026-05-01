package lobbycapture.policy;

import lobbycapture.util.Values;

public record PolicyContest(
        String id,
        String title,
        String issueDomain,
        ContestArena arena,
        boolean antiCaptureReform,
        double truePublicBenefit,
        double perceivedPublicSupport,
        double truePublicSupport,
        double publicSignalUncertainty,
        double privateGain,
        double concentratedHarm,
        double technicalComplexity,
        double salience,
        double legalVulnerability,
        double delayValue,
        double implementationCost,
        double lobbyPressure,
        double publicAdvocatePressure,
        double watchdogPressure,
        double informationDistortion,
        double commentRecordDistortion,
        double darkMoneyInfluence,
        double revolvingDoorInfluence,
        double campaignFinanceInfluence,
        double litigationThreat,
        double captureRisk,
        double publicInterestScore
) {
    public PolicyContest {
        requireText("id", id);
        requireText("title", title);
        requireText("issueDomain", issueDomain);
        if (arena == null) {
            throw new IllegalArgumentException("arena must not be null.");
        }
        Values.requireRange("truePublicBenefit", truePublicBenefit, 0.0, 1.0);
        Values.requireRange("perceivedPublicSupport", perceivedPublicSupport, 0.0, 1.0);
        Values.requireRange("truePublicSupport", truePublicSupport, 0.0, 1.0);
        Values.requireRange("publicSignalUncertainty", publicSignalUncertainty, 0.0, 1.0);
        Values.requireRange("privateGain", privateGain, 0.0, 1.0);
        Values.requireRange("concentratedHarm", concentratedHarm, 0.0, 1.0);
        Values.requireRange("technicalComplexity", technicalComplexity, 0.0, 1.0);
        Values.requireRange("salience", salience, 0.0, 1.0);
        Values.requireRange("legalVulnerability", legalVulnerability, 0.0, 1.0);
        Values.requireRange("delayValue", delayValue, 0.0, 1.0);
        Values.requireRange("implementationCost", implementationCost, 0.0, 1.0);
        Values.requireRange("lobbyPressure", lobbyPressure, -1.0, 1.0);
        Values.requireRange("publicAdvocatePressure", publicAdvocatePressure, 0.0, 1.0);
        Values.requireRange("watchdogPressure", watchdogPressure, 0.0, 1.0);
        Values.requireRange("informationDistortion", informationDistortion, 0.0, 1.0);
        Values.requireRange("commentRecordDistortion", commentRecordDistortion, 0.0, 1.0);
        Values.requireRange("darkMoneyInfluence", darkMoneyInfluence, 0.0, 1.0);
        Values.requireRange("revolvingDoorInfluence", revolvingDoorInfluence, 0.0, 1.0);
        Values.requireRange("campaignFinanceInfluence", campaignFinanceInfluence, 0.0, 1.0);
        Values.requireRange("litigationThreat", litigationThreat, 0.0, 1.0);
        captureRisk = Values.clamp(captureRisk, 0.0, 1.0);
        publicInterestScore = Values.clamp(publicInterestScore, 0.0, 1.0);
    }

    public static PolicyContest of(
            String id,
            String title,
            String issueDomain,
            ContestArena arena,
            boolean antiCaptureReform,
            double truePublicBenefit,
            double perceivedPublicSupport,
            double truePublicSupport,
            double privateGain,
            double concentratedHarm,
            double technicalComplexity,
            double salience
    ) {
        PolicyContest contest = new PolicyContest(
                id,
                title,
                issueDomain,
                arena,
                antiCaptureReform,
                truePublicBenefit,
                perceivedPublicSupport,
                truePublicSupport,
                0.20,
                privateGain,
                concentratedHarm,
                technicalComplexity,
                salience,
                0.25,
                0.20,
                0.20,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
        );
        return contest.rescored();
    }

    public PolicyContest withInfluence(
            double lobbyPressure,
            double perceivedPublicSupport,
            double truePublicBenefit,
            double privateGain,
            double publicAdvocatePressure,
            double watchdogPressure,
            double informationDistortion,
            double commentRecordDistortion,
            double darkMoneyInfluence,
            double revolvingDoorInfluence,
            double campaignFinanceInfluence,
            double litigationThreat
    ) {
        return new PolicyContest(
                id,
                title,
                issueDomain,
                arena,
                antiCaptureReform,
                Values.clamp(truePublicBenefit, 0.0, 1.0),
                Values.clamp(perceivedPublicSupport, 0.0, 1.0),
                truePublicSupport,
                publicSignalUncertainty,
                Values.clamp(privateGain, 0.0, 1.0),
                concentratedHarm,
                technicalComplexity,
                salience,
                legalVulnerability,
                delayValue,
                implementationCost,
                Values.clamp(lobbyPressure, -1.0, 1.0),
                Values.clamp(publicAdvocatePressure, 0.0, 1.0),
                Values.clamp(watchdogPressure, 0.0, 1.0),
                Values.clamp(informationDistortion, 0.0, 1.0),
                Values.clamp(commentRecordDistortion, 0.0, 1.0),
                Values.clamp(darkMoneyInfluence, 0.0, 1.0),
                Values.clamp(revolvingDoorInfluence, 0.0, 1.0),
                Values.clamp(campaignFinanceInfluence, 0.0, 1.0),
                Values.clamp(litigationThreat, 0.0, 1.0),
                0.0,
                0.0
        ).rescored();
    }

    public PolicyContest withId(String newId) {
        return new PolicyContest(
                newId,
                title,
                issueDomain,
                arena,
                antiCaptureReform,
                truePublicBenefit,
                perceivedPublicSupport,
                truePublicSupport,
                publicSignalUncertainty,
                privateGain,
                concentratedHarm,
                technicalComplexity,
                salience,
                legalVulnerability,
                delayValue,
                implementationCost,
                lobbyPressure,
                publicAdvocatePressure,
                watchdogPressure,
                informationDistortion,
                commentRecordDistortion,
                darkMoneyInfluence,
                revolvingDoorInfluence,
                campaignFinanceInfluence,
                litigationThreat,
                captureRisk,
                publicInterestScore
        );
    }

    public double publicPreferenceDistortion() {
        return Math.abs(truePublicSupport - perceivedPublicSupport);
    }

    private PolicyContest rescored() {
        double capture = CaptureScoring.captureRisk(this);
        double publicInterest = CaptureScoring.publicInterestScore(this);
        return new PolicyContest(
                id,
                title,
                issueDomain,
                arena,
                antiCaptureReform,
                truePublicBenefit,
                perceivedPublicSupport,
                truePublicSupport,
                publicSignalUncertainty,
                privateGain,
                concentratedHarm,
                technicalComplexity,
                salience,
                legalVulnerability,
                delayValue,
                implementationCost,
                lobbyPressure,
                publicAdvocatePressure,
                watchdogPressure,
                informationDistortion,
                commentRecordDistortion,
                darkMoneyInfluence,
                revolvingDoorInfluence,
                campaignFinanceInfluence,
                litigationThreat,
                capture,
                publicInterest
        );
    }

    private static void requireText(String name, String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank.");
        }
    }
}

