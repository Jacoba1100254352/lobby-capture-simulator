package lobbycapture.policy;

import lobbycapture.util.Values;

public record CommentTriageReport(
        double uniqueInformationShare,
        double organizedTechnicalShare,
        double duplicateCompressionRate,
        double reviewBurden,
        double proceduralAckRate,
        double substantiveUptakeRate,
        double effectiveInformationWeight,
        double recordDistortion,
        double authenticationConfidence
) {
    public CommentTriageReport {
        Values.requireRange("uniqueInformationShare", uniqueInformationShare, 0.0, 1.0);
        Values.requireRange("organizedTechnicalShare", organizedTechnicalShare, 0.0, 1.0);
        Values.requireRange("duplicateCompressionRate", duplicateCompressionRate, 0.0, 1.0);
        Values.requireRange("reviewBurden", reviewBurden, 0.0, 1.0);
        Values.requireRange("proceduralAckRate", proceduralAckRate, 0.0, 1.0);
        Values.requireRange("substantiveUptakeRate", substantiveUptakeRate, 0.0, 1.0);
        Values.requireRange("effectiveInformationWeight", effectiveInformationWeight, 0.0, 1.0);
        Values.requireRange("recordDistortion", recordDistortion, 0.0, 1.0);
        Values.requireRange("authenticationConfidence", authenticationConfidence, 0.0, 1.0);
    }
}
