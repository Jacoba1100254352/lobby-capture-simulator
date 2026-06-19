# First-Wave Linkage Candidates

This report mines the frozen normalized source snapshot for automated actor-name overlaps that could seed the first-wave venue-shifting and substitution source products. It is a candidate-generation artifact only: these rows do not clear the first-wave source-product gate, calibrated-policy claims, or venue-shifting detection claims.

## Summary

- Candidate status: `candidate_only_not_source_product`
- Candidate source records scanned: `35632`
- Cross-source candidate actors: `659`
- Cross-venue candidate actors: `140`
- Source systems represented: `9`
- Venues represented: `7`
- P1 manual-review candidates: `103`
- Production promotion path: manually adjudicate candidates into `data/calibration/first-wave/canonical-actor-identifiers.csv`, `alias-resolution-audit-sample.csv`, `false-match-review-log.csv`, and `linked-actor-issue-venue-time.csv` before any estimation.

## Review Triage

Review priority is a deterministic worklist ordering, not an adjudicated confidence score. It gives higher priority to shared public identifiers, more venues, more source systems, repeated source rows, and larger normalized activity while flagging likely false-match risks.

| Review priority | Candidate actors |
| --- | ---: |
| P1-manual-review | 103 |
| P2-manual-review | 555 |
| P3-manual-review | 1 |

| Linkage evidence class | Candidate actors |
| --- | ---: |
| shared-source-identifier-overlap | 615 |
| cross-venue-name-overlap | 43 |
| same-venue-multi-source-name-overlap | 1 |

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

| Candidate | Priority | Evidence class | Type | Sources | Venues | Records | Activity | Risk flags | Review action |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| ALLIANCE FOR TELECOMMUNICATIONS INDUSTRY SOLUTIONS | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge; USAspending agency actions | intermediary; opaque_nonprofit_or_dark_money; procurement | 4 | 0.3244 | procurement-name-overlap-requires-UEI-review | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BERGER ACTION FUND INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 7.6408 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| American Petroleum Institute | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 9 | 6.3054 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CREDIT UNION NATIONAL ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.4939 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| EDISON ELECTRIC INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.4437 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INVESTMENT COMPANY INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.9961 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CENTER FOR VOTER INFORMATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 3 | 1.7604 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF MANUFACTURERS OF THE USA | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4811 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| PLASTICS INDUSTRY ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4061 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN GAS ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.0157 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ENTERTAINMENT SOFTWARE ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9776 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF SOCIAL WORKERS INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9157 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CRUISE LINES INTERNATIONAL ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8919 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| RECORD INDUSTRY ASSOCIATION OF AMERICA INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8913 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| FUTURES INDUSTRY ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8659 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN ASSOCIATION FOR JUSTICE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8297 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INTERNATIONAL BAR ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7572 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| COUNCIL OF INSURANCE AGENTS & BROKERS | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7052 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| B S A BUSINESS SOFTWARE ALLIANCE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7031 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| HEALTHCARE DISTRIBUTION ALLIANCE HDA | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.6815 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN HOTEL & LODGING ASSOCIATION DIRECTORY CORPORATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.6596 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| PERSONAL CARE PRODUCTS COUNCIL | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.6040 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN IMMIGRATION LAWYERS ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.5443 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| RETAIL INDUSTRY LEADERS ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.5372 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INFORMATION TECHNOLOGY INDUSTRY COUNCIL LTD | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.5333 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| U S RUSSIA FOUNDATION FOR ECNOMIC ADVANCEMENT AND THE RULE OF LAW | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.4990 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ASSOCIATION OF AMERICAN PUBLISHERS INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 3 | 0.4546 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN CLEANING INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.3863 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| FINANCIAL SERVICES INSTITUTE INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2899 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| PUBLIC AFFAIRS COUNCIL INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2843 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL PHARMACEUTICAL COUNCIL INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2623 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL GAY & LESBIAN CHAMBER OF COMMERCE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2585 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF CLEAN WATER AGENCIES | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2573 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF THEATRE OWNERS | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2573 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INSURED RETIREMENT INSTITUTE INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2228 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN CLINICAL LABORATORY ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.2189 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN IRON AND STEEL INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.1931 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ASSOCIATION FOR HEALTH CENTER AFFILIATED HEALTH PLANS | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.1923 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| US CHINA BUSINESS COUNCIL | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.1816 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| HOUSEHOLD & COMMERICAL PRODUCTS ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.1792 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |

## Claim Boundary

Automated normalized-name overlap is not evidence that records refer to the same legal entity, funder, beneficial owner, or coordinated influence strategy. The report is useful because it turns the next empirical task into a reviewable worklist, not because it validates substitution magnitudes. Any promoted first-wave source product must preserve manual decisions, false-positive and false-negative checks, issue-code comparability, and source-record provenance.

## Next Steps

1. Review the highest-coverage candidates and assign durable `canonicalActorId` values.
2. Populate the alias-resolution audit sample with positive and negative decisions.
3. Map a narrow issue ontology across LDA, electoral, intermediary, nonprofit, procurement, and rulemaking surfaces.
4. Generate the linked actor-issue-venue-time table only after the manual audit records false-match risk.
