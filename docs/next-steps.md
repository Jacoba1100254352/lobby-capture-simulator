# Next Steps

The simulator now has a lobbying-centered MVP with calibration fixtures, optional live calibration normalization, explicit client funding, rulemaking comment dockets, evasion profiles, campaign reports, sensitivity sweeps, ablation sweeps, and a working paper scaffold.

## Completed in the current slice

- LDA, FEC, and regulatory docket fixture scripts write normalized CSVs into `data/raw/`.
- `CalibrationDataLoader` maps normalized fixture rows into issue funding scales, disclosure lag, traceability, and docket priors.
- `ClientFundingModel` replenishes lobby budgets from `InterestClient` exposure and writes client-to-lobby flows into `ContributionLedger`.
- Rulemaking comments are represented by `Docket`, `PublicComment`, and `CommentCampaign` records.
- Evasion now has explicit opacity, disclosure-lag, and legal-risk parameters.
- Scenario reports include client funding, donor concentration, disclosure lag, comment authenticity, template saturation, technical credibility, and evasion penalties.
- `make sensitivity` sweeps enforcement, disclosure, public financing, cooling-off, and evasion freedom.
- `make ablation` removes each full-bundle reform component and ranks capture openings.
- `--live` fetch modes normalize caller-provided LDA, FEC, and regulatory CSVs into the tracked fixture schemas.

## 1. Replace live CSV hooks with source-native downloaders

The current live mode requires explicit CSV paths or URLs. The next data step is to add source-native downloaders that know how to query each upstream service directly while preserving deterministic fixture mode for tests and paper snapshots.

Deliverables:

- `scripts/fetch-lda.sh --live` can discover and download current LDA bulk files without a prebuilt URL.
- `scripts/fetch-fec.sh --live` can pull FEC committee, candidate, and outside-spending slices from a configured API key.
- `scripts/fetch-regulatory.sh --live` can query Federal Register and Regulations.gov APIs by agency/topic/date range.
- Importers should validate column names and fail with actionable errors when source schemas drift.

## 2. Deepen actor adaptation

Lobby organizations currently update strategy from channel returns. Add longer-horizon adaptation by clients, regulators, and watchdogs.

Deliverables:

- clients update funding intensity based on realized private returns and sanctions;
- regulators update staff attention and public-advocate reliance after comment manipulation;
- watchdogs allocate monitoring to high-opacity domains;
- paper-facing metrics for adaptation speed and reform decay.

## 3. Build paper tables from stable snapshots

The paper now describes methods and the empirical bridge. The next paper increment should stop hand-copying tables and load stable report snapshots through a small generator.

Deliverables:

- a script that extracts selected rows from `reports/lobby-capture-campaign.csv` and `reports/lobby-capture-sensitivity.csv`;
- generated LaTeX tables under `paper/tables/`;
- paper text that cites exact snapshot seeds and generation commands.
