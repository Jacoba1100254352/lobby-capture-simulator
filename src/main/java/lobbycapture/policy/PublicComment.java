package lobbycapture.policy;

import lobbycapture.util.Values;

public record PublicComment(
        String sourceId,
        String issueDomain,
        boolean genuine,
        boolean template,
        double technicalCredibility,
        double authenticationConfidence
) {
    public PublicComment {
        if (sourceId == null || sourceId.isBlank()) {
            throw new IllegalArgumentException("sourceId must not be blank.");
        }
        if (issueDomain == null || issueDomain.isBlank()) {
            throw new IllegalArgumentException("issueDomain must not be blank.");
        }
        Values.requireRange("technicalCredibility", technicalCredibility, 0.0, 1.0);
        Values.requireRange("authenticationConfidence", authenticationConfidence, 0.0, 1.0);
    }
}

