# Substitution study redesign

Updated 2026-09-12. Status: expanded sources, identification unresolved.

## New evidence and its limits

`substitution-expanded-lda-panel.csv` contains 1,060 issue rows, 412 filing UUIDs
and six exact-name-linked actors over 2003-2008. The acquisition queried eight
canonical actors; two had no exact-name rows. Five observed actors have nine
distinct pre-event reporting periods after excluding registration forms; one has
six. These are chiefly semiannual periods, not independent quarters. A split of
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

Two additional 2003 filing UUIDs, `9bd361f7-98e7-46a9-90cd-267ace5ca84c` and
`bcb55688-3d56-4c98-a546-0730eb923bfa`, also have posting dates before their
covered periods; their original scans remain unreviewed. Filing-level amounts
are repeated on issue rows, not allocated across issues. Any monetary total
must first collapse to verified unique filings and resolve amendments; summing
issue rows would multiply the same amount. The source collector now fails
closed on request errors or pagination truncation. The entire 2003-2008
acquisition was rerun successfully under that rule.

`substitution-fec-report-panel.csv` contains 78 public reports from committee
C00007450, GASPAC. Historical FEC records for 2004, 2006 and 2008 identify a trade
association PAC and the affiliated name `GAS ASS'N; AMERICAN`. This supports a
candidate link to the American Gas Association, not a finding that all PAC
spending was financed by that lobbying principal. The canonical actor spine is
not promoted by this candidate link.

Six superseded/unknown report versions are retained in the acquisition file but
excluded from the prepared outcome. The 72 source-marked latest, non-amended
reports form twelve complete half-years: nine pre-event, the straddling 2007H2
excluded from contrasts, and two post-event. There are no date gaps or overlaps
in that selected series. Amounts retain cents; missing values are not zeros;
period totals are used instead of repeatedly summing year-to-date values.
Candidate contributions, independent expenditures, and total disbursements
are separate fields and must not be summed together as independent channels.

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
   target for five LDA actors and the single PAC series, but not the sixth
   observed LDA actor. This does not establish comparable controls, complete
   historical identity coverage, or a causal design. Treat the reform-straddling
   half-year separately.
4. **Observe both channels for each actor.** Verify historical PAC/organization
   links and collect the same outcomes for comparison actors. Report changes in
   LDA activity and PAC candidate contributions separately. A decline in one
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

## Reproduce acquisition and preparation

These networked acquisition commands use local keys without saving them:

```sh
. ./scripts/load-env.sh
python3 scripts/build-substitution-historical-lda-panel.py \
  --years 2003 2004 2005 2006 2007 2008 --max-actors 8 --design-candidate \
  --review-date 2026-09-12 \
  --output data/calibration/first-wave/substitution-expanded-lda-panel.csv
python3 scripts/fetch-substitution-fec-reports.py
```

`make empirical-expansion-audit` prepares and checks the committed snapshots
offline. It does not overwrite the original diagnostic or clear causal gates.
The acquisition is bounded to an existing canonical-actor list and one PAC;
it is not a representative population sample or a finished control cohort.

`notebooks/empirical-expansion-review.ipynb` is an offline companion to the
source audit. Its structure was validated with `nbformat`, and both code cells
passed top-to-bottom execution in a fresh Jupyter kernel using an isolated,
temporary dependency environment. Executed outputs are saved in the notebook.
The analysis uses only the Python standard library and the checked-in scripts;
Jupyter is needed only to run or view the notebook interface.
