# Lobby Capture Simulator Project Plan

This project should be a standalone Java simulation of lobbying, money-in-politics, regulatory capture, and anti-capture reforms. The existing congressional simulator is useful as a reference, but the new project should invert the center of gravity: lobby organizations, funders, and influence channels are the primary strategic actors; legislatures, regulators, campaigns, courts, disclosure systems, and enforcement bodies are target environments.

The base simulator already has useful primitives:

- `LobbyGroup` models issue preferences, budget, influence intensity, defensive multiplier, information bias, public campaign skill, capture strategy, and public-support mismatch tolerance.
- `BudgetedLobbyingProcess` models finite budgets, spend intent, channel allocation, defensive spending against anti-lobbying reforms, public financing/public advocate/blind review parameters, adaptive strategy switching, and channel-return learning.
- `LobbyAuditProcess` models audit probability, capture-risk weighting, failure thresholds, sanction severity, sponsor trust, and reversal of captured enactments.
- `LobbyTransparencyProcess` models disclosure strength, reputational backlash, and the effect of visible lobbying on public support.
- `ScenarioReport`, `MetricsAccumulator`, `MetricDefinition`, and `CampaignRunner` provide a mature reporting pattern with scenario catalogs, batch runs, CSV output, weighted case summaries, and directionally scored metrics.

The new project should not treat lobbying as one wrapper around a bill vote. It should model an influence economy in which organized interests allocate budgets across access, campaigns, litigation, information distortion, dark money, revolving-door incentives, regulatory comments, procurement pressure, and defensive anti-reform spending.

## Current Implementation Status

The repository now contains a runnable Java MVP with a Makefile workflow, scenario catalog, campaign reports, sensitivity sweeps, ablation sweeps, calibration fixtures, source-native live normalization hooks, generated paper tables, a LaTeX working paper, and smoke tests. Lobby organizations remain the central strategic actors. The active engine includes client funding, contribution-ledger flows, adaptive channel allocation, client funding multipliers, regulator attention, watchdog focus, rulemaking docket/comment campaigns, evasion profiles, enforcement detection and penalties, and anti-capture reform bundles.

## 1. Proposed Repo Architecture

Use Java with a small Makefile first, matching the base simulator's low-friction workflow. Add Gradle or Maven only when external data ingestion requires stable third-party CSV/JSON dependencies.

```text
lobby-capture-sim/
  README.md
  Makefile
  .gitignore
  data/
    calibration/
      empirical-benchmarks.csv
      source-map.md
    fixtures/
      minimal-world.json
      lobbying-baseline.json
      public-financing-baseline.json
    raw/
      .gitkeep
  docs/
    project-plan.md
    odd-model.md
    validation.md
    scenario-catalog.md
  reports/
    .gitkeep
  scripts/
    fetch-fec.sh
    fetch-lda.sh
    fetch-regulatory.sh
    run-campaign.sh
  src/main/java/lobbycapture/
    Main.java
    actor/
      LobbyOrganization.java
      Lobbyist.java
      InterestClient.java
      PublicOfficial.java
      Regulator.java
      Candidate.java
      EnforcementAgency.java
      PublicAdvocate.java
      WatchdogGroup.java
    budget/
      BudgetAccount.java
      FundingSource.java
      MoneyFlow.java
      ContributionLedger.java
      DarkMoneyPool.java
    strategy/
      InfluenceStrategy.java
      InfluenceChannel.java
      ChannelAllocation.java
      StrategyMemory.java
      LobbyAllocationEngine.java
      DefensiveReformStrategy.java
    arena/
      InfluenceArena.java
      LegislativeArena.java
      RulemakingArena.java
      ElectionArena.java
      ProcurementArena.java
      LitigationArena.java
      EnforcementArena.java
      PublicInformationArena.java
    policy/
      PolicyContest.java
      RegulatoryAction.java
      CampaignContest.java
      EnforcementAction.java
      PublicSignal.java
      CaptureScoring.java
    reform/
      ReformRegime.java
      TransparencySystem.java
      LobbyingBan.java
      CoolingOffPolicy.java
      PublicFinancingSystem.java
      DemocracyVoucherSystem.java
      ContributionLimitSystem.java
      DarkMoneyDisclosureRule.java
      BlindReviewSystem.java
    simulation/
      WorldState.java
      WorldSpec.java
      SimulationClock.java
      Scenario.java
      ScenarioCatalog.java
      Simulator.java
      RandomSource.java
    metrics/
      MetricsAccumulator.java
      ScenarioReport.java
      MetricDefinition.java
      CaptureDiagnostics.java
    reporting/
      CampaignRunner.java
      CsvReportWriter.java
      MarkdownReportWriter.java
      ReportProvenance.java
    calibration/
      CalibrationBenchmark.java
      CalibrationTarget.java
      CalibrationTargetCatalog.java
      DataSourceRegistry.java
      EmpiricalValidator.java
    util/
      Values.java
      WeightedChoice.java
      Gini.java
  src/test/java/lobbycapture/
    actor/
    strategy/
    arena/
    reform/
    metrics/
```

Core runtime loop:

1. Clients fund lobby organizations based on expected private gain, regulatory exposure, procurement stakes, and reform threat.
2. Lobby organizations choose target arenas and allocate budgets across influence channels.
3. Public officials, regulators, candidates, courts, enforcement agencies, watchdogs, and public-information systems react.
4. Policy, campaign, rulemaking, procurement, and enforcement outcomes update the world state.
5. Lobby organizations observe channel returns and adapt future budgets/strategies.
6. Reform systems update disclosure, detection, sanctions, public financing, and access restrictions.

Architectural boundary: `arena/*` should process interactions, but `strategy/*` should decide lobby action. This prevents lobbying from collapsing back into a single pressure modifier.

## 2. Model Entities And State Variables

### LobbyOrganization

Represents a strategic influence firm, trade association, corporation, union, advocacy network, or coalition.

- `id`, `name`, `sector`, `issueDomains`
- `clients`, `coalitionPartners`, `frontGroups`
- `disclosedBudget`, `darkMoneyBudget`, `legalBudget`, `campaignBudget`, `grassrootsBudget`, `researchBudget`
- `cashOnHand`, `fundraisingCapacity`, `donorConcentration`, `memberDuesReliance`
- `preferredPolicyPositions` by domain
- `regulatoryExposure`, `procurementExposure`, `enforcementExposure`
- `influenceIntensity`, `accessCapital`, `technicalExpertise`, `publicCampaignSkill`
- `informationBias`, `astroturfSkill`, `mediaPlacementSkill`
- `litigationThreatSkill`, `delayTolerance`, `settlementLeverage`
- `revolvingDoorNetworkStrength`, `formerOfficialShare`, `futureEmploymentOfferRate`
- `disclosureAvoidanceSkill`, `complianceCapacity`, `legalRiskTolerance`
- `reformThreatSensitivity`, `defensiveMultiplier`
- `channelReturnMemory`, `issueReturnMemory`, `targetReturnMemory`
- `publicSupportMismatchTolerance`, `backlashSensitivity`
- `credibilityWithOfficials`, `credibilityWithPublic`, `watchdogVisibility`

### InterestClient

Represents the economic or ideological principal paying for influence.

- `id`, `sector`, `marketConcentration`, `affectedRegulations`
- `privateGainByPolicy`, `expectedCostOfRegulation`, `contractAwardUpside`
- `publicHarmExternality`, `consumerVisibility`, `workerVisibility`
- `riskTolerance`, `timeHorizon`, `needForSecrecy`
- `budgetCommitmentRule`, `defensiveFundingRule`
- `reputationalRisk`, `litigationExposure`

### Lobbyist

Represents an individual agent who converts money into access, expertise, and pressure.

- `id`, `employerId`, `issueExpertise`, `legalExpertise`
- `priorPublicRole`, `coveredOfficialHistory`, `coolingOffRemaining`
- `personalAccessNetwork`, `committeeConnections`, `agencyConnections`
- `credibility`, `messageDiscipline`, `fundraisingNetwork`
- `complianceRisk`, `violationHistory`, `sanctionRisk`
- `expectedRevolvingDoorValue`

### PublicOfficial

Represents elected officials, senior staff, appointees, and agency leaders.

- `id`, `role`, `institution`, `partyOrBloc`, `ideology`
- `constituencyPreference`, `donorDependence`, `fundraisingPressure`
- `technicalInformationNeed`, `staffCapacity`, `policyAttention`
- `careerAmbition`, `postGovernmentSalaryAttraction`, `ethicsResistance`
- `publicInterestCommitment`, `captureSusceptibility`
- `mediaRiskSensitivity`, `watchdogRiskSensitivity`
- `trustInLobbyBySector`, `trustInPublicAdvocate`, `trustInAgencyExperts`

### Regulator / Agency

Represents a rulemaking or enforcement body.

- `agencyId`, `domain`, `statutoryMandate`, `independence`
- `staffCapacity`, `technicalComplexity`, `industryExpertiseDependence`
- `budget`, `enforcementBudget`, `inspectionCapacity`
- `rulemakingBacklog`, `commentProcessingCapacity`
- `captureVulnerability`, `revolvingDoorFlow`, `procurementDependence`
- `politicalOversightPressure`, `judicialReviewRisk`
- `publicAdvocateAccess`, `watchdogAccess`, `transparencyCoverage`

### Candidate / Campaign

Represents election-facing money-in-politics.

- `candidateId`, `office`, `ideology`, `incumbency`
- `smallDonorBase`, `largeDonorDependence`, `PACDependence`
- `publicFinancingOptIn`, `voucherParticipation`, `matchingFundsEligibility`
- `hardMoneyRaised`, `independentExpenditureSupport`, `oppositionSpending`
- `fundraisingTimeBurden`, `messageResponsivenessToDonors`
- `probabilityOfWinning`, `policyDebtToSponsors`

### PolicyContest

A generic target of influence: bill, rule, procurement decision, enforcement priority, appointment, guidance document, or litigation posture.

- `id`, `domain`, `arena`, `stage`
- `truePublicBenefit`, `perceivedPublicSupport`, `publicSignalUncertainty`
- `privateGain`, `concentratedHarm`, `diffuseBenefit`, `diffuseCost`
- `technicalComplexity`, `salience`, `mediaAttention`
- `legalVulnerability`, `delayValue`, `implementationCost`
- `targetAgency`, `targetOfficials`, `affectedGroups`
- `lobbyPressure`, `publicAdvocatePressure`, `watchdogPressure`
- `informationDistortion`, `commentRecordDistortion`, `darkMoneyInfluence`
- `revolvingDoorInfluence`, `campaignFinanceInfluence`, `litigationThreat`
- `captureRisk`, `publicInterestScore`, `outcomeStatus`

### PublicInformationEnvironment

Represents the public signal that officials and regulators observe.

- `truePublicPreference`, `perceivedPublicPreference`, `pollQuality`
- `mediaAttention`, `mediaCapture`, `messageSaturation`
- `astroturfVolume`, `genuineGrassrootsVolume`, `commentAuthenticity`
- `misinformationLoad`, `technicalUncertainty`, `sourceCredibility`
- `transparencyVisibility`, `publicBacklash`, `publicTrust`

### ReformRegime

Represents anti-capture rules applied to a world or scenario.

- `disclosureStrength`, `realTimeDisclosure`, `beneficialOwnerDisclosure`
- `lobbyingBanStrength`, `coolingOffYears`, `giftBanStrength`
- `contactLogCoverage`, `meetingTransparency`, `blindReviewStrength`
- `campaignContributionLimits`, `independentExpenditureTransparency`
- `publicFinancingStrength`, `smallDonorMatchRate`, `democracyVoucherBudget`
- `darkMoneyDisclosureStrength`, `foreignMoneyDetection`
- `publicAdvocateStrength`, `citizenCommentAuthentication`
- `enforcementBudget`, `auditRate`, `sanctionSeverity`, `appealsDelay`
- `falsePositiveCost`, `administrativeCost`, `constitutionalConstraintRisk`

### EnforcementAgency

Represents FEC-like, ethics, inspector general, DOJ referral, agency compliance, or procurement oversight bodies.

- `id`, `jurisdiction`, `independence`, `budget`, `staffCapacity`
- `auditProbability`, `riskBasedAuditWeight`, `randomAuditRate`
- `detectionCapability`, `dataAccess`, `backlog`
- `sanctionSeverity`, `settlementProbability`, `referralProbability`
- `politicalInterferenceRisk`, `captureSusceptibility`
- `trustByActor`, `repeatOffenderEscalation`

### MoneyFlow

Represents disclosed and undisclosed political money.

- `sourceId`, `recipientId`, `intermediaryId`
- `flowType`: `DIRECT_CONTRIBUTION`, `PAC`, `SUPER_PAC`, `DARK_MONEY`, `TRADE_ASSOCIATION`, `GRASSROOTS_SMALL_DONOR`, `PUBLIC_MATCH`, `DEMOCRACY_VOUCHER`
- `amount`, `disclosureLag`, `traceability`, `coordinationRisk`
- `targetContest`, `issueDomain`, `time`
- `legalRisk`, `reputationalRisk`, `expectedInfluenceReturn`

## 3. Scenario Catalog

The catalog should be organized as scenario families so batch reports can compare baseline influence systems against reform systems.

### Baseline Influence Systems

- `open-access-lobbying`: direct access, ordinary disclosure lag, no public financing, modest enforcement.
- `budgeted-disclosed-lobbying`: LDA-like reporting, finite lobby budgets, channel allocation, and public backlash.
- `high-salience-low-disclosure`: high media attention but weak beneficial-owner visibility.
- `low-salience-technical-rulemaking`: technical agency rulemaking with high information asymmetry and weak public attention.
- `procurement-capture-baseline`: firms lobby for contracts, favorable procurement specifications, or enforcement forbearance.

### Strategic Lobbying Channels

- `direct-pressure-dominant`: access meetings, drafting help, committee/staff pressure.
- `agenda-access-dominant`: spending mainly buys issue priority, procedural timing, and bottleneck access.
- `information-distortion-dominant`: commissioned research, selective technical claims, comment manipulation.
- `public-campaign-dominant`: ad campaigns, earned media, astroturf, public-opinion pressure.
- `litigation-threat-dominant`: delay, injunction threats, settlement pressure, and judicial review risk.
- `campaign-finance-dominant`: hard money, PAC giving, independent expenditures, fundraising access.
- `dark-money-dominant`: opaque intermediaries with lower traceability and delayed public backlash.
- `revolving-door-dominant`: hiring former officials, implicit future job incentives, and access networks.

### Regulatory Capture

- `agency-expertise-dependence`: understaffed regulator depends on industry-provided data.
- `comment-flood-capture`: genuine comments are diluted by template or astroturf campaigns.
- `guidance-document-capture`: low-visibility guidance shifts practical enforcement without visible legislation.
- `enforcement-forbearance`: lobbying reduces inspections, penalties, or referral intensity.
- `procurement-specification-capture`: lobbying shapes specifications before public procurement competition.
- `appointment-and-staffing-capture`: lobby influence affects appointments, staffing, and agency priorities.

### Campaign Finance And Public Financing

- `large-donor-dependence`: candidates spend more time fundraising and respond more to high-dollar donors.
- `super-pac-saturation`: independent expenditure spending changes perceived electoral threat.
- `small-donor-matching`: public match increases small donor value and reduces large donor dependence.
- `democracy-vouchers`: voucher allocations produce public financing and broader participation.
- `public-financing-plus-dark-money`: public financing competes against outside independent spending.
- `contribution-caps-with-evasion`: caps shift money into independent or nonprofit channels.

### Anti-Capture Reforms

- `real-time-transparency`: immediate disclosure of contacts, spend, clients, and issue targets.
- `beneficial-owner-disclosure`: dark money traceability is increased, but laundering attempts remain possible.
- `cooling-off-ban`: former officials lose access value for a fixed period.
- `lobbying-ban-for-covered-officials`: stronger restriction with higher legal challenge risk.
- `blind-regulatory-review`: officials see public-interest and technical records before lobby identity.
- `public-advocate`: independent public-interest actor counters technical claims and information distortion.
- `audit-and-sanctions`: risk-weighted enforcement with sanctions and repeat-offender escalation.
- `anti-astroturf-authentication`: comment systems distinguish genuine public comments from coordinated scripts.
- `defensive-lobby-cap`: limits defensive anti-reform spending by affected lobby groups.

### Stress And Combined Cases

- `adaptive-lobby-learning`: groups switch channels based on returns.
- `reform-threat-mobilization`: strong public reform proposals trigger defensive lobbying.
- `watchdog-surge`: investigative visibility increases backlash and enforcement referrals.
- `agency-budget-cut`: low public capacity increases dependence on industry information.
- `polarized-public-low-trust`: public backlash signals are weaker because trust is degraded.
- `full-anti-capture-bundle`: transparency, enforcement, public financing, public advocate, blind review, cooling-off, and dark-money disclosure combined.
- `bundle-with-evasion`: same bundle, but lobbies can shift to less regulated channels.

## 4. Metrics

### Capture And Public-Interest Outcomes

- `captureIndex`: combined score from private gain, policy/rule movement toward lobby preference, weak public value, and low visibility.
- `publicInterestScore`: true public benefit, genuine public support, and low concentrated harm.
- `privateGainRatio`: private gain divided by public benefit, with bounded denominator.
- `policyDistortion`: distance between public-interest optimum and final policy/rule.
- `regulatoryDrift`: movement from statutory/public-interest mandate toward regulated-party preference.
- `enforcementForbearanceRate`: expected enforcement actions avoided after influence spending.
- `procurementBiasIndex`: award/specification movement toward connected firms.
- `concentratedHarmPassageRate`: harmful outcomes that survive process.

### Money And Strategy

- `lobbySpendPerContest`
- `spendShareDirectAccess`
- `spendShareAgendaAccess`
- `spendShareInformationDistortion`
- `spendSharePublicCampaign`
- `spendShareLitigationThreat`
- `spendShareCampaignFinance`
- `spendShareDarkMoney`
- `spendShareRevolvingDoor`
- `defensiveReformSpendShare`
- `captureReturnOnSpend`
- `publicBenefitPerInfluenceDollar`
- `channelSwitchRate`
- `budgetEscalationRate`
- `evasionShiftRate`

### Campaign Finance

- `largeDonorDependence`
- `smallDonorShare`
- `voucherParticipationRate`
- `publicMatchShare`
- `independentExpenditurePressure`
- `darkMoneyTraceability`
- `fundraisingTimeBurden`
- `candidatePolicyDebt`
- `donorInfluenceGini`

### Information Environment

- `publicPreferenceDistortion`
- `commentRecordDistortion`
- `astroturfShare`
- `technicalUncertaintyExploited`
- `mediaCaptureIndex`
- `transparencyBacklash`
- `sourceCredibilityDecay`
- `genuinePublicSignalRecovery`

### Revolving Door

- `formerOfficialAccessPremium`
- `coolingOffViolationRisk`
- `postGovernmentOfferInfluence`
- `agencyStaffChurnCapture`
- `coveredOfficialDisclosureCompleteness`
- `revolvingDoorNetworkConcentration`

### Reform Performance

- `antiCaptureSuccessRate`
- `detectionRate`
- `auditFalseNegativeRate`
- `auditFalsePositiveRate`
- `sanctionDeterrence`
- `repeatOffenderRate`
- `administrativeCostIndex`
- `legitimateAdvocacyChillRate`
- `constitutionalChallengeDelay`
- `implementationFeasibilityScore`

### Reporting Scores

Keep composite scores transparent and secondary to raw metrics:

- `captureControlScore`: lower capture, lower private-gain ratio, lower preference distortion, lower enforcement forbearance.
- `representationScore`: higher public alignment, higher small donor/voucher participation, lower donor influence concentration.
- `reformFeasibilityScore`: lower admin cost, lower false positives, lower litigation delay, higher enforcement capacity.
- `directionalScore`: average of capture control, representation, and feasibility, reported only as a navigational summary.

## 5. Validation Data Sources

Use empirical data for scale, distributions, and plausibility checks. Do not claim the simulation estimates causal effects from these sources alone.

### Federal Lobbying And Disclosure

- [LDA.gov](https://lda.gov/) for LD-1 registrations, LD-2 quarterly activity reports, and LD-203 contribution reports through search and REST API download. Use for lobbying clients, registrants, issue codes, spend, and covered-position disclosure fields.
- [U.S. Senate downloadable lobbying databases](https://www.senate.gov/legislative/Public_Disclosure/database_download.htm) for historical LDA bulk files by year/quarter.
- [House Lobbying Disclosure](https://lobbyingdisclosure.house.gov/) for LDA guidance, filing deadlines, contribution reporting rules, registration thresholds, and compliance context.
- [GAO lobbying disclosure compliance reports](https://files.gao.gov/reports/GAO-25-107523/index.html) for audit-compliance benchmarks, prior covered official disclosure checks, contribution-report issues, and self-reporting limits.

### Campaign Finance And Political Spending

- [FEC browse and bulk campaign finance data](https://www.fec.gov/data/browse-data/?cf=phome) for candidate/committee summaries, individual contributions, independent expenditures, electioneering communications, communication costs, leadership PACs, and lobbyist bundled contributions.
- [FEC API](https://api.open.fec.gov/developers/) for programmatic campaign finance queries where an API key is available.
- [FollowTheMoney APIs](https://followthemoney.org/our-data/apis/) for state-level campaign donor data, subject to account and license limits.
- State and local campaign finance boards for public financing, matching funds, and enforcement records.

### Public Financing And Democracy Vouchers

- [Seattle Democracy Voucher program data](https://www.seattle.gov/democracyvoucher/program-data/distributed-voucher-funds-and-program-data) for voucher assignments, candidate totals, and historical-data contact path.
- [New York City Campaign Finance Board matching funds program](https://www.nyccfb.info/program/) for small-donor match structure, independent expenditure reporting, audits, penalties, and public-funds payment data.

### Legislative And Voting Baselines

- [Voteview data](https://voteview.uga.edu/data) for roll-call votes, NOMINATE ideology scores, and party/coalition structure.
- [govinfo Bill Status XML bulk data](https://www.govinfo.gov/bulkdata/BILLSTATUS/resources/readme.html) and Congress.gov/govinfo bill histories for introduced/referred/passed/enacted bill attrition and issue-domain timing.

### Regulatory And Agency Baselines

- [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) for proposed rules, final rules, agencies, topics, and publication timing. Treat FederalRegister.gov as an access layer and verify legal-critical text against official govinfo PDFs when needed.
- [Regulations.gov API](https://open.gsa.gov/api/regulationsgov/) for documents, dockets, comments, and comment-search data.
- [Reginfo.gov OIRA review data](https://mobile.reginfo.gov/public/do/eoPackageMain) for EO 12866 review timing and regulatory review status.
- [USAspending API](https://api.usaspending.gov/docs/endpoints) for agency spending, award recipients, contract/grant flows, and procurement-capture proxy variables.

### Watchdog And Enrichment Sources

- OpenSecrets/Revolving Door data, LegiStorm, agency calendars, inspector general reports, enforcement releases, and manually curated investigative datasets can enrich network validation. Treat these as secondary because access, licensing, and field coverage vary.
- Court dockets and major litigation trackers can calibrate litigation-delay scenarios, but the MVP should use simple delay/cost distributions before building a legal-data importer.

## 6. Implementation Milestones

### Milestone 0: Repo scaffold and design document

- Create the package tree, Makefile, README, `docs/odd-model.md`, and seed fixtures.
- Copy/adapt `Values` and basic report scaffolding.
- Define the first `WorldSpec`, `Scenario`, and deterministic seeded run.
- Done when `make test` and `make run ARGS="--scenario open-access-lobbying --seed 1"` produce a minimal report.

### Milestone 1: Core actor and money-flow model

- Implement `LobbyOrganization`, `InterestClient`, `PublicOfficial`, `Regulator`, `Candidate`, `EnforcementAgency`, `BudgetAccount`, `MoneyFlow`, and `WorldState`.
- Implement hard money, PAC, independent expenditure, dark money, public match, and voucher money-flow types.
- Add tests for budget conservation, disclosure traceability, and source/recipient ledger consistency.

### Milestone 2: Lobby strategy and influence channels

- Adapt the base `BudgetedLobbyingProcess` into `LobbyAllocationEngine`.
- Implement direct access, agenda access, information distortion, public campaign, litigation threat, campaign finance, dark money, and revolving-door channels.
- Add channel-return memory and adaptive strategy switching.
- Done when a batch run can show channel spend shares, capture return on spend, and defensive reform spend share.

### Milestone 3: Target arenas

- Implement `LegislativeArena`, `RulemakingArena`, `ElectionArena`, `ProcurementArena`, `LitigationArena`, `EnforcementArena`, and `PublicInformationArena`.
- Make `PolicyContest` generic enough to represent bills, rules, guidance, procurement, enforcement priorities, and campaign outcomes.
- Keep arena rules simple and inspectable. The first version should be comparative, not realism-heavy.

### Milestone 4: Public information distortion and regulatory capture

- Implement perceived versus true public support.
- Add astroturf/comment flooding, technical uncertainty, media attention, and source credibility.
- Add agency expertise dependence, staff capacity, rulemaking delay, enforcement forbearance, and procurement-specification capture.
- Done when low-salience technical rulemaking behaves differently from high-salience electoral issues.

### Milestone 5: Anti-capture reform systems

- Implement transparency systems, real-time disclosure, beneficial-owner disclosure, cooling-off periods, lobbying bans, public financing, democracy vouchers, public advocates, blind review, anti-astroturf authentication, and enforcement agencies.
- Add defensive spending against anti-lobbying reforms as a first-class strategy, not a special bill flag.
- Include false positives, legitimate-advocacy chilling, administrative cost, enforcement backlog, and litigation delay.

### Milestone 6: Scenario catalog and campaign runner

- Port the scenario catalog/reporting pattern from the congressional simulator.
- Add scenario families listed above.
- Produce CSV and Markdown reports with raw metrics, scenario summaries, weighted cases, and source provenance.
- Done when `make campaign` writes a reproducible report under `reports/`.

### Milestone 7: Empirical bridge and calibration

- Build a `DataSourceRegistry` and `CalibrationTargetCatalog`.
- Add importers or fixture converters for LDA, FEC, Federal Register, Regulations.gov, Voteview, govinfo, Seattle vouchers, NYC matching funds, and USAspending.
- Start with benchmark ranges and distribution checks: spend distributions, issue-domain mix, disclosure lag, campaign finance concentration, rulemaking duration, comment volume, and audit failure rates.
- Done when `make validate` explains which metrics are calibrated, which are only plausibility screened, and which remain synthetic.

### Milestone 8: Hardening and paper-ready artifacts

- Add seed robustness, scenario ablations, sensitivity sweeps, and report manifests.
- Add tests for deterministic seeds, budget conservation, disclosure lag, enforcement sanctions, adaptive strategy learning, and reform bundle interactions.
- Write `docs/validation.md`, `docs/scenario-catalog.md`, and an ODD+D style model appendix.
- Package an anonymous/shareable archive if needed.

## 7. Code To Copy Or Adapt From Existing Simulator

### Copy with light adaptation

- `congresssim.util.Values`: keep range validation, clamping, and simple numeric guardrails.
- `MetricDefinition`, `ScenarioReport`, `MetricsAccumulator`, and `CampaignRunner` reporting conventions: preserve the discipline of raw metrics plus transparent directional summaries.
- Scenario catalog registration pattern: keep named scenario keys and explicit scenario lists for campaign batches.

### Adapt heavily

- `LobbyGroup.java`: split into `LobbyOrganization`, `InterestClient`, `Lobbyist`, `BudgetAccount`, and `StrategyMemory`. Keep issue preferences, budgets, defensive multiplier, information bias, public campaign skill, capture strategy, and mismatch tolerance as starting concepts.
- `LobbyCaptureStrategy.java`: expand from six strategies into a channel taxonomy: direct access, agenda access, information distortion, public campaign, litigation threat, campaign finance, dark money, revolving door, procurement shaping, enforcement forbearance, and defensive reform blocking.
- `BudgetedLobbyingProcess.java`: convert the core loop into `LobbyAllocationEngine`. Reuse finite budgets, spend intent, channel shares, defensive anti-reform spending, public financing/public advocate/blind review effects, adaptive strategy updates, return signals, budget multipliers, issue multipliers, and channel-return memory. Remove the assumption that all effects mutate a `Bill`.
- `LobbyAuditProcess.java`: convert into `EnforcementAgency` plus `AuditQueue`. Reuse audit probability, risk weighting, failure threshold, sanctions, trust decay, reward for public-interest behavior, and reversal/blocked-action logic. Extend it to lobby organizations, public officials, agencies, campaigns, and regulated firms.
- `LobbyTransparencyProcess.java`: convert into `TransparencySystem`. Reuse disclosure strength and backlash, but add disclosure lag, beneficial ownership, contact logs, dark-money traceability, and strategic laundering.
- `LobbyCaptureScoring.java`: keep the idea of capture risk and public-interest scoring, but make scoring target-agnostic across policy, rulemaking, procurement, elections, and enforcement.

### Do not copy as central mechanics

- Do not make `Bill` the universal state object. Use `PolicyContest` and arena-specific records.
- Do not make `LegislativeProcess` the top-level abstraction. Use `InfluenceArena` and `LobbyAllocationEngine`.
- Do not let voting outcomes be the primary success metric. Capture may occur through rule text, enforcement priorities, procurement rules, litigation delay, staff incentives, or public-information distortion without any visible floor vote.
- Do not treat public financing or democracy vouchers as a single pressure correction. They need explicit candidates, contributors/voucher users, public funds, outside spending, and donor-dependence effects.

### First copied file set

Start by copying these into the new namespace and immediately renaming/reframing them:

- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/util/Values.java` -> `src/main/java/lobbycapture/util/Values.java`
- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/model/LobbyCaptureStrategy.java` -> `src/main/java/lobbycapture/strategy/InfluenceChannel.java`
- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/institution/BudgetedLobbyingProcess.java` -> reference only while writing `LobbyAllocationEngine.java`
- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/institution/LobbyAuditProcess.java` -> reference only while writing `EnforcementAgency.java`
- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/institution/LobbyTransparencyProcess.java` -> reference only while writing `TransparencySystem.java`
- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/simulation/ScenarioReport.java` -> `src/main/java/lobbycapture/metrics/ScenarioReport.java`
- `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/src/main/java/congresssim/experiment/CampaignRunner.java` -> `src/main/java/lobbycapture/reporting/CampaignRunner.java`

The first implementation slice should prove this model can answer one core question: when organized interests face a meaningful anti-capture reform threat, do they shift from ordinary policy capture to defensive reform blocking, and which reforms remain effective after that adaptation?
