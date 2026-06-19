# First-Wave Linkage Candidates

This report mines the frozen normalized source snapshot for automated actor-name overlaps that could seed the first-wave venue-shifting and substitution source products. It is a candidate-generation artifact only: these rows do not clear the first-wave source-product gate, calibrated-policy claims, or venue-shifting detection claims.

## Summary

- Candidate status: `candidate_only_not_source_product`
- Candidate source records scanned: `35632`
- Cross-source candidate actors: `659`
- Cross-venue candidate actors: `140`
- Source systems represented: `9`
- Venues represented: `7`
- Production promotion path: manually adjudicate candidates into `data/calibration/first-wave/canonical-actor-identifiers.csv`, `alias-resolution-audit-sample.csv`, `false-match-review-log.csv`, and `linked-actor-issue-venue-time.csv` before any estimation.

## Source Coverage

| Source system | Candidate records |
| --- | ---: |
| IRS/ProPublica dark-money bridge | 410 |
| Intermediary bridge | 1706 |
| LDA | 242 |
| LDA revolving-door proxy | 803 |
| OpenFEC | 2536 |
| Public financing | 140 |
| USAspending agency actions | 28095 |
| USAspending awards | 200 |
| USAspending national actions | 1500 |

## Venue Coverage

| Venue | Candidate records |
| --- | ---: |
| countervailing_finance | 140 |
| electoral_money | 2536 |
| intermediary | 1706 |
| opaque_nonprofit_or_dark_money | 410 |
| procurement | 29795 |
| revolving_door | 803 |
| visible_lobbying | 242 |

## Cross-Source Pair Counts

| Source pair | Candidate actors |
| --- | ---: |
| USAspending agency actions + USAspending national actions | 432 |
| IRS/ProPublica dark-money bridge + Intermediary bridge | 97 |
| USAspending agency actions + USAspending awards | 93 |
| LDA + LDA revolving-door proxy | 34 |
| USAspending awards + USAspending national actions | 6 |
| Intermediary bridge + USAspending agency actions | 5 |
| IRS/ProPublica dark-money bridge + OpenFEC | 1 |
| IRS/ProPublica dark-money bridge + USAspending agency actions | 1 |
| Intermediary bridge + LDA revolving-door proxy | 1 |
| Intermediary bridge + OpenFEC | 1 |
| LDA revolving-door proxy + USAspending agency actions | 1 |
| OpenFEC + USAspending agency actions | 1 |

## Cross-Venue Source Pair Counts

| Source pair | Cross-venue candidate actors |
| --- | ---: |
| IRS/ProPublica dark-money bridge + Intermediary bridge | 97 |
| LDA + LDA revolving-door proxy | 34 |
| Intermediary bridge + USAspending agency actions | 5 |
| IRS/ProPublica dark-money bridge + OpenFEC | 1 |
| IRS/ProPublica dark-money bridge + USAspending agency actions | 1 |
| Intermediary bridge + LDA revolving-door proxy | 1 |
| Intermediary bridge + OpenFEC | 1 |
| LDA revolving-door proxy + USAspending agency actions | 1 |
| OpenFEC + USAspending agency actions | 1 |

## Top Candidate Actors

| Candidate | Type | Sources | Venues | Records | Activity | Review action |
| --- | --- | --- | --- | ---: | ---: | --- |
| ALLIANCE FOR TELECOMMUNICATIONS INDUSTRY SOLUTIONS | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge; USAspending agency actions | intermediary; opaque_nonprofit_or_dark_money; procurement | 4 | 0.3244 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| MEHLMAN CONSULTING, INC. | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 57 | 19.0700 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| THE ALBERT B SABIN VACCINE INSTITUTE INC | cross_venue | Intermediary bridge; USAspending agency actions | intermediary; procurement | 2 | 17.1418 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BROWNSTEIN HYATT FARBER SCHRECK, LLP | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 40 | 13.2600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BGR GOVERNMENT AFFAIRS | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 25 | 8.1600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| HOLLAND & KNIGHT LLP | cross_venue | LDA revolving-door proxy; USAspending agency actions | procurement; revolving_door | 24 | 7.8505 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BERGER ACTION FUND INC | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 7.6408 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| FORBES-TATE | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 21 | 6.4600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| HB STRATEGIES | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 20 | 6.4600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| American Petroleum Institute | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 9 | 6.3054 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| KLEIN/JOHNSON GROUP | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 16 | 5.1000 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INVARIANT LLC | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 18 | 4.7600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| COASTAL STATES STEWARDSHIP FOUNDATION | cross_venue | Intermediary bridge; USAspending agency actions | intermediary; procurement | 2 | 4.0199 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ALPINE GROUP PARTNERS, LLC. | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 11 | 3.4000 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CORNERSTONE GOVERNMENT AFFAIRS, INC. | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 12 | 3.4000 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| THORN RUN PARTNERS | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 10 | 3.0600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CREDIT UNION NATIONAL ASSOCIATION INC | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.4939 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| EDISON ELECTRIC INSTITUTE | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.4437 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| K&L GATES, LLP | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 10 | 2.3800 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| MERCURY PUBLIC AFFAIRS, LLC | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 9 | 2.3800 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CGCN GROUP, LLC | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 10 | 2.0400 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| GRAYROBINSON PA | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 7 | 2.0400 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INVESTMENT COMPANY INSTITUTE | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.9961 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CENTER FOR VOTER INFORMATION | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 3 | 1.7604 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| FGS GLOBAL (US) LLC (FKA FGH HOLDINGS LLC) | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 6 | 1.7000 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF MANUFACTURERS OF THE USA | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4811 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| PLASTICS INDUSTRY ASSOCIATION INC | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4061 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| American Bankers Association | cross_venue | IRS/ProPublica dark-money bridge; OpenFEC | electoral_money; opaque_nonprofit_or_dark_money | 10 | 1.3609 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BOUNDARY STONE PARTNERS | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 5 | 1.3600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| DESIMONE CONSULTING, LLC | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 5 | 1.3600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| THE FERGUSON GROUP, LLC | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 6 | 1.3600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| FTI GOVERNMENT AFFAIRS | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 8 | 1.3600 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| DAVIDOFF HUTCHER & CITRON, LLP | cross_venue | Intermediary bridge; LDA revolving-door proxy | intermediary; revolving_door | 4 | 1.0203 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| MICHAEL BEST STRATEGIES LLC | cross_venue | LDA; LDA revolving-door proxy | revolving_door; visible_lobbying | 5 | 1.0200 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN GAS ASSOCIATION | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.0157 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ENTERTAINMENT SOFTWARE ASSOCIATION | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9776 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN RESOLVE PAC, INC. | cross_venue | Intermediary bridge; OpenFEC | electoral_money; intermediary | 5 | 0.9368 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF SOCIAL WORKERS INC | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9157 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN CHEMISTRY COUNCIL INC | cross_venue | OpenFEC; USAspending agency actions | electoral_money; procurement | 5 | 0.8939 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CRUISE LINES INTERNATIONAL ASSOCIATION INC | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8919 | manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |

## Claim Boundary

Automated normalized-name overlap is not evidence that records refer to the same legal entity, funder, beneficial owner, or coordinated influence strategy. The report is useful because it turns the next empirical task into a reviewable worklist, not because it validates substitution magnitudes. Any promoted first-wave source product must preserve manual decisions, false-positive and false-negative checks, issue-code comparability, and source-record provenance.

## Next Steps

1. Review the highest-coverage candidates and assign durable `canonicalActorId` values.
2. Populate the alias-resolution audit sample with positive and negative decisions.
3. Map a narrow issue ontology across LDA, electoral, intermediary, nonprofit, procurement, and rulemaking surfaces.
4. Generate the linked actor-issue-venue-time table only after the manual audit records false-match risk.
