# Lobby Capture Simulator

Standalone Java simulation focused on lobbying, money in politics, regulatory capture, and anti-capture reforms.

The current implementation is the first runnable slice of `PROJECT_PLAN.md`. It treats lobby organizations as strategic budget allocators across influence channels, then resolves outcomes in legislative, rulemaking, election, procurement, litigation, enforcement, and public-information arenas.

## Run

```sh
make test
make run ARGS="--list"
make run ARGS="--scenario reform-threat-mobilization --runs 10 --contests 30 --seed 7"
make campaign
```

`make campaign` writes:

- `reports/lobby-capture-campaign.csv`
- `reports/lobby-capture-campaign.md`

## Current Modeling Slice

The MVP answers a narrow question from the project plan:

> When organized interests face a meaningful anti-capture reform threat, do they shift from ordinary policy capture to defensive reform blocking, and which reforms remain effective after that adaptation?

It includes:

- finite disclosed, dark-money, legal, campaign, grassroots, and research budgets;
- adaptive channel selection and channel-return memory;
- direct access, agenda access, information distortion, public campaigns, litigation threats, campaign finance, dark money, revolving-door access, and defensive reform spending;
- arena-specific capture susceptibility;
- transparency, public financing, democracy vouchers, cooling-off, blind review, public advocates, enforcement, anti-astroturf systems, defensive-spend caps, and dark-money disclosure;
- raw and composite scenario metrics.

The formulas are stylized and comparative. Empirical files under `data/calibration/` are benchmark scaffolds, not causal estimates.

