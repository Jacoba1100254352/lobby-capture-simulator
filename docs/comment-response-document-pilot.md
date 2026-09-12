# Agency-documented comment responses: heavy-duty Phase 3 pilot

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
