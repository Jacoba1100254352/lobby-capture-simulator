#!/usr/bin/env python3
"""Prepare, and optionally create, an unpublished Zenodo draft deposit.

The default mode is an offline preflight. Networked draft creation is opt-in and
never publishes a deposition. This keeps the reviewer/release build
reproducible while making the final DOI archive step operational when a Zenodo
token is available.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
CITATION = ROOT / "CITATION.cff"
ZENODO = ROOT / ".zenodo.json"
DOI_PACKAGE = DIST / "lobby-capture-doi-deposit-package.zip"
DOI_PACKAGE_MANIFEST = DIST / "doi-deposit-package-manifest.json"
DOI_PACKAGE_CHECKSUM = DIST / "doi-deposit-package-checksum.json"
ARCHIVE_MANIFEST = REPORTS / "archive-handoff-manifest.json"
SUBMISSION_READINESS = REPORTS / "submission-readiness.csv"
FINAL_READTHROUGH = REPORTS / "final-human-readthrough.md"
METADATA_OUT = DIST / "zenodo-deposit-metadata.json"
PREFLIGHT_CSV = REPORTS / "zenodo-deposit-preflight.csv"
PREFLIGHT_MD = REPORTS / "zenodo-deposit-preflight.md"
DRAFT_JSON = DIST / "zenodo-draft-response.json"
DRAFT_CSV = REPORTS / "zenodo-draft-deposit.csv"
DRAFT_MD = REPORTS / "zenodo-draft-deposit.md"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
DEFAULT_API_BASE = "https://sandbox.zenodo.org/api"
PRODUCTION_API_BASE = "https://zenodo.org/api"
ZENODO_DEVELOPERS_URL = "https://developers.zenodo.org/"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--create-draft",
        action="store_true",
        help="Create or update an unpublished Zenodo draft deposit. Requires ZENODO_ACCESS_TOKEN.",
    )
    parser.add_argument(
        "--upload-package",
        action="store_true",
        help="Upload dist/lobby-capture-doi-deposit-package.zip to the unpublished draft.",
    )
    args = parser.parse_args()

    metadata = zenodo_metadata()
    DIST.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    METADATA_OUT.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = preflight_rows(metadata)
    write_csv(PREFLIGHT_CSV, rows, ["gate", "status", "evidence", "nextAction"])
    PREFLIGHT_MD.write_text(preflight_markdown(metadata, rows), encoding="utf-8")
    print(f"Wrote {METADATA_OUT.relative_to(ROOT)}")
    print(f"Wrote {PREFLIGHT_CSV.relative_to(ROOT)}")
    print(f"Wrote {PREFLIGHT_MD.relative_to(ROOT)}")

    if args.upload_package and not args.create_draft:
        raise SystemExit("--upload-package requires --create-draft")
    if args.create_draft:
        draft_rows, response = create_or_update_draft(metadata, upload_package=args.upload_package)
        write_csv(DRAFT_CSV, draft_rows, ["step", "status", "evidence", "nextAction"])
        DRAFT_MD.write_text(draft_markdown(draft_rows, response), encoding="utf-8")
        DRAFT_JSON.write_text(json.dumps(response, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {DRAFT_CSV.relative_to(ROOT)}")
        print(f"Wrote {DRAFT_MD.relative_to(ROOT)}")
        print(f"Wrote {DRAFT_JSON.relative_to(ROOT)}")
        return 0 if all(row["status"] in {"ready", "manual_required"} for row in draft_rows) else 1

    return 0 if all(row["status"] != "blocked" for row in rows) else 1


def zenodo_metadata() -> dict[str, Any]:
    source = read_json(ZENODO)
    release_tag = release_tag_from_citation()
    metadata = {
        "title": source.get("title", ""),
        "upload_type": source.get("upload_type", "software"),
        "publication_date": source.get("publication_date", ""),
        "creators": source.get("creators", []),
        "description": source.get("description", ""),
        "license": zenodo_license_id(str(source.get("license", ""))),
        "keywords": source.get("keywords", []),
        "related_identifiers": source.get("related_identifiers", []),
        "notes": source.get("notes", ""),
        "access_right": "open",
        "version": release_tag,
    }
    if "communities" in source:
        metadata["communities"] = source["communities"]
    return {"metadata": metadata}


def zenodo_license_id(value: str) -> str:
    normalized = value.strip().lower()
    if normalized == "mit":
        return "mit-license"
    return value.strip()


def preflight_rows(metadata_payload: dict[str, Any]) -> list[dict[str, str]]:
    release_tag = release_tag_from_citation()
    metadata = metadata_payload.get("metadata", {})
    api_base = zenodo_api_base()
    token_present = bool(os.environ.get("ZENODO_ACCESS_TOKEN") or os.environ.get("ZENODO_API_TOKEN"))
    package_ready, package_evidence = doi_package_ready()
    manifest_ready, manifest_evidence = archive_manifest_ready(release_tag)
    submission_ready, submission_evidence = submission_boundary_ready()
    doi = recorded_doi()
    final_status = final_readthrough_status()
    metadata_ready = bool(metadata.get("title")) and bool(metadata.get("creators")) and metadata.get("version") == release_tag
    rows = [
        row(
            "metadata-json",
            "ready" if metadata_ready else "blocked",
            (
                f"title={'present' if metadata.get('title') else 'missing'}; "
                f"creators={len(metadata.get('creators', [])) if isinstance(metadata.get('creators'), list) else 0}; "
                f"version={metadata.get('version', '')}; expected={release_tag}; "
                f"license={metadata.get('license', '')}"
            ),
            "Keep .zenodo.json and CITATION.cff synchronized before DOI deposit.",
        ),
        row(
            "api-target",
            "ready" if api_base.startswith(("https://sandbox.zenodo.org/api", "https://zenodo.org/api")) else "blocked",
            f"apiBase={api_base}; docs={ZENODO_DEVELOPERS_URL}",
            "Use sandbox for rehearsal; switch to https://zenodo.org/api only for the final DOI draft.",
        ),
        row(
            "token",
            "manual_required" if not token_present else "ready",
            "ZENODO_ACCESS_TOKEN=" + ("present" if token_present else "missing"),
            "Set ZENODO_ACCESS_TOKEN in .env only when creating an unpublished draft deposit.",
        ),
        row(
            "doi-package",
            "ready" if package_ready else "blocked",
            package_evidence,
            "Run make doi-deposit-package before a Zenodo upload.",
        ),
        row(
            "archive-manifest",
            "ready" if manifest_ready else "blocked",
            manifest_evidence,
            "Regenerate the archive handoff manifest before a DOI upload.",
        ),
        row(
            "claim-boundary",
            "ready" if submission_ready else "blocked",
            submission_evidence,
            "Keep the Zenodo description bounded to mechanism-model review until calibrated policy gates clear.",
        ),
        row(
            "doi-record",
            "manual_required" if not doi else "ready",
            f"DOI={'not recorded yet' if not doi else doi}",
            "After Zenodo reserves or mints a DOI, record it in CITATION.cff, .zenodo.json, the paper declarations, and final-human-readthrough.md.",
        ),
        row(
            "human-readthrough",
            "manual_required" if final_status != "complete" else "ready",
            f"final-human-readthrough status={final_status or 'missing'}",
            "Do not publish the Zenodo record as the final journal submission archive until the human read-through is signed off.",
        ),
    ]
    return rows


def create_or_update_draft(
    metadata_payload: dict[str, Any],
    *,
    upload_package: bool,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    token = os.environ.get("ZENODO_ACCESS_TOKEN") or os.environ.get("ZENODO_API_TOKEN")
    if not token:
        raise SystemExit("ZENODO_ACCESS_TOKEN is required for --create-draft")
    api_base = zenodo_api_base()
    draft_id = os.environ.get("ZENODO_DEPOSIT_ID", "").strip()
    rows: list[dict[str, str]] = []
    response: dict[str, Any]
    if draft_id:
        response = request_json(
            "GET",
            f"{api_base}/deposit/depositions/{urllib.parse.quote(draft_id)}",
            token=token,
        )
        rows.append(row("load-draft", "ready", f"draft id={draft_id}", "Update metadata on the existing unpublished draft."))
    else:
        response = request_json("POST", f"{api_base}/deposit/depositions", token=token, payload={})
        draft_id = str(response.get("id", ""))
        rows.append(row("create-draft", "ready" if draft_id else "blocked", f"draft id={draft_id or 'missing'}", "Review the unpublished draft in Zenodo."))
    response = request_json(
        "PUT",
        f"{api_base}/deposit/depositions/{urllib.parse.quote(draft_id)}",
        token=token,
        payload=metadata_payload,
    )
    rows.append(
        row(
            "metadata",
            "ready",
            f"title={response.get('metadata', {}).get('title', '')}; draft id={draft_id}",
            "Do not publish until DOI, read-through, and live journal author-page fields are complete.",
        )
    )
    if upload_package:
        bucket = str(response.get("links", {}).get("bucket", ""))
        if not bucket:
            rows.append(row("upload-package", "blocked", "bucket link=missing", "Create a fresh draft or inspect the Zenodo response."))
        else:
            upload_response = upload_file(
                bucket,
                DOI_PACKAGE,
                token=token,
            )
            checksum = hashlib.sha256(DOI_PACKAGE.read_bytes()).hexdigest() if DOI_PACKAGE.exists() else ""
            rows.append(
                row(
                    "upload-package",
                    "ready",
                    f"file={DOI_PACKAGE.name}; bytes={DOI_PACKAGE.stat().st_size}; sha256={checksum}; responseKey={upload_response.get('key', '')}",
                    "Verify the uploaded file and metadata in Zenodo before publishing.",
                )
            )
            response["uploadedPackage"] = upload_response
    else:
        rows.append(
            row(
                "upload-package",
                "manual_required",
                "not requested",
                "Run make zenodo-deposit-upload after inspecting the draft if direct-package upload is desired.",
            )
        )
    rows.append(
        row(
            "publish",
            "manual_required",
            "not performed by this script",
            "Publish only after DOI metadata is reviewed, human read-through is signed, and live author-page instructions are clear.",
        )
    )
    return rows, response


def request_json(
    method: str,
    url: str,
    *,
    token: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    separator = "&" if "?" in url else "?"
    url_with_token = f"{url}{separator}access_token={urllib.parse.quote(token)}"
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url_with_token, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Zenodo API {method} {url} failed: HTTP {error.code}: {body}")
    except urllib.error.URLError as error:
        raise SystemExit(f"Zenodo API {method} {url} failed: {error}") from error
    return json.loads(body) if body.strip() else {}


def upload_file(bucket_url: str, path: Path, *, token: str) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing upload package: {path.relative_to(ROOT)}")
    filename = urllib.parse.quote(path.name)
    separator = "&" if "?" in bucket_url else "?"
    url = f"{bucket_url.rstrip('/')}/{filename}{separator}access_token={urllib.parse.quote(token)}"
    headers = {"Content-Type": "application/zip", "Accept": "application/json"}
    request = urllib.request.Request(
        url,
        data=path.read_bytes(),
        headers=headers,
        method="PUT",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Zenodo file upload failed: HTTP {error.code}: {body}")
    except urllib.error.URLError as error:
        raise SystemExit(f"Zenodo file upload failed: {error}") from error
    return json.loads(body) if body.strip() else {}


def zenodo_api_base() -> str:
    value = os.environ.get("ZENODO_API_BASE", "").strip()
    if value:
        return value.rstrip("/")
    if truthy(os.environ.get("ZENODO_USE_PRODUCTION", "")):
        return PRODUCTION_API_BASE
    return DEFAULT_API_BASE


def doi_package_ready() -> tuple[bool, str]:
    if not DOI_PACKAGE.exists():
        return False, "package=missing"
    if not DOI_PACKAGE_MANIFEST.exists() or not DOI_PACKAGE_CHECKSUM.exists():
        return False, "manifest/checksum=missing"
    checksum = read_json(DOI_PACKAGE_CHECKSUM)
    row_data = checksum.get("row", {}) if isinstance(checksum, dict) else {}
    if not isinstance(row_data, dict):
        return False, "checksum row=missing"
    data = DOI_PACKAGE.read_bytes()
    size = len(data)
    sha = hashlib.sha256(data).hexdigest()
    ready = row_data.get("bytes") == str(size) and row_data.get("sha256") == sha
    return (
        ready,
        f"package=present; bytes={size}; checksum={'ok' if ready else 'mismatch'}",
    )


def archive_manifest_ready(release_tag: str) -> tuple[bool, str]:
    manifest = read_json(ARCHIVE_MANIFEST)
    if not manifest:
        return False, "archive handoff manifest=missing"
    return (
        manifest.get("releaseTag") == release_tag,
        f"releaseTag={manifest.get('releaseTag', 'missing')}; expected={release_tag}",
    )


def submission_boundary_ready() -> tuple[bool, str]:
    rows = {item.get("gate", ""): item for item in read_csv(SUBMISSION_READINESS)}
    posture = rows.get("overall-submission-posture", {}).get("status", "")
    policy = rows.get("policy-language-audit", {}).get("status", "")
    return (
        posture == "ready_for_mechanism_review" and policy == "ready",
        f"overall={posture or 'missing'}; policy-language={policy or 'missing'}",
    )


def recorded_doi() -> str:
    for path in (CITATION, ZENODO, ROOT / "paper" / "sections" / "submission-declarations.tex", FINAL_READTHROUGH):
        match = DOI_PATTERN.search(read_text(path))
        if match:
            return match.group(0)
    return ""


def final_readthrough_status() -> str:
    text = read_text(FINAL_READTHROUGH)
    match = re.search(r"^status:\s*(.*?)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip().lower() if match else ""


def release_tag_from_citation() -> str:
    match = VERSION_PATTERN.search(read_text(CITATION))
    if not match:
        raise SystemExit("Could not find version in CITATION.cff")
    return match.group(1).strip()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def row(name: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "gate": name,
        "step": name,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for item in rows:
            writer.writerow({field: item.get(field, "") for field in fieldnames})


def preflight_markdown(metadata_payload: dict[str, Any], rows: list[dict[str, str]]) -> str:
    ready = sum(1 for item in rows if item["status"] == "ready")
    manual = sum(1 for item in rows if item["status"] == "manual_required")
    blocked = sum(1 for item in rows if item["status"] == "blocked")
    metadata = metadata_payload.get("metadata", {})
    lines = [
        "# Zenodo Deposit Preflight",
        "",
        "This report prepares the Zenodo DOI deposit payload for the release. It is an offline preflight by default and does not assert that a DOI has been minted.",
        "",
        "## Summary",
        "",
        f"- Title: `{md(metadata.get('title', ''))}`",
        f"- Version: `{md(metadata.get('version', ''))}`",
        f"- Metadata file: `{METADATA_OUT.relative_to(ROOT)}`",
        f"- Zenodo API target: `{zenodo_api_base()}`",
        f"- Official API documentation: {ZENODO_DEVELOPERS_URL}",
        f"- Ready gates: `{ready}`",
        f"- Manual-required gates: `{manual}`",
        f"- Blocked gates: `{blocked}`",
        "",
        "## Gate Matrix",
        "",
        "| Gate | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {gate} | {status} | {evidence} | {nextAction} |".format(
                gate=md(item["gate"]),
                status=md(item["status"]),
                evidence=md(item["evidence"]),
                nextAction=md(item["nextAction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Networked Draft Workflow",
            "",
            "The safe default target only writes local metadata and this preflight report. To create an unpublished Zenodo draft, set `ZENODO_ACCESS_TOKEN` in `.env` and run `make zenodo-deposit-draft`. To upload the DOI deposit package to that unpublished draft, run `make zenodo-deposit-upload`. This workflow does not publish the Zenodo record.",
            "",
        ]
    )
    return "\n".join(lines)


def draft_markdown(rows: list[dict[str, str]], response: dict[str, Any]) -> str:
    lines = [
        "# Zenodo Draft Deposit",
        "",
        "This report records an unpublished Zenodo draft-deposit action. It does not assert that a DOI has been minted or that the record has been published.",
        "",
        "## Summary",
        "",
        f"- Draft ID: `{md(response.get('id', ''))}`",
        f"- Concept record ID: `{md(response.get('conceptrecid', ''))}`",
        f"- Record URL: {response.get('links', {}).get('html', '') if isinstance(response.get('links'), dict) else ''}",
        f"- DOI: `{md(response.get('metadata', {}).get('doi', '') if isinstance(response.get('metadata'), dict) else '')}`",
        "",
        "## Steps",
        "",
        "| Step | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {step} | {status} | {evidence} | {nextAction} |".format(
                step=md(item["step"]),
                status=md(item["status"]),
                evidence=md(item["evidence"]),
                nextAction=md(item["nextAction"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
