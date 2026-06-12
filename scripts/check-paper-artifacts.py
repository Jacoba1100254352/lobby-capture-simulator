#!/usr/bin/env python3
"""Check that generated paper PDFs and submission artifacts are current."""

from __future__ import annotations

import csv
import json
import os
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
SUPPLEMENT_BODY = PAPER / "sections" / "supplement-body.tex"
VALIDATION_SUMMARY = ROOT / "reports" / "validation-summary.md"
SOURCE_PANEL_INVENTORY = ROOT / "reports" / "source-panel-inventory.csv"
SOURCE_CAPABILITY_AUDIT_MD = ROOT / "reports" / "source-capability-audit.md"
SOURCE_CAPABILITY_AUDIT_CSV = ROOT / "reports" / "source-capability-audit.csv"
DARK_MONEY_BRIDGE_AUDIT_MD = ROOT / "reports" / "dark-money-bridge-audit.md"
DARK_MONEY_BRIDGE_AUDIT_CSV = ROOT / "reports" / "dark-money-bridge-audit.csv"
INTERMEDIARY_BRIDGE_AUDIT_MD = ROOT / "reports" / "intermediary-bridge-audit.md"
INTERMEDIARY_BRIDGE_AUDIT_CSV = ROOT / "reports" / "intermediary-bridge-audit.csv"
REVOLVING_DOOR_BRIDGE_AUDIT_MD = ROOT / "reports" / "revolving-door-bridge-audit.md"
REVOLVING_DOOR_BRIDGE_AUDIT_CSV = ROOT / "reports" / "revolving-door-bridge-audit.csv"
PROCUREMENT_DENOMINATOR_AUDIT_MD = ROOT / "reports" / "procurement-denominator-audit.md"
PROCUREMENT_DENOMINATOR_AUDIT_CSV = ROOT / "reports" / "procurement-denominator-audit.csv"
PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_MD = ROOT / "reports" / "procurement-modification-composition-audit.md"
PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_CSV = ROOT / "reports" / "procurement-modification-composition-audit.csv"
LAYOUT_AUDIT = ROOT / "reports" / "paper-layout-audit.md"
MANUAL_VISUAL_AUDIT = ROOT / "reports" / "manual-visual-audit.md"
CLAIM_BOUNDARY_AUDIT_MD = ROOT / "reports" / "claim-boundary-audit.md"
CLAIM_BOUNDARY_AUDIT_CSV = ROOT / "reports" / "claim-boundary-audit.csv"
CLAIM_SOURCE_DEPENDENCY_MD = ROOT / "reports" / "claim-source-dependency.md"
CLAIM_SOURCE_DEPENDENCY_CSV = ROOT / "reports" / "claim-source-dependency.csv"
CLAIM_POSTURE_AUDIT_MD = ROOT / "reports" / "claim-posture-audit.md"
CLAIM_POSTURE_AUDIT_CSV = ROOT / "reports" / "claim-posture-audit.csv"
RELEASE_TAG = "paper-publication-readiness-2026-06-12-r58"
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
TEX_BINARY_DIRS = [
    Path("/usr/local/texlive/2026basic/bin/universal-darwin"),
    Path("/usr/local/texlive/2025basic/bin/universal-darwin"),
    Path("/Library/TeX/texbin"),
    Path("/opt/homebrew/bin"),
    Path("/usr/local/bin"),
]
SUBMISSION_COMPILE_TIMEOUT_SECONDS = 180

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
    "supporting-information/source-capability-audit.md",
    "supporting-information/dark-money-bridge-audit.md",
    "supporting-information/intermediary-bridge-audit.md",
    "supporting-information/revolving-door-bridge-audit.md",
    "supporting-information/procurement-denominator-audit.md",
    "supporting-information/procurement-modification-composition-audit.md",
    "supporting-information/claim-boundary-audit.md",
    "supporting-information/claim-source-dependency.md",
    "supporting-information/claim-posture-audit.md",
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
    failures.extend(check_source_capability_audit())
    failures.extend(check_dark_money_bridge_audit())
    failures.extend(check_intermediary_bridge_audit())
    failures.extend(check_revolving_door_bridge_audit())
    failures.extend(check_procurement_denominator_audit())
    failures.extend(check_procurement_modification_composition_audit())
    failures.extend(check_claim_boundary_audit())
    failures.extend(check_claim_source_dependency_audit())
    failures.extend(check_claim_posture_audit())
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
        SOURCE_CAPABILITY_AUDIT_MD,
        DARK_MONEY_BRIDGE_AUDIT_MD,
        INTERMEDIARY_BRIDGE_AUDIT_MD,
        REVOLVING_DOOR_BRIDGE_AUDIT_MD,
        PROCUREMENT_DENOMINATOR_AUDIT_MD,
        PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_MD,
        ROOT / "reports" / "claim-boundary-audit.md",
        ROOT / "reports" / "claim-source-dependency.md",
        ROOT / "reports" / "claim-posture-audit.md",
        ROOT / "reports" / "validation-summary.md",
        ROOT / "reports" / "substitution-audit.md",
        ROOT / "reports" / "lobby-capture-portfolio.md",
        ROOT / "reports" / "calibration-queue.md",
        ROOT / "reports" / "paper-layout-audit.md",
        ROOT / "reports" / "manual-visual-audit.md",
        *report_bundle_inputs(),
        PAPER / ".wiley-build" / "USG.cls",
        PAPER / ".wiley-build" / "wileyNJD-Chicago.bst",
        PAPER / ".wiley-template" / "Optimal-Design-layout" / "LETTERSP.STY",
        *sorted((PAPER / "sections").glob("*.tex")),
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
        *sorted((PAPER / "figures").glob("Figure_*.svg")),
    ]


def report_bundle_inputs() -> list[Path]:
    return [
        *sorted((ROOT / "reports").glob("*.csv")),
        *sorted((ROOT / "reports").glob("*.md")),
        *sorted((ROOT / "reports").glob("*.manifest.json")),
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
    failures: list[str] = []
    if "- Miss: `0`" in validation and "benchmark misses" in body:
        failures.append(
            "manuscript still refers to benchmark misses even though validation-summary.md reports Miss: 0",
        )
    if SOURCE_PANEL_INVENTORY.exists():
        with SOURCE_PANEL_INVENTORY.open(newline="", encoding="utf-8") as source:
            panels = {row["panel"]: row for row in csv.DictReader(source)}
        electoral = panels.get("Electoral communications")
        if electoral and electoral.get("status") == "missing":
            required = "electioneering and communication-cost rows are schema-supported but absent"
            if required not in body:
                failures.append(
                    "source-panel inventory marks electoral communications missing, "
                    f"but the manuscript does not state that {required}"
                )
            required_supporting = {
                SUPPLEMENT_BODY: required,
                ROOT / "docs" / "scenario-catalog.md": "OpenFEC electioneering and communication-cost channels are parser-supported but absent from the pinned snapshot",
                ROOT / "docs" / "validation.md": "electioneering and communication-cost channels are parser-supported but absent from the pinned snapshot",
                ROOT / "docs" / "next-steps.md": "the pinned snapshot still has zero electoral-communication rows",
                ROOT / "docs" / "source-data-roadmap.md": "the pinned 2024 EPA/ENV snapshot has zero electoral-communication rows",
            }
            for path, phrase in required_supporting.items():
                if path.exists() and phrase not in path.read_text(encoding="utf-8"):
                    failures.append(
                        f"{path.relative_to(ROOT)} does not disclose missing electoral-communication source rows"
                    )
            overstated_phrases = [
                "validation snapshot adds Schedule E outside spending, parser-ready OpenFEC electioneering and communication-cost channels",
                "parser-ready OpenFEC electioneering and communication-cost rows",
                "OpenFEC party/Schedule E/electioneering/communication-cost rows",
                "Implemented for six national party committees, Schedule E independent expenditures, electioneering communications, and communication-cost rows",
                "beyond national party committees, Schedule E, and electoral-communication rows",
            ]
            checked_texts = {REGGOV_BODY: body}
            for path in required_supporting:
                if path.exists():
                    checked_texts[path] = path.read_text(encoding="utf-8")
            for path, text in checked_texts.items():
                for phrase in overstated_phrases:
                    if phrase in text:
                        failures.append(
                            f"{path.relative_to(ROOT)} overstates electoral-communication source coverage despite missing source-panel rows"
                        )
            runner = ROOT / "scripts" / "run-2024-env-live-snapshot.sh"
            if runner.exists():
                runner_text = runner.read_text(encoding="utf-8")
                stale_message = "normalized independent-expenditure and electoral-communication rows appended"
                if stale_message in runner_text:
                    failures.append(
                        "live snapshot runner status overstates electoral-communication rows despite missing source-panel rows"
                    )
        elif electoral and electoral.get("status") in {"usable", "thin", "warning"}:
            required = "OpenFEC electioneering and communication-cost rows"
            if required not in body:
                failures.append(
                    "source-panel inventory has electoral-communication rows, "
                    f"but the manuscript does not describe the {required} bridge"
                )
            supporting_required = {
                SUPPLEMENT_BODY: required,
                ROOT / "docs" / "scenario-catalog.md": "OpenFEC electioneering and communication-cost rows are included in the pinned snapshot",
                ROOT / "docs" / "validation.md": "OpenFEC electioneering and communication-cost rows are included in the pinned snapshot",
                ROOT / "docs" / "next-steps.md": "OpenFEC electioneering and communication-cost rows are now present in the pinned snapshot",
                ROOT / "docs" / "source-data-roadmap.md": "electioneering and communication-cost rows present in the pinned 2024 EPA/ENV snapshot",
            }
            for path, phrase in supporting_required.items():
                if path.exists() and phrase not in path.read_text(encoding="utf-8"):
                    failures.append(
                        f"{path.relative_to(ROOT)} does not disclose electoral-communication source-row coverage"
                    )
            stale_absent_phrases = [
                "electioneering and communication-cost rows are schema-supported but absent",
                "OpenFEC electioneering and communication-cost channels are parser-supported but absent from the pinned snapshot",
                "the pinned snapshot still has zero electoral-communication rows",
                "the pinned 2024 EPA/ENV snapshot has zero electoral-communication rows",
            ]
            checked_texts = {REGGOV_BODY: body}
            for path in supporting_required:
                if path.exists():
                    checked_texts[path] = path.read_text(encoding="utf-8")
            for path, text in checked_texts.items():
                for phrase in stale_absent_phrases:
                    if phrase in text:
                        failures.append(
                            f"{path.relative_to(ROOT)} still describes electoral-communication rows as absent"
                        )
    return failures


def check_source_capability_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (SOURCE_CAPABILITY_AUDIT_MD, SOURCE_CAPABILITY_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing source capability audit artifact: {path}" for path in missing]

    with SOURCE_CAPABILITY_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("capability", ""): row for row in csv.DictReader(source)}
    required = {
        "direct-dark-money-routing",
        "sam-contract-awards-action-history",
        "usaspending-stratified-action-panel",
        "lda-covered-position-revolving-door",
        "irs-527-political-organizations",
        "licensed-access-overlays",
    }
    missing_capabilities = sorted(required - set(rows))
    failures.extend(
        f"source capability audit missing capability: {capability}"
        for capability in missing_capabilities
    )
    if missing_capabilities:
        return failures

    if rows["direct-dark-money-routing"].get("capabilityStatus") != "active-usable":
        failures.append(
            "direct dark-money capability should be active-usable after the Schedule I nonprofit-routing bridge is present"
        )
    if rows["sam-contract-awards-action-history"].get("capabilityStatus") not in {
        "implemented-not-active",
        "active-bounded",
    }:
        failures.append(
            "SAM Contract Awards capability status should be implemented-not-active or active-bounded"
        )
    if rows["usaspending-stratified-action-panel"].get("capabilityStatus") not in {
        "active-usable",
        "active-bounded",
    }:
        failures.append(
            "USAspending action panel capability should be active in the committed snapshot"
        )
    if rows["lda-covered-position-revolving-door"].get("capabilityStatus") != "active-usable":
        failures.append(
            "LDA covered-position revolving-door capability should be active and usable"
        )
    if rows["irs-527-political-organizations"].get("capabilityStatus") != "active-usable":
        failures.append(
            "IRS 527 political-organization capability should be active and usable"
        )
    text = SOURCE_CAPABILITY_AUDIT_MD.read_text(encoding="utf-8")
    for phrase in (
            "Source Capability Audit",
            "SAM/FPDS action-history",
            "Direct hidden-donor",
            "SAM_CONTRACT_AWARDS_OFFSET_STARTS",
            "SAM_CONTRACT_AWARDS_EXTRACT_MODE",
    ):
        if phrase not in text:
            failures.append(f"source capability audit markdown missing phrase: {phrase}")
    return failures


def check_dark_money_bridge_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (DARK_MONEY_BRIDGE_AUDIT_MD, DARK_MONEY_BRIDGE_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing dark-money bridge audit artifact: {path}" for path in missing]

    with DARK_MONEY_BRIDGE_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("source", ""): row for row in csv.DictReader(source)}
    required = {
        "dark-money-capacity-proxy",
        "propublica-nonprofit-routing",
        "openfec-super-pac",
        "openfec-electoral-communications",
        "irs-527-political-organizations",
        "nonprofit-association-capacity",
        "nyc-cfb-campaign-intermediaries",
    }
    missing_sources = sorted(required - set(rows))
    failures.extend(
        f"dark-money bridge audit missing source: {source_name}"
        for source_name in missing_sources
    )
    if missing_sources:
        return failures

    dark = rows["dark-money-capacity-proxy"]
    if int(float(dark.get("rows", "0") or "0")) <= 0:
        failures.append("dark-money bridge audit should include committed opaque-capacity rows")
    if int(float(dark.get("capacityProxyRows", "0") or "0")) <= 0:
        failures.append("dark-money bridge audit should classify IRS EO BMF rows as capacity proxies")
    if int(float(dark.get("directRoutingRows", "0") or "0")) != 0:
        failures.append(
            "dark-money bridge audit should not promote capacity proxies as direct hidden-donor routing"
        )
    nonprofit_routing = rows["propublica-nonprofit-routing"]
    if int(float(nonprofit_routing.get("directRoutingRows", "0") or "0")) <= 0:
        failures.append("dark-money bridge audit should include Schedule I nonprofit-routing rows")
    if "not donor identity evidence" not in nonprofit_routing.get("claimBoundary", ""):
        failures.append("Schedule I nonprofit-routing rows must not be promoted as donor identity evidence")
    if int(float(rows["openfec-super-pac"].get("rows", "0") or "0")) <= 0:
        failures.append("dark-money bridge audit should include adjacent OpenFEC Super PAC rows")
    if int(float(rows["openfec-electoral-communications"].get("rows", "0") or "0")) <= 0:
        failures.append(
            "dark-money bridge audit should include adjacent electioneering or communication-cost rows"
        )
    if int(float(rows["irs-527-political-organizations"].get("rows", "0") or "0")) <= 0:
        failures.append("dark-money bridge audit should include adjacent IRS 527 rows")
    text = DARK_MONEY_BRIDGE_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Dark-Money Bridge Audit",
        "non-proxy nonprofit-routing",
        "zero observed hidden-donor identity rows",
        "not donor identity evidence",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"dark-money bridge audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "dark-money bridge audit" not in supplement:
            failures.append("supplement does not disclose the dark-money bridge audit")
    return failures


def check_intermediary_bridge_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (INTERMEDIARY_BRIDGE_AUDIT_MD, INTERMEDIARY_BRIDGE_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing intermediary bridge audit artifact: {path}" for path in missing]

    with INTERMEDIARY_BRIDGE_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("source", ""): row for row in csv.DictReader(source)}
    required = {
        "nyc-cfb-campaign-intermediaries",
        "irs-eo-bmf-nonprofit-capacity",
        "irs-527-political-organizations",
        "form990-nonprofit-routing",
        "association-capacity",
        "social-welfare-capacity",
        "think-tank-charitable-capacity",
    }
    missing_sources = sorted(required - set(rows))
    failures.extend(
        f"intermediary bridge audit missing source: {source_name}"
        for source_name in missing_sources
    )
    if missing_sources:
        return failures

    nyc = rows["nyc-cfb-campaign-intermediaries"]
    if int(float(nyc.get("rows", "0") or "0")) <= 0:
        failures.append("intermediary bridge audit should include NYC CFB local intermediary rows")
    bmf = rows["irs-eo-bmf-nonprofit-capacity"]
    if int(float(bmf.get("rows", "0") or "0")) <= 0:
        failures.append("intermediary bridge audit should include IRS EO BMF capacity rows")
    if int(float(bmf.get("capacityProxyRows", "0") or "0")) <= 0:
        failures.append("intermediary bridge audit should classify BMF rows as capacity proxies")
    c527 = rows["irs-527-political-organizations"]
    if int(float(c527.get("rows", "0") or "0")) <= 0:
        failures.append("intermediary bridge audit should include IRS 527 political-organization rows")
    if int(float(c527.get("c527Rows", "0") or "0")) <= 0:
        failures.append("intermediary bridge audit should classify IRS 527 rows separately")
    form990 = rows["form990-nonprofit-routing"]
    if int(float(form990.get("rows", "0") or "0")) != 0:
        failures.append(
            "intermediary bridge audit should report no committed Form 990 routing rows until the snapshot includes them"
        )
    if int(float(form990.get("directRoutingRows", "0") or "0")) != 0:
        failures.append(
            "intermediary bridge audit should not promote proxy rows as direct nonprofit routing"
        )
    for source_name, column in {
        "association-capacity": "c6Rows",
        "social-welfare-capacity": "c4Rows",
        "think-tank-charitable-capacity": "c3Rows",
    }.items():
        if int(float(rows[source_name].get("rows", "0") or "0")) <= 0:
            failures.append(f"intermediary bridge audit should include rows for {source_name}")
        if int(float(rows[source_name].get(column, "0") or "0")) <= 0:
            failures.append(f"intermediary bridge audit should classify subsection rows for {source_name}")

    text = INTERMEDIARY_BRIDGE_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Intermediary Bridge Audit",
        "0 Form 990 nonprofit-routing rows",
        "not representative nonprofit routing",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"intermediary bridge audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "intermediary bridge audit" not in supplement:
            failures.append("supplement does not disclose the intermediary bridge audit")
    return failures


def check_revolving_door_bridge_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (REVOLVING_DOOR_BRIDGE_AUDIT_MD, REVOLVING_DOOR_BRIDGE_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing revolving-door bridge audit artifact: {path}" for path in missing]

    with REVOLVING_DOOR_BRIDGE_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("source", ""): row for row in csv.DictReader(source)}
    required = {
        "lda-covered-position-access-proxy",
        "documented-post-employment-movement",
        "fixture-schema-rows",
        "cooling-off-under-one-year",
        "procurement-linked-roles",
    }
    missing_sources = sorted(required - set(rows))
    failures.extend(
        f"revolving-door bridge audit missing source: {source_name}"
        for source_name in missing_sources
    )
    if missing_sources:
        return failures

    lda = rows["lda-covered-position-access-proxy"]
    if int(float(lda.get("rows", "0") or "0")) <= 0:
        failures.append("revolving-door bridge audit should include committed LDA covered-position rows")
    if int(float(lda.get("coveredPositionRows", "0") or "0")) <= 0:
        failures.append("revolving-door bridge audit should classify LDA rows as covered-position proxies")
    if int(float(lda.get("documentedMovementRows", "0") or "0")) != 0:
        failures.append(
            "LDA covered-position rows should not be promoted as documented post-employment movement"
        )
    documented = rows["documented-post-employment-movement"]
    if int(float(documented.get("rows", "0") or "0")) != int(float(documented.get("documentedMovementRows", "0") or "0")):
        failures.append(
            "documented post-employment movement audit row should only count documented movement rows"
        )
    if int(float(rows["fixture-schema-rows"].get("fixtureRows", "0") or "0")) != int(float(rows["fixture-schema-rows"].get("rows", "0") or "0")):
        failures.append("fixture schema audit row should only contain fixture rows")
    text = REVOLVING_DOOR_BRIDGE_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Revolving-Door Bridge Audit",
        "documented post-employment movement rows",
        "LDA-derived covered-position rows",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"revolving-door bridge audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "revolving-door bridge audit" not in supplement:
            failures.append("supplement does not disclose the revolving-door bridge audit")
    return failures


def check_procurement_denominator_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (PROCUREMENT_DENOMINATOR_AUDIT_MD, PROCUREMENT_DENOMINATOR_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing procurement denominator audit artifact: {path}" for path in missing]

    with PROCUREMENT_DENOMINATOR_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("source", ""): row for row in csv.DictReader(source)}
    required = {
        "usaspending-procurement-actions",
        "sam-contract-awards",
        "usaspending-procurement-bridge",
        "usaspending-awards",
    }
    missing_sources = sorted(required - set(rows))
    failures.extend(
        f"procurement denominator audit missing source: {source_name}"
        for source_name in missing_sources
    )
    if missing_sources:
        return failures

    action_rows = int(float(rows["usaspending-procurement-actions"].get("rows", "0") or "0"))
    action_agencies = int(float(rows["usaspending-procurement-actions"].get("agencyCount", "0") or "0"))
    if action_rows <= 0 or action_agencies < 2:
        failures.append(
            "procurement denominator audit should show an active multi-agency USAspending action panel"
        )
    if rows["sam-contract-awards"].get("snapshotStatus") == "ok" and int(float(rows["sam-contract-awards"].get("rows", "0") or "0")) <= 0:
        failures.append(
            "SAM Contract Awards cannot be marked ok without committed action rows"
        )
    text = PROCUREMENT_DENOMINATOR_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Procurement Denominator Audit",
        "representative SAM/FPDS action-history denominator",
        "modified-action share",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"procurement denominator audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "procurement-denominator audit" not in supplement:
            failures.append("supplement does not disclose the procurement-denominator audit")
    return failures


def check_procurement_modification_composition_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (
            PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_MD,
            PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_CSV,
        )
        if not path.exists()
    ]
    if missing:
        return [f"missing procurement modification composition audit artifact: {path}" for path in missing]

    with PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    source_rows = {
        row.get("source", ""): row
        for row in rows
        if row.get("groupType") == "source"
    }
    primary = source_rows.get("usaspending-procurement-actions")
    if not primary:
        failures.append("procurement modification composition audit missing USAspending source summary")
    else:
        if audit_number(primary.get("rows")) <= 0:
            failures.append("procurement modification composition audit should include USAspending action rows")
        if audit_number(primary.get("modifiedRows")) <= 0:
            failures.append("procurement modification composition audit should include modified action rows")
        if audit_number(primary.get("modifiedActionShare")) <= 0.20:
            failures.append("procurement modification composition audit should preserve a nontrivial modified-action share")
        if audit_number(primary.get("knownPiidShare")) < 0.99:
            failures.append("procurement modification composition audit should show near-complete PIID coverage")
        if audit_number(primary.get("knownUeiShare")) < 0.99:
            failures.append("procurement modification composition audit should show near-complete UEI coverage")
        if audit_number(primary.get("knownCompetitionShare")) > 0.01:
            failures.append("procurement modification composition audit should keep competition fields separate from this panel")
        if "not representative SAM/FPDS" not in primary.get("claimBoundary", ""):
            failures.append("procurement modification composition audit should keep the USAspending panel bounded")

    sam = source_rows.get("sam-contract-awards")
    if not sam:
        failures.append("procurement modification composition audit missing SAM Contract Awards source summary")
    elif sam.get("snapshotStatus") == "ok" and audit_number(sam.get("rows")) <= 0:
        failures.append("SAM Contract Awards cannot be marked ok in the composition audit without committed rows")

    group_types = {row.get("groupType", "") for row in rows}
    for group_type in ("agency", "awardType", "recipient"):
        if group_type not in group_types:
            failures.append(f"procurement modification composition audit missing group type: {group_type}")

    defense = next(
        (
            row for row in rows
            if row.get("groupType") == "agency" and row.get("groupValue") == "Department of Defense"
        ),
        None,
    )
    if not defense or audit_number(defense.get("modifiedAmount")) <= 0:
        failures.append("procurement modification composition audit should include Defense modified-amount composition")

    definitive = next(
        (
            row for row in rows
            if row.get("groupType") == "awardType" and row.get("groupValue") == "DEFINITIVE CONTRACT"
        ),
        None,
    )
    if not definitive:
        failures.append("procurement modification composition audit should include DEFINITIVE CONTRACT composition")
    else:
        if audit_number(definitive.get("modifiedRows")) <= 0:
            failures.append("DEFINITIVE CONTRACT composition should include modified rows")
        if audit_number(definitive.get("amountWeightedModificationShare")) <= 0.50:
            failures.append("DEFINITIVE CONTRACT composition should preserve the high amount-weighted modification share")

    text = PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Procurement Modification Composition Audit",
        "bounded sample diagnostic",
        "SAM.gov Contract Awards has",
        "does not clear the procurement-modification source gap",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"procurement modification composition audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "procurement-modification composition audit" not in supplement:
            failures.append("supplement does not disclose the procurement-modification composition audit")
    return failures


def audit_number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def check_claim_boundary_audit() -> list[str]:
    failures: list[str] = []
    if not SOURCE_PANEL_INVENTORY.exists():
        return failures
    missing = [
        path.relative_to(ROOT)
        for path in (CLAIM_BOUNDARY_AUDIT_MD, CLAIM_BOUNDARY_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing claim-boundary audit artifact: {path}" for path in missing]

    with SOURCE_PANEL_INVENTORY.open(newline="", encoding="utf-8") as source:
        panels = list(csv.DictReader(source))
    with CLAIM_BOUNDARY_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        claim_rows = list(csv.DictReader(source))
    claim_by_panel = {row.get("panel", ""): row for row in claim_rows}
    audit_md = CLAIM_BOUNDARY_AUDIT_MD.read_text(encoding="utf-8")
    body = REGGOV_BODY.read_text(encoding="utf-8") if REGGOV_BODY.exists() else ""
    supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8") if SUPPLEMENT_BODY.exists() else ""

    if len(claim_rows) != len(panels):
        failures.append(
            "claim-boundary audit row count does not match source-panel inventory"
        )

    weak_statuses = {"thin", "warning", "fixture-only", "missing"}
    for panel in panels:
        panel_name = panel.get("panel", "")
        status = panel.get("status", "")
        claim = claim_by_panel.get(panel_name)
        if not claim:
            failures.append(f"claim-boundary audit missing panel: {panel_name}")
            continue
        if claim.get("status") != status:
            failures.append(
                f"claim-boundary audit status mismatch for {panel_name}: "
                f"{claim.get('status')} != {status}"
            )
        if status in weak_statuses:
            if panel_name not in audit_md:
                failures.append(f"claim-boundary audit markdown omits weak panel: {panel_name}")
            if claim.get("supportLevel") == "stronger":
                failures.append(f"weak panel has stronger support level: {panel_name}")

    if any(panel.get("status") in weak_statuses for panel in panels):
        required_phrases = [
            "claim-boundary audit",
            "source bridge remains incomplete",
        ]
        combined = body + "\n" + supplement
        for phrase in required_phrases:
            if phrase not in combined:
                failures.append(
                    f"manuscript/supplement missing claim-boundary phrase: {phrase}"
                )

    strong_claim_patterns = [
        r"\bis a calibrated policy simulation\b",
        r"\bempirically validated hidden capture\b",
        r"\bvalidated hidden-channel magnitudes\b",
        r"\brepresentative national source panel\b",
        r"\bcalibrated estimates of reform effects\b",
        r"\bvalidated reform-effect magnitudes\b",
    ]
    checked_files = [
        path for path in (
            REGGOV_BODY,
            SUPPLEMENT_BODY,
            ROOT / "docs" / "validation.md",
            ROOT / "docs" / "source-data-roadmap.md",
        )
        if path.exists()
    ]
    for path in checked_files:
        text = path.read_text(encoding="utf-8")
        for pattern in strong_claim_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                failures.append(
                    f"{path.relative_to(ROOT)} contains source-coverage overclaim: {pattern}"
                )
    return failures


def check_claim_source_dependency_audit() -> list[str]:
    failures: list[str] = []
    if not SOURCE_PANEL_INVENTORY.exists():
        return failures
    missing = [
        path.relative_to(ROOT)
        for path in (CLAIM_SOURCE_DEPENDENCY_MD, CLAIM_SOURCE_DEPENDENCY_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing claim-source dependency audit artifact: {path}" for path in missing]

    with SOURCE_PANEL_INVENTORY.open(newline="", encoding="utf-8") as source:
        panels = list(csv.DictReader(source))
    with CLAIM_SOURCE_DEPENDENCY_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("claimKey", ""): row for row in csv.DictReader(source)}

    required_claims = {
        "lobbying-disclosure-surface",
        "visible-electoral-money",
        "rulemaking-comment-record",
        "procurement-identifier-competition",
        "strategic-substitution-mechanism",
        "public-financing-counterweight",
        "revolving-door-cooling-off",
        "hidden-channel-magnitude",
        "procurement-modification-capture",
        "calibrated-policy-simulation",
    }
    missing_claims = sorted(required_claims - set(rows))
    failures.extend(f"claim-source dependency audit missing claim family: {claim}" for claim in missing_claims)
    if missing_claims:
        return failures

    weak_statuses = {"thin", "warning", "fixture-only", "missing"}
    weak_panels = [panel for panel in panels if panel.get("status") in weak_statuses]
    weak_panel_names = {panel.get("panel", "") for panel in weak_panels}
    if rows["lobbying-disclosure-surface"].get("status") != "cleared":
        failures.append("lobbying disclosure source dependency should be cleared")
    if rows["rulemaking-comment-record"].get("status") != "cleared":
        failures.append("rulemaking comment source dependency should be cleared")
    if rows["hidden-channel-magnitude"].get("status") != "bounded":
        failures.append("hidden-channel magnitude source dependency should stay bounded until donor identities and representative routing coverage exist")
    if weak_panels:
        bounded_expected = set()
        if "Direct dark money" in weak_panel_names or "Revolving door" in weak_panel_names:
            bounded_expected.add("strategic-substitution-mechanism")
        if "Revolving door" in weak_panel_names:
            bounded_expected.add("revolving-door-cooling-off")
        for claim in bounded_expected:
            if rows[claim].get("status") != "bounded":
                failures.append(f"claim-source dependency should be bounded while weak panels remain: {claim}")
        not_cleared_expected = {
            "procurement-modification-capture",
            "calibrated-policy-simulation",
        }
        for claim in not_cleared_expected:
            if rows[claim].get("status") != "not_cleared":
                failures.append(f"claim-source dependency should not be cleared while weak panels remain: {claim}")
    revolving_panel = next((panel for panel in panels if panel.get("panel") == "Revolving door"), {})
    if revolving_panel.get("status") == "usable" and rows["revolving-door-cooling-off"].get("status") != "cleared":
        failures.append("revolving-door source dependency should be cleared when the revolving-door panel is usable")
    public_panel = next((panel for panel in panels if panel.get("panel") == "Public financing"), {})
    if public_panel.get("status") == "usable" and rows["public-financing-counterweight"].get("status") != "cleared":
        failures.append("public-financing source dependency should be cleared when the public-financing panel is usable")

    dependency_md = CLAIM_SOURCE_DEPENDENCY_MD.read_text(encoding="utf-8")
    required_text = [
        "Claim-Source Dependency Audit",
        "Calibrated policy simulation",
        "not_cleared",
        "bounded",
    ]
    for phrase in required_text:
        if phrase not in dependency_md:
            failures.append(f"claim-source dependency markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        required_supplement = [
            "claim-source dependency audit",
            "claim_source_dependency.tex",
        ]
        for phrase in required_supplement:
            if phrase not in supplement:
                failures.append(f"supplement does not disclose claim-source dependency artifact: {phrase}")
    return failures


def check_claim_posture_audit() -> list[str]:
    failures: list[str] = []
    if not SOURCE_PANEL_INVENTORY.exists():
        return failures
    missing = [
        path.relative_to(ROOT)
        for path in (CLAIM_POSTURE_AUDIT_MD, CLAIM_POSTURE_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing claim-posture audit artifact: {path}" for path in missing]

    with SOURCE_PANEL_INVENTORY.open(newline="", encoding="utf-8") as source:
        panels = list(csv.DictReader(source))
    with CLAIM_POSTURE_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("gate", ""): row for row in csv.DictReader(source)}

    required_gates = {
        "Mechanism-model article",
        "Empirical bridge",
        "Calibrated policy-simulation claim",
        "Reproducibility and layout bundle",
    }
    missing_gates = sorted(required_gates - set(rows))
    failures.extend(f"claim-posture audit missing gate: {gate}" for gate in missing_gates)
    if missing_gates:
        return failures

    weak_statuses = {"thin", "warning", "fixture-only", "missing"}
    weak_panels = [panel for panel in panels if panel.get("status") in weak_statuses]
    if rows["Mechanism-model article"].get("status") != "cleared":
        failures.append("mechanism-model claim posture is not cleared")
    if rows["Reproducibility and layout bundle"].get("status") != "cleared":
        failures.append("reproducibility/layout claim posture is not cleared")
    if weak_panels:
        if rows["Empirical bridge"].get("status") != "bounded":
            failures.append("empirical bridge should be bounded while weak panels remain")
        if rows["Calibrated policy-simulation claim"].get("status") != "not_cleared":
            failures.append(
                "calibrated policy-simulation posture should not be cleared while weak panels remain"
            )
    posture_md = CLAIM_POSTURE_AUDIT_MD.read_text(encoding="utf-8")
    posture_md_lower = posture_md.lower()
    required_text = [
        "mechanism-model article",
        "calibrated policy-simulation claim",
        "Weak Source Panels",
        "Claim-Source Dependencies",
    ]
    for phrase in required_text:
        if phrase.lower() not in posture_md_lower:
            failures.append(f"claim-posture audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "claim-posture audit" not in supplement:
            failures.append("supplement does not disclose the claim-posture audit")
    return failures


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
            expected_members = EXPECTED_ZIP_MEMBERS | {
                member for _, member in package_byte_checks()
            }
            failures = [
                f"submission zip missing {member}"
                for member in sorted(expected_members - names)
            ]
            failures.extend(
                f"submission zip should not contain generic {member}"
                for member in sorted(FORBIDDEN_ZIP_MEMBERS & names)
            )
            for source, member in package_byte_checks():
                if member not in names:
                    continue
                if archive.read(member) != source.read_bytes():
                    failures.append(
                        f"submission zip {member} differs from {source.relative_to(ROOT)}"
                    )
            return failures
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        return [f"could not inspect submission zip: {error}"]


def package_byte_checks() -> list[tuple[Path, str]]:
    checks: list[tuple[Path, str]] = [
        (PAPER / "regulation-governance-wiley.tex", f"{LOCAL_BASENAME}.tex"),
        (WILEY_PDF, f"{LOCAL_BASENAME}.pdf"),
        (PAPER / "supplement.tex", "supplement.tex"),
        (SUPPLEMENT_PDF, "supplement.pdf"),
        (PAPER / "references.bib", "references.bib"),
        (PAPER / ".wiley-build" / "USG.cls", "USG.cls"),
        (PAPER / ".wiley-build" / "wileyNJD-Chicago.bst", "wileyNJD-Chicago.bst"),
        (ROOT / "docs" / "odd-model.md", "supporting-information/ODD-model.md"),
        (ROOT / "docs" / "scenario-catalog.md", "supporting-information/scenario-catalog.md"),
        (ROOT / "docs" / "validation.md", "supporting-information/validation-plan.md"),
        (ROOT / "docs" / "source-data-roadmap.md", "supporting-information/source-data-roadmap.md"),
        (ROOT / "reports" / "source-moments.md", "supporting-information/source-moments.md"),
        (ROOT / "reports" / "source-panel-inventory.md", "supporting-information/source-panel-inventory.md"),
        (SOURCE_CAPABILITY_AUDIT_MD, "supporting-information/source-capability-audit.md"),
        (DARK_MONEY_BRIDGE_AUDIT_MD, "supporting-information/dark-money-bridge-audit.md"),
        (INTERMEDIARY_BRIDGE_AUDIT_MD, "supporting-information/intermediary-bridge-audit.md"),
        (REVOLVING_DOOR_BRIDGE_AUDIT_MD, "supporting-information/revolving-door-bridge-audit.md"),
        (PROCUREMENT_DENOMINATOR_AUDIT_MD, "supporting-information/procurement-denominator-audit.md"),
        (
            PROCUREMENT_MODIFICATION_COMPOSITION_AUDIT_MD,
            "supporting-information/procurement-modification-composition-audit.md",
        ),
        (ROOT / "reports" / "claim-boundary-audit.md", "supporting-information/claim-boundary-audit.md"),
        (ROOT / "reports" / "claim-source-dependency.md", "supporting-information/claim-source-dependency.md"),
        (ROOT / "reports" / "claim-posture-audit.md", "supporting-information/claim-posture-audit.md"),
        (ROOT / "reports" / "validation-summary.md", "supporting-information/validation-summary.md"),
        (ROOT / "reports" / "substitution-audit.md", "supporting-information/substitution-audit.md"),
        (ROOT / "reports" / "lobby-capture-portfolio.md", "supporting-information/portfolio-screen.md"),
        (ROOT / "reports" / "calibration-queue.md", "supporting-information/calibration-queue.md"),
        (ROOT / "reports" / "paper-layout-audit.md", "supporting-information/paper-layout-audit.md"),
        (ROOT / "reports" / "manual-visual-audit.md", "supporting-information/manual-visual-audit.md"),
        (CITATION_CFF, "supporting-information/CITATION.cff"),
        (ZENODO_JSON, "supporting-information/zenodo.json"),
    ]
    checks.extend(
        (path, f"sections/{path.name}")
        for path in sorted((PAPER / "sections").glob("*.tex"))
    )
    checks.extend(
        (path, f"tables/{path.name}")
        for path in sorted((PAPER / "tables").glob("*.tex"))
    )
    checks.extend(
        (path, f"figures/{path.name}")
        for path in sorted((PAPER / "figures").glob("*.tex"))
    )
    checks.extend(
        (path, f"figures/{path.name}")
        for path in sorted((PAPER / "figures").glob("Figure_*.pdf"))
    )
    checks.extend(
        (path, f"figures/{path.name}")
        for path in sorted((PAPER / "figures").glob("Figure_*.svg"))
    )
    checks.extend(
        (path, f"supporting-information/report-data/{path.name}")
        for path in report_bundle_inputs()
    )
    return [(path, member) for path, member in checks if path.exists()]


def check_submission_zip_compiles() -> list[str]:
    if not SUBMISSION_ZIP.exists():
        return []
    binaries = {binary: resolve_binary(binary) for binary in ("pdflatex", "bibtex")}
    missing = [binary for binary, path in binaries.items() if path is None]
    if missing:
        return [f"could not compile submission zip; missing binaries: {', '.join(missing)}"]
    pdflatex = str(binaries["pdflatex"])
    bibtex = str(binaries["bibtex"])

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
            [pdflatex, "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            [bibtex, LOCAL_BASENAME],
            [pdflatex, "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
            [pdflatex, "-interaction=nonstopmode", f"{LOCAL_BASENAME}.tex"],
        ]
        for command in commands:
            result = run_compile_command(command, temp, env)
            if result.timed_out:
                return [
                    "submission zip compile timed out with "
                    f"`{' '.join(command)}` after {SUBMISSION_COMPILE_TIMEOUT_SECONDS} seconds:\n"
                    + result.tail
                ]
            if Path(command[0]).name == "pdflatex" and is_nonfatal_latex_pass(result.output, temp / f"{LOCAL_BASENAME}.pdf"):
                continue
            if result.returncode != 0:
                return [
                    "submission zip does not compile from extracted root with "
                    f"`{' '.join(command)}`:\n{result.tail}"
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
    pdflatex = resolve_binary("pdflatex")
    if pdflatex is None:
        return ["could not compile submission supplement; missing binary: pdflatex"]
    commands = [
        [str(pdflatex), "-interaction=nonstopmode", "supplement.tex"],
        [str(pdflatex), "-interaction=nonstopmode", "supplement.tex"],
    ]
    for command in commands:
        result = run_compile_command(command, temp, env)
        if result.timed_out:
            return [
                "submission supplement compile timed out with "
                f"`{' '.join(command)}` after {SUBMISSION_COMPILE_TIMEOUT_SECONDS} seconds:\n"
                + result.tail
            ]
        if Path(command[0]).name == "pdflatex" and is_nonfatal_latex_pass(result.output, temp / "supplement.pdf"):
            continue
        if result.returncode != 0:
            return [
                "submission supplement does not compile from extracted root with "
                f"`{' '.join(command)}`:\n{result.tail}"
            ]
    return []


class CompileResult:
    def __init__(self, returncode: int, output: str, timed_out: bool = False) -> None:
        self.returncode = returncode
        self.output = output
        self.timed_out = timed_out

    @property
    def tail(self) -> str:
        return "\n".join(self.output.splitlines()[-20:])


def run_compile_command(command: list[str], cwd: Path, env: dict[str, str]) -> CompileResult:
    with tempfile.NamedTemporaryFile(
        mode="w+",
        encoding="utf-8",
        errors="replace",
        prefix="lobby-capture-compile-",
        suffix=".log",
    ) as output:
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                text=True,
                stdout=output,
                stderr=subprocess.STDOUT,
                timeout=SUBMISSION_COMPILE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            output.seek(0)
            return CompileResult(124, output.read(), timed_out=True)
        output.seek(0)
        return CompileResult(completed.returncode, output.read())


def resolve_binary(name: str) -> Path | None:
    located = shutil.which(name)
    if located:
        return Path(located)
    for directory in TEX_BINARY_DIRS:
        candidate = directory / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


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
