package lobbycapture.budget;

import lobbycapture.actor.InterestClient;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.calibration.CalibrationProfile;
import lobbycapture.policy.PolicyContest;
import lobbycapture.simulation.WorldState;
import lobbycapture.util.Values;

public final class ClientFundingModel {
    public ClientFundingResult fund(PolicyContest contest, WorldState world) {
        double totalFunding = 0.0;
        double weightedDisclosureLag = 0.0;
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
                CalibrationProfile calibration = world.calibrationProfile();
                double issueScale = calibration.issueFundingScale(contest.issueDomain());
                double reformThreat = contest.antiCaptureReform()
                        ? 0.45 + (0.55 * lobby.reformThreatSensitivity())
                        : 0.0;
                double amount = Values.clamp(
                        (0.055 + (0.045 * world.evasionFreedom()))
                                * preference
                                * exposure
                                * issueScale
                                * (0.35 + clientGain + reformThreat),
                        0.0,
                        0.70
                );
                if (amount <= 0.000001) {
                    continue;
                }
                FundingSource source = fundingSource(client, world);
                double traceability = traceabilityFor(source, calibration, contest.issueDomain(), world);
                double disclosureLag = Values.clamp(
                        (0.55 * calibration.disclosureLag(contest.issueDomain()))
                                + (0.45 * world.evasionProfile().disclosureLag()),
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
                        source == FundingSource.DARK_MONEY ? 0.42 : 0.18,
                        contest.id(),
                        contest.issueDomain(),
                        world.clock().tick(),
                        source == FundingSource.DARK_MONEY ? world.evasionProfile().legalRisk() : 0.08,
                        client.reputationalRisk(),
                        Values.clamp(clientGain - contest.truePublicBenefit(), -1.0, 1.0)
                ));
                totalFunding += amount;
                weightedDisclosureLag += amount * disclosureLag;
            }
        }
        double averageDisclosureLag = totalFunding == 0.0 ? 0.0 : weightedDisclosureLag / totalFunding;
        return new ClientFundingResult(totalFunding, world.contributionLedger().donorInfluenceGini(), averageDisclosureLag);
    }

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
            CalibrationProfile calibration,
            String issueDomain,
            WorldState world
    ) {
        double baseline = calibration.averageTraceability(issueDomain);
        if (source == FundingSource.DARK_MONEY) {
            return Values.clamp((0.45 * baseline) + (0.55 * world.reformRegime().darkMoneyDisclosureStrength())
                    - (0.35 * world.evasionProfile().opacity()), 0.0, 1.0);
        }
        return Values.clamp((0.70 * baseline) + (0.30 * world.reformRegime().transparencyStrength()), 0.0, 1.0);
    }
}

