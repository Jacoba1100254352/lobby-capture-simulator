package lobbycapture.simulation;

import lobbycapture.actor.Candidate;
import lobbycapture.actor.EnforcementAgency;
import lobbycapture.actor.InterestClient;
import lobbycapture.actor.LobbyOrganization;
import lobbycapture.actor.PublicOfficial;
import lobbycapture.actor.Regulator;
import lobbycapture.actor.WatchdogGroup;
import lobbycapture.calibration.CalibrationDataLoader;
import lobbycapture.calibration.CalibrationProfile;
import lobbycapture.policy.ContestArena;
import lobbycapture.policy.PolicyContest;
import lobbycapture.reform.ReformRegime;
import lobbycapture.strategy.EvasionProfile;
import lobbycapture.strategy.InfluenceStrategy;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class ScenarioCatalog {
    private static CalibrationProfile cachedCalibration;

    private ScenarioCatalog() {
    }

    public static List<Scenario> all() {
        return List.of(
                scenario("open-access-lobbying", "Open access lobbying", "Weak disclosure and broad access.", ReformRegime.minimalDisclosure(), InfluenceStrategy.BALANCED, 0.00, false, standardContests()),
                scenario("budgeted-disclosed-lobbying", "Budgeted disclosed lobbying", "Finite budgets with ordinary disclosure.", ReformRegime.realTimeTransparency(), InfluenceStrategy.BALANCED, 0.10, true, standardContests()),
                scenario("low-salience-technical-rulemaking", "Low-salience technical rulemaking", "Rulemaking with high information asymmetry and weak public attention.", ReformRegime.minimalDisclosure(), InfluenceStrategy.INFORMATION_DISTORTION, 0.15, true, rulemakingContests()),
                scenario("campaign-finance-dominant", "Campaign finance dominant", "Influence mainly flows through campaigns and outside spending.", ReformRegime.minimalDisclosure(), InfluenceStrategy.CAMPAIGN_FINANCE, 0.20, true, electionContests()),
                scenario("dark-money-dominant", "Dark money dominant", "Opaque intermediaries dominate public and campaign pressure.", ReformRegime.minimalDisclosure(), InfluenceStrategy.DARK_MONEY, 0.75, true, standardContests()),
                scenario("revolving-door-dominant", "Revolving-door dominant", "Access networks and future-employment incentives dominate.", ReformRegime.minimalDisclosure(), InfluenceStrategy.REVOLVING_DOOR, 0.20, true, agencyContests()),
                scenario("real-time-transparency", "Real-time transparency", "Contact logs and rapid disclosure are strong, but other controls are moderate.", ReformRegime.realTimeTransparency(), InfluenceStrategy.BALANCED, 0.35, true, standardContests()),
                scenario("democracy-vouchers", "Democracy vouchers", "Public financing and vouchers reduce donor dependence.", ReformRegime.democracyVouchers(), InfluenceStrategy.CAMPAIGN_FINANCE, 0.30, true, electionAndReformContests()),
                scenario("cooling-off-ban", "Cooling-off ban", "Revolving-door access is restricted.", ReformRegime.coolingOffBan(), InfluenceStrategy.REVOLVING_DOOR, 0.30, true, agencyContests()),
                scenario("audit-and-sanctions", "Audit and sanctions", "Risk-weighted enforcement targets capture attempts.", ReformRegime.auditAndSanctions(), InfluenceStrategy.BALANCED, 0.25, true, standardContests()),
                scenario("full-anti-capture-bundle", "Full anti-capture bundle", "Transparency, enforcement, public financing, blind review, public advocate, anti-astroturf systems, and cooling-off controls.", ReformRegime.fullBundle(), InfluenceStrategy.BALANCED, 0.35, true, reformHeavyContests()),
                scenario("bundle-with-evasion", "Anti-capture bundle with evasion", "Strong reform bundle plus high ability to shift toward darker channels.", ReformRegime.fullBundle(), InfluenceStrategy.BALANCED, 0.90, true, reformHeavyContests()),
                scenario("reform-threat-mobilization", "Reform threat mobilization", "High-salience reform proposals trigger adaptive defensive spending by affected interests.", ReformRegime.realTimeTransparency(), InfluenceStrategy.DIRECT_ACCESS, 0.50, true, reformHeavyContests())
        );
    }

    public static Scenario require(String key) {
        return all().stream()
                .filter(scenario -> scenario.key().equals(key))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unknown scenario: " + key));
    }

    private static Scenario scenario(
            String key,
            String name,
            String description,
            ReformRegime reform,
            InfluenceStrategy initialStrategy,
            double evasionFreedom,
            boolean adaptive,
            List<PolicyContest> contests
    ) {
        CalibrationProfile calibration = calibration();
        return new Scenario(
                key,
                name,
                description,
                new WorldSpec(
                        name,
                        reform,
                        calibration,
                        evasionProfile(evasionFreedom),
                        lobbies(initialStrategy),
                        clients(),
                        officials(),
                        regulators(),
                        watchdogs(),
                        candidates(),
                        enforcementAgencies(reform),
                        contests,
                        0.34,
                        0.42,
                        0.34,
                        evasionFreedom,
                        adaptive
                )
        );
    }

    public static Scenario sensitivityScenario(
            String key,
            String name,
            ReformRegime reform,
            double evasionFreedom,
            InfluenceStrategy initialStrategy
    ) {
        return scenario(key, name, "Sensitivity sweep scenario.", reform, initialStrategy, evasionFreedom, true, reformHeavyContests());
    }

    public static Scenario stressedSensitivityScenario(
            String key,
            String name,
            ReformRegime reform,
            double evasionFreedom,
            InfluenceStrategy initialStrategy
    ) {
        return scenario(
                key,
                name,
                "Sensitivity sweep scenario with high-gain capture opportunities retained in the contest mix.",
                reform,
                initialStrategy,
                evasionFreedom,
                true,
                ablationStressContests()
        );
    }

    public static Scenario ablationScenario(
            String key,
            String name,
            ReformRegime reform,
            double evasionFreedom,
            InfluenceStrategy initialStrategy
    ) {
        return scenario(key, name, "Ablation scenario removing one anti-capture component under a stressed capture mix.", reform, initialStrategy, evasionFreedom, true, ablationStressContests());
    }

    private static List<LobbyOrganization> lobbies(InfluenceStrategy initialStrategy) {
        return List.of(
                lobby("energy-trade", "Energy Trade Council", "energy", Map.of(
                        "energy", 1.00, "rulemaking", 0.72, "procurement", 0.64, "democracy", 0.55
                ), 0.72, 7.0, 3.8, 3.0, 2.6, 2.2, 2.8, 0.86, 0.78, 0.62, 0.62, 0.52, 0.58, 0.64, 0.58, 0.52, 0.88, 2.1, 0.28, 0.42, initialStrategy),
                lobby("platform-coalition", "Digital Platform Coalition", "technology", Map.of(
                        "technology", 1.00, "rulemaking", 0.86, "public-information", 0.72, "democracy", 0.48
                ), 0.58, 5.4, 4.8, 2.2, 2.8, 3.4, 3.9, 0.78, 0.62, 0.86, 0.78, 0.74, 0.76, 0.44, 0.48, 0.70, 0.74, 1.7, 0.22, 0.38, initialStrategy),
                lobby("finance-network", "Financial Markets Network", "finance", Map.of(
                        "finance", 1.00, "election", 0.86, "enforcement", 0.66, "democracy", 0.58
                ), 0.66, 6.2, 5.6, 3.4, 5.8, 1.6, 2.1, 0.84, 0.70, 0.70, 0.58, 0.46, 0.48, 0.56, 0.66, 0.78, 0.82, 2.3, 0.30, 0.46, initialStrategy),
                lobby("contractor-alliance", "Federal Contractor Alliance", "procurement", Map.of(
                        "procurement", 1.00, "enforcement", 0.62, "rulemaking", 0.46, "democracy", 0.42
                ), 0.52, 4.8, 2.4, 2.6, 1.6, 1.2, 1.8, 0.72, 0.74, 0.58, 0.42, 0.38, 0.34, 0.52, 0.80, 0.44, 0.66, 1.6, 0.24, 0.34, initialStrategy)
        );
    }

    private static List<InterestClient> clients() {
        return List.of(
                new InterestClient("energy-producers", "energy", Map.of("energy", 0.86, "rulemaking", 0.74, "democracy", 0.62), 0.88, 0.42, 0.58, 0.54, 0.64, 0.58, 0.42),
                new InterestClient("platform-operators", "technology", Map.of("technology", 0.90, "rulemaking", 0.82, "democracy", 0.55), 0.82, 0.24, 0.46, 0.48, 0.72, 0.70, 0.50),
                new InterestClient("financial-firms", "finance", Map.of("finance", 0.92, "election", 0.84, "democracy", 0.70), 0.74, 0.28, 0.66, 0.42, 0.78, 0.76, 0.46),
                new InterestClient("federal-contractors", "procurement", Map.of("procurement", 0.88, "enforcement", 0.62, "democracy", 0.48), 0.46, 0.86, 0.52, 0.38, 0.58, 0.44, 0.34)
        );
    }

    private static EvasionProfile evasionProfile(double evasionFreedom) {
        if (evasionFreedom >= 0.70) {
            return EvasionProfile.high();
        }
        if (evasionFreedom >= 0.25) {
            return EvasionProfile.moderate();
        }
        return EvasionProfile.low();
    }

    private static LobbyOrganization lobby(
            String id,
            String name,
            String sector,
            Map<String, Double> preferences,
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
        return new LobbyOrganization(
                id,
                name,
                sector,
                preferences,
                preferredPolicyPosition,
                disclosedBudget,
                darkMoneyBudget,
                legalBudget,
                campaignBudget,
                grassrootsBudget,
                researchBudget,
                influenceIntensity,
                accessCapital,
                technicalExpertise,
                publicCampaignSkill,
                informationBias,
                astroturfSkill,
                litigationThreatSkill,
                revolvingDoorNetworkStrength,
                disclosureAvoidanceSkill,
                reformThreatSensitivity,
                defensiveMultiplier,
                publicSupportMismatchTolerance,
                backlashSensitivity,
                initialStrategy
        );
    }

    private static List<PublicOfficial> officials() {
        return List.of(
                new PublicOfficial("senior-legislator", "legislator", "congress", 0.24, 0.56, 0.48, 0.44, 0.42, 0.54, 0.50, 0.52, 0.58),
                new PublicOfficial("agency-lead", "agency leader", "agency", 0.08, 0.32, 0.72, 0.42, 0.60, 0.50, 0.58, 0.56, 0.52)
        );
    }

    private static List<Regulator> regulators() {
        return List.of(
                new Regulator("market-agency", "finance", 0.62, 0.54, 0.44, 0.72, 0.48, 0.42, 0.58, 0.52, 0.56),
                new Regulator("safety-agency", "energy", 0.70, 0.58, 0.46, 0.68, 0.52, 0.44, 0.52, 0.46, 0.50)
        );
    }

    private static List<WatchdogGroup> watchdogs() {
        return List.of(
                new WatchdogGroup("public-integrity-watch", 0.62, 0.58, 0.66),
                new WatchdogGroup("rulemaking-transparency-project", 0.54, 0.46, 0.58)
        );
    }

    private static List<Candidate> candidates() {
        return List.of(
                new Candidate("incumbent-a", "house", 0.18, true, 0.28, 0.68, 0.18, 0.62, 0.56),
                new Candidate("challenger-b", "house", -0.10, false, 0.46, 0.42, 0.34, 0.52, 0.34)
        );
    }

    private static List<EnforcementAgency> enforcementAgencies(ReformRegime reform) {
        return List.of(new EnforcementAgency(
                "integrity-office",
                "lobbying and campaign finance",
                0.58,
                reform.enforcementBudget(),
                0.52,
                reform.auditRate(),
                0.62,
                reform.enforcementStrength(),
                reform.sanctionSeverity(),
                0.28,
                0.22
        ));
    }

    private static List<PolicyContest> standardContests() {
        List<PolicyContest> contests = new ArrayList<>();
        contests.addAll(rulemakingContests());
        contests.addAll(electionContests());
        contests.addAll(agencyContests());
        contests.add(procurementContest());
        contests.add(antiCaptureDisclosure());
        return List.copyOf(contests);
    }

    private static List<PolicyContest> rulemakingContests() {
        return List.of(
                contest("tech-data-rule", "Platform data access rule", "technology", ContestArena.RULEMAKING, false, 0.62, 0.50, 0.64, 0.72, 0.46, 0.86, 0.38),
                contest("energy-safety-rule", "Energy safety standard update", "energy", ContestArena.RULEMAKING, false, 0.68, 0.54, 0.66, 0.70, 0.52, 0.78, 0.42),
                contest("financial-capital-guidance", "Capital guidance revision", "finance", ContestArena.RULEMAKING, false, 0.52, 0.46, 0.58, 0.76, 0.44, 0.82, 0.32)
        );
    }

    private static List<PolicyContest> electionContests() {
        return List.of(
                contest("outside-spending-election", "Outside spending race", "election", ContestArena.ELECTION, false, 0.42, 0.44, 0.50, 0.72, 0.40, 0.34, 0.78),
                contest("campaign-access-pressure", "Fundraising access pressure", "finance", ContestArena.ELECTION, false, 0.45, 0.42, 0.48, 0.68, 0.38, 0.38, 0.70)
        );
    }

    private static List<PolicyContest> agencyContests() {
        return List.of(
                contest("enforcement-priority", "Enforcement priority guidance", "enforcement", ContestArena.ENFORCEMENT, false, 0.56, 0.48, 0.60, 0.68, 0.50, 0.70, 0.34),
                contest("industry-staffing-rule", "Industry staffing and advisory access", "rulemaking", ContestArena.RULEMAKING, false, 0.50, 0.44, 0.56, 0.64, 0.42, 0.72, 0.30)
        );
    }

    private static PolicyContest procurementContest() {
        return contest("procurement-spec", "Procurement specification design", "procurement", ContestArena.PROCUREMENT, false, 0.48, 0.40, 0.46, 0.78, 0.56, 0.56, 0.30);
    }

    private static List<PolicyContest> electionAndReformContests() {
        List<PolicyContest> contests = new ArrayList<>();
        contests.addAll(electionContests());
        contests.add(antiCaptureVouchers());
        contests.add(antiCaptureDisclosure());
        contests.add(antiDarkMoneyDisclosure());
        return List.copyOf(contests);
    }

    private static List<PolicyContest> reformHeavyContests() {
        List<PolicyContest> contests = new ArrayList<>();
        contests.addAll(standardContests());
        contests.add(antiCaptureVouchers());
        contests.add(antiCoolingOff());
        contests.add(antiDarkMoneyDisclosure());
        contests.add(antiAstroturfAuth());
        return List.copyOf(contests);
    }

    private static List<PolicyContest> ablationStressContests() {
        List<PolicyContest> contests = new ArrayList<>();
        contests.addAll(reformHeavyContests());
        contests.add(contest("stress-dark-money-rule", "High-gain opaque platform rule", "technology", ContestArena.RULEMAKING, false, 0.50, 0.38, 0.58, 0.96, 0.72, 0.90, 0.28));
        contests.add(contest("stress-procurement-award", "High-value procurement specification", "procurement", ContestArena.PROCUREMENT, false, 0.44, 0.36, 0.52, 0.94, 0.76, 0.72, 0.30));
        contests.add(contest("stress-campaign-access", "Large-donor access election", "finance", ContestArena.ELECTION, false, 0.42, 0.34, 0.50, 0.92, 0.70, 0.48, 0.64));
        contests.add(contest("stress-enforcement-forbearance", "High-stakes enforcement forbearance", "enforcement", ContestArena.ENFORCEMENT, false, 0.46, 0.34, 0.56, 0.95, 0.78, 0.76, 0.34));
        contests.add(contest("stress-public-information", "Public-information distortion campaign", "public-information", ContestArena.PUBLIC_INFORMATION, false, 0.48, 0.32, 0.58, 0.88, 0.68, 0.62, 0.42));
        return List.copyOf(contests);
    }

    private static PolicyContest antiCaptureDisclosure() {
        return contest("real-time-disclosure-reform", "Real-time lobbying disclosure", "democracy", ContestArena.LEGISLATIVE, true, 0.78, 0.66, 0.72, 0.14, 0.06, 0.50, 0.72);
    }

    private static PolicyContest antiCaptureVouchers() {
        return contest("voucher-reform", "Democracy voucher public financing", "democracy", ContestArena.ELECTION, true, 0.74, 0.62, 0.68, 0.16, 0.05, 0.46, 0.70);
    }

    private static PolicyContest antiCoolingOff() {
        return contest("cooling-off-reform", "Covered official cooling-off period", "democracy", ContestArena.ENFORCEMENT, true, 0.72, 0.58, 0.66, 0.12, 0.04, 0.42, 0.62);
    }

    private static PolicyContest antiDarkMoneyDisclosure() {
        return contest("dark-money-disclosure", "Beneficial-owner dark-money disclosure", "democracy", ContestArena.LEGISLATIVE, true, 0.80, 0.64, 0.72, 0.13, 0.05, 0.52, 0.76);
    }

    private static PolicyContest antiAstroturfAuth() {
        return contest("comment-authentication", "Public comment authentication", "democracy", ContestArena.RULEMAKING, true, 0.70, 0.56, 0.64, 0.10, 0.04, 0.58, 0.60);
    }

    private static PolicyContest contest(
            String id,
            String title,
            String domain,
            ContestArena arena,
            boolean antiCapture,
            double publicBenefit,
            double perceivedSupport,
            double trueSupport,
            double privateGain,
            double harm,
            double complexity,
            double salience
    ) {
        return PolicyContest.of(id, title, domain, arena, antiCapture, publicBenefit, perceivedSupport, trueSupport, privateGain, harm, complexity, salience)
                .withDocket(calibration().docketFor(domain));
    }

    private static synchronized CalibrationProfile calibration() {
        if (cachedCalibration == null) {
            cachedCalibration = CalibrationDataLoader.loadOrEmbedded(Path.of("data", "raw"));
        }
        return cachedCalibration;
    }
}
