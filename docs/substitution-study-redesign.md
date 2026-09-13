# Substitution study redesign

Updated 2026-09-13 UTC. Status: expanded sources, identification unresolved.

## New evidence and its limits

`substitution-expanded-lda-panel.csv` contains 1,119 issue rows, 427 filing UUIDs
and six candidate actors over 2003-2008. The acquisition queried eight
canonical actors; two had no exact-name rows. A reviewed, registration-specific
AdvaMed name variant restores fifteen filings omitted by the earlier exact-name
query, retaining all 412 previously acquired filings. All six API-attributed candidates now
have nine distinct pre-enactment reporting periods after excluding registration
forms. These are chiefly semiannual periods, not independent quarters. A split of
a semiannual amount cannot add pre-trend information. The original 2007-2008
diagnostic remains separate so its published failure analysis is reproducible.

One record, `a93a23e5-9da2-4c18-8625-b41fc0987d06`, has a posting date preceding
its 2004 covered period. Visual review of page 1 of the
[original scanned filing](https://lda.gov/filings/public/filing/a93a23e5-9da2-4c18-8625-b41fc0987d06/print/)
confirms reporting year 2004, termination date January 5, 2005, and the checked
income category "Less than $10,000." The API instead returns posting date
1995-05-19, no termination date, and income `0.00`. The acquired row preserves
those API values for provenance, but its point amount is censored rather than
a verified observed zero. Do not invent a corrected filing date from a
termination date. Posting timestamps alone are not a validated amendment-ordering
rule. Registration forms, amendment families, unknown/below-threshold amounts,
and possible in-house/retained-firm overlap must be reviewed before aggregation.
The expanded rows carry `unassigned_design_candidate`, not treatment labels.
The legacy 2007-2008 diagnostic inputs are unchanged.

Two additional 2003 filing UUIDs, `9bd361f7-98e7-46a9-90cd-267ace5ca84c` and
`bcb55688-3d56-4c98-a546-0730eb923bfa`, also have posting dates before their
covered periods; their complete cover scans are now reviewed below. Filing-level amounts
are repeated on issue rows, not allocated across issues. Any monetary total
must first collapse to verified unique filings and resolve amendments; summing
issue rows would multiply the same amount. The source collector fails closed
on request errors, malformed responses, incomplete result counts, duplicate query
UUIDs and pagination truncation. The entire 2003-2008 acquisition was rerun
successfully under those rules. A same-UTC-day public-response cache supports
resumption without refetching successful pages; cache URL, date and content
hashes are checked. Authentication and quota errors are not automatically retried.

### Complete review of the three flagged posting dates

The separate `substitution-lda-date-reviews.json` covers all three unique filings
whose API posting date precedes the reporting-period start in the frozen
427-filing panel. This is an anomaly-selected review, not evidence that the
other 424 dates are correct or that the population is complete. September 12
public API rechecks still match the saved metadata for all three records.

| Filing | API posting date | Source receipt stamp date | Full Senate ID on the cover |
| --- | --- | --- | --- |
| [APGA candidate, 2003H1](https://lda.gov/filings/public/filing/9bd361f7-98e7-46a9-90cd-267ace5ca84c/print/) | 2002-08-29 | 2003-07-31 | 74077-12 |
| [AAJ/ATLA, 2003H2](https://lda.gov/filings/public/filing/bcb55688-3d56-4c98-a546-0730eb923bfa/print/) | 2003-02-24 | 2004-02-24 | 4733-12 |
| [Shea & Gardner for API, 2004H2](https://lda.gov/filings/public/filing/a93a23e5-9da2-4c18-8625-b41fc0987d06/print/) | 1995-05-19 | 2005-01-19 | 35024-90 |

Receipt dates are separately transcribed observations, **not corrected API
posting dates**. The stamps show times without an explicit timezone; no UTC
timestamp is inferred. The official [API schema](https://lda.gov/api/openapi/v1/)
labels the query filters as date-posted filters and supplies a read-only
date-time field separately from the termination date. The inspected definitions
do not establish how to convert a receipt stamp into a posting timestamp or
guarantee amendment ordering. The origin of the date discrepancies remains
unknown; these checks do not establish whether a filing was late.

The ordinary PDF render clips the right edge of these scanned forms. Extracting
the original embedded image with `pdfimages -f 1 -l 1 -png` reveals the full
cover without modifying its pixels. Object 6 0, a 1696-by-2200 image, occurs on
PDF pages 1 and 2. The three PDFs have 8, 28 and 6 pages respectively; their
cover images are each one underlying scanned form page, not two independent
records. The full images recover the registration components, AAJ's checked
year-end box, and the complete receipt stamps. This review covers those three
embedded covers only, not every page of the filings or their version families.
The JSON retains PDF, extracted-image and API-response hashes plus the public
API projection, scan identifiers, reviewer, date and pending independent review.

The APGA candidate's cover names **Bert Kalisch**, checks Self and Method A,
and reports $100,000 of expenses. Both expense-threshold boxes appear unchecked;
the numeric disclosure is retained with that caveat. The full Senate ID matches
API registrant 74077 and client-relationship component 12, despite the API's
organization name. That matches this source registration, not every historical
name or organization-level financial perimeter. AAJ's historical ATLA cover
reports $2,380,000 of expenses using Method A; its year-end, Self and threshold
boxes are checked. Both API accounting methods remain null. These are two
additional filing-specific method observations, not permission to carry Method A
across either organization's whole history.

The Shea & Gardner cover supplies no point income amount: its selected category
is below $10,000. The source API zero remains unchanged, while the reviewed
disclosure is censored and cannot be used as an exact zero. The checked
termination box gives January 5, 2005, separately from the January 19 receipt
stamp; the API termination date remains null. The API filing type YT already
labels the report as a year-end termination. All three cover amendment boxes
are unchecked; no API amendment-status conflict is established. In particular,
`sameClientRegistrantName` is a name-comparison flag, not amendment status.

**Assessment: share with caveats for the source discrepancies.** The timing and
censored-amount issues are high-risk for version selection and aggregation.
The offline audit checks the complete flagged frame, fresh-source projections,
registration components, dates, field distinctions and no-promotion boundaries;
it does not independently authenticate the manual reading. Next, review complete
filing families and methods before constructing comparable actor-period totals.
No receipt date repairs treatment exposure, and no matched registration supplies
a valid untreated control. Independent review and source-date explanations
remain unresolved.

### Candidate version families and the APGA partial amendment

`substitution-lda-family-queue.csv` inventories all **22 multi-record groups**
within the frozen acquisition: 46 filings grouped by registrant ID, client
relationship component, year and native period. Excluding 39 registration
records leaves 388 report records in 364 candidate groups. This is not a census
of complete historical version families; even singleton groups can have missing
versions, and one singleton is itself labeled an amendment. Ten multi-record
groups have no amendment-labeled filing. A repeated group is therefore neither
an automatic duplicate nor necessarily an original/amendment pair.

The reproducible queue flags eight groups with different nonmissing source
amounts, three with tied posting timestamps, two where the latest timestamp has
no amount although another record has one, and one with a nonzero amount on a
record labeled No Activity. These are overlapping review flags, not mutually
exclusive classes or verified source errors. Different decimal representations
of the same numeric amount are not counted as different amounts. Income and
expenses remain separate measures. A no-activity label is not a rule for setting
income to zero, and neither the latest posting nor an amount match selects a
final version. The source reviews below now reach seven candidate groups;
fifteen remain unreviewed at source-page level. Reviewed groups are not thereby
certified as complete historical version families.

The separately selected APGA 2003H1 group has a terminal [official API query](https://lda.gov/api/v1/filings/?registrant_id=74077&filing_year=2003&filing_period=mid_year&page_size=100)
with two unique records and no next page. Both reproduce every frozen metadata
field and identify registration 74077-12 and client API ID 167305. This verifies
the query scope, not all aliases or the completeness of original paper packets.
The [original report](https://lda.gov/filings/public/filing/9bd361f7-98e7-46a9-90cd-267ace5ca84c/print/)
contains four distinct embedded images, each repeated on two PDF pages: cover,
TAX activity, ENG activity and information update. Its update page removes TRA
from previously reported issues; that is not another current activity page.
The [amendment download](https://lda.gov/filings/public/filing/50ca0707-6dc1-43a0-9115-89ba56ffd0c7/print/)
contains only one distinct ENG issue image, also repeated on two PDF pages.
Its fax/image pagination refers to a larger sequence. No financial cover is
present in that download, but these observations do not prove which additional
pages were filed or how omitted financial fields should inherit values.

| Reviewed field | Original ENG image, PDF 5/6 | Amendment ENG image, PDF 1/2 | API representation |
| --- | --- | --- | --- |
| Contacted bodies | House, Senate, FERC | Same three bodies | Original: House, Senate, Treasury; amendment: House and Senate only |
| Field 18 lobbyist list | Blank | Handwritten Bert Kalisch | Both already name Bert Kalisch |
| Signature date | July 21, 2003 | July 21, 2003 | API posting dates are different fields, not signature dates |
| Financial amount fields | Not on this issue page | Not on this issue page | Original expense 100000.00; amendment income and expenses null |

The amendment retains the original ENG scan number 00000232930 beneath the
later scan number 00000480590. Its receipt stamp is February 24, 2004 at 9:33 AM
without an explicit timezone. Matching issue text, contacts and the older scan
number support a field-specific comparison. They do not establish that filling
the lobbyist field was the only intended amendment. In particular the original
TAX page, on PDF 3/4, is not the corresponding ENG page.

`substitution-lda-family-review.json` retains the minimal public query projection,
official filing-type catalog, original PDF and full-image hashes, page/object
map, transcription and explicit unresolved decisions. Agency names use obvious
API-label equivalents for comparison, with literal source text retained. Both
ENG contact lists differ from their scanned pages; the cause of the discrepancy
is unknown. The API should not be assumed to preserve the original-versus-amended
field history or provide faithful agency exposure without source validation.

#### NVG: a candidate group contains different clients

The next amount-conflict/posting-tie pair supplies a counterexample to treating
the API grouping as a real financial-version family. The frozen records and a
fresh [NVG 2005H2 API query](https://lda.gov/api/v1/filings/?registrant_id=76833&filing_year=2005&filing_period=year_end&page_size=100)
assign both selected UUIDs to AAJ, client API ID 169036, relationship 330 and
type YY, with the same February 8, 2006 posting date. The query returns fourteen
records on one terminal page; only these two covers are reviewed here.

| Selected source cover | Client named on the cover | Full Senate ID | Amendment box | Income disclosure |
| --- | --- | --- | --- | --- |
| [b53db4eb](https://lda.gov/filings/public/filing/b53db4eb-a3e2-465a-91b4-51e10da90408/print/) | Association of Trial Lawyers of America | 76833-113 | Checked | $100,000, threshold box checked |
| [cda90ce4](https://lda.gov/filings/public/filing/cda90ce4-487d-415a-98d9-535be41f6b94/print/) | America Votes | 76833-330 | Unchecked | $60,000, threshold boxes appear unchecked |

Both covers name Nueva Vista Group, LLC. The House IDs are 35960005 for ATLA
and 35960015 for America Votes. The latter corrects an earlier reviewer
transcription, not the raw API or source image. The ATLA name
is consistent with AAJ's historical name, but its suffix 113 and checked
amendment box differ from the API representation. The America Votes cover
matches suffix 330 but identifies a different client, so it is **not eligible
for AAJ attribution**. This pair must not be merged as alternative spending
versions of one AAJ client-period. The queue marks it
`source_identity_conflict_not_mergeable`; no replacement identity or final
amount has been written into the frozen source records.

Each PDF has six rendered pages containing three repeated image objects.
This identity review covers the full embedded cover only, not its other pages.
Both have a handwritten February 8, 2006 received date and a July 5, 2006 fax
header; those dates are preserved separately and do not order amendments.
The source JSON retains both PDF/cover hashes, the complete query UUID inventory
and the two exact metadata projections. The remaining twelve queried records
are not cleared by that query or cover pair. A follow-up now reviews all 21 NVG
records in the frozen acquisition, as described below. The source-indexing
cause is unknown, and independent review remains pending.

#### NVG frozen-history identity review

The follow-up covers the full **21-record frozen NVG subset**, not all public
NVG filings: seventeen embedded PDF covers and four electronic HTML print forms.
Some older PDF wrappers crop the underlying scans, so the full embedded image
was extracted and visually reviewed. The 2008 print responses are HTML, not
independently archived historical scans. Their identity and selected timing
fields were read from the downloaded markup. Other pages and financial-version
histories remain outside this review.

| Source client-name category | Records | Identity disposition |
| --- | ---: | --- |
| ATLA name variants | 9 | Historical-name candidates, not fully cleared identities |
| AAJ name variants | 6 | Matching-name candidates, not fully cleared identities |
| America Votes | 6 | Ineligible for AAJ attribution; includes one registration and five activity filings |

The America Votes activity filings occupy 2005H1, 2005H2, 2006H1, 2006H2 and
2007H1 in the API. Each is grouped with an ATLA/AAJ-named report, yielding **five
mixed-client candidate groups**. The queue marks all five not mergeable. The
[America Votes registration](https://lda.gov/filings/public/filing/8e4c1558-6449-4e73-bb00-5ec8a927f015/print/)
has an April 19, 2004 effective date and April 21, 2005 receipt stamp; neither
turns that registration into an activity-period observation.

Senate suffixes cannot be repaired by one global replacement. Six forms show
suffix 113 where the API stores 330, five leave the Senate ID blank, and the
2007H1 AAJ-named cover itself shows 330. Its termination date is filled although
the termination box is unchecked. The 2008 HTML forms also display 330; their
agreement with the API does not independently settle the historical mapping.
Two older activity covers disagree with their API year: `3a8cf433` shows 2004
against API 2003, and `72fc2b87` shows 2005 against API 2004. Preserve the cover
year, checked period, receipt date and API label separately; the receipt date
is not evidence that either year can be silently corrected.

`nvgHistoryReview` in the source JSON records each UUID, original metadata
fingerprint, document/cover hashes, page or HTML-field scope, transcribed
identity/timing fields and disposition. The first-pair House-ID correction is
explicitly logged. This review excludes six incompatible client records from
AAJ attribution but does not assign final spending values to the other fifteen,
establish complete historical coverage, or select comparable controls. Raw
metadata and issue rows remain unchanged. Independent review is still pending.

The opened [House amendment guidance](https://lobbyingdisclosure.house.gov/help/WordDocuments/activityreportamendments.htm)
addresses filing defects and errors or omissions, but its viewed paragraph does
not resolve field inheritance for this 2003 paper record. The linked archived
semiannual form returned 404. Rules for personal financial-disclosure amendments
belong to a different reporting system and have not been imported here.

**Assessment: share with caveats as source-quality findings.** The APGA original
$100,000 remains an original-filing disclosure, not an adjudicated final
organization-period amount. The amendment's nulls remain null; no whole-record
replacement, final spending value, agency exposure or control assignment is
selected. The high-risk gaps are historical packet/field inheritance and API
field fidelity, with independent review still pending. Reproduce the queue with
`python3 scripts/review-substitution-lda-families.py`; the companion notebook
checks its full membership, source fingerprints, flags and no-promotion boundary.

### AAJ 2005H1: an explicit, expense-only amendment resolution

The September 13 UTC review selected the unreviewed pre-reform self-expense pair
for registration `4733-12`, 2005 midyear, before reading its source outcome.
The [original filing](https://lda.gov/filings/public/filing/e8171441-7e83-4c9e-b896-51e57a851cc7/print/)
has 22 PDF pages containing eleven distinct scans, each repeated twice. The
[amendment](https://lda.gov/filings/public/filing/d72204ef-692a-4b5f-a757-b480ccd9c646/print/)
has six pages containing three distinct scans, likewise repeated. All fourteen
distinct images were visually reviewed. A terminal [public API query](https://lda.gov/api/v1/filings/?registrant_id=4733&filing_year=2005&filing_period=mid_year&page_size=100)
returned exactly these two records and matched their frozen metadata. This query
does not establish complete historical aliases or every possible version.

Both covers name Association of Trial Lawyers of America as registrant and
self-client, with Senate ID `4733-12` and House ID `31241000`. Each reports
$4,020,000 of expenses using Method A for January-June 2005. Only the amended
cover checks the amendment box; neither checks No Lobbying Activity or
termination. API expenses match both covers, but API accounting methods remain
null. The review does not fill those nulls or change the raw metadata.

The amendment includes a letter dated August 11, 2005, explaining an omitted TOR
item and explicitly retaining the expense amount:

> the item was included in factoring our expenses shown on page one, so that amount is unchanged.

The letter is on amendment PDF pages 5-6, scan `00000372198`. The replacement
printed page 10, amendment PDF pages 3-4, retains the earlier items and adds
H.AMDT 28 to H.R. 3 concerning rental-car-owner vicarious liability. Its original
counterpart is printed page 10 on original PDF pages 19-20, not the preceding
TOR activity page. The original receipt stamp is August 11 at 1:53 PM; the
amended cover and letter are stamped August 15 at 4:20 PM, with timezone
unstated. Letter dates, receipt stamps and API posting timestamps remain
distinct evidence fields.

The generated `substitution-lda-expense-adjudications.csv` therefore records
**one reported $4,020,000 Method A expense observation for this pair**, supported
by matching covers and the explicit letter. Adding versions would incorrectly
produce $8,040,000. This is neither independently audited expenditure nor an
instruction to split the amount into quarters, add retained-firm income, or
replace the entire eleven-image original with the three-image amendment.

The activity evidence remains a separate, high-risk measurement issue:

| Source field | Downloaded source | API projection | Analytical risk |
| --- | --- | --- | --- |
| Amendment TOR addendum | Revised printed page 10 is present | Zero activity rows | Empty API activities cannot establish no lobbying or deletion of the original issues |
| Original TAX contacts | House only, printed page 7 | House and Senate | Senate exposure cannot be assigned from this API row alone |
| Original INS contacts | House only, printed page 8 | House and Senate | Same unresolved contact discrepancy |

The original has seven issue activity pages: ENG, GOV, HCR, MAR, TAX, INS and
TOR. All seven API descriptions are null. The other five source contact lists
agree with House/Senate API labels at the reviewed scope. Neither the expense
resolution nor that agreement establishes a valid treatment or control group.

**Assessment: share with caveats as a field-specific source adjudication.**
Independent review, complete actor/version histories, compatible spending
definitions, exposure and control selection remain pending. The companion
`notebooks/empirical-expansion-review.ipynb` reproduces the expense row and,
when the ignored raw downloads and Poppler tools are available, checks query/PDF
hashes and all fourteen embedded-image pairs. Those checks authenticate saved
bytes and reproduce transformations; they do not independently verify the
manual source interpretation. No causal effect or model recalibration is cleared.

### Restored registration and incompatible spending measures

`substitution-lda-alias-reviews.csv` admits only client API ID 123312 and
registrant API ID 17831 under `ADVANCED MEDICAL TECHNOLOGY ASSN` in the declared
2003-2008 window. Page 1 of the 2003H1 original report identifies the abbreviated
association name, checks Self, and shows Senate registration 17831-12. The
allowlist restores that registration's fifteen reports, including a 2008Q2
amendment. It does not authorize every `ADVAMED` name match or establish an
exhaustive organizational filing history. Original-form review and API identity
matching do not independently validate the cross-source actor spine.

`substitution-lda-filing-metadata.csv` now preserves one row per filing, including
the separate income and expense amounts in source dollars, API accounting method,
client and registrant IDs, dates, source URLs and a projected-source fingerprint.
There are 267 income reports, 89 expense reports and 71 filings with neither
amount supplied. The successor issue panel leaves these missing amounts blank
instead of converting them to zero; 122 issue rows are affected. Twenty-five
filings contain a source-reported zero. The separate date-review ledger above
identifies one as censored income; the other 24 remain unadjudicated rather than
being declared exact zero spending. Dollar-to-million conversion retains eight
decimal places, without claiming greater precision than the reported source.

Sixty-three of the 89 expense filings have no accounting method in the API.
The separate `substitution-lda-filing-reviews.csv` records two page-1 visual
reviews, preserving the original method without overwriting raw API nulls:

| Filing | Original-form expense amount | Method | Reviewed scope |
| --- | ---: | --- | --- |
| [AdvaMed, 2003H1](https://lda.gov/filings/public/filing/af25ead8-a340-4e1f-826d-ba8ec844f91a/print/) | $2,440,000 | C | Page 1 of 7, identity/amount/method only |
| [AAJ/Association of Trial Lawyers of America, 2003H1](https://lda.gov/filings/public/filing/20c683b7-f75f-46ab-ab43-609699b7c337/print/) | $2,260,000 | A | Page 1 of 28, identity/amount/method only |

Both original amounts agree with the API; both API methods are missing. The
ledger retains PDF hashes, reviewed pages, source fingerprints and reviewer/date.
Neither review establishes amendment-family completeness, and neither method is
carried forward or backward to another filing. Independent review remains pending.

Page 3 of the official [legacy semiannual LD-2 instructions](https://www.senate.gov/reference/resources/pdf/LD2_Instructions.pdf)
was visually reviewed on 2026-09-12. Its Line 13 includes payments to outside
lobbying firms in organizational expenses. The acquired records have 74
actor-period cells containing both income and expense filings, so adding the
two reporting sides is not a valid organizational spending measure. This is an
overlap warning, not a calculation of the exact double-counted amount. The same
instructions distinguish Method A's LDA definitions from Method C's tax-code
definitions; Method C retains grassroots and state lobbying expenses. Thus the
reviewed AdvaMed and AAJ amounts are not interchangeable federal-only outcomes
merely because both were reported through LDA. The legacy instructions' thresholds
and rounding rules describe these historical forms, not today's requirements.
Instruction PDF SHA-256: `534da9b30b4952a7716ee4dbfeae5d0de09b512ff150e4fc61de450cf8bac72b`.

Before estimation, define one spending concept, resolve version families and
unknown methods, and use comparable baseline reporting-method strata. Flag
method changes as measurement breaks rather than selecting controls by their
post-reform reporting behavior. No actor spending totals or valid controls have
been established by this measurement audit.

`substitution-fec-report-panel.csv` contains 229 public reports for four PAC
candidates linked to existing observed LDA actors. The acquisition frame is
explicit in `substitution-fec-acquisition-cohort.csv`; it is an exploratory
name-linked frame, not a preregistered population or a treatment/control cohort.
No candidate was removed because its acquired outcomes were unusable. Twelve
historical affiliation rows cover the 2004, 2006 and 2008 cycles.

| Candidate organization | Committee | Raw reports | Complete half-years / expected |
| --- | --- | ---: | ---: |
| American Benefits Council | C00153171 | 24 | 0 / 12 |
| Advanced Medical Technology Association | C00340356 | 49 | 12 / 12 |
| American Gas Association (GASPAC) | C00007450 | 78 | 12 / 12 |
| American Association for Justice (AAJ PAC) | C00024521 | 78 | 12 / 12 |

The prepared series contains 36 half-years from 152 report versions: 27
pre-event observations, three excluded 2007H2 observations and six 2008
observations. These are pooled counts across three committees, not 27 distinct
time periods for one actor. Here `pre` means before the September 14 enactment
convention, not untreated by every 2007 rule change (see the timing review below).
All 48 expected committee-half-years remain visible
in `substitution-fec-halfyear-coverage.csv`, including the twelve unresolved
Benefits Council periods. A missing committee or period cannot silently drop
out of this denominator. This source-period coverage is not proof that all
historical filings or identities have been captured.

By default, preparation requires affirmative latest/non-amended source flags,
complete date coverage, finite amounts in all three fields, and no unresolved
alternative version. One AAJ period uses the explicit source-bound adjudication
described below. Without that adjudication, the strict source-flag-only result
is 35 complete half-years. Gaps, overlaps, unknown alternatives and reports
crossing half-years are quarantined at the affected half-year, with reasons;
malformed or duplicate source keys and off-frame records abort the build.
Missing outcomes are never filled with zero, and period totals are used rather
than repeatedly summing year-to-date values.

### Historical identity and measure review

The GASPAC historical affiliate is `GAS ASS'N; AMERICAN`. AdvaMed's historical
affiliate is `ADVANCED MECICAL TECHNOLOGY ASSOC`, including that source-native
spelling. The Benefits Council's 2004/2006 affiliate uses its older private
pension and welfare plans name; [October 12, 2000 House hearing testimony,
printed page 19](https://www.govinfo.gov/cgiredirects/getdoc.action?dbname=106_house_hearings&docid=f%3A67812.pdf)
identifies the Council as formerly APPWP. AAJ's 2004 committee name uses
Association of Trial Lawyers of America; [AAJ's organizational history](https://www.justice.org/about-us/aaj-history)
documents the 2006 name change. These sources support organizational continuity,
not a finding that each lobbying principal financed all PAC spending. The
canonical actor spine is not promoted by these candidate links.

Official FEC committee name searches for the remaining observed LDA actors,
American Public Gas Association and American Petroleum Institute, returned no
matches in the bounded search; that is not proof of no PAC or zero spending.
The AAJ search also returned C70003017, classified by the official committee
endpoint as `Communication Cost`. It is a distinct potential channel, not an
additional PAC report series, and is not included in this four-PAC frame.

The legacy CSV name `candidateContributionsDollars` maps to the API's
`fed_candidate_committee_contributions_period`. The reviewed Form 3X line 23
covers contributions to federal candidates/committees **and other political
committees**. It must not be described as candidate-only spending without
recipient-level classification. `independentExpendituresDollars` and
`totalDisbursementsDollars` remain separate fields; the total includes components
and must not be added to them as an independent channel. Two-decimal formatting
preserves API precision but cannot recover cents omitted from API extraction.

### Source-specific version adjudication and remaining discrepancy

The AAJ paper record `file:418573` is API-labeled an amendment with unknown
latest status and missing outcome cells. [Its ten-page PDF](https://docquery.fec.gov/pdf/610/28039940610/28039940610.pdf)
was visually inspected: the December 4, 2008 cover letter supplies Schedule C-1
and loan paperwork alongside the December 3 electronically filed report for
October 16-November 24. The remaining pages contain the loan documents and
receipt envelope, not a replacement Form 3X spending summary. The
[electronic report `file:388257`](https://docquery.fec.gov/pdf/971/28934531971/28934531971.pdf),
pages 1 and 4, confirms the same period, filing date and API totals: line 23
$201,500.00, independent expenditures $66,640.59, and total disbursements
$556,688.99. Only those cover/summary pages of the 667-page electronic report
were reviewed; its itemized transactions have not been independently audited.

`substitution-fec-version-adjudications.csv` retains that decision, both PDF
hashes, reviewed pages, reviewer and date, and fingerprints of both raw records.
Preparation retains the electronic totals, marks the supplement as non-replacing
for this outcome calculation, and explicitly labels AAJ 2008H2
`source_reviewed_supplement`. Neither raw flags nor amounts are overwritten;
new source contents invalidate the adjudication. Unreviewed alternative versions
still block a half-year. Independent review of this decision remains pending.

All 24 Benefits Council reports retain unknown latest flags in the frozen
**reports-endpoint** snapshot, and several outcome cells are missing. The
[2003H1 original scan](https://docquery.fec.gov/pdf/867/23038131867/23038131867.pdf),
pages 1-4, was visually reviewed on 2026-09-12 by Codex. Its page 4 shows line 23
$11,798.21 and total disbursements $11,818.21; the API returns $11,798.00 and
$11,818.00. The independent-expenditure line is blank, not an explicit zero.
PDF SHA-256: `b90c3d8bd069bbf023bafcc0f6b82351b3f0ba9a5bd8b42fba271ec690c1af1b`.
The raw API values remain unchanged and no outcome is promoted.

### Benefits Council: version metadata recovered, financial coverage unresolved

The September 13 UTC follow-up in `substitution-fec-paper-review.json` joins all
24 frozen reports to a separate [committee-only filings inventory](https://api.open.fec.gov/v1/filings/?committee_id=C00153171).
That query exhausted pagination and returned 280 distinct beginning-image IDs.
Six refreshed reports queries, one for each report year 2003-2008, reproduce the
frozen normalized rows except retrieval time. Beginning-image IDs give a
one-to-one join for all 24 reports; committee, file number, type, period, receipt
date and PDF URL also match. The filings endpoint supplies **21 true and three
false** `most_recent` flags where the reports endpoint supplies null. Its
`is_amended` projection is unavailable, so preparation retains the reports
endpoint's separate flag. These are source-version designations, not independent
proof of complete historical filings.

Preparation applies only the recovered `mostRecent` field to in-memory copies,
with review ID `fec-benefits-filings-2026-09-13` in the coverage ledger. Raw flags,
dates and amounts remain untouched. Changed source rows, incomplete joins and
contradictory flags fail validation. This clears the frozen frame's version
obstacle but recovers **zero additional complete half-years**: eleven Benefits
Council periods now report `missing_outcome`; 2006H1 reports `gap_or_overlap`
before the missing-outcome check. It also has missing outcome cells. The usable
series remains 36 of 48 expected committee-half-years.

Seven selected report PDFs and a two-page FEC letter were visually reviewed.
The review is field-specific for four reports; three packets were read page by
page to establish downloaded page inventories, not to audit transactions.

| Source | Reviewed finding | Consequence |
| --- | --- | --- |
| [2006Q1](https://docquery.fec.gov/pdf/147/26039073147/26039073147.pdf), PDF 1, 2 and 4 | Both cover and summary end March 1, not March 31. Line 23 is $3,769.58 and line 31 is $3,778.89; API values are $3,769.00 and $3,778.00. Line 24 is blank. | The March 2-31 gap is source-confirmed, not repaired as an API-only error. Cents and missingness remain separate issues. Itemized activity was not reviewed. |
| [2008Q3 original](https://docquery.fec.gov/pdf/924/28039861924/28039861924.pdf) and [amendment](https://docquery.fec.gov/pdf/804/29030092804/29030092804.pdf), PDF 1 and 4 of each | The original uses Form 3; its $5,000 is line 18 transfers. The amendment uses Form 3X; its $5,000 is line 23 contributions. | Equal amounts do not make the field definitions equivalent. The amended independent-expenditure field remains blank. |
| [2008 post-general original](https://docquery.fec.gov/pdf/791/29039971791/29039971791.pdf), all seven pages | A letter precedes Form 3. No disbursement-summary page occurs in the downloaded packet. The letter reports no candidate/PAC contributions during the period. | A reported no-contribution claim does not verify zero total disbursements or independent expenditures. PDF page 4 is a receipts summary. |
| [2008 post-general amendment](https://docquery.fec.gov/pdf/796/29030092796/29030092796.pdf), PDF 1 and 4 | Form 3X period lines 23, 24 and 31 are blank; line 23's $16,721.22 is in year-to-date column B. | Do not turn blanks into zeros or carry year-to-date values into period spending. |
| [2008 year-end original](https://docquery.fec.gov/pdf/277/29039981277/29039981277.pdf), all five pages, and [amendment](https://docquery.fec.gov/pdf/814/29030092814/29030092814.pdf), all seven pages | Neither downloaded packet has a disbursement-summary page. PDF page 4 in each is Schedule A. The amendment's page-2 period disbursements cell is blank despite cash arithmetic implying no reduction. | These are packet-specific missing-page observations, not proof of which pages were originally filed or that all period outcomes are zero. |

The [May 15, 2009 FEC letter](https://docquery.fec.gov/pdf/629/29030090629/29030090629.pdf),
both pages reviewed, references all three late-2008 periods and requests Form
3X. All three originals visibly use Form 3 although the filings API classifies
them as F3X. Their May 26, 2009 amendments use Form 3X. The three false latest
flags belong to those originals. Negative `previous_file_number` values are
preserved, not joined to null original file numbers. The letter is a request
for information, not an enforcement outcome; copies are not independent events.

**Assessment: share with caveats for source reconciliation; not usable as an
expanded financial panel.** The [FEC's data guidance](https://www.fec.gov/data/browse-data/)
gives paper filings precedence over discrepant data entry. The ledger separates
native forms, printed lines, columns, actual PDF pages, hashes and transcriptions.
Acquisition hashes refer to minimum metadata projections, not raw HTTP bodies;
optional-field projections can collapse absent keys and null. Offline checks
reproduce the join and coverage. The companion notebook checks available ignored
acquisition/PDF files, reporting unavailable files as checks not run. Neither
byte checks nor API agreement independently validates manual reading. Independent
review, missing financial evidence, historical completeness and a comparable
treatment/control design remain open.

## Revised design contract

1. **Define provision-level exposure first.** Identify a specific reform
   provision and measure exposure using pre-reform institutional records. No
   actor is treated merely because it appears in federal LDA. Do not select
   controls using post-reform survival or observed spending changes. If credible
   differential exposure cannot be documented, HLOGA remains a descriptive study.
   For travel, assess the earlier scrutiny/adaptation period described below;
   being before the legal effective date does not establish an unaffected baseline.
2. **Use comparable controls.** Draw potential controls from the same federal
   LDA source, reporting regime, pre-period, and organization/issue strata. Match
   or weight using pre-event size, trends, issue mix and organizational features;
   inspect overlap and spillovers. Colorado income is a separate outcome system
   and will not serve as the untreated outcome in this design.
3. **Keep native time resolution.** Start with half-years for both LDA and FEC,
   aggregating complete 2008 quarterly/monthly reports upward. Seek at least four
   years of genuinely observed pre-period history and multiple pre-event placebo
   windows. The new 2003-2007H1 acquisition meets an eight-half-year source-depth
   target for all six API-attributed LDA candidates and three PAC series after the scoped
   AdvaMed alias restoration. This does not establish comparable controls, complete
   historical identity coverage, or a causal design. Treat the reform-straddling
   half-year separately.
4. **Observe both channels for each actor.** Verify historical PAC/organization
   links and collect the same outcomes for comparison actors. Report changes in
   LDA activity and PAC Form 3X line 23 contributions separately. A decline in one
   alone is not substitution; neither amount measures hidden influence.
   LD-203 cannot supply a pre-HLOGA contributions baseline: the official LDA
   public portal dates its first required filing to July 2008.
5. **Separate source validity from statistical results.** Validate filing
   versions, coverage and units before fitting anything. Predeclare the contrast,
   treatment timing, exclusions, placebo windows, clustering and sensitivity
   analysis. An interval containing zero is a valid possible result, not an
   automatic identification failure. Balance and plausible parallel trends are
   necessary diagnostics, not proof of a causal design.
6. **Conclude within identified scope.** Produce estimates only if the exposure,
   comparison, temporal and linkage evidence supports them. Otherwise document
   which contrasts remain unidentified and why. A negative identification result
   must distinguish unavailable evidence from observed null effects.

The official reporting-start source is https://lda.gov/system/public/. Committee
history can be inspected at https://www.fec.gov/data/committee/C00007450/?cycle=2006;
individual report URLs and amendment metadata are retained in the source panel.

## Provision-level identification review

The [enacted HLOGA text](https://www.govinfo.gov/content/pkg/PLAW-110publ81/html/PLAW-110publ81.htm)
separates provisions and dates. Section 201 changes semiannual reporting to
quarterly reporting. Section 215 applies the relevant Title II reporting changes
to registrations and reporting periods beginning January 1, 2008, subject to
its listed exceptions. Section 206's knowing provision of impermissible gifts
or travel takes effect at enactment. Section 207 changes coalition/association
disclosure based on funding and participation conditions, with specified
website-disclosure qualifications. Those provisions cannot share an
automatically assigned treatment rule just because they belong to one Act.

Our current design assessment is:

| Candidate contrast | What the present data can establish | Why an effect remains unidentified |
| --- | --- | --- |
| Quarterly-reporting reform | Native LDA periods before and after the reporting change | No verified unexposed group within the same reporting system; raw filing counts change mechanically with reporting frequency |
| Gift/travel restriction exposure | Names and filing histories of candidate organizations | No pre-reform gift/travel reliance or provision-specific coverage coding; PAC spending is not a gift/travel baseline |
| Coalition-disclosure exposure | Some actors have association names | Names do not establish qualifying funding, active participation, or prior disclosure status; pre-reform exposure and comparable controls are absent |

These are negative identification findings for the current evidence, not
findings that the reforms had no effect. The 2007H2 exclusion in the prepared
PAC series is an enactment/anticipation-window convention, not a verified
common implementation date. Keep it separate until a specific provision and
comparison design are selected. Next acquisition should prioritize pre-reform
exposure records and matched actors' alternate-channel outcomes; adding filing
rows alone cannot resolve these identification failures.

### House travel exposure: earlier timing and an unverified baseline

The [January 4, 2007 Congressional Record, page H7](https://www.govinfo.gov/content/pkg/CREC-2007-01-04/pdf/CREC-2007-01-04-pt1-PgH6-9.pdf)
sets out a March 1, 2007 effective date for the House travel restrictions and
advance-approval requirements, including an exception for colleges/universities
and limited one-day travel for entities employing lobbyists. Page H7 was
visually reviewed. The [2008 House Ethics Manual](https://ethics.house.gov/sites/ethics.house.gov/files/documents/2008_House_Ethics_Manual.pdf)
also dates the travel guidelines' implementation to March 1. Thus 2007H1 is
**not an untreated half-year for a House travel-reform contrast**. The existing
September-enactment event labels are retained solely as a descriptive convention;
they must be rebuilt for any selected provision and chamber.

A [July 3, 2014 Ethics Committee disclosure statement](https://ethics.house.gov/press-releases/statement-chairman-and-ranking-member-committee-ethics-regarding-disclosure-privately/)
describes bulk post-travel reports going back to 2007. It also explains that
annual financial disclosures neither report travel dollar values nor cover most
House staff. That is a historical description, not a verified inventory of all
archives accessible today. No 2003-2006 sponsor/trip baseline has been acquired
here. Annual financial disclosures cannot simply replace the detailed trip
series as an equivalent outcome. Colleges/universities are an institutionally
different potential comparison group, not automatically comparable untreated
controls. Before pursuing this contrast, establish historical travel coverage,
sponsor identities and pre-reform trip reliance, then assess overlap within a
defensible organization/issue frame. The present PAC series cannot supply that
missing exposure measure.

### Located pre-reform travel records, originals login-gated

A September 12 public-source follow-up located a concrete pre-2007 archive.
[LegiStorm's collection description](https://www.legistorm.com/trip/about.html)
states that its travel records begin in 2000 and derive from filed disclosures.
Its [FAQ](https://www.legistorm.com/trip/faq.html) describes a privately financed
travel collection, not all congressional travel. Neither statement independently
establishes complete sponsor-year coverage or validates a zero-exposure control.

The public [March 2004 AdvaMed trip group](https://www.legistorm.com/trip/group/2528.html)
lists fourteen travelers to Scottsdale, including House and Senate personnel.
Individual start/end dates differ. These are clustered trips for one sponsored
event, not fourteen independent reform exposures. Two public details were checked:

| Archive trip | Chamber indicated by approver | Listed dates | Original disclosure access |
| --- | --- | --- | --- |
| [17561, Alan Eisenberg](https://www.legistorm.com/trip/17561.html) | House, Jim Greenwood | March 4-7, 2004 | [Original-form link](https://www.legistorm.com/pdf/trip_17561.pdf) returned login page |
| [12536, Aaron Cohen](https://www.legistorm.com/trip/12536.html) | Senate, John Ensign | March 4-7, 2004 | [Original-form link](https://www.legistorm.com/pdf/trip_12536.pdf) returned login page |

No account was created, no terms accepted, and no original travel forms were
read. These remain archive-summary leads, not a promoted exposure panel. The
earlier baseline gap means no verified baseline has been acquired in this
workspace, not that historical records do not exist. Obtain authorized original
forms, resolve historical sponsor identity, document coverage across 2003-2006,
and recruit comparable sponsors using pre-reform characteristics. Keep chamber
timing and shared event identities explicit. Do not infer that the House reform
also supplies an untreated Senate control or assign treatment from one located
trip. User provision of the two original disclosures has been requested.

### Historical publisher records: measurement and earlier-change risks

A September 13 UTC follow-up reviewed the original data publishers' descriptions,
not a recovered trip-level dataset. CPI's [Power Trips methodology](https://publicintegrity.org/politics/methodology-the-team-for-power-trips/)
describes trip starts from January 1, 2000 through June 30, 2005. It warns that
disclosure and collection problems make its totals conservative. It also records
setting foreign-currency totals to zero, assigning some incomplete dates to a
year, and leaving most conflicting sponsorships and proportional co-sponsor
allocations unresolved. Thus a recovered numeric zero would need its original
currency and coding history checked; date precision and sponsor shares cannot
be assumed. These are publisher-described operations, not independently measured
error rates in a dataset acquired here.

The publishers also report changes before the 2007 House restriction:

| Publisher and observation window | Published observation | Design implication |
| --- | --- | --- |
| [CPI, January 3, 2007 article](https://publicintegrity.org/politics/with-change-on-the-horizon-privately-funded-travel-plummets/), July 2005-June 2006 versus the preceding year | Roughly 2,700 versus 4,700 trips; over $5.4 million versus over $10.3 million | A pre-2007 decline is already reported. These rounded aggregates are not an actor/chamber panel or an estimated reform effect. |
| [American RadioWorks, Chilled Travel](https://americanradioworks.publicradio.org/features/chilledtravel/), July 2004-June 2005 versus the preceding year | A reported 20 percent decline in members' privately paid trips | The risk extends earlier than 2006. This is a member-focused series, not a replication of CPI's member-and-staff comparison. |

The CPI article's June 12, 2006 related-story box is not its publication date.
Its own byline dates the article January 3, 2007. Neither publisher's comparison
identifies a common anticipation date, differential trends between our candidate
actors, or whether scrutiny caused the decline. Their findings motivate checking
those possibilities, not mechanically deleting every 2004-2006 observation.
Do not splice these aggregate series or use them as LDA/PAC outcomes.

[American RadioWorks' data overview](https://americanradioworks.publicradio.org/features/congtravel/data.html)
specifies members only, January 2000 through mid-November 2005, with incomplete
records reflecting incomplete or illegible disclosures. That scope excludes
staff and ends before the required 2006 baseline coverage. Its linked member,
top-sponsor and expensive-trip pages returned HTTP 403 through the web reader.
CPI's linked `projects.publicintegrity.org` database hostname failed local DNS
resolution. A bounded Internet Archive index request timed out without a response.
These access observations do not establish that the data are lost or that no
authorized archive is available. No travel rows or original forms were acquired.

**Next acquisition and comparison requirements.** Seek a recoverable trip-level
corpus and originals spanning the intended pre-period, with traveler/chamber,
historical sponsor, shared event, currency, date precision and amendment fields.
Evaluate coverage by sponsor, chamber and period before coding nonappearance as
zero. Preserve both member-only and member-plus-staff definitions when bridging
sources. Check earlier changes and election-cycle composition with matched
actors' observed LDA and PAC outcomes; choose exposure and comparison rules
without conditioning on their subsequent spending. Extending history alone
does not establish unaffected controls. No exposure assignment or causal estimate
is cleared by this publisher review; independent review remains pending.

## Reproduce acquisition and preparation

These networked acquisition commands use local keys without saving them:

```sh
. ./scripts/load-env.sh
python3 scripts/build-substitution-historical-lda-panel.py \
  --years 2003 2004 2005 2006 2007 2008 --max-actors 8 --design-candidate \
  --review-date 2026-09-12 \
  --alias-reviews data/calibration/first-wave/substitution-lda-alias-reviews.csv \
  --metadata-output data/calibration/first-wave/substitution-lda-filing-metadata.csv \
  --response-cache out/substitution-lda-response-cache \
  --output data/calibration/first-wave/substitution-expanded-lda-panel.csv
python3 scripts/fetch-substitution-fec-reports.py
```

`make empirical-expansion-audit` prepares and checks the committed snapshots
offline. It does not overwrite the original diagnostic or clear causal gates.
The fetcher's default is the committed four-PAC acquisition cohort. Both report
and affiliation outputs are written only after the whole acquisition succeeds.
For a single-committee exploratory fetch, provide both `--committee-id` and
`--canonical-actor-id`, and use separate `--output` and `--history-output` paths
to avoid replacing the cohort snapshots. Version adjudications are not generated
by the fetcher; they require review of the original source documents.

The acquisition is bounded to an existing canonical-actor list and four PACs;
it is not a representative population sample or a finished control cohort.

`notebooks/empirical-expansion-review.ipynb` is an offline companion to the
source audit. Its structure was validated with `nbformat`, and its code cells
passed top-to-bottom execution in a fresh Jupyter kernel using an isolated,
temporary dependency environment. Executed outputs are saved in the notebook.
The analysis uses only the Python standard library and the checked-in scripts;
Jupyter is needed only to run or view the notebook interface.
