# Comment-uptake pilot: Utah regional haze

Source review: 2026-09-12. Unit: docket-issue, not individual comment.

## Verified observations

The two observations in `data/calibration/first-wave/comment-uptake-issue-pilot.csv`
come from the published final rule, 89 FR 95117, document 2024-27941. Page 95119
was checked visually against the official PDF as well as its text. The CSV
records the PDF's SHA-256, page, source URL, coding date, and reviewer.

- **Intermountain:** the agency explicitly connects consideration of comments
  with removal of one proposed ground for disapproval. This is a change in
  the agency's rationale, not proof of a change to codified text or a measured
  effect of any particular comment.
- **CCI Paradox Lisbon:** the agency acknowledges Utah's comment conceding an
  emissions-calculation error but retains the disapproval ground. A substantive
  response and a favorable outcome are therefore separate variables.

These are purposively selected pilot cases from one rule, not a denominator
for an uptake rate. Independent review is pending. Neither observation is
assigned to any of the 500 sampled public comments.

## Source and access boundaries

- Final rule: https://www.govinfo.gov/content/pkg/FR-2024-12-02/pdf/2024-27941.pdf
- Searchable official text: https://www.govinfo.gov/content/pkg/FR-2024-12-02/html/2024-27941.htm
- Full response document: https://www.regulations.gov/document/EPA-R08-OAR-2024-0389-5687

The Regulations.gov API and public document page identify the full response
document and its publication date, but the PDF download returned HTTP 403 in
this run. Sections 5.F.i, 4.B, and 11 in the pilot are references made by the
final rule; they must not be described as independently read response sections.
The actual comment IDs, response arguments, and any proposed-to-final codified
text movement remain to be adjudicated from those primary materials.

A September 12 follow-up verified the public document-details page in the
browser, including the November 23, 2024 received date and December 2 posting
date. The download actions did not yield a verifiable local PDF, and opening
the linked PDF for reading returned a browser client-blocking error. No response
sections were read through that route, and no pilot coding was promoted.

The final rule states that comments closed on 2024-09-18. The sampled corpus
contains later *posting* dates. Posting is not submission/receipt: do not mark
those comments late without receipt-date evidence.

## Candidate submissions located

A bounded public API keyword search for `Intermountain` returned 17 comments.
Detail requests with `include=attachments` identified the following relevant
submission metadata on 2026-09-12. These are title-based review candidates, not
adjudicated links from particular arguments to agency responses.

| Comment ID suffix | Public submitter title | Received date | Posted date | Public attachment metadata |
| --- | --- | --- | --- | --- |
| 5126 | Intermountain Power Agency and Intermountain Power Service Corporation | 2024-09-18 | 2024-10-09 | Main comments and a March 7, 2024 EPA response-letter exhibit |
| 5143 | Utah Division of Air Quality | 2024-09-18 | 2024-10-09 | DAQP-080-24 |
| 5538 | Utah Division of Air Quality | 2024-08-29 | 2024-10-09 | DAQ-074-24 |

Each suffix follows `EPA-R08-OAR-2024-0389-`. Inspect the public records:
[Intermountain](https://www.regulations.gov/comment/EPA-R08-OAR-2024-0389-5126),
[Utah September submission](https://www.regulations.gov/comment/EPA-R08-OAR-2024-0389-5143),
and [Utah August submission](https://www.regulations.gov/comment/EPA-R08-OAR-2024-0389-5538).
All three bodies refer readers to attachments. The Intermountain main attachment
and August Utah attachment returned HTTP 403; the September attachment was
identified but not downloaded. None has been read. The API provides receipt and
posting as separate fields, confirming that these October postings do not by
themselves establish late receipt. The precise deadline/time-zone eligibility
rule and attachment contents still need review.

These candidates do not change the two pilot rows' blank individual-comment
IDs. A submitter title alone cannot distinguish which Utah submission, argument,
or supplement the agency addressed, and none may be attributed causal influence.

## Public-letter position pilot: agreement is not uptake

`comment-position-pilot.csv` codes two positions in one
[public letter published by the Coalition to Protect America's National Parks](https://protectnps.org/2024/09/18/coalition-comments-on-epas-proposed-response-to-utahs-regional-haze-state-implementation-plan/).
The letter is dated September 18, 2024 and identifies this docket. The HTML body
was read; its acquisition hash and review scope are in
`comment-position-source.json`. This purposefully discovered public copy is
not a verified copy of the filed attachment and is not part of an uptake-rate
denominator.

| Position in public letter | August proposal | December final action | Permitted conclusion |
| --- | --- | --- | --- |
| Support partial disapproval of the regional haze plan | Partial disapproval | Partial disapproval | Policy alignment at overall disposition level |
| Support approval of monitoring strategy | Approval | Approval | Policy alignment for monitoring component |

The comparison uses the original proposed rule, document 2024-18462,
[89 FR 67254, section VI](https://www.govinfo.gov/content/pkg/FR-2024-08-19/pdf/2024-18462.pdf)
(PDF page 47), and final rule 2024-27941,
[89 FR 95120, section III continued](https://www.govinfo.gov/content/pkg/FR-2024-12-02/pdf/2024-27941.pdf)
(PDF page 4). Both pages were visually reviewed. The first PDF's SHA-256 is
`991375941e755d5e5dd08b59b3d2becbb25293e526342b10a05f8c92e36b56fa`;
the final-rule hash matches the existing issue pilot. The positions agree with
both actions, so there is no observed change at these two coded levels. This is
not a finding that all rationale or codified text remained unchanged. It also
does not prove either influence or no influence by the letter.

A docket-scoped `Coalition` keyword query returned two records with no further
page. Detail requests with `include=attachments` preserved separate IDs:

- [5115](https://www.regulations.gov/comment/EPA-R08-OAR-2024-0389-5115):
  standalone coalition submission, one PDF attachment.
- [5144](https://www.regulations.gov/comment/EPA-R08-OAR-2024-0389-5144):
  joint conservation-organization submission, eleven PDF volumes and eight
  spreadsheet attachments. None of those attachment contents was read.

Both source `receiveDate` values are September 18 and `postedDate` values are
October 9. The API field is `receiveDate`, not `receivedDate`; a nonexistent field
must not be interpreted as missing receipt evidence. The standalone PDF returned
HTTP 403. Identity, title, docket and date support a candidate link to 5115, but
do not establish a content/version match. The shared coalition name does not
license assigning its public letter to joint submission 5144 or merging the two.
The source JSON retains only public metadata projections, original-response
hashes and projection fingerprints; no credentials or full copyrighted letter
are committed. Position reviews also bind to the public-copy hash and both
rule-page source records, so changed source provenance invalidates prior coding.
The offline audit checks those projections and row joins, not
the unread docket files or independent authenticity of manual coding.

Agency response linkage, docket-version match, uptake and codified-text change
remain `not_established`, not observed zero. The two positions share one letter
and cannot be counted as two independent comments. Independent review remains
pending. Next compare the filed 5115 attachment with the public copy, then trace
its arguments in the full response document without inferring uptake from
agreement alone. The existing 500-comment corpus, two docket-issue observations
and candidate response worklist are unchanged.

The additional [EPA-hosted PacifiCorp petition](https://www.epa.gov/system/files/documents/2025-03/25-9518.pdf)
contains the published final rule as Attachment A, not the missing full response
document. PDF pages 7-8 were visually checked; the 15-page file's SHA-256 is
`f6333c8636adfdc82e7750920baace39db3234b5bbc0aac68347305d66e453ad`.
It does not supply a new response-to-comment link.

## Corpus repair

The 2026-09-12 source audit found over-escaped whitespace expressions in the
comment cleaner. They removed literal `t`, `r`, `f`, and `v` characters and
mishandled line breaks. All 500 bodies in the previous corpus were affected.
After repair, the same ordered 500 IDs were re-fetched from the official API:
500 bodies changed, none was empty, and 145 distinct body strings remained.
Template clusters and the 80-row candidate worklist were regenerated. Previous
technical-content scores and text hashes are superseded, not comparable
observations from a different time period.

`scripts/test-comment-source-products.py` covers ordinary-letter preservation,
HTML breaks, real versus literal escaped whitespace, idempotence, and exact-ID
cohort validation. `make test` includes these tests. To refresh the same cohort:

```sh
. ./scripts/load-env.sh
python3 scripts/build-first-wave-comment-products.py \
  --comment-ids-from data/calibration/first-wave/comment-body-corpus.csv
```

## Coding contract and next work

1. Record acknowledgment, substantive response, rationale change, and codified
   text change separately. Use `not_established` for missing evidence, not zero.
2. Preserve collective responses at issue/cluster level. A phrase match or
   agreement with the final rule does not identify an individual comment's effect.
3. Obtain the full response PDF and the relevant submitted comments; trace each
   pilot observation to actual comment IDs before joining it to the corpus.
4. Have a second reviewer check the evidence and resolve coding disagreements.
5. Define the sampling frame and eligible denominator before estimating uptake
   frequencies. Authenticity/triage effects need a separate comparison design.

The pilot is deliberately separate from `agency-response-final-rule-linkage.csv`.
It advances source-backed coding but does not clear that product's promotion
gate or any causal-calibration target.
