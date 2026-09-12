# Empirical expansion evidence audit

Current committed source products; no causal-calibration promotion.

## expanded-lda-history

Status: `source_only`

issueRows=1060; filingUUIDs=412; actors=6; years=2003,2004,2005,2006,2007,2008; observedPrePeriodsByActor=cand-372cc95f9387:9;cand-5d1da86118e5:9;cand-9948f2974958:6;cand-b905d6833296:9;cand-d5522e62fad7:9;cand-f7178708cc78:9

Remaining: Validate amendments and exact actor identities; pre-period counts are native reporting periods, not independent quarters or proof of completeness.

## lda-posting-date-anomaly

Status: `review_required`

postingBeforeCoveredPeriod=3; filingUUIDs=9bd361f7-98e7-46a9-90cd-267ace5ca84c;a93a23e5-9da2-4c18-8625-b41fc0987d06;bcb55688-3d56-4c98-a546-0730eb923bfa

Remaining: Review original filings and resolve API/scanned-form disagreements. One 2004 scan is reviewed in the redesign note; its amount is below-threshold, not an observed zero. Do not order amendments or treatment timing solely by dtPosted.

## alternate-channel-reports

Status: `bounded_affiliation_candidate`

reportRows=78; committees=1; affiliationCycles=2004,2006,2008; overlappingPeriods=6; gapsBetweenReports=0; halfYearStraddlingReports=0; missingOutcomeCells=3

Remaining: Review historical sponsor links and report amendments; obtain transaction dates for straddling periods; one PAC cannot supply treatment-control identification.

## alternate-channel-halfyears

Status: `observed_outcome_not_effect`

completeHalfYears=12; includedReportVersions=72; eventClasses={'pre': 9, 'straddles_event_excluded': 1, 'post': 2}

Remaining: Source-marked latest, non-amended reports only; compare with native LDA periods after actor linkage and exposure validation, without interpreting the excluded event half-year.

## comment-corpus

Status: `source_refreshed`

rows=500; uniqueBodies=145; emptyBodies=0

Remaining: Verify receipt dates separately from posting dates and sample coverage before calculating docket-level rates.

## comment-uptake-pilot

Status: `issue_level_only`

observations=2; individualCommentLinks=0; changes={'removed_ground': 1, 'retained_ground': 1}

Remaining: Retrieve full response document, link actual comments and complete independent coding review; do not compute an uptake rate from this purposive pilot.

## gao-partial-adjudication

Status: `not_award_linked`

rows=17; partiallyReviewed=1; verifiedDecisionDates=1

Remaining: Link decision-body dates and awarded PIID/UEI; a solicitation number is not a verified award key. No-match is not no-protest.

## overall

Status: `not_identified`

New source history, PAC outcomes and issue-level comment coding exist; no provision-exposure control design, representative SAM export or historical exclusion overlay has cleared.

Remaining: Continue all three tracks. These findings are an interim source/design audit, not completion of the active empirical goal.
