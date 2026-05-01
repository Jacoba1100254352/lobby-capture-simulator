package lobbycapture.strategy;

import lobbycapture.actor.LobbyOrganization;
import lobbycapture.arena.ContestOutcome;
import lobbycapture.budget.ClientFundingModel;
import lobbycapture.budget.ClientFundingResult;
import lobbycapture.policy.CommentCampaign;
import lobbycapture.policy.Docket;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.reform.TransparencySystem;
import lobbycapture.simulation.WorldState;
import lobbycapture.util.Values;

import java.util.ArrayList;
import java.util.List;

public final class LobbyAllocationEngine {
    private final ClientFundingModel clientFundingModel = new ClientFundingModel();

    public InfluenceResult apply(PolicyContest contest, WorldState world) {
        ReformRegime reform = world.reformRegime();
        ClientFundingResult funding = clientFundingModel.fund(contest, world);
        double totalSpend = 0.0;
        double defensiveSpend = 0.0;
        int channelSwitches = 0;
        int evasionShifts = 0;
        double lobbyPressure = contest.lobbyPressure();
        double perceivedSupport = contest.perceivedPublicSupport();
        double publicBenefit = contest.truePublicBenefit();
        double privateGain = contest.privateGain();
        double regulatorAttention = world.regulatorAttention(contest.issueDomain());
        double watchdogFocus = world.watchdogFocus(contest.issueDomain());
        double publicAdvocatePressure = contest.publicAdvocatePressure()
                + (reform.publicAdvocateStrength() * 0.16)
                + (regulatorAttention * reform.publicAdvocateStrength() * 0.08);
        double watchdogPressure = contest.watchdogPressure()
                + (reform.transparencyStrength() * 0.10)
                + (reform.enforcementStrength() * 0.06)
                + (watchdogFocus * 0.14);
        double informationDistortion = contest.informationDistortion();
        double commentRecordDistortion = contest.commentRecordDistortion();
        double darkMoneyInfluence = contest.darkMoneyInfluence();
        double revolvingDoorInfluence = contest.revolvingDoorInfluence();
        double campaignFinanceInfluence = contest.campaignFinanceInfluence();
        double litigationThreat = contest.litigationThreat();
        Docket docket = contest.docket();
        ChannelAllocation totalAllocation = ChannelAllocation.zero();
        List<LobbySpendRecord> records = new ArrayList<>();

        for (LobbyOrganization group : world.lobbyOrganizations()) {
            double preference = preferenceFor(group, contest);
            if (preference <= 0.000001) {
                continue;
            }
            StrategyMemory memory = world.memoryFor(group.id(), group.initialStrategy());
            InfluenceStrategy strategy = selectStrategy(group, contest, reform, world, memory);
            double spendIntent = contest.antiCaptureReform()
                    ? DefensiveReformStrategy.spendIntent(group, contest) * memory.reformThreat()
                    : supportiveSpendIntent(group, contest, preference);
            double requestedSpend = spendIntent
                    * world.spendScale()
                    * memory.budgetMultiplier()
                    * memory.issueMultiplier(contest.issueDomain());
            if (contest.antiCaptureReform()) {
                requestedSpend = Math.min(requestedSpend, group.totalBudget() * reform.defensiveCapShare() * memory.budgetMultiplier());
            }
            double spend = world.spendBudget(group.id(), requestedSpend);
            if (spend <= 0.000001) {
                continue;
            }

            if (strategy != memory.currentStrategy()) {
                channelSwitches++;
            }
            if (strategy == InfluenceStrategy.DARK_MONEY && memory.currentStrategy() != InfluenceStrategy.DARK_MONEY) {
                memory.recordEvasionShift();
                evasionShifts++;
            }

            ChannelAllocation allocation = ChannelAllocation.forStrategy(strategy, spend);
            totalAllocation = totalAllocation.plus(allocation);
            totalSpend += spend;
            if (contest.antiCaptureReform()) {
                defensiveSpend += spend;
            }
            records.add(new LobbySpendRecord(group.id(), strategy, spend, preference, contest.antiCaptureReform()));

            if (contest.antiCaptureReform()) {
                double defensivePower = defensivePower(allocation, group);
                lobbyPressure -= world.pressurePerSpend() * group.influenceIntensity() * defensivePower;
                perceivedSupport -= world.publicCampaignEffect() * group.publicCampaignSkill()
                        * ((0.16 * allocation.publicCampaign()) + (0.11 * allocation.darkMoney()));
                perceivedSupport -= group.informationBias() * allocation.informationDistortion() * 0.06;
                litigationThreat += group.litigationThreatSkill() * allocation.litigationThreat() * 0.08;
                informationDistortion += group.informationBias() * allocation.informationDistortion() * 0.06;
                darkMoneyInfluence += group.disclosureAvoidanceSkill() * allocation.darkMoney() * (1.0 - reform.darkMoneyDisclosureStrength()) * 0.08;
                campaignFinanceInfluence += allocation.campaignFinance() * 0.035;
                publicBenefit -= group.informationBias() * allocation.informationDistortion() * 0.025;
            } else {
                double fit = policyFit(group, contest) * preference;
                double accessEffectiveness = 1.0 - (reform.contactLogCoverage() * 0.45) - (reform.lobbyingBanStrength() * 0.35);
                double informationEffectiveness = 1.0 - (reform.blindReviewStrength() * 0.70)
                        - (reform.publicAdvocateStrength() * 0.30)
                        - (regulatorAttention * 0.18);
                double campaignEffectiveness = 1.0 - (reform.campaignFinanceCounterweight() * 0.45);
                double mismatchPenalty = publicMismatchPenalty(group, contest);
                lobbyPressure += world.pressurePerSpend() * group.influenceIntensity() * fit
                        * ((0.78 * allocation.directAccess() * accessEffectiveness)
                        + (0.62 * allocation.agendaAccess() * accessEffectiveness)
                        + (0.42 * allocation.revolvingDoor()));
                perceivedSupport += world.publicCampaignEffect() * group.publicCampaignSkill() * group.informationBias()
                        * campaignEffectiveness * ((0.09 * allocation.publicCampaign()) + (0.045 * allocation.darkMoney()));
                perceivedSupport += group.informationBias() * informationEffectiveness * allocation.informationDistortion() * 0.045;
                perceivedSupport -= mismatchPenalty * (allocation.publicCampaign() + allocation.darkMoney()) * 0.025;
                publicBenefit -= group.informationBias() * informationEffectiveness * allocation.informationDistortion() * 0.028;
                publicBenefit -= allocation.litigationThreat() * 0.018;
                privateGain += group.influenceIntensity() * spend * (0.026 + (0.038 * fit));
                informationDistortion += group.informationBias() * informationEffectiveness * allocation.informationDistortion() * 0.075;
                CommentCampaign commentCampaign = CommentCampaign.fromAllocation(docket, group, allocation, reform);
                docket = docket.withCampaign(commentCampaign);
                commentRecordDistortion += commentDistortionEffect(contest, group, allocation, reform, commentCampaign);
                darkMoneyInfluence += group.disclosureAvoidanceSkill() * allocation.darkMoney()
                        * (1.0 - reform.darkMoneyDisclosureStrength())
                        * (1.0 + world.evasionProfile().opacity()) * 0.075;
                revolvingDoorInfluence += group.revolvingDoorNetworkStrength() * allocation.revolvingDoor()
                        * (1.0 - reform.coolingOffStrength())
                        * (1.0 + world.evasionProfile().revolvingDoorPlacementShift()) * 0.070;
                campaignFinanceInfluence += allocation.campaignFinance() * (1.0 - reform.campaignFinanceCounterweight()) * 0.075;
                litigationThreat += group.litigationThreatSkill() * allocation.litigationThreat()
                        * (1.0 + world.evasionProfile().litigationFundingShift()) * 0.070;
            }
        }

        double financingCorrection = reform.campaignFinanceCounterweight();
        if (financingCorrection > 0.0) {
            perceivedSupport += financingCorrection * (publicBenefit - perceivedSupport) * 0.22;
            lobbyPressure -= Math.max(0.0, lobbyPressure) * financingCorrection * 0.18;
            privateGain -= privateGain * financingCorrection * 0.05;
        }

        PolicyContest influenced = contest.withInfluence(
                lobbyPressure,
                perceivedSupport,
                publicBenefit,
                privateGain,
                publicAdvocatePressure,
                watchdogPressure,
                informationDistortion,
                commentRecordDistortion,
                darkMoneyInfluence,
                revolvingDoorInfluence,
                campaignFinanceInfluence,
                litigationThreat
        ).withDocket(docket);
        influenced = new TransparencySystem(reform).applyBacklash(influenced);
        return new InfluenceResult(
                influenced,
                totalAllocation,
                totalSpend,
                defensiveSpend,
                funding.totalFunding(),
                funding.donorInfluenceGini(),
                funding.averageDisclosureLag(),
                channelSwitches,
                evasionShifts,
                records
        );
    }

    public void observe(ContestOutcome outcome, WorldState world) {
        if (!world.adaptiveStrategies()) {
            return;
        }
        for (LobbySpendRecord record : outcome.influenceResult().spendRecords()) {
            LobbyOrganization group = findLobby(world, record.lobbyId());
            StrategyMemory memory = world.memoryFor(group.id(), group.initialStrategy());
            double signal = returnSignal(group, record.strategy(), outcome);
            memory.recordReturn(record.strategy(), signal, outcome.contest());
            memory.adapt(outcome.contest(), outcome.captured(), outcome.antiCaptureReformEnacted());
            if (signal > 0.08) {
                world.topUpBudget(group.id(), group.totalBudget() * 0.035 * signal * memory.budgetMultiplier());
            }
        }
    }

    private static InfluenceStrategy selectStrategy(
            LobbyOrganization group,
            PolicyContest contest,
            ReformRegime reform,
            WorldState world,
            StrategyMemory memory
    ) {
        if (contest.antiCaptureReform()) {
            return InfluenceStrategy.DEFENSIVE_REFORM;
        }
        if (world.evasionFreedom() > 0.0
                && reform.transparencyStrength() >= 0.52
                && group.disclosureAvoidanceSkill() * world.evasionFreedom() * (1.0 + world.evasionProfile().opacity()) >= 0.30) {
            return InfluenceStrategy.DARK_MONEY;
        }
        return memory.currentStrategy();
    }

    private static double preferenceFor(LobbyOrganization group, PolicyContest contest) {
        if (contest.antiCaptureReform()) {
            return Math.max(0.45, group.preferenceFor("democracy"));
        }
        return group.preferenceFor(contest.issueDomain());
    }

    private static double supportiveSpendIntent(LobbyOrganization group, PolicyContest contest, double preference) {
        double fit = policyFit(group, contest);
        double privateUpside = 0.24 + contest.privateGain();
        double salience = 0.30 + contest.salience();
        double publicMismatch = publicMismatchPenalty(group, contest);
        return Values.clamp(
                group.influenceIntensity() * preference * fit * privateUpside * salience * (1.0 + publicMismatch),
                0.0,
                1.20
        );
    }

    private static double policyFit(LobbyOrganization group, PolicyContest contest) {
        return Values.clamp(1.0 - (Math.abs(group.preferredPolicyPosition() - normalizedContestPosition(contest)) / 2.0), 0.0, 1.0);
    }

    private static double normalizedContestPosition(PolicyContest contest) {
        return Values.clamp((contest.privateGain() - contest.truePublicBenefit()) * 1.35, -1.0, 1.0);
    }

    private static double publicMismatchPenalty(LobbyOrganization group, PolicyContest contest) {
        double mismatch = Math.max(0.0, contest.truePublicSupport() - contest.perceivedPublicSupport());
        return Math.max(0.0, mismatch - group.publicSupportMismatchTolerance());
    }

    private static double defensivePower(ChannelAllocation allocation, LobbyOrganization group) {
        return (0.44 * allocation.defensiveReform())
                + (0.22 * allocation.publicCampaign())
                + (0.16 * allocation.litigationThreat())
                + (0.12 * allocation.darkMoney())
                + (0.08 * allocation.informationDistortion())
                + (group.defensiveMultiplier() * 0.04);
    }

    private static double commentDistortionEffect(
            PolicyContest contest,
            LobbyOrganization group,
            ChannelAllocation allocation,
            ReformRegime reform,
            CommentCampaign campaign
    ) {
        if (contest.arena() != ContestArena.RULEMAKING && contest.arena() != ContestArena.PUBLIC_INFORMATION) {
            return 0.0;
        }
        double authenticationControl = 1.0 - reform.antiAstroturfStrength();
        return campaign.distortion() * group.astroturfSkill() * authenticationControl
                * ((0.055 * allocation.publicCampaign()) + (0.045 * allocation.darkMoney()) + (0.035 * allocation.informationDistortion()));
    }

    private static double returnSignal(LobbyOrganization group, InfluenceStrategy strategy, ContestOutcome outcome) {
        PolicyContest contest = outcome.contest();
        if (contest.antiCaptureReform()) {
            double threat = (0.42 * contest.truePublicBenefit()) + (0.32 * contest.perceivedPublicSupport()) + (0.26 * contest.salience());
            return outcome.antiCaptureReformEnacted() ? -threat : threat;
        }
        double privateUpside = contest.privateGain() * group.preferenceFor(contest.issueDomain());
        double publicBacklash = Math.max(0.0, contest.truePublicSupport() - contest.perceivedPublicSupport());
        double result = outcome.captured()
                ? privateUpside + (0.38 * outcome.captureIndex()) - (0.22 * publicBacklash)
                : (-0.25 * privateUpside) - (0.12 * contest.salience());
        if (strategy == InfluenceStrategy.INFORMATION_DISTORTION && publicBacklash > group.publicSupportMismatchTolerance()) {
            result -= 0.10 * publicBacklash;
        }
        if (outcome.detected()) {
            result -= 0.20 + (0.20 * outcome.sanctionCost());
        }
        return Values.clamp(result, -1.0, 1.0);
    }

    private static LobbyOrganization findLobby(WorldState world, String id) {
        return world.lobbyOrganizations().stream()
                .filter(group -> group.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unknown lobby organization: " + id));
    }
}
