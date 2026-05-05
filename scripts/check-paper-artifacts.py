#!/usr/bin/env python3
"""Check that generated paper PDFs and submission artifacts are current."""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DIST = ROOT / "dist"

LOCAL_PDF = PAPER / "main.pdf"
WILEY_PDF = PAPER / "regulation-governance-wiley.pdf"
SUBMISSION_ZIP = DIST / "lobby-capture-wiley-submission.zip"

EXPECTED_ZIP_MEMBERS = {
    "lobby-capture-wiley-submission/main.tex",
    "lobby-capture-wiley-submission/main.pdf",
    "lobby-capture-wiley-submission/references.bib",
    "lobby-capture-wiley-submission/USG.cls",
    "lobby-capture-wiley-submission/wileyNJD-Chicago.bst",
    "lobby-capture-wiley-submission/SUBMISSION_README.txt",
    "lobby-capture-wiley-submission/sections/reggov-body.tex",
    "lobby-capture-wiley-submission/sections/submission-declarations.tex",
    "lobby-capture-wiley-submission/tables/campaign_snapshot.tex",
    "lobby-capture-wiley-submission/tables/sensitivity_snapshot.tex",
    "lobby-capture-wiley-submission/tables/ablation_snapshot.tex",
    "lobby-capture-wiley-submission/tables/interaction_snapshot.tex",
    "lobby-capture-wiley-submission/figures/Figure_1_channel_mix.pdf",
    "lobby-capture-wiley-submission/figures/Figure_2_evasion_sensitivity.pdf",
    "lobby-capture-wiley-submission/figures/Figure_3_interaction_tradeoffs.pdf",
    "lobby-capture-wiley-submission/figures/Figure_4_scenario_tradeoffs.pdf",
}


def main() -> int:
    failures: list[str] = []
    failures.extend(check_exists([LOCAL_PDF, WILEY_PDF, SUBMISSION_ZIP]))
    failures.extend(check_freshness())
    failures.extend(check_wiley_text())
    failures.extend(check_submission_zip())

    if failures:
        print("Paper artifact check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        print("\nRun `make paper-artifacts` and commit tracked regenerated files.", file=sys.stderr)
        return 1

    print("Paper artifacts are current.")
    return 0


def check_exists(paths: list[Path]) -> list[str]:
    return [f"missing required artifact: {path.relative_to(ROOT)}" for path in paths if not path.exists()]


def check_freshness() -> list[str]:
    failures: list[str] = []
    checks = [
        (LOCAL_PDF, local_pdf_inputs()),
        (WILEY_PDF, wiley_pdf_inputs()),
        (SUBMISSION_ZIP, submission_inputs()),
    ]
    for artifact, inputs in checks:
        if not artifact.exists():
            continue
        newest = newest_input(inputs)
        if newest and artifact.stat().st_mtime + 1 < newest.stat().st_mtime:
            failures.append(
                f"{artifact.relative_to(ROOT)} is older than {newest.relative_to(ROOT)}"
            )
    return failures


def local_pdf_inputs() -> list[Path]:
    return [
        PAPER / "main.tex",
        PAPER / "references.bib",
        *sorted((PAPER / "sections").glob("*.tex")),
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
    ]


def wiley_pdf_inputs() -> list[Path]:
    return [
        PAPER / "regulation-governance-wiley.tex",
        PAPER / "references.bib",
        ROOT / "scripts" / "build-wiley-paper.sh",
        *sorted((PAPER / "sections").glob("*.tex")),
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
    ]


def submission_inputs() -> list[Path]:
    return [
        WILEY_PDF,
        PAPER / "regulation-governance-wiley.tex",
        PAPER / "references.bib",
        ROOT / "scripts" / "build-submission-package.sh",
        *sorted((PAPER / "sections").glob("*.tex")),
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
    ]


def newest_input(inputs: list[Path]) -> Path | None:
    existing = [path for path in inputs if path.exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: path.stat().st_mtime)


def check_wiley_text() -> list[str]:
    if not WILEY_PDF.exists():
        return []
    try:
        text = subprocess.check_output(
            ["pdftotext", str(WILEY_PDF), "-"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        return [f"could not inspect Wiley PDF text with pdftotext: {error}"]
    forbidden = ["Allergy", "OPEN ACCESS", "Received:", "Revised:", "Accepted:", "Published on:"]
    return [f"Wiley PDF still contains template placeholder text: {term}" for term in forbidden if term in text]


def check_submission_zip() -> list[str]:
    if not SUBMISSION_ZIP.exists():
        return []
    try:
        with zipfile.ZipFile(SUBMISSION_ZIP) as archive:
            names = set(archive.namelist())
            failures = [
                f"submission zip missing {member}"
                for member in sorted(EXPECTED_ZIP_MEMBERS - names)
            ]
            with WILEY_PDF.open("rb") as pdf:
                if archive.read("lobby-capture-wiley-submission/main.pdf") != pdf.read():
                    failures.append("submission zip main.pdf differs from paper/regulation-governance-wiley.pdf")
            return failures
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        return [f"could not inspect submission zip: {error}"]


if __name__ == "__main__":
    raise SystemExit(main())
