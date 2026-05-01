# Next Steps

The simulator now has a lobbying-centered MVP with calibration fixtures, source-native live calibration downloaders, source JSON parser fixtures, explicit client funding, rulemaking comment dockets, evasion profiles, adaptive clients/regulators/watchdogs, campaign reports, sensitivity sweeps, ablation sweeps, interaction sweeps, validation summaries, generated paper tables, and a working paper scaffold.

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
- `--live` fetch modes can normalize caller-provided CSVs or query LDA, OpenFEC, Regulations.gov, and Federal Register APIs directly.
- Source-native parser fixtures exercise LDA, OpenFEC, Regulations.gov, and Federal Register JSON without network access.
- Live source fetches retry transient `429` and `5xx` responses and redact API keys from error URLs.
- `make tables` regenerates paper table inputs from report CSV snapshots using `paper/tables.yml`.
- Adaptive institutions now include per-client/per-domain funding memory, regulator queue pressure, watchdog monitoring budget allocation, adaptation speed, and reform-decay pressure.

## 1. Validate live source snapshots against official bulk/API extracts

The source-native fixture tests cover parser shape, but the empirical bridge still needs a documented live snapshot workflow.

Deliverables:

- choose pinned date ranges and agencies/committees for first live snapshots;
- run each source-native fetch with real credentials where required;
- archive row counts and filter settings in `docs/validation.md`;
- compare normalized live distributions against the existing synthetic fixtures.

## 2. Tighten calibration-fit diagnostics

The first validation target exists, but the benchmark catalog is still thin and mostly broad plausibility bands.

Deliverables:

- add benchmark rows for dark-money traceability, disclosure lag, comment template saturation, regulator queue burden, and adaptation speed;
- classify benchmark quality as observed, proxy, or judgmental;
- add a paper subsection distinguishing benchmark fit, stylized mechanism, and unexplained residual.

## 3. Expand reform interaction experiments

The first interaction sweep exists, but it is still table/report oriented.

Deliverables:

- interaction plots or tables for the paper;
- interpretation notes on where reforms complement each other versus displace influence into other channels.
- optional three-way stress test for disclosure, enforcement, and evasion freedom.
