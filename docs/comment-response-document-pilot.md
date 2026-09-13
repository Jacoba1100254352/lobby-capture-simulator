# Agency-documented comment responses: heavy-duty Phase 3 pilot

## Publisher-original inventory and warranty follow-up, September 13

**Assessment: share with caveats for documentary measurement, not rates or causal
calibration.** This new source-first product is separate from all older pilots
below. Their original-file limits and counts are unchanged.

A complete visual review of the [MEMA publisher submission](https://www.mema.org/system/files/EPA-HQ-OAR-2022-0985%20MEMA%20Comments%20EPA%20HD%20GHG%20Ph3%20NPRM%2016June2023%20Final.pdf)
records 48 action/retention entries from one 28-page letter dated June 16, 2023.
The inventory includes 44 requested actions, one conditional request and three
retention positions. These are not 48 comments, independent observations or
policy changes. Related actions can share a response and are explicitly linked.
The labels are navigation aids; the cited original pages and locators control
interpretation, and independent segmentation review is pending.

`comment-publisher-inventory.json` preserves the full page-coverage map, compact
request labels, repeat/facet decisions and exclusions. Summary/body/appendix
restatements are collapsed; background claims, illustrative charts, quotations
and offers of additional data are not automatically extra requests. Distinct
actions, instruments or addressees remain separate. The ambiguous MY2028
condition on page 7 is not silently corrected. One indirect request is flagged.
Retention classifications describe the letter, not verified policy changes.
The page-2 opening statement on repair-information access is an explicit
context-only exclusion for independent review, not silently merged into the
repair-location request. The inventory is a declared coding, not a uniquely
determined count of every possible interpretation.

This is an access-led case, not a representative docket sample. Search snippets
had already exposed warranty excerpts and technology-neutrality discussion.
The whole-letter request frame was frozen before additional response matching,
but it was neither blinded nor preregistered. Its response-coding status at
frame freeze is retained; the separate follow-up below supplies later coding.

### Source identity and extraction risk

Public [submission metadata](https://api.regulations.gov/v4/comments/EPA-HQ-OAR-2022-0985-1570?include=attachments)
identifies comment 1570 and attachment 1. The attachment abstract matches the
publisher filename, and its reported 6,264,676 bytes match the acquired PDF.
Receipt and postmark are June 16; posting is June 21. The metadata's one-page
count describes the content file, not the 28-page attachment. The docket PDF
returned HTTP 403, so title/size agreement does not establish an exact byte
version match or independently verified historical archive time.

Ordinary text extraction loses most body text, and OCR also misses highlighted
requests. All 28 rendered pages were therefore checked; source highlights were
not added by the reviewer. Extraction cannot certify completeness. Raw public
source bytes remain ignored; only the minimal projection, hashes and coding
ledger enter the public package.

### Four-entry warranty comparison

All four inventory entries in the warranty theme were followed up. This theme
was selected after snippet exposure, not randomly. The [EPA response document](https://www.epa.gov/system/files/documents/2024-03/420r24007.pdf)
reproduces the relevant wording and original page citations at PDF 1461,
printed 1443. Its named summary is PDF 1466, printed 1448; the complete
section-11.2 response is PDF 1467-1468, printed 1449-1450.

| Inventory entry | Bounded finding |
| --- | --- |
| r26, repair locations | EPA explicitly names MEMA and says an existing provision addresses the concern. This is not a newly granted repair right. |
| r27, component specification | A named collective referral leads to a clarification with broader component coverage, not full acceptance of a narrow scope. |
| r28, wear/adjacency exclusions | The reviewed preamble and clause do not support a blanket exemption. Individual examples are not all separately adjudicated. |
| r29, supplier-informed list | No separate process decision in the reviewed passages. This is not docket-wide nonresponse or rejection. |

The [historical final preamble](https://www.govinfo.gov/content/pkg/FR-2024-04-22/pdf/2024-06809.pdf)
III.B.2, PDF 174-175 / printed 29613-29614, explains component coverage.
The published 40 CFR 1037.120(c) text at PDF 333 / printed 29772 was compared
with [proposal instruction 51](https://www.govinfo.gov/content/pkg/FR-2023-04-27/pdf/2023-07955.pdf),
PDF 199-200 / printed 26124-26125. Both versions have broad coverage; the final
text separates electric/hybrid components into their own sentence. That shared
comparison belongs to r27 and r28, not two independent policy changes. Printed
page references and actual PDF indices are recorded separately from footer form
numbers. This is not a review of current legal operativeness.

### Validation and remaining work

`comment-publisher-warranty-review.json` binds the four reviews to the frozen
request-frame hash, publisher bytes, agency excerpt, and proposal/final sources.
`scripts/review-comment-publisher.py` validates identity, page coverage, grain,
retention/conditional codes and non-attribution boundaries. Its optional source
arguments verify file hashes and regenerate the metadata projection; ordinary
offline audit checks do not independently authenticate manual source readings.
Mutation tests cover missing/duplicated entries, wrong pages or attachments,
content/attachment page-count confusion, stale bindings, unsupported acceptance,
and turning unadjudicated entries into nonresponses. The companion notebook
recomputes counts and displays the four findings.

At the warranty-only checkpoint, forty-four entries had not been adjudicated
against agency responses. The later technology review below reduces that pending
count to 35; broad requests can still be only partly resolved within reviewed scope.
Unadjudicated entries are neither nonresponses nor rejections. Further coding should use
the frozen frame, log search scope and preserve unresolved matches. Exact docket
version verification, independent coding review, and a justified population
frame remain requirements before stronger use. No causal simulator parameter
or older pilot count changes from this increment.

## Technology and fuel follow-up, September 13

**Assessment: share with caveats for bounded documentary coding, not causal
uptake or docket rates.** The separate `comment-publisher-technology-review.json`
follows up nine existing entries: r01, r04-r07 and r30-r33. These technical/fuel
and hydrogen-policy clusters were selected after response exposure. They are
not all technology requests, a blinded sample, or nine additional comments.
The frozen 48-entry frame and four warranty reviews remain unchanged.

### Findings and source links

All IDs below have prefix `mema-1570-`. Publisher page numbers are physical PDF
pages, also numbered in the letter. Response references are physical PDF pages
in the [March 2024 EPA response document](https://www.epa.gov/system/files/documents/2024-03/420r24007.pdf);
subtract 18 for its printed page number.

| Entry | Original pages; response locations | Bounded finding |
| --- | --- | --- |
| r01, technology neutrality | 2, 4-5; excerpts 80-81, named summary 108, response 132-134 | EPA explains a performance-based approach without a ZEV mandate. The letter already recognizes a performance-based proposal; no new concession or full technical acceptance is established. |
| r04, cleaner-combustion/fuel incentives | 4-6; excerpts 81, 1309, responses 1259-1263, 1321-1323 | EPA describes compliance pathways but does not grant blanket new incentives. The H2ICE multiplier refusal is the same decision discussed under r30, not another policy event. |
| r05, alternative-fuel analysis | 5; excerpt 1240, response 1259-1263 | Pathways and rule scope are explained. Completion of the requested additional comparative analysis is not verified. |
| r06, renewable-diesel compliance | 5; excerpt 1240, summary 1258, response 1259-1263 | Conditional exhaust-CO2 credit and the rule's lifecycle/fuel limits are discussed. The precise cited CARB off-road provision is not separately adjudicated in these passages. |
| r07, lifecycle-carbon assessment | 5-6; excerpt 81, responses 1259-1263, 1321-1323, 1608-1612 | EPA retains vehicle-based standard setting; broader requested assessment is not verified. The response does discuss some upstream hydrogen analysis, so this is not evidence that all upstream emissions were ignored. |
| r30, H2ICE multiplier extension | 14-15; excerpt 1411, summary 1319, responses 1321-1323, 1421-1423 | EPA explicitly names MEMA and declines a new multiplier as outside the reopened scope. This is a documented refusal, not missing response. |
| r31, FCEV multiplier retention | 14-15; excerpts 1309, 1411, response 1421-1423 | FCEV credit generation is retained as proposed through MY2027, with final restrictions on multiplier-credit use. This is not indefinite retention or an unchanged whole credit program. |
| r32, H2ICE zero-CO2 retention | 15; excerpt 1309, summary 1319, responses 1321-1323, 1421-1423 | The scoped vehicle clause is unchanged from the proposal. Neat-hydrogen vehicle treatment differs from engine certification and other-pollutant requirements. |
| r33, broader CARB exceptions | 15; excerpt 1309, named summary 1319, response 1321-1323 | The complete section-9.3 response does not separately commit to the requested CARB engagement. This is not docket-wide nonresponse or proof no interagency action occurred. |

The response review covers the complete general responses in sections 9.1, 9.3,
10.3.1 and 17.1, but only the opening performance-based discussion in section
2.1B. Section 9.1 stops before the ClearFlame-specific response on PDF 1263;
section 17.1 stops before individual responses on PDF 1612. Original statement
repetitions are matched at the recorded pages, not claimed as whole-letter
verbatim correspondence. Referenced RIA chapters were not independently reviewed.

### Two scoped proposal/final comparisons

The [April 2023 proposal](https://www.govinfo.gov/content/pkg/FR-2023-04-27/pdf/2023-07955.pdf)
and [April 2024 final rule](https://www.govinfo.gov/content/pkg/FR-2024-04-22/pdf/2024-06809.pdf)
support two comparisons, not two independently caused policy events:

- **Multiplier provision, shared by r30/r31:** proposed section 1037.150(p),
  PDF 201 / printed 26126, and final PDF 335 / printed 29774 enumerate PHEV,
  BEV and FCEV, without adding an H2ICE multiplier. Proposal PDF 88 / printed
  26013 already retains the 5.5 FCEV generation multiplier through MY2027.
  Final preamble PDF 165-166 / printed 29604-29605 and the final clause retain
  that generation but separate base/multiplier balances, restrict Phase 3 use
  in MY2027-2029 and prohibit multiplier use to certify MY2030 and later vehicles.
  Older Phase 2 deficit resolution is excepted; base credits have separate rules.
  PHEV/BEV generation through MY2027 differs from the proposed MY2026 cutoff,
  but that change is not attributed to MEMA's FCEV retention request.
- **Vehicle testing clause, r32:** proposed section 1037.150(f), PDF 201 /
  printed 26126, and final PDF 334 / printed 29773 have the same relevant
  neat-hydrogen vehicle zero-CO2 wording. Proposal preamble PDF 97 / printed
  26022 and final PDF 182 / printed 29621 distinguish this from other-pollutant
  engine obligations. Final preamble PDF 181-182 / printed 29620-29621 separately
  describes an optional engine default of 3 g/hp-hr and lower-emissions testing.
  This is a preamble reading, not an independent engine-clause comparison.

### Source discrepancies and interpretation risks

Three discrepancies remain explicit rather than silently corrected:

- **High analytical risk, program identity:** the original p5 footnote 3 and
  response PDF 1240 cite CARB's In-Use Off-Road Diesel-Fueled Fleets Regulation
  section 2449.1(f). PDF 1258 groups MEMA with cap-and-trade/Low Carbon Fuel
  Standard comments. That grouped summary cannot establish a response to the
  exact original program request; the CARB provision itself was not re-reviewed.
- **High analytical risk, units:** response PDF 1423 / printed 1405, footnote
  806, states the engine default as 3 grams CO2/ton-mile, whereas the final
  preamble uses 3 g/hp-hr. Both readings are preserved. No conversion or
  quantitative calibration is made, and neither is the vehicle zero-CO2 clause.
- **Medium navigation risk:** response PDF 1421 refers lifecycle comments to
  section 17.2. The heading and section-9.1 referral identify section 17.1.
  The review follows the verified heading without repairing the source text.

### Validation and remaining work

At the warranty-plus-technology checkpoint, the combined ledger contained 13 distinct entries with bounded response reviews
(four warranty plus nine technology/fuel), leaving 35 entries without a response
adjudication. This coverage count does not mean all facets of the thirteen are
resolved. Broad assessment, precise CARB-program and state-engagement requests
retain the limitations above. There is still one letter, zero independently
reviewed entries, no docket-rate eligibility and no identified individual effect.

`validate_all` in `scripts/review-comment-publisher.py` checks the frozen
inventory binding, thematic selection, physical/printed page mappings, source
links, shared comparisons, units and claim boundaries. Its older `validate`
function remains explicitly warranty-only and returns the historical 44 pending
entries. A three-argument `validate_all` call retains the historical 35-entry
pending count; current four-ledger CLI, audit and notebook calls include the
infrastructure follow-up below.
Mutation tests reject unsupported acceptance, altered scope, unit/program
conflation and duplicate coverage. The notebook displays both thematic products
and the source cautions. Optional archived-source checks verify all five file
hashes and regenerate the metadata projection, not independent coding or exact
docket-copy identity. No current regulatory-status or simulator-calibration
claim is made. Procurement and substitution requirements remain open.

## Infrastructure and monitoring follow-up, September 13

**Assessment: share with caveats as bounded documentary coding, not an uptake
rate, current legal-status assessment or identified lobbying effect.** The new
`comment-publisher-infrastructure-review.json` reviews seven existing entries:
r02, r03, r14, r16, r18, r22 and r23. Selection followed infrastructure/coordination
topics and prior response navigation, not outcome-blind sampling. The original
48-entry frame and earlier follow-up ledgers are unchanged. Other infrastructure
requests, including utility buildout and vehicle-specific modeling, are not
implicitly reviewed by this thematic grouping.

The original publisher pages 4, 9-12, 23 and 25-26 were rechecked visually.
Highlighted recommendations missing from OCR govern the request definitions.
The same hash-bound [EPA response document](https://www.epa.gov/system/files/documents/2024-03/420r24007.pdf),
[proposal](https://www.govinfo.gov/content/pkg/FR-2023-04-27/pdf/2023-07955.pdf)
and [April 2024 final publication](https://www.govinfo.gov/content/pkg/FR-2024-04-22/pdf/2024-06809.pdf)
provide the comparison. Hashes and physical/printed page maps are in the ledger.
These are historical publications; subsequent implementation and legal status
are not assessed.

### Request-to-response findings

RTC printed pages are physical PDF pages minus 18. The review reads the complete
general responses, not all comments, in sections 2.9 (PDF 518-519), 2.10 (524),
6.1 (907-913) and 6.4 (991-993). Section boundaries prevent a search hit or one
favorable paragraph from standing in for a complete scoped response.

| Existing request | Original / RTC excerpt PDF pages | Bounded finding |
| --- | --- | --- |
| r02, Joint Office coordination | 4 / 522 | Section 2.10 commits continued federal/stakeholder engagement, not complete alignment of every requested regulation or priority. |
| r03, assumption follow-through | 4 / 522 | Monitoring and reporting cover infrastructure and critical materials; they do not guarantee assumed outcomes or automatic corrective action. |
| r14, increased interstate funding | 9 / 522-523 | Coordination, existing programs and corridor planning are described. A specific increased funding target answering the request is not verified. |
| r16, DCFC/bidirectional public purchases | 10 / 875 | Section 6.4 names MEMA among future-proofing commenters and acknowledges V2G benefits, but says these were not quantitatively included in the analysis. The requested funding criterion is not verified. PDF 987 reproduces the rationale, not the actual public-purchase recommendation. |
| r18, public readiness dashboard | 10 / 875 | Periodic reporting aligns with a broad information objective. A separate adoption of the requested Joint Office dashboard is not established in the compared passages. |
| r22, charger lifecycle standards | 11 / 876 | Existing NEVI, reliability and voluntary efficiency programs are discussed; full adoption of the installation/operation/maintenance request is not established. |
| r23, charging cybersecurity policy | 11-12 / 876-877 | No separate disposition of this specific request is found in the complete section-6.1/6.4 general responses. This is not docket-wide nonresponse; reliability and V2G benefits are not cybersecurity standards. |

### Shared preamble comparison

Proposal PDF 9 and 75 (printed 25934 and 26000) describe existing monitoring,
public compliance reports and an invitation for additional information and
stakeholders. Final PDF 14 and 41-43 (printed 29453 and 29480-29482), including
the complete section II.B.2.iii, add specified commitments to engagement,
infrastructure/material monitoring and periodic reports. The final states data
collection will begin in CY2025 and reports could begin **as early as CY2026**;
these are publication-stated plans, not verified dates of actual implementation.
Possible later guidance, rulemaking or no change remain discretionary. The
automatic infrastructure-to-stringency mechanism requested by other commenters
is not adopted; that request is not assigned to MEMA.

This one comparison supports r02, r03 and r18 at different scopes. It is not
three independent policy changes, an operative CFR-clause comparison, proof
MEMA originated the proposal, or a measured individual influence effect.

### Source risks and validation

- **High attribution risk:** RTC 991 explicitly opens the public-information
  response by naming DTNA. Its mandatory-reporting refusal on 992 cannot be
  treated as an explicit rejection of MEMA's dashboard request.
- **High scope risk:** RTC 990 groups MECA and MEMA under minimum charger
  efficiency. The original MEMA request on page 11 concerns installation,
  operation and maintenance; the reproduced MECA excerpt on RTC 987 explicitly
  seeks minimum efficiency. Preserve those different instruments.
- **Medium timeline risk:** RTC 991 prints phase three as 2030-2045 and phase
  four as 2035-2040 while describing completion by 2040; RTC 912 describes four
  phases over 2024-2040. This internal tension is retained, not corrected or
  used as an outcome. The cited strategy schedule is not independently reviewed.

The combined four-ledger check now counts **20 distinct reviewed entries and
28 awaiting adjudication**, still in one letter. Reviewed entries may retain
unresolved facets. Zero entries have independent-review clearance or eligibility
for a docket response rate. The validator and mutation tests protect request
identity, exact page mappings, shared comparisons, the reporting-start qualifier,
attribution and scope cautions, and unchanged claim limits. They validate the
saved contract, not the truth of manual coding. The notebook reruns the checks
and displays the seven dispositions, comparison facts and cautions.

Independent source/coding review, exact docket-version verification and a
defensible sampling frame remain separate blockers to stronger claims. Detailed
grant instruments, underlying charger standards, RIA calculations and actual
implementation are not independently evaluated by this follow-up. No earlier
pilot or simulator parameter changes, and procurement/substitution work remains
unfinished.

## Original two-request agency-excerpt pilot

Reviewed 2026-09-12. Assessment: **share with caveats** for documentary coding;
not ready for an uptake rate, causal effect or simulator calibration.

## Question, selection and unit

Can a specific submitted request be linked to an explicitly named agency
response, while distinguishing clarification from rejection? This separate
historical pilot contains two comment-request observations from section 2.5 of
EPA's March 2024 Phase 3 response document, in docket EPA-HQ-OAR-2022-0985.
The requests were purposefully selected after reading responses. They are not a
random sample, complete section census or denominator for a response rate.
Neither observation belongs to the existing 500-comment Utah corpus or promotes
its candidate response-linkage product. No current regulatory-status claim is made.

## Source-reviewed observations

The [EPA response document](https://www.epa.gov/system/files/documents/2024-03/420r24007.pdf)
reproduces the request excerpts, identifies their comment/attachment IDs and
original page citations, and explicitly names both organizations in its response.
The table's page numbers refer to that response PDF, not the unread original letters.

| Request | Agency response | Reviewed response-document location |
| --- | --- | --- |
| Cummins: clarify whether the credit equation covers tractors as well as vocational vehicles | `clarified_existing_scope`: EPA confirms that tractor credits continue under the equation | Request: PDF 458, printed 440; response: PDF 462, printed 444 |
| Allison: correct alleged errors in proposed light heavy-duty vocational standards calculations | `disagreed_with_error_claim`: EPA disagrees that the proposed calculation had the alleged error | Request: PDF 457, printed 439; response: PDF 462, printed 444 |

Short response anchors are "In response to Cummins, we clarify that manufacturers
can continue" and "we disagree that there was an error in the NPRM".
The Cummins excerpt cites EPA-HQ-OAR-2022-0985-1598-A1, original pages 9-10.
The Allison excerpt cites EPA-HQ-OAR-2022-0985-1657-A2, original page 2, and
refers to an appendix on pages 4-5 that has not been read here.

Public API metadata for [Cummins](https://api.regulations.gov/v4/comments/EPA-HQ-OAR-2022-0985-1598?include=attachments)
and [Allison](https://api.regulations.gov/v4/comments/EPA-HQ-OAR-2022-0985-1657?include=attachments)
confirms the distinct submission IDs, titles, docket, receipt date of June 16,
2023, and respective posting dates of June 22 and June 29. Timestamps are
preserved as returned in UTC; calendar-date ordering is checked without inferring
an exact deadline-time eligibility rule. Attachment metadata identifies Cummins's
comment as attachment 1 and Allison's comment as attachment 2; Allison's
attachment 1 is a cover letter. These orders agree with the agency citations.
Both relevant original PDF downloads returned HTTP 403 during acquisition.
The request representation is therefore `agency_reproduced_excerpt`, not an
independently read or version-matched original submission. This is stronger than
title-only candidate matching but still has an explicit source-access limit.

## Rule-text comparison and non-attribution

The [April 2023 proposal](https://www.govinfo.gov/content/pkg/FR-2023-04-27/pdf/2023-07955.pdf)
(PDF 211, printed 26136, instruction 91) and
[April 2024 final rule](https://www.govinfo.gov/content/pkg/FR-2024-04-22/pdf/2024-06809.pdf)
(PDF 350, printed 29789, instruction 103) were visually compared for the
40 CFR 1037.705(b) equation and its Std definition. The final definition retains
the generic regulatory-subcategory standard and omits the proposed extra sentence
requiring a common reference for MY2027+ zero-CO2 vocational vehicles.
That text difference is observed; attributing it to Cummins is not justified.
EPA's explicit clarification describes continued tractor eligibility, not newly
granted eligibility. The section's broader method change addresses collective
concerns (PDF 461-462, printed 443-444), not one identified comment's effect.

The [June 2024 correction](https://www.govinfo.gov/content/pkg/FR-2024-06-17/pdf/2024-13196.pdf)
(PDF 1-2, printed 51234-51235) separately describes errors introduced in preparing
the final text for publication, including a tractor/vocational table substitution.
That later event does not establish acceptance of Allison's allegation about
the proposed calculation. Disagreement with that allegation also does not prove
that Allison had no influence elsewhere in the rulemaking.

## Provenance and validation

`data/calibration/first-wave/comment-response-document-pilot.csv` records the
two request-level codings. Its companion `comment-response-document-source.json`
preserves public metadata projections and raw-response hashes, four PDF hashes,
reviewed PDF/printed pages, request/response paraphrases, short anchors and scope.
No full corporate letter, private key, restricted cache or local path is packaged.
For this original two-request pilot, only the six pages listed in its source
JSON were visually reviewed, along with the specified proposed/final/correction
pages. The separate inventory below extends the reviewed section coverage
without rewriting the pilot's original selection or provenance.

The introduction (PDF 19-20, printed 1-2) explains that technical comments are
reproduced as excerpts, may recur by topic, and need not be the only comments
answered by a response. Selecting from these excerpts conditions on agency
selection, so it cannot identify comment-authenticity or triage effects. The
introduction also shares the docket with a separately finalized locomotive rule
and gives the final preamble priority in any inconsistency. Its reference to
comments after July 18, 2024 conflicts with its March 2024 document date; that
apparent chronology error is retained as a caveat, not silently corrected or used
to determine the pilot's eligibility.

`make empirical-expansion-audit` checks row grain, metadata fingerprints,
submission/attachment-order links, chronology, reviewed-page mappings, scope
codes and source-bound coding fingerprints. `make test` includes regressions for
duplicates, swapped identities, wrong attachment orders, changed PDF hashes or
page references, missing dates and unsupported promotion. The offline
`notebooks/empirical-expansion-review.ipynb` reproduces the two classifications.
These consistency checks do not download or authenticate the original sources
and do not independently establish that manual coding is correct.

## Remaining requirements and next decision

A September 13 UTC access follow-up located CARB's own
[program-page link to its Phase 3 comments](https://ww2.arb.ca.gov/es/node/23406).
It points to [comment 1591](https://www.regulations.gov/comment/EPA-HQ-OAR-2022-0985-1591),
which the ordinary public browser displayed as a CARB submission received and
postmarked June 16, 2023, posted June 21, with one Comment attachment. This
corroborates the section inventory's cited submission identity, not the original
PDF's content or version. The direct attachment returned HTTP 403, and the
browser could not open it. The Volvo attachment also returned HTTP 403 through
the web reader. A bounded publisher search did not recover an original copy for
the existing Cummins/Allison pilot; it does not establish that none exists.
User-provided original PDFs were requested. No new request rows, original-file
verification, uptake classification or independent-review clearance resulted.

Independent source/coding review is pending for both observations. The reviewer
should check the cited excerpts and named responses, distinguish the collective
method change, and verify any subsequently available original attachment against
the agency excerpt without treating metadata agreement as a full version match.
Retain disagreements and missing access in the review ledger.

Before expanding to rates, define the population, sampling rule, request-level
codebook, treatment of repeated/grouped responses and nonresponses, and review
procedure independently of observed favorable outcomes. Neither two selected
responses nor a broader response-document census supplies a causal comparison
by itself. Until those requirements are met, the defensible result is two
documented responses with different dispositions, not a measured lobbying effect.

## Complete section inventory, with a restricted denominator

The separate `comment-section-inventory.csv` and
`comment-section-inventory-source.json` now record a visual review of **all six
pages of section 2.5**, PDF 457-462, printed 439-444. The section begins partway
down PDF 457; the preceding section's material is excluded. Its response ends
on PDF 462. Text extraction identifies section 2.6 on the next page, outside
this coding scope. The downloaded PDF hash agrees with the earlier pilot.

This is a retrospective inventory of **seven agency-selected organization
blocks and eleven segmented requests**. The section was chosen after reading
its responses. It is not a prospective or representative sample, a census of
the seven original submissions, or a docket-wide response denominator. The
original two requests are included, with explicit overlap IDs, not added as
two extra observations. Original attachments remain unread and version matches
unestablished. New submission identities/orders come from EPA's excerpt
citations, not independently acquired metadata for every organization.

### Segmentation and response coding

One row represents one separable requested action or explanation within an
organization's reproduced section block. Repeated wording and cross-references
to the same request are collapsed. EPA's quoted requests for comment are not
the organization's requests. DTNA's response to EPA request 54 points elsewhere
without adding a substantive request in the excerpt; response 55 refers back
to response 53. Neither adds another row. Its engineering-judgment request on
original page 76 and again on pages 167-168 is counted once.

China's method/source question is separate from its international-comparability
question. Volvo's joint request is split into standard-setting and vehicle
categorization actions. PACCAR's MY2030 fallback stays a separate **conditional**
request linked to its main categorization request. These segmentation decisions
are explicit and remain subject to independent review.

| Organization | Requests | Section-level finding |
| --- | ---: | --- |
| Allison | 1 | EPA explicitly disputes the alleged calculation error. |
| CARB | 1 | The Multi-Purpose-only request conflicts with the described resolution, but EPA does not explicitly name CARB in its summary or response. |
| China WTO/TBT center | 2 | EPA gives a named qualitative explanation of international comparability limits; the separate request to reconstruct the proposed table's method/sources has no request-specific disposition here. |
| Cummins | 1 | EPA explicitly clarifies continued tractor-credit eligibility. |
| DTNA | 2 | Subcategory discretion aligns with the collective response; its averaging-set exemption has no separate disposition here. |
| PACCAR | 2 | Intended-use categorization aligns with the collective response; the MY2030 fallback is not separately adopted after EPA says it did not finalize the triggering proposal. |
| Volvo | 2 | Standard-setting and categorization concerns align with the collective revision, not two independently attributable policy changes. |

There are three explicitly named request responses, four links through a named
summary and collective response, one comparison with the section resolution
without a named link, and three requests lacking a separate disposition here.
The last category includes PACCAR's conditional fallback. For these unresolved
requests, response-page fields describe the searched response region, not an
observed answer. Absence of a separate disposition **in this section** is not
proof of nonresponse across the docket. A future search of other response
sections must record its expanded scope. Likewise, consistency with a shared
revision does not establish full acceptance, an independently verified enacted
text change for each request, or individual influence.

### Appendix A is not a nonresponse control group

Visual review of Appendix A's introduction, Tables A-1/A-2 and general response
(PDF 2050-2051, printed 2032-2033) confirms EPA's description of 1,011 general or
insufficiently specific comments not reproduced verbatim. EPA says responses
elsewhere address their general topics. Table A-3's individual list and these
original submissions were not reviewed. **Not reproduced does not mean
unanswered.**

Table A-1's counts sum to 1,011 comments. Weighting those counts by the number
of topics gives 2,533 theme incidences, matching Table A-2's eight theme counts.
Table A-2 percentages use the theme-incidence total, not 1,011 unique comments.
The preceding prose reports environmental justice as 28.0%, while the table
shows 28.1%; both source statements remain documented rather than silently
harmonized. Neither appendix total is a valid control/nonresponse denominator
for the selected section, and no response rate is computed.

### Validation and remaining work

Assessment: **share with caveats** as a source-bound documentary inventory,
not as an uptake estimate. All six section pages and both appendix pages were
visually checked. The offline audit verifies the fixed organization/request
frame, attachment citations, reviewed-page mappings, old-pilot overlap,
conditional-parent link, shared-response grouping, appendix arithmetic and
CSV/source fingerprints. The companion notebook reproduces these checks and
the request-level results. Its code can also regenerate the CSV using
`audit.comment_section_rows(section_sources)`; the audit rejects a stale
projection. Tests exercise missing and repeated requests, wrong identities,
unreviewed pages, altered coding, lost overlap, invented response matches and
unsupported promotion.

These are consistency checks, not independent coding review or fresh source
authentication. High-impact unresolved risks are agency/outcome-conditioned
selection, unavailable originals, unreviewed request segmentation and links,
and the absence of a credible causal contrast. The next review must check the
eleven-request segmentation and all seven blocks, especially the opposing CARB
position, repeated DTNA request, joint Volvo request and conditional PACCAR
fallback. A docket-rate study additionally requires an independently defined
comment population, duplicate/grouped-response rules and treatment of missing
access. This inventory advances comment coding independently of the SAM and
substitution tracks; it does not complete those tracks or recalibrate the model.

## Cross-section follow-up: DTNA averaging-set flexibility

The separate `comment-request-followups.json` preserves a targeted later review
of `s25-dtna-averaging`. Its fingerprint binds it to the unchanged eleven-request
inventory. The original section-2.5 finding remains correct within that section;
the follow-up adds evidence from section **10.3.2**, not a twelfth request or a
new sample. Selection followed the known unresolved request, using `1037.740`
and averaging-set-limit terms in the full response-document text.

EPA reproduces DTNA's detailed request at PDF 1425-1426, printed 1407-1408,
citing the same submission/attachment, **EPA-HQ-OAR-2022-0985-1555-A1**, original
pages 74-75 and 171. The earlier section cites original pages 167-168. Both
excerpts ask to exempt ZEV-generated credits from averaging-set restrictions.
This is a source-cited identity/action match, not an independently read or
version-matched original. Repeated wording is not another submission.

The complete summary (PDF 1430-1432, printed 1412-1414) names DTNA's request.
The complete response (PDF 1432-1434, printed 1414-1416) is collective. It
describes an interim transfer flexibility while retaining weight-based averaging
sets and declining vehicle-to-engine credit transfers. The documented disposition
is **partial alignment with interim flexibility**, not full acceptance or an
individually attributable change.

| Facet of this one request | Reviewed evidence and interpretation |
| --- | --- |
| Vehicle-category transfers | The shared response allows interim vehicle-to-vehicle transfers. The published clause permits part-1037 credits to be used through MY2032 in the named vehicle averaging sets. This is a bounded permission, not deletion of all averaging-set rules. |
| Program-life duration | DTNA requested availability throughout Phase 3's life. The response and published use limit are interim, through MY2032. The clause also covers specified pre-2027 advanced-technology credits; a use cutoff is not the same as a generation-date window. |
| Traded credits | The published text allows trading redesignated credits, subject to ordinary trading and retained credit restrictions. |
| No discount | No separate, comprehensive no-discount disposition is verified. No volume cap is not the same as no discount. Adjacent 10-percent discounts apply to credit-balance corrections, not a general transfer charge. |

The [published April 2024 text](https://www.govinfo.gov/content/pkg/FR-2024-04-22/pdf/2024-06809.pdf)
was visually reviewed at PDF 337, printed 29776, for 40 CFR 1037.150(z), and
PDF 351, printed 29790, for 1037.720(a), instruction 108/1037.740, and adjacent
credit-correction context. Other cross-references, all part-86/1036 provisions,
and subsequent amendments were not exhaustively reviewed. The retained credit
restrictions prevent a blanket no-discount or unrestricted-transfer claim.

Crucially, the [April 2023 proposal](https://www.govinfo.gov/content/pkg/FR-2023-04-27/pdf/2023-07955.pdf),
PDF 88, printed 26013, already invited comment on an interim cross-set option
for MY2027-2032 with possible caps. That preamble page was visually reviewed.
It records an option under consideration, not an already adopted rule. Selecting
a related option after comments does not demonstrate that DTNA originated it or
caused EPA to select it. The response also discusses other supporters and
opponents, so there is no isolated commenter counterfactual.

Assessment: **share with caveats** for the cross-section documentary link.
The follow-up source records ten newly reviewed PDF pages across three documents,
four facets of one existing request, exact page mappings and hashes, the baseline
fingerprint, and pending independent review. It does not census the whole
eleven-page section 10.3.2. Offline tests and the notebook check the old/new scope
separation, identity, pages, retained restrictions, interim timing, and no-causal
boundary; they do not independently validate the reading. Original-file access,
independent coding review and a valid docket population remain unresolved. The
other two section-2.5 disposition gaps are not resolved by this follow-up.
