package lobbycapture.calibration;

public record ProcurementAwardRecord(
        String awardId,
        String recipient,
        String issueDomain,
        double amount,
        double numberOfOffers,
        boolean priceOnlyAward,
        boolean exPostModification,
        boolean firewallCovered,
        boolean knownUei,
        boolean knownPiid
) {
}
