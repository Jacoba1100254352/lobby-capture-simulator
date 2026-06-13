# Procurement Refresh Readiness

This no-network preflight describes how to refresh the procurement bridge without spending quota during ordinary paper builds. It is an operational guardrail, not a source moment or empirical validation result.

## Publication Boundary

- Calibrated policy-simulation claims remain blocked until representative SAM/FPDS action-history coverage clears the procurement P1 gaps.
- Representative SAM/FPDS action-history status: `blocked` (SAM/FPDS action-history rows in frozen snapshot: 0).
- P1 procurement source-gap status: `blocked` (P1 procurement source-gap actions: 1).

## Current SAM Status

- Status: `missing`.
- Evidence: Not active in the committed snapshot. Set SAM_CONTRACT_AWARDS_LIVE_CSV or SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded Contract Awards export, or enable SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 with SAM_API_KEY; use SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 for asynchronous extracts or department-code/PIID-subtier filters plus SAM_CONTRACT_AWARDS_OFFSET_STARTS for synchronous non-adjacent page-index slices; respect SAM.gov 429 nextAccessTime before rerunning quota-limited keyed refreshes.
- Next action: Use SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded export, or run make sam-contract-awards-preflight immediately before a keyed API snapshot.

## Refresh Modes

Run `make sam-contract-awards-preflight` immediately before keyed SAM.gov API modes. The preflight makes a one-row redacted Contract Awards request and writes ignored operational reports under `reports/sam-contract-awards-preflight.*`. Manual export normalization does not spend SAM API quota.

1. Manual representative export: set `SAM_CONTRACT_AWARDS_LIVE_CSV` or `SAM_CONTRACT_AWARDS_LIVE_URL` to a downloaded SAM.gov Contract Awards CSV/JSON/ZIP export, then run `make sam-contract-awards-export-audit`. Only after the audit clears hard breadth checks should the export be promoted through `scripts/run-2024-env-live-snapshot.sh`. This path bypasses API quota during normalization while still writing `data/raw/sam-contract-awards.csv` into the standard procurement action schema.
2. Preferred keyed API run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_MODE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_FORMAT=json`, `SAM_API_KEY`, and `SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID`, then run `scripts/run-2024-env-live-snapshot.sh` after quota/access is available.
3. Bounded diagnostic run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, `SAM_CONTRACT_AWARDS_OFFSET_STARTS`, and either department-code or PIID-subtier filters, then compare the resulting rows against the bounded USAspending action panel.
4. Fallback path: keep the USAspending transaction/action panel as a schema and directional diagnostic if SAM is unavailable, quota-blocked, or returns no rows.

## Safety Rules

- Respect SAM.gov 429 `nextAccessTime` values before rerunning quota-limited refreshes.
- Keep `SOURCE_FETCH_CURL_FALLBACK=1` enabled when SAM responds to curl but hangs under urllib.
- Do not promote partial SAM payloads or timeout logs as source evidence.
- Rebuild with `make paper-artifacts-check` after any archived source refresh.

## Readiness Checklist

| Item | Status | Evidence | Next action |
| --- | --- | --- | --- |
| provenance | informational | 2026-05-05T00:00:00Z | Regenerate this report with make procurement-refresh-readiness after source-status changes. |
| sam-control-variables | ready | All SAM_CONTRACT_AWARDS controls documented in .env.example | Fill real values in .env only; do not commit private keys or raw payload archives. |
| sam-live-status | missing | Not active in the committed snapshot. Set SAM_CONTRACT_AWARDS_LIVE_CSV or SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded Contract Awards export, or enable SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 with SAM_API_KEY; use SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 for asynchronous extracts or department-code/PIID-subtier filters plus SAM_CONTRACT_AWARDS_OFFSET_STARTS for synchronous non-adjacent page-index slices; respect SAM.gov 429 nextAccessTime before rerunning quota-limited keyed refreshes. | Use SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL for a downloaded export, or run make sam-contract-awards-preflight immediately before a keyed API snapshot. |
| representative-sam-fpds-action-history | blocked | SAM/FPDS action-history rows in frozen snapshot: 0 | Archive a representative SAM/FPDS action-history panel before clearing procurement modification capture. |
| national-usaspending-concentration-panel | ready | National-volume USAspending action rows for concentration diagnostics: 1500 | Use this panel for agency and recipient concentration diagnostics only; do not use it to clear SAM/FPDS modification-incidence claims. |
| bounded-usaspending-fallback | ready | USAspending action rows remain available as bounded diagnostics: 28115 | Keep this fallback for schema checks and directional diagnostics, but do not treat it as volume-representative calibration. |
| p1-procurement-calibration-actions | blocked | P1 procurement source-gap actions: 1 | broaden the bounded USAspending action panel with representative SAM/FPDS action histories that support transaction-row, distinct-award, and amount-weighted denominators before treating modification incidence as calibrated |
| manual-export-path | ready | SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL can normalize a downloaded Contract Awards CSV/JSON/ZIP export | Use this path when SAM API quota or extract polling blocks a representative export; run make sam-contract-awards-export-audit before snapshot promotion. |
| manual-export-audit | ready | Downloaded SAM export promotion thresholds are documented for row count, award breadth, agency breadth, date span, PIID/UEI coverage, action-date coverage, and competition-field coverage. | Treat a candidate audit as a pre-promotion screen only; claim clearance still requires snapshot regeneration, validation, and paper-artifacts-check. |
| extract-mode-path | ready | SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 supports asynchronous JSON/CSV extract downloads. | Use extract mode for the next representative keyed refresh after make sam-contract-awards-preflight reports ok. |
| offset-strata-path | ready | SAM_CONTRACT_AWARDS_OFFSET_STARTS supports non-adjacent synchronous page-index strata. | Use department-code or PIID-subtier filters plus non-adjacent offsets only for bounded samples or diagnostics. |
| partial-payload-policy | ready | The live runner classifies SAM quota failures and falls back to USAspending action rows. | Do not promote partial SAM payloads; archive rows only after a completed source run and rerun paper-artifacts-check. |
| claim-boundary | blocked | Calibrated policy-simulation claims remain blocked until representative SAM/FPDS action-history coverage clears the procurement P1 gaps. | Keep the manuscript framed as a mechanism-model article with bounded empirical bridges. |
