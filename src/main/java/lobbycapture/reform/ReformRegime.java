package lobbycapture.reform;

import lobbycapture.util.Values;

public record ReformRegime(
        String name,
        double disclosureStrength,
        double realTimeDisclosure,
        double beneficialOwnerDisclosure,
        double contactLogCoverage,
        double lobbyingBanStrength,
        double coolingOffStrength,
        double publicFinancingStrength,
        double democracyVoucherStrength,
        double contributionLimitStrength,
        double darkMoneyDisclosureStrength,
        double publicAdvocateStrength,
        double blindReviewStrength,
        double antiAstroturfStrength,
        double enforcementBudget,
        double auditRate,
        double sanctionSeverity,
        double appealsDelay,
        double defensiveCapShare,
        double administrativeCost,
        double falsePositiveCost,
        double constitutionalChallengeRisk
) {
    public ReformRegime {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank.");
        }
        Values.requireRange("disclosureStrength", disclosureStrength, 0.0, 1.0);
        Values.requireRange("realTimeDisclosure", realTimeDisclosure, 0.0, 1.0);
        Values.requireRange("beneficialOwnerDisclosure", beneficialOwnerDisclosure, 0.0, 1.0);
        Values.requireRange("contactLogCoverage", contactLogCoverage, 0.0, 1.0);
        Values.requireRange("lobbyingBanStrength", lobbyingBanStrength, 0.0, 1.0);
        Values.requireRange("coolingOffStrength", coolingOffStrength, 0.0, 1.0);
        Values.requireRange("publicFinancingStrength", publicFinancingStrength, 0.0, 1.0);
        Values.requireRange("democracyVoucherStrength", democracyVoucherStrength, 0.0, 1.0);
        Values.requireRange("contributionLimitStrength", contributionLimitStrength, 0.0, 1.0);
        Values.requireRange("darkMoneyDisclosureStrength", darkMoneyDisclosureStrength, 0.0, 1.0);
        Values.requireRange("publicAdvocateStrength", publicAdvocateStrength, 0.0, 1.0);
        Values.requireRange("blindReviewStrength", blindReviewStrength, 0.0, 1.0);
        Values.requireRange("antiAstroturfStrength", antiAstroturfStrength, 0.0, 1.0);
        Values.requireRange("enforcementBudget", enforcementBudget, 0.0, 1.0);
        Values.requireRange("auditRate", auditRate, 0.0, 1.0);
        Values.requireRange("sanctionSeverity", sanctionSeverity, 0.0, 1.0);
        Values.requireRange("appealsDelay", appealsDelay, 0.0, 1.0);
        Values.requireRange("defensiveCapShare", defensiveCapShare, 0.0, 1.0);
        Values.requireRange("administrativeCost", administrativeCost, 0.0, 1.0);
        Values.requireRange("falsePositiveCost", falsePositiveCost, 0.0, 1.0);
        Values.requireRange("constitutionalChallengeRisk", constitutionalChallengeRisk, 0.0, 1.0);
    }

    public double transparencyStrength() {
        return Values.clamp((0.45 * disclosureStrength) + (0.25 * realTimeDisclosure)
                + (0.20 * beneficialOwnerDisclosure) + (0.10 * contactLogCoverage), 0.0, 1.0);
    }

    public double campaignFinanceCounterweight() {
        return Values.clamp((0.34 * publicFinancingStrength) + (0.34 * democracyVoucherStrength)
                + (0.22 * contributionLimitStrength) + (0.10 * darkMoneyDisclosureStrength), 0.0, 1.0);
    }

    public double enforcementStrength() {
        return Values.clamp((0.34 * enforcementBudget) + (0.33 * auditRate) + (0.33 * sanctionSeverity), 0.0, 1.0);
    }

    public double reformProtectionStrength() {
        return Values.clamp((0.22 * transparencyStrength()) + (0.18 * campaignFinanceCounterweight())
                + (0.18 * publicAdvocateStrength) + (0.15 * blindReviewStrength)
                + (0.14 * enforcementStrength()) + (0.08 * antiAstroturfStrength)
                + (0.05 * coolingOffStrength), 0.0, 1.0);
    }

    public static ReformRegime minimalDisclosure() {
        return new ReformRegime(
                "minimal disclosure",
                0.18, 0.05, 0.04, 0.10, 0.00, 0.00, 0.00, 0.00, 0.08, 0.04,
                0.06, 0.00, 0.04, 0.12, 0.08, 0.12, 0.06, 1.00, 0.05, 0.02, 0.05
        );
    }

    public static ReformRegime realTimeTransparency() {
        return new ReformRegime(
                "real-time transparency",
                0.76, 0.84, 0.58, 0.72, 0.06, 0.08, 0.04, 0.02, 0.16, 0.50,
                0.22, 0.12, 0.24, 0.34, 0.30, 0.34, 0.12, 0.55, 0.20, 0.05, 0.12
        );
    }

    public static ReformRegime democracyVouchers() {
        return new ReformRegime(
                "public financing and vouchers",
                0.42, 0.32, 0.28, 0.30, 0.06, 0.08, 0.66, 0.72, 0.42, 0.28,
                0.24, 0.10, 0.18, 0.30, 0.24, 0.30, 0.12, 0.70, 0.24, 0.05, 0.14
        );
    }

    public static ReformRegime coolingOffBan() {
        return new ReformRegime(
                "cooling-off and access limits",
                0.48, 0.34, 0.32, 0.58, 0.38, 0.78, 0.06, 0.03, 0.18, 0.28,
                0.28, 0.28, 0.16, 0.36, 0.34, 0.42, 0.18, 0.50, 0.28, 0.08, 0.22
        );
    }

    public static ReformRegime auditAndSanctions() {
        return new ReformRegime(
                "audit and sanctions",
                0.45, 0.34, 0.30, 0.44, 0.10, 0.20, 0.08, 0.04, 0.22, 0.34,
                0.32, 0.24, 0.22, 0.70, 0.68, 0.76, 0.22, 0.48, 0.32, 0.08, 0.18
        );
    }

    public static ReformRegime fullBundle() {
        return new ReformRegime(
                "full anti-capture bundle",
                0.82, 0.78, 0.78, 0.76, 0.34, 0.68, 0.62, 0.64, 0.56, 0.74,
                0.72, 0.68, 0.64, 0.72, 0.70, 0.72, 0.24, 0.34, 0.46, 0.10, 0.24
        );
    }

    public ReformRegime withTuning(
            String tunedName,
            double disclosureMultiplier,
            double enforcementMultiplier,
            double publicFinancingMultiplier,
            double coolingOffMultiplier
    ) {
        return new ReformRegime(
                tunedName,
                scale(disclosureStrength, disclosureMultiplier),
                scale(realTimeDisclosure, disclosureMultiplier),
                scale(beneficialOwnerDisclosure, disclosureMultiplier),
                scale(contactLogCoverage, disclosureMultiplier),
                lobbyingBanStrength,
                scale(coolingOffStrength, coolingOffMultiplier),
                scale(publicFinancingStrength, publicFinancingMultiplier),
                scale(democracyVoucherStrength, publicFinancingMultiplier),
                scale(contributionLimitStrength, publicFinancingMultiplier),
                scale(darkMoneyDisclosureStrength, disclosureMultiplier),
                publicAdvocateStrength,
                blindReviewStrength,
                antiAstroturfStrength,
                scale(enforcementBudget, enforcementMultiplier),
                scale(auditRate, enforcementMultiplier),
                scale(sanctionSeverity, enforcementMultiplier),
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, Math.max(
                        Math.max(disclosureMultiplier, enforcementMultiplier),
                        Math.max(publicFinancingMultiplier, coolingOffMultiplier)
                )),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    public ReformRegime withoutEnforcement(String tunedName) {
        return new ReformRegime(
                tunedName,
                disclosureStrength,
                realTimeDisclosure,
                beneficialOwnerDisclosure,
                contactLogCoverage,
                lobbyingBanStrength,
                coolingOffStrength,
                publicFinancingStrength,
                democracyVoucherStrength,
                contributionLimitStrength,
                darkMoneyDisclosureStrength,
                publicAdvocateStrength,
                blindReviewStrength,
                antiAstroturfStrength,
                0.0,
                0.0,
                0.0,
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, 0.76),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    public ReformRegime withoutBeneficialOwnerDisclosure(String tunedName) {
        return new ReformRegime(
                tunedName,
                disclosureStrength,
                realTimeDisclosure,
                0.0,
                contactLogCoverage,
                lobbyingBanStrength,
                coolingOffStrength,
                publicFinancingStrength,
                democracyVoucherStrength,
                contributionLimitStrength,
                0.0,
                publicAdvocateStrength,
                blindReviewStrength,
                antiAstroturfStrength,
                enforcementBudget,
                auditRate,
                sanctionSeverity,
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, 0.88),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    public ReformRegime withoutPublicFinancing(String tunedName) {
        return new ReformRegime(
                tunedName,
                disclosureStrength,
                realTimeDisclosure,
                beneficialOwnerDisclosure,
                contactLogCoverage,
                lobbyingBanStrength,
                coolingOffStrength,
                0.0,
                0.0,
                contributionLimitStrength,
                darkMoneyDisclosureStrength,
                publicAdvocateStrength,
                blindReviewStrength,
                antiAstroturfStrength,
                enforcementBudget,
                auditRate,
                sanctionSeverity,
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, 0.84),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    public ReformRegime withoutCoolingOff(String tunedName) {
        return new ReformRegime(
                tunedName,
                disclosureStrength,
                realTimeDisclosure,
                beneficialOwnerDisclosure,
                contactLogCoverage,
                lobbyingBanStrength,
                0.0,
                publicFinancingStrength,
                democracyVoucherStrength,
                contributionLimitStrength,
                darkMoneyDisclosureStrength,
                publicAdvocateStrength,
                blindReviewStrength,
                antiAstroturfStrength,
                enforcementBudget,
                auditRate,
                sanctionSeverity,
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, 0.90),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    public ReformRegime withoutAntiAstroturf(String tunedName) {
        return new ReformRegime(
                tunedName,
                disclosureStrength,
                realTimeDisclosure,
                beneficialOwnerDisclosure,
                contactLogCoverage,
                lobbyingBanStrength,
                coolingOffStrength,
                publicFinancingStrength,
                democracyVoucherStrength,
                contributionLimitStrength,
                darkMoneyDisclosureStrength,
                publicAdvocateStrength,
                blindReviewStrength,
                0.0,
                enforcementBudget,
                auditRate,
                sanctionSeverity,
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, 0.92),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    public ReformRegime withoutPublicAdvocateAndBlindReview(String tunedName) {
        return new ReformRegime(
                tunedName,
                disclosureStrength,
                realTimeDisclosure,
                beneficialOwnerDisclosure,
                contactLogCoverage,
                lobbyingBanStrength,
                coolingOffStrength,
                publicFinancingStrength,
                democracyVoucherStrength,
                contributionLimitStrength,
                darkMoneyDisclosureStrength,
                0.0,
                0.0,
                antiAstroturfStrength,
                enforcementBudget,
                auditRate,
                sanctionSeverity,
                appealsDelay,
                defensiveCapShare,
                scale(administrativeCost, 0.82),
                falsePositiveCost,
                constitutionalChallengeRisk
        );
    }

    private static double scale(double value, double multiplier) {
        return Values.clamp(value * multiplier, 0.0, 1.0);
    }
}
