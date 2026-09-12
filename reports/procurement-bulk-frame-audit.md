# Archived procurement bulk frame audit

## Dataset and checks

Archived bulk manifest created: 2026-06-13T08:06:00Z. Grain: archived prime transaction CSV rows, not distinct awards.
Exactly 56 manifest-selected ZIPs were scanned with matching SHA-256 and row counts; subaward files and superseded downloads were excluded.
The manifest covers each declared agency on all 366 inclusive FY2024 days, without gaps or overlaps.
All 13 source columns were checked, with date/agency containment, missingness, award descriptions, competition and exact-decimal obligation summaries.
Default report reproduction checks the committed profile, not the ignored raw archives; use --scan to repeat the raw audit.

## Findings

| Measure | Archived rows | Share of all rows |
| --- | ---: | ---: |
| rows | 6,449,101 | 100.00% |
| childDescriptionRows | 6,205,401 | 96.22% |
| blankAwardTypeRows | 243,700 | 3.78% |
| otherAwardTypeRows | 0 | 0.00% |
| afterExclusionCompetitionRows | 665,137 | 10.31% |
| missingOffersRows | 4,505,798 | 69.87% |
| zeroOffersRows | 351 | 0.01% |
| missingModificationRows | 0 | 0.00% |
| outsideDateRows | 0 | 0.00% |
| wrongAgencyRows | 0 | 0.00% |

| Raw award description | Rows | Net obligation, dollars |
| --- | ---: | ---: |
| (blank, unresolved type) | 243,700 | 14871775716.42 |
| BPA CALL | 868,765 | 21656731510.96 |
| DEFINITIVE CONTRACT | 141,449 | 259176757978.89 |
| DELIVERY ORDER | 4,447,816 | 391858099401.25 |
| PURCHASE ORDER | 747,371 | 16774074977.74 |

| Obligation sign | Rows |
| --- | ---: |
| negative | 224,248 |
| positive | 5,639,986 |
| zero | 584,867 |

## Count/export discrepancies

| Agency | Window | Planned | Exported | Difference |
| --- | --- | ---: | ---: | ---: |
| Department of Agriculture | 2024-07-01 to 2024-09-30 | 34678 | 34657 | -21 |
| Department of Defense | 2024-05-01 to 2024-05-31 | 387460 | 387459 | -1 |

## Interpretation, severity and remaining requirements

- High, confirmed measurement risk: the collector requests A/B/C/D and IDV types. Blank raw award types become the legacy label `contract`; that label does not establish a child-action type. Do not classify every blank as an IDV. Reconcile A/B/C/D and vehicle records separately using native type codes.
- High, confirmed semantic risk: the legacy bulk `exclusionFlag` tests whether competition text contains `exclusion`. It is not historical SAM vendor exclusion/debarment evidence. The [FPDS competition definition](https://www.fpds.gov/help/Extent_Competed.htm) identifies this as a competition procedure. It does not establish misconduct.
- High, confirmed missingness risk: missing offers become zero in the legacy normalizer, but source blanks are not observed zero offers. No blank modification numbers were found in this scan, although the legacy normalizer also defaults those to `0`. Protest and firewall flags default to false without an observed overlay; they cannot establish absence.
- High linkage limitation: the archived columns omit unique source transaction IDs, numeric awarding/parent subtier codes and native IDV type codes. Parent PIID is present raw but omitted from normalized rows. Row count agreement does not prove unique actions or a complete census; action-level uniqueness has not been tested without full keys.
- Medium, confirmed count discrepancy but unknown cause: two count/export differences were accepted under a live tolerance. No count-time membership list is available here, so source revisions, omitted records and other causes are not adjudicated. Do not describe the difference as identified missing transactions.
- Signed net obligations are $704337439585.26; absolute obligations are $774172847532.38. These are different summaries. Zero and negative actions remain in the denominator.
- This audit validates archived-file consistency and reveals comparison limits. It does not obtain a SAM export, independently verify source-system completeness, measure protest/exclusion rates, or identify capture effects.

## Validation assessment

Share with caveats as an archived-data quality report, not an estimation panel. The standalone notebook reproduces profile joins and totals; unit tests exercise malformed records, manifest gaps/overlaps, archive selection, source nulls, signed cents and stale evidence. See the reconciliation note for the separately verified blank-type IDV example and remaining acquisition requirements.
