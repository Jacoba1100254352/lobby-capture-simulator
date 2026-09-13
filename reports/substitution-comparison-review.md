# Substitution comparison: negative identification result

**Assessment: usable for documenting why the current study cannot estimate a causal substitution effect.** No new effect is fitted. Missing exposure and comparison evidence is not evidence of a zero effect.

## What the expanded records actually pair

The observed LDA source frame contains 6 API-attributed candidates across 72 actor-half-years in 2003-2008. This is the frame of actors with returned source rows, not the full acquisition-query frame, a population sample or a validated control cohort. Registrations are excluded. A complete native-period footprint means at least one activity filing is present for each expected reporting period; it does not certify exhaustive filings, final amendments, identity or comparable spending.

The 4-PAC acquisition frame retains 48 expected periods: 36 with usable prepared outcomes and 12 unresolved. Another 24 actor-half-years are outside that PAC cohort. There are 36 same-candidate periods with both an LDA filing and a PAC outcome. They are source overlaps, not independent observations or validated two-channel causal outcomes.

| API-attributed candidate | LDA half-years with full native-period footprint | PAC usable / expected | PAC acquisition status | Missing API expense methods / expense records |
|---|---:|---:|---|---:|
| AMERICAN PUBLIC GAS ASSOCIATION | 12 / 12 | not acquired | outside this PAC cohort | 10 / 15 |
| AMERICAN BENEFITS COUNCIL | 12 / 12 | 0 / 12 | retained, including unresolved periods | 9 / 13 |
| ADVANCED MEDICAL TECHNOLOGY ASSOCIATION | 12 / 12 | 12 / 12 | retained, including unresolved periods | 10 / 15 |
| American Petroleum Institute | 12 / 12 | not acquired | outside this PAC cohort | 11 / 15 |
| AMERICAN GAS ASSOCIATION | 12 / 12 | 12 / 12 | retained, including unresolved periods | 12 / 16 |
| AMERICAN ASSOCIATION FOR JUSTICE | 12 / 12 | 12 / 12 | retained, including unresolved periods | 11 / 15 |

The [availability CSV](substitution-comparison-availability.csv) preserves filing IDs, native-period counts, separate income/expense record counts, PAC evidence IDs and observed PAC amounts. Unknown or unacquired PAC amounts stay blank; an observed zero stays zero. API accounting-method missingness remains visible even where a separate source review has recovered a method. The earlier ledgers remain authoritative for those readings. No LDA monetary total or spending ratio is constructed.

## Why the legacy control comparison cannot separate a source change

On the legacy panel's 231 included actor-quarters (33 actors; 66 nominal pre and 165 post observations), the diagnostic basis `[1, treated, post, treated*post, federal_source*post]` has exact rank 4 of 5. The two interaction columns are identical: `true`. Increasing the treatment coefficient by one and decreasing the source-specific post coefficient by one changes fitted predictions by at most 0.

This is an algebraic non-identification result for an augmented model allowing an unrestricted federal-source post change. It does not show that such a shock actually occurred or that every difference-in-differences design with different sources is invalid. An estimate would require additional credible restrictions or comparison evidence that distinguishes the reform from source/jurisdiction-specific changes. The current federal amounts and Colorado income records also have different measurement definitions. The old descriptive estimate and its bootstrap interval remain unchanged; an interval crossing zero is not itself an identification failure. No causal coefficient or null-effect test follows from this rank check.

## Provision-specific conclusions

| Proposed contrast | Present failure | Evidence needed to reopen estimation |
|---|---|---|
| Quarterly reporting | No verified unexposed group in the same reporting system; filing frequency changes mechanically. | A comparable outcome and credible comparison or other design separating reporting changes from behavior. |
| Gift/travel restrictions | No pre-reform reliance or provision-specific exposure assignment; earlier scrutiny may contaminate nominal pre periods. | Dated pre-reform reliance, applicable timing, comparable actors, and both channels observed for both groups. |
| Coalition disclosure | Names, membership websites and empty affiliate arrays do not establish qualifying funding, participation or prior disclosure. | Pre-reform funding/participation and disclosure evidence, with comparably measured lower-exposure controls. |

The [enacted HLOGA, sections 201 and 215](https://www.govinfo.gov/content/pkg/PLAW-110publ81/html/PLAW-110publ81.htm) sets quarterly reporting from January 2008; sections 206 and 207 require separate provision-specific treatment definitions. The prepared PAC series' 2007H2 exclusion is an enactment/anticipation convention, not a verified common implementation date. Nine nominal pre-enactment half-years do not certify an unaffected baseline. Splitting semiannual observations into quarters adds no independent history.

## Decision and stopping rule for this evidence freeze

Do not fit a successor causal model from these products. Reopen that decision when dated pre-reform exposure and a defensible comparison are supplied, then resolve source versions, comparable accounting scope, actor/PAC links and common period coverage before estimation. Additional filing rows alone do not clear the design. A reform-induced change in two separately measured channels would still require interpretation before calling it substitution; an elasticity additionally needs a defined response to a measured cost or constraint change. PAC contributions and lobbying expense are not exhaustive measures of influence or hidden-channel spending.

This closes the inference decision for the present substitution freeze with a documented negative result. It does not close the full empirical goal, obtain a representative SAM export, resolve procurement links, or independently adjudicate comment coding. The detailed [redesign and source reviews](../docs/substitution-study-redesign.md) retain the evidence and acquisition limits.

Reproduce with `make empirical-expansion-audit` and the companion `notebooks/empirical-expansion-review.ipynb`. The [machine-readable review](substitution-comparison-review.json) fingerprints parsed input tables in stored row order. These hashes identify the checked products; they do not authenticate upstream raw responses or independently validate source readings.
