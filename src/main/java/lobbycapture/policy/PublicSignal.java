package lobbycapture.policy;

import lobbycapture.util.Values;

public record PublicSignal(
        double truePreference,
        double perceivedPreference,
        double mediaAttention,
        double astroturfShare,
        double misinformationLoad,
        double sourceCredibility
) {
    public PublicSignal {
        Values.requireRange("truePreference", truePreference, 0.0, 1.0);
        Values.requireRange("perceivedPreference", perceivedPreference, 0.0, 1.0);
        Values.requireRange("mediaAttention", mediaAttention, 0.0, 1.0);
        Values.requireRange("astroturfShare", astroturfShare, 0.0, 1.0);
        Values.requireRange("misinformationLoad", misinformationLoad, 0.0, 1.0);
        Values.requireRange("sourceCredibility", sourceCredibility, 0.0, 1.0);
    }
}

