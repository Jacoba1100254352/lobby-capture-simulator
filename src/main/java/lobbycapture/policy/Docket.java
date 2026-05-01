package lobbycapture.policy;

import lobbycapture.util.Values;

public record Docket(
        String id,
        String issueDomain,
        String agencyId,
        int genuineComments,
        int templateComments,
        int astroturfComments,
        double technicalClaimCredibility,
        double authenticationShare
) {
    public Docket {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("id must not be blank.");
        }
        if (issueDomain == null || issueDomain.isBlank()) {
            throw new IllegalArgumentException("issueDomain must not be blank.");
        }
        if (agencyId == null || agencyId.isBlank()) {
            throw new IllegalArgumentException("agencyId must not be blank.");
        }
        if (genuineComments < 0 || templateComments < 0 || astroturfComments < 0) {
            throw new IllegalArgumentException("comment counts must not be negative.");
        }
        Values.requireRange("technicalClaimCredibility", technicalClaimCredibility, 0.0, 1.0);
        Values.requireRange("authenticationShare", authenticationShare, 0.0, 1.0);
    }

    public static Docket empty(String issueDomain) {
        return new Docket("synthetic-" + issueDomain, issueDomain, "synthetic-agency", 80, 10, 10, 0.60, 0.50);
    }

    public int totalComments() {
        return genuineComments + templateComments + astroturfComments;
    }

    public double authenticityShare() {
        int total = totalComments();
        return total == 0 ? 0.0 : Values.clamp((genuineComments * authenticationShare) / total, 0.0, 1.0);
    }

    public double templateSaturation() {
        int total = totalComments();
        return total == 0 ? 0.0 : (double) (templateComments + astroturfComments) / total;
    }

    public Docket withCampaign(CommentCampaign campaign) {
        int updatedGenuine = genuineComments + campaign.genuineComments();
        int updatedTemplate = templateComments + campaign.templateComments();
        int updatedAstroturf = astroturfComments + campaign.astroturfComments();
        double total = Math.max(1.0, campaign.genuineComments() + campaign.templateComments() + campaign.astroturfComments());
        double campaignCredibility = ((campaign.genuineComments() * 0.72)
                + (campaign.templateComments() * 0.42)
                + (campaign.astroturfComments() * campaign.technicalCredibility())) / total;
        double credibility = Values.clamp((0.82 * technicalClaimCredibility) + (0.18 * campaignCredibility), 0.0, 1.0);
        double authentication = Values.clamp((0.86 * authenticationShare) + (0.14 * campaign.authenticationShare()), 0.0, 1.0);
        return new Docket(id, issueDomain, agencyId, updatedGenuine, updatedTemplate, updatedAstroturf, credibility, authentication);
    }
}

