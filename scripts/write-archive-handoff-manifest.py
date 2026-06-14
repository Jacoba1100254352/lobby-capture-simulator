#!/usr/bin/env python3
"""Write the release-asset checksum manifest used for DOI archive handoff."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIXED_GENERATED_AT = "2026-05-05T00:00:00Z"
SCHEMA = "lobby-capture-archive-handoff-manifest-v1"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)

ASSETS = [
    {
        "path": "dist/lobby-capture-wiley-submission.zip",
        "releaseAssetName": "lobby-capture-wiley-submission.zip",
        "role": "wiley-submission-archive",
        "includeInDoiDeposit": "yes",
        "archiveNote": "Primary journal submission archive with manuscript source, compiled PDFs, supporting information, generated reports, and package-member checksum manifest.",
    },
    {
        "path": "paper/regulation-governance-wiley.pdf",
        "releaseAssetName": "regulation-governance-wiley.pdf",
        "role": "wiley-rendered-manuscript",
        "includeInDoiDeposit": "yes",
        "archiveNote": "Wiley-template rendered manuscript PDF for review.",
    },
    {
        "path": "paper/strategic-channel-substitution-regulatory-capture.pdf",
        "releaseAssetName": "strategic-channel-substitution-regulatory-capture.pdf",
        "role": "local-rendered-manuscript",
        "includeInDoiDeposit": "yes",
        "archiveNote": "Local rendered manuscript PDF with the descriptive project filename.",
    },
    {
        "path": "paper/supplement.pdf",
        "releaseAssetName": "supplement.pdf",
        "role": "supporting-information-pdf",
        "includeInDoiDeposit": "yes",
        "archiveNote": "Rendered supporting-information PDF.",
    },
    {
        "path": "CITATION.cff",
        "releaseAssetName": "",
        "role": "citation-metadata",
        "includeInDoiDeposit": "source-archive",
        "archiveNote": "Machine-readable citation metadata included in the tagged source archive and Wiley submission archive.",
    },
    {
        "path": ".zenodo.json",
        "releaseAssetName": "",
        "role": "doi-deposit-metadata",
        "includeInDoiDeposit": "source-archive",
        "archiveNote": "Zenodo-compatible metadata included in the tagged source archive and Wiley submission archive.",
    },
    {
        "path": "reports/submission-readiness.md",
        "releaseAssetName": "",
        "role": "submission-readiness-audit",
        "includeInDoiDeposit": "source-archive",
        "archiveNote": "Generated gate summary distinguishing mechanism-review readiness from DOI and human signoff.",
    },
    {
        "path": "reports/final-human-readthrough.md",
        "releaseAssetName": "",
        "role": "manual-signoff-record",
        "includeInDoiDeposit": "source-archive",
        "archiveNote": "Manual final-submission read-through checklist; remains pending until signed for the release.",
    },
]


def main() -> int:
    release_tag = release_tag_from_citation(ROOT / "CITATION.cff")
    rows = manifest_rows()
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
        "rows": rows,
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
        rows.append(
            {
                **definition,
                "bytes": str(len(data)),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "path",
        "releaseAssetName",
        "role",
        "includeInDoiDeposit",
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
        "This report records checksums for the release assets and metadata that should be used when minting a DOI archive. It is a handoff aid, not proof that a DOI has been minted.",
        "",
        "## Summary",
        "",
        f"- Schema: `{manifest['schema']}`",
        f"- Release tag: `{manifest['releaseTag']}`",
        f"- Release URL: {manifest['releaseUrl']}",
        f"- Generated at: `{manifest['generatedAt']}`",
        "- DOI status: not asserted by this manifest",
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
            "| Path | Release asset | Role | DOI deposit | Bytes | SHA-256 |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            "| {path} | {releaseAssetName} | {role} | {includeInDoiDeposit} | {bytes} | `{sha256}` |".format(
                path=row["path"],
                releaseAssetName=row["releaseAssetName"] or "-",
                role=row["role"],
                includeInDoiDeposit=row["includeInDoiDeposit"],
                bytes=row["bytes"],
                sha256=row["sha256"],
            )
        )
    lines.extend(
        [
            "",
            "## Archive Use",
            "",
            "When minting a DOI archive, upload the primary release assets listed above or verify that the repository-to-archive integration preserved byte-identical assets. Keep the source archive for the tagged release with `CITATION.cff`, `.zenodo.json`, `reports/submission-readiness.md`, and `reports/final-human-readthrough.md` so the DOI record can be tied back to the exact claim boundary and manual signoff state.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
