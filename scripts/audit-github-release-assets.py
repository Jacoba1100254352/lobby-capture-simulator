#!/usr/bin/env python3
"""Verify uploaded GitHub release assets against local release manifests.

This is intentionally a post-release, networked audit. The normal paper build
must stay offline-reproducible, while DOI handoff benefits from an explicit
record that the GitHub release assets match the local release-machine checksums.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
CITATION = ROOT / "CITATION.cff"
RELEASE_CHECKSUM_CSV = DIST / "release-asset-checksums.csv"
DOI_PACKAGE_CHECKSUM_CSV = DIST / "doi-deposit-package-checksum.csv"
RELEASE_AID_PATHS = [
    "dist/release-asset-checksums.csv",
    "dist/release-asset-checksums.json",
    "dist/release-asset-checksums.md",
    "dist/doi-deposit-package-manifest.json",
    "dist/doi-deposit-package-manifest.md",
    "dist/doi-deposit-package-checksum.csv",
    "dist/doi-deposit-package-checksum.json",
    "dist/doi-deposit-package-checksum.md",
    "reports/archive-handoff-manifest.csv",
    "reports/archive-handoff-manifest.json",
    "reports/archive-handoff-manifest.md",
    "reports/doi-deposit-readiness.csv",
    "reports/doi-deposit-readiness.md",
    "reports/final-human-readthrough.md",
    "reports/reggov-guidelines-readiness.csv",
    "reports/reggov-guidelines-readiness.md",
    "reports/submission-readiness.csv",
    "reports/submission-readiness.md",
    "reports/wiley-submission-form-readiness.csv",
    "reports/wiley-submission-form-readiness.md",
]


def main() -> int:
    release_tag = release_tag_from_citation()
    expected = expected_assets()
    release, gh_error = github_release(release_tag)
    rows = audit_rows(expected, release, gh_error)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "github-release-asset-audit.csv", rows)
    (REPORTS / "github-release-asset-audit.md").write_text(
        markdown(release_tag, release, gh_error, rows),
        encoding="utf-8",
    )
    print("Wrote reports/github-release-asset-audit.csv")
    print("Wrote reports/github-release-asset-audit.md")
    if gh_error:
        print(gh_error, file=sys.stderr)
        return 2
    return 0 if all(row["status"] == "verified" for row in rows) else 1


def release_tag_from_citation() -> str:
    for line in CITATION.read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    raise SystemExit("Could not find version in CITATION.cff")


def expected_assets() -> dict[str, dict[str, str]]:
    assets: dict[str, dict[str, str]] = {}
    for row in read_csv(RELEASE_CHECKSUM_CSV):
        name = row.get("releaseAssetName", "")
        if name:
            assets[name] = {
                "sourcePath": row["path"],
                "expectedBytes": row["bytes"],
                "expectedSha256": row["sha256"],
                "role": row["role"],
            }
    for row in read_csv(DOI_PACKAGE_CHECKSUM_CSV):
        name = row.get("releaseAssetName", "")
        if name:
            assets[name] = {
                "sourcePath": row["path"],
                "expectedBytes": row["bytes"],
                "expectedSha256": row["sha256"],
                "role": row["role"],
            }
    for relative in RELEASE_AID_PATHS:
        path = ROOT / relative
        data = path.read_bytes()
        assets[path.name] = {
            "sourcePath": relative,
            "expectedBytes": str(len(data)),
            "expectedSha256": hashlib.sha256(data).hexdigest(),
            "role": "release-aid",
        }
    return assets


def github_release(release_tag: str) -> tuple[dict[str, object], str]:
    try:
        output = subprocess.check_output(
            [
                "gh",
                "release",
                "view",
                release_tag,
                "--json",
                "url,isDraft,isPrerelease,assets",
            ],
            cwd=ROOT,
            text=True,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        stderr = getattr(error, "stderr", "") or str(error)
        return {}, "could not query GitHub release with gh: " + stderr.strip()
    try:
        data = json.loads(output)
    except json.JSONDecodeError as error:
        return {}, f"could not parse gh release JSON: {error}"
    return data if isinstance(data, dict) else {}, ""


def audit_rows(
    expected: dict[str, dict[str, str]],
    release: dict[str, object],
    gh_error: str,
) -> list[dict[str, str]]:
    uploaded = {}
    for asset in release.get("assets", []) if isinstance(release, dict) else []:
        if isinstance(asset, dict) and asset.get("name"):
            uploaded[str(asset["name"])] = asset
    names = sorted(set(expected) | set(uploaded))
    rows: list[dict[str, str]] = []
    for name in names:
        exp = expected.get(name, {})
        got = uploaded.get(name, {})
        expected_sha = exp.get("expectedSha256", "")
        digest = str(got.get("digest", ""))
        uploaded_sha = digest.removeprefix("sha256:") if digest.startswith("sha256:") else digest
        expected_bytes = exp.get("expectedBytes", "")
        uploaded_bytes = str(got.get("size", "")) if got else ""
        if gh_error:
            status = "not_checked"
        elif not exp:
            status = "unexpected_upload"
        elif not got:
            status = "missing_upload"
        elif expected_sha != uploaded_sha:
            status = "sha256_mismatch"
        elif expected_bytes != uploaded_bytes:
            status = "size_mismatch"
        else:
            status = "verified"
        rows.append(
            {
                "asset": name,
                "status": status,
                "sourcePath": exp.get("sourcePath", ""),
                "role": exp.get("role", ""),
                "expectedBytes": expected_bytes,
                "uploadedBytes": uploaded_bytes,
                "expectedSha256": expected_sha,
                "uploadedSha256": uploaded_sha,
                "url": str(got.get("url", "")) if got else "",
            }
        )
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "asset",
        "status",
        "sourcePath",
        "role",
        "expectedBytes",
        "uploadedBytes",
        "expectedSha256",
        "uploadedSha256",
        "url",
    ]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(
    release_tag: str,
    release: dict[str, object],
    gh_error: str,
    rows: list[dict[str, str]],
) -> str:
    counts = {status: 0 for status in sorted({row["status"] for row in rows})}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    all_verified = rows and all(row["status"] == "verified" for row in rows)
    lines = [
        "# GitHub Release Asset Audit",
        "",
        "This post-release audit compares assets uploaded to the GitHub release against local release-machine checksum manifests. It is intentionally separate from the offline paper build and does not assert that a DOI has been minted.",
        "",
        "## Summary",
        "",
        f"- Release tag: `{release_tag}`",
        f"- Release URL: {release.get('url', '') if release else ''}",
        f"- GitHub query status: `{'error' if gh_error else 'ok'}`",
        f"- Overall status: `{'verified' if all_verified else 'check_required'}`",
        f"- Draft release: `{release.get('isDraft', 'unknown') if release else 'unknown'}`",
        f"- Prerelease: `{release.get('isPrerelease', 'unknown') if release else 'unknown'}`",
    ]
    if gh_error:
        lines.append(f"- Query error: `{md(gh_error)}`")
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: `{count}`")
    lines.extend(
        [
            "",
            "## Asset Matrix",
            "",
            "| Asset | Status | Role | Expected bytes | Uploaded bytes | Expected SHA-256 | Uploaded SHA-256 |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {asset} | {status} | {role} | {expectedBytes} | {uploadedBytes} | `{expectedSha256}` | `{uploadedSha256}` |".format(
                asset=md(row["asset"]),
                status=md(row["status"]),
                role=md(row["role"]),
                expectedBytes=md(row["expectedBytes"]),
                uploadedBytes=md(row["uploadedBytes"]),
                expectedSha256=md(row["expectedSha256"]),
                uploadedSha256=md(row["uploadedSha256"]),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Run this audit after creating or updating a GitHub release and before copying checksums into a DOI deposit record. The tracked DOI readiness report remains the source for claim-boundary and manual-signoff status.",
            "",
        ]
    )
    return "\n".join(lines)


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
