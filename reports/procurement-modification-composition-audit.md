# Procurement Modification Composition Audit

This audit decomposes the procurement modification source moment by source route, agency, award type, and recipient concentration. It is designed to keep the bounded USAspending action panel separate from any future representative SAM/FPDS action-history denominator.

## Claim Boundary

The active USAspending action panel has 2399 rows, a modified-action share of 0.3297, and an amount-weighted modification share of 0.6141. The largest modified-amount agency group is `Department of Defense` with 0.4478 of modified amount; the largest modified-amount award-type group is `DEFINITIVE CONTRACT` with 0.7406 of modified amount. SAM.gov Contract Awards has 0 committed rows. This composition audit does not clear the procurement-modification source gap; it explains why the current modified-action share remains a bounded sample diagnostic rather than a representative SAM/FPDS modification-incidence estimate.

## Source Route Summary

| Source | Rows | Modified rows | Modified share | Amount-weighted modified share | PIID | UEI | Competition known | Boundary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| usaspending-procurement-actions | 2399 | 791 | 0.3297 | 0.6141 | 1.0000 | 1.0000 | 0.0000 | bounded USAspending transaction/action diagnostics; not representative SAM/FPDS modification calibration |
| sam-contract-awards | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | calibration-grade only after representative SAM/FPDS action-history rows are archived |

## Composition Groups

| Group type | Group | Rows | Modified rows | Modified share | Modified amount share | Amount-weighted modified share |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| agency | Department of Defense | 200 | 69 | 0.3450 | 0.4478 | 0.7113 |
| agency | Department of Veterans Affairs | 200 | 39 | 0.1950 | 0.0368 | 0.0979 |
| agency | Department of Energy | 200 | 100 | 0.5000 | 0.2786 | 0.9985 |
| agency | Department of Health and Human Services | 200 | 67 | 0.3350 | 0.0635 | 0.6882 |
| agency | National Aeronautics and Space Administration | 200 | 97 | 0.4850 | 0.0525 | 0.9691 |
| agency | General Services Administration | 200 | 86 | 0.4300 | 0.0387 | 0.7242 |
| agency | Department of Homeland Security | 200 | 75 | 0.3750 | 0.0331 | 0.6928 |
| agency | Department of the Interior | 200 | 51 | 0.2550 | 0.0148 | 0.5070 |
| agency | Department of Agriculture | 199 | 31 | 0.1558 | 0.0081 | 0.4123 |
| agency | Department of Transportation | 200 | 70 | 0.3500 | 0.0120 | 0.6179 |
| agency | Department of Commerce | 200 | 71 | 0.3550 | 0.0118 | 0.6342 |
| agency | Environmental Protection Agency | 200 | 35 | 0.1750 | 0.0020 | 0.2311 |
| awardType | DEFINITIVE CONTRACT | 552 | 346 | 0.6268 | 0.7406 | 0.8105 |
| awardType | DELIVERY ORDER | 1236 | 401 | 0.3244 | 0.2436 | 0.3517 |
| awardType | BPA CALL | 221 | 43 | 0.1946 | 0.0141 | 0.6980 |
| awardType | PURCHASE ORDER | 390 | 1 | 0.0026 | 0.0018 | 0.8833 |
| recipient | OPTUM PUBLIC SECTOR SOLUTIONS, INC. | 33 | 0 | 0.0000 | 0.0000 | 0.0000 |
| recipient | LOCKHEED MARTIN CORPORATION | 23 | 12 | 0.5217 | 0.0535 | 0.4061 |
| recipient | THE BOEING COMPANY | 29 | 28 | 0.9655 | 0.0745 | 0.8728 |
| recipient | MCKESSON CORPORATION | 13 | 0 | 0.0000 | 0.0000 | 0.0000 |
| recipient | TRIWEST HEALTHCARE ALLIANCE CORP | 11 | 0 | 0.0000 | 0.0000 | 0.0000 |
| recipient | HUMANA GOVERNMENT BUSINESS INC | 8 | 8 | 1.0000 | 0.0606 | 1.0000 |
| recipient | ELECTRIC BOAT CORPORATION | 5 | 5 | 1.0000 | 0.0494 | 1.0000 |
| recipient | RAYTHEON COMPANY | 17 | 10 | 0.5882 | 0.0232 | 0.5085 |
