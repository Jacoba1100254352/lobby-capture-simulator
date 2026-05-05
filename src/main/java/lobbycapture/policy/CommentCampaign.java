package lobbycapture.policy;

import lobbycapture.actor.LobbyOrganization;
import lobbycapture.reform.ReformRegime;
import lobbycapture.strategy.ChannelAllocation;
import lobbycapture.util.Values;

public record CommentCampaign(
        String sponsorId,
        int genuineComments,
        int templateComments,
        int astroturfComments,
        double technicalCredibility,
        double authenticationShare
) {
    public static CommentCampaign fromAllocation(
            Docket docket,
            LobbyOrganization sponsor,
            ChannelAllocation allocation,
            ReformRegime reform
    ) {
        double commentSpend = allocation.publicCampaign()
                + allocation.darkMoney()
                + allocation.informationDistortion()
                + (1.18 * allocation.intermediary());
        int generated = (int) Math.round(commentSpend * (18.0 + (sponsor.astroturfSkill() * 36.0)));
        int astroturf = (int) Math.round(generated * sponsor.astroturfSkill() * (1.0 - reform.antiAstroturfStrength()));
        double intermediaryShare = commentSpend == 0.0 ? 0.0 : allocation.intermediary() / commentSpend;
        int template = (int) Math.round(generated * (0.30 + (0.30 * sponsor.informationBias()) + (0.12 * intermediaryShare)));
        int genuine = Math.max(0, generated - astroturf - template);
        double credibility = Values.clamp(
                (0.50 * sponsor.technicalExpertise())
                        + (0.30 * sponsor.informationBias())
                        + (0.20 * docket.technicalClaimCredibility()),
                0.0,
                1.0
        );
        double authentication = Values.clamp(
                docket.authenticationShare()
                        + (0.18 * reform.antiAstroturfStrength())
                        - (0.20 * sponsor.disclosureAvoidanceSkill()),
                0.0,
                1.0
        );
        return new CommentCampaign(sponsor.id(), genuine, template, astroturf, credibility, authentication);
    }

    public double distortion() {
        int total = Math.max(1, genuineComments + templateComments + astroturfComments);
        return Values.clamp(((templateComments * 0.42) + (astroturfComments * 0.78)) / total, 0.0, 1.0);
    }
}
