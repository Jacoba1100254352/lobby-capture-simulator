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
        List<LobbySpendRecord> spendRecords
) {
    public InfluenceResult {
        spendRecords = List.copyOf(spendRecords);
    }
}
