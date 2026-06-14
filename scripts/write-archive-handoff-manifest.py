#!/usr/bin/env python3
"""Write DOI archive handoff manifests.

The tracked report records the intended release asset set and stable checksums
for tracked metadata. Local PDF and ZIP byte streams can differ across TeX and
ZIP implementations, so their release-upload checksums are written under dist/
instead of into tracked report files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"
FIXED_GENERATED_AT = "2026-05-05T00:00:00Z"
SCHEMA = "lobby-capture-archive-handoff-manifest-v1"
CHECKSUM_SCHEMA = "lobby-capture-release-asset-checksums-v1"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
TRACKED_SOURCE_STATUS = "tracked-source-verified"
RELEASE_ASSET_DIST_STATUS = "release-asset-checksum-recorded-in-dist"
LOCAL_CHECKSUM_STATUS = "local-release-asset-sha256"

ASSETS = [
    {
        "path": "dist/lobby-capture-wiley-submission.zip",
        "releaseAssetName": "lobby-capture-wiley-submission.zip",
        "role": "wiley-submission-archive",
        "includeInDoiDeposit": "yes",
        "checksumMode": "release-asset",
        "archiveNote": "Primary journal submission archive with manuscript source, compiled PDFs, supporting information, generated reports, and package-member checksum manifest.",
    },
    {
        "path": "paper/regulation-governance-wiley.pdf",
        "releaseAssetName": "regulation-governance-wiley.pdf",
        "role": "wiley-rendered-manuscript",
        "includeInDoiDeposit": "yes",
        "checksumMode": "release-asset",
        "archiveNote": "Wiley-template rendered manuscript PDF for review.",
    },
    {
        "path": "paper/strategic-channel-substitution-regulatory-capture.pdf",
        "releaseAssetName": "strategic-channel-substitution-regulatory-capture.pdf",
        "role": "local-rendered-manuscript",
        "includeInDoiDeposit": "yes",
        "checksumMode": "release-asset",
        "archiveNote": "Local rendered manuscript PDF with the descriptive project filename.",
    },
    {
        "path": "paper/supplement.pdf",
        "releaseAssetName": "supplement.pdf",
        "role": "supporting-information-pdf",
        "includeInDoiDeposit": "yes",
        "checksumMode": "release-asset",
        "archiveNote": "Rendered supporting-information PDF.",
    },
    {
        "path": "CITATION.cff",
        "releaseAssetName": "",
        "role": "citation-metadata",
        "includeInDoiDeposit": "source-archive",
        "checksumMode": "tracked-source",
        "archiveNote": "Machine-readable citation metadata included in the tagged source archive and Wiley submission archive.",
    },
    {
        "path": ".zenodo.json",
        "releaseAssetName": "",
        "role": "doi-deposit-metadata",
        "includeInDoiDeposit": "source-archive",
        "checksumMode": "tracked-source",
        "archiveNote": "Zenodo-compatible metadata included in the tagged source archive and Wiley submission archive.",
    },
    {
        "path": "reports/submission-readiness.md",
        "releaseAssetName": "",
        "role": "submission-readiness-audit",
        "includeInDoiDeposit": "source-archive",
        "checksumMode": "tracked-source",
        "archiveNote": "Generated gate summary distinguishing mechanism-review readiness from DOI and human signoff.",
    },
    {
        "path": "reports/final-human-readthrough.md",
        "releaseAssetName": "",
        "role": "manual-signoff-record",
        "includeInDoiDeposit": "source-archive",
        "checksumMode": "tracked-source",
        "archiveNote": "Manual final-submission read-through checklist; remains pending until signed for the release.",
    },
]


def main() -> int:
    release_tag = release_tag_from_citation(ROOT / "CITATION.cff")
    checksum_rows = manifest_rows()
    rows = tracked_handoff_rows(checksum_rows)
    manifest = {
        "schema": SCHEMA,
        "releaseTag": release_tag,
        "releaseUrl": f"https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{release_tag}",
        "generatedAt": FIXED_GENERATED_AT,
        "primaryReleaseAssets": [
            row["releaseAssetName"]
            for row in rows
            if row["includeInDoiDeposit"] == "yes" and row["releaseAssetName"]
        ],
        "selfOmission": (
            "The archive-handoff manifest files are attached as release aids but are "
            "not checksum rows because they describe the package and release assets."
        ),
        "releaseAssetChecksumLocation": "dist/release-asset-checksums.{csv,json,md}",
        "rows": rows,
    }
    checksum_manifest = {
        "schema": CHECKSUM_SCHEMA,
        "releaseTag": release_tag,
        "releaseUrl": manifest["releaseUrl"],
        "generatedAt": FIXED_GENERATED_AT,
        "rows": checksum_rows,
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "archive-handoff-manifest.csv", rows)
    (REPORTS / "archive-handoff-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPORTS / "archive-handoff-manifest.md").write_text(markdown(manifest), encoding="utf-8")
    print("Wrote reports/archive-handoff-manifest.csv")
    print("Wrote reports/archive-handoff-manifest.json")
    print("Wrote reports/archive-handoff-manifest.md")
    DIST.mkdir(parents=True, exist_ok=True)
    write_csv(DIST / "release-asset-checksums.csv", checksum_rows)
    (DIST / "release-asset-checksums.json").write_text(
        json.dumps(checksum_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (DIST / "release-asset-checksums.md").write_text(
        checksum_markdown(checksum_manifest),
        encoding="utf-8",
    )
    print("Wrote dist/release-asset-checksums.csv")
    print("Wrote dist/release-asset-checksums.json")
    print("Wrote dist/release-asset-checksums.md")
    return 0


def release_tag_from_citation(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(text)
    if not match:
        raise SystemExit(f"Could not find release tag in {path.relative_to(ROOT)}")
    return match.group(1).strip()


def manifest_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for definition in ASSETS:
        path = ROOT / definition["path"]
        if not path.exists():
            raise SystemExit(f"Missing archive handoff input: {definition['path']}")
        data = path.read_bytes()
        row_definition = {
            key: value
            for key, value in definition.items()
            if key != "checksumMode"
        }
        checksum_status = (
            LOCAL_CHECKSUM_STATUS
            if definition["checksumMode"] == "release-asset"
            else TRACKED_SOURCE_STATUS
        )
        rows.append(
            {
                **row_definition,
                "checksumStatus": checksum_status,
                "bytes": str(len(data)),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return rows


def tracked_handoff_rows(checksum_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for checksum_row in checksum_rows:
        row = dict(checksum_row)
        if row["includeInDoiDeposit"] == "yes":
            row["checksumStatus"] = RELEASE_ASSET_DIST_STATUS
            row["bytes"] = "see-dist-release-asset-checksums"
            row["sha256"] = "see-dist-release-asset-checksums"
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "path",
        "releaseAssetName",
        "role",
        "includeInDoiDeposit",
        "checksumStatus",
        "bytes",
        "sha256",
        "archiveNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(manifest: dict[str, object]) -> str:
    rows = manifest["rows"]
    assert isinstance(rows, list)
    lines = [
        "# Archive Handoff Manifest",
        "",
        "This report records the release asset set and stable source-metadata checksums that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.",
        "",
        "PDF and ZIP byte streams can differ across TeX and archive implementations. The release-machine checksums for those binary assets are written to `dist/release-asset-checksums.{csv,json,md}` and should be attached to the GitHub release or DOI deposit record.",
        "",
        "## Summary",
        "",
        f"- Schema: `{manifest['schema']}`",
        f"- Release tag: `{manifest['releaseTag']}`",
        f"- Release URL: {manifest['releaseUrl']}",
        f"- Generated at: `{manifest['generatedAt']}`",
        "- DOI status: not asserted by this manifest",
        f"- Release asset checksum file: `{manifest['releaseAssetChecksumLocation']}`",
        "- Self-omission: archive-handoff manifest files are release aids and are not checksum rows.",
        "",
        "## Primary Release Assets",
        "",
    ]
    for asset in manifest["primaryReleaseAssets"]:
        lines.append(f"- `{asset}`")
    lines.extend(
        [
            "",
            "## Checksums",
            "",
            "| Path | Release asset | Role | DOI deposit | Checksum status | Bytes | SHA-256 |",
            "| --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            "| {path} | {releaseAssetName} | {role} | {includeInDoiDeposit} | {checksumStatus} | {bytes} | `{sha256}` |".format(
                path=row["path"],
                releaseAssetName=row["releaseAssetName"] or "-",
                role=row["role"],
                includeInDoiDeposit=row["includeInDoiDeposit"],
                checksumStatus=row["checksumStatus"],
                bytes=row["bytes"],
                sha256=row["sha256"],
            )
        )
    lines.extend(
        [
            "",
            "## Archive Use",
            "",
            "When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved the selected assets. Attach or retain `dist/release-asset-checksums.{csv,json,md}` from the release machine for byte-level PDF and ZIP verification. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record can be tied back to the exact claim boundary and manual signoff state.",
            "",
        ]
    )
    return "\n".join(lines)


def checksum_markdown(manifest: dict[str, object]) -> str:
    rows = manifest["rows"]
    assert isinstance(rows, list)
    lines = [
        "# Local Release Asset Checksums",
        "",
        "This ignored file records byte-level checksums from the release-building machine. It complements the tracked archive handoff manifest, whose PDF and ZIP rows deliberately avoid environment-specific hashes.",
        "",
        "## Summary",
        "",
        f"- Schema: `{manifest['schema']}`",
        f"- Release tag: `{manifest['releaseTag']}`",
        f"- Release URL: {manifest['releaseUrl']}",
        f"- Generated at: `{manifest['generatedAt']}`",
        "",
        "## SHA-256 Checksums",
        "",
        "| Path | Release asset | Role | Checksum status | Bytes | SHA-256 |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            "| {path} | {releaseAssetName} | {role} | {checksumStatus} | {bytes} | `{sha256}` |".format(
                path=row["path"],
                releaseAssetName=row["releaseAssetName"] or "-",
                role=row["role"],
                checksumStatus=row["checksumStatus"],
                bytes=row["bytes"],
                sha256=row["sha256"],
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
