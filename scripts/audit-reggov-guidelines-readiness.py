#!/usr/bin/env python3
"""Audit locally verifiable Regulation & Governance submission guidelines."""

from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"

FINAL_HUMAN_READTHROUGH = REPORTS / "final-human-readthrough.md"
CITATION_CFF = ROOT / "CITATION.cff"
LOCAL_BASENAME = "strategic-channel-substitution-regulatory-capture"
LOCAL_TEX = PAPER / f"{LOCAL_BASENAME}.tex"
LOCAL_BBL = PAPER / f"{LOCAL_BASENAME}.bbl"
WILEY_TEX = PAPER / "regulation-governance-wiley.tex"
WILEY_PDF = PAPER / "regulation-governance-wiley.pdf"
SUPPLEMENT_TEX = PAPER / "supplement.tex"
SUPPLEMENT_PDF = PAPER / "supplement.pdf"
SUBMISSION_DECLARATIONS = PAPER / "sections" / "submission-declarations.tex"
SUBMISSION_ZIP = DIST / "lobby-capture-wiley-submission.zip"
WILEY_FORM_CSV = REPORTS / "wiley-submission-form-readiness.csv"

MIN_WORDS = 8000
MAX_WORDS = 10000
WORD_RANGE_LABEL = "8,000-10,000"
REGGOV_AUTHOR_GUIDELINES_URL = "https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html"
WILEY_SUBMISSION_HELP_URL = "https://authors.wiley.com/help/submitting-your-manuscript.html"
WILEY_LATEX_URL = "https://authors.wiley.com/author-resources/Journal-Authors/Prepare/latex-template.html"
WILEY_AI_URL = "https://www.wiley.com/en-us/publish/article/ai-guidelines/"
WILEY_SUPPORTING_INFO_URL = (
    "https://authors.wiley.com/author-resources/Journal-Authors/Prepare/"
    "manuscript-preparation-guidelines.html/supporting-information.html"
)
SUPPORTING_INFO_MAX_BYTES = 10 * 1024 * 1024
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def main() -> int:
    rows = guideline_rows()
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "reggov-guidelines-readiness.csv", rows)
    (REPORTS / "reggov-guidelines-readiness.md").write_text(markdown(rows), encoding="utf-8")
    print("Wrote reports/reggov-guidelines-readiness.csv")
    print("Wrote reports/reggov-guidelines-readiness.md")
    return 0


def guideline_rows() -> list[dict[str, str]]:
    local = read_text(LOCAL_TEX)
    wiley = read_text(WILEY_TEX)
    declarations = read_text(SUBMISSION_DECLARATIONS)
    package = inspect_package()
    names = set(package["names"])
    words = manuscript_word_count()
    figure_pdfs = sorted((PAPER / "figures").glob("Figure_*.pdf"))
    figure_svgs = sorted((PAPER / "figures").glob("Figure_*.svg"))
    figure_wrappers = sorted((PAPER / "figures").glob("*.tex"))
    tables = sorted((PAPER / "tables").glob("*.tex"))
    wiley_form_rows = read_gate_rows(WILEY_FORM_CSV)
    live_author_page = live_author_page_refresh_state()

    rows = [
        row(
            "journal-target-and-article-type",
            "ready" if journal_target_ready(local, wiley) else "blocked",
            journal_target_evidence(local, wiley),
            "Keep the Wiley wrapper targeted to Regulation & Governance as an original article.",
        ),
        row(
            "word-limit",
            "ready" if MIN_WORDS <= words <= MAX_WORDS else "blocked",
            (
                f"approximate words={words}; "
                f"Regulation & Governance reported preferred range={MIN_WORDS}-{MAX_WORDS}"
            ),
            "Revise the manuscript if the approximate count falls outside the reported preferred range.",
        ),
        row(
            "abstract-and-keywords",
            "ready" if abstract_keywords_ready(local, wiley) else "blocked",
            abstract_keywords_evidence(local, wiley),
            "Retain extractable abstract and keyword metadata in both local and Wiley wrappers.",
        ),
        row(
            "title-page-metadata",
            "ready" if title_metadata_ready(local, wiley) else "blocked",
            title_metadata_evidence(local, wiley),
            "Keep author name, affiliation, country, correspondence, and email metadata present.",
        ),
        row(
            "data-code-availability",
            "ready" if data_code_ready(declarations) else "blocked",
            data_code_evidence(declarations),
            "Maintain repository, release, license, private-credential, and source-snapshot details.",
        ),
        row(
            "ai-funding-conflict-disclosures",
            "ready" if disclosure_ready(declarations, wiley) else "blocked",
            disclosure_evidence(declarations, wiley),
            "Keep AI use, human responsibility, funding, and conflict statements in the manuscript.",
        ),
        row(
            "figures-and-tables",
            "ready" if figures_tables_ready(figure_pdfs, figure_svgs, figure_wrappers, tables, names) else "blocked",
            figures_tables_evidence(figure_pdfs, figure_svgs, figure_wrappers, tables, names),
            "Retain generated PDF graphics, reproducible SVG sources, LaTeX wrappers, and table files.",
        ),
        row(
            "supporting-information",
            "ready" if supporting_information_ready(names) else "blocked",
            supporting_information_evidence(names),
            "Keep supplement files, ODD model, scenario catalog, validation plan, source roadmap, and report data in the package.",
        ),
        row(
            "supporting-information-format-size",
            (
                "ready"
                if supporting_information_format_size_ready(names, package["sizes"])
                else "blocked"
            ),
            supporting_information_format_size_evidence(names, package["sizes"]),
            "Keep every supporting-information member clearly labeled and at or below Wiley's 10 MB per-file guidance.",
        ),
        row(
            "latex-submission-files",
            "ready" if latex_submission_ready(package, names, wiley_form_rows) else "blocked",
            latex_submission_evidence(package, names, wiley_form_rows),
            "Keep the ZIP, root .tex, compiled PDF, bibliography, class/style files, figures, tables, and package manifest together.",
        ),
        row(
            "live-reggov-author-page-refresh",
            "ready" if live_author_page["ready"] else "manual_required",
            live_author_page["evidence"],
            live_author_page["nextAction"],
        ),
    ]
    return rows


def live_author_page_refresh_state() -> dict[str, str | bool]:
    text = read_text(FINAL_HUMAN_READTHROUGH)
    current_release = current_release_tag()
    reviewed_release = field_value(text, "reviewed-release")
    checked_by = field_value(text, "author-guidelines-checked-by")
    checked_date = field_value(text, "author-guidelines-checked-date")
    url = field_value(text, "author-guidelines-url")
    superseding = field_value(text, "author-guidelines-superseding-instructions")
    superseding_normalized = superseding.strip().lower()
    no_superseding = superseding_normalized in {
        "none",
        "no",
        "none identified",
        "no superseding instructions",
    }
    ready = all(
        [
            reviewed_release == current_release,
            checked_by,
            checked_date,
            url == REGGOV_AUTHOR_GUIDELINES_URL,
            no_superseding,
        ]
    )
    evidence = (
        f"official URL recorded={REGGOV_AUTHOR_GUIDELINES_URL}; "
        f"record URL={'matches' if url == REGGOV_AUTHOR_GUIDELINES_URL else 'missing/mismatch'}; "
        f"checked-by={'present' if checked_by else 'missing'}; "
        f"checked-date={'present' if checked_date else 'missing'}; "
        f"reviewed-release={reviewed_release or 'missing'}; "
        f"expected-release={current_release or 'missing'}; "
        f"superseding-instructions={superseding_evidence(superseding, no_superseding)}"
    )
    return {
        "ready": ready,
        "evidence": evidence,
        "nextAction": (
            "Keep the recorded live author-page check with the final signoff."
            if ready
            else live_author_page_next_action(superseding)
        ),
    }


def superseding_evidence(value: str, no_superseding: bool) -> str:
    if no_superseding:
        return "none"
    stripped = " ".join(value.split())
    if not stripped:
        return "missing"
    if len(stripped) > 180:
        stripped = stripped[:177].rstrip() + "..."
    return f"not-cleared: {stripped}"


def live_author_page_next_action(superseding: str) -> str:
    if superseding.strip():
        return (
            "Complete the live journal author-page browser review and replace the recorded non-clearance "
            "reason with none only if no superseding instructions require package changes."
        )
    return (
        "Immediately before submission, open the live journal author page and record checker, date, URL, "
        "and superseding-instruction status in reports/final-human-readthrough.md."
    )


def journal_target_ready(local: str, wiley: str) -> bool:
    return all(
        [
            "Strategic Channel Substitution in Regulatory Capture" in local,
            "Strategic Channel Substitution in Regulatory Capture" in wiley,
            r"\journal{Regulation \& Governance}" in wiley,
            r"\articletype{ORIGINAL ARTICLE}" in wiley,
            "Target venue: Regulation & Governance" in wiley,
        ]
    )


def journal_target_evidence(local: str, wiley: str) -> str:
    checks = {
        "local title": "Strategic Channel Substitution in Regulatory Capture" in local,
        "Wiley title": "Strategic Channel Substitution in Regulatory Capture" in wiley,
        "journal metadata": r"\journal{Regulation \& Governance}" in wiley,
        "article type": r"\articletype{ORIGINAL ARTICLE}" in wiley,
        "target comment": "Target venue: Regulation & Governance" in wiley,
    }
    return evidence(checks)


def manuscript_word_count() -> int:
    text = expand_inputs(LOCAL_TEX)
    if LOCAL_BBL.exists():
        text += "\n" + LOCAL_BBL.read_text(encoding="utf-8", errors="ignore")
    return count_words(text)


def expand_inputs(path: Path, seen: set[Path] | None = None) -> str:
    seen = seen or set()
    path = path.resolve()
    if path in seen or not path.exists():
        return ""
    seen.add(path)
    text = path.read_text(encoding="utf-8")

    def replace_input(match: re.Match[str]) -> str:
        raw_name = match.group(1).strip()
        name = raw_name if raw_name.endswith(".tex") else f"{raw_name}.tex"
        return expand_inputs((path.parent / name).resolve(), seen)

    return re.sub(r"\\input\{([^}]+)\}", replace_input, text)


def strip_latex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", " ", text)
    text = re.sub(
        r"\\begin\{(?:equation|align|displaymath)\*?\}.*?\\end\{(?:equation|align|displaymath)\*?\}",
        " ",
        text,
        flags=re.S,
    )
    text = re.sub(r"\$.*?\$", " ", text, flags=re.S)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    text = re.sub(r"[{}_^~&]", " ", text)
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z0-9'-]*", strip_latex(text)))


def abstract_keywords_ready(local: str, wiley: str) -> bool:
    return all(
        [
            r"\begin{abstract}" in local,
            r"\end{abstract}" in local,
            r"\textbf{Keywords:}" in local,
            r"\abstract[ABSTRACT]" in wiley,
            r"\keywords{" in wiley,
        ]
    )


def abstract_keywords_evidence(local: str, wiley: str) -> str:
    checks = {
        "local abstract": r"\begin{abstract}" in local and r"\end{abstract}" in local,
        "local keywords": r"\textbf{Keywords:}" in local,
        "Wiley abstract": r"\abstract[ABSTRACT]" in wiley,
        "Wiley keywords": r"\keywords{" in wiley,
    }
    return evidence(checks)


def title_metadata_ready(local: str, wiley: str) -> bool:
    return all(
        [
            r"\author{Jacob Anderson" in local,
            "Independent Researcher" in local,
            "United States" in local,
            "jacobdanderson@gmail.com" in local,
            r"\author[1]{Jacob Anderson}" in wiley,
            r"\address[1]" in wiley,
            r"\corres{" in wiley,
            "jacobdanderson@gmail.com" in wiley,
        ]
    )


def title_metadata_evidence(local: str, wiley: str) -> str:
    checks = {
        "local author": r"\author{Jacob Anderson" in local,
        "local affiliation": "Independent Researcher" in local,
        "local country": "United States" in local,
        "local email": "jacobdanderson@gmail.com" in local,
        "Wiley author": r"\author[1]{Jacob Anderson}" in wiley,
        "Wiley address": r"\address[1]" in wiley,
        "Wiley correspondence": r"\corres{" in wiley and "jacobdanderson@gmail.com" in wiley,
    }
    return evidence(checks)


def data_code_ready(declarations: str) -> bool:
    required = [
        "Data and Code Availability",
        "https://github.com/Jacoba1100254352/lobby-capture-simulator",
        "paper-publication-readiness-",
        "MIT License",
        "Private credentials and raw API payload archives are intentionally excluded",
        r"\texttt{data/snapshots/}",
    ]
    return all(phrase in declarations for phrase in required)


def data_code_evidence(declarations: str) -> str:
    checks = {
        "statement": "Data and Code Availability" in declarations,
        "repository": "https://github.com/Jacoba1100254352/lobby-capture-simulator" in declarations,
        "release tag": "paper-publication-readiness-" in declarations,
        "license": "MIT License" in declarations,
        "credential/raw exclusion": "Private credentials and raw API payload archives are intentionally excluded" in declarations,
        "snapshot path": r"\texttt{data/snapshots/}" in declarations,
    }
    return evidence(checks)


def disclosure_ready(declarations: str, wiley: str) -> bool:
    required = [
        "AI Use Disclosure",
        "The author reviewed and edited the output and is responsible",
        "AI tools were not used to fabricate, alter, or manipulate empirical source data or simulation results",
        "Funding",
        "No external funding is reported",
        "Conflict of Interest",
        "The author declares no conflicts of interest",
    ]
    return all(phrase in declarations for phrase in required) and r"\fundingInfo{No external funding is reported.}" in wiley


def disclosure_evidence(declarations: str, wiley: str) -> str:
    checks = {
        "AI disclosure": "AI Use Disclosure" in declarations,
        "human responsibility": "The author reviewed and edited the output and is responsible" in declarations,
        "AI no fabrication": "AI tools were not used to fabricate, alter, or manipulate empirical source data or simulation results" in declarations,
        "funding statement": "No external funding is reported" in declarations,
        "Wiley funding metadata": r"\fundingInfo{No external funding is reported.}" in wiley,
        "conflict statement": "The author declares no conflicts of interest" in declarations,
    }
    return evidence(checks)


def figures_tables_ready(
    figure_pdfs: list[Path],
    figure_svgs: list[Path],
    figure_wrappers: list[Path],
    tables: list[Path],
    names: set[str],
) -> bool:
    package_has_figures = any(name.startswith("figures/Figure_") and name.endswith(".pdf") for name in names)
    package_has_tables = any(name.startswith("tables/") and name.endswith(".tex") for name in names)
    return (
        len(figure_pdfs) >= 5
        and len(figure_svgs) >= 5
        and len(figure_wrappers) >= 5
        and len(tables) >= 10
        and package_has_figures
        and package_has_tables
    )


def figures_tables_evidence(
    figure_pdfs: list[Path],
    figure_svgs: list[Path],
    figure_wrappers: list[Path],
    tables: list[Path],
    names: set[str],
) -> str:
    package_pdf_figures = sum(1 for name in names if name.startswith("figures/Figure_") and name.endswith(".pdf"))
    package_tables = sum(1 for name in names if name.startswith("tables/") and name.endswith(".tex"))
    return (
        f"PDF figures={len(figure_pdfs)}; SVG sources={len(figure_svgs)}; "
        f"figure wrappers={len(figure_wrappers)}; table files={len(tables)}; "
        f"ZIP PDF figures={package_pdf_figures}; ZIP table files={package_tables}"
    )


def supporting_information_ready(names: set[str]) -> bool:
    required = {
        "supplement.tex",
        "supplement.pdf",
        "supporting-information/ODD-model.md",
        "supporting-information/scenario-catalog.md",
        "supporting-information/validation-plan.md",
        "supporting-information/source-data-roadmap.md",
        "supporting-information/submission-readiness.md",
        "supporting-information/final-human-readthrough.md",
    }
    return all((ROOT / path).exists() for path in ["docs/odd-model.md", "docs/scenario-catalog.md", "docs/validation.md"]) and required <= names


def supporting_information_evidence(names: set[str]) -> str:
    required = [
        "supplement.tex",
        "supplement.pdf",
        "supporting-information/ODD-model.md",
        "supporting-information/scenario-catalog.md",
        "supporting-information/validation-plan.md",
        "supporting-information/source-data-roadmap.md",
        "supporting-information/submission-readiness.md",
        "supporting-information/final-human-readthrough.md",
    ]
    report_data = sum(1 for name in names if name.startswith("supporting-information/report-data/"))
    return (
        "; ".join(f"{name}={yes_no(name in names)}" for name in required)
        + f"; report-data files={report_data}"
    )


def supporting_information_members(names: set[str]) -> list[str]:
    members = [
        name
        for name in names
        if name.startswith("supporting-information/") or name in {"supplement.tex", "supplement.pdf"}
    ]
    return sorted(members)


def supporting_information_format_size_ready(names: set[str], sizes: dict[str, int]) -> bool:
    members = supporting_information_members(names)
    return bool(members) and not oversized_supporting_members(names, sizes) and not unlabeled_supporting_members(names)


def oversized_supporting_members(names: set[str], sizes: dict[str, int]) -> list[str]:
    return [
        name
        for name in supporting_information_members(names)
        if int(sizes.get(name, 0)) > SUPPORTING_INFO_MAX_BYTES
    ]


def unlabeled_supporting_members(names: set[str]) -> list[str]:
    unlabeled: list[str] = []
    for name in supporting_information_members(names):
        normalized = name.lower()
        basename = Path(name).name.lower()
        labeled = (
            normalized.startswith("supporting-information/")
            or basename.startswith("supplement")
            or "suppinfo" in basename
            or "_supp" in basename
            or "-supp" in basename
        )
        if not labeled:
            unlabeled.append(name)
    return unlabeled


def supporting_information_format_size_evidence(names: set[str], sizes: dict[str, int]) -> str:
    members = supporting_information_members(names)
    oversized = oversized_supporting_members(names, sizes)
    unlabeled = unlabeled_supporting_members(names)
    largest_status = "within-limit" if members and not oversized else "over-limit"
    return (
        f"supporting members={len(members)}; "
        f"largest={largest_status}; limit={SUPPORTING_INFO_MAX_BYTES}; "
        f"oversized={'; '.join(oversized) if oversized else 'none'}; "
        f"unlabeled={'; '.join(unlabeled) if unlabeled else 'none'}"
    )


def latex_submission_ready(
    package: dict[str, object],
    names: set[str],
    wiley_form_rows: dict[str, dict[str, str]],
) -> bool:
    required = {
        f"{LOCAL_BASENAME}.tex",
        f"{LOCAL_BASENAME}.pdf",
        "references.bib",
        "USG.cls",
        "lettersp.sty",
        "wileyNJD-Chicago.bst",
        "supporting-information/submission-package-manifest.json",
        "supporting-information/submission-package-manifest.md",
    }
    wiley_form_ready = all(
        wiley_form_rows.get(gate, {}).get("status") == "ready"
        for gate in [
            "submission-archive-present",
            "upload-size",
            "filename-length",
            "root-latex-and-pdf",
            "supporting-files",
            "unsupported-upload-formats",
            "data-and-ai-statements",
        ]
    )
    return (
        bool(package["exists"])
        and bool(package["readable"])
        and not bool(package["encrypted"])
        and required <= names
        and WILEY_PDF.exists()
        and SUPPLEMENT_PDF.exists()
        and wiley_form_ready
    )


def latex_submission_evidence(
    package: dict[str, object],
    names: set[str],
    wiley_form_rows: dict[str, dict[str, str]],
) -> str:
    required = [
        f"{LOCAL_BASENAME}.tex",
        f"{LOCAL_BASENAME}.pdf",
        "references.bib",
        "USG.cls",
        "lettersp.sty",
        "wileyNJD-Chicago.bst",
        "supporting-information/submission-package-manifest.json",
        "supporting-information/submission-package-manifest.md",
    ]
    ready_form_gates = sum(1 for row in wiley_form_rows.values() if row.get("status") == "ready")
    return (
        f"exists={yes_no(bool(package['exists']))}; readable={yes_no(bool(package['readable']))}; "
        f"encrypted={yes_no(bool(package['encrypted']))}; members={len(names)}; "
        + "; ".join(f"{name}={yes_no(name in names)}" for name in required)
        + f"; Wiley form ready gates={ready_form_gates}"
    )


def inspect_package() -> dict[str, object]:
    if not SUBMISSION_ZIP.exists():
        return {"exists": False, "readable": False, "encrypted": False, "names": [], "sizes": {}}
    try:
        with zipfile.ZipFile(SUBMISSION_ZIP) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            encrypted = any(info.flag_bits & 0x1 for info in infos)
            return {
                "exists": True,
                "readable": True,
                "encrypted": encrypted,
                "names": [info.filename for info in infos],
                "sizes": {info.filename: int(info.file_size) for info in infos},
            }
    except (OSError, zipfile.BadZipFile):
        return {"exists": True, "readable": False, "encrypted": False, "names": [], "sizes": {}}


def read_gate_rows(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get("gate", ""): row for row in csv.DictReader(source)}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def field_value(text: str, field_name: str) -> str:
    match = re.search(
        rf"^[^\S\n]*{re.escape(field_name)}[^\S\n]*:[^\S\n]*(.*?)[^\S\n]*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def current_release_tag() -> str:
    match = VERSION_PATTERN.search(read_text(CITATION_CFF))
    return match.group(1).strip() if match else ""


def row(gate: str, status: str, evidence_text: str, next_action: str) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "evidence": evidence_text,
        "nextAction": next_action,
    }


def evidence(checks: dict[str, bool]) -> str:
    return "; ".join(f"{name}={yes_no(ok)}" for name, ok in checks.items())


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


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
    status = "ready_with_manual_live_check" if blocked == 0 else "blocked"
    lines = [
        "# Regulation & Governance Guideline Readiness",
        "",
        "This audit checks the locally verifiable Regulation & Governance and Wiley submission requirements for the generated manuscript bundle. It intentionally does not replace the final live journal author-page check.",
        "",
        "## Summary",
        "",
        f"- Automated guideline status: `{status}`",
        f"- Ready gates: `{ready}`",
        f"- Manual-required gates: `{manual}`",
        f"- Blocked gates: `{blocked}`",
        f"- Preferred word range checked: `{WORD_RANGE_LABEL}` words including abstract, references, endnotes, tables, and figures",
        "- Manuscript declarations checked: Data and Code Availability; AI Use Disclosure; funding; conflict of interest",
        "- Supporting-information checks include Wiley's clear-labeling and 10 MB per-file guidance",
        "",
        "## Source Notes",
        "",
        f"- Official Regulation & Governance author page: {REGGOV_AUTHOR_GUIDELINES_URL}",
        f"- Wiley submission help: {WILEY_SUBMISSION_HELP_URL}",
        f"- Wiley LaTeX template guidance: {WILEY_LATEX_URL}",
        f"- Wiley AI guidelines: {WILEY_AI_URL}",
        f"- Wiley supporting-information guidance: {WILEY_SUPPORTING_INFO_URL}",
        "",
        "The live Regulation & Governance author page should be opened immediately before final submission because journal-specific instructions can supersede generic Wiley guidance.",
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
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A `ready_with_manual_live_check` status means the repository satisfies the checks that can be made from committed files and the generated Wiley package. It does not mean the journal submission is complete: DOI archiving, human final read-through, and live Regulation & Governance author-page refresh remain separate final-submission controls.",
            "",
        ]
    )
    return "\n".join(lines)


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
