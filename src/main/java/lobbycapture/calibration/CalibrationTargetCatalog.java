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
                new CalibrationTarget("procurement-awards", "USAspending, SAM.gov, and FPDS", "award recipients, agencies, UEIs, PIIDs, competition, and modifications", "procurement capture", "Bound procurement concentration, single-bid pressure, and firewall exposure."),
                new CalibrationTarget("intermediary-routing", "IRS 8871/8872, TEOS, Form 990, and ProPublica overlays", "nonprofit, 527, association, think-tank, revenue, spend, grants, and donor-disclosure rows", "intermediary routing and opacity", "Separate source-observed intermediary capacity from synthetic hidden influence."),
                new CalibrationTarget("revolving-door-bridges", "FACA, OGE, LegiStorm, OpenSecrets, and curated personnel exports", "former-official roles, cooling-off intervals, source records, position type, and match confidence", "revolving-door bridge pressure", "Keep headcount, confidence, and modeled influence intensity separate.")
        );
    }
}
