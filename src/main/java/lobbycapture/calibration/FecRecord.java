package lobbycapture.calibration;

import lobbycapture.budget.FundingSource;
import lobbycapture.util.Values;

public record FecRecord(
        String source,
        String recipient,
        String issueDomain,
        double amount,
        FundingSource flowType,
        double traceability,
        double largeDonorShare
) {
    public FecRecord {
        requireText("source", source);
        requireText("recipient", recipient);
        requireText("issueDomain", issueDomain);
        Values.requireRange("amount", amount, 0.0, 1_000_000.0);
        if (flowType == null) {
            throw new IllegalArgumentException("flowType must not be null.");
        }
        Values.requireRange("traceability", traceability, 0.0, 1.0);
        Values.requireRange("largeDonorShare", largeDonorShare, 0.0, 1.0);
    }

    private static void requireText(String name, String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank.");
        }
    }
}

