#!/usr/bin/env python3
"""Write a checksum manifest for a staged Wiley submission package."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


MANIFEST_JSON = Path("supporting-information/submission-package-manifest.json")
MANIFEST_MD = Path("supporting-information/submission-package-manifest.md")
FIXED_GENERATED_AT = "2026-05-05T00:00:00Z"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: write-submission-package-manifest.py STAGING_DIR REPO_ROOT",
            file=sys.stderr,
        )
        return 2

    staging = Path(sys.argv[1]).resolve()
    root = Path(sys.argv[2]).resolve()
    if not staging.exists():
        print(f"Staging directory does not exist: {staging}", file=sys.stderr)
        return 2

    release_tag = release_tag_from_citation(root / "CITATION.cff")
    entries = package_entries(staging)
    manifest = {
        "schema": "lobby-capture-submission-package-manifest-v1",
        "releaseTag": release_tag,
        "generatedAt": FIXED_GENERATED_AT,
        "memberCount": len(entries),
        "members": entries,
        "notes": (
            "Checksums cover staged package members except the manifest files "
            "themselves. Private credentials and raw API payload archives are "
            "intentionally excluded from the submission package."
        ),
    }

    json_path = staging / MANIFEST_JSON
    md_path = staging / MANIFEST_MD
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown(manifest), encoding="utf-8")
    print(f"Wrote {json_path.relative_to(staging)}")
    print(f"Wrote {md_path.relative_to(staging)}")
    return 0


def release_tag_from_citation(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(text)
    if not match:
        raise SystemExit(f"Could not find version in {path}")
    return match.group(1).strip()


def package_entries(staging: Path) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for path in sorted(staging.rglob("*"), key=lambda item: item.relative_to(staging).as_posix()):
        if not path.is_file():
            continue
        relative = Path(path.relative_to(staging).as_posix())
        if relative in {MANIFEST_JSON, MANIFEST_MD}:
            continue
        data = path.read_bytes()
        entries.append(
            {
                "path": relative.as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "role": package_role(relative.as_posix()),
            }
        )
    return entries


def package_role(path: str) -> str:
    if path.endswith(".pdf") and path.startswith("figures/"):
        return "figure-pdf"
    if path.endswith(".svg") and path.startswith("figures/"):
        return "figure-source"
    if path.startswith("tables/"):
        return "generated-table"
    if path.startswith("sections/") or path.endswith(".tex"):
        return "latex-source"
    if path.startswith("supporting-information/report-data/"):
        return "generated-report"
    if path.startswith("supporting-information/"):
        return "supporting-information"
    if path.endswith(".cls") or path.endswith(".sty") or path.endswith(".bst"):
        return "latex-template"
    if path == "references.bib":
        return "bibliography"
    return "submission-file"


def markdown(manifest: dict[str, object]) -> str:
    entries = manifest["members"]
    assert isinstance(entries, list)
    lines = [
        "# Submission Package Manifest",
        "",
        "This manifest lists the files staged into the Wiley submission archive and records a SHA-256 checksum for each non-manifest member. It is intended to make DOI archiving, reviewer handoff, and final editorial signoff auditable.",
        "",
        "## Summary",
        "",
        f"- Release tag: `{manifest['releaseTag']}`",
        f"- Generated at: `{manifest['generatedAt']}`",
        f"- Member count, excluding manifest files: `{manifest['memberCount']}`",
        "- Exclusions: private credentials and raw API payload archives",
        "",
        "## Members",
        "",
        "| Path | Role | Bytes | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for entry in entries:
        assert isinstance(entry, dict)
        lines.append(
            "| {path} | {role} | {bytes} | `{sha256}` |".format(
                path=entry["path"],
                role=entry["role"],
                bytes=entry["bytes"],
                sha256=entry["sha256"],
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
