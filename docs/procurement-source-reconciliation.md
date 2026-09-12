# Procurement source reconciliation: interim findings

Reviewed 2026-09-12. No representative SAM export has been obtained or promoted.
The saved export link was expired, the minimal Contract Awards request returned
no usable rows, and the Exclusions request returned HTTP 401. Private operational
reports remain ignored. These are access findings, not zero procurement or zero
exclusion observations. A valid authorized export or restored API access is still
required.

The September 12 follow-up repeated the minimal synchronous Contract Awards
preflight (one requested row) and the Exclusions preflight. Contract Awards
remained unavailable with no usable rows; Exclusions again returned HTTP 401.
These checks did not promote data or refresh a representative SAM panel.

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

## FY2024 decision-to-award linkage pilot

The separate `gao-award-linkage-pilot.csv` now links four delivery orders named
in the September 16, 2024 consolidated
[Owens & Minor / Cardinal Health / Concordance decision](https://www.gao.gov/products/b-422689,b-422689.2,b-422689.3,b-422689.4,b-422690,b-422690.2,b-422690.3,b-422690.4,b-422692,b-422692.2,b-422693,b-422693.2,b-422693.3)
to official USAspending award and transaction records. The decision heading,
opening paragraphs, digest and footnotes 1-5 identify the date, VA, awardee
Medline Industries, LP, and challenged delivery-order IDs. Overall disposition
is denied, with supplemental organizational-conflict allegations dismissed;
the allegations are not findings of misconduct. Filed dates remain unknown.

| Award PIID | Original action date | Action obligation, dollars | Frozen small-panel candidates | Archived bulk matches |
| --- | --- | ---: | ---: | ---: |
| 36C10X24N0074 | 2024-05-31 | 10,000.00 | 0 | 1 |
| 36C10X24N0088 | 2024-05-31 | 10,000.00 | 0 | 1 |
| 36C10X24N0089 | 2024-05-31 | 10,000.00 | 0 | 1 |
| 36C10X24N0108 | 2024-05-31 | 10,000.00 | 0 | 1 |

All four match UEI `DMPAKJ9N9K66`, awarding subtier `3600`, parent PIID
`36C10X23D0032`, and original modification `0`. Their full USAspending award
keys retain the child PIID, awarding subtier, parent PIID and parent subtier.
This is one selected consolidated decision with four award links, not four
independent protest events. No docket-to-order pairing is inferred from the
order of lists in the decision. Independent source/coding review is pending.

`gao-award-linkage-source.json` preserves both public search requests and
responses, selected award-detail fields, original response hashes, GAO review
locations, and four extracted bulk rows. The live API observations were
retrieved September 12, 2026, not in 2024. The earlier bulk summary is dated
June 13, 2026 and records 6,449,101 normalized rows. The full local bulk file's
SHA-256 was rechecked against the committed summary:
`78322c3babe1a2b69ed2cc88a1c306f3344e97de96e2d8a81f8c4f4277dcee5b`.
All four original actions are present in that bulk file and agree with the live
records on date, modification, agency, UEI and amount. Thus their absence from
the small panel is not merely a later September API backfill. Neither source
vintage is a contemporaneous 2024 archive.

The current award-detail totals are zero for all four awards. Those current
totals are not the May 2024 action obligations. Performance starts June 1, 2024,
one day after the action date. Latest award details reflect 2026 modifications;
their offer/competition fields must not be silently assigned to the original
actions. The decision's evaluated prices and total delivery-order values also
have different scopes from transaction obligations. These distinctions supply
a concrete reconciliation example, not evidence of data fraud or a capture
effect. Do not infer exclusion status from responsibility findings or an API
no-match.

The pilot is kept outside `gao-protest-overlay.csv` and the model snapshot. Its
source bridge is verified at the stated scope, but it does not supply a
representative protest denominator, historical exclusion intervals, or causal
calibration. The offline audit checks the saved source bridge and bulk-manifest
identity. It does not independently authenticate the GAO coding or reconstruct
the entire ignored bulk file from its four-row extract.

## Prespecified SAM reconciliation population

The baseline action window is **fiscal year 2024: October 1, 2023 through
September 30, 2024**, not calendar 2024. The frozen small panel contains 28,103
rows across these twelve awarding top-tier agencies: EPA, Energy, Interior,
Agriculture, Transportation, Defense, Health and Human Services, Veterans
Affairs, Homeland Security, NASA, General Services Administration, and Commerce.
EPA contributes 2,228 rows; it is not the whole action panel.

For the next SAM extract, target all publicly reportable contract actions in
that agency/window frame, including original actions, modifications, zero
obligations and deobligations. Retain the action types corresponding to the
USAspending A/B/C/D contract frame; parent indefinite-delivery vehicles are
linkage records, not extra child actions. Preserve awarding and parent subtier
codes, child/parent PIIDs, source transaction ID, modification number, action
date, UEI, original currency/dollar obligation, and the source/scope of offers
and competition fields. Record extract time, filters, pagination and all
excluded or failed partitions. This target is a public twelve-agency population,
not a claim to cover all federal or hidden procurement.

The existing small panel takes at most two 100-row pages under each of three
sorts per agency-quarter: modification ascending, amount descending, and action
date ascending, deduplicated afterward. It is a ranked-slice diagnostic sample,
not a probability sample; balanced agency counts do not establish
representativeness. Prefer a complete SAM extract within the declared frame.
If a census cannot be obtained, a probability-sampling design and inclusion
weights must be specified against a verified frame before selection. Do not
retrofit weights to the current ranked slices.

The normalized small table has no exact duplicate rows, but 134 combinations
of top-tier agency, PIID and modification contain 361 rows (227 excess rows on
that partial key). Missing parent and unique source-transaction fields prevent
treating these as proven duplicate actions. Do not collapse them without source
review. Its model-oriented amount field also rounds millions to four decimal
places, a $100 increment; it cannot support cent-level reconciliation. The new
pilot preserves source-dollar observations separately, while the bulk extract's
eight-decimal million amounts retain cent precision.

Reconcile source-preserving action keys and unrounded obligations first, then
report coverage and disagreements by agency, quarter, action type and amount
sign. Compare with the archived bulk population, not only the ranked sample.
The bulk summary itself has 22 fewer downloaded than planned rows, so its
near-complete count is not proof of an exact census. Obtain those discrepancy
classifications before making population-completeness claims.

## Historical exclusions: a located but uninspected archive

The September 12 browser inspection of SAM's
[Public - Historical exclusions archive](https://sam.gov/data-services/Exclusions/Public%20-%20Historical?privacy=Public)
located `README_EXCLUSIONS.doc` and public extracts named
`SAM_Exclusions_Public_Extract_V2_2023_NOV_MODIFIED.ZIP`,
`SAM_Exclusions_Public_Extract_V2_2024_APR_MODIFIED.ZIP`, and
`SAM_Exclusions_Public_Extract_V2_2024_NOV_MODIFIED.ZIP`, among other dates.
The April 2024 file's metadata describes an active-exclusions monthly file,
but its displayed modification date is May 1, 2026. The historical filename
alone therefore does not establish an unchanged contemporaneous snapshot.

Selecting the README opened a Terms of Use acceptance dialog. No terms were
accepted, no login was attempted and no README/archive contents were obtained.
User review and file provision were requested. Next, inspect the README's
meaning of `MODIFIED`, original snapshot dates, deletions/revisions and field
definitions before extracting any firm-level UEI intervals. Restrict acquisition
to public files and keep any restricted-source material out of the repository.
Snapshots at a few dates cannot establish continuous exclusion status between
those dates or non-exclusion throughout FY2024. This archive is a concrete
acquisition lead, not a promoted historical exclusion overlay.

## Remaining empirical work

Freeze the intended agency/time population before a new export request. The
existing row/agency/date-span thresholds are only a screening floor, not evidence
of representative sampling. Reconcile matched SAM and USAspending actions in
the same period, quantify unmatched records and field disagreements by agency,
and compare coverage against the prespecified population. Establish protest and
historical exclusion coverage in that period before calculating event rates.
No-match is missing linkage until source coverage and identity are demonstrated.
