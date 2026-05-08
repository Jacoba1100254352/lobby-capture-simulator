# Deep Research Prompts for the Next Expansion

Use these prompts with ChatGPT Deep Research. The desired output is source-backed research that can be translated directly into simulator code, calibration rows, validation scripts, and paper limitations.

## Prompt 1: Public Data Source Inventory for Influence Networks

I am building an agent-based simulator of lobbying, money in politics, regulatory capture, and anti-capture reforms. The model now tracks visible capture, hidden capture, total influence distortion, substitution failure risk, and synthetic influence-network diagnostics such as network opacity, donor concentration, intermediary centrality, official-access centrality, procurement exposure, revolving-door bridge strength, comment-network load, venue-shift load, and network legibility.

Please produce a source-backed inventory of public or obtainable datasets that could empirically anchor these network diagnostics in the United States. Focus on:

- Lobbying Disclosure Act data, LD-2/LD-203 fields, covered officials, clients, registrants, issue codes, and disclosure timing.
- FEC/OpenFEC, independent expenditures, electioneering communications, lobbyist bundling, Super PAC flows, party committees, and donor concentration.
- Dark-money and outside-spending sources, including OpenSecrets, IRS Form 990/8872, 501(c)(4), 501(c)(6), trade associations, and known limitations.
- Think tanks, trade associations, sponsored experts, model comments, white papers, and public sponsorship disclosure sources.
- Revolving-door data sources, including OpenSecrets, LegiStorm, ProPublica, agency ethics disclosures, financial disclosures, cooling-off records, and licensing/coverage limits.
- USAspending, SAM.gov, FPDS/contract award fields, contract modifications, protests, subcontracting, and procurement concentration.
- Regulations.gov and Federal Register comment, docket, meeting, and rulemaking timeline fields.

For each dataset, identify URL/access path, required keys or licenses, fields available, temporal coverage, update frequency, reliability, matching keys, restrictions, and how it could map to simulator metrics. Separate direct observed measures, proxies, and unusable/too-restricted sources. End with a prioritized acquisition plan for a 2024 EPA/environmental-policy validation slice and a broader multi-domain slice.

## Prompt 2: Empirical Parameter Ranges for Substitution and Capture

I need empirical ranges, not generic theory, for calibrating a lobbying/regulatory-capture simulator. The current model separates observed capture, hidden capture, total influence distortion, substitution failure risk, defensive reform spending, administrative burden, and influence-network opacity. Please review political science, public administration, law, economics, and empirical watchdog literature to identify plausible ranges or source-backed proxies for:

- Substitution from registered lobbying to dark money, outside spending, advisory work, trade associations, think tanks, sponsored expertise, litigation, procurement routes, or public-information campaigns.
- Effects of transparency systems, real-time disclosure, meeting logs, beneficial-owner disclosure, and machine-readable records on visibility and enforcement.
- Public financing, matching funds, democracy vouchers, donor-base broadening, candidate uptake, and limits on large-donor dependence.
- Cooling-off periods, revolving-door restrictions, shadow lobbying, and enforcement/circumvention patterns.
- Comment flooding, template campaigns, fake/misattributed comments, duplicate compression, authentication rates, and agency substantive uptake.
- Procurement capture: vendor concentration, award concentration, contract modifications, protests, procurement firewalls, and revolving-door procurement links.
- Enforcement capacity: audit rates, sanction probabilities, penalties, delays, agency budgets, false positives, and legal challenges.

Return a table with metric, proposed low/mid/high range, source, evidence type, geographic/sectoral scope, date range, confidence, caveats, and recommended simulator mapping. Clearly separate empirical estimates, proxies, expert judgment, and speculative design assumptions. Flag any ranges that should not be used in a journal paper without additional validation.

## Prompt 3: Reform Portfolio Design and Failure Modes

I am evaluating anti-capture reforms in a simulator where the best reform is the one that minimizes total influence distortion, not merely visible lobbying or measured capture. Please research reform portfolios and failure modes for:

- Hard lobbying budgets and access limits.
- Public-interest representation funds and public advocate offices.
- Randomized audits and sanctions.
- Real-time disclosure with machine-readable meeting logs.
- Cooling-off periods with enforcement.
- Comment-authenticity rules and anti-astroturf systems.
- Public financing, democracy vouchers, and matching funds.
- Procurement firewalls, blind specification review, and vendor-contact rules.
- Venue-shifting detection across lobbying, campaign finance, litigation, procurement, rulemaking, and public information.

For each reform, identify intended mechanism, implementation examples, legal/constitutional constraints, administrative burden, false-positive risk, enforcement requirements, known evasion routes, equity/representation effects, and interaction effects with other reforms. Then propose 6-10 realistic reform portfolios that can be simulated, with expected tradeoffs and measurable indicators. The output should distinguish empirical claims, synthetic modeling hypotheses, and speculative design recommendations.
