#!/usr/bin/env python3
"""Audit Wiley Research Exchange upload readiness for the submission bundle."""

from __future__ import annotations

import csv
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PAPER = ROOT / "paper"
DIST = ROOT / "dist"

LOCAL_BASENAME = "strategic-channel-substitution-regulatory-capture"
SUBMISSION_ZIP = DIST / "lobby-capture-wiley-submission.zip"
WILEY_PDF = PAPER / "regulation-governance-wiley.pdf"
SUPPLEMENT_PDF = PAPER / "supplement.pdf"
SUBMISSION_DECLARATIONS = PAPER / "sections" / "submission-declarations.tex"
SUBMISSION_STRATEGY = ROOT / "docs" / "submission-strategy.md"
SUBMISSION_CHECKLIST = ROOT / "docs" / "submission-release-checklist.md"

MAX_UPLOAD_BYTES = 500 * 1024 * 1024
MAX_FILENAME_CHARS = 256
UNSUPPORTED_UPLOAD_SUFFIXES = {".exe", ".bat", ".cmd", ".com", ".js", ".vbs"}
EXPECTED_ROOT_MEMBERS = {
    f"{LOCAL_BASENAME}.tex",
    f"{LOCAL_BASENAME}.pdf",
    "supplement.tex",
    "supplement.pdf",
    "references.bib",
}
EXPECTED_SUPPORT_MEMBERS = {
    "USG.cls",
    "lettersp.sty",
    "wileyNJD-Chicago.bst",
    "supporting-information/submission-package-manifest.json",
    "supporting-information/submission-package-manifest.md",
    "supporting-information/CITATION.cff",
    "supporting-information/zenodo.json",
    "supporting-information/final-human-readthrough.md",
    "supporting-information/final-human-readthrough-audit.md",
}
EXPECTED_PREFIXES = {
    "figures/",
    "tables/",
    "sections/",
    "supporting-information/report-data/",
}


def main() -> int:
    rows = readiness_rows()
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "wiley-submission-form-readiness.csv", rows)
    (REPORTS / "wiley-submission-form-readiness.md").write_text(
        markdown(rows),
        encoding="utf-8",
    )
    print("Wrote reports/wiley-submission-form-readiness.csv")
    print("Wrote reports/wiley-submission-form-readiness.md")
    return 0


def readiness_rows() -> list[dict[str, str]]:
    package = inspect_package()
    names = set(package["names"])
    upload_files = [SUBMISSION_ZIP, WILEY_PDF, SUPPLEMENT_PDF]
    upload_bytes = sum(path.stat().st_size for path in upload_files if path.exists())
    unsupported_members = sorted(
        name for name in names if Path(name).suffix.lower() in UNSUPPORTED_UPLOAD_SUFFIXES
    )
    unsupported_upload_files = sorted(
        path.name for path in upload_files if path.suffix.lower() in UNSUPPORTED_UPLOAD_SUFFIXES
    )
    long_upload_names = [path.name for path in upload_files if len(path.name) > MAX_FILENAME_CHARS]
    long_member_names = [
        name
        for name in names
        if len(name) > MAX_FILENAME_CHARS or len(Path(name).name) > MAX_FILENAME_CHARS
    ]

    missing_root = sorted(EXPECTED_ROOT_MEMBERS - names)
    missing_support = sorted(EXPECTED_SUPPORT_MEMBERS - names)
    missing_prefixes = sorted(prefix for prefix in EXPECTED_PREFIXES if not any(name.startswith(prefix) for name in names))
    declarations = read_text(SUBMISSION_DECLARATIONS)
    strategy = read_text(SUBMISSION_STRATEGY)
    checklist = read_text(SUBMISSION_CHECKLIST)

    rows = [
        row(
            "submission-archive-present",
            "ready" if package["exists"] and package["readable"] and not package["encrypted"] else "blocked",
            (
                f"exists={yes_no(package['exists'])}; readable={yes_no(package['readable'])}; "
                f"encrypted={yes_no(package['encrypted'])}; members={yes_no(bool(names))}"
            ),
            "Upload the ZIP only if it opens without encryption or structural errors.",
        ),
        row(
            "upload-size",
            "ready" if upload_bytes > 0 and upload_bytes <= MAX_UPLOAD_BYTES else "blocked",
            (
                f"combined upload size={'within limit' if upload_bytes <= MAX_UPLOAD_BYTES and upload_bytes > 0 else 'outside limit'}; "
                f"upload files present={sum(1 for path in upload_files if path.exists())}/{len(upload_files)}; "
                f"limit={MAX_UPLOAD_BYTES}"
            ),
            "Keep the LaTeX ZIP, compiled PDF, and supplement below Wiley's 500 MB combined-file limit.",
        ),
        row(
            "filename-length",
            "ready" if not long_upload_names and not long_member_names else "blocked",
            (
                f"long upload names={len(long_upload_names)}; "
                f"long ZIP member names={len(long_member_names)}; limit={MAX_FILENAME_CHARS}"
            ),
            "Rename files before upload if any upload file or ZIP member exceeds Wiley's file-name limit.",
        ),
        row(
            "root-latex-and-pdf",
            "ready" if not missing_root and root_file(names, f"{LOCAL_BASENAME}.tex") and root_file(names, f"{LOCAL_BASENAME}.pdf") else "blocked",
            f"missing root files={'; '.join(missing_root) if missing_root else 'none'}",
            "Keep the main .tex file and compiled peer-review PDF at the ZIP root.",
        ),
        row(
            "supporting-files",
            "ready" if not missing_support and not missing_prefixes else "blocked",
            (
                f"missing support files={'; '.join(missing_support) if missing_support else 'none'}; "
                f"missing directories={'; '.join(missing_prefixes) if missing_prefixes else 'none'}"
            ),
            "Retain bibliography, class/style files, figures, tables, declarations, and supporting-information manifests.",
        ),
        row(
            "unsupported-upload-formats",
            "ready" if not unsupported_members and not unsupported_upload_files else "blocked",
            (
                f"unsupported upload files={'; '.join(unsupported_upload_files) if unsupported_upload_files else 'none'}; "
                f"unsupported ZIP members={'; '.join(unsupported_members) if unsupported_members else 'none'}"
            ),
            "Remove executable or script-format files before upload.",
        ),
        row(
            "data-and-ai-statements",
            "ready" if declarations_ready(declarations) else "blocked",
            data_ai_evidence(declarations),
            "Keep data/code availability, excluded-credentials language, AI use disclosure, funding, and conflict statements in the manuscript.",
        ),
        row(
            "journal-specific-author-guidelines",
            "manual_required",
            journal_guideline_evidence(strategy, checklist),
            "Before live submission, re-check the Regulation & Governance author page because Wiley says journal-specific instructions override generic Wiley guidance.",
        ),
    ]
    return rows


def inspect_package() -> dict[str, object]:
    if not SUBMISSION_ZIP.exists():
        return {"exists": False, "readable": False, "encrypted": False, "names": []}
    try:
        with zipfile.ZipFile(SUBMISSION_ZIP) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            encrypted = any(info.flag_bits & 0x1 for info in infos)
            return {
                "exists": True,
                "readable": True,
                "encrypted": encrypted,
                "names": [info.filename for info in infos],
            }
    except (OSError, zipfile.BadZipFile):
        return {"exists": True, "readable": False, "encrypted": False, "names": []}


def root_file(names: set[str], name: str) -> bool:
    return name in names and "/" not in name


def declarations_ready(text: str) -> bool:
    required = [
        "Data and Code Availability",
        "MIT License",
        "Private credentials and raw API payload archives are intentionally excluded",
        "AI Use Disclosure",
        "AI tools were not used to fabricate, alter, or manipulate empirical source data or simulation results",
        "Funding",
        "Conflict of Interest",
    ]
    return all(phrase in text for phrase in required)


def data_ai_evidence(text: str) -> str:
    checks = {
        "data availability": "Data and Code Availability" in text,
        "license": "MIT License" in text,
        "private/raw exclusion": "Private credentials and raw API payload archives are intentionally excluded" in text,
        "AI disclosure": "AI Use Disclosure" in text,
        "AI no data fabrication": "AI tools were not used to fabricate, alter, or manipulate empirical source data or simulation results" in text,
        "funding": "Funding" in text,
        "conflicts": "Conflict of Interest" in text,
    }
    return "; ".join(f"{name}={yes_no(ok)}" for name, ok in checks.items())


def journal_guideline_evidence(strategy: str, checklist: str) -> str:
    strategy_note = "Before live submission, re-check the Regulation & Governance author page" in strategy
    checklist_note = "If a Zenodo, OSF, or institutional archive DOI is created" in checklist
    return (
        f"strategy reminder={yes_no(strategy_note)}; "
        f"DOI checklist reminder={yes_no(checklist_note)}; "
        "manual journal-specific author-guidelines refresh required"
    )


def row(gate: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=["gate", "status", "evidence", "nextAction"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    ready = sum(1 for item in rows if item["status"] == "ready")
    manual = sum(1 for item in rows if item["status"] == "manual_required")
    blocked = sum(1 for item in rows if item["status"] == "blocked")
    mechanical = "ready" if blocked == 0 else "blocked"
    lines = [
        "# Wiley Submission Form Readiness",
        "",
        "This audit checks Wiley Research Exchange upload mechanics for the generated LaTeX submission bundle. It does not replace a live journal-specific author-guidelines check.",
        "",
        "## Summary",
        "",
        f"- Mechanical upload status: `{mechanical}`",
        f"- Ready gates: `{ready}`",
        f"- Manual-required gates: `{manual}`",
        f"- Blocked gates: `{blocked}`",
        "",
        "## Gate Matrix",
        "",
        "| Gate | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {gate} | {status} | {evidence} | {nextAction} |".format(
                gate=md(item["gate"]),
                status=md(item["status"]),
                evidence=md(item["evidence"]),
                nextAction=md(item["nextAction"]),
            )
        )
    lines.extend([
        "",
        "## Upload Notes",
        "",
        "Wiley guidance says LaTeX submissions may use a ZIP archive containing the root `.tex`, compiled PDF, bibliography, classes/packages, figures, tables, and supporting files. It also asks authors to provide a single compiled PDF for peer review and to avoid unsupported executable or script upload formats.",
        "",
        "The journal-specific author-guidelines gate remains manual because Regulation & Governance instructions may override generic Wiley guidance at live submission time.",
        "",
    ])
    return "\n".join(lines)


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def yes_no(value: object) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
