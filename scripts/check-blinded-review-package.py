#!/usr/bin/env python3
"""Check the double-anonymized Regulation & Governance review package."""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
PACKAGE = DIST / "lobby-capture-wiley-blinded-review.zip"
BLIND_BASENAME = "strategic-channel-substitution-regulatory-capture-blinded"
COMPILE_TIMEOUT_SECONDS = 180
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
UNSUPPORTED_UPLOAD_SUFFIXES = {".exe", ".bat", ".cmd", ".com", ".js", ".vbs", ".sh", ".py"}
TEX_BINARY_DIRS = [
    Path("/usr/local/texlive/2026basic/bin/universal-darwin"),
    Path("/usr/local/texlive/2025basic/bin/universal-darwin"),
    Path("/Library/TeX/texbin"),
    Path("/opt/homebrew/bin"),
    Path("/usr/local/bin"),
]
IDENTIFYING_TOKENS = [
    "Jacob Anderson",
    "jacobdanderson",
    "Independent Researcher",
    "Jacoba1100254352",
    "github.com/Jacoba1100254352",
    "paper-publication-readiness-2026",
]
EXPECTED_MEMBERS = {
    f"{BLIND_BASENAME}.tex",
    f"{BLIND_BASENAME}.pdf",
    "supplement-blinded.tex",
    "supplement-blinded.pdf",
    "title-page.tex",
    "title-page.pdf",
    "references.bib",
    "USG.cls",
    "lettersp.sty",
    "wileyNJD-Chicago.bst",
    "BLINDED_REVIEW_README.txt",
    "sections/reggov-body.tex",
    "sections/submission-declarations.tex",
    "sections/supplement-body.tex",
    "supporting-information/ODD-model.md",
    "supporting-information/scenario-catalog.md",
    "supporting-information/validation-plan.md",
    "supporting-information/source-data-roadmap.md",
    "supporting-information/blinded-review-package-manifest.json",
    "supporting-information/blinded-review-package-manifest.md",
}


@dataclass(frozen=True)
class CompileResult:
    returncode: int
    output: str
    timed_out: bool = False

    @property
    def tail(self) -> str:
        return "\n".join(self.output.splitlines()[-80:])


def main() -> int:
    package = inspect_package()
    rows = readiness_rows(package)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "blinded-review-package-readiness.csv", rows)
    (REPORTS / "blinded-review-package-readiness.md").write_text(markdown(rows), encoding="utf-8")
    print("Wrote reports/blinded-review-package-readiness.csv")
    print("Wrote reports/blinded-review-package-readiness.md")
    return 0 if all(row["status"] == "ready" for row in rows) else 1


def readiness_rows(package: dict[str, object]) -> list[dict[str, str]]:
    names = set(package["names"])
    sizes = package["sizes"]
    assert isinstance(sizes, dict)
    missing = sorted(EXPECTED_MEMBERS - names)
    unsupported = sorted(name for name in names if Path(name).suffix.lower() in UNSUPPORTED_UPLOAD_SUFFIXES)
    review_scan = scan_review_facing_members(package)
    rendered_scan = scan_rendered_review_pdfs(package)
    title_page = title_page_evidence(package)
    manifest = manifest_evidence(package)
    compile_check = compile_extracted_package() if package["exists"] and package["readable"] else "package missing"
    upload_bytes = int(package["bytes"])
    return [
        row(
            "package-present",
            "ready" if package["exists"] and package["readable"] and not package["encrypted"] else "blocked",
            (
                f"exists={yes_no(package['exists'])}; readable={yes_no(package['readable'])}; "
                f"encrypted={yes_no(package['encrypted'])}; members={len(names)}"
            ),
            "Build the blinded review package before journal review upload.",
        ),
        row(
            "expected-files",
            "ready" if not missing else "blocked",
            f"missing={'; '.join(missing) if missing else 'none'}",
            "Keep anonymous main manuscript, supplement, title page, references, classes, figures, tables, and selected supporting information together.",
        ),
        row(
            "upload-surface",
            "ready" if 0 < upload_bytes <= MAX_UPLOAD_BYTES and not unsupported else "blocked",
            (
                f"size={'within-limit' if 0 < upload_bytes <= MAX_UPLOAD_BYTES else 'outside-limit'}; "
                f"limit={MAX_UPLOAD_BYTES}; "
                f"unsupported members={'; '.join(unsupported) if unsupported else 'none'}"
            ),
            "Keep the blinded review ZIP within Wiley's upload size limit and free of unsupported executable/script formats.",
        ),
        row(
            "source-redaction",
            "ready" if not review_scan else "blocked",
            f"identifiers in review-facing source={'; '.join(review_scan) if review_scan else 'none'}",
            "Review-facing source files must not expose author, email, public repository, or release-tag identifiers.",
        ),
        row(
            "rendered-redaction",
            "ready" if not rendered_scan else "blocked",
            f"identifiers in review-facing PDFs={'; '.join(rendered_scan) if rendered_scan else 'none'}",
            "Review-facing PDFs must not expose author, email, public repository, or release-tag identifiers.",
        ),
        row(
            "separate-title-page",
            "ready" if title_page["ready"] else "blocked",
            title_page["evidence"],
            "Keep author and correspondence information only in separate title-page files.",
        ),
        row(
            "manifest",
            "ready" if manifest["ready"] else "blocked",
            manifest["evidence"],
            "Keep the blinded package member manifest synchronized with ZIP bytes.",
        ),
        row(
            "standalone-compile",
            "ready" if compile_check == "ready" else "blocked",
            compile_check,
            "The extracted blinded ZIP must compile its anonymous main manuscript, supplement, and title page.",
        ),
    ]


def inspect_package() -> dict[str, object]:
    if not PACKAGE.exists():
        return {"exists": False, "readable": False, "encrypted": False, "names": [], "sizes": {}, "bytes": 0}
    try:
        with zipfile.ZipFile(PACKAGE) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            encrypted = any(info.flag_bits & 0x1 for info in infos)
            return {
                "exists": True,
                "readable": True,
                "encrypted": encrypted,
                "names": [info.filename for info in infos],
                "sizes": {info.filename: int(info.file_size) for info in infos},
                "bytes": PACKAGE.stat().st_size,
            }
    except (OSError, zipfile.BadZipFile):
        return {"exists": True, "readable": False, "encrypted": False, "names": [], "sizes": {}, "bytes": PACKAGE.stat().st_size}


def scan_review_facing_members(package: dict[str, object]) -> list[str]:
    if not package["readable"]:
        return ["package unreadable"]
    failures: list[str] = []
    text_suffixes = {".tex", ".bib", ".md", ".txt", ".csv", ".json", ".yml", ".yaml"}
    with zipfile.ZipFile(PACKAGE) as archive:
        for name in package["names"]:
            if name.startswith("title-page."):
                continue
            if Path(name).suffix.lower() not in text_suffixes:
                continue
            try:
                text = archive.read(name).decode("utf-8", errors="replace")
            except KeyError:
                failures.append(f"{name}:missing")
                continue
            for token in IDENTIFYING_TOKENS:
                if token in text:
                    failures.append(f"{name}:{token}")
    return failures


def scan_rendered_review_pdfs(package: dict[str, object]) -> list[str]:
    if not package["readable"]:
        return ["package unreadable"]
    pdftotext = resolve_binary("pdftotext")
    if pdftotext is None:
        return ["pdftotext missing"]
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lobby-capture-blind-scan-") as temp_dir:
        temp = Path(temp_dir)
        with zipfile.ZipFile(PACKAGE) as archive:
            for member in (f"{BLIND_BASENAME}.pdf", "supplement-blinded.pdf"):
                try:
                    data = archive.read(member)
                except KeyError:
                    failures.append(f"{member}:missing")
                    continue
                pdf = temp / Path(member).name
                txt = temp / (Path(member).stem + ".txt")
                pdf.write_bytes(data)
                try:
                    subprocess.run(
                        [str(pdftotext), str(pdf), str(txt)],
                        cwd=temp,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=COMPILE_TIMEOUT_SECONDS,
                    )
                except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                    failures.append(f"{member}:pdftotext failed: {error}")
                    continue
                text = txt.read_text(encoding="utf-8", errors="replace")
                for token in IDENTIFYING_TOKENS:
                    if token in text:
                        failures.append(f"{member}:{token}")
    return failures


def title_page_evidence(package: dict[str, object]) -> dict[str, str | bool]:
    if not package["readable"]:
        return {"ready": False, "evidence": "package unreadable"}
    with zipfile.ZipFile(PACKAGE) as archive:
        try:
            title_tex = archive.read("title-page.tex").decode("utf-8", errors="replace")
        except KeyError:
            return {"ready": False, "evidence": "title-page.tex missing"}
    required = ["Jacob Anderson", "jacobdanderson@gmail.com", "Independent Researcher", "Conflict of Interest"]
    missing = [token for token in required if token not in title_tex]
    separate = all(member in set(package["names"]) for member in {"title-page.tex", "title-page.pdf"})
    return {
        "ready": separate and not missing,
        "evidence": (
            f"title-page files={yes_no(separate)}; "
            f"missing title-page metadata={'; '.join(missing) if missing else 'none'}"
        ),
    }


def manifest_evidence(package: dict[str, object]) -> dict[str, str | bool]:
    if not package["readable"]:
        return {"ready": False, "evidence": "package unreadable"}
    manifest_member = "supporting-information/blinded-review-package-manifest.json"
    manifest_markdown = "supporting-information/blinded-review-package-manifest.md"
    names = set(package["names"])
    if manifest_member not in names:
        return {"ready": False, "evidence": f"missing {manifest_member}"}
    failures: list[str] = []
    if manifest_markdown not in names:
        failures.append(f"missing {manifest_markdown}")
    with zipfile.ZipFile(PACKAGE) as archive:
        try:
            manifest = json.loads(archive.read(manifest_member).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as error:
            return {"ready": False, "evidence": f"manifest unreadable: {error}"}
        if manifest.get("schema") != "lobby-capture-blinded-review-package-manifest-v1":
            failures.append("unexpected schema")
        members = manifest.get("members")
        if not isinstance(members, list):
            return {"ready": False, "evidence": "manifest members field is not a list"}
        manifest_paths: set[str] = set()
        for entry in members:
            if not isinstance(entry, dict):
                failures.append("non-object manifest entry")
                continue
            path = entry.get("path")
            if not isinstance(path, str):
                failures.append("manifest entry has invalid path")
                continue
            manifest_paths.add(path)
            if path not in names:
                failures.append(f"listed missing member={path}")
                continue
            if path in {manifest_member, manifest_markdown}:
                failures.append(f"manifest should not checksum itself={path}")
                continue
            data = archive.read(path)
            if entry.get("bytes") != len(data):
                failures.append(f"byte mismatch={path}")
            if entry.get("sha256") != __import__("hashlib").sha256(data).hexdigest():
                failures.append(f"sha mismatch={path}")
    expected = names - {manifest_member, manifest_markdown}
    missing_from_manifest = sorted(expected - manifest_paths)
    extra = sorted(manifest_paths - expected)
    failures.extend(f"omits={path}" for path in missing_from_manifest)
    failures.extend(f"extra={path}" for path in extra)
    return {
        "ready": not failures,
        "evidence": f"manifest failures={'; '.join(failures) if failures else 'none'}",
    }


def compile_extracted_package() -> str:
    binaries = {binary: resolve_binary(binary) for binary in ("pdflatex", "bibtex")}
    missing = [binary for binary, path in binaries.items() if path is None]
    if missing:
        return f"missing binaries: {', '.join(missing)}"
    assert binaries["pdflatex"] is not None
    assert binaries["bibtex"] is not None
    pdflatex = str(binaries["pdflatex"])
    bibtex = str(binaries["bibtex"])
    with tempfile.TemporaryDirectory(prefix="lobby-capture-blinded-review-") as temp_dir:
        temp = Path(temp_dir)
        try:
            with zipfile.ZipFile(PACKAGE) as archive:
                archive.extractall(temp)
        except (OSError, zipfile.BadZipFile) as error:
            return f"could not extract package: {error}"
        env = os.environ.copy()
        for key in ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS"):
            env.pop(key, None)
        env["TZ"] = "UTC"
        env["SOURCE_DATE_EPOCH"] = "1777939200"
        env["FORCE_SOURCE_DATE"] = "1"
        commands = [
            [pdflatex, "-interaction=nonstopmode", f"{BLIND_BASENAME}.tex"],
            [bibtex, BLIND_BASENAME],
            [pdflatex, "-interaction=nonstopmode", f"{BLIND_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", f"{BLIND_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", f"{BLIND_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", f"{BLIND_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", "supplement-blinded.tex"],
            [pdflatex, "-interaction=nonstopmode", "supplement-blinded.tex"],
            [pdflatex, "-interaction=nonstopmode", "title-page.tex"],
            [pdflatex, "-interaction=nonstopmode", "title-page.tex"],
        ]
        for command in commands:
            result = run_compile_command(command, temp, env)
            target_pdf = target_pdf_for_command(command)
            if result.timed_out:
                return f"`{' '.join(command)}` timed out:\n{result.tail}"
            if Path(command[0]).name == "pdflatex" and target_pdf and is_nonfatal_latex_pass(result.output, temp / target_pdf):
                continue
            if result.returncode != 0:
                return f"`{' '.join(command)}` failed:\n{result.tail}"
        log = temp / f"{BLIND_BASENAME}.log"
        if not log.exists():
            return f"missing {BLIND_BASENAME}.log after compile"
        log_text = log.read_text(encoding="utf-8", errors="replace")
        unresolved = [
            marker
            for marker in [
                "There were undefined citations",
                "Citation(s) may have changed",
                "There were undefined references",
                "Rerun to get cross-references right",
            ]
            if marker in log_text
        ]
        if unresolved:
            return "unresolved LaTeX state: " + ", ".join(unresolved)
    return "ready"


def target_pdf_for_command(command: list[str]) -> str:
    tex = Path(command[-1]).name
    if tex == f"{BLIND_BASENAME}.tex":
        return f"{BLIND_BASENAME}.pdf"
    if tex == "supplement-blinded.tex":
        return "supplement-blinded.pdf"
    if tex == "title-page.tex":
        return "title-page.pdf"
    return ""


def run_compile_command(command: list[str], cwd: Path, env: dict[str, str]) -> CompileResult:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=COMPILE_TIMEOUT_SECONDS,
        )
        return CompileResult(result.returncode, result.stdout)
    except subprocess.TimeoutExpired as error:
        return CompileResult(124, error.stdout or "", timed_out=True)


def is_nonfatal_latex_pass(output: str, target_pdf: Path) -> bool:
    if not target_pdf.exists():
        return False
    fatal_patterns = [
        "Emergency stop",
        "Fatal error occurred",
        " ==> Fatal error occurred",
        "No output PDF file produced",
        "LaTeX Error: File `",
    ]
    return not any(pattern in output for pattern in fatal_patterns)


def resolve_binary(name: str) -> Path | None:
    resolved = shutil.which(name)
    if resolved:
        return Path(resolved)
    for directory in TEX_BINARY_DIRS:
        candidate = directory / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def row(gate: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["gate", "status", "evidence", "nextAction"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for item in rows:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    lines = [
        "# Blinded Review Package Readiness",
        "",
        "This audit checks the double-anonymized Regulation & Governance review package. The title page is allowed to contain author and correspondence information; the main manuscript, supplement, and inspectable review-facing sources are not.",
        "",
        "## Summary",
        "",
        f"- Ready gates: `{counts.get('ready', 0)}`",
        f"- Blocked gates: `{counts.get('blocked', 0)}`",
        "",
        "## Gates",
        "",
        "| Gate | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {gate} | {status} | {evidence} | {nextAction} |".format(
                gate=item["gate"],
                status=item["status"],
                evidence=item["evidence"].replace("|", "\\|").replace("\n", "<br>"),
                nextAction=item["nextAction"].replace("|", "\\|").replace("\n", "<br>"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def yes_no(value: object) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
