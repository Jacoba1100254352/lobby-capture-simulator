"""Release metadata helpers for generated paper-control artifacts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CITATION_CFF = ROOT / "CITATION.cff"
FALLBACK_GENERATED_AT = "2026-05-05T00:00:00Z"
RELEASE_METADATA_FIELDS = ("generatedAt", "releaseTag", "releaseDate")
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DATE_RELEASED_PATTERN = re.compile(r"^date-released:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def release_metadata() -> dict[str, str]:
    if not CITATION_CFF.exists():
        return {
            "generatedAt": FALLBACK_GENERATED_AT,
            "releaseTag": "missing",
            "releaseDate": "missing",
        }
    text = CITATION_CFF.read_text(encoding="utf-8")
    release_tag = pattern_value(VERSION_PATTERN, text) or "missing"
    release_date = pattern_value(DATE_RELEASED_PATTERN, text) or "missing"
    generated_at = (
        f"{release_date}T00:00:00Z"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", release_date)
        else FALLBACK_GENERATED_AT
    )
    return {
        "generatedAt": generated_at,
        "releaseTag": release_tag,
        "releaseDate": release_date,
    }


def with_release_metadata(
        rows: list[dict[str, str]],
        metadata: dict[str, str],
) -> list[dict[str, str]]:
    return [
        {
            **metadata,
            **row,
        }
        for row in rows
    ]


def metadata_summary_lines(metadata: dict[str, str]) -> list[str]:
    return [
        f"- Generated at: `{metadata['generatedAt']}`",
        f"- Release tag: `{metadata['releaseTag']}`",
        f"- Release date: `{metadata['releaseDate']}`",
    ]


def pattern_value(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip() if match else ""
