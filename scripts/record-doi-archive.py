#!/usr/bin/env python3
"""Record a minted or reserved archive DOI in the publication metadata.

This is intentionally separate from Zenodo draft creation. It updates the
tracked files that the readiness audits inspect after a DOI exists, but it does
not mark the human scholarly read-through complete.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--doi", default=os.environ.get("ARCHIVE_DOI") or os.environ.get("ZENODO_RESERVED_DOI", ""))
    parser.add_argument("--archive-url", default=os.environ.get("ARCHIVE_URL", ""))
    args = parser.parse_args()

    doi = normalize_doi(args.doi)
    if not doi:
        raise SystemExit("Provide --doi or set ARCHIVE_DOI/ZENODO_RESERVED_DOI.")
    archive_url = args.archive_url.strip() or f"https://doi.org/{doi}"
    root = args.root.resolve()

    changed = [
        update_citation(root / "CITATION.cff", doi),
        update_zenodo(root / ".zenodo.json", doi, archive_url),
        update_declarations(root / "paper" / "sections" / "submission-declarations.tex", doi, archive_url),
        update_final_readthrough(root / "reports" / "final-human-readthrough.md", archive_url),
    ]
    for path in changed:
        print(f"Updated {path.relative_to(root)}")
    print("DOI recorded. Human read-through status was not changed.")
    return 0


def normalize_doi(value: str) -> str:
    match = DOI_PATTERN.search(value.strip())
    return match.group(0) if match else ""


def update_citation(path: Path, doi: str) -> Path:
    text = read_required(path)
    doi_line = f'doi: "{doi}"'
    preferred_index = text.find("\npreferred-citation:")
    head = text if preferred_index == -1 else text[:preferred_index]
    tail = "" if preferred_index == -1 else text[preferred_index:]
    if re.search(r"(?m)^doi:\s*", head):
        head = re.sub(r"(?m)^doi:\s*.*$", doi_line, head)
    else:
        lines = head.splitlines()
        insert_at = next((index + 1 for index, line in enumerate(lines) if line.startswith("url: ")), len(lines))
        lines.insert(insert_at, doi_line)
        head = "\n".join(lines) + ("\n" if text.endswith("\n") or tail else "")
    write_if_changed(path, head + tail)
    return path


def update_zenodo(path: Path, doi: str, archive_url: str) -> Path:
    data = json.loads(read_required(path))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object.")
    data["doi"] = doi
    related = data.setdefault("related_identifiers", [])
    if not isinstance(related, list):
        raise SystemExit(f"{path} related_identifiers must be a list.")
    related = [item for item in related if not is_archive_doi_identifier(item)]
    related.append(
        {
            "identifier": archive_url,
            "relation": "isIdenticalTo",
            "resource_type": "software",
        }
    )
    data["related_identifiers"] = related
    write_if_changed(path, json.dumps(data, indent=2, sort_keys=False) + "\n")
    return path


def is_archive_doi_identifier(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    identifier = str(item.get("identifier", ""))
    if not normalize_doi(identifier):
        return False
    return item.get("relation") == "isIdenticalTo" and item.get("resource_type") == "software"


def update_declarations(path: Path, doi: str, archive_url: str) -> Path:
    text = read_required(path)
    sentence = f"The DOI archive for this review bundle is \\href{{{archive_url}}}{{{doi}}}."
    pattern = r"The DOI archive for this review bundle is \\href\{[^}]+\}\{[^}]+\}\."
    if re.search(pattern, text):
        text = re.sub(pattern, sentence, text)
    else:
        release_sentence = re.search(r"(release r\d+\}\. )", text)
        if not release_sentence:
            raise SystemExit(f"Could not find release sentence in {path}.")
        insert_at = release_sentence.end()
        text = text[:insert_at] + sentence + " " + text[insert_at:]
    write_if_changed(path, text)
    return path


def update_final_readthrough(path: Path, archive_url: str) -> Path:
    text = read_required(path)
    if re.search(r"(?m)^doi-archive:\s*", text):
        text = re.sub(r"(?m)^doi-archive:\s*.*$", f"doi-archive: {archive_url}", text)
    else:
        reviewed_match = re.search(r"(?m)^reviewed-commit:\s*.*$", text)
        if not reviewed_match:
            raise SystemExit(f"Could not find reviewed-commit field in {path}.")
        text = text[: reviewed_match.end()] + f"\ndoi-archive: {archive_url}" + text[reviewed_match.end():]
    write_if_changed(path, text)
    return path


def read_required(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> None:
    if path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
