# Next Steps

The simulator now has a lobbying-centered model core with calibration fixtures, source-native live calibration downloaders, source JSON parser fixtures, explicit client funding, rulemaking comment dockets, comment triage, evasion profiles, an influence-substitution engine, an influence-network diagnostic layer, adaptive clients/regulators/watchdogs, campaign reports, a mechanism-comparison report, sensitivity sweeps, ablation sweeps, interaction sweeps, reform-portfolio screens, validation summaries, calibration queues, source moments, generated paper tables and figures, a 2024 EPA/ENV snapshot, and a Regulation & Governance-oriented review manuscript with a reproducible Wiley submission bundle.

## Completed in the current slice

- LDA, FEC, and regulatory docket fixture scripts write normalized CSVs into `data/raw/`.
- `CalibrationDataLoader` maps normalized fixture rows into issue funding scales, disclosure lag, traceability, and docket priors.
- `ClientFundingModel` replenishes lobby budgets from `InterestClient` exposure and writes client-to-lobby flows into `ContributionLedger`.
- Rulemaking comments are represented by `Docket`, `PublicComment`, and `CommentCampaign` records.
- Evasion now has explicit opacity, disclosure-lag, and legal-risk parameters.
- Scenario reports include client funding, donor concentration, disclosure lag, comment authenticity, template saturation, technical credibility, and evasion penalties.
- Scenario reports also include client-funding adaptation, regulator attention, and watchdog focus.
- `make sensitivity` sweeps enforcement, disclosure, public financing, cooling-off, and evasion freedom.
- `make mechanism-comparison` compares the visible single-channel baseline, multi-channel/no-substitution model, and substitution-enabled model for the same reform-heavy contest family.
- `make ablation` removes each full-bundle reform component and ranks capture openings.
- `make interactions` runs two-way sweeps for enforcement/disclosure, public financing/evasion, and cooling-off/revolving-door strategy.
- `make validate` compares report metrics against benchmark plausibility bands and writes CSV/Markdown summaries.
- Report manifests record command, source Git state, runtime provenance, seed/runs/contests, and calibration checksum. The committed review artifacts use a stable runtime-provenance label so Java 21 CI and local Java runtimes do not rewrite otherwise identical report snapshots.
- `docs/research/research-synthesis.md` and `data/calibration/parameter-map.csv` translate the Deep Research reports into model and validation targets.
- Comment triage reports unique-information share, review burden, duplicate compression, procedural acknowledgment, and substantive uptake.
- Influence substitution reports pressure to switch, preserved influence capacity, hidden influence, messenger substitution, venue substitution, and net transparency gain.
- Influence-network diagnostics report path opacity, donor concentration, intermediary centrality, official-access centrality, procurement exposure, revolving-door bridges, comment-network load, venue-shift load, and legibility.
- `make portfolio` screens research-backed reform portfolio families by total distortion, hidden capture, substitution risk, administrative burden, network opacity, legitimate-advocacy chill, speech-restriction risk, cross-venue detection, and participation protection.
- The substitution audit now distinguishes distortion failures, hidden-capture warnings, hidden-influence warnings, substitution warnings, and channel-shift tradeoffs instead of treating every hidden-metric increase as a failure.
- `docs/source-data-roadmap.md` records the direct/proxy/restricted public-data roadmap for LDA, FEC, IRS, nonprofit, procurement, rulemaking, witness, advisory-committee, OGE, OpenSecrets, LegiStorm, and ProPublica-style panels.
- `make snapshot-2024-env` writes a closed-window snapshot manifest and freezes normalized rows for the 2024 environmental validation slice.
- `scripts/run-2024-env-live-snapshot.sh` executes the pinned 2024 EPA/ENV live run, preserves ignored raw payloads, and records public API rate-limit gaps.
- The default live-run pipeline uses source-native no-key NYC CFB public-financing rows, NYC CFB intermediary rows, IRS EO BMF nonprofit/association capacity rows, and IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows when configured. These replace fixture fallback for the default refresh path, but the dark-money bridge remains a capacity proxy rather than direct observed hidden donor/expenditure data.
- `--live` fetch modes can normalize caller-provided CSVs or query LDA, OpenFEC, Regulations.gov, and Federal Register APIs directly.
- Source-native parser fixtures exercise LDA, OpenFEC contribution, OpenFEC electioneering, OpenFEC communication-cost, Regulations.gov, Federal Register, USAspending award JSON, and USAspending transaction JSON without network access.
- Live source fetches retry transient `429` and `5xx` responses and redact API keys from error URLs.
- `make source-moments` records direct source-level top-k concentration, traceability, Schedule E outside-spending, direct dark-money visibility, public-financing, procurement bridge, revolving-door, and comment-record moments.
- `make calibration-queue` classifies validation misses and partial overlaps into actionable work categories.
- `make tables` regenerates paper table inputs from report CSV snapshots using `paper/tables.yml`.
- `make figures` regenerates the paper's numbered SVG/PDF figure assets and LaTeX wrappers.
- Adaptive institutions now include per-client/per-domain funding memory, regulator queue pressure, watchdog monitoring budget allocation, adaptation speed, and reform-decay pressure.
- The paper now has a Regulation & Governance framing, a Wiley-template wrapper, a word-count check, a standalone submission-package check, a release-tag exactness gate, and a separate submission strategy note.

## 1. Maintain the Regulation & Governance submission package

The main manuscript, supplement, Wiley wrapper, generated figures/tables, and submission ZIP are now built through the review pipeline. Future edits should preserve that separation rather than moving implementation inventory back into the main article.

Deliverables:

- keep the main article focused on the model mechanism, empirical bridge, curated result tables, and governance implication;
- keep full scenario catalogs, sensitivity matrices, ablation matrices, implementation details, and parser details in the supplement or repository reports;
- run `make paper-artifacts-check` after any manuscript, report, table, figure, or submission-bundle change;
- advance the release tag in `scripts/check-paper-artifacts.py` and `paper/sections/submission-declarations.tex` whenever the review bundle changes;
- prepare a separate anonymized package only if the paper is retargeted to a double-blind venue.

## 2. Expand the empirical source panels beyond the current 2024 EPA/ENV snapshot

The latest key-backed live run now completes the LDA, six-committee OpenFEC, Schedule E outside-spending, Regulations.gov, Federal Register, USAspending enrichment, and LDA-derived revolving-door requests. OpenFEC electioneering and communication-cost request paths are implemented, but the pinned snapshot still has zero electoral-communication rows. Public financing and intermediary panels now have source-native no-key paths, but their geographic/program scope remains narrower than a national calibration panel.

Deliverables:

- add direct dark-money identifiers and lobbyist-bundling rows rather than treating Schedule E, electioneering, communication-cost, or IRS opaque-capacity proxy rows as observed hidden-donor routing;
- replace the public-financing bridge with representative voucher and matching-fund source panels;
- add IRS 8871/8872, TEOS, and Form 990 XML rows for 527s, 501(c)(4)s, 501(c)(6)s, think tanks, associations, and nonprofit intermediaries;
- add FACA, House witness disclosure, and OGE panels for sponsored-expert, advisory-committee, and official-access bridges;
- expand the LDA-derived revolving-door bridge with documented post-employment movement, advisory-committee, witness, OGE, or licensed personnel panels;
- preserve raw source payloads outside git if they are too large;
- archive updated row counts and filter settings in `docs/validation.md`;
- compare normalized live distributions against the current snapshot and deterministic fixtures;
- rerun `make snapshot-2024-env source-moments validate calibration-queue paper` and commit the refreshed artifacts.

## 3. Broaden SAM/FPDS, revolving-door, and intermediary source panels

The source-moment layer now covers LDA, OpenFEC party/Schedule E rows, zero-row electioneering/communication-cost coverage diagnostics, regulatory dockets, USAspending award, bridge, and action-panel fields, public-financing bridge rows, and LDA-derived covered-position rows. Procurement, revolving-door, intermediary, and electoral-communication validation still need richer representative data rather than narrow, missing, or fixture-backed panels.

Deliverables:

- expand the USAspending action-panel bridge into representative SAM/FPDS UEI, PIID, action-level modification, exclusion, award-action, and protest coverage;
- add source moments for single-bid exposure, ex-post modification risk, price-only awards, award concentration, and procurement firewall coverage;
- expand the revolving-door import path beyond covered-position indicators and keep headcount share separate from influence intensity;
- update `data/calibration/parameter-map.csv` so procurement and revolving-door rows point at direct source moments where possible.

## 4. Work down the P1 calibration queue

`reports/calibration-queue.md` now identifies the highest-priority remaining gaps.

Deliverables:

- tune comment authenticity, comment compression, unique-information weight, detection, and sanction incidence;
- decide whether high-end Super PAC and opaque-capacity large-donor dependence should be scenario-specific rather than applied to every report;
- add scenario coverage where hidden substitution and revolving-door influence are intentionally stressed; the current catalog now includes visible-ban dark-money leakage, meeting-log intermediary leakage, public-finance outside-spending leakage, and comment-authenticity technical-substitution stress cases;
- replace synthetic influence-network diagnostics with direct network panels where sources permit.
- split speech-restriction risk, legitimate-advocacy chill, false-positive costs, and participation protection in the paper's portfolio interpretation.
