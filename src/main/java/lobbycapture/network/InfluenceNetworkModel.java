package lobbycapture.network;


import lobbycapture.actor.LobbyOrganization;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.simulation.WorldState;
import lobbycapture.strategy.ChannelAllocation;
import lobbycapture.strategy.InfluenceChannel;
import lobbycapture.strategy.SubstitutionProfile;
import lobbycapture.util.Values;

import java.util.ArrayList;
import java.util.List;


public final class InfluenceNetworkModel
{
	private InfluenceNetworkModel() {
	}
	
	public static List<InfluenceNetworkPath> pathsFor(
			LobbyOrganization group,
			PolicyContest contest,
			ReformRegime reform,
			WorldState world,
			ChannelAllocation allocation,
			double donorInfluenceGini,
			SubstitutionProfile substitution
	) {
		List<InfluenceNetworkPath> paths = new ArrayList<>();
		add(paths, group, contest, reform, world, InfluenceChannel.DIRECT_ACCESS, allocation.directAccess(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.AGENDA_ACCESS, allocation.agendaAccess(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.INFORMATION_DISTORTION, allocation.informationDistortion(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.PUBLIC_CAMPAIGN, allocation.publicCampaign(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.LITIGATION_THREAT, allocation.litigationThreat(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.CAMPAIGN_FINANCE, allocation.campaignFinance(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.DARK_MONEY, allocation.darkMoney(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.REVOLVING_DOOR, allocation.revolvingDoor(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.INTERMEDIARY, allocation.intermediary(), donorInfluenceGini, substitution);
		add(paths, group, contest, reform, world, InfluenceChannel.DEFENSIVE_REFORM, allocation.defensiveReform(), donorInfluenceGini, substitution);
		return paths;
	}
	
	private static void add(
			List<InfluenceNetworkPath> paths,
			LobbyOrganization group,
			PolicyContest contest,
			ReformRegime reform,
			WorldState world,
			InfluenceChannel channel,
			double weight,
			double donorInfluenceGini,
			SubstitutionProfile substitution
	) {
		if (weight <= 0.000001) {
			return;
		}
		paths.add(new InfluenceNetworkPath(
				group.id(),
				contest.issueDomain(),
				channel,
				weight,
				opacity(channel, group, contest, reform, world),
				donorConcentration(channel, group, donorInfluenceGini),
				intermediaryDependence(channel, group, contest, world),
				officialAccess(channel, group, reform),
				procurementLink(channel, group, contest, reform, world),
				revolvingDoorLink(channel, group, reform, world),
				commentMobilization(channel, group, contest, reform),
				venueShift(channel, world, reform, substitution)
		));
	}
	
	private static double opacity(
			InfluenceChannel channel,
			LobbyOrganization group,
			PolicyContest contest,
			ReformRegime reform,
			WorldState world
	) {
		double base = switch (channel) {
			case DIRECT_ACCESS -> 0.20;
			case AGENDA_ACCESS -> 0.28;
			case INFORMATION_DISTORTION -> 0.42;
			case PUBLIC_CAMPAIGN -> 0.30;
			case LITIGATION_THREAT -> 0.46;
			case CAMPAIGN_FINANCE -> 0.36;
			case DARK_MONEY -> 0.86;
			case REVOLVING_DOOR -> 0.60;
			case INTERMEDIARY -> 0.66;
			case DEFENSIVE_REFORM -> 0.54;
		};
		return Values.clamp(
				base
						+ (0.22 * group.disclosureAvoidanceSkill())
						+ (0.18 * world.evasionFreedom())
						+ (channel == InfluenceChannel.INTERMEDIARY ? 0.12 * world.calibrationProfile().intermediaryOpacity(contest.issueDomain()) : 0.0)
						- (0.28 * reform.transparencyStrength())
						- (0.10 * reform.contactLogCoverage())
						- (0.08 * reform.darkMoneyDisclosureStrength())
						- (0.10 * reform.crossVenueDetectionStrength()),
				0.0,
				1.0
		);
	}
	
	private static double donorConcentration(InfluenceChannel channel, LobbyOrganization group, double donorInfluenceGini) {
		double channelPressure = switch (channel) {
			case CAMPAIGN_FINANCE, DARK_MONEY, DEFENSIVE_REFORM -> 0.34;
			case PUBLIC_CAMPAIGN, INTERMEDIARY -> 0.22;
			default -> 0.08;
		};
		return Values.clamp((0.54 * donorInfluenceGini) + channelPressure + (0.16 * group.disclosureAvoidanceSkill()), 0.0, 1.0);
	}
	
	private static double intermediaryDependence(
			InfluenceChannel channel,
			LobbyOrganization group,
			PolicyContest contest,
			WorldState world
	) {
		double channelPressure = switch (channel) {
			case INTERMEDIARY -> 0.78;
			case DARK_MONEY -> 0.44;
			case PUBLIC_CAMPAIGN, INFORMATION_DISTORTION -> 0.28;
			case DEFENSIVE_REFORM -> 0.24;
			default -> 0.06;
		};
		return Values.clamp(
				channelPressure
						+ (0.16 * group.researchBudget() / Math.max(1.0, group.totalBudget()))
						+ (0.14 * world.calibrationProfile().intermediaryPoliticalPressure(contest.issueDomain())),
				0.0,
				1.0
		);
	}
	
	private static double officialAccess(InfluenceChannel channel, LobbyOrganization group, ReformRegime reform) {
		double channelPressure = switch (channel) {
			case DIRECT_ACCESS -> 0.78;
			case AGENDA_ACCESS -> 0.66;
			case REVOLVING_DOOR -> 0.58;
			case CAMPAIGN_FINANCE -> 0.36;
			case INTERMEDIARY -> 0.32;
			default -> 0.10;
		};
		return Values.clamp(channelPressure + (0.18 * group.accessCapital()) - (0.22 * reform.contactLogCoverage()), 0.0, 1.0);
	}
	
	private static double procurementLink(
			InfluenceChannel channel,
			LobbyOrganization group,
			PolicyContest contest,
			ReformRegime reform,
			WorldState world
	) {
		double domainPressure = contest.arena() == ContestArena.PROCUREMENT || contest.issueDomain().equals("procurement") ? 0.54 : 0.04;
		double channelPressure = switch (channel) {
			case DIRECT_ACCESS, AGENDA_ACCESS -> 0.20;
			case REVOLVING_DOOR -> 0.34;
			case INTERMEDIARY -> 0.28;
			case LITIGATION_THREAT -> 0.18;
			default -> 0.08;
		};
		return Values.clamp(
				domainPressure
						+ channelPressure
						+ (0.18 * group.preferenceFor("procurement"))
						+ (0.16 * world.calibrationProfile().procurementBridgeRisk(contest.issueDomain()))
						- (0.24 * reform.blindReviewStrength()),
				0.0,
				1.0
		);
	}
	
	private static double revolvingDoorLink(InfluenceChannel channel, LobbyOrganization group, ReformRegime reform, WorldState world) {
		double channelPressure = switch (channel) {
			case REVOLVING_DOOR -> 0.76;
			case DIRECT_ACCESS, AGENDA_ACCESS -> 0.24;
			case INTERMEDIARY -> 0.22;
			case LITIGATION_THREAT -> 0.16;
			default -> 0.04;
		};
		return Values.clamp(
				channelPressure
						+ (0.36 * group.revolvingDoorNetworkStrength())
						+ (0.14 * world.calibrationProfile().revolvingDoorSourcePressure(group.sector()))
						+ (0.12 * world.evasionProfile().revolvingDoorPlacementShift())
						- (0.34 * reform.coolingOffStrength()),
				0.0,
				1.0
		);
	}
	
	private static double commentMobilization(
			InfluenceChannel channel, LobbyOrganization group, PolicyContest contest, ReformRegime reform) {
		if (contest.arena() != ContestArena.RULEMAKING && contest.arena() != ContestArena.PUBLIC_INFORMATION) {
			return 0.0;
		}
		double channelPressure = switch (channel) {
			case PUBLIC_CAMPAIGN -> 0.54;
			case DARK_MONEY -> 0.40;
			case INTERMEDIARY -> 0.46;
			case INFORMATION_DISTORTION -> 0.36;
			default -> 0.08;
		};
		return Values.clamp(
				channelPressure
						+ (0.22 * group.astroturfSkill())
						+ (0.18 * contest.docket().templateSaturation())
						- (0.30 * reform.antiAstroturfStrength()),
				0.0,
				1.0
		);
	}
	
	private static double venueShift(InfluenceChannel channel, WorldState world, ReformRegime reform, SubstitutionProfile substitution) {
		double channelPressure = switch (channel) {
			case DARK_MONEY, INTERMEDIARY -> 0.34;
			case LITIGATION_THREAT, DEFENSIVE_REFORM -> 0.22;
			case REVOLVING_DOOR -> 0.18;
			default -> 0.06;
		};
		return Values.clamp(
				channelPressure
						+ (0.42 * substitution.venueSubstitutionRate())
						+ (0.24 * substitution.messengerSubstitutionRate())
						+ (0.16 * world.evasionFreedom())
						- (0.18 * reform.crossVenueDetectionStrength()),
				0.0,
				1.0
		);
	}
}
