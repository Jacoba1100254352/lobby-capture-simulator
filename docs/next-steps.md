# Next Steps

The simulator now has a lobbying-centered MVP with calibration fixtures, explicit client funding, rulemaking comment dockets, evasion profiles, campaign reports, sensitivity sweeps, and a working paper scaffold.

## Completed in the current slice

- LDA, FEC, and regulatory docket fixture scripts write normalized CSVs into `data/raw/`.
- `CalibrationDataLoader` maps normalized fixture rows into issue funding scales, disclosure lag, traceability, and docket priors.
- `ClientFundingModel` replenishes lobby budgets from `InterestClient` exposure and writes client-to-lobby flows into `ContributionLedger`.
- Rulemaking comments are represented by `Docket`, `PublicComment`, and `CommentCampaign` records.
- Evasion now has explicit opacity, disclosure-lag, and legal-risk parameters.
- Scenario reports include client funding, donor concentration, disclosure lag, comment authenticity, template saturation, technical credibility, and evasion penalties.
- `make sensitivity` sweeps enforcement, disclosure, public financing, cooling-off, and evasion freedom.

## 1. Replace fixture fetchers with live-data normalizers

The current scripts deliberately copy tracked normalized fixtures. The next data step is to add optional live download modes while preserving deterministic fixture mode for tests and paper snapshots.

Deliverables:

- `scripts/fetch-lda.sh --live` downloads current LDA bulk data and writes the same normalized schema.
- `scripts/fetch-fec.sh --live` pulls FEC committee, candidate, and outside-spending slices from a configured API key.
- `scripts/fetch-regulatory.sh --live` pulls Federal Register and Regulations.gov slices into the existing docket schema.
- Importers should validate column names and fail with actionable errors when source schemas drift.

## 2. Add ablation reporting

Sensitivity sweeps vary one reform dimension at a time. The next reporting layer should remove one component from the full anti-capture bundle at a time.

Deliverables:

- `make ablation`;
- scenarios for no enforcement, no beneficial-owner disclosure, no public financing, no cooling-off, no anti-astroturf authentication, and no public advocate;
- a compact report showing which missing reform opens the largest capture path.

## 3. Deepen actor adaptation

Lobby organizations currently update strategy from channel returns. Add longer-horizon adaptation by clients, regulators, and watchdogs.

Deliverables:

- clients update funding intensity based on realized private returns and sanctions;
- regulators update staff attention and public-advocate reliance after comment manipulation;
- watchdogs allocate monitoring to high-opacity domains;
- paper-facing metrics for adaptation speed and reform decay.

## 4. Build paper tables from stable snapshots

The paper now describes methods and the empirical bridge. The next paper increment should stop hand-copying tables and load stable report snapshots through a small generator.

Deliverables:

- a script that extracts selected rows from `reports/lobby-capture-campaign.csv` and `reports/lobby-capture-sensitivity.csv`;
- generated LaTeX tables under `paper/tables/`;
- paper text that cites exact snapshot seeds and generation commands.
