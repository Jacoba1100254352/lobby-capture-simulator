#!/usr/bin/env python3
"""Audit final LaTeX logs for unresolved compile state and visible warnings."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
REPORTS = ROOT / "reports"

LOGS = [
    ("local-manuscript", PAPER / "strategic-channel-substitution-regulatory-capture.log"),
    ("wiley-manuscript", PAPER / "regulation-governance-wiley.log"),
    ("supplement", PAPER / "supplement.log"),
]

UNRESOLVED_PATTERNS = [
    ("latex-error", re.compile(r"! LaTeX Error:")),
    ("undefined-control-sequence", re.compile(r"Undefined control sequence")),
    ("emergency-stop", re.compile(r"Emergency stop")),
    ("fatal-error", re.compile(r"Fatal error", re.IGNORECASE)),
    ("missing-bbl", re.compile(r"No file .+\.bbl")),
    ("undefined-citations", re.compile(r"There were undefined citations|Citation\(s\) may have changed|Rerun to get citations correct")),
    ("undefined-references", re.compile(r"There were undefined references|Label\(s\) may have changed|Rerun to get cross-references right")),
]
OVERFULL_HBOX_RE = re.compile(r"Overfull \\hbox \(([0-9.]+)pt too wide\)")
OVERFULL_VBOX_RE = re.compile(r"Overfull \\vbox \(([0-9.]+)pt too high\)")
UNDERFULL_HBOX_RE = re.compile(r"Underfull \\hbox")
UNDERFULL_VBOX_RE = re.compile(r"Underfull \\vbox")


def main() -> int:
    rows = [audit_log(name, path) for name, path in LOGS]
    write_csv(REPORTS / "latex-log-audit.csv", rows)
    write_markdown(REPORTS / "latex-log-audit.md", rows)
    print("Wrote reports/latex-log-audit.csv")
    print("Wrote reports/latex-log-audit.md")
    return 0


def audit_log(name: str, path: Path) -> dict[str, str]:
    if not path.exists():
        return {
            "document": name,
            "logPath": str(path.relative_to(ROOT)),
            "status": "missing",
            "unresolvedCount": "1",
            "unresolvedKinds": "missing-log",
            "overfullHBoxCount": "0",
            "maxOverfullHBoxPt": "0.0000",
            "overfullVBoxCount": "0",
            "maxOverfullVBoxPt": "0.0000",
            "underfullHBoxCount": "0",
            "underfullVBoxCount": "0",
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    unresolved = [
        name
        for name, pattern in UNRESOLVED_PATTERNS
        if pattern.search(text)
    ]
    overfull_hbox = [float(value) for value in OVERFULL_HBOX_RE.findall(text)]
    overfull_vbox = [float(value) for value in OVERFULL_VBOX_RE.findall(text)]
    return {
        "document": name,
        "logPath": str(path.relative_to(ROOT)),
        "status": "pass" if not unresolved else "fail",
        "unresolvedCount": str(len(unresolved)),
        "unresolvedKinds": ";".join(unresolved),
        "overfullHBoxCount": str(len(overfull_hbox)),
        "maxOverfullHBoxPt": f"{max(overfull_hbox, default=0.0):.4f}",
        "overfullVBoxCount": str(len(overfull_vbox)),
        "maxOverfullVBoxPt": f"{max(overfull_vbox, default=0.0):.4f}",
        "underfullHBoxCount": str(len(UNDERFULL_HBOX_RE.findall(text))),
        "underfullVBoxCount": str(len(UNDERFULL_VBOX_RE.findall(text))),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "document",
                "logPath",
                "status",
                "unresolvedCount",
                "unresolvedKinds",
                "overfullHBoxCount",
                "maxOverfullHBoxPt",
                "overfullVBoxCount",
                "maxOverfullVBoxPt",
                "underfullHBoxCount",
                "underfullVBoxCount",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    unresolved_total = sum(int(row["unresolvedCount"]) for row in rows)
    lines = [
        "# LaTeX Log Audit",
        "",
        "This audit scans the final local manuscript, Wiley manuscript, and supplement LaTeX logs for unresolved compile state. Overfull and underfull boxes are reported for visual follow-up, but only unresolved errors, citations, references, missing logs, or rerun-required states block the artifact gate.",
        "",
        f"- Logs checked: `{len(rows)}`",
        f"- Unresolved states: `{unresolved_total}`",
        "",
        "| Document | Status | Unresolved | Overfull hbox | Max hbox pt | Overfull vbox | Max vbox pt | Underfull hbox | Underfull vbox |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        unresolved = row["unresolvedKinds"] or "-"
        lines.append(
            "| {document} | {status} | {unresolved} | {overfull_hbox} | {max_hbox} | {overfull_vbox} | {max_vbox} | {underfull_hbox} | {underfull_vbox} |".format(
                document=row["document"],
                status=row["status"],
                unresolved=unresolved,
                overfull_hbox=row["overfullHBoxCount"],
                max_hbox=row["maxOverfullHBoxPt"],
                overfull_vbox=row["overfullVBoxCount"],
                max_vbox=row["maxOverfullVBoxPt"],
                underfull_hbox=row["underfullHBoxCount"],
                underfull_vbox=row["underfullVBoxCount"],
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
