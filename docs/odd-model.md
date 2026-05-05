# ODD Model Description

This document is the supporting-information model description for the Lobby Capture Simulator. It follows the spirit of the ODD protocol: purpose, entities, state variables, process overview, scheduling, design concepts, initialization, inputs, submodels, and outputs.

## Purpose

The model compares how organized interests allocate influence budgets under ordinary policy capture opportunities and under anti-capture reform threats. Its main question is whether reforms reduce capture or shift influence into less visible channels. It is a mechanism model, not a causal estimate of any single statute, agency rule, or campaign-finance law.

## Entities and State Variables

### Lobby Organization

Lobby organizations are the central adaptive actors.

- Identity and scope: `id`, name, issue-domain preferences, baseline influence intensity.
- Budget state: total budget, channel-specific accounts, donor/client replenishment, defensive reform budget, disclosure lag, traceability.
- Capability state: direct access capital, technical expertise, public campaign skill, information-bias skill, astroturf skill, litigation skill, revolving-door network strength, disclosure-avoidance skill.
- Adaptation state: channel return memory, issue-specific funding multipliers, evasion profile, reform-threat sensitivity, defensive spending multiplier.
- Output state: spend records, money-flow records, observed capture, hidden capture, total influence distortion, hidden influence, influence preservation, messenger substitution, venue substitution, evasion shift, defensive spending, and administrative burden.

### Interest Client and Funding Source

Interest clients replenish lobby budgets when expected private gain, regulatory exposure, procurement exposure, or reform threat justifies spending.

- Client state: issue domain, expected private gain, exposure to contests, secrecy preference, reputational risk tolerance.
- Funding-source state: source type, amount, traceability, disclosure lag, legal risk, reputational risk, contest link.
- Flow state: source-to-lobby transfers are recorded in the contribution ledger and later summarized as donor concentration, large-donor dependence, dark-money share, public-financing share, and traceability.

### Public Official, Regulator, Candidate, and Enforcement Agency

Target institutions define the contest arena and reform controls.

- Public officials: access susceptibility, agenda susceptibility, public backlash sensitivity.
- Regulators: queue pressure, technical review capacity, rulemaking susceptibility, enforcement attention.
- Candidates: campaign finance susceptibility, public-financing uptake, voucher participation.
- Enforcement agencies: audit probability, enforcement budget, sanction strength, false-positive cost, appeal delay, backlog.

### Watchdog and Public Advocate

Watchdogs and public advocates provide countervailing monitoring and review capacity.

- Watchdog state: attention budget, monitoring priority by issue, detection support, public-signal amplification.
- Public-advocate state: review capacity, blind-review strength, comment-record filtering, technical counterexpertise.

### Policy Contest and Arena

A policy contest is the unit of resolution. It can represent legislation, agency drafting, notice-and-comment rulemaking, enforcement priority, procurement, litigation posture, election pressure, or anti-capture reform.

- Contest state: issue domain, arena type, public benefit, private gain, baseline capture risk, public salience, technical complexity, reform relevance, procurement exposure, enforcement exposure.
- Arena state: susceptibility parameters for election, legislative, rulemaking, enforcement, litigation, procurement, and public-information arenas.
- Docket state for rulemaking: comment volume, template saturation, authentication confidence, technical-claim credibility, unique-information share, procedural acknowledgement, review burden, substantive uptake.

### Reform Regime

The reform regime changes channel costs, visibility, and enforcement.

- Transparency controls: disclosure strength, real-time contact transparency, machine-readable meeting logs, contact logs, beneficial-owner disclosure, dark-money disclosure, and venue-shifting detection.
- Participation controls: public financing, democracy vouchers, public-interest representation funds, contribution limits, public advocates, and blind review.
- Employment and access controls: hard lobbying budgets, lobbying bans, cooling-off rules, revolving-door restrictions, and procurement firewalls.
- Process controls: comment-authenticity rules, anti-astroturf authentication, randomized audits, sanctions, enforcement budgets, appeal delay, defensive-spending caps, constitutional challenge risk, administrative cost, and false-positive cost.

## Process Overview and Scheduling

Each simulation tick resolves one selected policy contest. Report runners aggregate many contests across many runs.

1. Select a contest from the scenario contest mix using the seeded random source.
2. Replenish lobby budgets through client funding when expected private gain, exposure, secrecy needs, or reform threat justify additional money.
3. For each lobby organization, compute substitution pressure and choose channel allocations subject to channel budgets and reform controls.
4. Apply channel effects to the contest state: public support, public benefit, private gain, agenda pressure, information distortion, campaign-finance pressure, dark-money influence, litigation threat, revolving-door influence, intermediary-sponsored expertise or association routing, technical comment quality, defensive anti-reform pressure, and hidden influence.
5. If the contest has a rulemaking docket, generate and triage public comments into unique content, organized technical content, template saturation, and astroturf or misattributed comments.
6. Resolve the contest in its arena by combining contest vulnerability, arena susceptibility, channel pressure, reform controls, public backlash, and stochastic noise.
7. Apply enforcement detection and sanctions. Detection can reverse or reduce a capture outcome and imposes evasion penalties.
8. Update lobby strategy memory, issue-specific funding multipliers, regulator attention, watchdog focus, adaptation speed, and reform-decay pressure.
9. Record metrics for the scenario report and manifest.

## Design Concepts

- Budget scarcity: influence is allocated across channels rather than applied as a scalar.
- Channel substitution: when one channel becomes costly or visible, actors shift to adjacent routes that preserve messengers, relationships, or objectives.
- Hidden influence: reforms can reduce observed capture while preserving influence capacity in less visible channels.
- Failure-aware reform scoring: a reform that lowers observed capture but increases hidden capture, hidden influence, total distortion, or substitution risk is flagged as a possible failure.
- Defensive reform spending: anti-capture reform threats can mobilize lobbying that targets the reform itself.
- Information asymmetry: rulemaking and low-salience technical contests are more vulnerable to expertise capture and comment-record distortion.
- Public backlash: transparency and public salience can reduce capture pressure when visible influence generates backlash.
- Enforcement deterrence: evasion is valuable only if opacity gains exceed expected detection, sanctions, legal cost, and disclosure cost.
- Adaptive memory: successful channels receive higher future allocation weight; failed or detected channels lose weight.

## Initialization

Scenarios define lobby organizations, interest clients, contest mixes, reform regimes, channel incentives, arena susceptibility, evasion freedom, and adaptation strength. Report builds default to the committed normalized snapshot under `data/snapshots/2024-env/normalized/` so ignored live-fetch outputs cannot silently change submitted artifacts. `LOBBY_CAPTURE_CALIBRATION_DIR` may point to another normalized calibration directory for exploratory runs, while embedded fixtures remain the fallback for parser tests and offline model construction. Seeded random sources make report runs reproducible.

Main report targets use fixed run designs. Each run has an independent deterministic seed offset, and reports include sample standard deviations for capture, hidden influence, and total influence distortion across runs.

- Campaign snapshot: 40 runs, 80 contests per run, seed 42.
- Sensitivity snapshot: 30 runs, 70 contests per run, seed 142.
- Ablation snapshot: 40 runs, 80 contests per run, seed 242.
- Interaction snapshot: 25 runs, 60 contests per run, seed 342.

Each report manifest records the command, seed, run count, contest count, Java version, Git state, and calibration checksum.

## Input Data and Calibration Mapping

External data constrain plausible ranges and schema behavior. They do not identify causal reform effects.

- LDA rows constrain issue funding scale, registrant/client concentration, issue-domain mix, and disclosure lag.
- FEC rows constrain donor concentration, public-financing share, traceability, and large-donor dependence.
- Federal Register and Regulations.gov rows constrain docket volume, comment authenticity, template saturation, and technical-claim credibility.
- USAspending rows constrain procurement-recipient and awarding-agency concentration.
- Revolving-door rows currently provide a fixture-backed schema continuity check unless a licensed/exported source panel is configured.
- Seattle voucher and public-financing benchmarks constrain participation and candidate uptake ranges.

The file `data/calibration/parameter-map.csv` records the intended low, middle, and high ranges, evidence class, source report, model target, and implementation status for each validation-facing quantity.

## Submodels

### Client Funding

Client funding is proportional to lobby issue preference, client exposure, issue scale, private gain, and reform-threat pressure, then clipped to the scenario maximum. Funding flows retain source type, traceability, lag, legal risk, reputational risk, and contest linkage.

### Channel Allocation

Lobby organizations allocate spend to direct access, agenda access, information distortion, public campaign, litigation threat, campaign finance, dark money, revolving door, think-tank/association intermediaries, and defensive reform spending. Channel weights combine the active strategy, issue preference, influence intensity, learned return memory, and evasion or reform-threat adjustments.

Current strategy-to-channel templates are deterministic share vectors before budget clipping:

| Strategy | Main intended route | Important secondary routes |
| --- | --- | --- |
| Direct access | meetings and official contact | agenda access, revolving-door access, intermediaries |
| Agenda access | rule/agenda positioning | direct access, technical information, litigation |
| Information distortion | technical claims and evidence framing | dark money, intermediaries, public campaign |
| Public campaign | salience and perceived support | dark money, technical information, intermediaries |
| Litigation threat | expected delay and legal risk | agenda access, revolving-door advice, intermediaries |
| Campaign finance | donor and outside-spending pressure | dark money, access, intermediaries |
| Dark money | opaque funding and pressure | public campaign, information distortion, intermediaries |
| Revolving door | relationship and employment incentives | access, agenda, intermediaries |
| Intermediary | sponsored expertise, associations, think tanks | dark money, information distortion, public campaign |
| Defensive reform | anti-reform lobbying | public campaign, litigation, dark money, intermediaries |

### Rulemaking Comment Triage

Rulemaking contests create dockets. Comment campaigns can produce genuine public comments, sponsored technical comments, templates, synthetic comments, or misattributed comments. The triage model estimates authenticity, duplicate compression, unique-information share, review burden, technical credibility, procedural acknowledgement, and substantive uptake.

### Substitution Engine

The substitution engine calculates a switch score from expected substitute influence, messenger credibility, anonymity value, venue overlap, intermediary fit, legal cost, disclosure cost, and setup time. It reports substitution pressure, influence preservation, hidden influence, messenger substitution, venue substitution, and net transparency gain.

Simplified pseudocode:

```text
if contest is anti-capture reform:
    strategy = DEFENSIVE_REFORM
else:
    access_pressure = f(contact_logs, lobbying_bans, cooling_off)
    campaign_pressure = f(public_financing, vouchers, contribution_limits)
    opacity_pressure = f(dark_money_disclosure, beneficial_owner, real_time_disclosure)
    comment_pressure = f(comment_authenticity, blind_review, public_advocate, enforcement)
    legal_pressure = f(legal_vulnerability, delay_value, litigation_shift)
    channel_pressure = pressure_for(current_strategy)
    switch_score = channel_pressure + anonymity + messenger + intermediary_fit + venue_overlap
                   - legal_cost - disclosure_cost - setup_time
    if switch_score crosses threshold:
        strategy = nearest_substitute(current_strategy)
```

Nearest-substitute routing intentionally favors intermediaries when visible access or comment routes bind but messenger credibility remains useful. This represents sponsored research, trade associations, expert coalitions, and issue institutes without treating them as direct registered lobbying.

### Contest Resolution

Non-reform contests combine baseline capture risk, arena susceptibility, channel pressure, hidden substitution pressure, reform controls, public backlash, and bounded stochastic noise. Hidden influence partially leaks through reform controls, so a strong formal rule can still fail when influence preserves messenger credibility or moves venues. Anti-capture contests compare public reform pressure against defensive lobbying, litigation delay, and constitutional challenge risk.

Simplified non-reform resolution:

```text
channel_pressure = weighted(information, campaign_finance, revolving_door, litigation)
hidden_pressure = weighted(hidden_influence, influence_preserved, venue_substitution, messenger_substitution)
reform_control = weighted(transparency, enforcement, public_advocate, blind_review,
                          campaign_finance_counterweight, anti_astroturf, cooling_off,
                          regulator_attention, watchdog_focus)
control_leakage = 1 - weighted(hidden_influence, influence_preserved, venue_substitution)
capture_pressure = contest_risk + arena_susceptibility + channel_pressure + hidden_pressure
                   + technical_complexity - reform_control * control_leakage
                   - public_backlash + stochastic_noise
captured_before_audit = capture_pressure >= threshold
detection_probability = f(audit, enforcement, transparency, watchdogs, attention,
                          dark_money, hidden_influence, appeals_delay)
sanctions can reverse captured_before_audit
```

### Enforcement

Enforcement probability increases with audit rate, enforcement budget, sanctions, public visibility, and evasion legal risk. Detected capture attempts can be reduced or reversed and generate penalties that affect future adaptation.

## Outputs

Scenario reports include:

- observed capture rate and captured-contest counts;
- hidden capture index;
- total influence distortion;
- substitution failure risk;
- multi-seed robustness standard deviations for capture, hidden influence, and total distortion;
- anti-capture reform success;
- channel spend shares;
- visible lobbying spend share;
- intermediary spend share;
- defensive reform spending;
- hidden influence and influence preservation;
- messenger, venue, and evasion substitution;
- public-preference distortion;
- comment authenticity, template saturation, compression, and substantive uptake;
- comment flooding;
- dark-money traceability and donor concentration;
- revolving-door influence;
- technical rulemaking distortion;
- procurement bias;
- enforcement capacity, detection, sanctions, and backlog;
- Wilson intervals for binomial capture and reform-success outcomes.

The primary synthetic comparison for reform packages is `totalInfluenceDistortion`, not `captureRate`. If observed capture falls while hidden influence, hidden capture, total distortion, or substitution failure risk rises, the validation audit treats the reform as a possible failure rather than a clean success.

Generated paper tables and figures are derived from committed report CSVs. The full report snapshots, source moments, validation summary, and calibration queue remain in the repository and are included in the Wiley submission support bundle.

## Known Boundaries

The current model is strongest as a comparative mechanism prototype. The 2024 EPA/ENV source snapshot is not yet representative for dark-money or public-financing calibration. The revolving-door panel has been expanded for mechanism testing, but it remains a tracked fixture unless a live licensed/exported source is configured. Several strong-reform scenarios can still sit near a saturated observed-capture region, so the paper emphasizes total distortion, substitution diagnostics, and robustness fields rather than definitive reform rankings.
