#!/usr/bin/env python3
"""Check that generated paper PDFs and submission artifacts are current."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DIST = ROOT / "dist"

LOCAL_PDF = PAPER / "main.pdf"
WILEY_PDF = PAPER / "regulation-governance-wiley.pdf"
SUBMISSION_ZIP = DIST / "lobby-capture-wiley-submission.zip"

EXPECTED_ZIP_MEMBERS = {
    "main.tex",
    "main.pdf",
    "references.bib",
    "USG.cls",
    "lettersp.sty",
    "wileyNJD-Chicago.bst",
    "SUBMISSION_README.txt",
    "sections/reggov-body.tex",
    "sections/submission-declarations.tex",
    "tables/campaign_snapshot.tex",
    "tables/sensitivity_snapshot.tex",
    "tables/ablation_snapshot.tex",
    "tables/interaction_snapshot.tex",
    "figures/Figure_1_channel_mix.pdf",
    "figures/Figure_2_evasion_sensitivity.pdf",
    "figures/Figure_3_interaction_tradeoffs.pdf",
    "figures/Figure_4_scenario_tradeoffs.pdf",
    "supporting-information/ODD-model.md",
    "supporting-information/scenario-catalog.md",
    "supporting-information/validation-plan.md",
    "supporting-information/source-moments.md",
    "supporting-information/validation-summary.md",
    "supporting-information/calibration-queue.md",
}


def main() -> int:
    failures: list[str] = []
    failures.extend(check_exists([LOCAL_PDF, WILEY_PDF, SUBMISSION_ZIP]))
    failures.extend(check_freshness())
    failures.extend(check_wiley_text())
    failures.extend(check_submission_zip())
    failures.extend(check_submission_zip_compiles())

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
        ROOT / "docs" / "odd-model.md",
        ROOT / "docs" / "scenario-catalog.md",
        ROOT / "docs" / "validation.md",
        ROOT / "reports" / "source-moments.md",
        ROOT / "reports" / "validation-summary.md",
        ROOT / "reports" / "calibration-queue.md",
        PAPER / ".wiley-build" / "USG.cls",
        PAPER / ".wiley-build" / "wileyNJD-Chicago.bst",
        PAPER / ".wiley-template" / "Optimal-Design-layout" / "LETTERSP.STY",
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
                if archive.read("main.pdf") != pdf.read():
                    failures.append("submission zip main.pdf differs from paper/regulation-governance-wiley.pdf")
            return failures
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        return [f"could not inspect submission zip: {error}"]


def check_submission_zip_compiles() -> list[str]:
    if not SUBMISSION_ZIP.exists():
        return []
    required = ["pdflatex", "bibtex"]
    missing = [binary for binary in required if shutil.which(binary) is None]
    if missing:
        return [f"could not compile submission zip; missing binaries: {', '.join(missing)}"]

    with tempfile.TemporaryDirectory(prefix="lobby-capture-submission-") as temp_dir:
        temp = Path(temp_dir)
        try:
            with zipfile.ZipFile(SUBMISSION_ZIP) as archive:
                archive.extractall(temp)
        except (OSError, zipfile.BadZipFile) as error:
            return [f"could not extract submission zip for compile check: {error}"]

        env = os.environ.copy()
        for key in ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS"):
            env.pop(key, None)
        commands = [
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            ["bibtex", "main"],
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
        ]
        for command in commands:
            result = subprocess.run(
                command,
                cwd=temp,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if command[0] == "pdflatex" and is_nonfatal_latex_pass(result.stdout, temp / "main.pdf"):
                continue
            if result.returncode != 0:
                tail = "\n".join(result.stdout.splitlines()[-20:])
                return [
                    "submission zip does not compile from extracted root with "
                    f"`{' '.join(command)}`:\n{tail}"
                ]
        final_log = temp / "main.log"
        if not final_log.exists():
            return ["submission zip compile check did not produce main.log"]
        log_text = final_log.read_text(encoding="utf-8", errors="replace")
        unresolved_markers = [
            "There were undefined citations",
            "Citation(s) may have changed",
            "There were undefined references",
            "Rerun to get cross-references right",
        ]
        failures = [marker for marker in unresolved_markers if marker in log_text]
        if failures:
            return [
                "submission zip compile ended with unresolved LaTeX state: "
                + ", ".join(failures)
            ]
    return []


def is_nonfatal_latex_pass(output: str, pdf_path: Path) -> bool:
    if "Output written on main.pdf" not in output or not pdf_path.exists():
        return False
    fatal_markers = [
        "! LaTeX Error:",
        "! Emergency stop.",
        "Fatal error occurred",
        " ==> Fatal error occurred",
    ]
    return not any(marker in output for marker in fatal_markers)


if __name__ == "__main__":
    raise SystemExit(main())
