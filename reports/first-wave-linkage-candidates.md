# First-Wave Linkage Candidates

This report mines the frozen normalized source snapshot for automated actor-name overlaps that could seed the first-wave venue-shifting and substitution source products. It is a candidate-generation artifact only: these rows do not clear the first-wave source-product gate, calibrated-policy claims, or venue-shifting detection claims.

## Summary

- Candidate status: `candidate_only_not_source_product`
- Candidate source records scanned: `38389`
- Cross-source candidate actors: `1067`
- Cross-venue candidate actors: `548`
- Source systems represented: `10`
- Venues represented: `8`
- P1 manual-review candidates: `499`
- Production promotion path: manually adjudicate candidates into `data/calibration/first-wave/canonical-actor-identifiers.csv`, `alias-resolution-audit-sample.csv`, `false-match-review-log.csv`, and `linked-actor-issue-venue-time.csv` before any estimation.

## Review Triage

Review priority is a deterministic worklist ordering, not an adjudicated confidence score. It gives higher priority to shared public identifiers, more venues, more source systems, repeated source rows, and larger normalized activity while flagging likely false-match risks.

| Review priority | Candidate actors |
| --- | ---: |
| P1-manual-review | 499 |
| P2-manual-review | 564 |
| P3-manual-review | 4 |

| Linkage evidence class | Candidate actors |
| --- | ---: |
| shared-source-identifier-overlap | 1010 |
| cross-venue-name-overlap | 54 |
| three-plus-venue-name-overlap | 2 |
| same-venue-multi-source-name-overlap | 1 |

## Source Coverage

| Source system | Candidate records |
| --- | ---: |
| IRS/ProPublica dark-money bridge | 653 |
| Intermediary bridge | 4206 |
| LDA | 242 |
| LDA revolving-door proxy | 803 |
| OpenFEC | 2536 |
| Public financing | 140 |
| Reginfo.gov EO 12866 meetings | 14 |
| USAspending agency actions | 28095 |
| USAspending awards | 200 |
| USAspending national actions | 1500 |

## Venue Coverage

| Venue | Candidate records |
| --- | ---: |
| access_meetings | 14 |
| countervailing_finance | 140 |
| electoral_money | 2536 |
| intermediary | 4206 |
| opaque_nonprofit_or_dark_money | 653 |
| procurement | 29795 |
| revolving_door | 803 |
| visible_lobbying | 242 |

## Cross-Source Pair Counts

| Source pair | Candidate actors |
| --- | ---: |
| IRS/ProPublica dark-money bridge + Intermediary bridge | 499 |
| USAspending agency actions + USAspending national actions | 432 |
| USAspending agency actions + USAspending awards | 93 |
| LDA + LDA revolving-door proxy | 34 |
| Intermediary bridge + USAspending agency actions | 13 |
| USAspending awards + USAspending national actions | 6 |
| Intermediary bridge + OpenFEC | 3 |
| IRS/ProPublica dark-money bridge + OpenFEC | 1 |
| IRS/ProPublica dark-money bridge + USAspending agency actions | 1 |
| Intermediary bridge + LDA revolving-door proxy | 1 |
| LDA revolving-door proxy + Reginfo.gov EO 12866 meetings | 1 |
| LDA revolving-door proxy + USAspending agency actions | 1 |
| OpenFEC + USAspending agency actions | 1 |
| Reginfo.gov EO 12866 meetings + USAspending agency actions | 1 |

## Cross-Venue Source Pair Counts

| Source pair | Cross-venue candidate actors |
| --- | ---: |
| IRS/ProPublica dark-money bridge + Intermediary bridge | 499 |
| LDA + LDA revolving-door proxy | 34 |
| Intermediary bridge + USAspending agency actions | 13 |
| Intermediary bridge + OpenFEC | 3 |
| IRS/ProPublica dark-money bridge + OpenFEC | 1 |
| IRS/ProPublica dark-money bridge + USAspending agency actions | 1 |
| Intermediary bridge + LDA revolving-door proxy | 1 |
| LDA revolving-door proxy + Reginfo.gov EO 12866 meetings | 1 |
| LDA revolving-door proxy + USAspending agency actions | 1 |
| OpenFEC + USAspending agency actions | 1 |
| Reginfo.gov EO 12866 meetings + USAspending agency actions | 1 |

## Top Candidate Actors

| Candidate | Priority | Evidence class | Type | Sources | Venues | Records | Activity | Risk flags | Review action |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| American Bankers Association | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge; OpenFEC | electoral_money; intermediary; opaque_nonprofit_or_dark_money | 11 | 4.5185 | committee-name-may-not-identify-actor-control | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ALLIANCE FOR TELECOMMUNICATIONS INDUSTRY SOLUTIONS | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge; USAspending agency actions | intermediary; opaque_nonprofit_or_dark_money; procurement | 4 | 0.3244 | procurement-name-overlap-requires-UEI-review | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| Ab Foundation | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 12 | 60.8043 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| American Action Network Inc | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 14 | 30.5093 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| National Restaurant Association | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 46 | 5.4309 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BERGER ACTION FUND INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 7.6408 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| American Petroleum Institute | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 9 | 6.3054 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CTIA-THE WIRELESS ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.5036 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CREDIT UNION NATIONAL ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.4939 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| EDISON ELECTRIC INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 2.4437 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INVESTMENT COMPANY INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.9961 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN COUNCIL OF LIFE INSURERS INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.8547 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CENTER FOR VOTER INFORMATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 3 | 1.7604 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ELECTRONIC PAYMENTS COALITION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.7464 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| REPUBLICAN JEWISH COALITION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 3 | 1.4948 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF MANUFACTURERS OF THE USA | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4811 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| MORTGAGE BANKERS ASSOCIATION OF AMERICA | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4316 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NUCLEAR ENERGY INSTITUTE INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4247 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| PLASTICS INDUSTRY ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.4061 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ADVANCED MEDICAL TECHNOLOGY ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.3147 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| PHARMACEUTICAL CARE MANAGEMENT ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.3005 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| THE FAIRNESS PROJECT | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.2328 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN GAS ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 1.0157 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ENTERTAINMENT SOFTWARE ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9776 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF SOCIAL WORKERS INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9157 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| SOLAR ENERGY INDUSTRIES ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.9027 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CRUISE LINES INTERNATIONAL ASSOCIATION INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8919 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| RECORD INDUSTRY ASSOCIATION OF AMERICA INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8913 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL ASSOCIATION OF REAL ESTATE INVESTMENT TRUST INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8739 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| FUTURES INDUSTRY ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8659 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| BANK POLICY INSTITUTE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8475 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN ASSOCIATION FOR JUSTICE | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8297 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| CENTER FOR AMERICAN PROGRESS ACTION FUND | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8283 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INSTITUTE OF INTERNATIONAL FINANCE INC | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8200 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| AMERICAN PUBLIC TRANSIT ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.8051 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| ASSOCIATION OF CORPORATE COUNSEL | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 3 | 0.7945 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL CONFECTIONERS ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7801 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| INTERNATIONAL BAR ASSOCIATION | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7572 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| NATIONAL MULTIFAMILY HOUSING COUNCIL | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7101 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |
| COUNCIL OF INSURANCE AGENTS & BROKERS | P1-manual-review | shared-source-identifier-overlap | cross_venue | IRS/ProPublica dark-money bridge; Intermediary bridge | intermediary; opaque_nonprofit_or_dark_money | 2 | 0.7052 | none | P1-manual-review: manually adjudicate aliases, source identifiers, false positives, and issue comparability before promoting any row under data/calibration/first-wave/ |

## Claim Boundary

Automated normalized-name overlap is not evidence that records refer to the same legal entity, funder, beneficial owner, or coordinated influence strategy. The report is useful because it turns the next empirical task into a reviewable worklist, not because it validates substitution magnitudes. Any promoted first-wave source product must preserve manual decisions, false-positive and false-negative checks, issue-code comparability, and source-record provenance.

## Next Steps

1. Review the highest-coverage candidates and assign durable `canonicalActorId` values.
2. Populate the alias-resolution audit sample with positive and negative decisions.
3. Map a narrow issue ontology across LDA, electoral, intermediary, nonprofit, procurement, and rulemaking surfaces.
4. Generate the linked actor-issue-venue-time table only after the manual audit records false-match risk.
