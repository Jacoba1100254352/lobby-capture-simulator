package lobbycapture.budget;

import lobbycapture.util.Values;

public record MoneyFlow(
        String sourceId,
        String recipientId,
        String intermediaryId,
        FundingSource flowType,
        double amount,
        double disclosureLag,
        double traceability,
        double coordinationRisk,
        String targetContest,
        String issueDomain,
        int time,
        double legalRisk,
        double reputationalRisk,
        double expectedInfluenceReturn
) {
    public MoneyFlow {
        if (sourceId == null || sourceId.isBlank()) {
            throw new IllegalArgumentException("sourceId must not be blank.");
        }
        if (recipientId == null || recipientId.isBlank()) {
            throw new IllegalArgumentException("recipientId must not be blank.");
        }
        if (flowType == null) {
            throw new IllegalArgumentException("flowType must not be null.");
        }
        Values.requireRange("amount", amount, 0.0, 1_000_000.0);
        Values.requireRange("disclosureLag", disclosureLag, 0.0, 1.0);
        Values.requireRange("traceability", traceability, 0.0, 1.0);
        Values.requireRange("coordinationRisk", coordinationRisk, 0.0, 1.0);
        Values.requireRange("legalRisk", legalRisk, 0.0, 1.0);
        Values.requireRange("reputationalRisk", reputationalRisk, 0.0, 1.0);
        Values.requireRange("expectedInfluenceReturn", expectedInfluenceReturn, -1.0, 1.0);
    }
}

