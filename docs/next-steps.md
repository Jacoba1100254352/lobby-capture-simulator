# Next Steps

The simulator now has a runnable lobbying-centered MVP. The next work should move in this order.

## 1. Replace synthetic budgets with calibrated distributions

Add importers for LDA registrations/reports and FEC campaign finance data. The immediate goal is not causal inference; it is making lobby budget sizes, issue concentration, disclosure lag, donor concentration, and dark-money traceability look plausible.

Deliverables:

- `scripts/fetch-lda.sh` writes normalized fixture CSV under `data/raw/`.
- `scripts/fetch-fec.sh` writes candidate, committee, independent expenditure, and bundled contribution fixture CSV.
- `CalibrationTargetCatalog` checks generated distributions against `data/calibration/empirical-benchmarks.csv`.

## 2. Add explicit client funding and budget replenishment

The current engine gives lobby organizations fixed initial budgets plus simple success top-ups. Add `InterestClient` funding rules so private gain, regulatory exposure, procurement exposure, and reform threat drive future contributions.

Deliverables:

- client-to-lobby money flows in `ContributionLedger`;
- budget replenishment by issue and arena;
- metrics for funder concentration and donor influence Gini.

## 3. Make rulemaking and comments first-class

The rulemaking arena currently receives pressure from information distortion and astroturfing, but comments are still aggregate variables. Add docket/comment objects and authentication rules.

Deliverables:

- `Docket`, `PublicComment`, and `CommentCampaign` records;
- comment authenticity, template-comment saturation, and technical-claim credibility;
- Regulations.gov/Federal Register validation fixtures.

## 4. Deepen reform evasion

The evasion scenario already shifts toward dark money. Add more explicit substitution paths: trade associations, 501(c)-style dark pools, litigation funding, procurement consultants, and post-government employment.

Deliverables:

- channel-specific legal risk and disclosure lag;
- beneficial-owner disclosure effects;
- evasion penalties when enforcement detects laundering.

## 5. Start sensitivity and ablation reporting

Add campaign modes that sweep enforcement strength, disclosure strength, public financing, cooling-off, and evasion freedom. The paper should rely on these sweeps rather than one baseline campaign.

Deliverables:

- `make sensitivity`;
- `reports/sensitivity-*.csv`;
- paper tables generated from stable report snapshots.

## 6. Paper development

The initial paper scaffold is under `paper/`. The next paper increment should add a methods section that fully specifies the lobby allocation equations and an empirical-bridge section that distinguishes calibrated distributions from synthetic mechanisms.

