package lobbycapture.calibration;

import java.util.List;

public final class CalibrationTargetCatalog {
    private CalibrationTargetCatalog() {
    }

    public static List<CalibrationTarget> standardTargets() {
        return List.of(
                new CalibrationTarget("lda-spend-distribution", "LDA.gov", "client, registrant, issue, and spend filings", "lobby budgets and issue preferences", "Constrain visible lobbying scale and sector mix."),
                new CalibrationTarget("fec-money-concentration", "FEC", "candidate, committee, independent expenditure, and bundling data", "campaign finance and donor dependence", "Bound large donor and outside-spending pressure."),
                new CalibrationTarget("rulemaking-comments", "Federal Register and Regulations.gov", "rulemaking timing, dockets, and comments", "rulemaking arena and comment distortion", "Bound low-salience technical capture scenarios."),
                new CalibrationTarget("voucher-public-financing", "Seattle and NYC public-financing data", "voucher/match participation and public funds", "democracy voucher and public financing systems", "Calibrate public financing counterweight."),
                new CalibrationTarget("procurement-awards", "USAspending", "award recipients, agencies, and award types", "procurement capture", "Bound procurement concentration and exposure.")
        );
    }
}

