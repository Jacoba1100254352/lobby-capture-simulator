package lobbycapture.strategy;

import lobbycapture.util.Values;

public record SubstitutionProfile(
        InfluenceStrategy selectedStrategy,
        double substitutionPressure,
        double suppressedActivityShare,
        double activatedSubstituteShare,
        double influencePreservationRate,
        double hiddenInfluenceShare,
        double netTransparencyGain,
        double messengerSubstitutionRate,
        double venueSubstitutionRate
) {
    public SubstitutionProfile {
        if (selectedStrategy == null) {
            throw new IllegalArgumentException("selectedStrategy must not be null.");
        }
        Values.requireRange("substitutionPressure", substitutionPressure, 0.0, 1.0);
        Values.requireRange("suppressedActivityShare", suppressedActivityShare, 0.0, 1.0);
        Values.requireRange("activatedSubstituteShare", activatedSubstituteShare, 0.0, 1.0);
        Values.requireRange("influencePreservationRate", influencePreservationRate, 0.0, 1.0);
        Values.requireRange("hiddenInfluenceShare", hiddenInfluenceShare, 0.0, 1.0);
        Values.requireRange("netTransparencyGain", netTransparencyGain, -1.0, 1.0);
        Values.requireRange("messengerSubstitutionRate", messengerSubstitutionRate, 0.0, 1.0);
        Values.requireRange("venueSubstitutionRate", venueSubstitutionRate, 0.0, 1.0);
    }

    public static SubstitutionProfile none(InfluenceStrategy strategy) {
        return new SubstitutionProfile(strategy, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    }
}
