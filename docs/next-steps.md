# Next Steps

The simulator now has a lobbying-centered MVP with calibration fixtures, source-native live calibration downloaders, explicit client funding, rulemaking comment dockets, evasion profiles, adaptive clients/regulators/watchdogs, campaign reports, sensitivity sweeps, ablation sweeps, generated paper tables, and a working paper scaffold.

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
- `--live` fetch modes can normalize caller-provided CSVs or query LDA, OpenFEC, Regulations.gov, and Federal Register APIs directly.
- `make tables` regenerates paper table inputs from report CSV snapshots.

## 1. Add live-data fixtures and rate-limit guards

The source-native fetchers now exist, but their network behavior should be made safer before routine use.

Deliverables:

- checked-in tiny JSON fixtures that mirror representative LDA, OpenFEC, Regulations.gov, and Federal Register responses;
- parser tests for those JSON fixtures without hitting the network;
- backoff/rate-limit handling for source-native live runs;
- clearer failure messages for empty result sets and authentication errors.

## 2. Improve adaptation realism

Clients, regulators, and watchdogs now adapt, but the behavior is still compact and aggregate.

Deliverables:

- per-client funding memory by issue domain rather than one multiplier per client;
- regulator staff queues and comment-processing capacity constraints;
- watchdog monitoring budgets allocated across issue domains;
- adaptation-speed and reform-decay diagnostics.

## 3. Move table selection into declarative config

The paper tables are generated, but row/column selection is still embedded in Python.

Deliverables:

- `paper/tables.yml` defining source report, selected rows, selected columns, labels, and captions;
- generator support for multiple paper table variants;
- one-line provenance comments at the top of each generated table.
