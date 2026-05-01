package lobbycapture.strategy;

import lobbycapture.actor.LobbyOrganization;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.WorldState;
import lobbycapture.util.Values;

public final class InfluenceSubstitutionEngine {
    public SubstitutionProfile evaluate(
            LobbyOrganization group,
            PolicyContest contest,
            ReformRegime reform,
            WorldState world,
            InfluenceStrategy currentStrategy
    ) {
        if (contest.antiCaptureReform()) {
            return SubstitutionProfile.none(InfluenceStrategy.DEFENSIVE_REFORM);
        }
        double accessPressure = Values.clamp(
                (0.38 * reform.contactLogCoverage())
                        + (0.34 * reform.lobbyingBanStrength())
                        + (0.28 * reform.coolingOffStrength()),
                0.0,
                1.0
        );
        double campaignPressure = reform.campaignFinanceCounterweight();
        double opacityPressure = Values.clamp(
                (0.44 * reform.darkMoneyDisclosureStrength())
                        + (0.34 * reform.beneficialOwnerDisclosure())
                        + (0.22 * reform.realTimeDisclosure()),
                0.0,
                1.0
        );
        double commentPressure = Values.clamp(
                (0.48 * reform.antiAstroturfStrength())
                        + (0.24 * reform.blindReviewStrength())
                        + (0.16 * reform.publicAdvocateStrength())
                        + (0.12 * reform.enforcementStrength()),
                0.0,
                1.0
        );
        double legalVenuePressure = Values.clamp(
                (0.55 * contest.legalVulnerability())
                        + (0.30 * contest.delayValue())
                        + (0.15 * world.evasionProfile().litigationFundingShift()),
                0.0,
                1.0
        );
        double channelPressure = pressureFor(currentStrategy, contest, accessPressure, campaignPressure, opacityPressure, commentPressure, legalVenuePressure);
        double anonymityValue = Values.clamp(
                (0.45 * group.disclosureAvoidanceSkill())
                        + (0.35 * world.evasionProfile().opacity())
                        + (0.20 * world.evasionFreedom()),
                0.0,
                1.0
        );
        double messengerCredibility = Values.clamp(
                (0.30 * group.technicalExpertise())
                        + (0.25 * group.publicCampaignSkill())
                        + (0.20 * group.astroturfSkill())
                        + (0.15 * group.accessCapital())
                        + (0.10 * group.litigationThreatSkill()),
                0.0,
                1.0
        );
        double vendorOverlap = Values.clamp(
                (0.28 * group.revolvingDoorNetworkStrength())
                        + (0.24 * group.accessCapital())
                        + (0.20 * group.publicCampaignSkill())
                        + (0.16 * group.litigationThreatSkill())
                        + (0.12 * group.disclosureAvoidanceSkill()),
                0.0,
                1.0
        );
        double legalCost = Values.clamp(
                (0.38 * world.evasionProfile().legalRisk())
                        + (0.28 * reform.enforcementStrength())
                        + (0.20 * reform.sanctionSeverity())
                        + (0.14 * contest.legalVulnerability()),
                0.0,
                1.0
        );
        double disclosureCost = Values.clamp(
                (0.45 * reform.transparencyStrength())
                        + (0.30 * opacityPressure)
                        + (0.25 * reform.contactLogCoverage()),
                0.0,
                1.0
        );
        double setupTime = Values.clamp(0.36 - (0.18 * vendorOverlap) - (0.12 * group.accessCapital()), 0.0, 1.0);
        double switchScore = Values.clamp(
                (0.34 * channelPressure)
                        + (0.22 * anonymityValue)
                        + (0.18 * messengerCredibility)
                        + (0.16 * vendorOverlap)
                        + (0.10 * world.evasionFreedom())
                        - (0.18 * legalCost)
                        - (0.10 * setupTime),
                0.0,
                1.0
        );
        InfluenceStrategy selected = switchScore > 0.34
                ? nearestSubstitute(currentStrategy, contest, accessPressure, campaignPressure, opacityPressure, commentPressure, legalVenuePressure)
                : currentStrategy;
        double activated = Values.clamp(switchScore * (0.45 + (0.55 * world.evasionFreedom())), 0.0, 1.0);
        double hiddenShare = Values.clamp(
                activated * (0.24 + (0.46 * anonymityValue) + (0.20 * world.evasionProfile().opacity()))
                        - (0.18 * reform.transparencyStrength()),
                0.0,
                1.0
        );
        double preservation = Values.clamp(
                0.18
                        + (0.52 * activated)
                        + (0.20 * vendorOverlap)
                        + (0.16 * messengerCredibility)
                        - (0.18 * legalCost),
                0.0,
                1.0
        );
        double messenger = Values.clamp(
                activated * (0.34 + (0.34 * messengerCredibility) + (0.20 * anonymityValue)),
                0.0,
                1.0
        );
        double venue = Values.clamp(
                activated * (0.22 + (0.35 * legalVenuePressure) + (0.22 * accessPressure) + (0.14 * campaignPressure)),
                0.0,
                1.0
        );
        double transparencyGain = Values.clamp(
                (0.52 * reform.transparencyStrength())
                        + (0.20 * reform.enforcementStrength())
                        - (0.62 * hiddenShare)
                        - (0.16 * messenger),
                -1.0,
                1.0
        );
        return new SubstitutionProfile(
                selected,
                switchScore,
                channelPressure,
                activated,
                preservation,
                hiddenShare,
                transparencyGain,
                messenger,
                venue
        );
    }

    private static double pressureFor(
            InfluenceStrategy strategy,
            PolicyContest contest,
            double accessPressure,
            double campaignPressure,
            double opacityPressure,
            double commentPressure,
            double legalVenuePressure
    ) {
        return switch (strategy) {
            case DIRECT_ACCESS, AGENDA_ACCESS -> accessPressure;
            case CAMPAIGN_FINANCE -> campaignPressure;
            case DARK_MONEY -> opacityPressure;
            case REVOLVING_DOOR -> Math.max(accessPressure, contest.arena() == ContestArena.PROCUREMENT ? 0.62 : accessPressure);
            case INFORMATION_DISTORTION, PUBLIC_CAMPAIGN -> commentPressure;
            case LITIGATION_THREAT -> legalVenuePressure;
            case BALANCED -> Math.max(Math.max(accessPressure, campaignPressure), Math.max(opacityPressure, commentPressure)) * 0.72;
            case DEFENSIVE_REFORM -> 0.0;
        };
    }

    private static InfluenceStrategy nearestSubstitute(
            InfluenceStrategy current,
            PolicyContest contest,
            double accessPressure,
            double campaignPressure,
            double opacityPressure,
            double commentPressure,
            double legalVenuePressure
    ) {
        if (campaignPressure >= Math.max(accessPressure, commentPressure)) {
            return InfluenceStrategy.DARK_MONEY;
        }
        if (opacityPressure > 0.72 && current == InfluenceStrategy.DARK_MONEY) {
            return InfluenceStrategy.PUBLIC_CAMPAIGN;
        }
        if (commentPressure >= 0.55) {
            return contest.legalVulnerability() > 0.45 ? InfluenceStrategy.LITIGATION_THREAT : InfluenceStrategy.INFORMATION_DISTORTION;
        }
        if (accessPressure >= 0.50) {
            return legalVenuePressure > 0.50 ? InfluenceStrategy.LITIGATION_THREAT : InfluenceStrategy.PUBLIC_CAMPAIGN;
        }
        if (contest.arena() == ContestArena.PROCUREMENT) {
            return InfluenceStrategy.REVOLVING_DOOR;
        }
        return current == InfluenceStrategy.DARK_MONEY ? InfluenceStrategy.PUBLIC_CAMPAIGN : InfluenceStrategy.DARK_MONEY;
    }
}
