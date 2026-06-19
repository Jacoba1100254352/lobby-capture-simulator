#!/usr/bin/env python3
"""Check that generated paper PDFs and submission artifacts are current."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
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
LATEX_LOGS = [
    PAPER / f"{LOCAL_BASENAME}.log",
    PAPER / "regulation-governance-wiley.log",
    PAPER / "supplement.log",
]
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
PROCUREMENT_BENCHMARK_CROSSWALK_MD = ROOT / "reports" / "procurement-benchmark-crosswalk.md"
PROCUREMENT_BENCHMARK_CROSSWALK_CSV = ROOT / "reports" / "procurement-benchmark-crosswalk.csv"
PROCUREMENT_REFRESH_READINESS_MD = ROOT / "reports" / "procurement-refresh-readiness.md"
PROCUREMENT_REFRESH_READINESS_CSV = ROOT / "reports" / "procurement-refresh-readiness.csv"
FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_MD = ROOT / "reports" / "first-wave-procurement-source-acquisition.md"
FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_CSV = ROOT / "reports" / "first-wave-procurement-source-acquisition.csv"
LAYOUT_AUDIT = ROOT / "reports" / "paper-layout-audit.md"
MANUAL_VISUAL_AUDIT = ROOT / "reports" / "manual-visual-audit.md"
CLAIM_BOUNDARY_AUDIT_MD = ROOT / "reports" / "claim-boundary-audit.md"
CLAIM_BOUNDARY_AUDIT_CSV = ROOT / "reports" / "claim-boundary-audit.csv"
VALIDATION_GAP_TABLE = PAPER / "tables" / "validation_gap_snapshot.tex"
CLAIM_SOURCE_DEPENDENCY_MD = ROOT / "reports" / "claim-source-dependency.md"
CLAIM_SOURCE_DEPENDENCY_CSV = ROOT / "reports" / "claim-source-dependency.csv"
CLAIM_LADDER_TABLE = PAPER / "tables" / "claim_ladder.tex"
CAUSAL_CALIBRATION_TARGETS_MD = ROOT / "reports" / "causal-calibration-targets.md"
CAUSAL_CALIBRATION_TARGETS_CSV = ROOT / "reports" / "causal-calibration-targets.csv"
FIRST_WAVE_CAUSAL_PROTOCOLS_MD = ROOT / "reports" / "first-wave-causal-protocols.md"
FIRST_WAVE_CAUSAL_PROTOCOLS_CSV = ROOT / "reports" / "first-wave-causal-protocols.csv"
FIRST_WAVE_CAUSAL_PROTOCOLS_TABLE = PAPER / "tables" / "first_wave_causal_protocols.tex"
FIRST_WAVE_SOURCE_PRODUCTS_MD = ROOT / "reports" / "first-wave-source-products.md"
FIRST_WAVE_SOURCE_PRODUCTS_CSV = ROOT / "reports" / "first-wave-source-products.csv"
FIRST_WAVE_SOURCE_TEMPLATE_DIR = ROOT / "docs" / "source-product-templates" / "first-wave"
FIRST_WAVE_SOURCE_TEMPLATE_MANIFEST_CSV = FIRST_WAVE_SOURCE_TEMPLATE_DIR / "manifest.csv"
FIRST_WAVE_SOURCE_TEMPLATE_MANIFEST_MD = FIRST_WAVE_SOURCE_TEMPLATE_DIR / "manifest.md"
FIRST_WAVE_SOURCE_TEMPLATE_README = FIRST_WAVE_SOURCE_TEMPLATE_DIR / "README.md"
FIRST_WAVE_SOURCE_PRODUCT_DIR = ROOT / "data" / "calibration" / "first-wave"
FIRST_WAVE_CANDIDATE_SEED_PRODUCTS = {
    "actor-issue-time-spine": FIRST_WAVE_SOURCE_PRODUCT_DIR / "actor-issue-time-spine.csv",
    "substitution-comparison-groups": FIRST_WAVE_SOURCE_PRODUCT_DIR / "substitution-comparison-groups.csv",
    "sam-fpds-action-history-crosswalk": FIRST_WAVE_SOURCE_PRODUCT_DIR / "sam-fpds-action-history-crosswalk.csv",
    "gao-protest-overlay": FIRST_WAVE_SOURCE_PRODUCT_DIR / "gao-protest-overlay.csv",
    "sam-exclusion-overlay": FIRST_WAVE_SOURCE_PRODUCT_DIR / "sam-exclusion-overlay.csv",
    "procurement-firewall-overlay": FIRST_WAVE_SOURCE_PRODUCT_DIR / "procurement-firewall-overlay.csv",
    "procurement-offer-competition-enrichment": FIRST_WAVE_SOURCE_PRODUCT_DIR / "procurement-offer-competition-enrichment.csv",
    "agency-response-final-rule-linkage": FIRST_WAVE_SOURCE_PRODUCT_DIR / "agency-response-final-rule-linkage.csv",
    "canonical-actor-identifiers": FIRST_WAVE_SOURCE_PRODUCT_DIR / "canonical-actor-identifiers.csv",
    "alias-resolution-audit-sample": FIRST_WAVE_SOURCE_PRODUCT_DIR / "alias-resolution-audit-sample.csv",
    "issue-code-crosswalk": FIRST_WAVE_SOURCE_PRODUCT_DIR / "issue-code-crosswalk.csv",
    "false-match-review-log": FIRST_WAVE_SOURCE_PRODUCT_DIR / "false-match-review-log.csv",
    "linked-actor-issue-venue-time": FIRST_WAVE_SOURCE_PRODUCT_DIR / "linked-actor-issue-venue-time.csv",
}
FIRST_WAVE_TEXT_SOURCE_PRODUCTS = {
    "comment-body-corpus": FIRST_WAVE_SOURCE_PRODUCT_DIR / "comment-body-corpus.csv",
    "duplicate-template-clusters": FIRST_WAVE_SOURCE_PRODUCT_DIR / "comment-template-clusters.csv",
    "meeting-log-or-missing-channel-note": FIRST_WAVE_SOURCE_PRODUCT_DIR / "meeting-log-channel-note.md",
}
FIRST_WAVE_LINKAGE_CANDIDATES_MD = ROOT / "reports" / "first-wave-linkage-candidates.md"
FIRST_WAVE_LINKAGE_CANDIDATES_CSV = ROOT / "reports" / "first-wave-linkage-candidates.csv"
FIRST_WAVE_LINKAGE_CANDIDATE_RECORDS_CSV = ROOT / "reports" / "first-wave-linkage-candidate-records.csv"
FIRST_WAVE_SOURCE_READINESS_MD = ROOT / "reports" / "first-wave-source-readiness.md"
FIRST_WAVE_SOURCE_READINESS_CSV = ROOT / "reports" / "first-wave-source-readiness.csv"
CLAIM_POSTURE_AUDIT_MD = ROOT / "reports" / "claim-posture-audit.md"
CLAIM_POSTURE_AUDIT_CSV = ROOT / "reports" / "claim-posture-audit.csv"
VALIDATION_SCOPE_COVERAGE_MD = ROOT / "reports" / "validation-scope-coverage.md"
VALIDATION_SCOPE_COVERAGE_CSV = ROOT / "reports" / "validation-scope-coverage.csv"
CALIBRATION_READINESS_MD = ROOT / "reports" / "calibration-readiness.md"
CALIBRATION_READINESS_CSV = ROOT / "reports" / "calibration-readiness.csv"
POLICY_CLAIM_LANGUAGE_AUDIT_MD = ROOT / "reports" / "policy-claim-language-audit.md"
POLICY_CLAIM_LANGUAGE_AUDIT_CSV = ROOT / "reports" / "policy-claim-language-audit.csv"
LITERATURE_POSITIONING_AUDIT_MD = ROOT / "reports" / "literature-positioning-audit.md"
LITERATURE_POSITIONING_AUDIT_CSV = ROOT / "reports" / "literature-positioning-audit.csv"
REFERENCE_INTEGRITY_AUDIT_MD = ROOT / "reports" / "reference-integrity-audit.md"
REFERENCE_INTEGRITY_AUDIT_CSV = ROOT / "reports" / "reference-integrity-audit.csv"
SUBMISSION_READINESS_MD = ROOT / "reports" / "submission-readiness.md"
SUBMISSION_READINESS_CSV = ROOT / "reports" / "submission-readiness.csv"
REVIEWER_RISK_REGISTER_CSV = ROOT / "reports" / "reviewer-risk-register.csv"
REVIEWER_RISK_REGISTER_MD = ROOT / "reports" / "reviewer-risk-register.md"
LATEX_LOG_AUDIT_MD = ROOT / "reports" / "latex-log-audit.md"
LATEX_LOG_AUDIT_CSV = ROOT / "reports" / "latex-log-audit.csv"
FINAL_HUMAN_READTHROUGH = ROOT / "reports" / "final-human-readthrough.md"
FINAL_HUMAN_READTHROUGH_AUDIT_CSV = ROOT / "reports" / "final-human-readthrough-audit.csv"
FINAL_HUMAN_READTHROUGH_AUDIT_MD = ROOT / "reports" / "final-human-readthrough-audit.md"
FINAL_READTHROUGH_EVIDENCE_CSV = ROOT / "reports" / "final-readthrough-evidence.csv"
FINAL_READTHROUGH_EVIDENCE_MD = ROOT / "reports" / "final-readthrough-evidence.md"
ARCHIVE_HANDOFF_CSV = ROOT / "reports" / "archive-handoff-manifest.csv"
ARCHIVE_HANDOFF_JSON = ROOT / "reports" / "archive-handoff-manifest.json"
ARCHIVE_HANDOFF_MD = ROOT / "reports" / "archive-handoff-manifest.md"
ZENODO_DEPOSIT_PREFLIGHT_CSV = ROOT / "reports" / "zenodo-deposit-preflight.csv"
ZENODO_DEPOSIT_PREFLIGHT_MD = ROOT / "reports" / "zenodo-deposit-preflight.md"
DOI_DEPOSIT_READINESS_CSV = ROOT / "reports" / "doi-deposit-readiness.csv"
DOI_DEPOSIT_READINESS_MD = ROOT / "reports" / "doi-deposit-readiness.md"
WILEY_SUBMISSION_FORM_READINESS_CSV = ROOT / "reports" / "wiley-submission-form-readiness.csv"
WILEY_SUBMISSION_FORM_READINESS_MD = ROOT / "reports" / "wiley-submission-form-readiness.md"
REGGOV_GUIDELINES_READINESS_CSV = ROOT / "reports" / "reggov-guidelines-readiness.csv"
REGGOV_GUIDELINES_READINESS_MD = ROOT / "reports" / "reggov-guidelines-readiness.md"
RELEASE_ASSET_CHECKSUM_CSV = ROOT / "dist" / "release-asset-checksums.csv"
RELEASE_ASSET_CHECKSUM_JSON = ROOT / "dist" / "release-asset-checksums.json"
RELEASE_ASSET_CHECKSUM_MD = ROOT / "dist" / "release-asset-checksums.md"
DOI_DEPOSIT_PACKAGE = ROOT / "dist" / "lobby-capture-doi-deposit-package.zip"
DOI_DEPOSIT_PACKAGE_MANIFEST_JSON = ROOT / "dist" / "doi-deposit-package-manifest.json"
DOI_DEPOSIT_PACKAGE_MANIFEST_MD = ROOT / "dist" / "doi-deposit-package-manifest.md"
DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV = ROOT / "dist" / "doi-deposit-package-checksum.csv"
DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON = ROOT / "dist" / "doi-deposit-package-checksum.json"
DOI_DEPOSIT_PACKAGE_CHECKSUM_MD = ROOT / "dist" / "doi-deposit-package-checksum.md"
ZENODO_DEPOSIT_METADATA_JSON = ROOT / "dist" / "zenodo-deposit-metadata.json"
RELEASE_TAG = "paper-publication-readiness-2026-06-18-r183"
ARCHIVE_HANDOFF_REPORT_NAMES = {
    "archive-handoff-manifest.csv",
    "archive-handoff-manifest.json",
    "archive-handoff-manifest.md",
}
POST_SUBMISSION_REPORT_NAMES = ARCHIVE_HANDOFF_REPORT_NAMES | {
    "zenodo-deposit-preflight.csv",
    "zenodo-deposit-preflight.md",
    "doi-deposit-readiness.csv",
    "doi-deposit-readiness.md",
    "wiley-submission-form-readiness.csv",
    "wiley-submission-form-readiness.md",
    "reggov-guidelines-readiness.csv",
    "reggov-guidelines-readiness.md",
    "final-readthrough-evidence.csv",
    "final-readthrough-evidence.md",
}
LOCAL_OPERATIONAL_REPORT_PREFIXES = (
    "external-finalization-checklist.",
    "gao-protest-feed-preflight.",
    "github-ci-status-audit.",
    "github-release-asset-audit.",
    "sam-contract-awards-export-audit.",
    "sam-contract-awards-preflight.",
    "usaspending-transaction-download-strata.",
)
SUBMISSION_REPORT_DATA_EXCLUSIONS = {
    "first-wave-linkage-candidate-records.csv",
}
TRACKED_SOURCE_CHECKSUM_STATUS = "tracked-source-verified"
RELEASE_ASSET_CHECKSUM_STATUS = "release-asset-checksum-recorded-in-dist"
CITATION_CFF = ROOT / "CITATION.cff"
ZENODO_JSON = ROOT / ".zenodo.json"
FORBIDDEN_LOCAL_ARTIFACTS = [
    PAPER / "main.tex",
    PAPER / "main.pdf",
]
FORBIDDEN_COPY_SUFFIX_ROOTS = [
    PAPER,
    ROOT / "reports",
    DIST,
]
FORBIDDEN_COPY_SUFFIX = re.compile(
    r".+ [0-9]+\.(aux|bbl|blg|bst|cff|cls|csv|eps|json|log|md|out|pag|pdf|sty|svg|tex|txt|zip)$",
    re.IGNORECASE,
)
FORBIDDEN_ZIP_MEMBERS = {
    "main.tex",
    "main.pdf",
    "supporting-information/submission-release-checklist.md",
    "supporting-information/report-data/archive-handoff-manifest.csv",
    "supporting-information/report-data/archive-handoff-manifest.json",
    "supporting-information/report-data/archive-handoff-manifest.md",
    "supporting-information/report-data/doi-deposit-readiness.csv",
    "supporting-information/report-data/doi-deposit-readiness.md",
    "supporting-information/report-data/wiley-submission-form-readiness.csv",
    "supporting-information/report-data/wiley-submission-form-readiness.md",
    "supporting-information/report-data/reggov-guidelines-readiness.csv",
    "supporting-information/report-data/reggov-guidelines-readiness.md",
    "supporting-information/report-data/external-finalization-checklist.csv",
    "supporting-information/report-data/external-finalization-checklist.md",
    "supporting-information/report-data/final-readthrough-evidence.csv",
    "supporting-information/report-data/final-readthrough-evidence.md",
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
    "tables/claim_ladder.tex",
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
    "supporting-information/procurement-benchmark-crosswalk.md",
    "supporting-information/procurement-refresh-readiness.md",
    "supporting-information/first-wave-procurement-source-acquisition.md",
    "supporting-information/claim-boundary-audit.md",
    "supporting-information/claim-source-dependency.md",
    "supporting-information/causal-calibration-targets.md",
    "supporting-information/first-wave-causal-protocols.md",
    "supporting-information/first-wave-source-products.md",
    "supporting-information/first-wave-linkage-candidates.md",
    "supporting-information/first-wave-source-readiness.md",
    "supporting-information/claim-posture-audit.md",
    "supporting-information/policy-claim-language-audit.md",
    "supporting-information/submission-readiness.md",
    "supporting-information/latex-log-audit.md",
    "supporting-information/validation-summary.md",
    "supporting-information/validation-scope-coverage.md",
    "supporting-information/substitution-audit.md",
    "supporting-information/portfolio-screen.md",
    "supporting-information/calibration-queue.md",
    "supporting-information/calibration-readiness.md",
    "supporting-information/paper-layout-audit.md",
    "supporting-information/manual-visual-audit.md",
    "supporting-information/final-human-readthrough.md",
    "supporting-information/final-human-readthrough-audit.md",
    "supporting-information/final-readthrough-evidence.md",
    "supporting-information/submission-package-manifest.json",
    "supporting-information/submission-package-manifest.md",
    "supporting-information/CITATION.cff",
    "supporting-information/zenodo.json",
    "supporting-information/source-product-templates/first-wave/README.md",
    "supporting-information/source-product-templates/first-wave/manifest.csv",
    "supporting-information/source-product-templates/first-wave/manifest.md",
    "supporting-information/source-product-templates/first-wave/substitution-reform-shocks.csv",
    "supporting-information/source-product-templates/first-wave/actor-issue-time-spine.csv",
    "supporting-information/source-product-templates/first-wave/substitution-comparison-groups.csv",
    "supporting-information/source-product-templates/first-wave/meeting-log-channel-note.md",
    "supporting-information/source-product-templates/first-wave/sam-fpds-action-history-crosswalk.csv",
    "supporting-information/source-product-templates/first-wave/gao-protest-overlay.csv",
    "supporting-information/source-product-templates/first-wave/sam-exclusion-overlay.csv",
    "supporting-information/source-product-templates/first-wave/procurement-firewall-overlay.csv",
    "supporting-information/source-product-templates/first-wave/comment-body-corpus.csv",
    "supporting-information/source-product-templates/first-wave/comment-template-clusters.csv",
    "supporting-information/source-product-templates/first-wave/agency-response-final-rule-linkage.csv",
    "supporting-information/source-product-templates/first-wave/canonical-actor-identifiers.csv",
    "supporting-information/source-product-templates/first-wave/alias-resolution-audit-sample.csv",
    "supporting-information/source-product-templates/first-wave/issue-code-crosswalk.csv",
    "supporting-information/source-product-templates/first-wave/false-match-review-log.csv",
    "supporting-information/source-product-templates/first-wave/linked-actor-issue-venue-time.csv",
}


def main() -> int:
    failures: list[str] = []
    failures.extend(
        check_exists([
            LOCAL_PDF,
            WILEY_PDF,
            SUPPLEMENT_PDF,
            SUBMISSION_ZIP,
            ARCHIVE_HANDOFF_CSV,
            ARCHIVE_HANDOFF_JSON,
            ARCHIVE_HANDOFF_MD,
            DOI_DEPOSIT_PACKAGE,
            DOI_DEPOSIT_PACKAGE_MANIFEST_JSON,
            DOI_DEPOSIT_PACKAGE_MANIFEST_MD,
            DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV,
            DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON,
            DOI_DEPOSIT_PACKAGE_CHECKSUM_MD,
            ZENODO_DEPOSIT_PREFLIGHT_CSV,
            ZENODO_DEPOSIT_PREFLIGHT_MD,
            VALIDATION_SCOPE_COVERAGE_CSV,
            VALIDATION_SCOPE_COVERAGE_MD,
            REGGOV_GUIDELINES_READINESS_CSV,
            REGGOV_GUIDELINES_READINESS_MD,
            REVIEWER_RISK_REGISTER_CSV,
            REVIEWER_RISK_REGISTER_MD,
            LITERATURE_POSITIONING_AUDIT_CSV,
            LITERATURE_POSITIONING_AUDIT_MD,
            REFERENCE_INTEGRITY_AUDIT_CSV,
            REFERENCE_INTEGRITY_AUDIT_MD,
            FINAL_READTHROUGH_EVIDENCE_CSV,
            FINAL_READTHROUGH_EVIDENCE_MD,
        ])
    )
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
    failures.extend(check_procurement_benchmark_crosswalk())
    failures.extend(check_procurement_refresh_readiness())
    failures.extend(check_first_wave_procurement_source_acquisition())
    failures.extend(check_claim_boundary_audit())
    failures.extend(check_claim_source_dependency_audit())
    failures.extend(check_causal_calibration_targets())
    failures.extend(check_first_wave_causal_protocols())
    failures.extend(check_first_wave_source_product_templates())
    failures.extend(check_first_wave_source_products())
    failures.extend(check_first_wave_linkage_candidates())
    failures.extend(check_first_wave_source_readiness())
    failures.extend(check_claim_posture_audit())
    failures.extend(check_validation_scope_coverage())
    failures.extend(check_policy_claim_language_audit())
    failures.extend(check_literature_positioning_audit())
    failures.extend(check_reference_integrity_audit())
    failures.extend(check_final_human_readthrough())
    failures.extend(check_final_human_readthrough_audit())
    failures.extend(check_final_readthrough_evidence())
    failures.extend(check_submission_readiness_audit())
    failures.extend(check_reviewer_risk_register())
    failures.extend(check_latex_log_audit())
    failures.extend(check_layout_and_visual_reports())
    failures.extend(check_archive_metadata())
    failures.extend(check_archive_handoff_manifest())
    failures.extend(check_doi_deposit_package())
    failures.extend(check_zenodo_deposit_preflight())
    failures.extend(check_doi_deposit_readiness())
    failures.extend(check_wiley_submission_form_readiness())
    failures.extend(check_reggov_guidelines_readiness())
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


def git_tracked(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(relative)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return False
    return result.returncode == 0


def check_forbidden_local_artifacts() -> list[str]:
    failures = [
        f"stale generic paper artifact remains: {path.relative_to(ROOT)}"
        for path in FORBIDDEN_LOCAL_ARTIFACTS
        if path.exists()
    ]
    for scan_root in FORBIDDEN_COPY_SUFFIX_ROOTS:
        if not scan_root.exists():
            continue
        failures.extend(
            f"duplicate copy-suffix artifact remains: {path.relative_to(ROOT)}"
            for path in sorted(scan_root.rglob("*"))
            if path.is_file() and FORBIDDEN_COPY_SUFFIX.fullmatch(path.name)
        )
    return failures


def check_freshness() -> list[str]:
    failures: list[str] = []
    checks = [
        (LOCAL_PDF, local_pdf_inputs()),
        (WILEY_PDF, wiley_pdf_inputs()),
        (SUPPLEMENT_PDF, supplement_pdf_inputs()),
        (LATEX_LOG_AUDIT_MD, latex_log_audit_inputs()),
        (LATEX_LOG_AUDIT_CSV, latex_log_audit_inputs()),
        (SUBMISSION_ZIP, submission_inputs()),
        (ARCHIVE_HANDOFF_CSV, archive_handoff_inputs()),
        (ARCHIVE_HANDOFF_JSON, archive_handoff_inputs()),
        (ARCHIVE_HANDOFF_MD, archive_handoff_inputs()),
        (DOI_DEPOSIT_PACKAGE, doi_deposit_package_inputs()),
        (DOI_DEPOSIT_PACKAGE_MANIFEST_JSON, doi_deposit_package_inputs()),
        (DOI_DEPOSIT_PACKAGE_MANIFEST_MD, doi_deposit_package_inputs()),
        (DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV, doi_deposit_package_inputs()),
        (DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON, doi_deposit_package_inputs()),
        (DOI_DEPOSIT_PACKAGE_CHECKSUM_MD, doi_deposit_package_inputs()),
        (ZENODO_DEPOSIT_PREFLIGHT_CSV, zenodo_deposit_preflight_inputs()),
        (ZENODO_DEPOSIT_PREFLIGHT_MD, zenodo_deposit_preflight_inputs()),
        (ZENODO_DEPOSIT_METADATA_JSON, zenodo_deposit_preflight_inputs()),
        (DOI_DEPOSIT_READINESS_CSV, doi_deposit_readiness_inputs()),
        (DOI_DEPOSIT_READINESS_MD, doi_deposit_readiness_inputs()),
        (WILEY_SUBMISSION_FORM_READINESS_CSV, wiley_submission_form_readiness_inputs()),
        (WILEY_SUBMISSION_FORM_READINESS_MD, wiley_submission_form_readiness_inputs()),
        (REGGOV_GUIDELINES_READINESS_CSV, reggov_guidelines_readiness_inputs()),
        (REGGOV_GUIDELINES_READINESS_MD, reggov_guidelines_readiness_inputs()),
        (LITERATURE_POSITIONING_AUDIT_CSV, literature_positioning_audit_inputs()),
        (LITERATURE_POSITIONING_AUDIT_MD, literature_positioning_audit_inputs()),
        (REFERENCE_INTEGRITY_AUDIT_CSV, reference_integrity_audit_inputs()),
        (REFERENCE_INTEGRITY_AUDIT_MD, reference_integrity_audit_inputs()),
        (FINAL_READTHROUGH_EVIDENCE_CSV, final_readthrough_evidence_inputs()),
        (FINAL_READTHROUGH_EVIDENCE_MD, final_readthrough_evidence_inputs()),
        (REVIEWER_RISK_REGISTER_CSV, reviewer_risk_register_inputs()),
        (REVIEWER_RISK_REGISTER_MD, reviewer_risk_register_inputs()),
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
        ROOT / "scripts" / "write-first-wave-causal-protocols.py",
        ROOT / "scripts" / "write-first-wave-source-product-templates.py",
        ROOT / "scripts" / "build-first-wave-entity-resolution-seeds.py",
        ROOT / "scripts" / "build-first-wave-comment-linkage-seeds.py",
        ROOT / "scripts" / "audit-first-wave-source-products.py",
        ROOT / "scripts" / "build-first-wave-linkage-candidates.py",
        ROOT / "scripts" / "audit-first-wave-source-readiness.py",
        ROOT / "scripts" / "write-first-wave-procurement-source-acquisition.py",
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
        PROCUREMENT_BENCHMARK_CROSSWALK_MD,
        PROCUREMENT_REFRESH_READINESS_MD,
        FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_MD,
        ROOT / "reports" / "claim-boundary-audit.md",
        ROOT / "reports" / "claim-source-dependency.md",
        CAUSAL_CALIBRATION_TARGETS_MD,
        FIRST_WAVE_CAUSAL_PROTOCOLS_MD,
        FIRST_WAVE_SOURCE_PRODUCTS_MD,
        FIRST_WAVE_LINKAGE_CANDIDATES_MD,
        FIRST_WAVE_SOURCE_READINESS_MD,
        ROOT / "reports" / "claim-posture-audit.md",
        ROOT / "reports" / "validation-summary.md",
        ROOT / "reports" / "substitution-audit.md",
        ROOT / "reports" / "lobby-capture-portfolio.md",
        ROOT / "reports" / "calibration-queue.md",
        ROOT / "reports" / "calibration-readiness.md",
        POLICY_CLAIM_LANGUAGE_AUDIT_MD,
        SUBMISSION_READINESS_MD,
        LATEX_LOG_AUDIT_MD,
        ROOT / "reports" / "paper-layout-audit.md",
        ROOT / "reports" / "manual-visual-audit.md",
        *report_bundle_inputs(),
        PAPER / ".wiley-build" / "USG.cls",
        PAPER / ".wiley-build" / "wileyNJD-Chicago.bst",
        PAPER / ".wiley-template" / "Optimal-Design-layout" / "LETTERSP.STY",
        *sorted(FIRST_WAVE_SOURCE_TEMPLATE_DIR.glob("*")),
        *sorted(FIRST_WAVE_CANDIDATE_SEED_PRODUCTS.values()),
        *sorted(FIRST_WAVE_TEXT_SOURCE_PRODUCTS.values()),
        *sorted((PAPER / "sections").glob("*.tex")),
        *sorted((PAPER / "tables").glob("*.tex")),
        *sorted((PAPER / "figures").glob("*.tex")),
        *sorted((PAPER / "figures").glob("Figure_*.pdf")),
        *sorted((PAPER / "figures").glob("Figure_*.svg")),
    ]


def latex_log_audit_inputs() -> list[Path]:
    return [
        ROOT / "scripts" / "audit-latex-logs.py",
        *LATEX_LOGS,
    ]


def report_bundle_inputs() -> list[Path]:
    return [
        path
        for path in [
            *sorted((ROOT / "reports").glob("*.csv")),
            *sorted((ROOT / "reports").glob("*.md")),
            *sorted((ROOT / "reports").glob("*.manifest.json")),
        ]
        if path.name not in POST_SUBMISSION_REPORT_NAMES
        and not path.name.startswith(LOCAL_OPERATIONAL_REPORT_PREFIXES)
    ]


def archive_handoff_inputs() -> list[Path]:
    return [
        SUBMISSION_ZIP,
        WILEY_PDF,
        LOCAL_PDF,
        SUPPLEMENT_PDF,
        CITATION_CFF,
        ZENODO_JSON,
        SUBMISSION_READINESS_MD,
        REVIEWER_RISK_REGISTER_CSV,
        REVIEWER_RISK_REGISTER_MD,
        FINAL_HUMAN_READTHROUGH,
        ROOT / "scripts" / "write-archive-handoff-manifest.py",
    ]


def doi_deposit_readiness_inputs() -> list[Path]:
    return [
        DOI_DEPOSIT_PACKAGE,
        DOI_DEPOSIT_PACKAGE_MANIFEST_JSON,
        DOI_DEPOSIT_PACKAGE_MANIFEST_MD,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_MD,
        ZENODO_DEPOSIT_PREFLIGHT_CSV,
        ZENODO_DEPOSIT_PREFLIGHT_MD,
        ZENODO_DEPOSIT_METADATA_JSON,
        ARCHIVE_HANDOFF_CSV,
        ARCHIVE_HANDOFF_JSON,
        ARCHIVE_HANDOFF_MD,
        RELEASE_ASSET_CHECKSUM_CSV,
        RELEASE_ASSET_CHECKSUM_JSON,
        RELEASE_ASSET_CHECKSUM_MD,
        SUBMISSION_READINESS_CSV,
        SUBMISSION_READINESS_MD,
        REVIEWER_RISK_REGISTER_CSV,
        REVIEWER_RISK_REGISTER_MD,
        FINAL_HUMAN_READTHROUGH,
        CITATION_CFF,
        ZENODO_JSON,
        SUBMISSION_DECLARATIONS,
        ROOT / "scripts" / "prepare-zenodo-deposit.py",
        ROOT / "scripts" / "audit-doi-deposit-readiness.py",
    ]


def zenodo_deposit_preflight_inputs() -> list[Path]:
    return [
        DOI_DEPOSIT_PACKAGE,
        DOI_DEPOSIT_PACKAGE_MANIFEST_JSON,
        DOI_DEPOSIT_PACKAGE_MANIFEST_MD,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_MD,
        ARCHIVE_HANDOFF_JSON,
        SUBMISSION_READINESS_CSV,
        FINAL_HUMAN_READTHROUGH,
        CITATION_CFF,
        ZENODO_JSON,
        ROOT / "scripts" / "prepare-zenodo-deposit.py",
    ]


def doi_deposit_package_inputs() -> list[Path]:
    return [
        SUBMISSION_ZIP,
        WILEY_PDF,
        LOCAL_PDF,
        SUPPLEMENT_PDF,
        CITATION_CFF,
        ZENODO_JSON,
        RELEASE_ASSET_CHECKSUM_CSV,
        RELEASE_ASSET_CHECKSUM_JSON,
        RELEASE_ASSET_CHECKSUM_MD,
        ARCHIVE_HANDOFF_CSV,
        ARCHIVE_HANDOFF_JSON,
        ARCHIVE_HANDOFF_MD,
        SUBMISSION_READINESS_CSV,
        SUBMISSION_READINESS_MD,
        REVIEWER_RISK_REGISTER_CSV,
        REVIEWER_RISK_REGISTER_MD,
        WILEY_SUBMISSION_FORM_READINESS_CSV,
        WILEY_SUBMISSION_FORM_READINESS_MD,
        REGGOV_GUIDELINES_READINESS_CSV,
        REGGOV_GUIDELINES_READINESS_MD,
        LITERATURE_POSITIONING_AUDIT_CSV,
        LITERATURE_POSITIONING_AUDIT_MD,
        REFERENCE_INTEGRITY_AUDIT_CSV,
        REFERENCE_INTEGRITY_AUDIT_MD,
        FINAL_HUMAN_READTHROUGH,
        FINAL_HUMAN_READTHROUGH_AUDIT_CSV,
        FINAL_HUMAN_READTHROUGH_AUDIT_MD,
        FINAL_READTHROUGH_EVIDENCE_CSV,
        FINAL_READTHROUGH_EVIDENCE_MD,
        ROOT / "scripts" / "build-doi-deposit-package.py",
    ]


def final_readthrough_evidence_inputs() -> list[Path]:
    return [
        FINAL_HUMAN_READTHROUGH,
        FINAL_HUMAN_READTHROUGH_AUDIT_CSV,
        FINAL_HUMAN_READTHROUGH_AUDIT_MD,
        SUBMISSION_READINESS_CSV,
        SUBMISSION_READINESS_MD,
        REVIEWER_RISK_REGISTER_CSV,
        REVIEWER_RISK_REGISTER_MD,
        CLAIM_POSTURE_AUDIT_CSV,
        CLAIM_POSTURE_AUDIT_MD,
        POLICY_CLAIM_LANGUAGE_AUDIT_CSV,
        POLICY_CLAIM_LANGUAGE_AUDIT_MD,
        LITERATURE_POSITIONING_AUDIT_CSV,
        LITERATURE_POSITIONING_AUDIT_MD,
        REFERENCE_INTEGRITY_AUDIT_CSV,
        REFERENCE_INTEGRITY_AUDIT_MD,
        SOURCE_PANEL_INVENTORY,
        SOURCE_CAPABILITY_AUDIT_CSV,
        SOURCE_CAPABILITY_AUDIT_MD,
        CAUSAL_CALIBRATION_TARGETS_CSV,
        CAUSAL_CALIBRATION_TARGETS_MD,
        LATEX_LOG_AUDIT_CSV,
        LATEX_LOG_AUDIT_MD,
        ROOT / "reports" / "paper-layout-audit.md",
        ROOT / "reports" / "manual-visual-audit.md",
        ARCHIVE_HANDOFF_CSV,
        ARCHIVE_HANDOFF_JSON,
        ARCHIVE_HANDOFF_MD,
        WILEY_SUBMISSION_FORM_READINESS_CSV,
        WILEY_SUBMISSION_FORM_READINESS_MD,
        REGGOV_GUIDELINES_READINESS_CSV,
        REGGOV_GUIDELINES_READINESS_MD,
        ROOT / "paper" / "sections" / "reggov-body.tex",
        ROOT / "paper" / "sections" / "submission-declarations.tex",
        ROOT / "paper" / "references.bib",
        ROOT / "scripts" / "write-final-readthrough-evidence.py",
    ]


def literature_positioning_audit_inputs() -> list[Path]:
    return [
        ROOT / "paper" / "sections" / "reggov-body.tex",
        ROOT / "paper" / "references.bib",
        ROOT / "scripts" / "audit-literature-positioning.py",
    ]


def reference_integrity_audit_inputs() -> list[Path]:
    return [
        ROOT / "paper" / "strategic-channel-substitution-regulatory-capture.tex",
        ROOT / "paper" / "regulation-governance-wiley.tex",
        ROOT / "paper" / "sections" / "reggov-body.tex",
        ROOT / "paper" / "sections" / "supplement-body.tex",
        ROOT / "paper" / "references.bib",
        ROOT / "scripts" / "audit-reference-integrity.py",
    ]


def reviewer_risk_register_inputs() -> list[Path]:
    return [
        SUBMISSION_READINESS_CSV,
        SUBMISSION_READINESS_MD,
        CALIBRATION_READINESS_CSV,
        CLAIM_SOURCE_DEPENDENCY_CSV,
        CAUSAL_CALIBRATION_TARGETS_CSV,
        SOURCE_CAPABILITY_AUDIT_CSV,
        SOURCE_PANEL_INVENTORY,
        PROCUREMENT_REFRESH_READINESS_CSV,
        FINAL_HUMAN_READTHROUGH_AUDIT_CSV,
        POLICY_CLAIM_LANGUAGE_AUDIT_CSV,
        ROOT / "reports" / "validation-summary.csv",
        ROOT / "scripts" / "write-reviewer-risk-register.py",
    ]


def wiley_submission_form_readiness_inputs() -> list[Path]:
    return [
        SUBMISSION_ZIP,
        WILEY_PDF,
        SUPPLEMENT_PDF,
        SUBMISSION_DECLARATIONS,
        ROOT / "docs" / "submission-strategy.md",
        ROOT / "docs" / "submission-release-checklist.md",
        ROOT / "scripts" / "audit-wiley-submission-form-readiness.py",
    ]


def reggov_guidelines_readiness_inputs() -> list[Path]:
    return [
        LOCAL_TEX,
        LOCAL_PDF,
        WILEY_PDF,
        SUPPLEMENT_PDF,
        SUBMISSION_ZIP,
        SUBMISSION_DECLARATIONS,
        WILEY_SUBMISSION_FORM_READINESS_CSV,
        WILEY_SUBMISSION_FORM_READINESS_MD,
        ROOT / "paper" / "regulation-governance-wiley.tex",
        ROOT / "paper" / "references.bib",
        ROOT / "scripts" / "audit-reggov-guidelines-readiness.py",
        ROOT / "scripts" / "check-paper-word-count.py",
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
    failures: list[str] = []
    if "- Miss: `0`" in validation and "benchmark misses" in body:
        failures.append(
            "manuscript still refers to benchmark misses even though validation-summary.md reports Miss: 0",
        )
    if CALIBRATION_READINESS_MD.exists():
        readiness = CALIBRATION_READINESS_MD.read_text(encoding="utf-8")
        p3_cleared = "- Validation-queue P3: `0`" in readiness and "No P3 calibration-scope rows remain" in readiness
        if "empirical-bridge-readiness" not in readiness:
            failures.append("calibration-readiness audit does not expose empirical-bridge readiness")
        if p3_cleared:
            stale_p3_phrases = [
                "Remaining P3 partial overlaps",
                "remaining P3 partial overlaps",
                "P3 partial overlaps concentrate",
            ]
            checked_texts = {
                REGGOV_BODY: body,
                SUPPLEMENT_BODY: SUPPLEMENT_BODY.read_text(encoding="utf-8") if SUPPLEMENT_BODY.exists() else "",
            }
            for path, text in checked_texts.items():
                for phrase in stale_p3_phrases:
                    if phrase in text:
                        failures.append(
                            f"{path.relative_to(ROOT)} describes unresolved P3 partials although calibration-readiness.md reports P3=0"
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


def check_validation_scope_coverage() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (VALIDATION_SCOPE_COVERAGE_MD, VALIDATION_SCOPE_COVERAGE_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing validation scope coverage artifact: {path}" for path in missing]
    if not (ROOT / "reports" / "validation-summary.csv").exists():
        return ["missing validation summary CSV needed to verify validation scope coverage"]

    with (ROOT / "reports" / "validation-summary.csv").open(newline="", encoding="utf-8") as source:
        validation_rows = list(csv.DictReader(source))
    with VALIDATION_SCOPE_COVERAGE_CSV.open(newline="", encoding="utf-8") as source:
        coverage_reader = csv.DictReader(source)
        coverage_rows = list(coverage_reader)
        coverage_fields = set(coverage_reader.fieldnames or [])

    required_fields = {
        "report",
        "benchmarkKey",
        "metric",
        "validationScope",
        "status",
        "coverageReports",
        "fitCoverageCount",
        "partialCoverageCount",
        "nextAction",
    }
    missing_fields = required_fields - coverage_fields
    if missing_fields:
        failures.append(
            "validation scope coverage CSV missing fields: " + ", ".join(sorted(missing_fields))
        )
        return failures

    validation_counts = Counter(row.get("status", "") for row in validation_rows)
    coverage_counts = Counter(row.get("status", "") for row in coverage_rows)
    not_applicable = validation_counts.get("not_applicable", 0)
    if len(coverage_rows) != not_applicable:
        failures.append(
            f"validation scope coverage rows ({len(coverage_rows)}) do not match not_applicable validations ({not_applicable})"
        )
    if coverage_counts.get("coverage_gap", 0):
        failures.append(
            f"validation scope coverage has unresolved coverage gaps: {coverage_counts.get('coverage_gap', 0)}"
        )
    uncovered = [
        row for row in coverage_rows
        if row.get("status") == "covered_elsewhere" and row.get("coverageReports", "") == "none"
    ]
    if uncovered:
        failures.append("validation scope coverage labels rows covered_elsewhere without coverage reports")

    markdown = VALIDATION_SCOPE_COVERAGE_MD.read_text(encoding="utf-8")
    required_phrases = [
        f"Not-applicable validations: `{not_applicable}`",
        f"Covered elsewhere: `{coverage_counts.get('covered_elsewhere', 0)}`",
        "Coverage gaps: `0`",
        "scenario-specific benchmark",
    ]
    for phrase in required_phrases:
        if phrase not in markdown:
            failures.append(f"validation scope coverage markdown missing phrase: {phrase}")
    if CALIBRATION_READINESS_MD.exists():
        readiness = CALIBRATION_READINESS_MD.read_text(encoding="utf-8")
        for phrase in (
            f"not_applicable={not_applicable}",
            f"coverage_gaps={coverage_counts.get('coverage_gap', 0)}",
        ):
            if phrase not in readiness:
                failures.append(f"calibration-readiness audit missing validation-scope evidence: {phrase}")
    if SUPPLEMENT_BODY.exists() and "validation-scope coverage audit" not in SUPPLEMENT_BODY.read_text(encoding="utf-8"):
        failures.append("supplement does not disclose the validation-scope coverage audit")
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
        "usaspending-national-action-panel",
        "usaspending-bulk-transaction-download-panel",
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
        "quota-blocked",
    }:
        failures.append(
            "SAM Contract Awards capability status should be implemented-not-active, quota-blocked, or active-bounded"
        )
    if rows["usaspending-stratified-action-panel"].get("capabilityStatus") not in {
        "active-usable",
        "active-bounded",
    }:
        failures.append(
            "USAspending action panel capability should be active in the committed snapshot"
        )
    if rows["usaspending-national-action-panel"].get("capabilityStatus") not in {
        "active-usable",
        "active-bounded",
    }:
        failures.append(
            "USAspending national action panel capability should be active in the committed snapshot"
        )
    if rows["usaspending-bulk-transaction-download-panel"].get("capabilityStatus") not in {
        "implemented-not-active",
        "active-bounded",
        "active-representative",
    }:
        failures.append(
            "USAspending bulk transaction download capability should be implemented and auditable"
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
            "usaspending-national-action-panel",
            "Direct hidden-donor",
            "SAM_CONTRACT_AWARDS_OFFSET_STARTS",
            "SAM_CONTRACT_AWARDS_EXTRACT_MODE",
            "api_key=REPLACE_WITH_API_KEY",
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
        "usaspending-procurement-national-actions",
        "usaspending-procurement-bulk-summary",
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
    national_rows = int(float(rows["usaspending-procurement-national-actions"].get("rows", "0") or "0"))
    national_agencies = int(float(rows["usaspending-procurement-national-actions"].get("agencyCount", "0") or "0"))
    if national_rows <= 0 or national_agencies < 2:
        failures.append(
            "procurement denominator audit should show an active multi-agency national-volume USAspending concentration panel"
        )
    if rows["sam-contract-awards"].get("snapshotStatus") == "ok" and int(float(rows["sam-contract-awards"].get("rows", "0") or "0")) <= 0:
        failures.append(
            "SAM Contract Awards cannot be marked ok without committed action rows"
        )
    text = PROCUREMENT_DENOMINATOR_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Procurement Denominator Audit",
        "archived USAspending bulk summary",
        "national concentration panel",
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
            if row.get("source") == "usaspending-procurement-actions"
            and row.get("groupType") == "awardType"
            and row.get("groupValue") == "DEFINITIVE CONTRACT"
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
        "SAM.gov Contract Awards has",
        "denominator-mapped diagnostics",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"procurement modification composition audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "procurement-modification composition audit" not in supplement:
            failures.append("supplement does not disclose the procurement-modification composition audit")
    return failures


def check_procurement_benchmark_crosswalk() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (PROCUREMENT_BENCHMARK_CROSSWALK_MD, PROCUREMENT_BENCHMARK_CROSSWALK_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing procurement benchmark crosswalk artifact: {path}" for path in missing]

    with PROCUREMENT_BENCHMARK_CROSSWALK_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    all_row = next(
        (
            row for row in rows
            if row.get("dimension") == "all" and row.get("value") == "all"
        ),
        None,
    )
    if not all_row:
        failures.append("procurement benchmark crosswalk missing aggregate all/all row")
    else:
        top3 = audit_number(all_row.get("top3RecipientShare"))
        modified_action = audit_number(all_row.get("modifiedActionShare"))
        modified_award = audit_number(all_row.get("modifiedAwardShare"))
        amount_weighted = audit_number(all_row.get("amountWeightedModificationShare"))
        if not (0.10 <= top3 <= 0.13):
            failures.append("procurement benchmark crosswalk aggregate top-3 share should match the archived bulk denominator")
        if not (0.16 <= modified_action <= 0.18):
            failures.append("procurement benchmark crosswalk aggregate modified-action share should match the archived bulk denominator")
        if not (0.10 <= modified_award <= 0.12):
            failures.append("procurement benchmark crosswalk aggregate modified-award share should match the archived bulk denominator")
        if not (0.55 <= amount_weighted <= 0.65):
            failures.append("procurement benchmark crosswalk aggregate amount-weighted modification share should match the archived bulk denominator")

    dimensions = {row.get("dimension", "") for row in rows}
    for dimension in ("agency", "awardType", "agencyAwardType"):
        if dimension not in dimensions:
            failures.append(f"procurement benchmark crosswalk missing dimension: {dimension}")

    text = PROCUREMENT_BENCHMARK_CROSSWALK_MD.read_text(encoding="utf-8")
    required_text = [
        "Procurement Benchmark Crosswalk",
        "Benchmark Remapping",
        "top-contractor benchmark",
        "delta/stress-screen",
        "action-row",
        "distinct-award",
        "amount-weighted",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"procurement benchmark crosswalk markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "procurement-benchmark crosswalk" not in supplement:
            failures.append("supplement does not disclose the procurement-benchmark crosswalk")
    return failures


def audit_number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def check_procurement_refresh_readiness() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (PROCUREMENT_REFRESH_READINESS_MD, PROCUREMENT_REFRESH_READINESS_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing procurement refresh readiness artifact: {path}" for path in missing]

    with PROCUREMENT_REFRESH_READINESS_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("item", ""): row for row in csv.DictReader(source)}
    required = {
        "sam-control-variables",
        "sam-live-status",
        "representative-sam-fpds-action-history",
        "bounded-usaspending-fallback",
        "usaspending-bulk-transaction-strata",
        "p1-procurement-calibration-actions",
        "extract-mode-path",
        "offset-strata-path",
        "partial-payload-policy",
        "claim-boundary",
    }
    missing_items = sorted(required - set(rows))
    failures.extend(
        f"procurement refresh readiness missing checklist item: {item}"
        for item in missing_items
    )
    if missing_items:
        return failures

    if rows["sam-control-variables"].get("status") != "ready":
        failures.append("procurement refresh readiness must show SAM controls documented in .env.example")
    if rows["bounded-usaspending-fallback"].get("status") != "ready":
        failures.append("procurement refresh readiness must preserve the USAspending fallback route")
    if rows["partial-payload-policy"].get("status") != "ready":
        failures.append("procurement refresh readiness must document the partial-payload guardrail")
    if "SAM_CONTRACT_AWARDS_EXTRACT_MODE=1" not in rows["extract-mode-path"].get("evidence", ""):
        failures.append("procurement refresh readiness must document the SAM extract-mode path")
    if "SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID=Yes" not in rows["extract-mode-path"].get("evidence", ""):
        failures.append("procurement refresh readiness must document SAM extract emailId=Yes")
    if "SAM_CONTRACT_AWARDS_OFFSET_STARTS" not in rows["offset-strata-path"].get("evidence", ""):
        failures.append("procurement refresh readiness must document the offset-strata path")
    if rows["claim-boundary"].get("status") != "bounded":
        failures.append("procurement refresh readiness must keep the procurement claim boundary bounded")
    if "calibrated policy-simulation claims remain outside scope" not in rows["claim-boundary"].get("evidence", ""):
        failures.append("procurement refresh readiness must keep calibrated policy-simulation claims outside scope")

    text = PROCUREMENT_REFRESH_READINESS_MD.read_text(encoding="utf-8")
    required_text = [
        "Procurement Refresh Readiness",
        "archived USAspending bulk diagnostics",
        "Do not promote partial SAM payloads",
        "calibrated policy-simulation claims remain outside scope",
        "SAM_CONTRACT_AWARDS_EXTRACT_MODE=1",
        "SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID=Yes",
        "SAM_CONTRACT_AWARDS_OFFSET_STARTS",
        "api_key=REPLACE_WITH_API_KEY",
        "sam-contract-awards-record-fresh-link",
        "--assume-fresh",
        "timeSource=recorded_at_fallback",
        "request a fresh export email",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"procurement refresh readiness markdown missing phrase: {phrase}")
    return failures


def check_first_wave_procurement_source_acquisition() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (
            FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_MD,
            FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_CSV,
        )
        if not path.exists()
    ]
    if missing:
        return [f"missing first-wave procurement source acquisition artifact: {path}" for path in missing]

    with FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("productKey", ""): row for row in csv.DictReader(source)}
    required = {
        "sam-fpds-action-history-crosswalk",
        "gao-protest-overlay",
        "sam-exclusion-overlay",
        "procurement-firewall-overlay",
        "procurement-offer-competition-enrichment",
    }
    missing_products = sorted(required - set(rows))
    failures.extend(
        f"first-wave procurement source acquisition missing product: {product}"
        for product in missing_products
    )
    if missing_products:
        return failures

    product_expectations = {
        "sam-fpds-action-history-crosswalk": [
            "Contract Awards",
            "PIID",
            "UEI",
            "make sam-procurement-refresh",
            "does not by itself estimate capture effects",
        ],
        "gao-protest-overlay": [
            "GAO",
            "B-number",
            "PIID",
            "manual",
            "does not identify lobbying exposure",
        ],
        "sam-exclusion-overlay": [
            "Exclusions API",
            "UEI",
            "exclusion type",
            "integrity-enforcement status",
        ],
        "procurement-firewall-overlay": [
            "procurement-integrity",
            "effective date",
            "covered officials",
            "document-review",
        ],
        "procurement-offer-competition-enrichment": [
            "number of offers",
            "competition",
            "not an independent capture outcome",
        ],
    }
    for product, phrases in product_expectations.items():
        row_text = " ".join(rows[product].values())
        for phrase in phrases:
            if phrase not in row_text:
                failures.append(
                    f"first-wave procurement source acquisition {product} missing phrase: {phrase}"
                )
    text = FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_MD.read_text(encoding="utf-8")
    required_text = [
        "First-Wave Procurement Source Acquisition",
        "acquisition_plan_only",
        "A row in this report is only an acquisition instruction",
        "GAO Legal Products XML feed",
        "SAM.gov Exclusions API",
        "SAM_Exclusions_Public_Extract",
        "SAM.gov Contract Awards remains the preferred source",
        "Procurement firewall coverage is a document-review product",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"first-wave procurement source acquisition markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "first-wave procurement source-acquisition report" not in supplement:
            failures.append("supplement does not disclose the first-wave procurement source-acquisition report")
    return failures


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
        expected_support = expected_claim_support_level(panel)
        actual_support = claim.get("supportLevel", "")
        if actual_support == "stronger":
            failures.append(f"claim-boundary audit overstates support level as stronger: {panel_name}")
        if actual_support != expected_support:
            failures.append(
                f"claim-boundary audit support-level mismatch for {panel_name}: "
                f"{actual_support} != {expected_support}"
            )
        if status in weak_statuses:
            if panel_name not in audit_md:
                failures.append(f"claim-boundary audit markdown omits weak panel: {panel_name}")
    if "Bounded-Evidence Gate" not in audit_md:
        failures.append("claim-boundary audit markdown omits bounded-evidence gate")
    if VALIDATION_GAP_TABLE.exists():
        table_text = VALIDATION_GAP_TABLE.read_text(encoding="utf-8")
        required_table_phrases = [
            "Claim support",
            "direct/proxy bounded",
            "proxy bounded",
            "denom. bounded",
            "conditional direct",
        ]
        for phrase in required_table_phrases:
            if phrase not in table_text:
                failures.append(f"source-panel table missing claim-support phrase: {phrase}")
        stale_table_phrases = [
            "0 direct rows",
            "high mod share",
            "Scaffold & Status",
        ]
        for phrase in stale_table_phrases:
            if phrase in table_text:
                failures.append(f"source-panel table contains stale source-support wording: {phrase}")

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


def expected_claim_support_level(panel: dict[str, str]) -> str:
    status = panel.get("status", "missing")
    if status in {"missing", "fixture-only"}:
        return "schema-only"
    if status == "warning":
        return "warning"
    if status == "thin":
        return "thin"
    if status != "usable":
        return "limited"

    evidence = panel.get("evidenceClass", "").lower()
    if "proxy/thin" in evidence:
        return "proxy-thin"
    if "direct/proxy" in evidence:
        return "direct-proxy-bounded"
    if "denominator-mapped" in evidence:
        return "denominator-bounded"
    if "proxy" in evidence:
        return "proxy-bounded"
    if "program" in evidence:
        return "program-bounded"
    if "when present" in evidence:
        return "conditional-direct"
    if "direct" in evidence:
        return "direct-bounded"
    return "source-bounded"


def check_claim_source_dependency_audit() -> list[str]:
    failures: list[str] = []
    if not SOURCE_PANEL_INVENTORY.exists():
        return failures
    missing = [
        path.relative_to(ROOT)
        for path in (CLAIM_SOURCE_DEPENDENCY_MD, CLAIM_SOURCE_DEPENDENCY_CSV, CLAIM_LADDER_TABLE)
        if not path.exists()
    ]
    if missing:
        return [f"missing claim-source dependency audit artifact: {path}" for path in missing]

    with SOURCE_PANEL_INVENTORY.open(newline="", encoding="utf-8") as source:
        panels = list(csv.DictReader(source))
    with CLAIM_SOURCE_DEPENDENCY_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("claimKey", ""): row for row in csv.DictReader(source)}
    causal_blocking_targets: set[str] = set()
    if CAUSAL_CALIBRATION_TARGETS_CSV.exists():
        with CAUSAL_CALIBRATION_TARGETS_CSV.open(newline="", encoding="utf-8") as source:
            causal_blocking_targets = {
                row.get("targetKey", "")
                for row in csv.DictReader(source)
                if row.get("blocksPolicySimulation") == "yes"
            }

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
    if causal_blocking_targets:
        if rows["calibrated-policy-simulation"].get("status") != "not_cleared":
            failures.append(
                "calibrated-policy source dependency must remain not_cleared while causal calibration targets block policy simulation"
            )
        target_claim_guards = {
            "hidden-donor-routing-magnitude": "hidden-channel-magnitude",
            "procurement-modification-causal-capture": "procurement-modification-capture",
        }
        for target, claim in target_claim_guards.items():
            if target in causal_blocking_targets and rows[claim].get("status") == "cleared":
                failures.append(
                    f"{claim} source dependency cannot be cleared while causal target remains blocked: {target}"
                )
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
    if revolving_panel.get("status") == "usable" and rows["revolving-door-cooling-off"].get("status") != "bounded":
        failures.append("revolving-door source dependency should remain bounded because the usable panel is LDA proxy/thin evidence")
    public_panel = next((panel for panel in panels if panel.get("panel") == "Public financing"), {})
    if public_panel.get("status") == "usable" and rows["public-financing-counterweight"].get("status") != "bounded":
        failures.append("public-financing source dependency should remain bounded because the usable panel is local program evidence")
    if rows["strategic-substitution-mechanism"].get("status") != "bounded":
        failures.append("strategic substitution source dependency should remain bounded while it depends on direct/proxy and proxy-thin panels")

    dependency_md = CLAIM_SOURCE_DEPENDENCY_MD.read_text(encoding="utf-8")
    required_text = [
        "Claim-Source Dependency Audit",
        "Calibrated policy simulation",
        "bounded",
        "not_cleared",
        "causal-calibration targets block policy simulation",
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
    if CLAIM_LADDER_TABLE.exists():
        claim_ladder = CLAIM_LADDER_TABLE.read_text(encoding="utf-8")
        required_ladder_text = [
            "Claim ladder",
            "Internal mechanism diagnostics",
            "Observable source moments",
            "Hidden and substitution mechanisms",
            "Calibrated policy-effect claims",
            "not cleared",
        ]
        for phrase in required_ladder_text:
            if phrase not in claim_ladder:
                failures.append(f"claim ladder table missing phrase: {phrase}")
    if REGGOV_BODY.exists():
        reggov_body = REGGOV_BODY.read_text(encoding="utf-8")
        required_main_claim_ladder = [
            "tables/claim_ladder.tex",
            "tab:claim-ladder",
            "manuscript-level decision rule",
        ]
        for phrase in required_main_claim_ladder:
            if phrase not in reggov_body:
                failures.append(f"main paper does not disclose claim ladder artifact: {phrase}")
    return failures


def check_causal_calibration_targets() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (CAUSAL_CALIBRATION_TARGETS_MD, CAUSAL_CALIBRATION_TARGETS_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing causal calibration target artifact: {path}" for path in missing]

    with CAUSAL_CALIBRATION_TARGETS_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) < 10:
        failures.append("causal calibration target audit should enumerate the main hidden-channel and reform-effect target classes")
    required_targets = {
        "hidden-donor-routing-magnitude",
        "substitution-elasticity",
        "procurement-modification-causal-capture",
        "revolving-door-access-effect",
        "public-financing-countervailing-effect",
        "comment-authenticity-and-uptake-effect",
        "enforcement-deterrence-effect",
        "meeting-disclosure-and-access-effect",
        "intermediary-network-effect",
        "venue-shifting-detection-effect",
    }
    present = {row.get("targetKey", "") for row in rows}
    failures.extend(
        f"causal calibration target audit missing target: {target}"
        for target in sorted(required_targets - present)
    )
    blockers = [
        row for row in rows
        if row.get("blocksPolicySimulation") == "yes"
    ]
    if not blockers:
        failures.append("causal calibration target audit should block calibrated policy-simulation claims until causal targets clear")
    if any(row.get("policyClaimStatus") == "cleared" for row in rows) and blockers:
        failures.append("causal calibration target audit cannot report cleared policy status while blocking targets remain")
    if not any(row.get("priority") == "P1" for row in rows):
        failures.append("causal calibration target audit should distinguish P1 targets")
    if not any(row.get("priority") == "P2" for row in rows):
        failures.append("causal calibration target audit should distinguish P2 targets")

    text = CAUSAL_CALIBRATION_TARGETS_MD.read_text(encoding="utf-8")
    required_text = [
        "Causal Calibration Targets",
        "independent causal evidence",
        "Blocking calibrated policy-simulation claims",
        "Target Matrix",
        "hidden-donor-routing-magnitude",
        "procurement-modification-causal-capture",
        "substitution-elasticity",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"causal calibration target markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "causal-calibration target audit" not in supplement:
            failures.append("supplement does not disclose the causal-calibration target audit")
    return failures


def check_first_wave_causal_protocols() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (
            FIRST_WAVE_CAUSAL_PROTOCOLS_MD,
            FIRST_WAVE_CAUSAL_PROTOCOLS_CSV,
            FIRST_WAVE_CAUSAL_PROTOCOLS_TABLE,
        )
        if not path.exists()
    ]
    if missing:
        return [f"missing first-wave causal protocol artifact: {path}" for path in missing]

    with FIRST_WAVE_CAUSAL_PROTOCOLS_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    expected = {
        "substitution-elasticity",
        "procurement-modification-causal-capture",
        "comment-authenticity-and-uptake-effect",
        "venue-shifting-detection-effect",
    }
    present = {row.get("targetKey", "") for row in rows}
    failures.extend(
        f"first-wave causal protocol report missing target: {target}"
        for target in sorted(expected - present)
    )
    if present - expected:
        failures.extend(
            f"first-wave causal protocol report includes non-first-wave target: {target}"
            for target in sorted(present - expected)
        )
    required_fields = [
        "unitOfAnalysis",
        "treatmentOrShock",
        "comparisonDesign",
        "primaryOutcomes",
        "linkageKeys",
        "minimumSources",
        "falsificationChecks",
        "sensitivityChecks",
        "threatModel",
        "claimUpgradeBoundary",
    ]
    for row in rows:
        for field_name in required_fields:
            if not row.get(field_name):
                failures.append(
                    f"first-wave causal protocol {row.get('targetKey', '<missing>')} missing {field_name}"
                )
        if row.get("protocolStatus") != "protocol_ready_source_pending":
            failures.append(
                f"first-wave causal protocol {row.get('targetKey', '<missing>')} should remain source-pending"
            )

    text = FIRST_WAVE_CAUSAL_PROTOCOLS_MD.read_text(encoding="utf-8")
    required_text = [
        "First-Wave Causal Protocols",
        "does not clear calibrated policy-simulation claims",
        "Policy-simulation status: `not_cleared`",
        "Falsification checks",
        "Claim-upgrade boundary",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"first-wave causal protocol markdown missing phrase: {phrase}")

    table = FIRST_WAVE_CAUSAL_PROTOCOLS_TABLE.read_text(encoding="utf-8")
    for phrase in (
        "First-wave causal calibration protocols",
        "tab:first-wave-causal-protocols",
        "Substitution elasticity",
        "Procurement modification",
    ):
        if phrase not in table:
            failures.append(f"first-wave causal protocol table missing phrase: {phrase}")

    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        for phrase in (
            "first-wave causal protocol report",
            "first_wave_causal_protocols.tex",
        ):
            if phrase not in supplement:
                failures.append(f"supplement does not disclose first-wave protocol artifact: {phrase}")
    return failures


def expected_first_wave_template_files() -> dict[str, str]:
    return {
        "substitution-reform-shocks": "substitution-reform-shocks.csv",
        "actor-issue-time-spine": "actor-issue-time-spine.csv",
        "substitution-comparison-groups": "substitution-comparison-groups.csv",
        "meeting-log-or-missing-channel-note": "meeting-log-channel-note.md",
        "sam-fpds-action-history-crosswalk": "sam-fpds-action-history-crosswalk.csv",
        "gao-protest-overlay": "gao-protest-overlay.csv",
        "sam-exclusion-overlay": "sam-exclusion-overlay.csv",
        "procurement-firewall-overlay": "procurement-firewall-overlay.csv",
        "procurement-offer-competition-enrichment": "procurement-offer-competition-enrichment.csv",
        "comment-body-corpus": "comment-body-corpus.csv",
        "duplicate-template-clusters": "comment-template-clusters.csv",
        "agency-response-final-rule-linkage": "agency-response-final-rule-linkage.csv",
        "canonical-actor-identifiers": "canonical-actor-identifiers.csv",
        "alias-resolution-audit-sample": "alias-resolution-audit-sample.csv",
        "issue-code-crosswalk": "issue-code-crosswalk.csv",
        "false-match-review-log": "false-match-review-log.csv",
        "linked-actor-issue-venue-time": "linked-actor-issue-venue-time.csv",
    }


def check_first_wave_source_product_templates() -> list[str]:
    failures: list[str] = []
    expected = expected_first_wave_template_files()
    required_paths = [
        FIRST_WAVE_SOURCE_TEMPLATE_README,
        FIRST_WAVE_SOURCE_TEMPLATE_MANIFEST_CSV,
        FIRST_WAVE_SOURCE_TEMPLATE_MANIFEST_MD,
        *(FIRST_WAVE_SOURCE_TEMPLATE_DIR / filename for filename in expected.values()),
    ]
    failures.extend(
        f"missing first-wave source product template artifact: {path.relative_to(ROOT)}"
        for path in required_paths
        if not path.exists()
    )
    if failures:
        return failures

    actual_files = {
        path.name
        for path in FIRST_WAVE_SOURCE_TEMPLATE_DIR.iterdir()
        if path.is_file()
    }
    expected_files = {"README.md", "manifest.csv", "manifest.md", *expected.values()}
    failures.extend(
        f"first-wave source product template directory missing file: {filename}"
        for filename in sorted(expected_files - actual_files)
    )
    failures.extend(
        f"first-wave source product template directory includes unexpected file: {filename}"
        for filename in sorted(actual_files - expected_files)
    )

    with FIRST_WAVE_SOURCE_TEMPLATE_MANIFEST_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    present_products = {row.get("productKey", "") for row in rows}
    failures.extend(
        f"first-wave source product template manifest missing product: {product}"
        for product in sorted(set(expected) - present_products)
    )
    failures.extend(
        f"first-wave source product template manifest includes unexpected product: {product}"
        for product in sorted(present_products - set(expected))
    )
    if len(rows) != len(expected):
        failures.append(
            f"first-wave source product template manifest row count {len(rows)} does not match expected {len(expected)}"
        )

    for row in rows:
        product = row.get("productKey", "<missing>")
        filename = expected.get(product)
        if not filename:
            continue
        template_path = row.get("templatePath", "")
        production_path = row.get("productionPath", "")
        expected_template_path = f"docs/source-product-templates/first-wave/{filename}"
        if template_path != expected_template_path:
            failures.append(
                f"first-wave source product template {product} path {template_path} should be {expected_template_path}"
            )
        if not production_path.startswith("data/calibration/first-wave/"):
            failures.append(
                f"first-wave source product template {product} production path should live under data/calibration/first-wave/"
            )
        template_file = FIRST_WAVE_SOURCE_TEMPLATE_DIR / filename
        if filename.endswith(".csv"):
            with template_file.open(newline="", encoding="utf-8") as source:
                reader = csv.reader(source)
                header = next(reader, [])
                extra_rows = list(reader)
            required = [
                value.strip()
                for value in row.get("requiredColumnsOrTerms", "").split(";")
                if value.strip()
            ]
            missing_header = [column for column in required if column not in header]
            if missing_header:
                failures.append(
                    f"first-wave source product template {product} missing CSV columns: {', '.join(missing_header)}"
                )
            if extra_rows:
                failures.append(
                    f"first-wave source product template {product} should be header-only, not source evidence"
                )
        else:
            text = template_file.read_text(encoding="utf-8").lower()
            for phrase in ("meeting", "missing", "substitution", "production path"):
                if phrase not in text:
                    failures.append(
                        f"first-wave source product text template {product} missing phrase: {phrase}"
                    )

    readme = FIRST_WAVE_SOURCE_TEMPLATE_README.read_text(encoding="utf-8")
    manifest_md = FIRST_WAVE_SOURCE_TEMPLATE_MANIFEST_MD.read_text(encoding="utf-8")
    for phrase in (
        "Production source-product directory: `data/calibration/first-wave/`",
        "Do not treat these templates as evidence.",
        "product-level semantic gates",
    ):
        if phrase not in readme:
            failures.append(f"first-wave source product template README missing phrase: {phrase}")
    if "cannot satisfy the production source-product audit" not in manifest_md:
        failures.append("first-wave source product template manifest missing production-audit boundary")
    if "Semantic checks" not in manifest_md:
        failures.append("first-wave source product template manifest missing semantic checks")
    return failures


def check_first_wave_source_products() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (
            FIRST_WAVE_SOURCE_PRODUCTS_MD,
            FIRST_WAVE_SOURCE_PRODUCTS_CSV,
        )
        if not path.exists()
    ]
    if missing:
        return [f"missing first-wave source product artifact: {path}" for path in missing]

    with FIRST_WAVE_SOURCE_PRODUCTS_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    expected_targets = {
        "substitution-elasticity",
        "procurement-modification-causal-capture",
        "comment-authenticity-and-uptake-effect",
        "venue-shifting-detection-effect",
    }
    present_targets = {row.get("targetKey", "") for row in rows}
    failures.extend(
        f"first-wave source product report missing target: {target}"
        for target in sorted(expected_targets - present_targets)
    )
    expected_products = set(expected_first_wave_template_files())
    present_products = {row.get("productKey", "") for row in rows}
    failures.extend(
        f"first-wave source product report missing product: {product}"
        for product in sorted(expected_products - present_products)
    )
    if present_products - expected_products:
        failures.extend(
            f"first-wave source product report includes unexpected product: {product}"
            for product in sorted(present_products - expected_products)
        )
    if len(rows) != len(expected_products):
        failures.append(
            f"first-wave source product report row count {len(rows)} does not match expected {len(expected_products)}"
        )
    required_fields = [
        "productLabel",
        "requirementLevel",
        "expectedPath",
        "templatePath",
        "acceptableSources",
        "requiredColumns",
        "minimumRows",
        "productStatus",
        "qualityIssueCount",
        "semanticIssueCount",
        "semanticChecks",
        "validationRule",
        "claimBoundary",
        "nextAction",
        "manualReviewChecklist",
    ]
    ready_rows = []
    candidate_rows = []
    for row in rows:
        product = row.get("productKey", "<missing>")
        for field_name in required_fields:
            if not row.get(field_name):
                failures.append(f"first-wave source product {product} missing {field_name}")
        if row.get("requirementLevel") != "required":
            failures.append(f"first-wave source product {product} should be required in this release")
        if row.get("productStatus") in {"schema_ready", "text_ready"}:
            ready_rows.append(product)
        if row.get("productStatus") == "candidate_unreviewed":
            candidate_rows.append(product)
            checklist = row.get("manualReviewChecklist", "")
            checklist_lower = checklist.lower()
            if (
                "remove candidateonly markers only after" not in checklist_lower
                and "promote only after" not in checklist_lower
            ):
                failures.append(
                    f"first-wave candidate source product {product} missing promotion-gate checklist language"
                )
        quality_issue_count = row.get("qualityIssueCount", "0")
        if quality_issue_count not in {"", "0"} and not row.get("qualityIssueExamples", "").strip():
            failures.append(
                f"first-wave source product {product} has quality issues but no example field-level issue"
            )
        if not row.get("expectedPath", "").startswith("data/calibration/first-wave/"):
            failures.append(
                f"first-wave source product {product} expected path should live under data/calibration/first-wave/"
            )
        expected_template = expected_first_wave_template_files().get(product)
        if expected_template:
            template_path = row.get("templatePath", "")
            expected_template_path = f"docs/source-product-templates/first-wave/{expected_template}"
            if template_path != expected_template_path:
                failures.append(
                    f"first-wave source product {product} template path {template_path} should be {expected_template_path}"
                )
            if not (ROOT / template_path).exists():
                failures.append(f"first-wave source product {product} template path does not exist: {template_path}")
    allowed_ready_rows = {
        "comment-body-corpus",
        "duplicate-template-clusters",
        "meeting-log-or-missing-channel-note",
        "substitution-reform-shocks",
    }
    expected_candidate_rows = set(FIRST_WAVE_CANDIDATE_SEED_PRODUCTS)
    unexpected_ready_rows = sorted(set(ready_rows) - allowed_ready_rows)
    if unexpected_ready_rows:
        failures.append(
            "first-wave source products should not be ready in this release without a matching manuscript update: "
            + ", ".join(unexpected_ready_rows)
        )
    if set(candidate_rows) != expected_candidate_rows:
        failures.append(
            "first-wave source products should mark exactly the candidate source-product seeds candidate_unreviewed: "
            + ", ".join(sorted(candidate_rows))
        )
    for product, path in FIRST_WAVE_CANDIDATE_SEED_PRODUCTS.items():
        if not path.exists():
            failures.append(f"missing first-wave candidate source-product seed: {path.relative_to(ROOT)}")
            continue
        with path.open(newline="", encoding="utf-8") as source:
            seed_rows = list(csv.DictReader(source))
        if not seed_rows:
            failures.append(f"first-wave candidate source-product seed is empty: {path.relative_to(ROOT)}")
            continue
        if "candidateOnly" not in seed_rows[0]:
            failures.append(f"first-wave candidate source-product seed missing candidateOnly field: {product}")
        if any(row.get("candidateOnly") != "true" for row in seed_rows):
            failures.append(f"first-wave candidate source-product seed must keep candidateOnly=true: {product}")
        combined = "\n".join(" ".join(row.values()) for row in seed_rows[:25])
        if "candidate_unreviewed" not in combined or "does not clear" not in combined:
            failures.append(f"first-wave candidate source-product seed missing boundary markers: {product}")
    if ready_rows:
        if set(ready_rows) != allowed_ready_rows:
            failures.append(
                "first-wave source products may only mark the bounded HLOGA reform-shock row, meeting/contact missing-channel design note, comment-body corpus, and duplicate/template cluster product ready in this release: "
                + ", ".join(sorted(ready_rows))
            )
        product_text = FIRST_WAVE_SOURCE_PRODUCTS_MD.read_text(encoding="utf-8")
        for phrase in (
            "Schema/text ready products: `4`",
            "Candidate-only unreviewed products: `13`",
            "named reform-shock event file",
            "Use the committed reform-shock row",
            "do not treat this event row as substitution evidence",
            "SAM/FPDS action-history export or keyed pull",
            "Candidate-only procurement source-surface worklist",
            "reviewed SAM.gov Contract Awards or FPDS action-history",
            "GAO protest overlay",
            "SAM exclusion overlay",
            "procurement firewall or integrity-control overlay",
            "offer-count and competition-code enrichment",
            "canonical actor-issue-time spine across at least three venues",
            "pre/post comparison groups for exposed and unaffected actors or jurisdictions",
            "meeting-log or contact-register panel, or explicit missing-channel design note",
            "Text source product contains the required missing-channel design terms",
            "comment-body corpus",
            "Use this public comment corpus",
            "do not treat body text alone as agency uptake evidence",
            "duplicate/template cluster assignments",
            "Use these reproducible pre-review clusters",
            "link clusters to response sections and final-rule text before estimating uptake",
            "agency response text and final-rule linkage",
            "Candidate-only manual-review seed is present",
            "response sections, final-rule text movement, and uptake coding are manually adjudicated",
            "Manual Promotion Checklists",
            "remove candidateOnly markers only after",
        ):
            if phrase not in product_text:
                failures.append(f"first-wave source products markdown missing ready-note boundary phrase: {phrase}")

    text = FIRST_WAVE_SOURCE_PRODUCTS_MD.read_text(encoding="utf-8")
    required_text = [
        "First-Wave Source Products",
        "schema/acquisition gate",
        "Policy-simulation status: `not_cleared`",
        "Products with field-level quality issues",
        "Products with semantic gate issues",
        "Field Quality Notes",
        "Field-level examples are deterministic samples",
        "Counts remain the gate",
        "candidate_unreviewed",
        "deterministic manual-review seed",
        "manual-review worklists until these checks are completed",
        "procurement source-surface worklists require reviewed action-history, protest, exclusion, firewall, and offer/competition rows",
        "Template path",
        "Semantic Gate Notes",
        "Manual Promotion Checklists",
        "SAM/FPDS action-history export or keyed pull",
        "canonical actor identifier table",
        "comment-body corpus",
        "duplicate/template cluster assignments",
        "agency response text and final-rule linkage",
        "Candidate-only procurement source-surface worklist",
        "does not clear source-product readiness until action-history, protest, exclusion, firewall, and offer/competition rows",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"first-wave source products markdown missing phrase: {phrase}")
    if "`issueCode`: invalid boolean" in text:
        failures.append("first-wave source products markdown should not classify issueCode as a boolean field")

    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        for phrase in (
            "first-wave source-product audit",
            "reports/first-wave-source-products.md",
            "Honest Leadership and Open Government Act of 2007",
            "not an actor-time panel or substitution estimate",
            "comment-body corpus",
            "duplicate/template clusters",
            "candidate-only response/final-rule linkage",
            "first-wave source-product audit",
            "manual promotion",
        ):
            if phrase not in supplement:
                failures.append(f"supplement does not disclose first-wave source product artifact: {phrase}")
    return failures


def check_first_wave_linkage_candidates() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (
            FIRST_WAVE_LINKAGE_CANDIDATES_MD,
            FIRST_WAVE_LINKAGE_CANDIDATES_CSV,
            FIRST_WAVE_LINKAGE_CANDIDATE_RECORDS_CSV,
        )
        if not path.exists()
    ]
    if missing:
        return [f"missing first-wave linkage candidate artifact: {path}" for path in missing]

    with FIRST_WAVE_LINKAGE_CANDIDATES_CSV.open(newline="", encoding="utf-8") as source:
        summary_rows = list(csv.DictReader(source))
    with FIRST_WAVE_LINKAGE_CANDIDATE_RECORDS_CSV.open(newline="", encoding="utf-8") as source:
        record_rows = list(csv.DictReader(source))

    if not summary_rows:
        failures.append("first-wave linkage candidates summary is empty")
    if not record_rows:
        failures.append("first-wave linkage candidate records are empty")

    required_summary_fields = {
        "candidateActorId",
        "normalizedName",
        "displayName",
        "sourceSystemCount",
        "sourceSystems",
        "venueCount",
        "venues",
        "candidateType",
        "sourceRecordCount",
        "candidateUse",
        "reviewAction",
        "claimBoundary",
    }
    required_record_fields = {
        "candidateActorId",
        "normalizedName",
        "displayName",
        "sourceSystem",
        "venue",
        "sourceFile",
        "sourceRecordId",
        "matchRule",
        "candidateOnly",
        "claimBoundary",
    }
    if summary_rows:
        missing_fields = sorted(required_summary_fields - set(summary_rows[0]))
        failures.extend(f"first-wave linkage candidates missing summary field: {field}" for field in missing_fields)
    if record_rows:
        missing_fields = sorted(required_record_fields - set(record_rows[0]))
        failures.extend(f"first-wave linkage candidates missing record field: {field}" for field in missing_fields)

    cross_venue_rows = [
        row for row in summary_rows
        if row.get("candidateType") == "cross_venue" and int_or_zero(row.get("venueCount")) >= 2
    ]
    if not cross_venue_rows:
        failures.append("first-wave linkage candidates should include cross-venue candidate rows")
    if any(row.get("candidateOnly") != "true" for row in record_rows):
        failures.append("first-wave linkage candidate records must remain candidateOnly=true")
    if any("not evidence" not in row.get("claimBoundary", "") for row in summary_rows[:25]):
        failures.append("first-wave linkage candidates summary rows must preserve candidate-only claim boundaries")

    text = FIRST_WAVE_LINKAGE_CANDIDATES_MD.read_text(encoding="utf-8")
    required_text = [
        "First-Wave Linkage Candidates",
        "candidate-generation artifact only",
        "Candidate status: `candidate_only_not_source_product`",
        "Cross-venue candidate actors",
        "Production promotion path",
        "Automated normalized-name overlap is not evidence",
        "linked actor-issue-venue-time",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"first-wave linkage candidates markdown missing phrase: {phrase}")

    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        for phrase in (
            "first-wave linkage-candidate report",
            "reports/first-wave-linkage-candidates.md",
        ):
            if phrase not in supplement:
                failures.append(f"supplement does not disclose first-wave linkage candidate artifact: {phrase}")
    return failures


def check_first_wave_source_readiness() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (
            FIRST_WAVE_SOURCE_READINESS_MD,
            FIRST_WAVE_SOURCE_READINESS_CSV,
        )
        if not path.exists()
    ]
    if missing:
        return [f"missing first-wave source readiness artifact: {path}" for path in missing]

    with FIRST_WAVE_SOURCE_READINESS_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    expected = {
        "substitution-elasticity",
        "procurement-modification-causal-capture",
        "comment-authenticity-and-uptake-effect",
        "venue-shifting-detection-effect",
    }
    present = {row.get("targetKey", "") for row in rows}
    failures.extend(
        f"first-wave source readiness report missing target: {target}"
        for target in sorted(expected - present)
    )
    if present - expected:
        failures.extend(
            f"first-wave source readiness report includes non-first-wave target: {target}"
            for target in sorted(present - expected)
        )
    required_fields = [
        "sourceReadiness",
        "sourceProductGate",
        "sourceProductEvidence",
        "currentSourceProducts",
        "boundedOrProxySupport",
        "missingSourceProducts",
        "candidateOnlySourceProducts",
        "schemaIssueSourceProducts",
        "blockingSourceProducts",
        "blockingIssue",
        "claimBoundary",
        "nextAction",
    ]
    ready_rows = []
    blocked_rows = []
    for row in rows:
        target = row.get("targetKey", "<missing>")
        for field_name in required_fields:
            if not row.get(field_name):
                failures.append(f"first-wave source readiness {target} missing {field_name}")
        readiness = row.get("sourceReadiness", "")
        if readiness == "ready_to_estimate":
            ready_rows.append(target)
        if readiness.startswith("blocked"):
            blocked_rows.append(target)
    by_target = {row.get("targetKey", ""): row for row in rows}
    comment_row = by_target.get("comment-authenticity-and-uptake-effect", {})
    if comment_row.get("missingSourceProducts") != "none":
        failures.append("first-wave source readiness should not call the committed comment linkage seed missing")
    if "agency response text and final-rule linkage" not in comment_row.get("candidateOnlySourceProducts", ""):
        failures.append("first-wave source readiness should list agency response/final-rule linkage as candidate-only")
    substitution_row = by_target.get("substitution-elasticity", {})
    if substitution_row.get("missingSourceProducts") != "none":
        failures.append("first-wave source readiness should not call committed substitution seed files missing")
    venue_row = by_target.get("venue-shifting-detection-effect", {})
    if venue_row.get("missingSourceProducts") != "none":
        failures.append("first-wave source readiness should not call committed venue seed files missing")
    if ready_rows:
        failures.append(
            "first-wave source readiness should not clear estimation-ready rows in this release: "
            + ", ".join(sorted(ready_rows))
        )
    if "procurement-modification-causal-capture" not in blocked_rows:
        failures.append("first-wave source readiness should keep procurement modification blocked")

    text = FIRST_WAVE_SOURCE_READINESS_MD.read_text(encoding="utf-8")
    required_text = [
        "First-Wave Source Readiness",
        "pre-estimation gate",
        "Ready to estimate: `0`",
        "Policy-simulation status: `not_cleared`",
        "Source-product schema gate",
        "Blocked source-product targets",
        "Candidate-only source products",
        "Schema/quality issue products",
        "ready=2",
        "candidateOnly=1",
        "candidateOnly=2",
        "candidateOnly=5",
        "| comment-authenticity-and-uptake-effect | partial_source_support_not_estimation_ready | candidate_only_blocked",
        "| venue-shifting-detection-effect | partial_identifier_support_not_linkage_ready | candidate_only_blocked",
        "| procurement-modification-causal-capture | blocked_by_sam_fps_crosswalk_and_overlays | candidate_only_blocked",
        "none | agency response text and final-rule linkage | none",
        "candidate procurement source-surface worklists",
        "SAM/FPDS action-history export or keyed pull; GAO protest overlay; SAM exclusion overlay; procurement firewall or integrity-control overlay; offer-count and competition-code enrichment",
        "Replace the candidate procurement source-surface worklists with reviewed SAM/FPDS action-history rows",
        "Manually adjudicate the candidate actor-issue-time spine and comparison groups",
        "first-wave ready products=comment-body corpus; duplicate/template cluster assignments",
        "Candidate response/final-rule linkage file is committed",
        "Manually adjudicate the candidate response/final-rule linkage file",
        "candidate-only seed files",
        "SAM/FPDS action-history export or keyed pull",
        "canonical actor identifier table",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"first-wave source readiness markdown missing phrase: {phrase}")

    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        for phrase in (
            "first-wave source-readiness audit",
            "reports/first-wave-source-readiness.md",
        ):
            if phrase not in supplement:
                failures.append(f"supplement does not disclose first-wave source readiness artifact: {phrase}")
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
    dependency_rows: list[dict[str, str]] = []
    if CLAIM_SOURCE_DEPENDENCY_CSV.exists():
        with CLAIM_SOURCE_DEPENDENCY_CSV.open(newline="", encoding="utf-8") as source:
            dependency_rows = list(csv.DictReader(source))
    causal_blockers: list[dict[str, str]] = []
    if CAUSAL_CALIBRATION_TARGETS_CSV.exists():
        with CAUSAL_CALIBRATION_TARGETS_CSV.open(newline="", encoding="utf-8") as source:
            causal_blockers = [
                row for row in csv.DictReader(source)
                if row.get("blocksPolicySimulation") == "yes"
            ]

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
    bounded_dependencies = [
        row for row in dependency_rows
        if row.get("status") == "bounded"
    ]
    if rows["Mechanism-model article"].get("status") != "cleared":
        failures.append("mechanism-model claim posture is not cleared")
    if rows["Reproducibility and layout bundle"].get("status") != "cleared":
        failures.append("reproducibility/layout claim posture is not cleared")
    if causal_blockers and rows["Calibrated policy-simulation claim"].get("status") != "not_cleared":
        failures.append(
            "calibrated policy-simulation posture must remain not_cleared while causal calibration blockers remain"
        )
    if causal_blockers:
        policy_evidence = rows["Calibrated policy-simulation claim"].get("evidence", "")
        required_evidence = [
            "validation queue P1=",
            "causal targets P1=",
            "open causal targets=",
        ]
        for phrase in required_evidence:
            if phrase not in policy_evidence:
                failures.append(f"calibrated policy-simulation evidence missing distinction: {phrase}")
        stale_evidence_phrases = [
            "calibration/source actions remain",
            "0 P1 and 0 P2",
        ]
        for phrase in stale_evidence_phrases:
            if phrase in policy_evidence:
                failures.append(f"calibrated policy-simulation evidence uses stale queue wording: {phrase}")
    if bounded_dependencies and rows["Empirical bridge"].get("status") != "bounded":
        failures.append(
            "empirical bridge posture should remain bounded while bounded claim-source dependencies remain"
        )
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
        "Coverage-Gap Source Panels",
        "Claim-Source Dependencies",
        "Causal Calibration Targets",
        "Validation-Queue P1/P2 Actions",
        "Blocking P1 targets",
        "open causal targets",
    ]
    for phrase in required_text:
        if phrase.lower() not in posture_md_lower:
            failures.append(f"claim-posture audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "claim-posture audit" not in supplement:
            failures.append("supplement does not disclose the claim-posture audit")
    return failures


def check_policy_claim_language_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (POLICY_CLAIM_LANGUAGE_AUDIT_MD, POLICY_CLAIM_LANGUAGE_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing policy-claim language audit artifact: {path}" for path in missing]

    with POLICY_CLAIM_LANGUAGE_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        failures.append("policy-claim language audit has no rows")
        return failures

    blocking_statuses = {"overclaim", "missing_required_boundary", "missing"}
    for item in rows:
        if item.get("status") in blocking_statuses:
            failures.append(
                "policy-claim language audit has blocking row: "
                f"{item.get('file', '')}:{item.get('line', '')} "
                f"{item.get('auditKey', '')} ({item.get('status', '')})"
            )

    text = POLICY_CLAIM_LANGUAGE_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Policy-Claim Language Audit",
        "representative-scenario-language",
        "Overclaim hits: `0`",
        "Missing required boundary phrases: `0`",
        "calibrated-policy dependency=not_cleared",
        "not a representative empirical panel",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"policy-claim language audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "policy-claim language audit" not in supplement:
            failures.append("supplement does not disclose the policy-claim language audit")
    return failures


def check_literature_positioning_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (LITERATURE_POSITIONING_AUDIT_MD, LITERATURE_POSITIONING_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing literature-positioning audit artifact: {path}" for path in missing]

    with LITERATURE_POSITIONING_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("category", ""): row for row in csv.DictReader(source)}
    required_categories = {
        "lobbying-and-access",
        "capture-and-governance",
        "venue-substitution",
        "money-in-politics",
        "rulemaking-and-comments",
        "revolving-door-and-intermediaries",
        "abm-and-validation",
        "public-data-bridge",
    }
    for category in sorted(required_categories - set(rows)):
        failures.append(f"literature-positioning audit missing category: {category}")
    for category in sorted(required_categories & set(rows)):
        row = rows[category]
        if row.get("status") == "blocked":
            failures.append(f"literature-positioning audit category is blocked: {category}")
        if row.get("bodySignals") in {"", "none"}:
            failures.append(f"literature-positioning audit category lacks body signals: {category}")
        if row.get("citedRequiredKeys") in {"", "none"}:
            failures.append(f"literature-positioning audit category lacks required cited keys: {category}")
        if row.get("missingBibliographyKeys") not in {"", "none"}:
            failures.append(f"literature-positioning audit category has missing bibliography keys: {category}")

    text = LITERATURE_POSITIONING_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Literature Positioning Audit",
        "regulatory-governance mechanism-model paper",
        "lobbying-and-access",
        "capture-and-governance",
        "venue-substitution",
        "money-in-politics",
        "rulemaking-and-comments",
        "revolving-door-and-intermediaries",
        "abm-and-validation",
        "public-data-bridge",
        "Ready categories",
        "human reader still needs to judge",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"literature-positioning audit markdown missing phrase: {phrase}")
    return failures


def check_reference_integrity_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (REFERENCE_INTEGRITY_AUDIT_MD, REFERENCE_INTEGRITY_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing reference-integrity audit artifact: {path}" for path in missing]

    with REFERENCE_INTEGRITY_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        failures.append("reference-integrity audit has no rows")
        return failures
    blocked = [row for row in rows if row.get("status") == "blocked"]
    for row in blocked:
        failures.append(
            "reference-integrity audit has blocking row: "
            f"{row.get('auditKey', '')}/{row.get('subject', '')}: {row.get('detail', '')}"
        )
    required_audits = {
        "citation-key-summary",
        "entry-persistent-id",
        "entry-required-fields",
        "placeholder-summary",
        "source-metadata",
    }
    seen_audits = {row.get("auditKey", "") for row in rows}
    for audit_key in sorted(required_audits - seen_audits):
        failures.append(f"reference-integrity audit missing audit group: {audit_key}")
    text = REFERENCE_INTEGRITY_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Reference Integrity Audit",
        "citation-key consistency",
        "Ready rows",
        "Advisory rows",
        "Blocked rows: `0`",
        "all-citations",
        "source-metadata",
        "placeholderHits=0",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"reference-integrity audit markdown missing phrase: {phrase}")
    return failures


def check_submission_readiness_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (SUBMISSION_READINESS_MD, SUBMISSION_READINESS_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing submission-readiness audit artifact: {path}" for path in missing]

    with SUBMISSION_READINESS_CSV.open(newline="", encoding="utf-8") as source:
        rows = {row.get("gate", ""): row for row in csv.DictReader(source)}
    required = {
        "mechanism-manuscript": {"ready"},
        "empirical-bridge-scope": {"bounded"},
        "calibrated-policy-claims": {"blocked"},
        "claim-source-dependencies": {"bounded"},
        "policy-language-audit": {"ready"},
        "layout-and-visual-audit": {"ready"},
        "reproducible-review-bundle": {"ready"},
        "final-journal-submission": {"manual_required", "ready"},
        "overall-submission-posture": {"ready_for_mechanism_review"},
    }
    for gate_name, expected_statuses in required.items():
        if gate_name not in rows:
            failures.append(f"submission-readiness audit missing gate: {gate_name}")
            continue
        if rows[gate_name].get("status") not in expected_statuses:
            failures.append(
                "submission-readiness audit gate has unexpected status: "
                f"{gate_name}={rows[gate_name].get('status', '')}, expected one of {sorted(expected_statuses)}"
            )

    text = SUBMISSION_READINESS_MD.read_text(encoding="utf-8")
    required_text = [
        "ready_for_mechanism_review",
        "bounded empirical bridge",
        "not a calibrated policy-effect submission",
        "calibrated policy-effect claims",
        "final human read-through",
        "final-journal-submission",
        "DOI archive",
        "human scholarly read-through",
        "live author-page refresh",
        "latex unresolved=0",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"submission-readiness audit markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "submission-readiness audit" not in supplement:
            failures.append("supplement does not disclose the submission-readiness audit")
    return failures


def check_reviewer_risk_register() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (REVIEWER_RISK_REGISTER_CSV, REVIEWER_RISK_REGISTER_MD)
        if not path.exists()
    ]
    if missing:
        return [f"missing reviewer risk register artifact: {path}" for path in missing]

    with REVIEWER_RISK_REGISTER_CSV.open(newline="", encoding="utf-8") as source:
        rows = {
            row.get("riskId", ""): row
            for row in csv.DictReader(source)
            if row.get("riskId")
        }
    required_statuses = {
        "overall-reviewer-risk-posture": {"bounded_for_mechanism_review"},
        "self-confirming-substitution-result": {"mitigated"},
        "composite-diagnostic-construct-validity": {"mitigated"},
        "empirical-bridge-hidden-channel-support": {"bounded"},
        "procurement-modification-causal-validity": {"open_calibration"},
        "agent-based-institutional-depth": {"bounded"},
        "result-generalizability": {"bounded"},
        "policy-ranking-overinterpretation": {"mitigated"},
        "reproducibility-package-integrity": {"mitigated"},
        "journal-finalization": {"manual_required", "ready"},
    }
    for risk_id, expected_statuses in required_statuses.items():
        row = rows.get(risk_id)
        if not row:
            failures.append(f"reviewer risk register missing risk: {risk_id}")
            continue
        status = row.get("status", "")
        if status not in expected_statuses:
            failures.append(
                f"reviewer risk register risk {risk_id} has status={status!r}, "
                f"expected one of {sorted(expected_statuses)}"
            )
        for field in ("reviewerConcern", "evidence", "currentResponse", "claimBoundary", "nextAction"):
            if not row.get(field, "").strip():
                failures.append(f"reviewer risk register risk {risk_id} has empty {field}")

    text = REVIEWER_RISK_REGISTER_MD.read_text(encoding="utf-8")
    required_phrases = [
        "Reviewer Risk Register",
        "bounded_for_mechanism_review",
        "self-confirming-substitution-result",
        "procurement-modification-causal-validity",
        "calibrated policy-simulation claims",
        "manual_required",
        "review-control artifact",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"reviewer risk register markdown missing phrase: {phrase}")
    if SUPPLEMENT_BODY.exists():
        supplement = SUPPLEMENT_BODY.read_text(encoding="utf-8")
        if "reviewer-risk register" not in supplement:
            failures.append("supplement does not disclose the reviewer-risk register")
    return failures


def check_final_human_readthrough() -> list[str]:
    failures: list[str] = []
    if not FINAL_HUMAN_READTHROUGH.exists():
        return [f"missing final human read-through artifact: {FINAL_HUMAN_READTHROUGH.relative_to(ROOT)}"]
    text = FINAL_HUMAN_READTHROUGH.read_text(encoding="utf-8")
    fields = {
        "status": field_value(text, "status"),
        "signed-off-by": field_value(text, "signed-off-by"),
        "signed-off-date": field_value(text, "signed-off-date"),
        "reviewed-release": field_value(text, "reviewed-release"),
        "reviewed-commit": field_value(text, "reviewed-commit"),
        "doi-archive": field_value(text, "doi-archive"),
        "venue-target": field_value(text, "venue-target"),
        "author-guidelines-url": field_value(text, "author-guidelines-url"),
        "author-guidelines-checked-by": field_value(text, "author-guidelines-checked-by"),
        "author-guidelines-checked-date": field_value(text, "author-guidelines-checked-date"),
        "author-guidelines-superseding-instructions": field_value(
            text,
            "author-guidelines-superseding-instructions",
        ),
    }
    for field_name, value in fields.items():
        if field_name in {
            "signed-off-by",
            "signed-off-date",
            "reviewed-commit",
            "doi-archive",
            "author-guidelines-checked-by",
            "author-guidelines-checked-date",
            "author-guidelines-superseding-instructions",
        }:
            continue
        if not value:
            failures.append(f"final human read-through missing {field_name}")
    status = fields["status"].lower()
    if status not in {"pending", "complete"}:
        failures.append(f"final human read-through has unsupported status: {fields['status']}")
    if fields["reviewed-release"] != RELEASE_TAG:
        failures.append(
            "final human read-through reviewed-release does not match current release tag: "
            f"{fields['reviewed-release']} != {RELEASE_TAG}"
        )
    if status == "complete":
        for field_name in (
            "signed-off-by",
            "signed-off-date",
            "reviewed-commit",
            "author-guidelines-checked-by",
            "author-guidelines-checked-date",
            "author-guidelines-superseding-instructions",
        ):
            if not fields[field_name]:
                failures.append(f"completed final human read-through missing {field_name}")
        if fields["author-guidelines-superseding-instructions"].strip().lower() not in {
            "none",
            "no",
            "none identified",
            "no superseding instructions",
        }:
            failures.append(
                "completed final human read-through has not cleared live author-page superseding instructions"
            )
    required_phrases = [
        "Scholarly Read-Through Checklist",
        "Live Regulation & Governance Author-Page Refresh",
        "Data and Code Availability",
        "AI Use Disclosure",
        "make paper-artifacts-check",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"final human read-through missing checklist phrase: {phrase}")
    return failures


def check_final_human_readthrough_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path
        for path in (FINAL_HUMAN_READTHROUGH_AUDIT_CSV, FINAL_HUMAN_READTHROUGH_AUDIT_MD)
        if not path.exists()
    ]
    if missing:
        return [f"missing final human read-through audit artifact: {path.relative_to(ROOT)}" for path in missing]
    with FINAL_HUMAN_READTHROUGH_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = {
            row.get("item", ""): row
            for row in csv.DictReader(source)
        }
    overall = rows.get("overall-final-human-readthrough", {})
    if not overall:
        failures.append("final human read-through audit missing overall row")
    elif overall.get("status") == "blocked":
        failures.append(f"final human read-through audit is blocked: {overall.get('evidence', '')}")
    elif overall.get("status") not in {"manual_required", "ready"}:
        failures.append(
            "final human read-through audit has unexpected overall status: "
            f"{overall.get('status', '')}"
        )
    required_items = [
        "status",
        "reviewed-release",
        "venue-target",
        "author-guidelines-url",
        "overall-final-human-readthrough",
    ]
    required_items.extend(f"scholarly-readthrough-checklist-{index:02d}" for index in range(1, 15))
    required_items.extend(f"live-author-page-checklist-{index:02d}" for index in range(1, 4))
    for item in required_items:
        if item not in rows:
            failures.append(f"final human read-through audit missing item: {item}")
    text = FINAL_HUMAN_READTHROUGH_AUDIT_MD.read_text(encoding="utf-8")
    for phrase in (
        "Final Human Read-Through Audit",
        "Manual-required",
        "overall-final-human-readthrough",
        "scholarly-readthrough-checklist-14",
    ):
        if phrase not in text:
            failures.append(f"final human read-through audit markdown missing phrase: {phrase}")
    if "blocked=0" not in overall.get("evidence", ""):
        failures.append("final human read-through audit overall evidence does not record blocked=0")
    return failures


def check_final_readthrough_evidence() -> list[str]:
    failures: list[str] = []
    missing = [
        path
        for path in (FINAL_READTHROUGH_EVIDENCE_CSV, FINAL_READTHROUGH_EVIDENCE_MD)
        if not path.exists()
    ]
    if missing:
        return [f"missing final read-through evidence artifact: {path.relative_to(ROOT)}" for path in missing]
    with FINAL_READTHROUGH_EVIDENCE_CSV.open(newline="", encoding="utf-8") as source:
        rows = {
            row.get("item", ""): row
            for row in csv.DictReader(source)
        }
    overall = rows.get("overall-final-readthrough-evidence", {})
    if not overall:
        failures.append("final read-through evidence missing overall row")
    elif overall.get("status") != "manual_required":
        failures.append(
            "final read-through evidence should remain manual_required, not "
            f"{overall.get('status', '')}"
        )
    for index in range(1, 15):
        item = f"scholarly-readthrough-checklist-{index:02d}"
        row = rows.get(item)
        if not row:
            failures.append(f"final read-through evidence missing item: {item}")
            continue
        if row.get("status") == "blocked":
            failures.append(f"final read-through evidence row is blocked: {item}")
        if not row.get("evidenceFiles"):
            failures.append(f"final read-through evidence row lacks evidence files: {item}")
        if not row.get("remainingHumanAction"):
            failures.append(f"final read-through evidence row lacks human action: {item}")
    text = FINAL_READTHROUGH_EVIDENCE_MD.read_text(encoding="utf-8")
    for phrase in (
        "Final Read-Through Evidence",
        "reviewer aid, not a human signoff",
        "automated_support_present",
        "external_manual_required",
        "Human signoff remains controlled by `reports/final-human-readthrough.md`",
        "scholarly-readthrough-checklist-14",
    ):
        if phrase not in text:
            failures.append(f"final read-through evidence markdown missing phrase: {phrase}")
    return failures


def field_value(text: str, field_name: str) -> str:
    match = re.search(
        rf"^[^\S\n]*{re.escape(field_name)}[^\S\n]*:[^\S\n]*(.*?)[^\S\n]*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def check_latex_log_audit() -> list[str]:
    failures: list[str] = []
    missing = [
        path.relative_to(ROOT)
        for path in (LATEX_LOG_AUDIT_MD, LATEX_LOG_AUDIT_CSV)
        if not path.exists()
    ]
    if missing:
        return [f"missing LaTeX log audit artifact: {path}" for path in missing]

    with LATEX_LOG_AUDIT_CSV.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        failures.append("LaTeX log audit has no rows")
    for row in rows:
        document = row.get("document", "<missing document>")
        if row.get("status") != "pass":
            failures.append(
                "LaTeX log audit has unresolved compile state: "
                f"{document} status={row.get('status', '')} unresolved={row.get('unresolvedKinds', '')}"
            )
        if row.get("unresolvedCount") not in {"0", ""}:
            failures.append(
                "LaTeX log audit reports unresolved markers: "
                f"{document} unresolvedCount={row.get('unresolvedCount', '')}"
            )
    text = LATEX_LOG_AUDIT_MD.read_text(encoding="utf-8")
    required_text = [
        "Unresolved states: `0`",
        "Box-Warning Follow-Up",
        "Visual follow-up",
        "local-manuscript",
        "wiley-manuscript",
        "supplement",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"LaTeX log audit markdown missing phrase: {phrase}")
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


def check_archive_handoff_manifest() -> list[str]:
    failures: list[str] = []
    required = [ARCHIVE_HANDOFF_CSV, ARCHIVE_HANDOFF_JSON, ARCHIVE_HANDOFF_MD]
    for path in required:
        if not path.exists():
            failures.append(f"missing archive handoff manifest file: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        manifest = json.loads(ARCHIVE_HANDOFF_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"archive handoff JSON is not valid JSON: {error}"]
    if manifest.get("schema") != "lobby-capture-archive-handoff-manifest-v1":
        failures.append("archive handoff manifest has unexpected schema")
    if manifest.get("releaseTag") != RELEASE_TAG:
        failures.append(
            f"archive handoff manifest releaseTag={manifest.get('releaseTag')!r} does not match {RELEASE_TAG}"
        )
    expected_url = f"https://github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/{RELEASE_TAG}"
    if manifest.get("releaseUrl") != expected_url:
        failures.append("archive handoff manifest releaseUrl does not match the current release tag")

    try:
        with ARCHIVE_HANDOFF_CSV.open(newline="", encoding="utf-8") as source:
            csv_rows = list(csv.DictReader(source))
    except OSError as error:
        return [*failures, f"could not read archive handoff CSV: {error}"]
    json_rows = manifest.get("rows")
    if not isinstance(json_rows, list):
        failures.append("archive handoff JSON rows field is not a list")
        json_rows = []
    if len(csv_rows) != len(json_rows):
        failures.append("archive handoff CSV and JSON row counts differ")

    rows_by_path = {
        row.get("path", ""): row
        for row in csv_rows
        if row.get("path")
    }
    expected_paths = {
        "dist/lobby-capture-wiley-submission.zip",
        "paper/regulation-governance-wiley.pdf",
        f"paper/{LOCAL_BASENAME}.pdf",
        "paper/supplement.pdf",
        "CITATION.cff",
        ".zenodo.json",
        "reports/submission-readiness.md",
        "reports/reviewer-risk-register.csv",
        "reports/reviewer-risk-register.md",
        "reports/final-human-readthrough.md",
        "reports/final-human-readthrough-audit.csv",
        "reports/final-human-readthrough-audit.md",
    }
    for path in sorted(expected_paths - set(rows_by_path)):
        failures.append(f"archive handoff manifest omits expected path: {path}")

    for path, row in sorted(rows_by_path.items()):
        if path in {f"reports/{name}" for name in ARCHIVE_HANDOFF_REPORT_NAMES}:
            failures.append(f"archive handoff manifest should not checksum itself: {path}")
            continue
        source = ROOT / path
        if not source.exists():
            failures.append(f"archive handoff manifest lists missing file: {path}")
            continue
        checksum_status = row.get("checksumStatus")
        if row.get("includeInDoiDeposit") == "yes":
            if checksum_status != RELEASE_ASSET_CHECKSUM_STATUS:
                failures.append(
                    f"archive handoff release asset {path} has unexpected checksumStatus={checksum_status!r}"
                )
            if row.get("sha256") != "see-dist-release-asset-checksums":
                failures.append(
                    f"archive handoff release asset {path} should point to dist release checksums"
                )
            if row.get("bytes") != "see-dist-release-asset-checksums":
                failures.append(
                    f"archive handoff release asset {path} should not record environment-specific byte counts"
                )
            continue
        if checksum_status != TRACKED_SOURCE_CHECKSUM_STATUS:
            failures.append(
                f"archive handoff tracked source {path} has unexpected checksumStatus={checksum_status!r}"
            )
            continue
        if not git_tracked(source):
            failures.append(f"archive handoff tracked source {path} is not tracked by git")
        data = source.read_bytes()
        if row.get("sha256") != hashlib.sha256(data).hexdigest():
            failures.append(f"archive handoff checksum mismatch for {path}")
        if row.get("bytes") != str(len(data)):
            failures.append(f"archive handoff byte count mismatch for {path}")

    primary_assets = set(manifest.get("primaryReleaseAssets", []))
    expected_assets = {
        "lobby-capture-wiley-submission.zip",
        "regulation-governance-wiley.pdf",
        f"{LOCAL_BASENAME}.pdf",
        "supplement.pdf",
    }
    if primary_assets != expected_assets:
        failures.append("archive handoff primary release asset list is incomplete or unexpected")
    markdown = ARCHIVE_HANDOFF_MD.read_text(encoding="utf-8")
    for phrase in (
        RELEASE_TAG,
        "DOI status: not asserted by this manifest",
        "SHA-256",
        "dist/release-asset-checksums",
        RELEASE_ASSET_CHECKSUM_STATUS,
    ):
        if phrase not in markdown:
            failures.append(f"archive handoff markdown missing required phrase: {phrase}")
    return failures


def check_doi_deposit_package() -> list[str]:
    failures: list[str] = []
    for path in (
        DOI_DEPOSIT_PACKAGE,
        DOI_DEPOSIT_PACKAGE_MANIFEST_JSON,
        DOI_DEPOSIT_PACKAGE_MANIFEST_MD,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON,
        DOI_DEPOSIT_PACKAGE_CHECKSUM_MD,
    ):
        if not path.exists():
            failures.append(f"missing DOI deposit package artifact: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        manifest = json.loads(DOI_DEPOSIT_PACKAGE_MANIFEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"DOI deposit package manifest JSON is invalid: {error}"]
    if manifest.get("schema") != "lobby-capture-doi-deposit-package-v1":
        failures.append("DOI deposit package manifest has unexpected schema")
    if manifest.get("releaseTag") != RELEASE_TAG:
        failures.append(
            f"DOI deposit package manifest releaseTag={manifest.get('releaseTag')!r} does not match {RELEASE_TAG}"
        )

    members = manifest.get("members")
    if not isinstance(members, list):
        return [*failures, "DOI deposit package manifest members field is not a list"]
    expected_primary = {
        "primary-assets/lobby-capture-wiley-submission.zip",
        "primary-assets/regulation-governance-wiley.pdf",
        f"primary-assets/{LOCAL_BASENAME}.pdf",
        "primary-assets/supplement.pdf",
    }
    primary = set(manifest.get("primaryDepositAssets", []))
    if primary != expected_primary:
        failures.append("DOI deposit package primaryDepositAssets list is incomplete or unexpected")

    rows_by_member = {
        row.get("member", ""): row
        for row in members
        if isinstance(row, dict) and row.get("member")
    }
    required_members = expected_primary | {
        "README-DOI-DEPOSIT.txt",
        "metadata/CITATION.cff",
        "metadata/zenodo.json",
        "metadata/release-asset-checksums.csv",
        "metadata/release-asset-checksums.json",
        "metadata/release-asset-checksums.md",
        "readiness/archive-handoff-manifest.csv",
        "readiness/archive-handoff-manifest.json",
        "readiness/archive-handoff-manifest.md",
        "readiness/submission-readiness.csv",
        "readiness/submission-readiness.md",
        "readiness/reviewer-risk-register.csv",
        "readiness/reviewer-risk-register.md",
        "readiness/wiley-submission-form-readiness.csv",
        "readiness/wiley-submission-form-readiness.md",
        "readiness/reggov-guidelines-readiness.csv",
        "readiness/reggov-guidelines-readiness.md",
        "readiness/final-human-readthrough.md",
        "readiness/final-human-readthrough-audit.csv",
        "readiness/final-human-readthrough-audit.md",
        "readiness/literature-positioning-audit.csv",
        "readiness/literature-positioning-audit.md",
        "readiness/reference-integrity-audit.csv",
        "readiness/reference-integrity-audit.md",
        "readiness/final-readthrough-evidence.csv",
        "readiness/final-readthrough-evidence.md",
    }
    for member in sorted(required_members - set(rows_by_member)):
        failures.append(f"DOI deposit package manifest omits expected member: {member}")

    try:
        with zipfile.ZipFile(DOI_DEPOSIT_PACKAGE) as archive:
            names = set(archive.namelist())
            bad_member = archive.testzip()
            if bad_member is not None:
                failures.append(f"DOI deposit package has corrupt member: {bad_member}")
            required_zip_members = set(rows_by_member) | {
                "doi-deposit-package-manifest.json",
                "doi-deposit-package-manifest.md",
            }
            for member in sorted(required_zip_members - names):
                failures.append(f"DOI deposit package zip omits expected member: {member}")
            if "readiness/doi-deposit-readiness.md" in names or "readiness/doi-deposit-readiness.csv" in names:
                failures.append("DOI deposit package should not include the verifier report that checks the package")
            if "doi-deposit-package-manifest.json" in names:
                if archive.read("doi-deposit-package-manifest.json") != DOI_DEPOSIT_PACKAGE_MANIFEST_JSON.read_bytes():
                    failures.append("DOI deposit package embedded JSON manifest differs from dist copy")
            if "doi-deposit-package-manifest.md" in names:
                if archive.read("doi-deposit-package-manifest.md") != DOI_DEPOSIT_PACKAGE_MANIFEST_MD.read_bytes():
                    failures.append("DOI deposit package embedded Markdown manifest differs from dist copy")
            for member, row in sorted(rows_by_member.items()):
                if member not in names:
                    continue
                data = archive.read(member)
                if row.get("sha256") != hashlib.sha256(data).hexdigest():
                    failures.append(f"DOI deposit package manifest checksum mismatch for {member}")
                if row.get("bytes") != str(len(data)):
                    failures.append(f"DOI deposit package manifest byte count mismatch for {member}")
                source_path = row.get("sourcePath", "")
                if source_path and source_path != "generated":
                    source = ROOT / source_path
                    if not source.exists():
                        failures.append(f"DOI deposit package lists missing source path: {source_path}")
                    elif data != source.read_bytes():
                        failures.append(f"DOI deposit package member {member} differs from {source_path}")
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        failures.append(f"could not inspect DOI deposit package zip: {error}")

    markdown = DOI_DEPOSIT_PACKAGE_MANIFEST_MD.read_text(encoding="utf-8")
    for phrase in (
        "DOI Deposit Package Manifest",
        RELEASE_TAG,
        "does not assert that a DOI has been minted",
        "primary-assets/lobby-capture-wiley-submission.zip",
        "readiness/submission-readiness.md",
        "readiness/reviewer-risk-register.md",
    ):
        if phrase not in markdown:
            failures.append(f"DOI deposit package manifest markdown missing phrase: {phrase}")
    failures.extend(check_doi_deposit_package_checksum())
    return failures


def check_doi_deposit_package_checksum() -> list[str]:
    failures: list[str] = []
    data = DOI_DEPOSIT_PACKAGE.read_bytes()
    expected_sha = hashlib.sha256(data).hexdigest()
    expected_bytes = str(len(data))
    try:
        with DOI_DEPOSIT_PACKAGE_CHECKSUM_CSV.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
    except OSError as error:
        return [f"could not read DOI deposit package checksum CSV: {error}"]
    if len(rows) != 1:
        failures.append("DOI deposit package checksum CSV should have exactly one data row")
        row = rows[0] if rows else {}
    else:
        row = rows[0]
    if row.get("path") != str(DOI_DEPOSIT_PACKAGE.relative_to(ROOT)):
        failures.append("DOI deposit package checksum CSV path does not match package")
    if row.get("releaseAssetName") != DOI_DEPOSIT_PACKAGE.name:
        failures.append("DOI deposit package checksum CSV release asset name does not match package")
    if row.get("sha256") != expected_sha:
        failures.append("DOI deposit package checksum CSV SHA-256 does not match package")
    if row.get("bytes") != expected_bytes:
        failures.append("DOI deposit package checksum CSV byte count does not match package")

    try:
        checksum_json = json.loads(DOI_DEPOSIT_PACKAGE_CHECKSUM_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [*failures, f"DOI deposit package checksum JSON is invalid: {error}"]
    if checksum_json.get("schema") != "lobby-capture-doi-deposit-package-checksum-v1":
        failures.append("DOI deposit package checksum JSON has unexpected schema")
    if checksum_json.get("releaseTag") != RELEASE_TAG:
        failures.append("DOI deposit package checksum JSON release tag does not match current release tag")
    json_row = checksum_json.get("row")
    if not isinstance(json_row, dict):
        failures.append("DOI deposit package checksum JSON row is missing")
    elif json_row.get("sha256") != expected_sha or json_row.get("bytes") != expected_bytes:
        failures.append("DOI deposit package checksum JSON does not match package bytes")

    checksum_md = DOI_DEPOSIT_PACKAGE_CHECKSUM_MD.read_text(encoding="utf-8")
    for phrase in (
        "DOI Deposit Package Checksum",
        RELEASE_TAG,
        DOI_DEPOSIT_PACKAGE.name,
        expected_sha,
    ):
        if phrase not in checksum_md:
            failures.append(f"DOI deposit package checksum markdown missing phrase: {phrase}")
    return failures


def check_zenodo_deposit_preflight() -> list[str]:
    failures: list[str] = []
    for path in (
        ZENODO_DEPOSIT_PREFLIGHT_CSV,
        ZENODO_DEPOSIT_PREFLIGHT_MD,
        ZENODO_DEPOSIT_METADATA_JSON,
    ):
        if not path.exists():
            failures.append(f"missing Zenodo deposit preflight artifact: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        metadata_payload = json.loads(ZENODO_DEPOSIT_METADATA_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"Zenodo deposit metadata JSON is invalid: {error}"]
    metadata = metadata_payload.get("metadata")
    if not isinstance(metadata, dict):
        failures.append("Zenodo deposit metadata JSON missing metadata object")
        metadata = {}
    if metadata.get("version") != RELEASE_TAG:
        failures.append(
            "Zenodo deposit metadata version does not match current release tag: "
            f"{metadata.get('version', '')} != {RELEASE_TAG}"
        )
    for field_name in ("title", "upload_type", "publication_date", "creators", "description", "license"):
        if not metadata.get(field_name):
            failures.append(f"Zenodo deposit metadata missing {field_name}")
    if metadata.get("license") == "MIT":
        failures.append("Zenodo deposit metadata should use Zenodo license id mit-license, not raw MIT")
    related = metadata.get("related_identifiers", [])
    if not isinstance(related, list) or not any(
        isinstance(item, dict)
        and str(item.get("identifier", "")).endswith(f"/releases/tag/{RELEASE_TAG}")
        for item in related
    ):
        failures.append("Zenodo deposit metadata does not relate to the current GitHub release tag")

    try:
        with ZENODO_DEPOSIT_PREFLIGHT_CSV.open(newline="", encoding="utf-8") as source:
            rows = {row.get("gate", ""): row for row in csv.DictReader(source)}
    except OSError as error:
        return [*failures, f"could not read Zenodo deposit preflight CSV: {error}"]
    expected_statuses = {
        "metadata-json": {"ready"},
        "api-target": {"ready"},
        "token": {"manual_required", "ready"},
        "doi-package": {"ready"},
        "archive-manifest": {"ready"},
        "claim-boundary": {"ready"},
        "doi-record": {"manual_required", "ready"},
        "human-readthrough": {"manual_required", "ready"},
    }
    for gate_name, statuses in expected_statuses.items():
        row = rows.get(gate_name)
        if not row:
            failures.append(f"Zenodo deposit preflight missing gate: {gate_name}")
            continue
        if row.get("status") not in statuses:
            failures.append(
                f"Zenodo deposit preflight gate {gate_name} has status={row.get('status', '')}, "
                f"expected one of {sorted(statuses)}"
            )
    if any(row.get("status") == "blocked" for row in rows.values()):
        failures.append("Zenodo deposit preflight has a blocked gate")

    text = ZENODO_DEPOSIT_PREFLIGHT_MD.read_text(encoding="utf-8")
    for phrase in (
        "Zenodo Deposit Preflight",
        RELEASE_TAG,
        "does not assert that a DOI has been minted",
        "ZENODO_ACCESS_TOKEN",
        "make zenodo-deposit-draft",
        "make zenodo-deposit-upload",
    ):
        if phrase not in text:
            failures.append(f"Zenodo deposit preflight markdown missing phrase: {phrase}")
    return failures


def check_doi_deposit_readiness() -> list[str]:
    failures: list[str] = []
    for path in (DOI_DEPOSIT_READINESS_CSV, DOI_DEPOSIT_READINESS_MD):
        if not path.exists():
            failures.append(f"missing DOI deposit readiness report: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        with DOI_DEPOSIT_READINESS_CSV.open(newline="", encoding="utf-8") as source:
            rows = {row.get("gate", ""): row for row in csv.DictReader(source)}
    except OSError as error:
        return [f"could not read DOI deposit readiness CSV: {error}"]
    expected_statuses = {
        "release-metadata": {"ready"},
        "primary-release-assets": {"ready"},
        "release-asset-checksums": {"ready"},
        "doi-deposit-package": {"ready"},
        "zenodo-preflight": {"ready"},
        "claim-boundary": {"ready"},
        "doi-record": {"manual_required", "ready"},
        "human-readthrough": {"manual_required", "ready"},
        "final-journal-submission": {"manual_required", "ready"},
    }
    for gate_name, statuses in expected_statuses.items():
        row = rows.get(gate_name)
        if not row:
            failures.append(f"DOI deposit readiness missing gate: {gate_name}")
            continue
        if row.get("status") not in statuses:
            failures.append(
                f"DOI deposit readiness gate {gate_name} has status={row.get('status', '')}, "
                f"expected one of {sorted(statuses)}"
            )

    final_gate = rows.get("final-journal-submission", {})
    if final_gate.get("status") == "ready":
        doi_gate = rows.get("doi-record", {})
        human_gate = rows.get("human-readthrough", {})
        if doi_gate.get("status") != "ready" or human_gate.get("status") != "ready":
            failures.append("DOI deposit readiness clears final submission before DOI and human signoff are ready")
    if rows.get("doi-record", {}).get("status") == "ready":
        text_sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (CITATION_CFF, ZENODO_JSON, SUBMISSION_DECLARATIONS, FINAL_HUMAN_READTHROUGH)
            if path.exists()
        )
        if not re.search(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", text_sources):
            failures.append("DOI deposit readiness says DOI is ready but no DOI appears in metadata")

    text = DOI_DEPOSIT_READINESS_MD.read_text(encoding="utf-8")
    required_text = [
        "DOI Deposit Readiness",
        RELEASE_TAG,
        "It does not assert that a DOI has been minted",
        "Final journal-submission status:",
        "live author-page refresh",
        "lobby-capture-wiley-submission.zip",
        "lobby-capture-doi-deposit-package.zip",
        "zenodo-preflight",
        "dist/release-asset-checksums",
        "reports/final-human-readthrough.md",
        "reports/final-human-readthrough-audit.md",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"DOI deposit readiness markdown missing phrase: {phrase}")
    return failures


def check_wiley_submission_form_readiness() -> list[str]:
    failures: list[str] = []
    for path in (WILEY_SUBMISSION_FORM_READINESS_CSV, WILEY_SUBMISSION_FORM_READINESS_MD):
        if not path.exists():
            failures.append(f"missing Wiley submission form readiness report: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        with WILEY_SUBMISSION_FORM_READINESS_CSV.open(newline="", encoding="utf-8") as source:
            rows = {row.get("gate", ""): row for row in csv.DictReader(source)}
    except OSError as error:
        return [f"could not read Wiley submission form readiness CSV: {error}"]
    expected_statuses = {
        "submission-archive-present": {"ready"},
        "upload-size": {"ready"},
        "filename-length": {"ready"},
        "root-latex-and-pdf": {"ready"},
        "supporting-files": {"ready"},
        "unsupported-upload-formats": {"ready"},
        "data-and-ai-statements": {"ready"},
        "journal-specific-author-guidelines": {"manual_required", "ready"},
    }
    for gate_name, statuses in expected_statuses.items():
        row = rows.get(gate_name)
        if not row:
            failures.append(f"Wiley submission form readiness missing gate: {gate_name}")
            continue
        if row.get("status") not in statuses:
            failures.append(
                f"Wiley submission form gate {gate_name} has status={row.get('status', '')}, "
                f"expected one of {sorted(statuses)}"
            )
    blocked = [name for name, row in rows.items() if row.get("status") == "blocked"]
    for gate_name in sorted(blocked):
        failures.append(f"Wiley submission form readiness has blocked gate: {gate_name}")

    text = WILEY_SUBMISSION_FORM_READINESS_MD.read_text(encoding="utf-8")
    required_text = [
        "Wiley Submission Form Readiness",
        "Mechanical upload status: `ready`",
        "manual journal-specific author-guidelines refresh required",
        "500 MB",
        "root `.tex`",
        "compiled PDF",
        "unsupported executable or script upload formats",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"Wiley submission form readiness markdown missing phrase: {phrase}")
    return failures


def check_reggov_guidelines_readiness() -> list[str]:
    failures: list[str] = []
    for path in (REGGOV_GUIDELINES_READINESS_CSV, REGGOV_GUIDELINES_READINESS_MD):
        if not path.exists():
            failures.append(f"missing Regulation & Governance guideline readiness report: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        with REGGOV_GUIDELINES_READINESS_CSV.open(newline="", encoding="utf-8") as source:
            rows = {row.get("gate", ""): row for row in csv.DictReader(source)}
    except OSError as error:
        return [f"could not read Regulation & Governance guideline readiness CSV: {error}"]

    expected_statuses = {
        "journal-target-and-article-type": {"ready"},
        "word-limit": {"ready"},
        "abstract-and-keywords": {"ready"},
        "title-page-metadata": {"ready"},
        "data-code-availability": {"ready"},
        "ai-funding-conflict-disclosures": {"ready"},
        "figures-and-tables": {"ready"},
        "supporting-information": {"ready"},
        "supporting-information-format-size": {"ready"},
        "latex-submission-files": {"ready"},
        "live-reggov-author-page-refresh": {"manual_required", "ready"},
    }
    for gate_name, statuses in expected_statuses.items():
        row = rows.get(gate_name)
        if not row:
            failures.append(f"Regulation & Governance guideline readiness missing gate: {gate_name}")
            continue
        if row.get("status") not in statuses:
            failures.append(
                f"Regulation & Governance guideline gate {gate_name} has status={row.get('status', '')}, "
                f"expected one of {sorted(statuses)}"
            )
    blocked = [name for name, row in rows.items() if row.get("status") == "blocked"]
    for gate_name in sorted(blocked):
        failures.append(f"Regulation & Governance guideline readiness has blocked gate: {gate_name}")

    text = REGGOV_GUIDELINES_READINESS_MD.read_text(encoding="utf-8")
    required_text = [
        "Regulation & Governance Guideline Readiness",
        "Automated guideline status:",
        "8,000-10,000",
        "11,000",
        "150",
        "three suggested reviewers",
        "double-anonymized review",
        "Data and Code Availability",
        "AI Use Disclosure",
        "10 MB",
        "live Regulation & Governance author page",
        "root .tex",
        "compiled PDF",
        "supporting-information",
    ]
    for phrase in required_text:
        if phrase not in text:
            failures.append(f"Regulation & Governance guideline readiness markdown missing phrase: {phrase}")
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
            failures.extend(check_submission_package_manifest(archive, names))
            return failures
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        return [f"could not inspect submission zip: {error}"]


def check_submission_package_manifest(
    archive: zipfile.ZipFile,
    names: set[str],
) -> list[str]:
    manifest_member = "supporting-information/submission-package-manifest.json"
    manifest_markdown = "supporting-information/submission-package-manifest.md"
    failures: list[str] = []
    if manifest_member not in names:
        return [f"submission zip missing {manifest_member}"]
    if manifest_markdown not in names:
        failures.append(f"submission zip missing {manifest_markdown}")
    try:
        manifest = json.loads(archive.read(manifest_member).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as error:
        return [*failures, f"submission package manifest is not valid JSON: {error}"]

    if manifest.get("schema") != "lobby-capture-submission-package-manifest-v1":
        failures.append("submission package manifest has unexpected schema")
    if manifest.get("releaseTag") != RELEASE_TAG:
        failures.append(
            f"submission package manifest releaseTag={manifest.get('releaseTag')!r} does not match {RELEASE_TAG}"
        )
    members = manifest.get("members")
    if not isinstance(members, list):
        return [*failures, "submission package manifest members field is not a list"]

    manifest_paths: set[str] = set()
    for index, entry in enumerate(members):
        if not isinstance(entry, dict):
            failures.append(f"submission package manifest member {index} is not an object")
            continue
        path = entry.get("path")
        expected_sha = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        if not isinstance(path, str) or not path:
            failures.append(f"submission package manifest member {index} has invalid path")
            continue
        manifest_paths.add(path)
        if path in {manifest_member, manifest_markdown}:
            failures.append(f"submission package manifest should not checksum itself: {path}")
            continue
        if path not in names:
            failures.append(f"submission package manifest lists missing member: {path}")
            continue
        data = archive.read(path)
        actual_sha = hashlib.sha256(data).hexdigest()
        if expected_sha != actual_sha:
            failures.append(f"submission package manifest checksum mismatch for {path}")
        if expected_bytes != len(data):
            failures.append(f"submission package manifest byte count mismatch for {path}")

    expected_paths = {
        name
        for name in names
        if not name.endswith("/")
        and name not in {manifest_member, manifest_markdown}
    }
    missing_from_manifest = sorted(expected_paths - manifest_paths)
    extra_in_manifest = sorted(manifest_paths - expected_paths)
    failures.extend(
        f"submission package manifest omits member: {path}"
        for path in missing_from_manifest
    )
    failures.extend(
        f"submission package manifest lists non-package member: {path}"
        for path in extra_in_manifest
    )
    if manifest.get("memberCount") != len(manifest_paths):
        failures.append("submission package manifest memberCount does not match listed members")
    return failures


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
        (PROCUREMENT_BENCHMARK_CROSSWALK_MD, "supporting-information/procurement-benchmark-crosswalk.md"),
        (PROCUREMENT_REFRESH_READINESS_MD, "supporting-information/procurement-refresh-readiness.md"),
        (
            FIRST_WAVE_PROCUREMENT_SOURCE_ACQUISITION_MD,
            "supporting-information/first-wave-procurement-source-acquisition.md",
        ),
        (ROOT / "reports" / "claim-boundary-audit.md", "supporting-information/claim-boundary-audit.md"),
        (ROOT / "reports" / "claim-source-dependency.md", "supporting-information/claim-source-dependency.md"),
        (CAUSAL_CALIBRATION_TARGETS_MD, "supporting-information/causal-calibration-targets.md"),
        (FIRST_WAVE_CAUSAL_PROTOCOLS_MD, "supporting-information/first-wave-causal-protocols.md"),
        (FIRST_WAVE_SOURCE_PRODUCTS_MD, "supporting-information/first-wave-source-products.md"),
        (FIRST_WAVE_LINKAGE_CANDIDATES_MD, "supporting-information/first-wave-linkage-candidates.md"),
        (FIRST_WAVE_SOURCE_READINESS_MD, "supporting-information/first-wave-source-readiness.md"),
        (ROOT / "reports" / "claim-posture-audit.md", "supporting-information/claim-posture-audit.md"),
        (ROOT / "reports" / "validation-summary.md", "supporting-information/validation-summary.md"),
        (VALIDATION_SCOPE_COVERAGE_MD, "supporting-information/validation-scope-coverage.md"),
        (ROOT / "reports" / "substitution-audit.md", "supporting-information/substitution-audit.md"),
        (ROOT / "reports" / "lobby-capture-portfolio.md", "supporting-information/portfolio-screen.md"),
        (ROOT / "reports" / "calibration-queue.md", "supporting-information/calibration-queue.md"),
        (CALIBRATION_READINESS_MD, "supporting-information/calibration-readiness.md"),
        (POLICY_CLAIM_LANGUAGE_AUDIT_MD, "supporting-information/policy-claim-language-audit.md"),
        (SUBMISSION_READINESS_MD, "supporting-information/submission-readiness.md"),
        (REVIEWER_RISK_REGISTER_MD, "supporting-information/reviewer-risk-register.md"),
        (LATEX_LOG_AUDIT_MD, "supporting-information/latex-log-audit.md"),
        (ROOT / "reports" / "paper-layout-audit.md", "supporting-information/paper-layout-audit.md"),
        (ROOT / "reports" / "manual-visual-audit.md", "supporting-information/manual-visual-audit.md"),
        (FINAL_HUMAN_READTHROUGH, "supporting-information/final-human-readthrough.md"),
        (FINAL_HUMAN_READTHROUGH_AUDIT_MD, "supporting-information/final-human-readthrough-audit.md"),
        (FINAL_READTHROUGH_EVIDENCE_MD, "supporting-information/final-readthrough-evidence.md"),
        (CITATION_CFF, "supporting-information/CITATION.cff"),
        (ZENODO_JSON, "supporting-information/zenodo.json"),
    ]
    checks.extend(
        (path, f"supporting-information/source-product-templates/first-wave/{path.name}")
        for path in sorted(FIRST_WAVE_SOURCE_TEMPLATE_DIR.glob("*"))
        if path.is_file()
    )
    checks.extend(
        (path, f"supporting-information/source-products/first-wave/{path.name}")
        for path in sorted([
            *FIRST_WAVE_CANDIDATE_SEED_PRODUCTS.values(),
            *FIRST_WAVE_TEXT_SOURCE_PRODUCTS.values(),
        ])
        if path.exists()
    )
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
        if path.name not in SUBMISSION_REPORT_DATA_EXCLUSIONS
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
        env["TZ"] = "UTC"
        env["SOURCE_DATE_EPOCH"] = "1777939200"
        env["FORCE_SOURCE_DATE"] = "1"
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


def int_or_zero(value: object) -> int:
    try:
        return int(str(value or "").strip())
    except ValueError:
        return 0


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
