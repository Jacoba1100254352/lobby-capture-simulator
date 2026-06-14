#!/usr/bin/env python3
"""Write a DOI deposit readiness audit without asserting that a DOI exists."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"
CITATION = ROOT / "CITATION.cff"
ZENODO = ROOT / ".zenodo.json"
DECLARATIONS = ROOT / "paper" / "sections" / "submission-declarations.tex"
ARCHIVE_MANIFEST = REPORTS / "archive-handoff-manifest.json"
SUBMISSION_READINESS = REPORTS / "submission-readiness.csv"
FINAL_READTHROUGH = REPORTS / "final-human-readthrough.md"
CHECKSUM_CSV = DIST / "release-asset-checksums.csv"
CHECKSUM_JSON = DIST / "release-asset-checksums.json"
CHECKSUM_MD = DIST / "release-asset-checksums.md"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
EXPECTED_PRIMARY_ASSETS = {
    "lobby-capture-wiley-submission.zip",
    "regulation-governance-wiley.pdf",
    "strategic-channel-substitution-regulatory-capture.pdf",
    "supplement.pdf",
}


def main() -> int:
    release_tag = release_tag_from_citation()
    rows = readiness_rows(release_tag)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "doi-deposit-readiness.csv", rows)
    (REPORTS / "doi-deposit-readiness.md").write_text(
        markdown(release_tag, rows),
        encoding="utf-8",
    )
    print("Wrote reports/doi-deposit-readiness.csv")
    print("Wrote reports/doi-deposit-readiness.md")
    return 0


def readiness_rows(release_tag: str) -> list[dict[str, str]]:
    manifest = read_json(ARCHIVE_MANIFEST)
    checksum_rows = read_csv(CHECKSUM_CSV)
    submission = keyed_rows(SUBMISSION_READINESS, "gate")
    final_readthrough = read_text(FINAL_READTHROUGH)
    doi = find_doi()
    human_signoff = human_readthrough_complete(final_readthrough, release_tag)
    primary_assets = set(manifest.get("primaryReleaseAssets", [])) if isinstance(manifest, dict) else set()
    checksum_assets = {
        row.get("releaseAssetName", "")
        for row in checksum_rows
        if row.get("includeInDoiDeposit") == "yes"
    }
    checksum_files_present = all(path.exists() for path in (CHECKSUM_CSV, CHECKSUM_JSON, CHECKSUM_MD))
    checksum_rows_complete = bool(checksum_rows) and all(
        row.get("sha256") and row.get("bytes") and row.get("checksumStatus")
        for row in checksum_rows
    )
    metadata_ok = release_metadata_ok(release_tag)
    submission_ok = submission.get("overall-submission-posture", {}).get("status") == "ready_for_mechanism_review"
    final_gate_status = submission.get("final-journal-submission", {}).get("status", "")

    rows = [
        row(
            "release-metadata",
            "ready" if metadata_ok else "blocked",
            metadata_evidence(release_tag),
            "Use these metadata as the deposit record source.",
        ),
        row(
            "primary-release-assets",
            "ready" if primary_assets == EXPECTED_PRIMARY_ASSETS else "blocked",
            (
                f"manifest assets={len(primary_assets)}; "
                f"expected assets={len(EXPECTED_PRIMARY_ASSETS)}"
            ),
            "Deposit the primary assets listed in the archive handoff manifest.",
        ),
        row(
            "release-asset-checksums",
            "ready" if checksum_files_present and checksum_rows_complete and checksum_assets == EXPECTED_PRIMARY_ASSETS else "blocked",
            (
                f"checksum files={'present' if checksum_files_present else 'missing'}; "
                f"checksum asset rows={len(checksum_assets)}"
            ),
            "Attach or retain dist/release-asset-checksums.* with the DOI record.",
        ),
        row(
            "claim-boundary",
            "ready" if submission_ok else "blocked",
            f"overall submission posture={submission.get('overall-submission-posture', {}).get('status', 'missing')}",
            "Keep the DOI record description bounded to mechanism-model review unless policy-calibration gates later clear.",
        ),
        row(
            "doi-record",
            "ready" if doi else "manual_required",
            f"DOI={'present: ' + doi if doi else 'not recorded in citation, deposit metadata, or declarations'}",
            "After minting a Zenodo, OSF, or journal-linked archive DOI, record it in CITATION.cff, .zenodo.json, submission declarations, and the final read-through record.",
        ),
        row(
            "human-readthrough",
            "ready" if human_signoff else "manual_required",
            human_readthrough_evidence(final_readthrough, release_tag),
            "Complete the final human scholarly read-through against the exact release tag before final journal submission.",
        ),
        row(
            "final-journal-submission",
            "ready" if doi and human_signoff and final_gate_status == "ready" else "manual_required",
            (
                f"submission final gate={final_gate_status or 'missing'}; "
                f"doi={'present' if doi else 'missing'}; "
                f"human signoff={'complete' if human_signoff else 'pending'}"
            ),
            "Do not treat the bundle as final-journal-submission ready until DOI and human signoff are both recorded.",
        ),
    ]
    return rows


def release_metadata_ok(release_tag: str) -> bool:
    citation = read_text(CITATION)
    zenodo = read_json(ZENODO)
    if f'version: "{release_tag}"' not in citation:
        return False
    if f"/releases/tag/{release_tag}" not in citation:
        return False
    if not isinstance(zenodo, dict):
        return False
    related = zenodo.get("related_identifiers", [])
    return any(
        isinstance(item, dict)
        and item.get("identifier")
        == f"https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{release_tag}"
        for item in related
    )


def metadata_evidence(release_tag: str) -> str:
    zenodo = read_json(ZENODO)
    related = zenodo.get("related_identifiers", []) if isinstance(zenodo, dict) else []
    has_release = any(
        isinstance(item, dict) and item.get("identifier", "").endswith(f"/{release_tag}")
        for item in related
    )
    return (
        f"CITATION release={release_tag_from_citation() or 'missing'}; "
        f"Zenodo related release={'present' if has_release else 'missing'}"
    )


def human_readthrough_complete(text: str, release_tag: str) -> bool:
    return (
        field_value(text, "status").lower() == "complete"
        and bool(field_value(text, "signed-off-by"))
        and bool(field_value(text, "signed-off-date"))
        and bool(field_value(text, "reviewed-commit"))
        and field_value(text, "reviewed-release") == release_tag
    )


def human_readthrough_evidence(text: str, release_tag: str) -> str:
    status = field_value(text, "status") or "missing"
    reviewed = field_value(text, "reviewed-release") or "missing"
    signer = "present" if field_value(text, "signed-off-by") else "missing"
    date = "present" if field_value(text, "signed-off-date") else "missing"
    commit = "present" if field_value(text, "reviewed-commit") else "missing"
    return (
        f"status={status}; reviewed-release={reviewed}; expected-release={release_tag}; "
        f"signer={signer}; date={date}; commit={commit}"
    )


def find_doi() -> str:
    for path in (CITATION, ZENODO, DECLARATIONS, FINAL_READTHROUGH):
        match = DOI_PATTERN.search(read_text(path))
        if match:
            return match.group(0)
    return ""


def release_tag_from_citation() -> str:
    match = VERSION_PATTERN.search(read_text(CITATION))
    return match.group(1).strip() if match else ""


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path)}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def field_value(text: str, field_name: str) -> str:
    match = re.search(
        rf"^[^\S\n]*{re.escape(field_name)}[^\S\n]*:[^\S\n]*(.*?)[^\S\n]*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def row(gate: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=["gate", "status", "evidence", "nextAction"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def markdown(release_tag: str, rows: list[dict[str, str]]) -> str:
    ready = sum(1 for row in rows if row["status"] == "ready")
    manual = sum(1 for row in rows if row["status"] == "manual_required")
    blocked = sum(1 for row in rows if row["status"] == "blocked")
    final_status = next(
        (row["status"] for row in rows if row["gate"] == "final-journal-submission"),
        "missing",
    )
    lines = [
        "# DOI Deposit Readiness",
        "",
        "This audit checks whether the release has the metadata, asset list, checksum handoff, and claim-boundary records needed for DOI deposition. It does not assert that a DOI has been minted.",
        "",
        "## Summary",
        "",
        f"- Release tag: `{release_tag}`",
        f"- Ready gates: `{ready}`",
        f"- Manual-required gates: `{manual}`",
        f"- Blocked gates: `{blocked}`",
        f"- Final journal-submission status: `{final_status}`",
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
    lines.extend([
        "",
        "## Deposit Asset Set",
        "",
        "Upload or preserve these primary release assets with the DOI record, using `dist/release-asset-checksums.{csv,json,md}` for byte-level verification:",
        "",
    ])
    for asset in sorted(EXPECTED_PRIMARY_ASSETS):
        lines.append(f"- `{asset}`")
    lines.extend([
        "",
        "The tagged source archive should also preserve `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record remains tied to the release claim boundary.",
        "",
    ])
    return "\n".join(lines)


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
