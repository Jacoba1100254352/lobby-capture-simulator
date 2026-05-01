package lobbycapture.actor;

import lobbycapture.util.Values;

public record Candidate(
        String id,
        String office,
        double ideology,
        boolean incumbent,
        double smallDonorBase,
        double largeDonorDependence,
        double publicFinancingOptIn,
        double fundraisingTimeBurden,
        double policyDebtToSponsors
) {
    public Candidate {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        Values.requireRange("ideology", ideology, -1.0, 1.0);
        Values.requireRange("smallDonorBase", smallDonorBase, 0.0, 1.0);
        Values.requireRange("largeDonorDependence", largeDonorDependence, 0.0, 1.0);
        Values.requireRange("publicFinancingOptIn", publicFinancingOptIn, 0.0, 1.0);
        Values.requireRange("fundraisingTimeBurden", fundraisingTimeBurden, 0.0, 1.0);
        Values.requireRange("policyDebtToSponsors", policyDebtToSponsors, 0.0, 1.0);
    }
}

