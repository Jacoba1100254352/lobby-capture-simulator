package lobbycapture.calibration;

public record ProcurementAwardRecord(
        String awardId,
        String recipient,
        String agency,
        String subAgency,
        String issueDomain,
        double amount,
        double numberOfOffers,
        boolean priceOnlyAward,
        boolean exPostModification,
        String actionDate,
        String competitionType,
        boolean protestFiled,
        boolean exclusionFlag,
        boolean firewallCovered,
        boolean knownUei,
        boolean knownPiid
) {
    public boolean initialAward() {
        return !exPostModification;
    }

    public boolean limitedCompetition() {
        String text = competitionType == null ? "" : competitionType.toUpperCase();
        return text.contains("NOT COMPETED")
                || text.contains("LIMITED")
                || text.contains("SOLE SOURCE")
                || text.contains("EXCLUSION")
                || (numberOfOffers > 0.0 && numberOfOffers <= 1.0);
    }
}
