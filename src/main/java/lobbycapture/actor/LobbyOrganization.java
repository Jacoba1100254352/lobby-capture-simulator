package lobbycapture.actor;

import lobbycapture.strategy.InfluenceStrategy;
import lobbycapture.util.Values;

import java.util.LinkedHashMap;
import java.util.Map;

public record LobbyOrganization(
        String id,
        String name,
        String sector,
        Map<String, Double> issuePreferences,
        double preferredPolicyPosition,
        double disclosedBudget,
        double darkMoneyBudget,
        double legalBudget,
        double campaignBudget,
        double grassrootsBudget,
        double researchBudget,
        double influenceIntensity,
        double accessCapital,
        double technicalExpertise,
        double publicCampaignSkill,
        double informationBias,
        double astroturfSkill,
        double litigationThreatSkill,
        double revolvingDoorNetworkStrength,
        double disclosureAvoidanceSkill,
        double reformThreatSensitivity,
        double defensiveMultiplier,
        double publicSupportMismatchTolerance,
        double backlashSensitivity,
        InfluenceStrategy initialStrategy
) {
    public LobbyOrganization {
        requireText("id", id);
        requireText("name", name);
        requireText("sector", sector);
        Values.requireRange("preferredPolicyPosition", preferredPolicyPosition, -1.0, 1.0);
        Values.requireRange("disclosedBudget", disclosedBudget, 0.0, 100.0);
        Values.requireRange("darkMoneyBudget", darkMoneyBudget, 0.0, 100.0);
        Values.requireRange("legalBudget", legalBudget, 0.0, 100.0);
        Values.requireRange("campaignBudget", campaignBudget, 0.0, 100.0);
        Values.requireRange("grassrootsBudget", grassrootsBudget, 0.0, 100.0);
        Values.requireRange("researchBudget", researchBudget, 0.0, 100.0);
        Values.requireRange("influenceIntensity", influenceIntensity, 0.0, 1.0);
        Values.requireRange("accessCapital", accessCapital, 0.0, 1.0);
        Values.requireRange("technicalExpertise", technicalExpertise, 0.0, 1.0);
        Values.requireRange("publicCampaignSkill", publicCampaignSkill, 0.0, 1.0);
        Values.requireRange("informationBias", informationBias, 0.0, 1.0);
        Values.requireRange("astroturfSkill", astroturfSkill, 0.0, 1.0);
        Values.requireRange("litigationThreatSkill", litigationThreatSkill, 0.0, 1.0);
        Values.requireRange("revolvingDoorNetworkStrength", revolvingDoorNetworkStrength, 0.0, 1.0);
        Values.requireRange("disclosureAvoidanceSkill", disclosureAvoidanceSkill, 0.0, 1.0);
        Values.requireRange("reformThreatSensitivity", reformThreatSensitivity, 0.0, 1.0);
        Values.requireRange("defensiveMultiplier", defensiveMultiplier, 0.0, 3.0);
        Values.requireRange("publicSupportMismatchTolerance", publicSupportMismatchTolerance, 0.0, 1.0);
        Values.requireRange("backlashSensitivity", backlashSensitivity, 0.0, 1.0);
        if (initialStrategy == null) {
            throw new IllegalArgumentException("initialStrategy must not be null.");
        }
        issuePreferences = normalize(issuePreferences);
    }

    public double totalBudget() {
        return disclosedBudget + darkMoneyBudget + legalBudget + campaignBudget + grassrootsBudget + researchBudget;
    }

    public double preferenceFor(String issueDomain) {
        return issuePreferences.getOrDefault(issueDomain, 0.0);
    }

    private static Map<String, Double> normalize(Map<String, Double> preferences) {
        Map<String, Double> normalized = new LinkedHashMap<>();
        if (preferences != null) {
            for (Map.Entry<String, Double> entry : preferences.entrySet()) {
                if (entry.getKey() == null || entry.getKey().isBlank()) {
                    continue;
                }
                Values.requireRange("issuePreference", entry.getValue(), 0.0, 1.0);
                if (entry.getValue() > 0.0) {
                    normalized.put(entry.getKey(), entry.getValue());
                }
            }
        }
        return Map.copyOf(normalized);
    }

    private static void requireText(String name, String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank.");
        }
    }
}

