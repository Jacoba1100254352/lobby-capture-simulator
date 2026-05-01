# Next Steps

The simulator now has a lobbying-centered MVP with calibration fixtures, source-native live calibration downloaders, source JSON parser fixtures, explicit client funding, rulemaking comment dockets, comment triage, evasion profiles, an influence-substitution engine, adaptive clients/regulators/watchdogs, campaign reports, sensitivity sweeps, ablation sweeps, interaction sweeps, validation summaries, generated paper tables, a 2024 EPA/ENV snapshot scaffold, and a working paper scaffold.

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
- `--live` fetch modes can normalize caller-provided CSVs or query LDA, OpenFEC, Regulations.gov, and Federal Register APIs directly.
- Source-native parser fixtures exercise LDA, OpenFEC, Regulations.gov, and Federal Register JSON without network access.
- Live source fetches retry transient `429` and `5xx` responses and redact API keys from error URLs.
- `make tables` regenerates paper table inputs from report CSV snapshots using `paper/tables.yml`.
- Adaptive institutions now include per-client/per-domain funding memory, regulator queue pressure, watchdog monitoring budget allocation, adaptation speed, and reform-decay pressure.

## 1. Run the 2024 EPA/ENV live snapshot against official bulk/API extracts

The snapshot scaffold exists, but the empirical bridge still needs an actual live run with credentials and preserved raw payloads.

Deliverables:

- run the pinned 2024 EPA/ENV request templates with real credentials where required;
- preserve raw source payloads outside git if they are too large;
- archive row counts and filter settings in `docs/validation.md`;
- compare normalized live distributions against the existing synthetic fixtures;
- rerun `make snapshot-2024-env` and commit the manifest/normalized summary if row counts are manageable.

## 2. Add source-level moments for concentration and traceability

The parameter map now names the moments, but several current report metrics are normalized proxies rather than direct source moments.

Deliverables:

- add explicit top-k concentration metrics for lobbying clients, FEC donors, and procurement recipients;
- split `darkMoneyTraceability` into average money-flow traceability and dark-only direct visibility;
- split public-financing regime strength from candidate uptake and resident voucher participation;
- keep validation rows labeled as observed, inferred, proxy, sectoral, or judgmental.

## 3. Expand reform interaction experiments into figures

The first interaction sweep exists, and report columns now include substitution metrics. The paper still needs visual interpretation.

Deliverables:

- interaction plots or tables for the paper;
- interpretation notes on where reforms complement each other versus displace influence into other channels.
- optional three-way stress test for disclosure, enforcement, and evasion freedom.
