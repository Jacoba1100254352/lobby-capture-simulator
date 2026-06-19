# Meeting/Contact Channel Missingness Design Note

This source product documents the partial meeting/contact channel for the
first-wave substitution-elasticity protocol. It is a boundary artifact, not an
estimation dataset or a clearance to treat access-channel substitution as
observed.

## Meeting Or Contact Source Availability

The current committed source surfaces include LDA visible-lobbying rows,
OpenFEC campaign-finance rows, Regulations.gov and Federal Register rulemaking
rows, USAspending/SAM procurement rows where available, intermediary or
public-financing rows from IRS, ProPublica, New York City, and Seattle sources,
and a small Reginfo.gov EO 12866 public meeting-log panel. Those sources support
visible activity, money flows, comments, procurement actions, intermediary
capacity, and bounded public access-disclosure diagnostics within their stated
limits.

The committed OIRA panel contains machine-readable public meeting disclosures
with meeting date, agency, RIN, rule title, requestor, requestor-client where
available, and source URL fields. It is useful as a bounded access-channel
source surface, but it is too sparse and too weakly linked to actors, outcomes,
and other venues to estimate substitution elasticity. The current panel is not a
representative contact-register, agency-calendar, visitor-log, or private-access
dataset. LDA records can identify agencies, covered official positions, and
issue codes, but they do not observe individual meetings or private contacts.
The public source roadmap still lists broader personnel and access records such
as official names, agency positions, dates, employers, committee or hearing
identifiers, FACA records, House witness disclosures, OGE records, richer meeting
logs, and contact registers as planned source families rather than committed
estimation panels.

## Missingness Assessment

The missing channel is private or semi-private access after visible-channel
reforms bind. Missingness is unlikely to be random. High-resource regulated
actors, associations, contractors, former officials, and technical
intermediaries may be more able to move pressure into unobserved meetings or
contacts than diffuse public-interest actors. Coverage can also vary by agency,
office, record-retention rule, visitor-log practice, calendar disclosure rule,
and whether an interaction occurs through a vendor, association, law firm,
consultant, or former official.

Because the present bundle contains only a thin public OIRA meeting panel, the
first-wave substitution-elasticity protocol must not treat unchanged public
activity in other venues as evidence that private-access substitution is absent.
The meeting/contact channel remains an omitted-channel risk for any future
cross-source substitution estimate until a broader direct access panel, a linked
public-meeting panel with outcome fields, or an explicit latent-channel
sensitivity design is added.

## Substitution Handling

The current simulator keeps meeting and contact substitution synthetic. The
OIRA rows can document that a public meeting-disclosure surface exists, but
meeting-log leak scenarios remain stress tests for reform-design diagnostics;
they are not estimated effects from observed access records.

Before a first-wave substitution estimate can be promoted, the protocol must
take one of three documented paths:

1. add a broader machine-readable meeting/contact panel with actor, issue, date,
   venue, source-record, completeness, and outcome linkage fields;
2. retain the channel as a latent access-pressure term with a declared
   sensitivity range; or
3. proxy access pressure through LDA agency, covered-position, issue fields, and
   the thin public OIRA meeting surface while clearly reporting that private
   meetings remain mostly unobserved.

The required sensitivity check is to compare the substitution design with the
meeting/contact channel excluded, bounded as latent access pressure, proxied
through LDA agency or covered-position fields, and proxied through the thin OIRA
meeting surface. Stability across those cases can support a narrower design
hypothesis, but it must not be described as causal evidence about private-access
substitution without an observed access panel.

## Provenance

- Source URLs:
  - `docs/source-data-roadmap.md`
  - `reports/first-wave-source-products.md`
  - `reports/first-wave-source-readiness.md`
  - `reports/source-panel-inventory.md`
  - `reports/source-capability-audit.md`
  - `data/snapshots/2024-env/manifest.json`
- Extracted at: 2026-06-19
- Reviewer: Codex
- Notes: This note is intended to clear only the explicit partial-access-channel design-note requirement for the source-product gate. It does not clear the named reform-shock event file, actor-issue-time spine, pre/post comparison groups, representative meeting-log panel, or any causal substitution-elasticity estimate.
