#!/usr/bin/env python3
"""Build a deterministic DOI-deposit handoff package.

The package is a convenience artifact for archive deposition. It bundles the
primary release assets plus the metadata and readiness reports needed to verify
the claim boundary. It does not assert that a DOI has been minted.
"""

from __future__ import annotations

import hashlib
import json
import re
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PACKAGE = DIST / "lobby-capture-doi-deposit-package.zip"
PACKAGE_MANIFEST_JSON = DIST / "doi-deposit-package-manifest.json"
PACKAGE_MANIFEST_MD = DIST / "doi-deposit-package-manifest.md"
PACKAGE_CHECKSUM_CSV = DIST / "doi-deposit-package-checksum.csv"
PACKAGE_CHECKSUM_JSON = DIST / "doi-deposit-package-checksum.json"
PACKAGE_CHECKSUM_MD = DIST / "doi-deposit-package-checksum.md"
SCHEMA = "lobby-capture-doi-deposit-package-v1"
CHECKSUM_SCHEMA = "lobby-capture-doi-deposit-package-checksum-v1"
FIXED_GENERATED_AT = "2026-05-05T00:00:00Z"
FIXED_ZIP_TIME = (2026, 5, 5, 0, 0, 0)
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class PackageInput:
    source: str
    member: str
    role: str


PACKAGE_INPUTS = [
    PackageInput(
        "dist/lobby-capture-wiley-submission.zip",
        "primary-assets/lobby-capture-wiley-submission.zip",
        "wiley-submission-archive",
    ),
    PackageInput(
        "paper/regulation-governance-wiley.pdf",
        "primary-assets/regulation-governance-wiley.pdf",
        "wiley-rendered-manuscript",
    ),
    PackageInput(
        "paper/strategic-channel-substitution-regulatory-capture.pdf",
        "primary-assets/strategic-channel-substitution-regulatory-capture.pdf",
        "local-rendered-manuscript",
    ),
    PackageInput(
        "paper/supplement.pdf",
        "primary-assets/supplement.pdf",
        "supporting-information-pdf",
    ),
    PackageInput("CITATION.cff", "metadata/CITATION.cff", "citation-metadata"),
    PackageInput(".zenodo.json", "metadata/zenodo.json", "doi-deposit-metadata"),
    PackageInput(
        "dist/release-asset-checksums.csv",
        "metadata/release-asset-checksums.csv",
        "release-asset-checksums",
    ),
    PackageInput(
        "dist/release-asset-checksums.json",
        "metadata/release-asset-checksums.json",
        "release-asset-checksums",
    ),
    PackageInput(
        "dist/release-asset-checksums.md",
        "metadata/release-asset-checksums.md",
        "release-asset-checksums",
    ),
    PackageInput(
        "reports/archive-handoff-manifest.csv",
        "readiness/archive-handoff-manifest.csv",
        "archive-handoff-manifest",
    ),
    PackageInput(
        "reports/archive-handoff-manifest.json",
        "readiness/archive-handoff-manifest.json",
        "archive-handoff-manifest",
    ),
    PackageInput(
        "reports/archive-handoff-manifest.md",
        "readiness/archive-handoff-manifest.md",
        "archive-handoff-manifest",
    ),
    PackageInput(
        "reports/submission-readiness.csv",
        "readiness/submission-readiness.csv",
        "submission-readiness-audit",
    ),
    PackageInput(
        "reports/submission-readiness.md",
        "readiness/submission-readiness.md",
        "submission-readiness-audit",
    ),
    PackageInput(
        "reports/wiley-submission-form-readiness.csv",
        "readiness/wiley-submission-form-readiness.csv",
        "wiley-submission-form-readiness",
    ),
    PackageInput(
        "reports/wiley-submission-form-readiness.md",
        "readiness/wiley-submission-form-readiness.md",
        "wiley-submission-form-readiness",
    ),
    PackageInput(
        "reports/reggov-guidelines-readiness.csv",
        "readiness/reggov-guidelines-readiness.csv",
        "reggov-guidelines-readiness",
    ),
    PackageInput(
        "reports/reggov-guidelines-readiness.md",
        "readiness/reggov-guidelines-readiness.md",
        "reggov-guidelines-readiness",
    ),
    PackageInput(
        "reports/final-human-readthrough.md",
        "readiness/final-human-readthrough.md",
        "manual-final-submission-signoff",
    ),
]


def main() -> int:
    release_tag = release_tag_from_citation(ROOT / "CITATION.cff")
    rows = source_rows()
    readme = readme_text(release_tag)
    rows.append(row_for_bytes("README-DOI-DEPOSIT.txt", "doi-deposit-instructions", readme.encode("utf-8")))
    manifest = {
        "schema": SCHEMA,
        "releaseTag": release_tag,
        "releaseUrl": f"https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{release_tag}",
        "generatedAt": FIXED_GENERATED_AT,
        "packagePath": str(PACKAGE.relative_to(ROOT)),
        "statusBoundary": (
            "This package is archive-ready as a handoff artifact but does not assert "
            "that a DOI has been minted or that human final-submission signoff is complete."
        ),
        "primaryDepositAssets": [
            item.member
            for item in PACKAGE_INPUTS
            if item.member.startswith("primary-assets/")
        ],
        "selfOmission": (
            "doi-deposit-package-manifest.json and .md describe this package and are "
            "not included in the checksum rows."
        ),
        "members": rows,
    }
    manifest_json = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    manifest_md = markdown(manifest)

    DIST.mkdir(parents=True, exist_ok=True)
    PACKAGE_MANIFEST_JSON.write_text(manifest_json, encoding="utf-8")
    PACKAGE_MANIFEST_MD.write_text(manifest_md, encoding="utf-8")
    with zipfile.ZipFile(PACKAGE, "w") as archive:
        add_bytes(archive, "README-DOI-DEPOSIT.txt", readme.encode("utf-8"))
        add_bytes(archive, "doi-deposit-package-manifest.json", manifest_json.encode("utf-8"))
        add_bytes(archive, "doi-deposit-package-manifest.md", manifest_md.encode("utf-8"))
        for item in PACKAGE_INPUTS:
            add_bytes(archive, item.member, (ROOT / item.source).read_bytes())
    write_package_checksum(release_tag)

    print(f"Wrote {PACKAGE.relative_to(ROOT)}")
    print(f"Wrote {PACKAGE_MANIFEST_JSON.relative_to(ROOT)}")
    print(f"Wrote {PACKAGE_MANIFEST_MD.relative_to(ROOT)}")
    print(f"Wrote {PACKAGE_CHECKSUM_CSV.relative_to(ROOT)}")
    print(f"Wrote {PACKAGE_CHECKSUM_JSON.relative_to(ROOT)}")
    print(f"Wrote {PACKAGE_CHECKSUM_MD.relative_to(ROOT)}")
    return 0


def source_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in PACKAGE_INPUTS:
        path = ROOT / item.source
        if not path.exists():
            raise SystemExit(f"Missing DOI package input: {item.source}")
        rows.append(row_for_bytes(item.member, item.role, path.read_bytes(), source_path=item.source))
    return rows


def row_for_bytes(
    member: str,
    role: str,
    data: bytes,
    *,
    source_path: str = "generated",
) -> dict[str, str]:
    return {
        "member": member,
        "sourcePath": source_path,
        "role": role,
        "bytes": str(len(data)),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def add_bytes(archive: zipfile.ZipFile, member: str, data: bytes) -> None:
    info = zipfile.ZipInfo(member, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def release_tag_from_citation(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(text)
    if not match:
        raise SystemExit(f"Could not find release tag in {path.relative_to(ROOT)}")
    return match.group(1).strip()


def write_package_checksum(release_tag: str) -> None:
    data = PACKAGE.read_bytes()
    row = {
        "path": str(PACKAGE.relative_to(ROOT)),
        "releaseAssetName": PACKAGE.name,
        "role": "doi-deposit-handoff-package",
        "checksumStatus": "local-doi-package-sha256",
        "bytes": str(len(data)),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    checksum = {
        "schema": CHECKSUM_SCHEMA,
        "releaseTag": release_tag,
        "releaseUrl": f"https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{release_tag}",
        "generatedAt": FIXED_GENERATED_AT,
        "row": row,
    }
    PACKAGE_CHECKSUM_CSV.write_text(
        ",".join(row.keys()) + "\n" + ",".join(row.values()) + "\n",
        encoding="utf-8",
    )
    PACKAGE_CHECKSUM_JSON.write_text(
        json.dumps(checksum, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    PACKAGE_CHECKSUM_MD.write_text(package_checksum_markdown(checksum), encoding="utf-8")


def package_checksum_markdown(checksum: dict[str, object]) -> str:
    row = checksum["row"]
    assert isinstance(row, dict)
    return "\n".join(
        [
            "# DOI Deposit Package Checksum",
            "",
            "This file records the byte-level checksum for the generated DOI-deposit handoff package. It is an ignored release aid and does not assert that a DOI has been minted.",
            "",
            "## Summary",
            "",
            f"- Schema: `{checksum['schema']}`",
            f"- Release tag: `{checksum['releaseTag']}`",
            f"- Release URL: {checksum['releaseUrl']}",
            f"- Generated at: `{checksum['generatedAt']}`",
            "",
            "## SHA-256 Checksum",
            "",
            "| Path | Release asset | Role | Checksum status | Bytes | SHA-256 |",
            "| --- | --- | --- | --- | ---: | --- |",
            "| {path} | {releaseAssetName} | {role} | {checksumStatus} | {bytes} | `{sha256}` |".format(
                path=row["path"],
                releaseAssetName=row["releaseAssetName"],
                role=row["role"],
                checksumStatus=row["checksumStatus"],
                bytes=row["bytes"],
                sha256=row["sha256"],
            ),
            "",
        ]
    )


def readme_text(release_tag: str) -> str:
    return textwrap.dedent(
        f"""\
        Lobby Capture Simulator DOI Deposit Package
        ==================================================

        Release tag: {release_tag}
        Release URL: https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{release_tag}

        This ZIP is a convenience handoff for archive deposition. It includes
        the four primary release assets, release-machine checksums, citation and
        Zenodo metadata, submission and journal-readiness audits, and the final
        human read-through checklist. The DOI deposit readiness report remains
        outside this ZIP because it verifies this package after construction.

        This package does not assert that a DOI has been minted. After a DOI is
        created, record it in CITATION.cff, .zenodo.json, the paper declarations,
        and reports/final-human-readthrough.md, then rerun make paper-artifacts-check.

        Primary assets:
        - primary-assets/lobby-capture-wiley-submission.zip
        - primary-assets/regulation-governance-wiley.pdf
        - primary-assets/strategic-channel-substitution-regulatory-capture.pdf
        - primary-assets/supplement.pdf

        Verification:
        - doi-deposit-package-manifest.json lists package members and SHA-256 hashes.
        - dist/doi-deposit-package-checksum.* in the release records the package
          ZIP's byte-level SHA-256 hash.
        - metadata/release-asset-checksums.* records byte-level checksums for the
          release assets produced on the release-building machine.
        - After GitHub release assets are uploaded, make github-release-asset-audit
          writes ignored reports comparing uploaded asset sizes and SHA-256
          digests against the local release-machine checksum manifests. That
          post-release audit verifies upload integrity only and does not mint a DOI.
        - reports/zenodo-deposit-preflight.md in the repository/release records
          the local Zenodo payload check and the unpublished-draft workflow.
        - readiness/submission-readiness.md states the claim boundary and
          remaining final-submission gates.
        - reports/doi-deposit-readiness.md in the repository/release verifies
          this package after it is built.
        """
    )


def markdown(manifest: dict[str, object]) -> str:
    rows = manifest["members"]
    assert isinstance(rows, list)
    lines = [
        "# DOI Deposit Package Manifest",
        "",
        "This manifest describes the generated DOI-deposit handoff package. It is a convenience artifact for archive deposition and does not assert that a DOI has been minted.",
        "",
        "## Summary",
        "",
        f"- Schema: `{manifest['schema']}`",
        f"- Release tag: `{manifest['releaseTag']}`",
        f"- Release URL: {manifest['releaseUrl']}",
        f"- Generated at: `{manifest['generatedAt']}`",
        f"- Package path: `{manifest['packagePath']}`",
        f"- Status boundary: {manifest['statusBoundary']}",
        f"- Self-omission: {manifest['selfOmission']}",
        "",
        "## Primary Deposit Assets",
        "",
    ]
    primary = manifest["primaryDepositAssets"]
    assert isinstance(primary, list)
    for member in primary:
        lines.append(f"- `{member}`")
    lines.extend(
        [
            "",
            "## Member Checksums",
            "",
            "| Member | Source path | Role | Bytes | SHA-256 |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for entry in rows:
        assert isinstance(entry, dict)
        lines.append(
            "| {member} | {sourcePath} | {role} | {bytes} | `{sha256}` |".format(
                member=entry["member"],
                sourcePath=entry["sourcePath"],
                role=entry["role"],
                bytes=entry["bytes"],
                sha256=entry["sha256"],
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
