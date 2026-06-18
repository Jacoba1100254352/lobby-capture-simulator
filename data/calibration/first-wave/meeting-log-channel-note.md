# Meeting/Contact Channel Missingness Design Note

This source product documents the missing meeting/contact channel for the
first-wave substitution-elasticity protocol. It is a boundary artifact, not a
meeting-log panel, contact-register panel, or estimation dataset.

## Meeting Or Contact Source Availability

The current committed source surfaces include LDA visible-lobbying rows,
OpenFEC campaign-finance rows, Regulations.gov and Federal Register rulemaking
rows, USAspending/SAM procurement rows where available, and intermediary or
public-financing rows from IRS, ProPublica, New York City, and Seattle sources.
Those sources support visible activity, money flows, comments, procurement
actions, and intermediary capacity within their stated limits.

No committed source panel currently contains machine-readable meeting logs,
agency calendars, visitor logs, contact registers, or equivalent direct-access
records linked to actor, issue, venue, date, and outcome fields. LDA records can
identify agencies, covered official positions, and issue codes, but they do not
observe individual meetings or private contacts. The public source roadmap lists
personnel and access records such as official names, agency positions, dates,
employers, committee or hearing identifiers, FACA records, House witness
disclosures, OGE records, and meeting logs as planned source families rather
than committed estimation panels.

## Missingness Assessment

The missing channel is private or semi-private access after visible-channel
reforms bind. Missingness is unlikely to be random. High-resource regulated
actors, associations, contractors, former officials, and technical
intermediaries may be more able to move pressure into unobserved meetings or
contacts than diffuse public-interest actors. Coverage can also vary by agency,
office, record-retention rule, visitor-log practice, calendar disclosure rule,
and whether an interaction occurs through a vendor, association, law firm,
consultant, or former official.

Because the present bundle does not contain an observed meeting/contact panel,
the first-wave substitution-elasticity protocol must not treat unchanged public
activity in other venues as evidence that private-access substitution is absent.
The missing meeting/contact channel remains an omitted-channel risk for any
future cross-source substitution estimate until a direct access panel or an
explicit latent-channel sensitivity design is added.

## Substitution Handling

The current simulator keeps meeting and contact substitution synthetic. Meeting
log leak scenarios are stress tests for reform-design diagnostics; they are not
estimated effects from observed access records.

Before a first-wave substitution estimate can be promoted, the protocol must
take one of three documented paths:

1. add a machine-readable meeting/contact panel with actor, issue, date, venue,
   source-record, and outcome linkage fields;
2. retain the channel as a latent access-pressure term with a declared
   sensitivity range; or
3. proxy access pressure through LDA agency, covered-position, and issue fields
   while clearly reporting that private meetings remain unobserved.

The required sensitivity check is to compare the substitution design with the
meeting/contact channel excluded, bounded as latent access pressure, and proxied
through LDA agency or covered-position fields. Stability across those cases can
support a narrower design hypothesis, but it must not be described as causal
evidence about private-access substitution without an observed access panel.

## Provenance

- Source URLs:
  - `docs/source-data-roadmap.md`
  - `reports/first-wave-source-products.md`
  - `reports/first-wave-source-readiness.md`
  - `data/snapshots/2024-env/manifest.json`
- Extracted at: 2026-06-18
- Reviewer: Codex
- Notes: This note is intended to clear only the explicit missing-channel design-note requirement for the source-product gate. It does not clear the named reform-shock event file, actor-issue-time spine, pre/post comparison groups, meeting-log panel, or any causal substitution-elasticity estimate.
