package lobbycapture.budget;

import lobbycapture.util.Values;

public record DarkMoneyPool(
        String id,
        double balance,
        double traceability,
        double launderingSkill,
        double disclosureRisk
) {
    public DarkMoneyPool {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        Values.requireRange("balance", balance, 0.0, 1_000_000.0);
        Values.requireRange("traceability", traceability, 0.0, 1.0);
        Values.requireRange("launderingSkill", launderingSkill, 0.0, 1.0);
        Values.requireRange("disclosureRisk", disclosureRisk, 0.0, 1.0);
    }
}

