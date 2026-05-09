package lobbycapture.calibration;

public record IntermediaryRecord(
        String organization,
        String subsection,
        String issueDomain,
        double revenue,
        double politicalSpend,
        double grantmaking,
        double donorDisclosure
) {
}
