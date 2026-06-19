#!/usr/bin/env python3
"""Write an ignored checklist for external DOI and source-refresh steps.

The paper artifact gate is intentionally offline and deterministic. This helper
collects local environment state and post-release operational reports into a
single handoff report without changing tracked publication artifacts or
asserting that a DOI, journal signoff, or SAM/FPDS panel is complete.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"
CITATION = ROOT / "CITATION.cff"
ZENODO = ROOT / ".zenodo.json"
DECLARATIONS = ROOT / "paper" / "sections" / "submission-declarations.tex"
FINAL_READTHROUGH = REPORTS / "final-human-readthrough.md"
FINAL_READTHROUGH_AUDIT_CSV = REPORTS / "final-human-readthrough-audit.csv"
DOI_READINESS_CSV = REPORTS / "doi-deposit-readiness.csv"
ZENODO_PREFLIGHT_CSV = REPORTS / "zenodo-deposit-preflight.csv"
ZENODO_DRAFT_CSV = REPORTS / "zenodo-draft-deposit.csv"
GITHUB_ASSET_AUDIT_CSV = REPORTS / "github-release-asset-audit.csv"
GITHUB_ASSET_AUDIT_MD = REPORTS / "github-release-asset-audit.md"
GITHUB_CI_STATUS_CSV = REPORTS / "github-ci-status-audit.csv"
REGGOV_GUIDELINES_CSV = REPORTS / "reggov-guidelines-readiness.csv"
SAM_PREFLIGHT_CSV = REPORTS / "sam-contract-awards-preflight.csv"
SAM_EXPORT_AUDIT_CSV = REPORTS / "sam-contract-awards-export-audit.csv"
SAM_EXPORT_AUDIT_MD = REPORTS / "sam-contract-awards-export-audit.md"
SNAPSHOT_LIVE_STATUS_CSV = ROOT / "data" / "snapshots" / "2024-env" / "live-run-status.csv"
OUT_CSV = REPORTS / "external-finalization-checklist.csv"
OUT_MD = REPORTS / "external-finalization-checklist.md"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
GENERIC_ZENODO_TOKEN_ENV_NAMES = ("ZENODO_ACCESS_TOKEN", "ZENODO_API_TOKEN", "ZENODO_TOKEN")
SANDBOX_ZENODO_TOKEN_ENV_NAMES = ("ZENODO_SANDBOX_TOKEN",)
PRODUCTION_ZENODO_TOKEN_ENV_NAMES = ("ZENODO_PRODUCTION_TOKEN",)
SECRET_QUERY_KEYS = {"api_key", "access_token", "token", "key"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when any checklist row is blocked.",
    )
    args = parser.parse_args()

    rows = checklist_rows()
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_CSV, rows)
    OUT_MD.write_text(markdown(rows), encoding="utf-8")
    print(f"Wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    if args.strict and any(row["status"] == "blocked" for row in rows):
        return 1
    return 0


def checklist_rows() -> list[dict[str, str]]:
    release_tag = release_tag_from_citation()
    release_state = release_tag_git_state(release_tag)
    rows = [
        release_tag_row(release_tag, release_state),
        doi_readiness_row(),
        github_asset_audit_row(release_state),
        github_ci_status_row(release_state),
        zenodo_target_row(),
        zenodo_token_row(),
        zenodo_draft_row(),
        zenodo_upload_row(),
        doi_record_row(),
        human_readthrough_row(release_tag),
        live_author_page_row(),
        sam_preflight_row(),
        sam_snapshot_refresh_row(),
        sam_export_input_row(),
        sam_export_audit_row(),
    ]
    return rows


def release_tag_row(release_tag: str, release_state: dict[str, str]) -> dict[str, str]:
    if not release_tag:
        return item(
            "release-tag",
            "blocked",
            "release=missing",
            "Set the versioned review-bundle tag in CITATION.cff before finalization.",
            "metadata",
        )
    status = release_state["status"]
    if status == "ready":
        next_action = "Keep CITATION.cff, .zenodo.json, paper declarations, release artifacts, and HEAD synchronized."
    else:
        next_action = "Create a new release tag for the current HEAD, update CITATION.cff and .zenodo.json, rebuild artifacts, and rerun post-release audits."
    return item(
        "release-tag",
        status,
        f"release={release_tag}; {release_state['evidence']}",
        next_action,
        "metadata",
    )


def doi_readiness_row() -> dict[str, str]:
    rows = read_csv(DOI_READINESS_CSV)
    if not rows:
        return item(
            "doi-deposit-readiness",
            "manual_required",
            "report=missing",
            "Run make doi-deposit-readiness-audit before preparing a DOI record.",
            "doi",
        )
    counts = status_counts(rows)
    blocked = counts.get("blocked", 0)
    status = "ready" if blocked == 0 else "blocked"
    final = next((row for row in rows if row.get("gate") == "final-journal-submission"), {})
    return item(
        "doi-deposit-readiness",
        status,
        (
            f"ready={counts.get('ready', 0)}; manual_required={counts.get('manual_required', 0)}; "
            f"blocked={blocked}; final={final.get('status', 'missing')}"
        ),
        "Use this report as the bounded DOI handoff surface; manual gates still require DOI, read-through, and live author-page records.",
        "doi",
    )


def github_asset_audit_row(release_state: dict[str, str] | None = None) -> dict[str, str]:
    if release_state is None:
        release_state = release_tag_git_state(release_tag_from_citation())
    if release_state["status"] != "ready":
        return item(
            "github-release-assets",
            "blocked",
            f"releaseTagTarget={release_state['status']}; {release_state['evidence']}",
            "Create or update the current release before trusting release-asset audit files.",
            "doi",
        )
    rows = read_csv(GITHUB_ASSET_AUDIT_CSV)
    if not rows:
        return item(
            "github-release-assets",
            "manual_required",
            "post-release asset audit=missing",
            "After creating or updating the GitHub release, run make github-release-asset-audit.",
            "doi",
        )
    counts = status_counts(rows, key="status")
    verified = counts.get("verified", 0)
    not_verified = sum(count for status, count in counts.items() if status != "verified")
    release_tag = release_tag_from_citation()
    md_text = read_text(GITHUB_ASSET_AUDIT_MD)
    tag_ok = not release_tag or f"Release tag: `{release_tag}`" in md_text
    status = "ready" if rows and not_verified == 0 and tag_ok else "blocked"
    evidence = (
        f"verified={verified}; nonverified={not_verified}; "
        f"releaseTag={'matches' if tag_ok else 'mismatch'}"
    )
    return item(
        "github-release-assets",
        status,
        evidence,
        "Use the verified asset digests when copying checksums into the DOI deposit record.",
        "doi",
    )


def github_ci_status_row(release_state: dict[str, str] | None = None) -> dict[str, str]:
    if release_state is None:
        release_state = release_tag_git_state(release_tag_from_citation())
    if release_state["status"] != "ready":
        return item(
            "github-ci-status",
            "blocked",
            f"releaseTagTarget={release_state['status']}; {release_state['evidence']}",
            "Create or update the current release tag and wait for GitHub Actions before treating CI evidence as synchronized.",
            "doi",
        )
    rows = read_csv(GITHUB_CI_STATUS_CSV)
    if not rows:
        return item(
            "github-ci-status",
            "manual_required",
            "post-release CI audit=missing",
            "After pushing main and the release tag, run make github-ci-status-audit.",
            "doi",
        )
    counts = status_counts(rows)
    blocked = counts.get("blocked", 0)
    manual = counts.get("manual_required", 0)
    status = "blocked" if blocked else "manual_required" if manual else "ready"
    by_gate = keyed_rows(GITHUB_CI_STATUS_CSV, "gate")
    main = by_gate.get("main-ci", {})
    tag = by_gate.get("release-tag-ci", {})
    target = by_gate.get("release-tag-target", {})
    evidence = (
        f"ready={counts.get('ready', 0)}; manual_required={manual}; blocked={blocked}; "
        f"main={main.get('runStatus', 'missing')}/{main.get('conclusion', 'missing')}; "
        f"tag={tag.get('runStatus', 'missing')}/{tag.get('conclusion', 'missing')}; "
        f"tagTarget={target.get('status', 'missing')}"
    )
    if status == "ready":
        next_action = "Retain this CI evidence with the release and DOI handoff records."
    elif status == "blocked":
        next_action = "Fix the failed or mismatched GitHub CI/tag state before final submission."
    else:
        next_action = "Wait for GitHub Actions to finish or rerun make github-ci-status-audit after the release/tag run appears."
    return item("github-ci-status", status, evidence, next_action, "doi")


def zenodo_target_row() -> dict[str, str]:
    api_base = env("ZENODO_API_BASE") or ("https://zenodo.org/api" if truthy(env("ZENODO_USE_PRODUCTION")) else "https://sandbox.zenodo.org/api")
    status = "ready" if api_base in {"https://sandbox.zenodo.org/api", "https://zenodo.org/api"} else "blocked"
    target = "production" if api_base == "https://zenodo.org/api" else "sandbox" if api_base == "https://sandbox.zenodo.org/api" else "custom"
    return item(
        "zenodo-api-target",
        status,
        f"target={target}; apiBase={api_base}",
        "Use sandbox for rehearsal; switch to production only for the final human-reviewed DOI draft.",
        "doi",
    )


def zenodo_token_row() -> dict[str, str]:
    token_name, token_present = zenodo_token_status()
    return item(
        "zenodo-token",
        "ready" if token_present else "manual_required",
        f"tokenVariable={token_name or 'missing'}; token={'present' if token_present else 'missing'}",
        "Set ZENODO_ACCESS_TOKEN, ZENODO_API_TOKEN, ZENODO_TOKEN, or the target-specific sandbox/production token in .env before running make zenodo-deposit-draft or make zenodo-deposit-upload.",
        "doi",
    )


def zenodo_draft_row() -> dict[str, str]:
    draft_rows = read_csv(ZENODO_DRAFT_CSV)
    configured_id = env("ZENODO_DEPOSIT_ID")
    if not draft_rows and not configured_id:
        return item(
            "zenodo-unpublished-draft",
            "manual_required",
            "draft=not recorded",
            "With a token configured, run make zenodo-deposit-draft to create or update an unpublished draft.",
            "doi",
        )
    blocked = any(row.get("status") == "blocked" for row in draft_rows)
    ready_steps = sum(1 for row in draft_rows if row.get("status") == "ready")
    return item(
        "zenodo-unpublished-draft",
        "blocked" if blocked else "ready",
        f"configuredId={'present' if configured_id else 'missing'}; readySteps={ready_steps}; blocked={'yes' if blocked else 'no'}",
        "Inspect the unpublished draft in Zenodo before publishing or reserving final DOI metadata.",
        "doi",
    )


def zenodo_upload_row() -> dict[str, str]:
    rows = read_csv(ZENODO_DRAFT_CSV)
    upload = next((row for row in rows if row.get("step") == "upload-package"), {})
    status = upload.get("status", "")
    if status == "ready":
        return item(
            "zenodo-package-upload",
            "ready",
            upload.get("evidence", "upload-package=ready"),
            "Verify the uploaded DOI package in the Zenodo draft before publishing.",
            "doi",
        )
    if status == "blocked":
        return item(
            "zenodo-package-upload",
            "blocked",
            upload.get("evidence", "upload-package=blocked"),
            "Fix the draft upload failure before treating the archive package as deposited.",
            "doi",
        )
    return item(
        "zenodo-package-upload",
        "manual_required",
        "upload-package=not recorded",
        "Run make zenodo-deposit-upload only after the unpublished draft metadata has been inspected.",
        "doi",
    )


def doi_record_row() -> dict[str, str]:
    doi = recorded_doi()
    configured_doi = normalize_doi(env("ARCHIVE_DOI") or env("ZENODO_RESERVED_DOI"))
    if configured_doi and not doi:
        return item(
            "doi-recorded-in-repo",
            "blocked",
            f"configuredDOI={configured_doi}; recordedDOI=missing",
            "Run make record-doi-archive, then rerun make paper-artifacts-check before treating DOI metadata as synchronized.",
            "doi",
        )
    if configured_doi and doi != configured_doi:
        return item(
            "doi-recorded-in-repo",
            "blocked",
            f"configuredDOI={configured_doi}; recordedDOI={doi}",
            "Resolve the DOI mismatch, run make record-doi-archive, and rebuild the paper artifacts before DOI publication.",
            "doi",
        )
    return item(
        "doi-recorded-in-repo",
        "ready" if doi else "manual_required",
        f"DOI={'present: ' + doi if doi else 'not recorded'}; configuredDOI={configured_doi or 'missing'}",
        "After a DOI is reserved or minted, set ARCHIVE_DOI in .env, run make record-doi-archive, and then rerun make paper-artifacts-check.",
        "doi",
    )


def human_readthrough_row(release_tag: str) -> dict[str, str]:
    audit_rows = keyed_rows(FINAL_READTHROUGH_AUDIT_CSV, "item")
    audit_overall = audit_rows.get("overall-final-human-readthrough", {})
    if audit_overall:
        audit_status = audit_overall.get("status", "manual_required")
        status = "ready" if audit_status == "ready" else "blocked" if audit_status == "blocked" else "manual_required"
        return item(
            "human-scholarly-readthrough",
            status,
            audit_overall.get("evidence", "final human read-through audit present"),
            audit_overall.get("nextAction", "Complete the human scholarly read-through against the exact release tag before final journal submission."),
            "journal",
        )

    text = read_text(FINAL_READTHROUGH)
    status = field_value(text, "status") or "missing"
    signer = bool(field_value(text, "signed-off-by"))
    date = bool(field_value(text, "signed-off-date"))
    commit = bool(field_value(text, "reviewed-commit"))
    reviewed = field_value(text, "reviewed-release") or "missing"
    complete = status.lower() == "complete" and signer and date and commit and reviewed == release_tag
    return item(
        "human-scholarly-readthrough",
        "ready" if complete else "manual_required",
        f"status={status}; reviewedRelease={reviewed}; signer={'present' if signer else 'missing'}; date={'present' if date else 'missing'}; commit={'present' if commit else 'missing'}",
        "Complete the human scholarly read-through against the exact release tag before final journal submission.",
        "journal",
    )


def live_author_page_row() -> dict[str, str]:
    rows = keyed_rows(REGGOV_GUIDELINES_CSV, "gate")
    row_data = rows.get("live-reggov-author-page-refresh", {})
    status = row_data.get("status", "manual_required")
    normalized_status = status if status in {"ready", "blocked"} else "manual_required"
    default_next_action = (
        "Recheck the live Regulation & Governance author instructions immediately before final submission."
        if normalized_status == "ready"
        else "Open the live Regulation & Governance author instructions and record any superseding guidance before final submission."
    )
    return item(
        "live-reggov-author-page-refresh",
        normalized_status,
        row_data.get("evidence", "live author-page refresh=not recorded"),
        row_data.get("nextAction", default_next_action) or default_next_action,
        "journal",
    )


def sam_preflight_row() -> dict[str, str]:
    rows = read_csv(SAM_PREFLIGHT_CSV)
    if not rows:
        return item(
            "sam-keyed-preflight",
            "manual_required",
            "preflight=missing",
            "Run make sam-contract-awards-preflight immediately before keyed SAM.gov API refreshes; do not promote rows unless it reports ok.",
            "source-refresh",
        )
    row = rows[0]
    status = row.get("status", "").strip()
    rows_returned = row.get("rows", "").strip()
    next_access = row.get("nextAccessTime", "").strip()
    notes = row.get("notes", "").strip()
    if status == "ok":
        checklist_status = "ready"
        next_action = (
            "If a keyed refresh is intended, run scripts/run-2024-env-live-snapshot.sh "
            "with representative settings and rebuild paper artifacts before using refreshed rows."
        )
    elif status == "quota_blocked":
        checklist_status = "manual_required"
        next_action = (
            f"Wait until {next_access or 'the SAM.gov reset time'} or use a downloaded export "
            "through SAM_CONTRACT_AWARDS_LIVE_CSV/URL before rerunning the preflight."
        )
    elif status == "missing":
        checklist_status = "manual_required"
        next_action = "Set SAM_API_KEY in .env before running make sam-contract-awards-preflight."
    elif status in {"unavailable", "empty"}:
        checklist_status = "blocked"
        next_action = (
            "Resolve the keyed SAM.gov access/preflight condition before any keyed live snapshot; "
            "use the manual export path if available."
        )
    else:
        checklist_status = "manual_required"
        next_action = (
            "Review the SAM.gov preflight status, rerun make sam-contract-awards-preflight, "
            "or use the manual export path if available."
        )
    evidence = (
        f"status={status or 'missing'}; rows={rows_returned or '0'}; "
        f"nextAccessTime={next_access or 'none'}"
    )
    if notes:
        evidence = f"{evidence}; notes={notes}"
    return item(
        "sam-keyed-preflight",
        checklist_status,
        evidence,
        next_action,
        "source-refresh",
    )


def sam_snapshot_refresh_row() -> dict[str, str]:
    rows = read_csv(SNAPSHOT_LIVE_STATUS_CSV)
    if not rows:
        return item(
            "sam-snapshot-refresh-status",
            "manual_required",
            "snapshot live-run status=missing",
            "Run make sam-procurement-refresh or snapshot-2024-env before treating SAM/FPDS source status as current.",
            "source-refresh",
        )
    row = next((candidate for candidate in rows if candidate.get("source") == "sam-contract-awards"), {})
    if not row:
        return item(
            "sam-snapshot-refresh-status",
            "manual_required",
            "sam-contract-awards live-run row=missing",
            "Rerun the guarded SAM procurement refresh so the snapshot records whether SAM/FPDS rows were promoted, unavailable, or quota-blocked.",
            "source-refresh",
        )
    status = row.get("status", "").strip() or "missing"
    notes = row.get("notes", "").strip()
    next_access = sam_next_access_from_notes(notes)
    if status == "ok":
        checklist_status = "ready"
        next_action = "Keep the promoted SAM/FPDS snapshot row with the artifact bundle and rerun paper-artifacts-check after any source change."
    elif status == "quota_blocked":
        checklist_status = "manual_required"
        next_action = (
            f"Wait until {next_access or 'the SAM.gov reset time'}, or use a fresh downloaded SAM export, "
            "before trying to promote SAM/FPDS rows again."
        )
    elif status in {"unavailable", "missing"}:
        checklist_status = "manual_required"
        next_action = "Use the manual export path or a mode-matched keyed preflight before rerunning make sam-procurement-refresh."
    elif status in {"fixture", "skipped"}:
        checklist_status = "manual_required"
        next_action = "Do not treat SAM/FPDS evidence as promoted unless this row reports ok with nonzero normalized rows."
    else:
        checklist_status = "manual_required"
        next_action = "Review the SAM snapshot live-run status before relying on the procurement source bridge."
    evidence = f"status={status}; notes={notes or 'missing'}"
    if next_access:
        evidence = f"{evidence}; nextAccessTime={next_access}"
    return item(
        "sam-snapshot-refresh-status",
        checklist_status,
        evidence,
        next_action,
        "source-refresh",
    )


def sam_export_input_row() -> dict[str, str]:
    csv_path = env("SAM_CONTRACT_AWARDS_LIVE_CSV")
    url = env("SAM_CONTRACT_AWARDS_LIVE_URL")
    sam_key_present = bool(env("SAM_API_KEY"))
    if csv_path:
        path = Path(csv_path).expanduser()
        exists = path.exists()
        return item(
            "sam-export-input",
            "ready" if exists else "blocked",
            f"configuredCsv={path}; exists={'yes' if exists else 'no'}",
            "Run make sam-procurement-refresh so the export audit must report candidate before snapshot promotion.",
            "source-refresh",
        )
    if url:
        needs_key = "REPLACE_WITH_API_KEY" in url
        key_resolution = sam_export_key_resolution(needs_key, sam_key_present)
        freshness = sam_export_url_freshness()
        retry_window_missed = sam_export_retry_window_missed(freshness["evidence"])
        status = "ready" if (not needs_key or sam_key_present) and freshness["status"] == "fresh" else "manual_required"
        evidence = (
            f"configuredUrl={redact_url(url)}; placeholderKey={'yes' if needs_key else 'no'}; "
            f"SAM_API_KEY={'present' if sam_key_present else 'missing'}; keyResolution={key_resolution}; "
            f"linkFreshness={freshness['status']}; {freshness['evidence']}"
        )
        next_action = "Keep the emailed URL in SAM_CONTRACT_AWARDS_LIVE_URL and the private key in SAM_API_KEY, then run make sam-procurement-refresh."
        if retry_window_missed:
            status = "manual_required"
            evidence = f"{evidence}; retryWindow=missed"
            next_action = "Wait for the SAM.gov quota reset, request a fresh export email, record the full email with make sam-contract-awards-record-export-link or a just-received body-only email with make sam-contract-awards-record-fresh-link, then rerun make sam-procurement-refresh."
        if freshness["status"] == "expired":
            next_action = "Request a fresh SAM.gov export email, record the full email with make sam-contract-awards-record-export-link or a just-received body-only email with make sam-contract-awards-record-fresh-link, then run make sam-procurement-refresh."
        elif freshness["status"] == "unknown":
            next_action = "Record this emailed URL with make sam-contract-awards-record-export-link so expiration metadata is set, then run make sam-procurement-refresh before the token expires."
        if needs_key and not sam_key_present:
            if freshness["status"] == "expired" or retry_window_missed:
                next_action = "Set SAM_API_KEY in .env, request a fresh SAM.gov export email, record the full email with make sam-contract-awards-record-export-link or a just-received body-only email with make sam-contract-awards-record-fresh-link, then run make sam-procurement-refresh."
            elif freshness["status"] == "unknown":
                next_action = "Set SAM_API_KEY in .env so the REPLACE_WITH_API_KEY placeholder can be substituted at runtime, then run make sam-procurement-refresh before the token expires."
            else:
                next_action = "Set SAM_API_KEY in .env so the REPLACE_WITH_API_KEY placeholder can be substituted at runtime, then run make sam-procurement-refresh before the token expires."
        return item(
            "sam-export-input",
            status,
            evidence,
            next_action,
            "source-refresh",
        )
    return item(
        "sam-export-input",
        "manual_required",
        "SAM_CONTRACT_AWARDS_LIVE_CSV/URL=missing",
        "If using a SAM.gov email link, record the full email with make sam-contract-awards-record-export-link or a just-received body-only email with make sam-contract-awards-record-fresh-link so .env keeps api_key=REPLACE_WITH_API_KEY, expiration metadata, and a separate SAM_API_KEY.",
        "source-refresh",
    )


def sam_export_key_resolution(needs_key: bool, sam_key_present: bool) -> str:
    if not needs_key:
        return "not_needed"
    if sam_key_present:
        return "runtime_substituted"
    return "missing_key"


def sam_export_retry_window_missed(freshness_evidence: str) -> bool:
    rows = keyed_rows(SAM_EXPORT_AUDIT_CSV, "item")
    row = rows.get("export-link-retry-window", {})
    return (
        row.get("status") == "manual_required"
        and row.get("value") == "quota reset occurs after emailed token expiry"
        and row.get("notes") == freshness_evidence
    )


def sam_export_audit_row() -> dict[str, str]:
    rows = read_csv(SAM_EXPORT_AUDIT_CSV)
    if not rows:
        return item(
            "sam-export-audit",
            "manual_required",
            "audit=missing",
            "Run make sam-procurement-refresh after configuring a SAM export CSV or emailed URL; the wrapper audits first and promotes only candidate exports.",
            "source-refresh",
        )
    promotion = next((row for row in rows if row.get("item") == "promotion-readiness"), rows[0])
    promotion_status = promotion.get("status", "")
    source_rows = audit_item_value(rows, "row-count") or "missing"
    promotion_value = promotion.get("value", "").strip()
    hard_blockers = sam_export_hard_blockers(rows)
    shape_summary = sam_export_shape_summary(rows)
    promotion_summary = (
        f"previousPromotion={promotion_status or 'missing'}"
        if not (env("SAM_CONTRACT_AWARDS_LIVE_CSV") or env("SAM_CONTRACT_AWARDS_LIVE_URL"))
        else f"promotion={promotion_status or 'missing'}"
    )
    if promotion_value:
        promotion_summary = f"{promotion_summary}; {promotion_value}"
    if hard_blockers:
        promotion_summary = f"{promotion_summary}; hardBlockers={'+'.join(hard_blockers)}"
    if shape_summary:
        promotion_summary = f"{promotion_summary}; {shape_summary}"
    if not (env("SAM_CONTRACT_AWARDS_LIVE_CSV") or env("SAM_CONTRACT_AWARDS_LIVE_URL")):
        return item(
            "sam-export-audit",
            "manual_required",
            f"staleAudit=present; currentInput=missing; {promotion_summary}; sourceRows={source_rows}; auditRows={len(rows)}",
            "Configure the current SAM export URL or CSV in .env, then rerun make sam-procurement-refresh so stale audits cannot be promoted.",
            "source-refresh",
        )
    if promotion_status == "candidate":
        status = "ready"
    elif promotion_status in {"quota_blocked", "manual_required", "diagnostic"}:
        status = "manual_required"
    else:
        status = "blocked"
    return item(
        "sam-export-audit",
        status,
        f"{promotion_summary}; sourceRows={source_rows}; auditRows={len(rows)}",
        sam_export_next_action(status, hard_blockers, shape_summary),
        "source-refresh",
    )


def recorded_doi() -> str:
    for path in (CITATION, ZENODO, DECLARATIONS, FINAL_READTHROUGH):
        match = DOI_PATTERN.search(read_text(path))
        if match:
            return match.group(0)
    return ""


def normalize_doi(value: str) -> str:
    match = DOI_PATTERN.search(value.strip())
    return match.group(0) if match else ""


def release_tag_from_citation() -> str:
    match = VERSION_PATTERN.search(read_text(CITATION))
    return match.group(1).strip() if match else ""


def status_counts(rows: list[dict[str, str]], key: str = "status") -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get(key, "")
        if status:
            counts[status] = counts.get(status, 0) + 1
    return counts


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path)}


def audit_item_value(rows: list[dict[str, str]], item_name: str) -> str:
    row = next((candidate for candidate in rows if candidate.get("item") == item_name), {})
    return row.get("value", "").strip()


def sam_export_hard_blockers(rows: list[dict[str, str]]) -> list[str]:
    return [
        row.get("item", "")
        for row in rows
        if row.get("status") == "blocked" and row.get("item") != "promotion-readiness"
    ]


def sam_export_shape_summary(rows: list[dict[str, str]]) -> str:
    parts = []
    for item_name, label in [
        ("raw-action-date-candidate-share", "rawActionDate"),
        ("raw-solicitation-date-share", "rawSolicitationDate"),
        ("raw-amount-field-share", "rawAmount"),
    ]:
        value = audit_item_value(rows, item_name)
        if value:
            parts.append(f"{label}={value}")
    return "; ".join(parts)


def sam_export_next_action(status: str, blockers: list[str], shape_summary: str) -> str:
    if status == "ready":
        return "Promote through make sam-procurement-refresh so the audited candidate export is followed by the live snapshot and full paper-artifacts-check; the audit alone does not clear procurement claims."
    if blockers:
        blocker_text = "+".join(blockers)
        shape_text = f" Current shape: {shape_summary}." if shape_summary else ""
        return (
            "Do not promote this SAM export. Request an action-history export with multi-agency breadth, "
            "action/signed dates, obligation or current-award-value fields, and competition/offer fields; "
            f"current hard blockers={blocker_text}.{shape_text}"
        )
    if status == "manual_required":
        return "Resolve the SAM.gov token/quota/download condition, rerun make sam-procurement-refresh, and promote only after the audit reports candidate."
    return "Use make sam-procurement-refresh to audit, promote, refresh the live snapshot, and run paper-artifacts-check with the SAM export."


def sam_next_access_from_notes(notes: str) -> str:
    match = re.search(r"until ([^;,\n]+UTC)", notes)
    return match.group(1).strip() if match else ""


def sam_export_url_freshness() -> dict[str, str]:
    generated_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_GENERATED_AT")
    expires_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_EXPIRES_AT")
    recorded_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_RECORDED_AT")
    time_source = env("SAM_CONTRACT_AWARDS_LIVE_URL_TIME_SOURCE") or "missing"
    ttl_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_VALID_MINUTES") or "60"
    generated = parse_time(generated_raw)
    expires = parse_time(expires_raw)
    recorded = parse_time(recorded_raw)
    ttl_minutes = parse_positive_int(ttl_raw, default=60)
    if not expires and generated:
        expires = generated + timedelta(minutes=ttl_minutes)
    if not generated and not expires:
        return {
            "status": "unknown",
            "evidence": sam_freshness_evidence(None, None, ttl_minutes, recorded, time_source),
        }
    if generated_raw and not generated:
        return {
            "status": "unknown",
            "evidence": sam_freshness_evidence("unparseable", expires, ttl_minutes, recorded, time_source),
        }
    if expires_raw and not expires:
        return {
            "status": "unknown",
            "evidence": sam_freshness_evidence(generated, "unparseable", ttl_minutes, recorded, time_source),
        }
    assert expires is not None
    status = "fresh" if datetime.now(timezone.utc) < expires else "expired"
    return {
        "status": status,
        "evidence": sam_freshness_evidence(generated, expires, ttl_minutes, recorded, time_source),
    }


def sam_freshness_evidence(
        generated: datetime | str | None,
        expires: datetime | str | None,
        ttl_minutes: int,
        recorded: datetime | None,
        time_source: str,
) -> str:
    generated_text = generated if isinstance(generated, str) else fmt_time(generated) or "missing"
    expires_text = expires if isinstance(expires, str) else fmt_time(expires) or "missing"
    return (
        f"generatedAt={generated_text}; expiresAt={expires_text}; "
        f"ttlMinutes={ttl_minutes}; recordedAt={fmt_time(recorded) or 'missing'}; "
        f"timeSource={time_source}"
    )


def parse_time(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    normalized = value
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fmt_time(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_positive_int(value: str, default: int) -> int:
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def field_value(text: str, field_name: str) -> str:
    match = re.search(
        rf"^[^\S\n]*{re.escape(field_name)}[^\S\n]*:[^\S\n]*(.*?)[^\S\n]*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def release_tag_git_state(release_tag: str) -> dict[str, str]:
    if not release_tag:
        return {"status": "blocked", "evidence": "release=missing"}
    head, head_error = git_maybe_output(["rev-parse", "HEAD"])
    tag_sha, tag_error = git_maybe_output(["rev-parse", f"{release_tag}^{{commit}}"])
    if head_error:
        return {"status": "blocked", "evidence": f"head=unresolved; error={head_error}"}
    if tag_error:
        return {
            "status": "blocked",
            "evidence": f"head={short_sha(head)}; tag=unresolved; error={tag_error}",
        }
    status = "ready" if head == tag_sha else "blocked"
    evidence = (
        f"head={short_sha(head)}; tag={short_sha(tag_sha)}; "
        f"tagTarget={'current-head' if status == 'ready' else 'mismatch'}"
    )
    return {"status": status, "evidence": evidence}


def git_maybe_output(args: list[str]) -> tuple[str, str]:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.PIPE).strip(), ""
    except (OSError, subprocess.CalledProcessError) as error:
        stderr = getattr(error, "stderr", "") or str(error)
        return "", stderr.strip()


def short_sha(value: str) -> str:
    return value[:12] if value else "missing"


def env(key: str) -> str:
    return os.environ.get(key, "").strip()


def zenodo_token_status() -> tuple[str, bool]:
    api_base = env("ZENODO_API_BASE") or ("https://zenodo.org/api" if truthy(env("ZENODO_USE_PRODUCTION")) else "https://sandbox.zenodo.org/api")
    names: list[str] = []
    if api_base.rstrip("/") == "https://sandbox.zenodo.org/api":
        names.extend(SANDBOX_ZENODO_TOKEN_ENV_NAMES)
    elif api_base.rstrip("/") == "https://zenodo.org/api":
        names.extend(PRODUCTION_ZENODO_TOKEN_ENV_NAMES)
    names.extend(GENERIC_ZENODO_TOKEN_ENV_NAMES)
    for name in names:
        if env(name):
            return name, True
    return "", False


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def redact_url(value: str) -> str:
    if not value:
        return ""
    parts = urlsplit(value)
    query = []
    for key, raw in parse_qsl(parts.query, keep_blank_values=True):
        query.append((key, "REDACTED" if key.lower() in SECRET_QUERY_KEYS else raw))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def item(name: str, status: str, evidence: str, next_action: str, category: str) -> dict[str, str]:
    return {
        "item": name,
        "category": category,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=["item", "category", "status", "evidence", "nextAction"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    counts = status_counts(rows)
    release_tag = release_tag_from_citation()
    finalization_posture = posture_for_categories(rows, {"metadata", "doi", "journal"})
    source_refresh_posture = posture_for_categories(rows, {"source-refresh"})
    blocked = [row for row in rows if row["status"] == "blocked"]
    manual = [row for row in rows if row["status"] == "manual_required"]
    lines = [
        "# External Finalization Checklist",
        "",
        "This ignored operational checklist consolidates local environment state, post-release asset verification, DOI handoff status, journal-finalization items, and SAM.gov export readiness. It is not part of the deterministic paper artifact gate and does not assert that a DOI, journal submission, or promoted SAM/FPDS panel exists.",
        "",
        "## Summary",
        "",
        f"- Release tag: `{md(release_tag or 'missing')}`",
        f"- DOI/journal finalization posture: `{finalization_posture}`",
        f"- Source-refresh posture: `{source_refresh_posture}`",
        f"- Ready: `{counts.get('ready', 0)}`",
        f"- Manual required: `{counts.get('manual_required', 0)}`",
        f"- Blocked: `{counts.get('blocked', 0)}`",
        "",
        "## Checklist",
        "",
        "| Item | Category | Status | Evidence | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {item} | {category} | {status} | {evidence} | {nextAction} |".format(
                item=md(row["item"]),
                category=md(row["category"]),
                status=md(row["status"]),
                evidence=md(row["evidence"]),
                nextAction=md(row["nextAction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Immediate Commands",
            "",
            "Use these commands after filling any private values in `.env`:",
            "",
            "```sh",
            "make github-release-asset-audit",
            "make github-ci-status-audit",
            "make external-finalization-checklist",
            "",
            "# After Zenodo, OSF, or another archive reserves or mints a DOI:",
            "# set ARCHIVE_DOI and optionally ARCHIVE_URL in .env",
            "make record-doi-archive",
            "make paper-artifacts-check",
            "make external-finalization-checklist",
            "",
            "# If a SAM.gov emailed export link is available:",
            "# make sam-contract-awards-record-export-link < sam-email-with-headers.txt",
            "# make sam-contract-awards-record-fresh-link < just-received-sam-email-body.txt",
            "make sam-procurement-refresh",
            "# For audit-only diagnostics without snapshot promotion:",
            "make sam-contract-awards-export-audit",
            "",
            "# Before a keyed SAM.gov Contract Awards API refresh:",
            "make sam-contract-awards-preflight",
            "# Use the mode-specific checks before the guarded wrapper chooses that mode:",
            "make sam-contract-awards-preflight-extract",
            "make sam-contract-awards-preflight-offset",
            "",
            "# If a Zenodo token is configured and the draft should be rehearsed or updated:",
            "make zenodo-deposit-draft",
            "make zenodo-deposit-upload",
            "```",
            "",
            "## Boundaries",
            "",
            "- `ready` means the local operational precondition is present or verified.",
            "- `manual_required` means the next step depends on a private credential, a live website, or a human signoff.",
            "- `blocked` means a configured input or post-release check disagrees with the expected state for that category.",
            "- A source-refresh `blocked` item blocks promotion of that live source into a refreshed snapshot; it does not invalidate the current released review bundle unless the manuscript is regenerated to rely on that source.",
            "- A candidate SAM export still must be promoted through the live snapshot and full paper artifact gate before it affects manuscript evidence.",
            "- A Zenodo draft or upload is not a published DOI record until the record is explicitly published and the DOI is recorded in repository metadata.",
            "",
        ]
    )
    if blocked:
        lines.extend(["## Blocked Items", ""])
        for row in blocked:
            lines.append(f"- `{md(row['item'])}`: {md(row['evidence'])}")
        lines.append("")
    if manual:
        lines.extend(["## Manual Items", ""])
        for row in manual:
            lines.append(f"- `{md(row['item'])}`: {md(row['nextAction'])}")
        lines.append("")
    return "\n".join(lines)


def posture_for_categories(rows: list[dict[str, str]], categories: set[str]) -> str:
    scoped = [row for row in rows if row.get("category") in categories]
    if any(row.get("status") == "blocked" for row in scoped):
        return "blocked"
    if any(row.get("status") == "manual_required" for row in scoped):
        return "manual_required"
    if scoped and all(row.get("status") == "ready" for row in scoped):
        return "ready"
    return "unknown"


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
