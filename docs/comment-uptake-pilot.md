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
