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
import json
import os
import re
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
DOI_READINESS_CSV = REPORTS / "doi-deposit-readiness.csv"
ZENODO_PREFLIGHT_CSV = REPORTS / "zenodo-deposit-preflight.csv"
ZENODO_DRAFT_CSV = REPORTS / "zenodo-draft-deposit.csv"
GITHUB_ASSET_AUDIT_CSV = REPORTS / "github-release-asset-audit.csv"
GITHUB_ASSET_AUDIT_MD = REPORTS / "github-release-asset-audit.md"
REGGOV_GUIDELINES_CSV = REPORTS / "reggov-guidelines-readiness.csv"
SAM_EXPORT_AUDIT_CSV = REPORTS / "sam-contract-awards-export-audit.csv"
SAM_EXPORT_AUDIT_MD = REPORTS / "sam-contract-awards-export-audit.md"
OUT_CSV = REPORTS / "external-finalization-checklist.csv"
OUT_MD = REPORTS / "external-finalization-checklist.md"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
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
    rows = [
        item(
            "release-tag",
            "ready" if release_tag else "blocked",
            f"release={release_tag or 'missing'}",
            "Keep CITATION.cff, .zenodo.json, paper declarations, and release artifacts synchronized.",
            "metadata",
        ),
        doi_readiness_row(),
        github_asset_audit_row(),
        zenodo_target_row(),
        zenodo_token_row(),
        zenodo_draft_row(),
        zenodo_upload_row(),
        doi_record_row(),
        human_readthrough_row(release_tag),
        live_author_page_row(),
        sam_export_input_row(),
        sam_export_audit_row(),
    ]
    return rows


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


def github_asset_audit_row() -> dict[str, str]:
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
    token_present = bool(env("ZENODO_ACCESS_TOKEN") or env("ZENODO_API_TOKEN"))
    return item(
        "zenodo-token",
        "ready" if token_present else "manual_required",
        "ZENODO_ACCESS_TOKEN=" + ("present" if token_present else "missing"),
        "Set ZENODO_ACCESS_TOKEN in .env before running make zenodo-deposit-draft or make zenodo-deposit-upload.",
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
    return item(
        "doi-recorded-in-repo",
        "ready" if doi else "manual_required",
        f"DOI={'present: ' + doi if doi else 'not recorded'}",
        "After a DOI is reserved or minted, record it in CITATION.cff, .zenodo.json, paper declarations, and final-human-readthrough.md.",
        "doi",
    )


def human_readthrough_row(release_tag: str) -> dict[str, str]:
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
    return item(
        "live-reggov-author-page-refresh",
        status if status in {"ready", "blocked"} else "manual_required",
        row_data.get("evidence", "live author-page refresh=not recorded"),
        "Open the live Regulation & Governance author instructions and record any superseding guidance before final submission.",
        "journal",
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
            "Run SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/export.zip make sam-contract-awards-export-audit before snapshot promotion.",
            "source-refresh",
        )
    if url:
        needs_key = "REPLACE_WITH_API_KEY" in url
        status = "ready" if (not needs_key or sam_key_present) else "manual_required"
        evidence = (
            f"configuredUrl={redact_url(url)}; placeholderKey={'yes' if needs_key else 'no'}; "
            f"SAM_API_KEY={'present' if sam_key_present else 'missing'}"
        )
        return item(
            "sam-export-input",
            status,
            evidence,
            "Keep the emailed URL in SAM_CONTRACT_AWARDS_LIVE_URL and the private key in SAM_API_KEY, then run make sam-contract-awards-export-audit.",
            "source-refresh",
        )
    return item(
        "sam-export-input",
        "manual_required",
        "SAM_CONTRACT_AWARDS_LIVE_CSV/URL=missing",
        "If using a SAM.gov email link, paste it into .env as SAM_CONTRACT_AWARDS_LIVE_URL with api_key=REPLACE_WITH_API_KEY and keep SAM_API_KEY separate.",
        "source-refresh",
    )


def sam_export_audit_row() -> dict[str, str]:
    rows = read_csv(SAM_EXPORT_AUDIT_CSV)
    if not rows:
        return item(
            "sam-export-audit",
            "manual_required",
            "audit=missing",
            "Run make sam-contract-awards-export-audit after configuring a SAM export CSV or emailed URL.",
            "source-refresh",
        )
    promotion = next((row for row in rows if row.get("item") == "promotion-readiness"), rows[0])
    promotion_status = promotion.get("status", "")
    source_rows = audit_item_value(rows, "row-count") or "missing"
    promotion_value = promotion.get("value", "").strip()
    promotion_summary = (
        f"previousPromotion={promotion_status or 'missing'}"
        if not (env("SAM_CONTRACT_AWARDS_LIVE_CSV") or env("SAM_CONTRACT_AWARDS_LIVE_URL"))
        else f"promotion={promotion_status or 'missing'}"
    )
    if promotion_value:
        promotion_summary = f"{promotion_summary}; {promotion_value}"
    if not (env("SAM_CONTRACT_AWARDS_LIVE_CSV") or env("SAM_CONTRACT_AWARDS_LIVE_URL")):
        return item(
            "sam-export-audit",
            "manual_required",
            f"staleAudit=present; currentInput=missing; {promotion_summary}; sourceRows={source_rows}; auditRows={len(rows)}",
            "Configure the current SAM export URL or CSV in .env, then rerun make sam-contract-awards-export-audit.",
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
        "Use the audit output to decide whether to rerun the live snapshot and paper-artifacts-check with the SAM export.",
        "source-refresh",
    )


def recorded_doi() -> str:
    for path in (CITATION, ZENODO, DECLARATIONS, FINAL_READTHROUGH):
        match = DOI_PATTERN.search(read_text(path))
        if match:
            return match.group(0)
    return ""


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


def env(key: str) -> str:
    return os.environ.get(key, "").strip()


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
            "make external-finalization-checklist",
            "",
            "# If a SAM.gov emailed export link is configured in .env:",
            "make sam-contract-awards-export-audit",
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
