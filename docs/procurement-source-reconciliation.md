# Procurement source reconciliation: interim findings

Reviewed 2026-09-12. No representative SAM export has been obtained or promoted.
The saved export link was expired, the minimal Contract Awards request returned
no usable rows, and the Exclusions request returned HTTP 401. Private operational
reports remain ignored. These are access findings, not zero procurement or zero
exclusion observations. A valid authorized export or restored API access is still
required.

## Definitions for the linked action panel

| Concept | Use | Do not substitute |
| --- | --- | --- |
| Award/action identity | Awarding subtier plus PIID, parent award identifiers where applicable, modification and transaction/source IDs | Vendor name or solicitation number alone |
| Action timing | Source action date or SAM `awardDetails.dates.dateSigned`, preserving the original field | Solicitation date, export time, or award start date |
| Action amount | `awardDetails.dollars.actionObligation`, including deobligations, reconciled against USAspending transaction obligation | Cumulative contract obligations, award ceiling, or base-and-option values |
| Modification incidence | Explicit original-action/modification coding with a fixed action denominator | A finding of capture or misconduct; routine administrative modifications are included |
| Competition/offers | Preserve source code, scope and number-of-offers provenance; distinguish this action from parent/inherited values | Missing equals zero offers or noncompetitive |
| Exclusion status | UEI-matched interval evidence relevant to the award-action date | Today's active-list absence as proof of historical non-exclusion |
| Protest timing | Filed date and decision-body date, separately from public-release/feed date | RSS publication date as the decision date |

The current [SAM Contract Awards API documentation](https://open.gsa.gov/api/contract-awards/)
distinguishes action obligations from cumulative totals and exposes date-signed
and number-of-offers provenance. The [Exclusions API documentation](https://open.gsa.gov/api/exclusions-api/)
states that its search returns active records only. Even after access is restored,
that endpoint alone cannot reconstruct all exclusions that were active during a
historical award window. Historical extracts or independently sourced intervals
are necessary; missing termination dates require explicit right-censoring.

## Protest adjudication advanced

[TechGlobal, Inc., B-424287/B-424287.2](https://www.gao.gov/products/b-424287,b-424287.2)
identifies Commerce/NOAA, the protester, Reston Consulting Group as awardee, a
June 1, 2026 decision, and denial. The worklist previously used its June 10 feed
publication date and issue hints about small-business status/jurisdiction.
Those fields now reflect the decision's evaluation/source-selection dispute.
RFQ 1305M226Q0013 is retained in notes as a solicitation number, not put into the
PIID field. Filed date and award/vendor-key linkage remain unresolved.

The importer no longer converts RSS dates to decision dates. Sixteen other
publication-derived dates were cleared to unreviewed; their original feed
timestamps remain in provenance notes. All 17 rows remain candidate-only.
This 2026 decision is not a time-aligned overlay for the frozen 2024 action panel.

## Remaining empirical work

Freeze the intended agency/time population before a new export request. The
existing row/agency/date-span thresholds are only a screening floor, not evidence
of representative sampling. Reconcile matched SAM and USAspending actions in
the same period, quantify unmatched records and field disagreements by agency,
and compare coverage against the prespecified population. Establish protest and
historical exclusion coverage in that period before calculating event rates.
No-match is missing linkage until source coverage and identity are demonstrated.
