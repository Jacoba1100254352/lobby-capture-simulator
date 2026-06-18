#!/usr/bin/env python3
"""Audit citation and bibliography integrity for the manuscript package."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REFERENCES = ROOT / "paper" / "references.bib"
TARGET_FILES = [
    ROOT / "paper" / "strategic-channel-substitution-regulatory-capture.tex",
    ROOT / "paper" / "regulation-governance-wiley.tex",
    ROOT / "paper" / "sections" / "reggov-body.tex",
    ROOT / "paper" / "sections" / "supplement-body.tex",
]
OUTPUT_CSV = REPORTS / "reference-integrity-audit.csv"
OUTPUT_MD = REPORTS / "reference-integrity-audit.md"

PLACEHOLDER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bTODO\b",
        r"\bFIXME\b",
        r"planned validation",
        r"citation needed",
        r"publisher unknown",
        r"forthcoming\?",
    )
]

REQUIRED_FIELDS = {
    "article": {"title", "author", "journal", "year"},
    "book": {"title", "publisher", "year"},
    "incollection": {"title", "author", "booktitle", "publisher", "year"},
    "misc": {"title", "author", "year", "howpublished"},
}

RECOMMENDED_ARTICLE_FIELDS = {"volume", "pages"}
SOURCE_KEYS = {
    "ldaData",
    "fecData",
    "federalRegisterApi",
    "regulationsGovApi",
    "nycCfbData",
    "irsEoBmf",
    "seattleVouchers",
    "usaspending",
}


def main() -> int:
    references_text = read_text(REFERENCES)
    entries = parse_bibtex_entries(references_text)
    cited_keys = cited_keys_from_targets()
    rows: list[dict[str, str]] = []
    rows.extend(citation_key_rows(cited_keys, entries))
    rows.extend(entry_metadata_rows(entries, cited_keys))
    rows.extend(placeholder_rows(entries))
    rows.extend(source_metadata_rows(entries))
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown(rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 1 if any(row["status"] == "blocked" for row in rows) else 0


def citation_key_rows(cited_keys: set[str], entries: dict[str, dict[str, object]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    entry_keys = set(entries)
    for key in sorted(cited_keys - entry_keys):
        rows.append(row("citation-key", key, "blocked", "cited key is missing from references.bib"))
    for key in sorted(entry_keys - cited_keys):
        rows.append(row("citation-key", key, "advisory", "bibliography key is not cited in manuscript targets"))
    rows.append(
        row(
            "citation-key-summary",
            "all-citations",
            "ready" if cited_keys <= entry_keys else "blocked",
            f"citedKeys={len(cited_keys)}; bibliographyEntries={len(entry_keys)}; missing={len(cited_keys - entry_keys)}; unused={len(entry_keys - cited_keys)}",
        )
    )
    return rows


def entry_metadata_rows(entries: dict[str, dict[str, object]], cited_keys: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key, entry in sorted(entries.items()):
        entry_type = str(entry["type"]).lower()
        fields = entry["fields"]
        assert isinstance(fields, dict)
        required = set(REQUIRED_FIELDS.get(entry_type, {"title", "year"}))
        if entry_type == "book" and ("author" in fields or "editor" in fields):
            required.discard("author")
        missing_required = sorted(field for field in required if not field_present(fields, field))
        if missing_required:
            rows.append(
                row(
                    "entry-required-fields",
                    key,
                    "blocked",
                    f"type={entry_type}; missing={'; '.join(missing_required)}",
                )
            )
            continue
        detail_parts = [f"type={entry_type}", f"cited={'yes' if key in cited_keys else 'no'}"]
        if entry_type == "article":
            missing_recommended = sorted(field for field in RECOMMENDED_ARTICLE_FIELDS if not field_present(fields, field))
            if missing_recommended:
                rows.append(
                    row(
                        "entry-recommended-fields",
                        key,
                        "advisory",
                        f"missing recommended article fields={'; '.join(missing_recommended)}",
                    )
                )
            if not field_present(fields, "doi"):
                rows.append(row("entry-doi", key, "advisory", "peer-reviewed article has no DOI field recorded"))
        rows.append(row("entry-required-fields", key, "ready", "; ".join(detail_parts)))
    return rows


def placeholder_rows(entries: dict[str, dict[str, object]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    hit_count = 0
    for key, entry in sorted(entries.items()):
        raw = str(entry["raw"])
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(raw):
                hit_count += 1
                rows.append(row("placeholder-text", key, "blocked", f"matched={pattern.pattern}"))
    rows.append(
        row(
            "placeholder-summary",
            "references.bib",
            "ready" if hit_count == 0 else "blocked",
            f"placeholderHits={hit_count}",
        )
    )
    return rows


def source_metadata_rows(entries: dict[str, dict[str, object]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key in sorted(SOURCE_KEYS):
        entry = entries.get(key)
        if not entry:
            rows.append(row("source-metadata", key, "blocked", "public source key missing"))
            continue
        fields = entry["fields"]
        assert isinstance(fields, dict)
        note = str(fields.get("note", ""))
        howpublished = str(fields.get("howpublished", ""))
        has_accessed = "accessed" in note.lower()
        has_url = "\\url{" in howpublished or "http://" in howpublished or "https://" in howpublished
        status = "ready" if has_accessed and has_url else "blocked"
        rows.append(
            row(
                "source-metadata",
                key,
                status,
                f"accessedNote={'yes' if has_accessed else 'no'}; url={'yes' if has_url else 'no'}",
            )
        )
    return rows


def parse_bibtex_entries(text: str) -> dict[str, dict[str, object]]:
    entries: dict[str, dict[str, object]] = {}
    index = 0
    while True:
        start = text.find("@", index)
        if start == -1:
            break
        type_match = re.match(r"@([A-Za-z]+)\s*\{", text[start:])
        if not type_match:
            index = start + 1
            continue
        entry_type = type_match.group(1)
        open_brace = start + type_match.end() - 1
        close_brace = matching_brace(text, open_brace)
        if close_brace == -1:
            break
        raw_entry = text[start:close_brace + 1]
        inner = text[open_brace + 1:close_brace]
        key, fields_text = split_key_and_fields(inner)
        if key:
            entries[key] = {
                "type": entry_type,
                "fields": parse_fields(fields_text),
                "raw": raw_entry,
            }
        index = close_brace + 1
    return entries


def split_key_and_fields(inner: str) -> tuple[str, str]:
    depth = 0
    for index, char in enumerate(inner):
        if char == "{":
            depth += 1
        elif char == "}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            return inner[:index].strip(), inner[index + 1:]
    return inner.strip(), ""


def parse_fields(fields_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in split_top_level(fields_text):
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        cleaned_name = name.strip().lower()
        cleaned_value = clean_value(value.strip())
        if cleaned_name:
            fields[cleaned_name] = cleaned_value
    return fields


def split_top_level(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    in_quote = False
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
        elif not in_quote and char == "{":
            depth += 1
        elif not in_quote and char == "}":
            depth = max(0, depth - 1)
        elif not in_quote and depth == 0 and char == ",":
            part = text[start:index].strip()
            if part:
                parts.append(part)
            start = index + 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def clean_value(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    if len(value) >= 2 and ((value[0] == "{" and value[-1] == "}") or (value[0] == '"' and value[-1] == '"')):
        return value[1:-1].strip()
    return value


def matching_brace(text: str, open_index: int) -> int:
    depth = 0
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def cited_keys_from_targets() -> set[str]:
    keys: set[str] = set()
    for target in TARGET_FILES:
        text = read_text(target)
        for match in re.finditer(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}", text):
            for key in match.group(1).split(","):
                cleaned = key.strip()
                if cleaned:
                    keys.add(cleaned)
    return keys


def field_present(fields: dict[str, str], field: str) -> bool:
    return bool(str(fields.get(field, "")).strip())


def row(audit_key: str, subject: str, status: str, detail: str) -> dict[str, str]:
    return {
        "auditKey": audit_key,
        "subject": subject,
        "status": status,
        "detail": detail,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=["auditKey", "subject", "status", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    counts = {
        status: sum(1 for row in rows if row["status"] == status)
        for status in ("ready", "advisory", "blocked")
    }
    lines = [
        "# Reference Integrity Audit",
        "",
        (
            "This audit checks citation-key consistency, type-specific bibliography "
            "metadata, public-source access notes, and placeholder text. Advisory rows "
            "record optional metadata that can still be improved without blocking the package."
        ),
        "",
        "## Summary",
        "",
        f"- Ready rows: `{counts['ready']}`.",
        f"- Advisory rows: `{counts['advisory']}`.",
        f"- Blocked rows: `{counts['blocked']}`.",
        "",
        "| Audit | Subject | Status | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {audit} | {subject} | {status} | {detail} |".format(
                audit=cell(item["auditKey"]),
                subject=cell(item["subject"]),
                status=cell(item["status"]),
                detail=cell(item["detail"]),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "`blocked` rows indicate missing cited keys, missing required fields, "
                "placeholder text, or missing public-source access metadata. `advisory` "
                "rows identify optional metadata such as DOI fields for older articles "
                "or uncited bibliography entries."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


if __name__ == "__main__":
    raise SystemExit(main())
