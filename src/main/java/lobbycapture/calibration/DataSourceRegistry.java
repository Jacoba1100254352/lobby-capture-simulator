package lobbycapture.calibration;

import java.util.List;

public final class DataSourceRegistry {
    private DataSourceRegistry() {
    }

    public static List<String> sources() {
        return List.of(
                "LDA.gov and Senate LDA bulk data",
                "FEC campaign finance data",
                "Federal Register API",
                "Regulations.gov API",
                "Voteview",
                "govinfo Bill Status XML",
                "Seattle Democracy Voucher data",
                "NYC Campaign Finance Board data",
                "USAspending API",
                "SAM.gov and FPDS procurement bridge exports",
                "IRS 8871/8872, TEOS, and Form 990 nonprofit records",
                "FACA, OGE, LegiStorm, OpenSecrets, and ProPublica-style access or personnel exports"
        );
    }
}
