# Next Steps

The simulator now has a lobbying-centered MVP with calibration fixtures, source-native live calibration downloaders, source JSON parser fixtures, explicit client funding, rulemaking comment dockets, comment triage, evasion profiles, an influence-substitution engine, adaptive clients/regulators/watchdogs, campaign reports, sensitivity sweeps, ablation sweeps, interaction sweeps, validation summaries, calibration queues, source moments, generated paper tables and figures, a 2024 EPA/ENV snapshot, and a working paper scaffold.

## Completed in the current slice

- LDA, FEC, and regulatory docket fixture scripts write normalized CSVs into `data/raw/`.
- `CalibrationDataLoader` maps normalized fixture rows into issue funding scales, disclosure lag, traceability, and docket priors.
- `ClientFundingModel` replenishes lobby budgets from `InterestClient` exposure and writes client-to-lobby flows into `ContributionLedger`.
- Rulemaking comments are represented by `Docket`, `PublicComment`, and `CommentCampaign` records.
- Evasion now has explicit opacity, disclosure-lag, and legal-risk parameters.
- Scenario reports include client funding, donor concentration, disclosure lag, comment authenticity, template saturation, technical credibility, and evasion penalties.
- Scenario reports also include client-funding adaptation, regulator attention, and watchdog focus.
- `make sensitivity` sweeps enforcement, disclosure, public financing, cooling-off, and evasion freedom.
- `make ablation` removes each full-bundle reform component and ranks capture openings.
- `make interactions` runs two-way sweeps for enforcement/disclosure, public financing/evasion, and cooling-off/revolving-door strategy.
- `make validate` compares report metrics against benchmark plausibility bands and writes CSV/Markdown summaries.
- Report manifests record command, source Git state, Java version, seed/runs/contests, and calibration checksum.
- `docs/research/research-synthesis.md` and `data/calibration/parameter-map.csv` translate the Deep Research reports into model and validation targets.
- Comment triage reports unique-information share, review burden, duplicate compression, procedural acknowledgment, and substantive uptake.
- Influence substitution reports pressure to switch, preserved influence capacity, hidden influence, messenger substitution, venue substitution, and net transparency gain.
- `make snapshot-2024-env` writes a closed-window snapshot manifest and freezes normalized rows for the 2024 environmental validation slice.
- `scripts/run-2024-env-live-snapshot.sh` executes the pinned 2024 EPA/ENV live run, preserves ignored raw payloads, and records public API rate-limit gaps.
- The current committed 2024 EPA/ENV snapshot has 13 LDA rows, 100 OpenFEC rows, and 100 Federal Register regulatory rows; Regulations.gov and two OpenFEC committee requests were blocked by public/demo rate limits.
- `--live` fetch modes can normalize caller-provided CSVs or query LDA, OpenFEC, Regulations.gov, and Federal Register APIs directly.
- Source-native parser fixtures exercise LDA, OpenFEC, Regulations.gov, and Federal Register JSON without network access.
- Live source fetches retry transient `429` and `5xx` responses and redact API keys from error URLs.
- `make source-moments` records direct source-level top-k concentration, traceability, and comment-record moments.
- `make calibration-queue` classifies validation misses and partial overlaps into actionable work categories.
- `make tables` regenerates paper table inputs from report CSV snapshots using `paper/tables.yml`.
- `make figures` regenerates the paper interaction tradeoff figure.
- Adaptive institutions now include per-client/per-domain funding memory, regulator queue pressure, watchdog monitoring budget allocation, adaptation speed, and reform-decay pressure.

## 1. Rerun the 2024 EPA/ENV live snapshot with personal API keys

The first live run used public/demo access. It produced a useful snapshot, but public rate limits blocked Regulations.gov and two OpenFEC committee requests.

Deliverables:

- rerun `scripts/run-2024-env-live-snapshot.sh` with personal `FEC_API_KEY` and `REGULATIONS_API_KEY`;
- preserve raw source payloads outside git if they are too large;
- archive updated row counts and filter settings in `docs/validation.md`;
- compare normalized live distributions against the current partial snapshot and deterministic fixtures;
- rerun `make snapshot-2024-env source-moments validate calibration-queue paper` and commit the refreshed artifacts.

## 2. Add USAspending and revolving-door source panels

The source-moment layer now covers LDA, OpenFEC, and regulatory dockets. Procurement and revolving-door validation still need direct data rather than proxy report metrics.

Deliverables:

- add a USAspending fetcher and source moments for top-recipient and top-agency concentration;
- add a revolving-door source panel or import path and keep headcount share separate from influence intensity;
- update `data/calibration/parameter-map.csv` so procurement and revolving-door rows point at direct source moments where possible.

## 3. Work down the P1 calibration queue

`reports/calibration-queue.md` now identifies the highest-priority remaining gaps.

Deliverables:

- tune comment authenticity, comment compression, unique-information weight, detection, and sanction incidence;
- decide whether high-end Super PAC large-donor dependence should be scenario-specific rather than applied to every report;
- add scenario coverage where hidden substitution and revolving-door influence are intentionally stressed.
