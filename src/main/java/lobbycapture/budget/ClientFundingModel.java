package lobbycapture.budget;


import lobbycapture.actor.InterestClient;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.policy.PolicyContest;
import lobbycapture.simulation.WorldState;
import lobbycapture.util.Values;


public final class ClientFundingModel
{
	private static double exposureFor(InterestClient client, PolicyContest contest) {
		return switch (contest.arena()) {
			case RULEMAKING -> client.regulatoryExposure();
			case PROCUREMENT -> client.procurementExposure();
			case ENFORCEMENT -> client.enforcementExposure();
			case ELECTION, LEGISLATIVE, PUBLIC_INFORMATION, LITIGATION -> Math.max(
					client.regulatoryExposure(),
					Math.max(client.procurementExposure(), client.enforcementExposure())
			);
		};
	}
	
	private static FundingSource fundingSource(InterestClient client, WorldState world) {
		if (client.needForSecrecy() + world.evasionProfile().opacity() > 1.05) {
			return FundingSource.DARK_MONEY;
		}
		if (world.reformRegime().democracyVoucherStrength() > 0.50 && client.sector().equals("democracy")) {
			return FundingSource.DEMOCRACY_VOUCHER;
		}
		return FundingSource.TRADE_ASSOCIATION;
	}
	
	private static double traceabilityFor(
			FundingSource source,
			String issueDomain,
			WorldState world
	) {
		double baseline = world.calibratedAverageTraceability(issueDomain);
		if (source == FundingSource.DARK_MONEY) {
			return Values.clamp((0.45 * baseline) + (0.55 * world.reformRegime().darkMoneyDisclosureStrength())
					                    - (0.35 * world.evasionProfile().opacity()), 0.0, 1.0);
		}
		return Values.clamp((0.70 * baseline) + (0.30 * world.reformRegime().transparencyStrength()), 0.0, 1.0);
	}
	
	private static double largeDonorDependenceFor(
			FundingSource source,
			String issueDomain,
			WorldState world
	) {
		double baseline = Values.clamp(
				(0.62 * world.calibratedLargeDonorShare(issueDomain))
						+ (0.38 * world.calibratedDonorConcentrationIndex(issueDomain)),
				0.0,
				1.0
		);
		if (source == FundingSource.PUBLIC_MATCH || source == FundingSource.DEMOCRACY_VOUCHER) {
			return Values.clamp((0.35 * baseline) - (0.18 * world.reformRegime().campaignFinanceCounterweight()), 0.0, 1.0);
		}
		double opacityPressure = source == FundingSource.DARK_MONEY ? 0.16 + (0.10 * world.evasionProfile().opacity()) : 0.06;
		return Values.clamp((0.70 * baseline) + opacityPressure, 0.0, 1.0);
	}
	
	public ClientFundingResult fund(PolicyContest contest, WorldState world) {
		double totalFunding = 0.0;
		double weightedDisclosureLag = 0.0;
		double weightedLobbyingDisclosureLag = 0.0;
		double weightedCampaignDisclosureLag = 0.0;
		for (InterestClient client : world.clients()) {
			double clientGain = client.privateGainByPolicy().getOrDefault(contest.issueDomain(), contest.privateGain());
			double exposure = exposureFor(client, contest);
			if (exposure <= 0.000001) {
				continue;
			}
			for (LobbyOrganization lobby : world.lobbyOrganizations()) {
				double preference = contest.antiCaptureReform()
						? Math.max(0.35, lobby.preferenceFor("democracy"))
						: lobby.preferenceFor(contest.issueDomain());
				if (preference <= 0.000001 || !client.sector().equals(lobby.sector())) {
					continue;
				}
				double issueScale = world.calibratedIssueFundingScale(contest.issueDomain());
				double reformThreat = contest.antiCaptureReform()
						? 0.45 + (0.55 * lobby.reformThreatSensitivity())
						: 0.0;
				double amount = Values.clamp(
						(0.055 + (0.045 * world.evasionFreedom()))
								* preference
								* exposure
								* issueScale
								* world.clientFundingMultiplier(client.id(), contest.issueDomain())
								* (0.35 + clientGain + reformThreat),
						0.0,
						0.70
				);
				if (amount <= 0.000001) {
					continue;
				}
				FundingSource source = fundingSource(client, world);
				double traceability = traceabilityFor(source, contest.issueDomain(), world);
				double largeDonorDependence = largeDonorDependenceFor(source, contest.issueDomain(), world);
				double lobbyingDisclosureLag = Values.clamp(
						0.18
								+ (0.48 * world.calibratedDisclosureLag(contest.issueDomain()))
								+ (0.06 * world.evasionProfile().disclosureLag()),
						0.0,
						1.0
				);
				double campaignDisclosureLag = Values.clamp(
						world.calibratedCampaignDisclosureLag(contest.issueDomain())
								+ (0.12 * world.evasionProfile().disclosureLag()),
						0.0,
						1.0
				);
				double disclosureLag = Values.clamp(
						(0.70 * lobbyingDisclosureLag)
								+ (0.30 * campaignDisclosureLag)
								- (0.10 * world.reformRegime().realTimeDisclosure()),
						0.0,
						1.0
				);
				world.topUpBudget(lobby.id(), amount);
				world.contributionLedger().add(new MoneyFlow(
						client.id(),
						lobby.id(),
						source == FundingSource.DARK_MONEY ? "dark-pool" : "trade-association",
						source,
						amount,
						disclosureLag,
						traceability,
						largeDonorDependence,
						contest.id(),
						contest.issueDomain(),
						world.clock().tick(),
						source == FundingSource.DARK_MONEY ? world.evasionProfile().legalRisk() : 0.08,
						client.reputationalRisk(),
						Values.clamp(clientGain - contest.truePublicBenefit(), -1.0, 1.0)
				));
				totalFunding += amount;
				weightedDisclosureLag += amount * disclosureLag;
				weightedLobbyingDisclosureLag += amount * lobbyingDisclosureLag;
				weightedCampaignDisclosureLag += amount * campaignDisclosureLag;
			}
		}
		double averageDisclosureLag = totalFunding == 0.0 ? 0.0 : weightedDisclosureLag / totalFunding;
		double averageLobbyingDisclosureLag = totalFunding == 0.0 ? 0.0 : weightedLobbyingDisclosureLag / totalFunding;
		double averageCampaignDisclosureLag = totalFunding == 0.0 ? 0.0 : weightedCampaignDisclosureLag / totalFunding;
		return new ClientFundingResult(
				totalFunding,
				world.contributionLedger().donorInfluenceGini(),
				averageDisclosureLag,
				averageLobbyingDisclosureLag,
				averageCampaignDisclosureLag
		);
	}
}
