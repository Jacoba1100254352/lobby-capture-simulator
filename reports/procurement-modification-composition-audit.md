# Procurement Modification Composition Audit

This audit decomposes the procurement modification source moment by source route, agency, award type, and recipient concentration. It is designed to keep action-row, distinct-award, amount-weighted, USAspending bulk, and optional SAM/FPDS-style denominators visibly separate.

## Claim Boundary

The active USAspending action panel has 28115 rows, a modified-action share of 0.4220, a distinct-award modification share of 0.3442, and an amount-weighted modification share of 0.6344. The archived USAspending bulk summary has 6449101 rows, a modified-action share of 0.1702, a distinct-award modification share of 0.1067, and an amount-weighted modification share of 0.5955. The largest modified-amount agency group is `Department of Defense` with 0.6059 of modified amount; the largest modified-amount award-type group is `DEFINITIVE CONTRACT` with 0.4809 of modified amount. SAM.gov Contract Awards has 0 committed rows. This composition audit does not clear the procurement-modification source gap; it explains why the current modified-action share remains a bounded sample diagnostic rather than a representative SAM/FPDS modification-incidence estimate.

## Source Route Summary

| Source | Rows | Modified rows | Modified action share | Modified award share | Rows/mod. award | Amount-weighted modified share | PIID | UEI | Competition known | Boundary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| usaspending-procurement-actions | 28115 | 11864 | 0.4220 | 0.3442 | 1.4470 | 0.6344 | 1.0000 | 1.0000 | 0.0000 | bounded USAspending transaction/action diagnostics; not representative SAM/FPDS modification calibration |
| usaspending-procurement-bulk-summary | 6449101 | 1097429 | 0.1702 | 0.1067 | 1.7920 | 0.5955 | 1.0000 | 1.0000 | 0.9983 | representative public USAspending transaction summary for configured agencies; raw CSV/ZIP archive required for full reproduction |
| sam-contract-awards | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | use for SAM/FPDS coding crosswalks, exclusions, offer counts, protests, and firewalls before upgrading procurement modification claims |

## Composition Groups

| Group type | Group | Rows | Modified rows | Modified action share | Modified award share | Modified amount share | Amount-weighted modified share |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| agency | Department of Defense |  |  |  |  | 0.6059 |  |
| agency | Department of Energy |  |  |  |  | 0.1120 |  |
| agency | Department of Health and Human Services |  |  |  |  | 0.0693 |  |
| agency | General Services Administration |  |  |  |  | 0.0447 |  |
| agency | National Aeronautics and Space Administration |  |  |  |  | 0.0427 |  |
| agency | Department of Veterans Affairs |  |  |  |  | 0.0422 |  |
| agency | Department of Homeland Security |  |  |  |  | 0.0403 |  |
| agency | Department of Transportation |  |  |  |  | 0.0153 |  |
| agency | Department of the Interior |  |  |  |  | 0.0095 |  |
| agency | Department of Commerce |  |  |  |  | 0.0078 |  |
| agency | Department of Agriculture |  |  |  |  | 0.0075 |  |
| agency | Environmental Protection Agency |  |  |  |  | 0.0030 |  |
| awardType | DEFINITIVE CONTRACT |  |  |  |  | 0.4809 |  |
| awardType | DELIVERY ORDER |  |  |  |  | 0.4494 |  |
| awardType | contract |  |  |  |  | 0.0317 |  |
| awardType | BPA CALL |  |  |  |  | 0.0272 |  |
| awardType | PURCHASE ORDER |  |  |  |  | 0.0108 |  |
| recipient | LOCKHEED MARTIN CORPORATION |  |  |  |  | 0.0637 |  |
| recipient | THE BOEING COMPANY |  |  |  |  | 0.0416 |  |
| recipient | RAYTHEON COMPANY |  |  |  |  | 0.0249 |  |
| recipient | NORTHROP GRUMMAN SYSTEMS CORPORATION |  |  |  |  | 0.0234 |  |
| recipient | ELECTRIC BOAT CORPORATION |  |  |  |  | 0.0189 |  |
| recipient | HUMANA GOVERNMENT BUSINESS INC |  |  |  |  | 0.0179 |  |
| recipient | BOOZ ALLEN HAMILTON INC |  |  |  |  | 0.0157 |  |
| recipient | LEIDOS, INC. |  |  |  |  | 0.0141 |  |
| recipient | LOCKHEED MARTIN CORP |  |  |  |  | 0.0125 |  |
| recipient | SAVANNAH RIVER NUCLEAR SOLUTIONS LLC |  |  |  |  | 0.0120 |  |
| recipient | TRIAD NATIONAL SECURITY, LLC |  |  |  |  | 0.0112 |  |
| recipient | NATIONAL TECHNOLOGY & ENGINEERING SOLUTIONS OF SANDIA, LLC |  |  |  |  | 0.0109 |  |
| agency | Department of Defense | 2399 | 615 | 0.2564 | 0.1899 | 0.4695 | 0.6463 |
| agency | Department of Veterans Affairs | 2386 | 612 | 0.2565 | 0.2028 | 0.0553 | 0.2169 |
| agency | Department of Energy | 2319 | 1422 | 0.6132 | 0.4372 | 0.2108 | 0.9883 |
| agency | Department of Health and Human Services | 2365 | 1098 | 0.4643 | 0.4499 | 0.0642 | 0.6898 |
| agency | General Services Administration | 2400 | 713 | 0.2971 | 0.1523 | 0.0571 | 0.8079 |
| agency | Department of Homeland Security | 2374 | 1206 | 0.5080 | 0.4526 | 0.0436 | 0.7135 |
| agency | National Aeronautics and Space Administration | 2333 | 1345 | 0.5765 | 0.4246 | 0.0512 | 0.9465 |
| agency | Department of Agriculture | 2367 | 570 | 0.2408 | 0.2271 | 0.0072 | 0.2644 |
| agency | Department of the Interior | 2356 | 944 | 0.4007 | 0.3786 | 0.0122 | 0.4830 |
| agency | Department of Transportation | 2333 | 1168 | 0.5006 | 0.4253 | 0.0147 | 0.6350 |
| agency | Department of Commerce | 2255 | 1023 | 0.4537 | 0.4176 | 0.0108 | 0.5914 |
| agency | Environmental Protection Agency | 2228 | 1148 | 0.5153 | 0.4564 | 0.0033 | 0.4008 |
| awardType | DEFINITIVE CONTRACT | 4660 | 3133 | 0.6723 | 0.5253 | 0.6523 | 0.7974 |
| awardType | DELIVERY ORDER | 15019 | 6339 | 0.4221 | 0.3526 | 0.3216 | 0.4506 |
| awardType | BPA CALL | 3556 | 1227 | 0.3451 | 0.3029 | 0.0249 | 0.5974 |
| awardType | PURCHASE ORDER | 4880 | 1165 | 0.2387 | 0.2332 | 0.0013 | 0.4443 |
| recipient | LOCKHEED MARTIN CORPORATION | 141 | 114 | 0.8085 | 0.7471 | 0.0791 | 0.6175 |
| recipient | OPTUM PUBLIC SECTOR SOLUTIONS, INC. | 39 | 3 | 0.0769 | 0.0769 | 0.0000 | 0.0000 |
| recipient | THE BOEING COMPANY | 115 | 90 | 0.7826 | 0.6250 | 0.0576 | 0.7691 |
| recipient | RAYTHEON COMPANY | 109 | 82 | 0.7523 | 0.6667 | 0.0250 | 0.5155 |
| recipient | MCKESSON CORPORATION | 21 | 4 | 0.1905 | 0.1500 | 0.0001 | 0.0017 |
| recipient | TRIWEST HEALTHCARE ALLIANCE CORP | 23 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recipient | HUMANA GOVERNMENT BUSINESS INC | 16 | 16 | 1.0000 | 1.0000 | 0.0367 | 1.0000 |
| recipient | ELECTRIC BOAT CORPORATION | 20 | 18 | 0.9000 | 0.8333 | 0.0319 | 0.9377 |
