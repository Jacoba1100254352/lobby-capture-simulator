# Public Source Data Roadmap

This roadmap translates the May 2026 source-data research into acquisition tasks. It keeps three layers separate:

- direct observed data: source rows that measure a public record directly;
- proxy data: public records that approximate hidden or partly private activity;
- restricted or poor-fit data: useful context that should not be treated as a reproducible public validation source unless an export/license is configured.

## Identifier Spine

The matching spine should prefer stable source-native identifiers:

- LDA: registrant ID, client ID, filing UUID, issue code, covered official position, agency/contact fields.
- FEC/OpenFEC: committee ID, candidate ID, cycle, schedule, transaction ID, spender/payee names.
- IRS and nonprofit records: EIN, organization name, subsection, tax period, return object ID.
- SAM/FPDS/USAspending: UEI, recipient name, awarding agency, PIID, award ID, modification number.
- Regulations.gov and Federal Register: docket ID, document ID, comment ID, object ID, comment-on ID, CFR/title metadata.
- Personnel and access records: official name, agency, position title, date range, employer, committee/hearing ID.

## Source Matrix

| Source | Evidence layer | Use in model | Access/key | Current status |
| --- | --- | --- | --- | --- |
| Senate/LDA bulk and API | Direct observed | visible lobbying spend, issue-domain mix, registrant/client concentration, agencies and covered positions | `LDA_API_KEY`; <https://lda.gov/api/register/> | Implemented source-native fetcher and 2024 ENV snapshot |
| FEC/OpenFEC | Direct observed | hard-money flows, PAC/party committees, independent expenditures, electioneering communications, lobbyist bundling | `FEC_API_KEY`; <https://api.data.gov/signup/> | Implemented for six national party committees and Schedule E independent expenditures; direct dark-money and lobbyist-bundling panels still needed |
| IRS 8871/8872 | Direct observed for 527s | politically active organization identities and reported receipts/disbursements | public bulk/web data | Normalized import schema and fixture panel implemented; source-native bulk fetch still planned |
| IRS EO BMF and Form 990 XML | Direct observed nonprofit filings, with donor limits | nonprofit intermediaries, association capacity, grantee/contractor links | public bulk; `IRS_EO_BMF_CSV_BASE`, `IRS_FORM990_BULK_BASE` | EO BMF source-native no-key importer implemented for intermediary capacity and opaque 501(c)(4)/(c)(6) capacity proxy rows; Form 990 XML remains planned |
| NYC Campaign Finance Board data library | Direct observed local program records | public matching funds, candidate public-fund payments, intermediary fundraising networks | no key; `NYC_CFB_DATA_BASE` | Source-native no-key importers implemented for public-funds payments and intermediary fundraising rows |
| ProPublica Nonprofit Explorer | Convenience layer | nonprofit metadata and 990 lookup by EIN | `PROPUBLICA_NONPROFIT_API_KEY`; <https://projects.propublica.org/nonprofits/api> | Optional overlay; normalized CSV/URL importer implemented |
| OpenSecrets | Curated proxy overlay | outside spending, dark-money routing, industry classifications, lobbying overlays | `OPENSECRETS_API_KEY`; <https://www.opensecrets.org/api/admin/index.php> | Optional; do not treat as canonical raw source |
| FollowTheMoney / National Institute on Money in Politics | Curated state/local overlay | state campaign finance, ballot-measure spending, state public-financing programs, and cross-jurisdiction donor-network checks | `FOLLOWTHEMONEY_API_KEY` | Optional overlay; source-native importer still planned |
| LegiStorm | Curated/restricted overlay | staff movements, congressional employment, some revolving-door links | `LEGISTORM_API_KEY`; <https://www.legistorm.com/api.html> | Optional/restricted; keep license status explicit |
| FACA database | Direct/proxy access record | advisory committee membership, sponsored expert access, venue shifting | public web data; `FACA_DATA_BASE` | Planned |
| House witness disclosures | Direct/proxy access record | sponsored-expert testimony, association/think-tank intermediaries | public committee pages | Planned |
| OGE disclosures | Direct/proxy personnel record | senior-official financial interests and post-employment context | public web data; `OGE_DISCLOSURE_BASE` | Planned |
| USAspending | Direct observed procurement | prime awards, recipient/agency concentration, award types, PIID fallback, single-bid, competition, offer-count, initial-award status, multi-agency top-award bridge diagnostics, and optional latest-transaction modification enrichment | no key currently required; `USASPENDING_API_BASE` | Implemented source-native parser/fetcher plus award-detail and transaction enrichment; multi-agency top-award bridge implemented for concentration diagnostics; latest-transaction modifications remain directional proxies rather than action-level incidence denominators |
| SAM.gov/FPDS | Direct observed procurement | UEI/PIID matching, contract awards, exclusions, action-level modifications | `SAM_API_KEY`; <https://open.gsa.gov/api/> | Normalized bridge fields populated where USAspending exposes them; representative source-native SAM/FPDS action-history fetch still planned |
| GAO protests | Direct observed dispute outcomes | procurement challenge pressure and sustain rates | public reports/data | Planned |
| Regulations.gov | Direct observed rulemaking | dockets, documents, comments, comment volume, duplicate/authenticity fields where available | `REGULATIONS_API_KEY`; <https://api.data.gov/signup/> | Implemented source-native fetcher |
| Federal Register | Direct observed rulemaking | proposed/final rules, dates, agency/topic metadata | no key; `FEDERAL_REGISTER_API_BASE` | Implemented source-native fetcher |

## Acquisition Sequence

1. Freeze the current 2024 EPA/ENV slice as the baseline paper snapshot.
2. Extend the OpenFEC bridge beyond Schedule E by adding direct dark-money identifiers, lobbyist-bundling records, electioneering-communication rows, and optional FollowTheMoney state/local overlays where available.
3. Broaden the public-financing bridge from the implemented NYC CFB public-funds payment importer to Seattle vouchers, federal public financing, and additional local matching-fund programs where source files can be archived.
4. Broaden the implemented NYC CFB intermediary and IRS EO BMF intermediary-capacity importers with IRS 8871/8872 plus Form 990 rows for 527, 501(c)(4), 501(c)(6), association, think-tank, and grantmaking intermediaries. Keep donor invisibility as a measured missingness property, not as a filled-in fact.
5. Broaden the procurement bridge from the EPA/USAspending slice and implemented multi-agency top-award bridge into representative SAM/FPDS action-history coverage with exclusions, action-level modifications, award-action dates, protest links, and firewall coverage for procurement firewalls, ex-post modifications, and single-bid or price-only risks.
6. Expand the LDA-derived revolving-door panel with documented source exports from LegiStorm, OGE, ProPublica appointee records, FACA, or manually archived public personnel data so covered-position headcount can be separated from post-employment movement and access intensity.
7. Add FACA and House witness disclosure panels for expert-access and intermediary venue-shifting diagnostics.
8. Rerun `make snapshot-2024-env source-moments validate calibration-queue paper-artifacts-check` and commit regenerated artifacts.

`make source-panel-inventory` should be run after each source refresh. It classifies direct dark-money, outside-spending, public-financing, intermediary, revolving-door, procurement-identifier, procurement-concentration-bridge, and procurement-modification panels as usable, thin, warning-level, or missing so model claims cannot silently outrun source coverage.

## Claim Discipline

- LDA, FEC, NYC CFB, Regulations.gov, Federal Register, USAspending, SAM/FPDS, IRS EO BMF, IRS 8871/8872, and filed Form 990 data can support observed distribution claims within their coverage limits.
- OpenSecrets, LegiStorm, ProPublica, FACA, House witness disclosures, and OGE records can strengthen bridge panels, but licensing, coverage, matching, and missingness must be disclosed.
- 501(c)(4) and 501(c)(6) donor identities are often not public. The simulator should model this as opacity and traceability; the IRS EO BMF dark-money bridge is an opaque-capacity proxy, not a direct donor or expenditure panel.
- Cross-venue detection, participation protection, and speech-restriction risk are portfolio-design metrics until source panels are built to observe coverage, false positives, and enforcement practice.
