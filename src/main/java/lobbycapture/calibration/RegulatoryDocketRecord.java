package lobbycapture.calibration;

import lobbycapture.util.Values;

public record RegulatoryDocketRecord(
        String docketId,
        String issueDomain,
        String agency,
        int commentVolume,
        double genuineShare,
        double templateShare,
        double technicalClaimCredibility,
        double authenticationShare
) {
    public RegulatoryDocketRecord {
        if (commentVolume < 0) {
            throw new IllegalArgumentException("commentVolume must not be negative.");
        }
        Values.requireRange("genuineShare", genuineShare, 0.0, 1.0);
        Values.requireRange("templateShare", templateShare, 0.0, 1.0);
        Values.requireRange("technicalClaimCredibility", technicalClaimCredibility, 0.0, 1.0);
        Values.requireRange("authenticationShare", authenticationShare, 0.0, 1.0);
    }
}

