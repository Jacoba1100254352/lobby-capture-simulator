# Substitution study redesign

Updated 2026-09-12. Status: expanded sources, identification unresolved.

## New evidence and its limits

`substitution-expanded-lda-panel.csv` contains 1,119 issue rows, 427 filing UUIDs
and six candidate actors over 2003-2008. The acquisition queried eight
canonical actors; two had no exact-name rows. A reviewed, registration-specific
AdvaMed name variant restores fifteen filings omitted by the earlier exact-name
query, retaining all 412 previously acquired filings. All six observed actors now
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
covered periods; their original scans remain unreviewed. Filing-level amounts
are repeated on issue rows, not allocated across issues. Any monetary total
must first collapse to verified unique filings and resolve amendments; summing
issue rows would multiply the same amount. The source collector fails closed
on request errors, malformed responses, incomplete result counts, duplicate query
UUIDs and pagination truncation. The entire 2003-2008 acquisition was rerun
successfully under those rules. A same-UTC-day public-response cache supports
resumption without refetching successful pages; cache URL, date and content
hashes are checked. Authentication and quota errors are not automatically retried.

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
filings contain a source-reported zero, which remains unadjudicated rather than
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

All 24 Benefits Council reports have unknown latest flags, and several outcome
cells are missing. The [2003H1 original scan](https://docquery.fec.gov/pdf/867/23038131867/23038131867.pdf),
pages 1-4, was visually reviewed on 2026-09-12 by Codex. Its page 4 shows line 23
$11,798.21 and total disbursements $11,818.21; the API returns $11,798.00 and
$11,818.00. The independent-expenditure line is blank, not an explicit zero.
PDF SHA-256: `b90c3d8bd069bbf023bafcc0f6b82351b3f0ba9a5bd8b42fba271ec690c1af1b`.
The raw API values remain unchanged and no outcome is promoted. The 2006Q1 API
coverage also ends March 1 before an April 1 next-period start; that original
filing still needs review. Resolving version flags alone would not resolve
these amount, missingness and date issues.

## Revised design contract

1. **Define provision-level exposure first.** Identify a specific reform
   provision and measure exposure using pre-reform institutional records. No
   actor is treated merely because it appears in federal LDA. Do not select
   controls using post-reform survival or observed spending changes. If credible
   differential exposure cannot be documented, HLOGA remains a descriptive study.
2. **Use comparable controls.** Draw potential controls from the same federal
   LDA source, reporting regime, pre-period, and organization/issue strata. Match
   or weight using pre-event size, trends, issue mix and organizational features;
   inspect overlap and spillovers. Colorado income is a separate outcome system
   and will not serve as the untreated outcome in this design.
3. **Keep native time resolution.** Start with half-years for both LDA and FEC,
   aggregating complete 2008 quarterly/monthly reports upward. Seek at least four
   years of genuinely observed pre-period history and multiple pre-event placebo
   windows. The new 2003-2007H1 acquisition meets an eight-half-year source-depth
   target for all six observed LDA actors and three PAC series after the scoped
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
