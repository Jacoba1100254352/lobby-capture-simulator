# Next Steps

The simulator now has a lobbying-centered model core with calibration fixtures, source-native live calibration downloaders, source JSON parser fixtures, explicit client funding, rulemaking comment dockets, comment triage, evasion profiles, an influence-substitution engine, an influence-network diagnostic layer, adaptive clients/regulators/watchdogs, campaign reports, a mechanism-comparison report, sensitivity sweeps, ablation sweeps, interaction sweeps, reform-portfolio screens, validation summaries, calibration queues, source moments, generated paper tables and figures, a 2024 EPA/ENV snapshot, and a Regulation & Governance-oriented review manuscript with a reproducible Wiley submission bundle.

## Completed in the current slice

- LDA, FEC, and regulatory docket fixture scripts write normalized CSVs into `data/raw/`.
- `CalibrationDataLoader` maps normalized fixture rows into issue funding scales, disclosure lag, traceability, and docket priors.
- `ClientFundingModel` replenishes lobby budgets from `InterestClient` exposure and writes client-to-lobby flows into `ContributionLedger`.
- Rulemaking comments are represented by `Docket`, `PublicComment`, and `CommentCampaign` records.
- Evasion now has explicit opacity, disclosure-lag, and legal-risk parameters.
- Scenario reports include client funding, donor concentration, an operational disclosure-lag blend, separate lobbying and campaign visibility lags, comment authenticity, template saturation, technical credibility, and evasion penalties.
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
- The default live-run pipeline uses source-native no-key NYC CFB public-financing rows, Seattle Democracy Voucher rows, NYC CFB intermediary rows, IRS EO BMF nonprofit/association capacity rows, and IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity proxy rows when configured. These replace fixture fallback for the default refresh path, but the dark-money bridge remains a capacity proxy rather than direct observed hidden donor/expenditure data.
- `--live` fetch modes can normalize caller-provided CSVs or query LDA, OpenFEC, Regulations.gov, and Federal Register APIs directly.
- Source-native parser fixtures exercise LDA, OpenFEC contribution, OpenFEC electioneering, OpenFEC communication-cost, Regulations.gov, Federal Register, USAspending award JSON, USAspending transaction JSON, and SAM.gov Contract Awards JSON without network access.
- The procurement action fetchers now honor the documented `USASPENDING_PROCUREMENT_ACTIONS_*` aliases directly, normalize downloaded SAM.gov Contract Awards CSV/JSON/ZIP exports through `SAM_CONTRACT_AWARDS_LIVE_CSV` or `SAM_CONTRACT_AWARDS_LIVE_URL`, use non-overlapping SAM.gov Contract Awards offset page-index slices plus optional non-adjacent `SAM_CONTRACT_AWARDS_OFFSET_STARTS`, support asynchronous `SAM_CONTRACT_AWARDS_EXTRACT_MODE` JSON/CSV downloads, and bound optional SAM attempts with retry/timeout controls before falling back to USAspending action rows. `make sam-contract-awards-preflight` performs a one-row redacted access/quota check before keyed API refreshes, and `make sam-procurement-refresh` wraps export, extract, and artifact-gate paths behind that guardrail.
- The procurement denominator audit now reports archived bulk-summary, action-row, distinct-award, amount-weighted, agency-mix, fiscal-year, and award-type diagnostics separately, and the procurement benchmark crosswalk remaps concentration and modification ranges to the observed denominators.
- `make test` now includes Python compilation plus `bash -n` shell-script checks through `make script-checks`, and CI uses the same target before simulator and paper-package gates.
- Live source fetches retry transient `429` and `5xx` responses and redact API keys from error URLs.
- `make source-moments` records direct source-level top-k concentration, traceability, Schedule E outside-spending, non-proxy direct dark-money routing row coverage, direct dark-money visibility, public-financing, procurement bridge, revolving-door, and comment-record moments.
- `make calibration-queue` classifies validation misses and partial overlaps into actionable work categories, including scenario-family splits where one validation scope mixes baseline, stress, and extreme-stress rows.
- `make causal-calibration-targets` generates the causal target matrix that must clear before the project can use calibrated policy-simulation language.
- `make first-wave-causal-protocols` translates the first-wave causal targets into protocol-level units, treatments or shocks, comparison designs, linkage keys, falsification checks, sensitivity checks, and claim-upgrade boundaries.
- `make first-wave-source-readiness` maps those protocols to committed source products, bounded/proxy support, missing products, blocking issues, and next source actions.
- `make doi-deposit-readiness-audit` checks the release metadata, primary release assets, checksum handoff files, DOI-record state, and final human-read-through state needed before a final journal submission can be treated as externally complete.
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
- run `make doi-deposit-readiness-audit` after building a release bundle and before DOI deposition, then record the minted DOI and completed human read-through before treating the final-journal-submission gate as cleared;
- advance the release tag in `scripts/check-paper-artifacts.py` and `paper/sections/submission-declarations.tex` whenever the review bundle changes;
- prepare a separate anonymized package only if the paper is retargeted to a double-blind venue.

## 2. Expand the empirical source panels beyond the current 2024 EPA/ENV snapshot

The latest key-backed live run now completes the LDA, six-committee OpenFEC, Schedule E outside-spending, OpenFEC electioneering and communication-cost rows, Regulations.gov, Federal Register, USAspending enrichment, bounded IRS POFD Form 8872 527 rows, and an 803-row LDA-derived covered-position revolving-door bridge. OpenFEC electioneering and communication-cost rows are now present in the pinned snapshot, but the bridge remains bounded and should not be treated as a representative national electoral-spending panel. Public financing and intermediary panels now have source-native no-key paths, but their geographic/program scope remains narrower than a national calibration panel.

Deliverables:

- add hidden-donor identity evidence and lobbyist-bundling rows rather than treating Schedule E, electioneering, communication-cost, IRS opaque-capacity proxy rows, or public Schedule I nonprofit-transfer rows as observed hidden-donor routing;
- broaden the public-financing bridge from NYC matching-fund and Seattle voucher rows into representative federal, state, and additional local voucher and matching-fund source panels;
- broaden the IRS 8871/8872 bridge beyond the default A-G Form 8872 slice and expand TEOS/Form 990 coverage beyond the bounded top-EIN Schedule I importer for 501(c)(4)s, 501(c)(6)s, think tanks, associations, and nonprofit intermediaries;
- add FACA, House witness disclosure, and OGE panels for sponsored-expert, advisory-committee, and official-access bridges;
- expand the LDA-derived revolving-door bridge with documented post-employment movement, advisory-committee, witness, OGE, or licensed personnel panels;
- preserve raw source payloads outside git if they are too large;
- archive updated row counts and filter settings in `docs/validation.md`;
- compare normalized live distributions against the current snapshot and deterministic fixtures;
- rerun `make snapshot-2024-env source-moments validate calibration-queue paper` and commit the refreshed artifacts.

## 3. Broaden SAM/FPDS, revolving-door, and intermediary source panels

The source-moment layer now covers LDA, OpenFEC party/Schedule E/electioneering/communication-cost rows, regulatory dockets, USAspending award, multi-agency bridge, stratified action-panel fields, an archived USAspending bulk transaction summary, a procurement benchmark crosswalk, an optional SAM.gov Contract Awards procurement-action importer, public-financing bridge rows, bounded ProPublica/IRS Schedule I nonprofit-routing rows, and LDA-derived covered-position rows. Procurement modification now has a public bulk denominator and denominator-mapped benchmark ranges; causal procurement-modification capture claims still need SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, and independent calibration targets. Hidden-donor identity, representative nonprofit/intermediary routing, electoral-communication, and revolving-door validation still need richer representative data before the model can claim calibrated national hidden-channel magnitudes.

Deliverables:

- run `make sam-contract-awards-preflight` immediately before any keyed SAM API refresh; if the redacted preflight reports `quota_blocked`, wait until its `nextAccessTime` before rerunning rather than spending the full live snapshot attempt;
- archive a SAM/FPDS action-history crosswalk using `make sam-procurement-refresh`, which normalizes a configured Contract Awards/DataBank CSV/JSON/ZIP export or runs a preflight-gated keyed SAM Contract Awards extract before regenerating the live snapshot and paper artifact gate; compare its UEI, PIID, action-level modification, exclusion, award-action, and protest coverage against the archived USAspending bulk summary and stratified USAspending action panel;
- add source moments for single-bid exposure, ex-post modification risk, price-only awards, award concentration, and procurement firewall coverage;
- expand the revolving-door import path beyond covered-position indicators and keep headcount share separate from influence intensity;
- update `data/calibration/parameter-map.csv` so procurement and revolving-door rows point at direct source moments where possible.

## 4. Work down the remaining calibration queue

`reports/calibration-queue.md` now identifies the highest-priority remaining gaps.
`reports/causal-calibration-targets.md` is stricter than the validation queue and now separates first-wave empirical upgrades from second-wave coverage work. Treat the first-wave rows as the next publication-grade empirical agenda because they are the shortest route from public/source panels to stronger manuscript claims without changing the current mechanism-model boundary.
`reports/first-wave-causal-protocols.md` is the operational workplan for those first-wave rows; use it before collecting or promoting new source panels so the unit of analysis, treatment or shock, comparison design, linkage keys, and falsification checks are fixed before results are inspected.
`reports/first-wave-source-readiness.md` is the source-product gate for the same work; use it to keep design-ready protocols separate from estimation-ready source panels.

Deliverables:

- prioritize the first-wave causal-calibration rows: a cross-source substitution event panel, a SAM/FPDS-style procurement action crosswalk with protest/exclusion/firewall overlays, a docket comment-authenticity and agency-response panel, and an auditable cross-venue entity-resolution spine;
- clear the first-wave source-readiness audit before promoting any protocol to estimation-ready or changing the manuscript's claim posture;
- promote any first-wave source refresh only after the matching protocol row has documented minimum source products, linkage keys, falsification checks, and sensitivity checks;
- extend procurement evidence beyond the denominator-mapped crosswalk with SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, and independent calibration targets before any calibrated policy-simulation claim;
- use `reports/causal-calibration-targets.md` as the stricter policy-claim checklist; source panels that clear mechanism diagnostics still need an external causal design before they clear policy-simulation language;
- keep the cleared campaign/outside-spending `largeDonorDependence` regression covered by tests, while treating broader hidden-donor identity evidence as a separate source-panel expansion rather than a model-tuning item;
- keep venue-substitution and hidden-influence partials as scenario-coverage or scenario-family-split work rather than collapsing baseline, stress, and extreme-stress rows into one benchmark;
- replace synthetic influence-network diagnostics with direct network panels where sources permit;
- preserve the current claim boundary in the paper until the calibrated-policy posture clears in `reports/claim-posture-audit.md`.
