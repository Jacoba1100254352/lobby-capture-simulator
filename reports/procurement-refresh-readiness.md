# Procurement Refresh Readiness

This no-network preflight describes how to refresh the procurement bridge without spending quota during ordinary paper builds. It is an operational guardrail, not a source moment or empirical validation result.

## Publication Boundary

- Procurement benchmarks are denominator-mapped against the archived USAspending bulk diagnostics; calibrated policy-simulation claims remain outside scope until causal calibration and SAM/FPDS action-history coding are reconciled.
- Representative SAM/FPDS action-history status: `blocked` (SAM/FPDS action-history rows in frozen snapshot: 0; promotion readiness: blocked; distinct awards: 0; agencies: 0; date span: 0 days; PIID coverage: 0.0000; action-date coverage: 0.0000).
- P1 procurement source-gap status: `clear` (P1 procurement source-gap actions: 0).
- Next procurement evidence: No P1 procurement source-gap actions remain; next procurement work is SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, and independent causal calibration.

## Current SAM Status

- Status: `unavailable`.
- Evidence: SAM.gov Contract Awards request failed; mode=1; format=json; filterCount=12; pageSize=100; maxPages=1; offsetPageStarts=0+10+50; fallback=USAspending action rows
- Next action: Use SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded export, or run make sam-contract-awards-preflight immediately before a keyed API snapshot.

## Refresh Modes

Run `make sam-contract-awards-preflight` immediately before keyed SAM.gov API modes. The preflight makes a one-row redacted Contract Awards request and writes ignored operational reports under `reports/sam-contract-awards-preflight.*`. Manual export normalization does not spend SAM API quota.

1. Manual representative export: set `SAM_CONTRACT_AWARDS_LIVE_CSV` or `SAM_CONTRACT_AWARDS_LIVE_URL` to a downloaded SAM.gov Contract Awards CSV/JSON/ZIP export, then run `make sam-contract-awards-export-audit`. SAM.gov emailed async-extract links with `api_key=REPLACE_WITH_API_KEY` should be recorded with `make sam-contract-awards-record-export-link < sam-email.txt` or `python3 scripts/record-sam-export-link.py --url ...`; the helper writes expiration metadata, records whether timing came from an email `Date` header, an explicit timestamp, or a record-time fallback, clears stale `SAM_CONTRACT_AWARDS_LIVE_CSV` overrides, and keeps the private key in `SAM_API_KEY`. If the helper reports `timeSource=recorded_at_fallback`, treat the link as usable only if the email was just generated; otherwise request a fresh export email. The local `SAM_API_KEY` is substituted at runtime and redacted from diagnostics. If SAM.gov returns a quota or token-download failure, the audit still writes redacted `reports/sam-contract-awards-export-audit.*` files with the HTTP status and any `nextAccessTime`, but it does not promote rows. Only after the audit reports `candidate` should the export be promoted. The `make sam-procurement-refresh` wrapper enforces that fail-closed rule before running `scripts/run-2024-env-live-snapshot.sh`; diagnostic exports require the explicit `--allow-diagnostic-export` flag or `SAM_CONTRACT_AWARDS_ALLOW_DIAGNOSTIC_PROMOTION=1`. This path bypasses API quota during normalization while still writing `data/raw/sam-contract-awards.csv` into the standard procurement action schema.
2. Preferred keyed API run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_MODE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_FORMAT=json`, `SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID=Yes`, and `SAM_API_KEY`, then run `scripts/run-2024-env-live-snapshot.sh` after quota/access is available.
3. Bounded diagnostic run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, `SAM_CONTRACT_AWARDS_OFFSET_STARTS`, and either department-code or PIID-subtier filters, then compare the resulting rows against the archived USAspending bulk summary and the smaller fallback action panel.
4. No-key USAspending bulk transaction route: run `make usaspending-transaction-download-strata` to audit row-limit-safe download/count strata, then rerun `python3 scripts/audit-usaspending-transaction-download-strata.py --download` only when intentionally archiving normalized transaction rows. When the compact summary is present in the frozen snapshot, use it as a public transaction-history denominator while preserving the calibrated-claim boundary until USAspending modification coding is crosswalked against SAM/FPDS definitions and causal calibration targets are available.
5. Fallback path: keep the bounded USAspending transaction/action panel as a schema and directional diagnostic if SAM is unavailable, quota-blocked, or returns no rows.

## Safety Rules

- Respect SAM.gov 429 `nextAccessTime` values before rerunning quota-limited refreshes.
- Keep `SOURCE_FETCH_CURL_FALLBACK=1` enabled when SAM responds to curl but hangs under urllib.
- Do not promote partial SAM payloads, timeout logs, or diagnostic exports as source evidence unless a diagnostic-only refresh is explicitly recorded.
- Rebuild with `make paper-artifacts-check` after any archived source refresh.

## Readiness Checklist

| Item | Status | Evidence | Next action |
| --- | --- | --- | --- |
| provenance | informational | 2026-05-05T00:00:00Z | Regenerate this report with make procurement-refresh-readiness after source-status changes. |
| sam-control-variables | ready | All SAM_CONTRACT_AWARDS controls documented in .env.example | Fill real values in .env only; do not commit private keys or raw payload archives. |
| sam-live-status | unavailable | SAM.gov Contract Awards request failed; mode=1; format=json; filterCount=12; pageSize=100; maxPages=1; offsetPageStarts=0+10+50; fallback=USAspending action rows | Use SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded export, or run make sam-contract-awards-preflight immediately before a keyed API snapshot. |
| representative-sam-fpds-action-history | blocked | SAM/FPDS action-history rows in frozen snapshot: 0; promotion readiness: blocked; distinct awards: 0; agencies: 0; date span: 0 days; PIID coverage: 0.0000; action-date coverage: 0.0000 | Use SAM/FPDS action-history exports to crosswalk USAspending modification coding and add exclusions, offer counts, protests, and firewall overlays before clearing procurement modification capture. |
| national-usaspending-concentration-panel | ready | National-volume USAspending action rows for concentration diagnostics: 1500 | Keep this panel as a fallback concentration diagnostic; prefer the archived bulk summary when present. |
| bounded-usaspending-fallback | ready | USAspending action rows remain available as bounded diagnostics: 28104 | Keep this fallback for schema checks and directional diagnostics, but do not treat it as volume-representative calibration. |
| usaspending-bulk-transaction-strata | ready | Archived USAspending bulk summary rows: 6449101; agencies: 12; promotion readiness: candidate | Use the archived summary as the public transaction-history denominator; rerun the bulk download only when refreshing or expanding the archive. |
| p1-procurement-calibration-actions | clear | P1 procurement source-gap actions: 0 | No P1 procurement source-gap actions remain; next procurement work is SAM/FPDS coding reconciliation, protest/exclusion/firewall overlays, and independent causal calibration. |
| manual-export-path | ready | SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL can normalize a downloaded Contract Awards CSV/JSON/ZIP export | Use this path when SAM API quota or extract polling blocks a representative export; run make sam-procurement-refresh so candidate status is enforced before snapshot promotion. |
| manual-export-audit | ready | Downloaded SAM export promotion thresholds are documented for row count, award breadth, agency breadth, date span, PIID/UEI coverage, action-date coverage, and competition-field coverage. | Treat a candidate audit as a pre-promotion screen only; claim clearance still requires snapshot regeneration, validation, and paper-artifacts-check. |
| extract-mode-path | ready | SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 supports asynchronous JSON/CSV extract downloads; SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID=Yes supplies the SAM.gov-required emailId parameter. | Use extract mode for the next representative keyed refresh after make sam-contract-awards-preflight reports ok and quota is available. |
| offset-strata-path | ready | SAM_CONTRACT_AWARDS_OFFSET_STARTS supports non-adjacent synchronous page-index strata. | Use department-code or PIID-subtier filters plus non-adjacent offsets only for bounded samples or diagnostics. |
| partial-payload-policy | ready | The live runner classifies SAM quota failures and falls back to USAspending action rows. | Do not promote partial SAM payloads, timeout logs, or diagnostic exports; archive rows only after a completed candidate source run and rerun paper-artifacts-check. |
| claim-boundary | bounded | Procurement benchmarks are denominator-mapped against the archived USAspending bulk diagnostics; calibrated policy-simulation claims remain outside scope until causal calibration and SAM/FPDS action-history coding are reconciled. | Keep the manuscript framed as a mechanism-model article with bounded empirical bridges. |
