package lobbycapture.policy;

import lobbycapture.reform.ReformRegime;
import lobbycapture.util.Values;

public final class CommentTriageModel {
    private CommentTriageModel() {
    }

    public static CommentTriageReport triage(
            Docket docket,
            PolicyContest contest,
            ReformRegime reform,
            double reviewCapacity
    ) {
        int totalComments = docket.totalComments();
        if (totalComments == 0) {
            return new CommentTriageReport(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
        }
        double total = totalComments;
        double genuineShare = docket.genuineComments() / total;
        double templateShare = docket.templateComments() / total;
        double astroturfShare = docket.astroturfComments() / total;
        double saturation = docket.templateSaturation();
        double authentication = Values.clamp(
                0.28
                        + (0.42 * docket.authenticationShare())
                        + (0.20 * genuineShare)
                        + (0.06 * reform.realTimeDisclosure())
                        + (0.05 * reform.antiAstroturfStrength())
                        - (0.10 * astroturfShare),
                0.0,
                1.0
        );
        double dedupeTooling = Values.clamp(
                0.25
                        + (0.45 * reform.antiAstroturfStrength())
                        + (0.20 * reform.blindReviewStrength())
                        + (0.16 * reform.publicAdvocateStrength())
                        + (0.14 * reform.enforcementStrength()),
                0.0,
                1.0
        );
        double duplicateCompression = Values.clamp(
                (saturation * (0.82 + (0.52 * dedupeTooling)))
                        + (astroturfShare * reform.antiAstroturfStrength() * 0.34),
                0.0,
                1.0
        );
        double uniqueInformation = Values.clamp(
                (genuineShare * (0.07 + (0.25 * docket.technicalClaimCredibility())))
                        + (templateShare * 0.006)
                        + (Math.max(0.0, 1.0 - saturation) * 0.020)
                        - (astroturfShare * 0.095),
                0.0,
                1.0
        );
        double organizedTechnicalShare = Values.clamp(
                0.24
                        + (0.38 * contest.technicalComplexity())
                        + (0.28 * docket.technicalClaimCredibility())
                        - (0.12 * contest.salience()),
                0.0,
                1.0
        );
        double effectiveReviewLoad = total * (1.0 - (0.76 * duplicateCompression));
        double capacity = 40.0 + (540.0 * Values.clamp(reviewCapacity, 0.0, 1.0));
        double reviewBurden = Values.clamp(effectiveReviewLoad / Math.max(capacity, effectiveReviewLoad), 0.0, 1.0);
        double proceduralAck = Values.clamp(
                0.46
                        + (0.22 * contest.salience())
                        + (0.18 * duplicateCompression)
                        + (0.10 * reform.realTimeDisclosure()),
                0.0,
                1.0
        );
        double substantiveUptake = Values.clamp(
                (0.48 * uniqueInformation)
                        + (0.22 * organizedTechnicalShare)
                        + (0.18 * docket.technicalClaimCredibility())
                        + (0.10 * reform.blindReviewStrength())
                        - (0.30 * reviewBurden)
                        - (0.10 * astroturfShare),
                0.0,
                1.0
        );
        double effectiveInformationWeight = Values.clamp(
                (0.52 * uniqueInformation)
                        + (0.30 * substantiveUptake)
                        + (0.18 * docket.technicalClaimCredibility())
                        - (0.20 * reviewBurden),
                0.0,
                1.0
        );
        double recordDistortion = Values.clamp(
                (0.38 * templateShare)
                        + (0.54 * astroturfShare)
                        + (0.24 * (1.0 - authentication))
                        + (0.14 * reviewBurden)
                        - (0.25 * duplicateCompression),
                0.0,
                1.0
        );
        return new CommentTriageReport(
                uniqueInformation,
                organizedTechnicalShare,
                duplicateCompression,
                reviewBurden,
                proceduralAck,
                substantiveUptake,
                effectiveInformationWeight,
                recordDistortion,
                authentication
        );
    }
}
