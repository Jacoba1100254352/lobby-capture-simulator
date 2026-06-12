#!/usr/bin/env python3
"""Classify source-fetch failures into a live-run status CSV row.

The live snapshot runner deliberately falls back when optional public APIs are
quota-blocked or unavailable. This helper keeps those failure notes structured
enough for source-capability reports without promoting partial payloads as
evidence.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


NEXT_ACCESS_RE = re.compile(r'"nextAccessTime"\s*:\s*"([^"]+)"')
HTTP_STATUS_RE = re.compile(r"HTTP\s+(\d{3})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="live-run source identifier, e.g. sam-contract-awards")
    parser.add_argument("log", type=Path, help="captured source-fetch stdout/stderr log")
    parser.add_argument("--context", action="append", default=[], help="extra source configuration context")
    parser.add_argument("--fallback-note", default="", help="fallback behavior after this source failed")
    args = parser.parse_args()

    text = args.log.read_text(encoding="utf-8", errors="replace") if args.log.exists() else ""
    status, reason = classify_failure(args.source, text)
    notes = [reason, *[item for item in args.context if item], args.fallback_note]
    writer = csv.DictWriter(sys.stdout, fieldnames=["source", "status", "notes"], lineterminator="\n")
    writer.writerow({
        "source": args.source,
        "status": status,
        "notes": "; ".join(item for item in notes if item),
    })
    return 0


def classify_failure(source: str, text: str) -> tuple[str, str]:
    if source == "sam-contract-awards":
        return classify_sam_contract_awards_failure(text)
    status = "unavailable"
    http_status = first_http_status(text)
    if http_status:
        return status, f"{source} request failed with HTTP {http_status}"
    if "hard timeout" in text.lower():
        return status, f"{source} request exceeded the configured hard timeout"
    return status, f"{source} request failed"


def classify_sam_contract_awards_failure(text: str) -> tuple[str, str]:
    next_access = first_match(NEXT_ACCESS_RE, text)
    quota_markers = (
        "exceeded your quota",
        "message throttled out",
        '"code":"900804"',
        '"code": "900804"',
    )
    if next_access or any(marker in text.lower() for marker in quota_markers):
        if next_access:
            return "quota_blocked", f"SAM.gov quota blocked until {next_access}"
        return "quota_blocked", "SAM.gov quota blocked; retry after the upstream reset time"
    http_status = first_http_status(text)
    if http_status == "403":
        return "unavailable", "SAM.gov Contract Awards request failed authorization or access checks"
    if http_status == "429":
        return "quota_blocked", "SAM.gov Contract Awards request returned HTTP 429"
    if "hard timeout" in text.lower():
        return "unavailable", "SAM.gov Contract Awards request exceeded the configured hard timeout"
    return "unavailable", "SAM.gov Contract Awards request failed"


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1) if match else ""


def first_http_status(text: str) -> str:
    match = HTTP_STATUS_RE.search(text)
    return match.group(1) if match else ""


if __name__ == "__main__":
    raise SystemExit(main())
