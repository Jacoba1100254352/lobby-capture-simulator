package lobbycapture.calibration;

import lobbycapture.util.Values;

public record LdaRecord(
        String client,
        String registrant,
        String issueDomain,
        double amount,
        double disclosureLag,
        double coveredOfficialShare
) {
    public LdaRecord {
        requireText("client", client);
        requireText("registrant", registrant);
        requireText("issueDomain", issueDomain);
        Values.requireRange("amount", amount, 0.0, 1_000_000.0);
        Values.requireRange("disclosureLag", disclosureLag, 0.0, 1.0);
        Values.requireRange("coveredOfficialShare", coveredOfficialShare, 0.0, 1.0);
    }

    private static void requireText(String name, String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank.");
        }
    }
}

