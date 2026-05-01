package lobbycapture.strategy;

import lobbycapture.policy.PolicyContest;

import java.util.List;

public record InfluenceResult(
        PolicyContest contest,
        ChannelAllocation allocation,
        double totalSpend,
        double defensiveSpend,
        double clientFunding,
        double donorInfluenceGini,
        double averageDisclosureLag,
        int channelSwitches,
        int evasionShifts,
        double substitutionPressure,
        double influencePreservationRate,
        double hiddenInfluenceShare,
        double netTransparencyGain,
        double messengerSubstitutionRate,
        double venueSubstitutionRate,
        List<LobbySpendRecord> spendRecords
) {
    public InfluenceResult {
        spendRecords = List.copyOf(spendRecords);
    }

    public InfluenceResult(
            PolicyContest contest,
            ChannelAllocation allocation,
            double totalSpend,
            double defensiveSpend,
            double clientFunding,
            double donorInfluenceGini,
            double averageDisclosureLag,
            int channelSwitches,
            int evasionShifts,
            List<LobbySpendRecord> spendRecords
    ) {
        this(
                contest,
                allocation,
                totalSpend,
                defensiveSpend,
                clientFunding,
                donorInfluenceGini,
                averageDisclosureLag,
                channelSwitches,
                evasionShifts,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                spendRecords
        );
    }
}
