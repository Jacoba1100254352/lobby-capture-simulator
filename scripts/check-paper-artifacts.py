#!/usr/bin/env python3
"""Check that generated paper PDFs and submission artifacts are current."""

from __future__ import annotations

import os
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DIST = ROOT / "dist"

LOCAL_BASENAME = "strategic-channel-substitution-regulatory-capture"
LOCAL_TEX = PAPER / f"{LOCAL_BASENAME}.tex"
LOCAL_PDF = PAPER / f"{LOCAL_BASENAME}.pdf"
WILEY_PDF = PAPER / "regulation-governance-wiley.pdf"
SUPPLEMENT_PDF = PAPER / "supplement.pdf"
SUBMISSION_ZIP = DIST / "lobby-capture-wiley-submission.zip"
SUBMISSION_DECLARATIONS = PAPER / "sections" / "submission-declarations.tex"
REGGOV_BODY = PAPER / "sections" / "reggov-body.tex"
VALIDATION_SUMMARY = ROOT / "reports" / "validation-summary.md"
LAYOUT_AUDIT = ROOT / "reports" / "paper-layout-audit.md"
MANUAL_VISUAL_AUDIT = ROOT / "reports" / "manual-visual-audit.md"
RELEASE_TAG = "paper-publication-readiness-2026-06-11-r18"
CITATION_CFF = ROOT / "CITATION.cff"
ZENODO_JSON = ROOT / ".zenodo.json"
FORBIDDEN_LOCAL_ARTIFACTS = [
    PAPER / "main.tex",
    PAPER / "main.pdf",
]
FORBIDDEN_LOCAL_COPY_SUFFIX = re.compile(
    r".+ [0-9]+\.(aux|bbl|blg|log|out|pag|pdf|tex)$",
    re.IGNORECASE,
)
FORBIDDEN_DIST_COPY_SUFFIX = re.compile(
    r"lobby-capture-wiley-submission [0-9]+\.zip$",
    re.IGNORECASE,
)
FORBIDDEN_ZIP_MEMBERS = {
    "main.tex",
    "main.pdf",
    "supporting-information/submission-release-checklist.md",
}

EXPECTED_ZIP_MEMBERS = {
    f"{LOCAL_BASENAME}.tex",
    f"{LOCAL_BASENAME}.pdf",
    "supplement.tex",
    "supplement.pdf",
    "references.bib",
    "USG.cls",
    "lettersp.sty",
    "wileyNJD-Chicago.bst",
    "SUBMISSION_README.txt",
    "sections/reggov-body.tex",
    "sections/submission-declarations.tex",
    "tables/mechanism_comparison.tex",
    "tables/campaign_snapshot.tex",
    "tables/full_campaign_appendix.tex",
    "tables/distortion_decomposition.tex",
    "tables/apparent_failure_ranking.tex",
    "tables/substitution_warning_ranking.tex",
    "tables/composite_weights.tex",
    "tables/validation_gap_snapshot.tex",
    "tables/sensitivity_snapshot.tex",
    "tables/ablation_snapshot.tex",
    "tables/interaction_snapshot.tex",
    "tables/portfolio_snapshot.tex",
    "figures/Figure_1_model_architecture.pdf",
    "tables/switch_rule_snapshot.tex",
    "tables/diagnostic_variant_snapshot.tex",
    "figures/Figure_1_channel_mix.pdf",
    "figures/Figure_2_evasion_sensitivity.pdf",
    "figures/Figure_3_interaction_tradeoffs.pdf",
    "figures/Figure_4_scenario_tradeoffs.pdf",
    "figures/Figure_5_substitution_warning_map.pdf",
    "figures/Figure_1_channel_mix.svg",
    "figures/Figure_1_model_architecture.svg",
    "figures/Figure_2_evasion_sensitivity.svg",
    "figures/Figure_3_interaction_tradeoffs.svg",
    "figures/Figure_4_scenario_tradeoffs.svg",
    "figures/Figure_5_substitution_warning_map.svg",
    "figures/channel_mix.tex",
    "figures/evasion_sensitivity.tex",
    "figures/interaction_tradeoffs.tex",
    "figures/model_architecture.tex",
    "figures/scenario_tradeoffs.tex",
    "figures/substitution_warning_map.tex",
    "supporting-information/ODD-model.md",
    "supporting-information/scenario-catalog.md",
    "supporting-information/validation-plan.md",
    "supporting-information/source-data-roadmap.md",
    "supporting-information/source-moments.md",
    "supporting-information/source-panel-inventory.md",
    "supporting-information/validation-summary.md",
    "supporting-information/substitution-audit.md",
    "supporting-information/portfolio-screen.md",
    "supporting-information/calibration-queue.md",
    "supporting-information/paper-layout-audit.md",
    "supporting-information/manual-visual-audit.md",
    "supporting-information/CITATION.cff",
    "supporting-information/zenodo.json",
}


def main() -> int:
    failures: list[str] = []
    failures.extend(check_exists([LOCAL_PDF, WILEY_PDF, SUPPLEMENT_PDF, SUBMISSION_ZIP]))
    failures.extend(check_forbidden_local_artifacts())
    failures.extend(check_freshness())
    failures.extend(check_wiley_text())
    failures.extend(check_submission_statements())
    failures.extend(check_claim_alignment())
    failures.extend(check_layout_and_visual_reports())
    failures.extend(check_archive_metadata())
    failures.extend(check_release_tag_exactness())
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


def check_forbidden_local_artifacts() -> list[str]:
    failures = [
        f"stale generic paper artifact remains: {path.relative_to(ROOT)}"
        for path in FORBIDDEN_LOCAL_ARTIFACTS
        if path.exists()
    ]
    failures.extend(
        f"duplicate copy-suffix paper artifact remains: {path.relative_to(ROOT)}"
        for path in sorted(PAPER.iterdir())
        if path.is_file() and FORBIDDEN_LOCAL_COPY_SUFFIX.fullmatch(path.name)
    )
    if DIST.exists():
        failures.extend(
            f"duplicate copy-suffix submission archive remains: {path.relative_to(ROOT)}"
            for path in sorted(DIST.iterdir())
            if path.is_file() and FORBIDDEN_DIST_COPY_SUFFIX.fullmatch(path.name)
        )
    return failures


def check_freshness() -> list[str]:
    failures: list[str] = []
    checks = [
        (LOCAL_PDF, local_pdf_inputs()),
        (WILEY_PDF, wiley_pdf_inputs()),
        (SUPPLEMENT_PDF, supplement_pdf_inputs()),
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
        LOCAL_TEX,
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


def supplement_pdf_inputs() -> list[Path]:
    return [
        PAPER / "supplement.tex",
        PAPER / "references.bib",
        PAPER / "sections" / "supplement-body.tex",
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
    ]


def submission_inputs() -> list[Path]:
    return [
        WILEY_PDF,
        SUPPLEMENT_PDF,
        PAPER / "regulation-governance-wiley.tex",
        PAPER / "supplement.tex",
        PAPER / "references.bib",
        ROOT / "scripts" / "build-submission-package.sh",
        CITATION_CFF,
        ZENODO_JSON,
        ROOT / "docs" / "odd-model.md",
        ROOT / "docs" / "scenario-catalog.md",
        ROOT / "docs" / "validation.md",
        ROOT / "docs" / "source-data-roadmap.md",
        ROOT / "reports" / "source-moments.md",
        ROOT / "reports" / "source-panel-inventory.md",
        ROOT / "reports" / "validation-summary.md",
        ROOT / "reports" / "substitution-audit.md",
        ROOT / "reports" / "lobby-capture-portfolio.md",
        ROOT / "reports" / "calibration-queue.md",
        ROOT / "reports" / "paper-layout-audit.md",
        ROOT / "reports" / "manual-visual-audit.md",
        PAPER / ".wiley-build" / "USG.cls",
        PAPER / ".wiley-build" / "wileyNJD-Chicago.bst",
        PAPER / ".wiley-template" / "Optimal-Design-layout" / "LETTERSP.STY",
        *sorted((PAPER / "sections").glob("*.tex")),
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
        *sorted((PAPER / "figures").glob("Figure_*.svg")),
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


def check_submission_statements() -> list[str]:
    if not SUBMISSION_DECLARATIONS.exists():
        return [f"missing submission declarations: {SUBMISSION_DECLARATIONS.relative_to(ROOT)}"]
    text = SUBMISSION_DECLARATIONS.read_text(encoding="utf-8")
    failures: list[str] = []
    forbidden = [
        "No external DOI",
        "should be minted",
        "before external journal submission",
        "working draft",
    ]
    failures.extend(
        f"submission declarations contain pre-submission archive language: {phrase}"
        for phrase in forbidden
        if phrase in text
    )
    required = [
        RELEASE_TAG,
        f"/releases/tag/{RELEASE_TAG}",
        "MIT License",
        "Private credentials and raw API payload archives are intentionally excluded",
    ]
    failures.extend(
        f"submission declarations missing required availability detail: {phrase}"
        for phrase in required
        if phrase not in text
    )
    return failures


def check_claim_alignment() -> list[str]:
    if not REGGOV_BODY.exists() or not VALIDATION_SUMMARY.exists():
        return []
    body = REGGOV_BODY.read_text(encoding="utf-8")
    validation = VALIDATION_SUMMARY.read_text(encoding="utf-8")
    if "- Miss: `0`" in validation and "benchmark misses" in body:
        return [
            "manuscript still refers to benchmark misses even though validation-summary.md reports Miss: 0",
        ]
    return []


def check_layout_and_visual_reports() -> list[str]:
    failures: list[str] = []
    if not LAYOUT_AUDIT.exists():
        failures.append(f"missing layout audit report: {LAYOUT_AUDIT.relative_to(ROOT)}")
    else:
        layout = LAYOUT_AUDIT.read_text(encoding="utf-8")
        if "- Failures: `0`" not in layout:
            failures.append("paper layout audit reports at least one failure")

    if not MANUAL_VISUAL_AUDIT.exists():
        failures.append(f"missing visual review report: {MANUAL_VISUAL_AUDIT.relative_to(ROOT)}")
    else:
        visual = MANUAL_VISUAL_AUDIT.read_text(encoding="utf-8")
        if "needs review" in visual:
            failures.append("visual review checklist contains at least one needs review entry")
        if "Layout audit has not been generated yet" in visual:
            failures.append("visual review checklist was generated without a layout audit")
    return failures


def check_archive_metadata() -> list[str]:
    failures: list[str] = []
    for path in (CITATION_CFF, ZENODO_JSON):
        if not path.exists():
            failures.append(f"missing archive metadata file: {path.relative_to(ROOT)}")
    if CITATION_CFF.exists():
        citation = CITATION_CFF.read_text(encoding="utf-8")
        required = [
            "cff-version: 1.2.0",
            f'version: "{RELEASE_TAG}"',
            f'url: "https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{RELEASE_TAG}"',
            "license: MIT",
            "preferred-citation:",
        ]
        failures.extend(
            f"CITATION.cff missing required release metadata: {phrase}"
            for phrase in required
            if phrase not in citation
        )
    if ZENODO_JSON.exists():
        try:
            zenodo = json.loads(ZENODO_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            return [*failures, f".zenodo.json is not valid JSON: {error}"]
        required_pairs = {
            "title": "Lobby Capture Simulator: Strategic Channel Substitution in Regulatory Capture",
            "upload_type": "software",
            "license": "MIT",
        }
        failures.extend(
            f".zenodo.json missing or changed required field {key}={value!r}"
            for key, value in required_pairs.items()
            if zenodo.get(key) != value
        )
        related = zenodo.get("related_identifiers", [])
        if not any(
            isinstance(item, dict)
            and item.get("identifier")
            == f"https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{RELEASE_TAG}"
            for item in related
        ):
            failures.append(".zenodo.json missing related identifier for the current release tag")
    return failures


def check_release_tag_exactness() -> list[str]:
    if os.environ.get("LOBBY_CAPTURE_REQUIRE_RELEASE_TAG") != "1":
        return []
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        tagged = subprocess.check_output(
            ["git", "rev-parse", f"{RELEASE_TAG}^{{commit}}"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        return [
            "could not verify review-bundle release tag; "
            f"fetch or create {RELEASE_TAG}: {error}"
        ]
    if tagged != head:
        return [
            f"review-bundle release tag {RELEASE_TAG} points at {tagged[:12]}, "
            f"but HEAD is {head[:12]}"
        ]
    return []


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
            failures.extend(
                f"submission zip should not contain generic {member}"
                for member in sorted(FORBIDDEN_ZIP_MEMBERS & names)
            )
            with WILEY_PDF.open("rb") as pdf:
                if archive.read(f"{LOCAL_BASENAME}.pdf") != pdf.read():
                    failures.append(
                        f"submission zip {LOCAL_BASENAME}.pdf differs from paper/regulation-governance-wiley.pdf"
                    )
            with SUPPLEMENT_PDF.open("rb") as pdf:
                if archive.read("supplement.pdf") != pdf.read():
                    failures.append("submission zip supplement.pdf differs from paper/supplement.pdf")
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
            ["pdflatex", "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            ["bibtex", LOCAL_BASENAME],
            ["pdflatex", "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            ["pdflatex", "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            ["pdflatex", "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            ["pdflatex", "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
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
            if command[0] == "pdflatex" and is_nonfatal_latex_pass(result.stdout, temp / f"{LOCAL_BASENAME}.pdf"):
                continue
            if result.returncode != 0:
                tail = "\n".join(result.stdout.splitlines()[-20:])
                return [
                    "submission zip does not compile from extracted root with "
                    f"`{' '.join(command)}`:\n{tail}"
                ]
        final_log = temp / f"{LOCAL_BASENAME}.log"
        if not final_log.exists():
            return [f"submission zip compile check did not produce {LOCAL_BASENAME}.log"]
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
        supplement_failures = compile_supplement(temp, env)
        if supplement_failures:
            return supplement_failures
    return []


def compile_supplement(temp: Path, env: dict[str, str]) -> list[str]:
    if not (temp / "supplement.tex").exists():
        return ["submission zip compile check did not find supplement.tex"]
    commands = [
        ["pdflatex", "-interaction=nonstopmode", "supplement.tex"],
        ["pdflatex", "-interaction=nonstopmode", "supplement.tex"],
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
        if command[0] == "pdflatex" and is_nonfatal_latex_pass(result.stdout, temp / "supplement.pdf"):
            continue
        if result.returncode != 0:
            tail = "\n".join(result.stdout.splitlines()[-20:])
            return [
                "submission supplement does not compile from extracted root with "
                f"`{' '.join(command)}`:\n{tail}"
            ]
    return []


def is_nonfatal_latex_pass(output: str, pdf_path: Path) -> bool:
    if f"Output written on {pdf_path.name}" not in output or not pdf_path.exists():
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
