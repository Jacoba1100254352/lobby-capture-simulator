# Procurement source reconciliation: interim findings

Reviewed through 2026-09-13 UTC. No representative SAM export has been obtained or promoted.
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

## SAM import semantics regression review

Reviewed September 13, 2026. **Assessment: corrected import semantics, not new
empirical observations.** The prospective SAM normalizer contradicted the
definitions above: it omitted the current nested signed-date field, accepted
approval/modified dates as substitutes, fell back to total/ceiling amounts and
parent offer counts, and inferred vendor exclusion from competition wording.
These paths are now corrected in `scripts/fetch-source-data.py` and the export
screen. No SAM records are present in the frozen snapshot, and its existing
USAspending observations and the four-award pilot remain unchanged.

The current [GSA API documentation](https://open.gsa.gov/api/contract-awards/)
and its [OpenAPI schema](https://open.gsa.gov/api/contract-awards/v1/openapi.yaml)
were acquired. Their respective SHA-256 values are
`46cb995d2d026bef0d5a1e85ff2ec2220c3775b9d3701fded4895f5244ac7fb2`
and `87ab11d503a19a622dfbb1a1ea8fa840f19440a83b0b2d89cf6132ddb3cfb8fc`.
These are current interface definitions, not a recovered historical dictionary
or proof that any particular 2024 order contains these values.

| Normalized concept | Current documented input | Preserved distinction |
| --- | --- | --- |
| Action date | `awardDetails.dates.dateSigned` | Approval, performance-start and last-modified dates do not fill a missing signed/action date. Explicit legacy signed/action aliases remain supported. |
| Action obligation | `awardDetails.dollars.actionObligation` | `totalContractDollars.totalActionObligation` and ceilings are not action amounts. Blank, malformed and nonfinite amounts remain missing; zero and negative obligations remain valid. |
| Reported order offers | `awardDetails.competitionInformation.numberOfOffersReceived` | The reported count is not replaced by `idvNumberOfOffersReceived`. Its source may itself be inherited, so the native `numberOfOffersSource.code/name` is retained. |
| Action identity | `contractId.subtier`, `piid`, `modificationNumber`, `transactionNumber`, `referencedIDVSubtier`, `referencedIDVPiid` | Retain parent and transaction identifiers; sharing a partial model key does not prove duplication. |

The normalized SAM CSV retains the original model column names and adds thirteen
provenance/identity columns. `actionObligationDollars` preserves the selected raw
dollar string, and its decimal million conversion retains cents in the CSV.
The three `*SourcePath` columns identify paths in the parsed record; for CSV
inputs these may be parser aliases, not original header spellings. The
`parsedRecordSha256` hashes the whole parsed record including CSV aliases. It
is a deduplication aid, **not a raw-file hash, authenticity proof, or unique
underlying-action identifier**. Only identical parsed records collapse; records
with differing source metadata remain separate for later review.

`numberOfOffersSourceCode`, `numberOfOffersSourceName` and
`idvNumberOfOffersReceived` remain separate from `numberOfOffers`. A missing
modification number is not assigned original-action code zero. Parent competition
does not fill missing order competition. The existing
`exclusionFlag=false` model placeholder is paired with
`exclusionEvidenceStatus=not_observed_in_contract_awards`; neither denotes
verified historical non-exclusion. Protest/firewall defaults and the
`priceOnlyAward` heuristic likewise remain model inputs, not adjudicated outcomes.

The export audit uses the same admissible action-date/amount paths, requires
finite action obligations for all rows, and counts explicit zero offers as
observed. Missing or invalid fields cannot be rescued by a later contract total.
Its breadth thresholds are still only an operational screen: a passing candidate
does not establish a census, valid sampling weights, complete identifiers,
historical exclusions, or causal identification.

`scripts/test-sam-reconciliation.py` and the empirical notebook use explicitly
synthetic examples to check precedence, forbidden fallbacks, missing/zero values,
cent precision, provenance and partial-key collisions. They cannot authenticate
actual SAM rows. Source access is a separate gate: the current browser check
reached a signed-out contract-data page, so an authorized sign-in or fresh export
remains necessary. No account terms were accepted and no frozen panel was refreshed.

### Downstream exclusion-evidence boundary

The September 13 follow-through review reproduced two additional defects with
synthetic records: generic procurement CSV normalization dropped the SAM
importer's thirteen added identity/provenance fields, and the Java loader
reintroduced `exclusionFlag=true` from competition text despite the explicit
`not_observed_in_contract_awards` marker. The source-moment reporter likewise
counted the competition wording in its legacy exclusion proxy. None of these
tests is an observation about an actual excluded vendor.

The generic `usaspending` and `usaspending-actions` routes now preserve those
thirteen columns when supplied, retaining all 32 importer fields. They do not
add empty provenance columns to old nineteen-column inputs or infer missing
source facts. The Java loader honors the unobserved marker while preserving
the separately named limited-competition procedure proxy. Both Java and the
source-moment reporter reject a contradictory true exclusion flag, unsupported
status values, and an explicitly present but blank status. No observed-vendor
status is accepted without a separately implemented evidence contract.

Unmarked legacy fixtures retain their old competition-proxy behavior for
reproducibility, not as historical vendor-exclusion evidence. When intentionally
combining legacy rows with marked rows, `legacy_competition_proxy` explicitly
declares that old meaning; a blank status is not silently assigned it. The
reporter excludes unobserved rows from the legacy proxy denominator, reports
their count, and labels a mixed or all-unobserved result as diagnostic. With no
legacy rows, its numeric zero is an unavailable-value placeholder, not an
observed zero exclusion rate.

Eight additional Python regressions cover metadata preservation, legacy replay,
unknown/contradictory statuses and denominator handling, including a synthetic
source JSON through export, generic normalization and the actual Java loader.
Java checks independently exercise its parsing branch; these software checks
are not independent empirical adjudication. The companion notebook executes
the downstream suite and displays the all-unobserved and mixed examples.
Frozen source rows, model coefficients and existing legacy proxy results remain
unchanged. Representative SAM acquisition, historical intervals and reviewed
award/protest links remain separate requirements.

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
the allegations are not findings of misconduct. The separate docket ledger below
now supplies filing dates at listed-case grain; award-specific dates remain
unassigned.

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

### Filing-date coverage and unresolved award mappings

Reviewed September 12, 2026. `gao-docket-timing-pilot.csv` retains all **13 case
numbers listed in the decision**, including the initial and related entries.
Each public docket was read in the ordinary browser and links to that same
September 16, 2024 decision. The base numbers in the decision appear with `.1`
in the public docket; four explicit, source-specific aliases preserve both forms.
This is complete coverage of the decision's listed cases, not a census of all
protests about these awards or a representative procurement population.

| Public filing date | Listed docket entries | Source location |
| --- | ---: | --- |
| June 24, 2024 | 6 | Each docket's Filed Date field |
| June 26, 2024 | 4 | Each docket's Filed Date field |
| August 2, 2024 | 3 | Each docket's Filed Date field |

All 13 pages display September 16, 2024 for both Decision Date and Posted on.
The displayed due dates are October 2, October 4, and November 12 respectively.
Those deadlines are not actual decision dates, filing dates, or evidence of a
continued proceeding after the September decision. A displayed posting date is
not independent proof of when a redacted decision first became publicly available.
[GAO's FAQ](https://www.gao.gov/legal/bid-protests/faqs) distinguishes decision
dates from public release and explains that routine dismissals are generally
not published. The selected decision's overall denial also does not overwrite
its dismissed supplemental organizational-conflict grounds.

The source JSON preserves each docket URL and its displayed protester,
solicitation, agency, date and outcome fields. In particular, Cardinal appears
as `Cardinal Health 200, Inc.` on its docket pages but `Cardinal Health 200, LLC`
in the decision. That source-native difference is retained, not silently resolved
as a verified legal-entity alias. Surrounding whitespace alone is normalized.

Three Concordance dockets list two solicitations:
[B-422690.2](https://www.gao.gov/docket/b-422690.2),
[B-422692.1](https://www.gao.gov/docket/b-422692.1), and
[B-422693.1](https://www.gao.gov/docket/b-422693.1) each include `36C10X24R0007`
alongside a different solicitation. The decision's footnotes associate those
cases with VISN 22, OGA, and VISN 19 respectively, while footnote 6 explicitly
associates `36C10X24R0007` with VISN 8. Conversely,
[B-422693.3](https://www.gao.gov/docket/b-422693.3) displays only
`36C10X24R0014`, but footnotes 2-5 include it in all four service areas.
Consolidation may explain broader docket metadata, but that explanation has not
been verified. Both representations remain visible. Neither source justifies
matching docket cases to delivery orders by list order or treating 13 entries
as 13 independent award events.

Four current USAspending award-detail responses were rechecked. Their latest
contract-data `solicitation_identifier` fields are null. Current descriptions
explicitly name VISN 19 for `36C10X24N0074` and VISN 22 for `36C10X24N0108`;
these are two service-area candidates, not original-action mapping clearance.
The other descriptions are not assigned by elimination. Those descriptions
reflect a September 2026 source vintage with 2026 last-modified dates.

The manifest-selected VA April-June 2024 ZIP was reopened, and its SHA-256 again
matched `9e114859a0dd24de1118cd87070d4811f4ac7522f2ad164fed531aac3b5fcaae`.
Original actions appear at CSV rows 17136, 17138, 17139 and 17142, including the
header, in `Contracts_PrimeTransactions_2026-06-13_H07M30S14_1.csv`.
The export's 13-column schema contains neither description nor solicitation
columns. These are absent columns, not observed null cells. The saved excerpts
retain source parent IDs, action dates, modifications, UEIs and dollar amounts.
They confirm the original actions but cannot adjudicate the service-area mapping.

The decision's Affirmative Responsibility Determination section also recounts
the contracting officer's SAM review as finding no active or inactive exclusions
for Medline, citing the VISN 8 decision document at pages 47-48. The underlying
SAM and agency records have not been independently read, and the check date is
not specified in the reviewed paragraph. This is a decision-reported check,
not a reconstructed historical exclusion interval or proof of no misconduct.
It does not populate `sam-exclusion-overlay.csv`.

**Validation assessment: share with caveats for documentary timing only.**
`gao-docket-timing-source.json` records the review frame, field projections,
decision footnotes, current award-response hashes and archive excerpts. Direct
docket downloading returned HTTP 403; the browser could display every page but
could not export them. No original HTML archive is claimed. Projected-source
fingerprints bind the reviewed fields and coding context, not original web bytes.
The offline audit and `notebooks/empirical-expansion-review.ipynb` check completeness,
aliases, date conversion and chronology, many-to-many scope, source identity and
unsupported promotion. They do not independently authenticate the transcription.

The remaining high-impact requirements are original-action solicitation/service-area
evidence and independent source/coding review. Until then, all four award-pilot
`filedDate` cells and all docket-ledger `piid` cells stay blank. Even a later
verified mapping would require an explicit initial-versus-supplemental timing
definition and a representative denominator before protest-rate estimation.

### Original-action follow-up: recovered fields and a partial crosswalk

On September 13 UTC, the public USAspending
[transaction-history endpoint](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/transactions.md)
returned complete pages for all four existing pilot awards: 26 transaction rows
in total, with one modification-`0` action per award. Separate
[contract-specific downloads](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/download/contract.md)
finished successfully for all four. Each ZIP passed its CRC check. The transaction
members contain 6, 7, 7 and 6 rows, respectively, and 297 columns per member.
The status endpoint's 505-column figure describes the download package, not the
transaction member's schema. An earlier four-award general transaction-download
job failed with a generic server error; its zero-row status is not a zero-award
observation. No failed job was restarted.

The new `gao-original-action-review.json` preserves the requests, full history
responses, ZIP/member hashes, complete transaction-ID lists, original CSV row
locations and selected source-native fields. All 26 API IDs match the downloaded
transaction IDs after accounting for the API's `CONT_TX_` prefix. Original dates,
descriptions and obligations agree across the API and downloads; the four dates,
identities and dollar obligations also agree with the prior selected bulk rows.
These are newly retrieved records describing 2024 actions, not a contemporaneous
2024 archive. Source initial-report and last-modified timestamps are retained
separately from action dates; an initial report before the action is not a protest
filing date or an earlier award date.

| Original-action PIID | Explicit service-area label | Reported offers | Native solicitation identifier |
| --- | --- | ---: | --- |
| 36C10X24N0074 | VISN 19 | 4 | blank |
| 36C10X24N0088 | unassigned | 2 | blank |
| 36C10X24N0089 | unassigned | 4 | blank |
| 36C10X24N0108 | VISN 22 | 4 | blank |

All four original actions are May 31, 2024 delivery orders with $10,000.00 action
obligations, competition code `A` and solicitation-procedure code `MAFO`. Preserve
both source fields: the latter describes multiple-award fair opportunity. These
reported offer counts have not been verified against bids or agency records and
do not resolve missing offer fields in the broader panel. The solicitation
identifier column is now observed and blank in each original row, unlike the
earlier limited archive where the entire column was absent. The separately
reported October 17, 2023 solicitation date does not supply an identifier.

The explicit VISN 19 and VISN 22 labels now occur in **original-action**
descriptions, not only in latest award summaries. Together with decision
footnotes 3 and 4, they support eight provisional award/docket pairs across seven
distinct dockets. The supplemental `B-422693.3` belongs to both service areas;
preserve that many-to-many relationship. These are candidate documentary links,
not eight independent protest events or new observations in a representative
sample. Descriptions alone do not assign the other two awards: a generic reference
to other government agencies is not a unique OGA identification, and the residual
award must not be assigned VISN 8 by elimination.

Reopening the public decision also supplied an additional, explicitly inferential
cross-check. Its Jurisdiction discussion reports total order values by service
area; footnote 10 specifies whole-dollar rounding. Three original potential-total
values match those amounts after rounding. The explicitly labeled VISN 22 record
is $100 lower after rounding, exactly the source-system difference described in
footnote 15. Do not change the original dollar amounts to remove that difference.

| PIID | Original potential total, dollars | Decision service area | Decision total, dollars | Evidence basis |
| --- | ---: | --- | ---: | --- |
| 36C10X24N0074 | 164,568,206.07 | VISN 19 | 164,568,206 | explicit description; rounded value agrees |
| 36C10X24N0088 | 149,284,426.64 | OGA | 149,284,427 | unique rounded-value candidate |
| 36C10X24N0089 | 373,078,665.37 | VISN 8 | 373,078,665 | unique rounded-value candidate |
| 36C10X24N0108 | 340,131,789.10 | VISN 22 | 340,131,889 | explicit description; documented $100 difference |

The two amount-only matches are candidates within this already declared four-award
frame, not verified solicitation identities or justification for a general fuzzy
amount join. They extend the provisional crosswalk to sixteen award/docket pairs
covering all thirteen listed dockets. The shared supplemental case maps to all
four service areas and must not be counted four times as independent evidence.

**High-priority reconciliation issue:** the decision's Background reports five
timely proposals for VISN 8, four for VISN 19, four for VISN 22 and two for OGA.
The candidate VISN 8 original row instead reports four offers. The other three
numbers agree at this scope, but neither agreement nor disagreement proves an
underlying bid count or establishes that these source fields have identical
definitions. Preserve the discrepancy; do not correct either source, discard
the fifth proposal or use count agreement to select an award mapping. Resolving
it requires source definitions and, if available, the underlying agency records.

**Validation assessment: share with caveats for this partial documentary
crosswalk.** The prior four-award and thirteen-docket ledgers remain unchanged.
The notebook derives the provisional pairs and their source filing dates in a
separate follow-up; it does not fill the baseline timing cells. The offline audit
and regression tests check the fixed award/docket frames, pagination, transaction
identity, original-versus-modified actions, exact obligations, source dates and
unsupported promotion. They do not independently authenticate the ignored raw
files or review manual source interpretation. Independent review, the two
amount-only mappings, offer-count and solicitation reconciliation, representative SAM data
and historical exclusion evidence remain required. No rate or causal estimate
is added.

### Current VA publisher corroboration, separate from original actions

A September 13 UTC follow-up reads VA's [MSPV program page](https://department.va.gov/procurement-acquisition-and-logistics/strategic-acquisition-center/sac-medical-surgical-prime-vendor-program-mspv-updated/),
whose displayed update date is **August 27, 2026**. The entire delivery-order
table contains twenty service-area rows and nineteen distinct parent/child
keys. Its full bounded projection is preserved in
`gao-procurement-publisher-review.json`, not just the matched rows. The raw HTML
SHA-256 is `9a9aed4c147f7eb0eb40844204df2446a3fea9fffd5d77c42e1e4bfdc536b019`.
Staff contacts and other tables are excluded from the public projection.

Three rows explicitly name existing pilot awards under Medline's parent
`36C10X23D0032`:

| Publisher service area | Child PIID | Evidence added to the original review |
| --- | --- | --- |
| VISN 19 | 36C10X24N0074 | current agency label corroborates the original description |
| VISN 22 | 36C10X24N0108 | current agency label corroborates the original description |
| Other Government Agencies (OGAs) | 36C10X24N0088 | explicit agency label corroborates the previous rounded-value candidate |

All three display June 1, 2024-May 31, 2026 performance periods. These are not
action or protest filing dates. The OGA identification now has primary-agency
documentary support beyond an amount match, but the page is a **current
publisher statement**, not a contemporaneously archived 2024 record or an
original solicitation. The original-action ledger is intentionally unchanged.
Joining these three labels to the decision's separate service-area footnotes
corroborates **eleven of the sixteen provisional award/docket pairs**, covering
**nine distinct dockets**. VISN 19 and OGA each have three pairs; VISN 22 has
five. The shared supplemental docket is not three independent events.

**High-severity identity/temporal limitation:** the table assigns the same newer
`36C10X25N0014` child and parent to both VISN 7 and VISN 8 excluding Puerto Rico.
It does not contain the pilot's `36C10X24N0089`. Preserve both displayed rows;
do not silently correct the duplicate, assign the old award by elimination,
infer supersession, or treat absence from this current table as historical
absence. The source of the repeated key is unknown. The page's Historical
Contracts link leads to a FOIA information page, not an acquired contract archive.

**Assessment: share with caveats for current-label corroboration only.** The
offline audit derives native-cell projections, duplicate keys, complete-frame
coverage and the decision-footnote joins. The notebook also replays the parser
against the hash-matched ignored HTML when available. These checks do not
independently validate manual interpretation. Solicitation identity, original
offer provenance, independent review, representative SAM coverage and historical
exclusion intervals remain open; no baseline timing cells or causal estimates
are promoted.

A September 13 check of the current page's historical-contracts link reached
the [OALC FOIA library](https://department.va.gov/administrations-and-offices/acquisition-logistics-and-construction/freedom-of-information-act-requests/).
Its displayed MSPV contract-records section lists older program generations,
including Medline's `36C10X23D0003` transition vehicle, not a new source match
for `36C10X24N0089`. That different parent cannot fill the original-order
mapping. This was a review of the displayed section, not every library record;
no FOIA request was submitted and no additional award link was promoted.

### Archived VA labels and conflicting later cells

Reviewed September 13, 2026. The separate
`gao-archived-publisher-review.json` preserves two actual 2024 captures of the
old VA MSPV page. The Wayback CDX query for that address, calendar 2024,
successful responses and HTML content returned seven capture rows, with no
collapse or result limit. This is the returned index for the specified filters,
not proof that every historical version was archived. The selected dates are
the first indexed capture after the May 31 original actions and the latest
indexed capture before the September 16 decision. The full June award table
and September delivery-order list were read in acquired HTML and the ordinary
browser replay. Independent source/coding review remains pending.

The [June 13 capture](https://web.archive.org/web/20240613162439/https://www.va.gov/opal/sac/mspv.asp)
displays a June 6 page-update date. Its complete five-row table explicitly
labels these parent/child pairs under `36C10X23D0032` and Medline Industries, LP:

| Service area | Child PIID | Displayed base performance period |
| --- | --- | --- |
| VISN 8 excluding Puerto Rico | 36C10X24N0089 | June 1, 2024-May 31, 2025 |
| VISN 19 | 36C10X24N0074 | June 1, 2024-May 31, 2025 |
| VISN 20 | 36C10X24N0080 | May 10, 2024-May 9, 2025 |
| VISN 22 | 36C10X24N0108 | June 1, 2024-May 31, 2025 |
| Other Government Agencies | 36C10X24N0088 | June 1, 2024-May 31, 2025 |

This recovers direct historical agency-label evidence for VISN 8, previously
absent from the current page, and corroborates all four pilot awards. Joining
the labels to the separately reviewed GAO service-area footnotes supports all
**sixteen provisional pairs across thirteen distinct dockets**. The fifth
table row, VISN 20, is retained for complete display coverage; it is not added
to the selected decision family. The June capture precedes the earliest
recorded filing date among the thirteen reviewed dockets. Capture and displayed
update dates do not establish the original award date, original solicitation
identity or any protest filing date. The one-year base periods remain distinct
from the longer periods displayed by the 2026 page.

The [September 6 capture](https://web.archive.org/web/20240906233447/https://www.va.gov/opal/sac/mspv.asp)
displays a September 4 update. Its complete bounded list contains **nineteen
service areas, fourteen marked TBD**, with staff contact fields excluded from
the public projection. VISN 23 is omitted from this display. Neither TBD nor
omission establishes an unawarded contract or a missing historical transaction.
Two material conflicts prevent simply selecting the latest source cells:

- VISN 22 displays `36C10X24N0074`, repeating the VISN 19 key and disagreeing
  with June's `36C10X24N0108`. The repeated value is preserved without correction.
- VISN 20's displayed start changes from May 10 to June 1, 2024, while its end
  remains May 9, 2025. A changed webpage cell is not an adjudicated modification.

Four area entries carry a star linked to an agency notice reporting that the
orders are under GAO protest and a stay of performance is in effect. Because
of the repeated key, these are **four displayed rows but three distinct
parent/child keys**. The notice supplies no case IDs, stay start/end dates or
underlying stay instrument. It is an archived agency statement at this snapshot,
not an exact interval or verified four-award stay mapping. The June table's
lack of a star note is not a finding of no protest or no stay.

The June HTML SHA-256 is
`aeb03678b2a4525762ca0bd1018224f8c83b2d709f025eb493f98b0675a12fd2`;
its payload SHA-1 agrees with the CDX digest. September was returned gzip
encoded. Its encoded payload SHA-256 is
`60f5da029d4e7f48701fb27e648ef674200accc09c99f592f7f4a46a97e84588`
and agrees with CDX at the encoded-payload SHA-1 level; its decoded HTML SHA-256
is `1118eb4e72cc772854bec96f417c5450e92014bd7cff5409ed120b3c72ac21cc`.
Both resolved replay URLs and Memento datetimes match the requested captures.
These checks bind acquired bytes to the archive index, not the truth of every
agency entry. Ignored raw responses retain acquisition evidence; no archived
cookies or staff contacts are included in the public ledger.

**Assessment: historical label corroboration with explicit source conflicts.**
The notebook and offline audit reproduce complete display coverage, native
cell projection, the two conflicts, duplicate keys and the many-to-many docket
join. Optional raw checks verify encoded/decoded hashes, CDX digests and fresh
extraction. The independent-review gate, baseline award `filedDate` cells and
docket `piid` cells remain unchanged. Original solicitations, offer provenance,
representative SAM coverage and historical exclusion intervals are still absent.

### Offer-count provenance and dictionary-version limits

On September 13 UTC, GSA's public [dictionary article, KB0090014](https://www.fsd.gov/gsafsd_sp/en/fpds-help-data-dictionary-v1-5?id=kb_article_view&sys_kb_id=bc3f142fcf190750d1eaf2c42f851ca4&spa=1)
linked a [downloadable FPDS V1.5 dictionary](https://falextracts.s3.amazonaws.com/Data%20Dictionary/Contract%20Awards/FPDS%20V1.5%20Specifications/FPDS_Data_Dictionary_V1.5.pdf).
The article labels it 2026, but the downloaded cover is dated October 20, 2025.
Its SHA-256 is `020e9684bba3e2551c5878ad4aa45959c8e97f1a2a821d8e7c48de94e36beedd`.
Printed pages 119-122 (PDF 121-124) were read and visually checked:

- **10D** counts bids/offers submitted for a solicitation, not a stated count of
  technically acceptable proposals. Its requirement table distinguishes order
  types and shows propagation for modifications.
- **10F**, XML `numberOfOffersSource`, identifies whether the count was entered
  on this action (code `F`) or inherited from a referenced vehicle (codes `A-E`).
- **10G**, XML `idvNumberOfOffersReceived`, is a separate parent-vehicle count.
  The revision history records its addition to the dictionary on October 18, 2025 and a change to
  10D's notes on September 20, 2025 (printed page 8, PDF 10).

These later specifications do not establish the rules applied to May 2024
records. No complete contemporaneous dictionary or per-record 10F value was
recovered. Dictionary inclusion is not proof of a field's introduction date.

A separate source review acquires DoD's [2024 FPDS Reporting Basics training](https://www.acq.osd.mil/asda/dpc/ce/p2p/docs/training-presentations/2024/P2P%202024%20-%20FPDS%20Reporting%20Basics%20-%20Procurement%20Awards.pdf),
SHA-256 `baceacbccbc679fa55b94b924dd850e527cf8064ae1fa3d55d2e0648de35835b`.
The cover and PDF page 41 were visually reviewed, not all 68 slides. Page 41
dates service pack 20.0 to January 27, 2024 and lists the set-aside-source and
offer-count-source elements as dictionary additions. This establishes that the
offer-source concept was documented in a 2024 publication; it does not supply
the four awards' field values or a complete historical 10D/10F specification.

The public web reader also displays an [FPDS service-pack revision comparison](https://fpds.gov/wiki/index.php?diff=cur&oldid=5021&title=V1.5_SP_20.0)
between January 30, 2024 and February 6, 2025. Its dictionary ticket describes
previously undocumented system-generated fields, while `IAEMOD-20385` describes
an IDV-offer propagation fix for Part 8 BPAs referencing FSS modifications.
This further cautions against treating a later dictionary entry as the first
existence of a field. The old-revision link redirected to SAM; no immutable
historical HTML archive was acquired. That BPA/FSS example does not establish
which rule applied to the pilot delivery orders. The source ledger preserves
the access and interpretation limits separately from the acquired PDF.

#### Archived reporting guidance predating the award-date label

A further September 13 acquisition recovers official DoD
[PGI HTML under the April 27, 2023 archive path](https://www.acq.osd.mil/dpap/dars/pgi/pgi_htm/r20230427/PGI204_6.htm),
whose displayed revision is January 31, 2023, and the
[May 30, 2024 PGI PDF](https://www.acq.osd.mil/dpap/dars/pgi/pgi_pdf/r20240530/PGI204_6.pdf).
Both versions' PGI 204.606(3)(xiv)(M)(1)-(2) distinguish three concepts:
the specific order's offers for multiple-award orders, the separately displayed
original-contract count, and a system-generated field indicating action entry
versus prepopulation. These are two versions of one guidance family, not
independent observations of the VA orders.

The 2023 HTML hash is
`250288e1c9d1ffa2a71939aa22d72382a0630366eb4f925af095a3dbb01b7763`;
the 2024 PDF hash is
`658b10552bd21d5ddb8c4990eef2c0125e5d64b715316d0ae7c5dad5d0b0c6b8`.
The HTML header, hierarchy and two paragraphs were read. PDF pages 1, 22 and 23
were visually reviewed, not all 27 pages; their printed labels are 204.6-1,
204.6-22 and 204.6-23. The HTML retains damaged quotation glyphs, and the PDF
header still describes the entity identifier as DUNS. Neither is silently
repaired or adopted as the VA identifier definition.

This strengthens the historical documentation beyond the dictionary-addition
slide. It does not establish VA applicability, exact XML-code equivalence,
field-introduction dates or a complete historical dictionary. Archive labels
and displayed revisions precede the May 31, 2024 actions, but these are 2026
retrievals without independently verified historical capture times. The
`historicalOfferGuidance` ledger and notebook preserve these distinctions and
optionally authenticate the acquired bytes. Neither source supports dropping
an allegedly unacceptable proposal to reconcile four offers with five timely
proposals. Per-order source fields and the decision-cited agency evidence remain
needed; no offer count, solicitation, timing or exclusion value is changed.

Reopening all four hash-matched, 297-column transaction members finds exactly
one header containing `offer`: `number_of_offers_received`. Thus neither 10F nor
10G is separately exposed under an offer-named column in these downloads.
Each original row reports `fair_opportunity_limited_sources_code=FAIR`; the
native `idv_type_code` and `multiple_or_single_award_idv_code` cells are blank.
Those child-row blanks do not classify the referenced vehicle. The notebook
reproduces this schema/row check when the ignored raw files are available.

The publisher follow-up separately acquires the shared parent's complete
seven-action history and an official USAspending IDV export. The original
May 23, 2023 parent row reports `idv_type_code=B`, `type_of_idc_code=B`,
`multiple_or_single_award_idv_code=M`, six offers, and solicitation
`36C10X23R0007`. The history API identifies the vehicle as `IDV_B_B`; the CSV's
generic `award_type` cell is blank. All seven retrieved actions retain the same
type codes and offer count. These are parent-vehicle observations, not values
inferred from blank child fields. They describe historical actions in a 2026
retrieval, not an immutable contemporaneous 2023/2024 snapshot.

`parentVehicleSource` in the new ledger preserves the API response, request/job
provenance, archive/member/row hashes and all seven native parent projections.
The archive job reports 3,609 rows across three CSV members, **not 3,609 parent
actions**; only the seven-row transaction-history member is substantively
adjudicated here. The other members receive structural count/hash checks.
The 297-column parent history also exposes only `number_of_offers_received`
among offer-named headers. Parent six-offer and solicitation values must not
replace the children's two/four offers or blank solicitation identifiers. This
additional parent context does not recover 10F or explain the VISN 8 discrepancy.

**Assessment: share with caveats.** The definitions identify additional source
fields needed for reconciliation; they do not explain the four-versus-five
VISN 8 discrepancy. Do not infer inheritance, discard an allegedly unacceptable
proposal, or replace either source count. The next step is a source-preserving
SAM action record with its offer-count provenance and the applicable historical
specification, followed by comparison with the decision-cited agency record.

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

For offer counts, request 10F/source provenance alongside 10D, retaining native
codes and the applicable dictionary version. Keep any separately supplied 10G
parent-vehicle count distinct; its later documentation is not a requirement that
an original 2024 record contain that field. Do not substitute a parent count for
an order's count or treat modification rows as new solicitations.

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

## Full archived-file frame audit

The September 12 raw-file audit scanned exactly the 56 ZIP paths in the frozen
June 13 bulk manifest, not the superseded and overlapping download attempts
also present locally. Every selected SHA-256 and prime-transaction row count
matched. Subaward CSV members were excluded. The declared twelve-agency frame
covers all 366 inclusive FY2024 days without date gaps or overlaps; all
6,449,101 exported rows fall within their assigned agency and date partition.
These checks establish consistency of the archived files, not source-system
completeness or unique action identity.

`procurement-bulk-frame-profile.json` retains the source header, selected ZIP
hashes and members, per-partition missingness, award/competition categories,
obligation signs and exact-decimal dollar sums. Run
`python3 scripts/audit-procurement-bulk-frame.py --scan` to repeat the raw-file
audit. `make procurement-bulk-frame-audit` and the empirical notebook check the
saved public profile and reproduce reports without requiring ignored archives.
That lighter check does not independently authenticate the original ZIP bytes.

| Finding | Rows | Implication |
| --- | ---: | --- |
| Explicit A/B/C/D-equivalent descriptions | 6,205,401 | Child-action description stratum, not verified full-key unique actions |
| Blank raw award type | 243,700 | Unresolved type; legacy normalization labels these `contract` |
| Missing offers | 4,505,798 | Unknown, not zero offers; 69.87% of all exported rows |
| Explicit zero offers | 351 | Separate source-reported category |
| Competition after exclusion of sources | 665,137 | Competition procedure, not SAM vendor status |
| Zero / negative obligations | 584,867 / 224,248 | Retained in action denominator |

The current bulk collector's award-type filter includes both A/B/C/D and IDV
codes. [USAspending's award-type reference](https://api.usaspending.gov/api/v2/references/award_types/)
distinguishes these groups. A concrete archived blank-type example is EPA
PIID `68HE0120D0001`, modification `P00013`, October 16, 2023, obligation $0.00,
UEI `Z4XGALW7L9K6`. Its original ZIP excerpt was checked at the recorded member
and row. The September 12 [official award detail](https://api.usaspending.gov/api/v2/awards/CONT_IDV_68HE0120D0001_6800/)
matches the PIID, recipient and agency, and reports category `idv`, type
`IDV_B_B`. `procurement-bulk-type-review.json` preserves the raw excerpt,
current response projection, response hash and review scope. This verifies one
vehicle identity in the blank-type group; it does not classify all 243,700
blank rows or establish a contemporaneous 2024 classification history.

The archive's thirteen columns omit native IDV type codes, numeric awarding
and parent subtier codes, and unique source transaction IDs. Parent PIID is
present raw but dropped in the legacy normalized table. Consequently, the
bulk denominator cannot be assumed identical to the intended A/B/C/D SAM
frame, and a row-count match cannot certify distinct actions. Preserve an
unresolved-type stratum until native source identity/type evidence resolves it;
do not silently drop the blanks or relabel them all as vehicles.

The legacy `exclusionFlag` is generated by testing competition text for
`exclusion`. The [FPDS field definition](https://www.fpds.gov/help/Extent_Competed.htm)
defines this as competitive-procedure information, not historical excluded or
debarred vendor status. It supplies no SAM exclusion interval, misconduct
finding or exclusion prevalence estimate. The bulk normalizer also defaults
protest and firewall flags to false without linked source observations. The
source-moment report now labels those default-only bulk values as diagnostics,
not observed proxies. Historical SAM intervals and independently reviewed
protest links are still required. No Java parameter is recalibrated here.

The 22-row count/export difference localizes to Agriculture July-September 2024
(34,678 planned versus 34,657 exported) and Defense May 2024 (387,460 versus
387,459). The collector accepts differences within the larger of five rows or
0.1% of the planned count under its default settings. The saved records confirm
accepted drift but do not preserve a count-time membership list or prove which
runtime tolerance settings were used. The affected record identities and cause
remain unknown; this is not evidence of 22 specifically identified omissions.

Exact-decimal aggregation yields $704,337,439,585.26 signed net obligations and
$774,172,847,532.38 absolute obligations. The legacy summary accumulates
floating-point millions and differs by less than $0.25 in each total; its
frozen bytes are unchanged. Net spending and absolute action volume remain
different concepts, and neither includes parent ceilings as child obligations.

### Saved Agriculture partition comparison

The September 13 follow-up compares the manifest-selected Agriculture
July-September ZIP with 33 saved alternative exports: July and September
monthly files plus one file for every August day. They cover all 92 days once.
All **34,657 complete rows match exactly across all thirteen exported fields**,
including multiplicities. Neither set has value-exact duplicate rows or
unmatched rows. The monthly totals are 10,626 for July, 11,500 for August and
12,531 for September. The alternatives are comparison evidence and are never
appended to the frozen panel.

`procurement-bulk-partition-comparison.json` records all 34 archive hashes,
member names, excluded subaward members, per-file counts and complete-row
multiset hashes. CSV values remain untrimmed and unrounded. The digest sorts
the complete field tuples and hashes compact ASCII JSON records containing
each tuple and its multiplicity, separated by newlines. This preserves missing
fields, quoted CSV text and repeated rows; it is not deduplication on a partial
award key. Agency and action-date containment are checked for every source row.
The ZIP member times have no specified timezone and are not count-query times
or evidence of an unchanged contemporaneous FY2024 source snapshot.

This is a negative result for recovering the additional Agriculture rows by
finer saved partitioning: the same 34,657 exported rows recur. It does not
identify the count endpoint's 34,678 records, explain the 21-row difference,
or certify unique action identity and source completeness. The Defense May
difference of one remains unresolved, so the aggregate 22-row discrepancy
remains open. No alternative full-May export was found in the scoped local
archive inventory, and no new Defense identity reconciliation is claimed.

### Count and export implementation scope

A read-only review of USAspending's public source at commit
`56ccdab55cdc6fa38854c036630288dad6e944d7`, committed June 12, 2026,
documents distinct stages. This was the latest commit returned on `master`
before June 13 UTC, **not a verified production deployment**:

- The [count endpoint](https://github.com/fedspendingtransparency/usaspending-api/blob/56ccdab55cdc6fa38854c036630288dad6e944d7/usaspending_api/download/v2/download_count.py#L44-L85)
  counts transaction search-index records under a response-cache decorator.
- The [export helper](https://github.com/fedspendingtransparency/usaspending-api/blob/56ccdab55cdc6fa38854c036630288dad6e944d7/usaspending_api/download/helpers/elasticsearch_download_functions.py#L59-L159)
  collects transaction IDs through a search point in time, populates a job lookup
  and joins those IDs to database transaction rows. It obtains its own count.
- The [contract export path](https://github.com/fedspendingtransparency/usaspending-api/blob/56ccdab55cdc6fa38854c036630288dad6e944d7/usaspending_api/download/filestreaming/download_generation.py#L297-L319)
  additionally filters database rows on `is_fpds=True` before SQL export.
- [Export-job reuse](https://github.com/fedspendingtransparency/usaspending-api/blob/56ccdab55cdc6fa38854c036630288dad6e944d7/usaspending_api/download/v2/base_download_viewset.py#L205-L246)
  uses stored requests and load/submission-window dates separately from the
  count-response cache. The ID collector also contains a timeout branch that
  can return a partial ID list, but its use in these jobs is not established.

The source code supplies concrete reconciliation stages, not a diagnosis of
this historical discrepancy. Cache reuse, source changes, incomplete ID
enumeration and database/filter differences remain unassigned possibilities.
Resolving them requires count-time membership, historical request/cache/job
records, matched index/database vintages and production-code identity. No
upstream code was executed or modified. Independent source review is pending.

Run `python3 scripts/review-procurement-partitions.py --scan` to reproduce the
34-archive comparison. Its default mode checks the saved ledger; the empirical
audit and notebook use that portable mode. These checks do not promote a
representative SAM export, historical exclusion intervals or causal estimates.

## Exclusions preflight response repair

The September 13 review of the [public v4 API documentation](https://open.gsa.gov/api/exclusions-api/)
found an acquisition defect in `scripts/probe-sam-exclusions.py`: the parser did
not recognize the documented top-level `excludedEntity` array. A successful
response in that structure was therefore reported as an empty page. The sample
formatter also missed `exclusionActions.listOfActions`, the `activateDate`
response field and the excluding-agency fields. Its generic recursive lookup did
not distinguish primary identity sections from other nested objects. This diagnosis was
reproduced offline with synthetic records; it does not explain or supersede the
previous live HTTP 401 authorization failure.

The repaired probe decodes the native entity array and treats unknown or malformed
response structures as unavailable. It reads identity only from
`exclusionIdentification`, keeps classification, exclusion type and program
separate, and displays each returned action separately with creation, update,
activation, termination, termination type and status fields. Missing values remain
blank; display positions are not source identifiers. The report counts decoded
entities on the requested page, not actions or the full query population, and
checks all returned entities before showing up to five samples.

Nine offline regression tests cover native and empty responses, malformed
structures, primary-versus-linked identity, action-date distinctions, missing
termination and action information, page-versus-sample counts, redacted request
metadata and report rendering. Synthetic action rows are not exclusion
observations. No live request was retried, no archive terms were accepted and no
source-product or simulator parameter changed in this repair. The API's active-only
coverage still cannot establish historical non-exclusion. Historical records,
identity adjudication and date/revision/censoring review remain necessary before
constructing exclusion intervals at award dates.

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

Selecting the README initially opened a Terms of Use acceptance dialog. On
September 13, after explicit user acceptance, the browser's Accept control was
activated. The signed-out attempt returned to the archive listing without an
inspectable file; a second attempt produced no download event within fifteen
seconds. The subsequent sign-in route reached Login.gov, where authentication
remains pending. These observations establish neither a downloaded README nor
the cause of the failed delivery. The terms approval is resolved; obtaining the
files is still open. Next, inspect the README's meaning of `MODIFIED`, original
snapshot dates, deletions/revisions and field definitions before extracting any
firm-level UEI intervals. Restrict acquisition to public files and keep any
restricted-source material out of the repository.
Snapshots at a few dates cannot establish continuous exclusion status between
those dates or non-exclusion throughout FY2024. This archive is a concrete
acquisition lead, not a promoted historical exclusion overlay.

### Public extract layout obtained independently

GSA's [Extracts Download API documentation](https://open.gsa.gov/api/sam-entity-extracts-api/)
provides a separate authenticated download route. Public downloads require an
eligible account and API key. Its `fileName` selector must be used without other
file-selection parameters. This documents a possible route; it does not prove
that the historical `MODIFIED` filenames or README are available through it.
The documented daily exclusions extracts contain currently active records.

The linked [public V2 layout](https://open.gsa.gov/api/sam-entity-extracts-api/v1/SAM_Exclusions_Public_Extract_Layout_V2.pdf)
was obtained September 13 and both pages inspected. Its footer identifies version
1.5, April 16, 2026. The 171,367-byte PDF has SHA-256
`b5d9aedcf81398bef1e3499af5cd30b31676966183c2929bdc93a94272775965`.
Relevant columns are:

| Column | Field | Linkage interpretation |
| --- | --- | --- |
| 16 | Open Data Flag | Provider provenance for business name/address; retain before reuse. |
| 17 / 18 | Deprecated blank / Unique Entity ID | Preserve the empty position; UEI is the separate entity identifier. |
| 24 / 31 | Active Date / Creation Date | Exclusion activation and creation in SAM are distinct dates. |
| 25 | Termination Date | Scheduled termination, or `Indefinite` when no date is set. |
| 26 | Record Status | Intentionally blank because this extract contains only active records. |
| 28 | SAM Number | Internal exclusion-record identifier, distinct from UEI. |

These definitions apply to this documented layout. They do not validate an
unread historical file's schema, revisions or coverage. A scheduled termination
is not proof of an observed termination. Neither the blank status nor a missing
match establishes historical non-exclusion. Preserve raw values and source
version before deriving status or intervals.

## Remaining empirical work

Freeze the intended agency/time population before a new export request. The
existing row/agency/date-span thresholds are only a screening floor, not evidence
of representative sampling. Reconcile matched SAM and USAspending actions in
the same period, quantify unmatched records and field disagreements by agency,
and compare coverage against the prespecified population. Establish protest and
historical exclusion coverage in that period before calculating event rates.
No-match is missing linkage until source coverage and identity are demonstrated.
