package lobbycapture.strategy;


import lobbycapture.actor.LobbyOrganization;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.WorldState;
import lobbycapture.util.Values;


public final class InfluenceSubstitutionEngine
{
	private static double average(double... values) {
		if (values.length == 0) {
			return 0.0;
		}
		double sum = 0.0;
		for (double value : values) {
			sum += value;
		}
		return sum / values.length;
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
			case INTERMEDIARY -> Math.max(commentPressure, Math.max(accessPressure, opacityPressure)) * 0.88;
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
		if (current == InfluenceStrategy.INTERMEDIARY && opacityPressure > 0.70) {
			return legalVenuePressure > 0.45 ? InfluenceStrategy.LITIGATION_THREAT : InfluenceStrategy.PUBLIC_CAMPAIGN;
		}
		if (contest.arena() == ContestArena.PROCUREMENT && accessPressure >= 0.42) {
			return opacityPressure > 0.45 ? InfluenceStrategy.INTERMEDIARY : InfluenceStrategy.REVOLVING_DOOR;
		}
		if (commentPressure >= 0.50 && (accessPressure >= 0.35 || opacityPressure >= 0.35)) {
			return InfluenceStrategy.INTERMEDIARY;
		}
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
			return legalVenuePressure > 0.50 ? InfluenceStrategy.LITIGATION_THREAT : InfluenceStrategy.INTERMEDIARY;
		}
		if (contest.arena() == ContestArena.PROCUREMENT) {
			return InfluenceStrategy.REVOLVING_DOOR;
		}
		return current == InfluenceStrategy.DARK_MONEY ? InfluenceStrategy.PUBLIC_CAMPAIGN : InfluenceStrategy.DARK_MONEY;
	}
	
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
		double crossVenueDetection = reform.crossVenueDetectionStrength();
		double visibleRestriction = Values.clamp(
				(0.38 * reform.lobbyingBanStrength())
						+ (0.24 * reform.contactLogCoverage())
						+ (0.18 * (1.0 - reform.defensiveCapShare()))
						+ (0.12 * reform.coolingOffStrength())
						+ (0.08 * reform.contributionLimitStrength()),
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
		double procurementVenueValue = Values.clamp(
				((contest.arena() == ContestArena.PROCUREMENT || contest.issueDomain().equals("procurement")) ? 0.38 : 0.0)
						+ (0.24 * world.evasionProfile().procurementConsultantShift())
						+ (0.18 * group.preferenceFor("procurement"))
						+ (0.12 * group.revolvingDoorNetworkStrength())
						+ (0.08 * group.accessCapital()),
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
		double intermediaryFit = Values.clamp(
				(0.34 * group.technicalExpertise())
						+ (0.24 * group.publicCampaignSkill())
						+ (0.18 * group.disclosureAvoidanceSkill())
						+ (0.14 * group.accessCapital())
						+ (0.10 * contest.technicalComplexity()),
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
						+ (0.14 * contest.legalVulnerability())
						+ (0.12 * crossVenueDetection),
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
						+ (0.12 * vendorOverlap)
						+ (0.08 * intermediaryFit)
						+ (0.10 * world.evasionFreedom())
						+ (0.12 * visibleRestriction)
						+ (0.08 * procurementVenueValue)
						- (0.18 * legalCost)
						- (0.08 * disclosureCost)
						- (0.10 * crossVenueDetection)
						- (0.10 * setupTime),
				0.0,
				1.0
		);
		double equalWeightSwitchScore = Values.clamp(
				average(
						channelPressure,
						anonymityValue,
						messengerCredibility,
						vendorOverlap,
						intermediaryFit,
						world.evasionFreedom(),
						visibleRestriction,
						procurementVenueValue
				)
						- (0.55 * average(legalCost, disclosureCost, crossVenueDetection, setupTime)),
				0.0,
				1.0
		);
		double anonymityHeavySwitchScore = Values.clamp(
				(0.26 * channelPressure)
						+ (0.34 * anonymityValue)
						+ (0.18 * messengerCredibility)
						+ (0.12 * vendorOverlap)
						+ (0.08 * intermediaryFit)
						+ (0.14 * world.evasionFreedom())
						+ (0.10 * visibleRestriction)
						+ (0.06 * procurementVenueValue)
						- (0.14 * legalCost)
						- (0.12 * disclosureCost)
						- (0.10 * crossVenueDetection)
						- (0.08 * setupTime),
				0.0,
				1.0
		);
		double enforcementCostHeavySwitchScore = Values.clamp(
				(0.30 * channelPressure)
						+ (0.18 * anonymityValue)
						+ (0.16 * messengerCredibility)
						+ (0.12 * vendorOverlap)
						+ (0.06 * intermediaryFit)
						+ (0.08 * world.evasionFreedom())
						+ (0.10 * visibleRestriction)
						+ (0.06 * procurementVenueValue)
						- (0.26 * legalCost)
						- (0.14 * disclosureCost)
						- (0.16 * crossVenueDetection)
						- (0.12 * setupTime),
				0.0,
				1.0
		);
		InfluenceStrategy selected = switchScore > 0.31
				? nearestSubstitute(currentStrategy, contest, accessPressure, campaignPressure, opacityPressure, commentPressure, legalVenuePressure)
				: currentStrategy;
		double activated = Values.clamp(
				switchScore * (0.45 + (0.55 * world.evasionFreedom())) * (1.0 - (0.18 * crossVenueDetection)),
				0.0,
				1.0
		);
		double hiddenShare = Values.clamp(
				activated * (
						0.42
								+ (0.66 * anonymityValue)
								+ (0.32 * world.evasionProfile().opacity())
								+ (0.28 * world.evasionFreedom())
								+ (0.24 * intermediaryFit)
								+ (0.34 * visibleRestriction)
								+ (0.24 * procurementVenueValue)
								+ (0.18 * legalVenuePressure)
				)
						- (0.07 * Math.max(0.0, reform.transparencyStrength() - world.evasionFreedom()))
						- (0.12 * crossVenueDetection),
				0.0,
				1.0
		);
		double preservation = Values.clamp(
				0.18
						+ (0.52 * activated)
						+ (0.20 * vendorOverlap)
						+ (0.16 * messengerCredibility)
						- (0.18 * legalCost)
						- (0.10 * crossVenueDetection),
				0.0,
				1.0
		);
		double messenger = Values.clamp(
				activated * (0.34 + (0.34 * messengerCredibility) + (0.20 * anonymityValue)),
				0.0,
				1.0
		);
		double venue = Values.clamp(
				activated * (
						0.24
								+ (0.32 * legalVenuePressure)
								+ (0.24 * accessPressure)
								+ (0.18 * campaignPressure)
								+ (0.24 * procurementVenueValue)
								+ (0.18 * visibleRestriction)
								+ (0.15 * reform.coolingOffStrength())
				)
						- (0.16 * crossVenueDetection),
				0.0,
				1.0
		);
		double transparencyGain = Values.clamp(
				(0.52 * reform.transparencyStrength())
						+ (0.20 * reform.enforcementStrength())
						+ (0.18 * crossVenueDetection)
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
				venue,
				equalWeightSwitchScore,
				anonymityHeavySwitchScore,
				enforcementCostHeavySwitchScore,
				disclosureCost
		);
	}
}
