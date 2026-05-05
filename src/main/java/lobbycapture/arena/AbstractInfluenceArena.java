package lobbycapture.arena;

import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.WorldState;
import lobbycapture.strategy.InfluenceResult;
import lobbycapture.util.Values;

abstract class AbstractInfluenceArena implements InfluenceArena {
    private final ContestArena arenaType;
    private final double captureSusceptibility;
    private final double informationWeight;
    private final double campaignFinanceWeight;
    private final double revolvingDoorWeight;
    private final double litigationWeight;
    private final double publicVisibility;

    AbstractInfluenceArena(
            ContestArena arenaType,
            double captureSusceptibility,
            double informationWeight,
            double campaignFinanceWeight,
            double revolvingDoorWeight,
            double litigationWeight,
            double publicVisibility
    ) {
        this.arenaType = arenaType;
        this.captureSusceptibility = captureSusceptibility;
        this.informationWeight = informationWeight;
        this.campaignFinanceWeight = campaignFinanceWeight;
        this.revolvingDoorWeight = revolvingDoorWeight;
        this.litigationWeight = litigationWeight;
        this.publicVisibility = publicVisibility;
    }

    @Override
    public ContestArena arenaType() {
        return arenaType;
    }

    @Override
    public ContestOutcome resolve(InfluenceResult influence, WorldState world) {
        PolicyContest contest = influence.contest();
        ReformRegime reform = world.reformRegime();
        if (contest.antiCaptureReform()) {
            return resolveAntiCaptureReform(influence, world, reform);
        }
        return resolveCaptureContest(influence, world, reform);
    }

    private ContestOutcome resolveAntiCaptureReform(InfluenceResult influence, WorldState world, ReformRegime reform) {
        PolicyContest contest = influence.contest();
        double defensivePressure = Values.clamp(
                Math.max(0.0, -contest.lobbyPressure())
                        + (0.22 * contest.litigationThreat())
                        + (0.18 * contest.darkMoneyInfluence())
                        + (0.16 * contest.informationDistortion())
                        + (0.12 * contest.campaignFinanceInfluence()),
                0.0,
                1.0
        );
        double publicCase = (0.40 * contest.truePublicBenefit())
                + (0.30 * contest.perceivedPublicSupport())
                + (0.12 * contest.watchdogPressure())
                + (0.18 * reform.reformProtectionStrength());
        double opposition = (0.56 * defensivePressure)
                + (0.12 * contest.litigationThreat())
                + (0.08 * reform.constitutionalChallengeRisk());
        double score = publicCase - opposition + randomNoise(world, 0.05);
        boolean enacted = score >= 0.42;
        boolean delayed = !enacted && contest.litigationThreat() + reform.constitutionalChallengeRisk() > 0.62;
        double distortion = enacted ? Math.max(0.0, 1.0 - reform.reformProtectionStrength()) * 0.15 : 0.60 + (0.25 * defensivePressure);
        return new ContestOutcome(
                contest,
                arenaType,
                influence,
                false,
                enacted,
                false,
                false,
                delayed,
                0.0,
                contest.publicInterestScore(),
                Values.clamp(distortion, 0.0, 1.0),
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                reform.administrativeCost() + (delayed ? reform.constitutionalChallengeRisk() * 0.35 : 0.0),
                enacted ? "anti-capture reform survived defensive lobbying" : "defensive lobbying blocked reform"
        );
    }

    private ContestOutcome resolveCaptureContest(InfluenceResult influence, WorldState world, ReformRegime reform) {
        PolicyContest contest = influence.contest();
        double channelPressure = (informationWeight * contest.informationDistortion())
                + (campaignFinanceWeight * contest.campaignFinanceInfluence())
                + (revolvingDoorWeight * contest.revolvingDoorInfluence())
                + (litigationWeight * contest.litigationThreat());
        double hiddenSubstitutionPressure = Values.clamp(
                (0.16 * influence.hiddenInfluenceShare())
                        + (0.11 * influence.influencePreservationRate())
                        + (0.08 * influence.venueSubstitutionRate())
                        + (0.05 * influence.messengerSubstitutionRate()),
                0.0,
                1.0
        );
        double publicBacklash = publicVisibility * reform.transparencyStrength() * Math.max(0.0, contest.lobbyPressure());
        double reformControl = (0.24 * reform.transparencyStrength())
                + (0.22 * reform.enforcementStrength())
                + (0.18 * reform.publicAdvocateStrength())
                + (0.14 * reform.blindReviewStrength())
                + (0.10 * reform.campaignFinanceCounterweight())
                + (0.07 * reform.antiAstroturfStrength())
                + (0.05 * reform.coolingOffStrength())
                + (0.07 * world.regulatorAttention(contest.issueDomain()) * (1.0 - (0.30 * world.regulatorQueue(contest.issueDomain()))))
                + (0.05 * world.watchdogFocus(contest.issueDomain()));
        double controlLeakage = Values.clamp(
                1.0
                        - (0.22 * influence.hiddenInfluenceShare())
                        - (0.10 * influence.influencePreservationRate())
                        - (0.08 * influence.venueSubstitutionRate()),
                0.62,
                1.0
        );
        double capturePressure = contest.captureRisk()
                + captureSusceptibility
                + channelPressure
                + hiddenSubstitutionPressure
                + (0.10 * contest.technicalComplexity())
                - (0.35 * reformControl * controlLeakage)
                - (0.18 * publicBacklash)
                + randomNoise(world, 0.06);
        boolean capturedBeforeAudit = capturePressure >= 0.48;
        double detectionProbability = Values.clamp(
                0.025
                        + reform.auditRate()
                        + (0.34 * reform.enforcementStrength())
                        + (0.18 * reform.transparencyStrength())
                        + (0.14 * contest.watchdogPressure())
                        - (0.16 * contest.darkMoneyInfluence())
                        - (0.10 * influence.hiddenInfluenceShare())
                        + (0.10 * world.evasionProfile().legalRisk())
                        + (0.10 * world.watchdogFocus(contest.issueDomain()))
                        + (0.07 * world.regulatorAttention(contest.issueDomain()) * (1.0 - (0.35 * world.regulatorQueue(contest.issueDomain()))))
                        - (0.08 * reform.appealsDelay()),
                0.0,
                1.0
        );
        double processFlagProbability = detectionProbability * (capturedBeforeAudit ? 1.0 : 0.22);
        boolean detected = world.random().nextDouble() < processFlagProbability;
        double sanctionProbability = Values.clamp(
                (capturedBeforeAudit ? 1.0 : 0.18)
                        * (0.06 + (0.62 * reform.sanctionSeverity() * reform.enforcementStrength())),
                0.0,
                1.0
        );
        boolean sanctioned = detected && world.random().nextDouble() < sanctionProbability;
        boolean reversed = sanctioned && world.random().nextDouble() < Values.clamp(reform.sanctionSeverity() * 0.65, 0.0, 1.0);
        boolean captured = capturedBeforeAudit && !reversed;
        double regulatoryDrift = arenaType == ContestArena.RULEMAKING ? drift(contest, captured, 0.82) : drift(contest, captured, 0.18);
        double enforcementForbearance = arenaType == ContestArena.ENFORCEMENT ? drift(contest, captured, 0.95) : drift(contest, captured, 0.10);
        double procurementBias = arenaType == ContestArena.PROCUREMENT ? drift(contest, captured, 0.92) : drift(contest, captured, 0.08);
        double policyDistortion = Values.clamp(
                captured
                        ? (0.45 * contest.captureRisk()) + (0.30 * contest.privateGain()) + (0.25 * contest.publicPreferenceDistortion())
                        : contest.publicPreferenceDistortion() * 0.22,
                0.0,
                1.0
        );
        double evasionPenalty = sanctioned
                ? Values.clamp(world.evasionProfile().legalRisk() * contest.darkMoneyInfluence() * reform.sanctionSeverity(), 0.0, 1.0)
                : 0.0;
        return new ContestOutcome(
                contest,
                arenaType,
                influence,
                captured,
                false,
                detected,
                sanctioned,
                contest.litigationThreat() + reform.appealsDelay() > 1.05,
                contest.captureRisk(),
                contest.publicInterestScore(),
                policyDistortion,
                regulatoryDrift,
                enforcementForbearance,
                procurementBias,
                detectionProbability,
                sanctioned ? reform.sanctionSeverity() : 0.0,
                evasionPenalty,
                reform.administrativeCost() + (detected ? 0.08 : 0.0) + (sanctioned ? 0.06 : 0.0),
                captured ? "captured outcome survived process" : "public-interest controls held"
        );
    }

    private static double drift(PolicyContest contest, boolean captured, double weight) {
        if (!captured) {
            return contest.publicPreferenceDistortion() * 0.12 * weight;
        }
        return Values.clamp((0.55 * contest.privateGain()) + (0.45 * contest.captureRisk()), 0.0, 1.0) * weight;
    }

    private static double randomNoise(WorldState world, double range) {
        return (world.random().nextDouble() - 0.5) * 2.0 * range;
    }
}
