package lobbycapture.strategy;

import lobbycapture.util.Values;

public record EvasionProfile(
        double tradeAssociationShift,
        double nonprofitDarkPoolShift,
        double litigationFundingShift,
        double procurementConsultantShift,
        double revolvingDoorPlacementShift,
        double legalRisk,
        double disclosureLag
) {
    public EvasionProfile {
        Values.requireRange("tradeAssociationShift", tradeAssociationShift, 0.0, 1.0);
        Values.requireRange("nonprofitDarkPoolShift", nonprofitDarkPoolShift, 0.0, 1.0);
        Values.requireRange("litigationFundingShift", litigationFundingShift, 0.0, 1.0);
        Values.requireRange("procurementConsultantShift", procurementConsultantShift, 0.0, 1.0);
        Values.requireRange("revolvingDoorPlacementShift", revolvingDoorPlacementShift, 0.0, 1.0);
        Values.requireRange("legalRisk", legalRisk, 0.0, 1.0);
        Values.requireRange("disclosureLag", disclosureLag, 0.0, 1.0);
    }

    public static EvasionProfile low() {
        return new EvasionProfile(0.08, 0.06, 0.04, 0.04, 0.05, 0.12, 0.28);
    }

    public static EvasionProfile moderate() {
        return new EvasionProfile(0.24, 0.24, 0.16, 0.12, 0.18, 0.28, 0.48);
    }

    public static EvasionProfile high() {
        return new EvasionProfile(0.44, 0.56, 0.32, 0.28, 0.36, 0.46, 0.72);
    }

    public double opacity() {
        return Values.clamp((0.28 * tradeAssociationShift) + (0.34 * nonprofitDarkPoolShift)
                + (0.14 * litigationFundingShift) + (0.10 * procurementConsultantShift)
                + (0.14 * revolvingDoorPlacementShift), 0.0, 1.0);
    }
}

