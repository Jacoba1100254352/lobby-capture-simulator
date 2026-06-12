# Source Capability Audit

This audit separates implemented live-source routes from the empirical support actually present in the committed 2024 snapshot. It is a process guardrail: an implemented importer does not support manuscript claims unless the frozen snapshot contains usable rows and the claim ledger permits the claim. Direct hidden-donor and SAM/FPDS action-history routes remain especially important claim boundaries.

## Summary

- active-usable: `3`
- implemented-not-active: `1`
- planned-overlay: `1`
- proxy-only: `1`

| Capability | Snapshot source | Rows | Panel status | Capability status | Needed for | Next action |
| --- | --- | ---: | --- | --- | --- | --- |
| direct-dark-money-routing | dark-money (ok) | 250 | fixture-only | proxy-only | Hidden-channel magnitude and calibrated policy-simulation claims | Add curated direct dark-money, nonprofit-routing, or hidden-donor source rows and keep them separate from Schedule E, electioneering, communication-cost, and IRS BMF capacity proxies. |
| sam-contract-awards-action-history | sam-contract-awards (missing) | 0 | thin | implemented-not-active | Procurement modification capture and calibrated policy-simulation claims | Archive a representative SAM/FPDS action-history pull or configured export; compare modification incidence against the bounded USAspending action panel. |
| usaspending-stratified-action-panel | usaspending-procurement-actions (ok) | 2399 | usable | active-usable | Bounded procurement concentration and modification diagnostics | Broaden beyond the selected 12-agency quarterly stress panel before treating modification incidence as calibration-grade. |
| lda-covered-position-revolving-door | revolving-door (ok) | 803 | usable | active-usable | Revolving-door access mechanism diagnostics | Supplement with OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel-movement exports before claiming representative post-employment movement. |
| irs-527-political-organizations | intermediary (ok) | 1353 | usable | active-usable | Intermediary and campaign-adjacent substitution diagnostics | Broaden beyond the bounded alphabetic slice while preserving 527 rows as distinct from 501(c)(4)/(c)(6) dark-money evidence. |
| licensed-access-overlays | not-promoted (not-promoted) | 0 | not-promoted | planned-overlay | Representative hidden-channel, intermediary, and personnel-movement validation | Implement importer-specific schemas only after licensing and export fields are fixed enough to preserve reproducibility. |
