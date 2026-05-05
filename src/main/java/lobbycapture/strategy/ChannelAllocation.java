package lobbycapture.strategy;

import lobbycapture.util.Values;

public record ChannelAllocation(
        double directAccess,
        double agendaAccess,
        double informationDistortion,
        double publicCampaign,
        double litigationThreat,
        double campaignFinance,
        double darkMoney,
        double revolvingDoor,
        double intermediary,
        double defensiveReform
) {
    public ChannelAllocation {
        Values.requireRange("directAccess", directAccess, 0.0, 1_000_000.0);
        Values.requireRange("agendaAccess", agendaAccess, 0.0, 1_000_000.0);
        Values.requireRange("informationDistortion", informationDistortion, 0.0, 1_000_000.0);
        Values.requireRange("publicCampaign", publicCampaign, 0.0, 1_000_000.0);
        Values.requireRange("litigationThreat", litigationThreat, 0.0, 1_000_000.0);
        Values.requireRange("campaignFinance", campaignFinance, 0.0, 1_000_000.0);
        Values.requireRange("darkMoney", darkMoney, 0.0, 1_000_000.0);
        Values.requireRange("revolvingDoor", revolvingDoor, 0.0, 1_000_000.0);
        Values.requireRange("intermediary", intermediary, 0.0, 1_000_000.0);
        Values.requireRange("defensiveReform", defensiveReform, 0.0, 1_000_000.0);
    }

    public static ChannelAllocation zero() {
        return new ChannelAllocation(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    }

    public static ChannelAllocation forStrategy(InfluenceStrategy strategy, double spend) {
        double[] shares = switch (strategy) {
            case DIRECT_ACCESS -> new double[]{0.45, 0.17, 0.07, 0.05, 0.04, 0.05, 0.03, 0.08, 0.06, 0.00};
            case AGENDA_ACCESS -> new double[]{0.13, 0.45, 0.09, 0.04, 0.07, 0.05, 0.04, 0.08, 0.05, 0.00};
            case INFORMATION_DISTORTION -> new double[]{0.06, 0.09, 0.45, 0.07, 0.04, 0.02, 0.12, 0.05, 0.10, 0.00};
            case PUBLIC_CAMPAIGN -> new double[]{0.05, 0.07, 0.11, 0.43, 0.04, 0.06, 0.12, 0.04, 0.08, 0.00};
            case LITIGATION_THREAT -> new double[]{0.05, 0.09, 0.07, 0.05, 0.49, 0.03, 0.06, 0.09, 0.07, 0.00};
            case CAMPAIGN_FINANCE -> new double[]{0.07, 0.09, 0.04, 0.07, 0.02, 0.48, 0.10, 0.05, 0.08, 0.00};
            case DARK_MONEY -> new double[]{0.04, 0.07, 0.11, 0.13, 0.04, 0.07, 0.40, 0.04, 0.10, 0.00};
            case REVOLVING_DOOR -> new double[]{0.12, 0.10, 0.07, 0.02, 0.05, 0.04, 0.04, 0.45, 0.11, 0.00};
            case INTERMEDIARY -> new double[]{0.05, 0.10, 0.20, 0.18, 0.04, 0.04, 0.22, 0.05, 0.12, 0.00};
            case DEFENSIVE_REFORM -> new double[]{0.07, 0.09, 0.11, 0.18, 0.15, 0.06, 0.11, 0.05, 0.08, 0.10};
            case BALANCED -> new double[]{0.15, 0.13, 0.13, 0.12, 0.09, 0.10, 0.09, 0.11, 0.08, 0.00};
        };
        return new ChannelAllocation(
                spend * shares[0],
                spend * shares[1],
                spend * shares[2],
                spend * shares[3],
                spend * shares[4],
                spend * shares[5],
                spend * shares[6],
                spend * shares[7],
                spend * shares[8],
                spend * shares[9]
        );
    }

    public ChannelAllocation plus(ChannelAllocation other) {
        return new ChannelAllocation(
                directAccess + other.directAccess,
                agendaAccess + other.agendaAccess,
                informationDistortion + other.informationDistortion,
                publicCampaign + other.publicCampaign,
                litigationThreat + other.litigationThreat,
                campaignFinance + other.campaignFinance,
                darkMoney + other.darkMoney,
                revolvingDoor + other.revolvingDoor,
                intermediary + other.intermediary,
                defensiveReform + other.defensiveReform
        );
    }

    public double total() {
        return directAccess + agendaAccess + informationDistortion + publicCampaign + litigationThreat
                + campaignFinance + darkMoney + revolvingDoor + intermediary + defensiveReform;
    }

    public double share(InfluenceChannel channel) {
        double total = total();
        if (total == 0.0) {
            return 0.0;
        }
        return switch (channel) {
            case DIRECT_ACCESS -> directAccess / total;
            case AGENDA_ACCESS -> agendaAccess / total;
            case INFORMATION_DISTORTION -> informationDistortion / total;
            case PUBLIC_CAMPAIGN -> publicCampaign / total;
            case LITIGATION_THREAT -> litigationThreat / total;
            case CAMPAIGN_FINANCE -> campaignFinance / total;
            case DARK_MONEY -> darkMoney / total;
            case REVOLVING_DOOR -> revolvingDoor / total;
            case INTERMEDIARY -> intermediary / total;
            case DEFENSIVE_REFORM -> defensiveReform / total;
        };
    }
}
