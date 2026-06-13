#!/usr/bin/env python3
"""Audit manuscript language for unbounded calibrated-policy overclaims."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


REPORTS = Path("reports")

TARGET_FILES = [
    Path("paper/sections/reggov-body.tex"),
    Path("paper/sections/supplement-body.tex"),
    Path("docs/scenario-catalog.md"),
    Path("docs/validation.md"),
    Path("docs/source-data-roadmap.md"),
    Path("docs/next-steps.md"),
    Path("reports/claim-boundary-audit.md"),
    Path("reports/claim-source-dependency.md"),
    Path("reports/causal-calibration-targets.md"),
    Path("reports/claim-posture-audit.md"),
    Path("reports/calibration-readiness.md"),
]

WATCH_PATTERNS = [
    ("calibrated-policy-simulation", re.compile(r"calibrated[- ]policy[- ]simulation", re.IGNORECASE)),
    ("calibrated-reform-effects", re.compile(r"calibrated reform effects", re.IGNORECASE)),
    ("policy-effect-language", re.compile(r"policy[- ]effect", re.IGNORECASE)),
    ("representative-hidden-channel", re.compile(r"representative national hidden-channel magnitudes", re.IGNORECASE)),
    ("causal-effect-language", re.compile(r"causal (?:effect|effects|estimate|estimates)", re.IGNORECASE)),
    ("policy-ranking-language", re.compile(r"policy ranking", re.IGNORECASE)),
]

BOUNDARY_TERMS = [
    "not ",
    "do not",
    "cannot",
    "outside",
    "before",
    "until",
    "blocked",
    "blocking",
    "remain",
    "rather than",
    "instead of",
    "only ",
    "future",
    "would move",
    "required before",
    "must clear",
    "not as evidence",
    "not_cleared",
]

BLOCKING_STATUSES = {
    "overclaim",
    "missing_required_boundary",
    "missing",
}

REQUIRED_BOUNDARIES = [
    (
        Path("paper/sections/reggov-body.tex"),
        "not a representative empirical panel",
        "main paper identifies the source snapshot as nonrepresentative",
    ),
    (
        Path("paper/sections/reggov-body.tex"),
        "not uncertainty intervals around an empirical target",
        "main paper keeps uncertainty language tied to finite-run diagnostics",
    ),
    (
        Path("paper/sections/reggov-body.tex"),
        "design diagnostic rather than a policy ranking",
        "main paper bounds the portfolio screen",
    ),
    (
        Path("paper/sections/reggov-body.tex"),
        "Ten generated causal-calibration targets remain open",
        "main paper names open causal-calibration blockers",
    ),
    (
        Path("paper/sections/supplement-body.tex"),
        "not an estimated policy-effect model",
        "supplement bounds the model purpose",
    ),
    (
        Path("paper/sections/supplement-body.tex"),
        "before the project can claim calibrated reform effects",
        "supplement ties stronger claims to causal calibration",
    ),
    (
        Path("docs/validation.md"),
        "calibrated policy claims remain blocked",
        "validation docs separate mechanism readiness from policy calibration",
    ),
    (
        Path("reports/claim-posture-audit.md"),
        "calibrated-policy dependency=not_cleared",
        "claim-posture audit records the not-cleared policy dependency",
    ),
    (
        Path("reports/calibration-readiness.md"),
        "calibrated-policy-readiness | blocked",
        "calibration-readiness audit blocks calibrated policy claims",
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    root = args.root
    rows = audit_rows(root)
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "policy-claim-language-audit.csv", rows)
    write_markdown(args.reports / "policy-claim-language-audit.md", rows)
    print(f"Wrote {args.reports / 'policy-claim-language-audit.csv'}")
    print(f"Wrote {args.reports / 'policy-claim-language-audit.md'}")
    blocking_rows = [item for item in rows if item["status"] in BLOCKING_STATUSES]
    if blocking_rows:
        print(f"Policy-claim language audit failed with {len(blocking_rows)} blocking row(s).")
        return 1
    return 0


def audit_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_path in TARGET_FILES:
        path = root / relative_path
        if not path.exists():
            rows.append(row("missing_file", relative_path, "", 0, "missing", "audit target is absent"))
            continue
        text = path.read_text(encoding="utf-8")
        rows.extend(watch_rows(relative_path, text))
    rows.extend(required_boundary_rows(root))
    return rows


def watch_rows(relative_path: Path, text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in WATCH_PATTERNS:
            if not pattern.search(line):
                continue
            status = "bounded_context" if has_boundary_context(line) else "overclaim"
            detail = (
                "phrase appears with limiting language"
                if status == "bounded_context"
                else "phrase appears without local claim-boundary language"
            )
            rows.append(row(label, relative_path, line.strip(), line_number, status, detail))
    return rows


def required_boundary_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_path, phrase, detail in REQUIRED_BOUNDARIES:
        path = root / relative_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        status = "required_boundary_present" if phrase in text else "missing_required_boundary"
        rows.append(row("required-boundary", relative_path, phrase, 0, status, detail))
    return rows


def has_boundary_context(line: str) -> bool:
    lowered = line.lower()
    return any(term in lowered for term in BOUNDARY_TERMS)


def row(
        audit_key: str,
        relative_path: Path,
        context: str,
        line_number: int,
        status: str,
        detail: str,
) -> dict[str, str]:
    return {
        "auditKey": audit_key,
        "file": str(relative_path),
        "line": str(line_number) if line_number else "",
        "status": status,
        "detail": detail,
        "context": context,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["auditKey", "file", "line", "status", "detail", "context"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {
        status: sum(1 for row in rows if row["status"] == status)
        for status in (
            "bounded_context",
            "required_boundary_present",
            "overclaim",
            "missing_required_boundary",
            "missing",
        )
    }
    lines = [
        "# Policy-Claim Language Audit",
        "",
        "This audit scans the manuscript, supplement, and paper-facing documentation for calibrated-policy and policy-effect language. Hits are acceptable only when the local sentence also carries claim-boundary language such as not, before, until, outside, blocked, blocking, not_cleared, or rather than. The audit is a mechanical guardrail; it does not replace substantive peer review.",
        "",
        "## Summary",
        "",
        f"- Bounded policy-language hits: `{counts['bounded_context']}`",
        f"- Required boundary phrases present: `{counts['required_boundary_present']}`",
        f"- Overclaim hits: `{counts['overclaim']}`",
        f"- Missing required boundary phrases: `{counts['missing_required_boundary']}`",
        f"- Missing audit target files: `{counts['missing']}`",
        "",
        "## Required Boundaries",
        "",
        "| File | Status | Boundary phrase | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        if item["auditKey"] != "required-boundary":
            continue
        lines.append(
            f"| {md(item['file'])} | {md(item['status'])} | {md(item['context'])} | {md(item['detail'])} |"
        )
    lines.extend(
        [
            "",
            "## Watched Language Hits",
            "",
            "| File | Line | Key | Status | Context |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for item in rows:
        if item["auditKey"] == "required-boundary":
            continue
        lines.append(
            f"| {md(item['file'])} | {md(item['line'])} | {md(item['auditKey'])} | {md(item['status'])} | {md(item['context'])} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("|", "\\|")).strip()


if __name__ == "__main__":
    raise SystemExit(main())
