# Procurement Refresh Readiness

This no-network preflight describes how to refresh the procurement bridge without spending quota during ordinary paper builds. It is an operational guardrail, not a source moment or empirical validation result.

## Publication Boundary

- Calibrated policy-simulation claims remain blocked until representative SAM/FPDS action-history coverage clears the procurement P1 gaps.
- Representative SAM/FPDS action-history status: `blocked` (SAM/FPDS action-history rows in frozen snapshot: 0).
- P1 procurement source-gap status: `blocked` (P1 procurement source-gap actions: 3).

## Current SAM Status

- Status: `missing`.
- Evidence: Not active in the committed snapshot. Enable SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 with SAM_API_KEY; use SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 for asynchronous extracts or department-code/PIID-subtier filters plus SAM_CONTRACT_AWARDS_OFFSET_STARTS for synchronous non-adjacent page-index slices; respect SAM.gov 429 nextAccessTime before rerunning quota-limited refreshes.
- Next action: Run only after confirming quota/access status; if the endpoint returns nextAccessTime, wait for that UTC timestamp.

## Refresh Modes

1. Preferred representative run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_MODE=1`, `SAM_CONTRACT_AWARDS_EXTRACT_FORMAT=json`, `SAM_API_KEY`, and `SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID`, then run `scripts/run-2024-env-live-snapshot.sh` after quota/access is available.
2. Bounded diagnostic run: set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1`, `SAM_CONTRACT_AWARDS_OFFSET_STARTS`, and either department-code or PIID-subtier filters, then compare the resulting rows against the bounded USAspending action panel.
3. Fallback path: keep the USAspending transaction/action panel as a schema and directional diagnostic if SAM is unavailable, quota-blocked, or returns no rows.

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
| sam-live-status | missing | Not active in the committed snapshot. Enable SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 with SAM_API_KEY; use SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 for asynchronous extracts or department-code/PIID-subtier filters plus SAM_CONTRACT_AWARDS_OFFSET_STARTS for synchronous non-adjacent page-index slices; respect SAM.gov 429 nextAccessTime before rerunning quota-limited refreshes. | Run only after confirming quota/access status; if the endpoint returns nextAccessTime, wait for that UTC timestamp. |
| representative-sam-fpds-action-history | blocked | SAM/FPDS action-history rows in frozen snapshot: 0 | Archive a representative SAM/FPDS action-history panel before clearing procurement modification capture. |
| bounded-usaspending-fallback | ready | USAspending action rows remain available as bounded diagnostics: 28115 | Keep this fallback for schema checks and directional diagnostics, but do not treat it as volume-representative calibration. |
| p1-procurement-calibration-actions | blocked | P1 procurement source-gap actions: 3 | replace the bounded USAspending concentration panel with representative SAM/FPDS action-level extracts before treating agency concentration as calibrated; broaden the bounded USAspending action panel with representative SAM/FPDS action histories that support transaction-row, distinct-award, and amount-weighted denominators before treating modification incidence as calibrated; compare recipient concentration against the bounded procurement concentration panel, then broaden by award type and fiscal year before treating it as calibrated |
| extract-mode-path | ready | SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 supports asynchronous JSON/CSV extract downloads. | Use extract mode for the next representative keyed refresh when the SAM account has Contract Awards access. |
| offset-strata-path | ready | SAM_CONTRACT_AWARDS_OFFSET_STARTS supports non-adjacent synchronous page-index strata. | Use department-code or PIID-subtier filters plus non-adjacent offsets only for bounded samples or diagnostics. |
| partial-payload-policy | ready | The live runner classifies SAM quota failures and falls back to USAspending action rows. | Do not promote partial SAM payloads; archive rows only after a completed source run and rerun paper-artifacts-check. |
| claim-boundary | blocked | Calibrated policy-simulation claims remain blocked until representative SAM/FPDS action-history coverage clears the procurement P1 gaps. | Keep the manuscript framed as a mechanism-model article with bounded empirical bridges. |
