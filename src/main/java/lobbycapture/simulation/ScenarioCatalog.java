package lobbycapture.simulation;


import lobbycapture.actor.*;
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


public final class ScenarioCatalog
{
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
				scenario("intermediary-substitution", "Think-tank and association intermediaries", "Visible lobbying constraints push influence through sponsored research, associations, and expert messengers.", ReformRegime.realTimeTransparency(), InfluenceStrategy.INTERMEDIARY, 0.70, true, technicalRulemakingContests()),
				scenario("real-time-transparency", "Real-time transparency", "Contact logs and rapid disclosure are strong, but other controls are moderate.", ReformRegime.realTimeTransparency(), InfluenceStrategy.BALANCED, 0.35, true, standardContests()),
				scenario("democracy-vouchers", "Democracy vouchers", "Public financing and vouchers reduce donor dependence.", ReformRegime.democracyVouchers(), InfluenceStrategy.CAMPAIGN_FINANCE, 0.30, true, electionAndReformContests()),
				scenario("cooling-off-ban", "Cooling-off ban", "Revolving-door access is restricted.", ReformRegime.coolingOffBan(), InfluenceStrategy.REVOLVING_DOOR, 0.30, true, agencyContests()),
				scenario("audit-and-sanctions", "Audit and sanctions", "Risk-weighted enforcement targets capture attempts.", ReformRegime.auditAndSanctions(), InfluenceStrategy.BALANCED, 0.25, true, standardContests()),
				scenario("hard-lobbying-budgets", "Hard lobbying budgets", "Strict expenditure caps and access limits test whether influence moves to indirect messengers.", ReformRegime.hardLobbyingBudgets(), InfluenceStrategy.BALANCED, 0.55, true, standardContests()),
				scenario("public-interest-representation-funds", "Public-interest representation funds", "Public-interest advocates and representation funds counter technical and legal asymmetries.", ReformRegime.publicInterestRepresentationFunds(), InfluenceStrategy.INFORMATION_DISTORTION, 0.35, true, technicalRulemakingContests()),
				scenario("randomized-audit-sanctions", "Randomized audit and sanctions", "Randomized audits raise expected evasion costs across channels.", ReformRegime.randomizedAuditSanctions(), InfluenceStrategy.BALANCED, 0.40, true, standardContests()),
				scenario("machine-readable-meeting-logs", "Machine-readable meeting logs", "Real-time structured meeting logs improve visibility of direct and indirect contacts.", ReformRegime.machineReadableMeetingLogs(), InfluenceStrategy.DIRECT_ACCESS, 0.45, true, agencyContests()),
				scenario("hard-budget-substitution-stress", "Hard-budget substitution stress", "Tight visible lobbying budgets with high evasion test whether influence moves through dark, intermediary, procurement, and legal channels.", ReformRegime.hardLobbyingBudgets(), InfluenceStrategy.INTERMEDIARY, 0.88, true, ablationStressContests()),
				scenario("shadow-lobbying-maximum-stress", "Shadow lobbying maximum stress", "Extreme visible-channel constraints test the upper tail of dark-money, association, advisory, and procurement-consultant substitution.", ReformRegime.hardLobbyingBudgets(), InfluenceStrategy.DARK_MONEY, 0.98, true, shadowLobbyingMaxStressContests()),
				scenario("visible-ban-dark-money-leakage", "Visible lobbying ban with dark-money leakage", "A hard visible-lobbying cap is treated as a failure candidate when influence migrates into opaque issue advocacy and outside spending.", ReformRegime.hardLobbyingBudgets(), InfluenceStrategy.DARK_MONEY, 0.96, true, darkMoneyLeakageContests()),
				scenario("opaque-network-substitution-frontier", "Opaque network substitution frontier", "Machine-readable disclosure tests whether influence moves into nonprofit, association, advisory, and venue-shift paths that remain hard to connect.", ReformRegime.machineReadableMeetingLogs(), InfluenceStrategy.INTERMEDIARY, 0.96, true, opaqueNetworkSubstitutionContests()),
				scenario("meeting-log-intermediary-leakage", "Meeting-log intermediary leakage", "Machine-readable meeting logs are stressed against association messengers, sponsored experts, and unofficial advisory routes.", ReformRegime.machineReadableMeetingLogs(), InfluenceStrategy.INTERMEDIARY, 0.92, true, meetingLogIntermediaryLeakageContests()),
				scenario("advisory-lobbying-substitution", "Advisory lobbying substitution", "Cooling-off and access limits test whether activity moves into advisory, expert, and behind-the-scenes messenger channels.", ReformRegime.enforcedCoolingOff(), InfluenceStrategy.REVOLVING_DOOR, 0.84, true, advisorySubstitutionContests()),
				scenario("procurement-venue-shift-stress", "Procurement venue-shift stress", "Procurement firewalls test whether vendor influence moves through consultants, associations, bid specifications, and litigation threats.", ReformRegime.procurementFirewall(), InfluenceStrategy.INTERMEDIARY, 0.86, true, procurementSubstitutionContests()),
				scenario("procurement-modification-capture-frontier", "Procurement modification capture frontier", "Procurement firewalls are stressed against post-award modifications, exclusion language, bid protests, consultants, and subcontract eligibility pressure.", ReformRegime.procurementFirewall(), InfluenceStrategy.INTERMEDIARY, 0.92, true, procurementModificationContests()),
				scenario("outside-spending-disclosure-evasion", "Outside-spending disclosure evasion", "Dark-money disclosure and public financing test whether electoral influence moves into independent expenditures and nonprofit messengers.", ReformRegime.electoralSubstitutionShield(), InfluenceStrategy.DARK_MONEY, 0.90, true, outsideSpendingStressContests()),
				scenario("public-finance-dark-money-frontier", "Public-finance dark-money frontier", "Public financing and vouchers are stressed against independent expenditure, nonprofit issue-ad, and donor-network substitution.", ReformRegime.democracyVouchers(), InfluenceStrategy.DARK_MONEY, 0.94, true, publicFinanceDarkMoneyContests()),
				scenario("public-finance-outside-spending-leakage", "Public-finance outside-spending leakage", "Public financing is treated as incomplete when candidate-side dependence falls but independent expenditure and nonprofit messaging capacity rises.", ReformRegime.democracyVouchers(), InfluenceStrategy.CAMPAIGN_FINANCE, 0.90, true, publicFinanceOutsideSpendingLeakageContests()),
				scenario("enforced-cooling-off", "Enforced cooling-off periods", "Cooling-off rules are paired with audit and sanction capacity.", ReformRegime.enforcedCoolingOff(), InfluenceStrategy.REVOLVING_DOOR, 0.40, true, agencyContests()),
				scenario("comment-authenticity-rules", "Comment-authenticity rules", "Authentication and deduplication target comment flooding and synthetic salience.", ReformRegime.commentAuthenticityRules(), InfluenceStrategy.INTERMEDIARY, 0.50, true, commentFloodingContests()),
				scenario("comment-authenticity-technical-substitution", "Comment-authenticity technical substitution", "Comment-authenticity rules are stressed against sponsored expert filings, technical attachments, and consultant-written unique comments.", ReformRegime.commentAuthenticityRules(), InfluenceStrategy.INFORMATION_DISTORTION, 0.88, true, commentAuthenticitySubstitutionContests()),
				scenario("public-advocate-office", "Public advocate office", "Dedicated public advocates and blind review counter one-sided technical submissions.", ReformRegime.publicAdvocateOffice(), InfluenceStrategy.INFORMATION_DISTORTION, 0.35, true, technicalRulemakingContests()),
				scenario("procurement-firewalls", "Procurement firewalls", "Procurement contact controls, blind review, and sanctions target vendor capture.", ReformRegime.procurementFirewall(), InfluenceStrategy.REVOLVING_DOOR, 0.45, true, procurementContests()),
				scenario("venue-shifting-detection", "Venue-shifting detection", "Transparency and enforcement systems explicitly track movement across venues and messengers.", ReformRegime.venueShiftingDetection(), InfluenceStrategy.INTERMEDIARY, 0.65, true, ablationStressContests()),
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
		return scenario(key, name, description, reform, initialStrategy, evasionFreedom, adaptive, contests, true, false);
	}

	private static Scenario scenario(
			String key,
			String name,
			String description,
			ReformRegime reform,
			InfluenceStrategy initialStrategy,
			double evasionFreedom,
			boolean adaptive,
			List<PolicyContest> contests,
			boolean substitutionEnabled,
			boolean singleChannelVisibleLobbying
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
						adaptive,
						substitutionEnabled,
						singleChannelVisibleLobbying
				)
		);
	}

	public static List<Scenario> mechanismComparison() {
		return List.of(
				scenario(
						"comparison-low-visible-scalar",
						"Low reform: single-channel visible lobbying",
						"Low-reform visible-channel baseline: direct and agenda access only, with substitution disabled.",
						ReformRegime.minimalDisclosure(),
						InfluenceStrategy.DIRECT_ACCESS,
						0.0,
						false,
						standardContests(),
						false,
						true
				),
				scenario(
						"comparison-low-multichannel-no-substitution",
						"Low reform: multi-channel without substitution",
						"Low-reform multi-channel model with reform-triggered substitution and evasion switching disabled.",
						ReformRegime.minimalDisclosure(),
						InfluenceStrategy.BALANCED,
						0.20,
						false,
						standardContests(),
						false,
						false
				),
				scenario(
						"comparison-low-multichannel-substitution",
						"Low reform: multi-channel with substitution",
						"Low-reform multi-channel model with substitution enabled under moderate evasion freedom.",
						ReformRegime.minimalDisclosure(),
						InfluenceStrategy.BALANCED,
						0.35,
						true,
						standardContests(),
						true,
						false
				),
				scenario(
						"comparison-moderate-visible-scalar",
						"Moderate reform: single-channel visible lobbying",
						"Moderate-reform visible-channel baseline: direct and agenda access only, with substitution disabled.",
						ReformRegime.realTimeTransparency(),
						InfluenceStrategy.DIRECT_ACCESS,
						0.0,
						false,
						standardContests(),
						false,
						true
				),
				scenario(
						"comparison-moderate-multichannel-no-substitution",
						"Moderate reform: multi-channel without substitution",
						"Moderate-reform multi-channel model with reform-triggered substitution and evasion switching disabled.",
						ReformRegime.realTimeTransparency(),
						InfluenceStrategy.BALANCED,
						0.45,
						false,
						standardContests(),
						false,
						false
				),
				scenario(
						"comparison-moderate-multichannel-substitution",
						"Moderate reform: multi-channel with substitution",
						"Moderate-reform multi-channel model with substitution enabled.",
						ReformRegime.realTimeTransparency(),
						InfluenceStrategy.BALANCED,
						0.60,
						true,
						standardContests(),
						true,
						false
				),
				scenario(
						"comparison-strong-visible-scalar",
						"Strong reform: single-channel visible lobbying",
						"Strong-reform stress baseline: direct and agenda access only, with substitution disabled.",
						ReformRegime.fullBundle(),
						InfluenceStrategy.DIRECT_ACCESS,
						0.0,
						false,
						reformHeavyContests(),
						false,
						true
				),
				scenario(
						"comparison-strong-multichannel-no-substitution",
						"Strong reform: multi-channel without substitution",
						"Strong-reform stress model with multiple influence channels available but reform-triggered substitution and evasion switching disabled.",
						ReformRegime.fullBundle(),
						InfluenceStrategy.BALANCED,
						0.90,
						false,
						reformHeavyContests(),
						false,
						false
				),
				scenario(
						"comparison-strong-multichannel-substitution",
						"Strong reform: multi-channel with substitution",
						"Strong-reform stress model with multiple influence channels and reform-triggered substitution enabled under high evasion freedom.",
						ReformRegime.fullBundle(),
						InfluenceStrategy.BALANCED,
						0.90,
						true,
						reformHeavyContests(),
						true,
						false
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
	
	private static List<PolicyContest> procurementContests() {
		return List.of(
				procurementContest(),
				contest("procurement-firewall-award", "Firewall-sensitive award specification", "procurement", ContestArena.PROCUREMENT, false, 0.50, 0.34, 0.54, 0.92, 0.76, 0.70, 0.32),
				contest("procurement-subcontract-routing", "Subcontractor eligibility routing", "procurement", ContestArena.PROCUREMENT, false, 0.44, 0.32, 0.50, 0.86, 0.70, 0.62, 0.28),
				antiCoolingOff()
		);
	}
	
	private static List<PolicyContest> procurementSubstitutionContests() {
		return List.of(
				contest("procurement-consultant-routing", "Procurement consultant routing", "procurement", ContestArena.PROCUREMENT, false, 0.44, 0.30, 0.52, 0.96, 0.78, 0.74, 0.28),
				contest("association-written-spec", "Association-written technical specification", "procurement", ContestArena.PROCUREMENT, false, 0.42, 0.32, 0.50, 0.94, 0.76, 0.86, 0.24),
				contest("bid-protest-leverage", "Bid-protest leverage threat", "procurement", ContestArena.LITIGATION, false, 0.38, 0.28, 0.48, 0.92, 0.72, 0.64, 0.22),
				contest("subaward-eligibility-pressure", "Subaward eligibility pressure", "procurement", ContestArena.PROCUREMENT, false, 0.40, 0.30, 0.46, 0.90, 0.70, 0.66, 0.20),
				antiCoolingOff(),
				antiCaptureDisclosure()
		);
	}
	
	private static List<PolicyContest> advisorySubstitutionContests() {
		return List.of(
				contest("advisory-board-routing", "Advisory board access routing", "rulemaking", ContestArena.RULEMAKING, false, 0.48, 0.34, 0.54, 0.88, 0.68, 0.78, 0.24),
				contest("expert-consultant-shadow-lobbying", "Expert consultant shadow lobbying", "technology", ContestArena.PUBLIC_INFORMATION, false, 0.44, 0.30, 0.50, 0.90, 0.70, 0.88, 0.26),
				contest("post-employment-advice-channel", "Post-employment advice channel", "enforcement", ContestArena.ENFORCEMENT, false, 0.42, 0.30, 0.48, 0.92, 0.74, 0.72, 0.18),
				contest("standards-body-venue-shift", "Standards-body venue shift", "rulemaking", ContestArena.RULEMAKING, false, 0.46, 0.32, 0.52, 0.86, 0.66, 0.90, 0.22),
				antiCoolingOff(),
				antiAstroturfAuth()
		);
	}
	
	private static List<PolicyContest> shadowLobbyingMaxStressContests() {
		return List.of(
				contest("maximum-dark-money-routing", "Maximum dark-money routing", "democracy", ContestArena.PUBLIC_INFORMATION, false, 0.38, 0.24, 0.52, 0.98, 0.82, 0.62, 0.84),
				contest("maximum-association-routing", "Maximum association routing", "rulemaking", ContestArena.RULEMAKING, false, 0.40, 0.26, 0.50, 0.96, 0.80, 0.92, 0.28),
				contest("maximum-procurement-consulting", "Maximum procurement consulting", "procurement", ContestArena.PROCUREMENT, false, 0.36, 0.24, 0.48, 0.98, 0.84, 0.82, 0.20),
				contest("maximum-shadow-advisory", "Maximum shadow advisory channel", "enforcement", ContestArena.ENFORCEMENT, false, 0.38, 0.24, 0.46, 0.96, 0.82, 0.78, 0.18),
				antiDarkMoneyDisclosure(),
				antiCoolingOff(),
				antiCaptureDisclosure()
		);
	}

	private static List<PolicyContest> darkMoneyLeakageContests() {
		return List.of(
				contest("ban-leak-nonprofit-issue-ads", "Nonprofit issue-ad leakage after visible lobbying cap", "democracy", ContestArena.PUBLIC_INFORMATION, false, 0.40, 0.24, 0.54, 0.98, 0.82, 0.64, 0.86),
				contest("ban-leak-trade-association-research", "Trade association research leakage after visible lobbying cap", "rulemaking", ContestArena.RULEMAKING, false, 0.42, 0.26, 0.52, 0.96, 0.80, 0.90, 0.30),
				contest("ban-leak-independent-expenditure", "Independent expenditure leakage after visible lobbying cap", "election", ContestArena.ELECTION, false, 0.40, 0.24, 0.50, 0.98, 0.80, 0.42, 0.88),
				contest("ban-leak-litigation-threat", "Litigation threat leakage after visible lobbying cap", "rulemaking", ContestArena.LITIGATION, false, 0.36, 0.22, 0.48, 0.94, 0.76, 0.68, 0.28),
				antiDarkMoneyDisclosure(),
				antiCaptureDisclosure()
		);
	}
	
	private static List<PolicyContest> opaqueNetworkSubstitutionContests() {
		return List.of(
				contest("opaque-nonprofit-research-network", "Opaque nonprofit research network", "technology", ContestArena.PUBLIC_INFORMATION, false, 0.42, 0.28, 0.54, 0.94, 0.76, 0.92, 0.32),
				contest("association-advisory-meeting-gap", "Association advisory meeting gap", "rulemaking", ContestArena.RULEMAKING, false, 0.44, 0.30, 0.52, 0.92, 0.74, 0.88, 0.26),
				contest("funded-expert-venue-shift", "Funded expert venue shift", "public-information", ContestArena.PUBLIC_INFORMATION, false, 0.40, 0.28, 0.50, 0.90, 0.72, 0.94, 0.30),
				contest("machine-log-side-channel", "Machine-log side-channel pressure", "enforcement", ContestArena.ENFORCEMENT, false, 0.42, 0.30, 0.50, 0.88, 0.70, 0.76, 0.24),
				antiDarkMoneyDisclosure(),
				antiAstroturfAuth(),
				antiCaptureDisclosure()
		);
	}

	private static List<PolicyContest> meetingLogIntermediaryLeakageContests() {
		return List.of(
				contest("logged-meeting-association-substitute", "Association substitute for logged meetings", "rulemaking", ContestArena.RULEMAKING, false, 0.42, 0.28, 0.52, 0.94, 0.74, 0.90, 0.28),
				contest("logged-meeting-sponsored-expert", "Sponsored expert outside the meeting log", "technology", ContestArena.PUBLIC_INFORMATION, false, 0.40, 0.28, 0.50, 0.92, 0.72, 0.96, 0.32),
				contest("logged-meeting-advisory-committee-gap", "Advisory committee gap after meeting-log reform", "enforcement", ContestArena.ENFORCEMENT, false, 0.40, 0.28, 0.50, 0.90, 0.70, 0.82, 0.24),
				contest("logged-meeting-procurement-side-channel", "Procurement side channel after meeting-log reform", "procurement", ContestArena.PROCUREMENT, false, 0.38, 0.26, 0.48, 0.92, 0.76, 0.74, 0.22),
				antiAstroturfAuth(),
				antiCaptureDisclosure()
		);
	}
	
	private static List<PolicyContest> outsideSpendingStressContests() {
		return List.of(
				contest("super-pac-independent-expenditure", "Super PAC independent expenditure push", "election", ContestArena.ELECTION, false, 0.42, 0.30, 0.52, 0.94, 0.72, 0.42, 0.80),
				contest("dark-money-public-campaign", "Dark-money public campaign", "democracy", ContestArena.PUBLIC_INFORMATION, false, 0.48, 0.34, 0.58, 0.88, 0.68, 0.56, 0.78),
				contest("nonprofit-issue-ad-blitz", "Nonprofit issue-ad blitz", "democracy", ContestArena.ELECTION, false, 0.46, 0.32, 0.54, 0.90, 0.70, 0.48, 0.82),
				antiDarkMoneyDisclosure(),
				antiCaptureVouchers()
		);
	}
	
	private static List<PolicyContest> publicFinanceDarkMoneyContests() {
		return List.of(
				contest("voucher-independent-expenditure-offset", "Voucher independent-expenditure offset", "election", ContestArena.ELECTION, false, 0.46, 0.34, 0.56, 0.92, 0.72, 0.42, 0.82),
				contest("public-match-donor-network-pressure", "Public-match donor-network pressure", "finance", ContestArena.ELECTION, false, 0.44, 0.34, 0.54, 0.90, 0.70, 0.48, 0.78),
				contest("voucher-nonprofit-issue-ad-routing", "Voucher nonprofit issue-ad routing", "democracy", ContestArena.PUBLIC_INFORMATION, false, 0.48, 0.36, 0.58, 0.88, 0.70, 0.58, 0.84),
				antiCaptureVouchers(),
				antiDarkMoneyDisclosure(),
				antiCaptureDisclosure()
		);
	}

	private static List<PolicyContest> publicFinanceOutsideSpendingLeakageContests() {
		return List.of(
				contest("public-match-outside-spending-offset", "Outside-spending offset to public matching funds", "election", ContestArena.ELECTION, false, 0.44, 0.32, 0.54, 0.94, 0.74, 0.42, 0.86),
				contest("voucher-donor-network-independent-committee", "Donor-network independent committee offset", "finance", ContestArena.ELECTION, false, 0.42, 0.32, 0.52, 0.92, 0.72, 0.46, 0.84),
				contest("public-finance-nonprofit-persuasive-campaign", "Nonprofit persuasive campaign outside candidate finance", "democracy", ContestArena.PUBLIC_INFORMATION, false, 0.46, 0.34, 0.56, 0.90, 0.72, 0.62, 0.84),
				contest("public-finance-technical-ballot-messaging", "Technical ballot messaging outside candidate finance", "democracy", ContestArena.PUBLIC_INFORMATION, false, 0.42, 0.32, 0.52, 0.88, 0.70, 0.76, 0.80),
				antiCaptureVouchers(),
				antiDarkMoneyDisclosure()
		);
	}
	
	private static List<PolicyContest> procurementModificationContests() {
		return List.of(
				contest("post-award-modification-pressure", "Post-award modification pressure", "procurement", ContestArena.PROCUREMENT, false, 0.40, 0.28, 0.50, 0.98, 0.84, 0.78, 0.20),
				contest("exclusion-language-specification", "Exclusion-language specification", "procurement", ContestArena.PROCUREMENT, false, 0.38, 0.26, 0.48, 0.96, 0.82, 0.86, 0.18),
				contest("bid-protest-settlement-leverage", "Bid-protest settlement leverage", "procurement", ContestArena.LITIGATION, false, 0.36, 0.24, 0.46, 0.94, 0.80, 0.66, 0.20),
				contest("subcontract-eligibility-after-award", "Subcontract eligibility after award", "procurement", ContestArena.PROCUREMENT, false, 0.38, 0.28, 0.46, 0.92, 0.76, 0.70, 0.18),
				antiCoolingOff(),
				antiCaptureDisclosure()
		);
	}
	
	private static List<PolicyContest> technicalRulemakingContests() {
		List<PolicyContest> contests = new ArrayList<>();
		contests.addAll(rulemakingContests());
		contests.add(contest("technical-guidance-benchmark", "Technical benchmark guidance", "technology", ContestArena.RULEMAKING, false, 0.58, 0.38, 0.62, 0.86, 0.64, 0.94, 0.24));
		contests.add(contest("standards-incorporation-rule", "Standards incorporation rule", "rulemaking", ContestArena.RULEMAKING, false, 0.56, 0.36, 0.60, 0.84, 0.62, 0.92, 0.22));
		contests.add(contest("expert-evidence-advisory", "Expert evidence advisory docket", "public-information", ContestArena.PUBLIC_INFORMATION, false, 0.54, 0.34, 0.58, 0.80, 0.60, 0.88, 0.26));
		contests.add(antiAstroturfAuth());
		return List.copyOf(contests);
	}
	
	private static List<PolicyContest> commentFloodingContests() {
		return List.of(
				contest("mass-comment-rule", "Mass-comment rulemaking docket", "rulemaking", ContestArena.RULEMAKING, false, 0.56, 0.30, 0.60, 0.82, 0.66, 0.78, 0.42),
				contest("public-information-salience", "Synthetic public-information campaign", "public-information", ContestArena.PUBLIC_INFORMATION, false, 0.48, 0.28, 0.62, 0.78, 0.64, 0.66, 0.54),
				contest("template-heavy-guidance", "Template-heavy technical guidance", "technology", ContestArena.RULEMAKING, false, 0.52, 0.34, 0.58, 0.84, 0.68, 0.90, 0.36),
				antiAstroturfAuth()
		);
	}

	private static List<PolicyContest> commentAuthenticitySubstitutionContests() {
		return List.of(
				contest("sponsored-technical-attachment", "Sponsored technical attachment campaign", "rulemaking", ContestArena.RULEMAKING, false, 0.50, 0.30, 0.56, 0.90, 0.72, 0.96, 0.30),
				contest("consultant-written-unique-comments", "Consultant-written unique comments", "technology", ContestArena.RULEMAKING, false, 0.48, 0.30, 0.54, 0.88, 0.70, 0.94, 0.34),
				contest("expert-affiliation-disclosure-gap", "Expert affiliation disclosure gap", "public-information", ContestArena.PUBLIC_INFORMATION, false, 0.46, 0.28, 0.52, 0.86, 0.68, 0.92, 0.32),
				contest("comment-auth-venue-shift-to-guidance", "Comment-auth venue shift to guidance", "rulemaking", ContestArena.RULEMAKING, false, 0.46, 0.30, 0.52, 0.84, 0.68, 0.90, 0.26),
				antiAstroturfAuth(),
				antiCaptureDisclosure()
		);
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
			String configuredDirectory = System.getenv("LOBBY_CAPTURE_CALIBRATION_DIR");
			Path calibrationDirectory = configuredDirectory == null || configuredDirectory.isBlank()
					? Path.of("data", "snapshots", "2024-env", "normalized")
					: Path.of(configuredDirectory);
			cachedCalibration = CalibrationDataLoader.loadOrEmbedded(calibrationDirectory);
		}
		return cachedCalibration;
	}
}
