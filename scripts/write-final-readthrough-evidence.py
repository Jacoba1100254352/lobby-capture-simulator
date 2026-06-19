#!/usr/bin/env python3
"""Write an evidence packet for the final human scholarly read-through.

This report does not sign off the paper. It maps each manual read-through
checkbox to current generated evidence so the final reviewer can see what the
automated pipeline already supports and what still requires human judgment or
external DOI/archive action.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
READTHROUGH = REPORTS / "final-human-readthrough.md"
OUTPUT_CSV = REPORTS / "final-readthrough-evidence.csv"
OUTPUT_MD = REPORTS / "final-readthrough-evidence.md"

EXPECTED_ITEMS = [
    "Abstract states the mechanism-model contribution without implying calibrated policy-effect estimation.",
    "Introduction separates model assumptions, synthetic results, and empirical bridge scope.",
    "Literature positioning explains the regulatory-governance contribution relative to lobbying, capture, venue-shifting, and ABM validation work.",
    "Model specification is internally consistent with the ODD-style supplement and does not leave unresolved equations, parameters, or diagnostic definitions.",
    "Results describe synthetic mechanism behavior and do not present reform rankings as real-world policy estimates.",
    "Empirical bridge language is bounded to source moments, source-panel coverage, and validation-gap diagnostics.",
    "Tables and figures are referenced in order, readable in the Wiley PDF, and not duplicative or misleading.",
    "Limitations identify open source panels, causal-calibration targets, and construct-validity risks without self-rejecting submission language.",
    "Data and Code Availability names the exact release, repository, license, DOI archive if available, and excluded private/raw credentialed payloads.",
    "Archive-handoff manifest checksums match the final release assets and DOI-deposit asset set.",
    "Zenodo deposit preflight and any unpublished draft metadata match the signed-off release before a DOI record is published.",
    'References are complete enough for the target venue and do not contain placeholder or "planned validation" entries.',
    "AI Use Disclosure and declarations match journal expectations.",
    "The final release ZIP, PDFs, supplement, reports, and metadata match the signed-off release tag.",
]

ACCEPTABLE_POLICY_STATUSES = {"bounded_context", "required_boundary_present"}


def main() -> int:
    rows = evidence_rows()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown(rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 0 if not any(row["status"] == "blocked" for row in rows) else 1


def evidence_rows() -> list[dict[str, str]]:
    rows = [
        abstract_scope_row(),
        introduction_scope_row(),
        literature_positioning_row(),
        model_specification_row(),
        synthetic_results_row(),
        empirical_bridge_row(),
        layout_visual_row(),
        limitations_row(),
        data_code_row(),
        archive_handoff_row(),
        zenodo_row(),
        references_row(),
        ai_disclosure_row(),
        final_bundle_row(),
    ]
    readthrough_items = checklist_items(read_text(READTHROUGH))
    for index, row in enumerate(rows, start=1):
        expected = EXPECTED_ITEMS[index - 1]
        if row["checklistItem"] != expected:
            row["status"] = "blocked"
            row["automatedEvidence"] = "Script checklist mapping is out of sync with final-human-readthrough.md."
        elif expected not in readthrough_items:
            row["status"] = "blocked"
            row["automatedEvidence"] = "Checklist item is missing from final-human-readthrough.md."
        row["item"] = f"scholarly-readthrough-checklist-{index:02d}"
    rows.append(overall_row(rows))
    return rows


def abstract_scope_row() -> dict[str, str]:
    policy_rows = read_csv(REPORTS / "policy-claim-language-audit.csv")
    overclaims = [row for row in policy_rows if row.get("status") not in ACCEPTABLE_POLICY_STATUSES]
    abstract_text = manuscript_abstract()
    has_mechanism = "mechanism" in abstract_text.lower()
    has_bounded_language = any(
        phrase in abstract_text.lower()
        for phrase in ("rather than causal", "synthetic", "modeled", "public data")
    )
    status = "automated_support_present" if not overclaims and has_mechanism and has_bounded_language else "manual_review_required"
    evidence = (
        f"policy overclaim hits={len(overclaims)}; abstract mechanism language={'yes' if has_mechanism else 'no'}; "
        f"abstract bounded-language signal={'yes' if has_bounded_language else 'no'}"
    )
    return evidence_row(
        EXPECTED_ITEMS[0],
        status,
        evidence,
        "paper/strategic-channel-substitution-regulatory-capture.tex; paper/regulation-governance-wiley.tex; reports/policy-claim-language-audit.md",
        "Confirm the abstract reads as a mechanism-model contribution, not a calibrated policy-effect claim.",
    )


def introduction_scope_row() -> dict[str, str]:
    submission = keyed_rows(REPORTS / "submission-readiness.csv", "gate")
    mechanism = submission.get("mechanism-manuscript", {})
    empirical = submission.get("empirical-bridge-scope", {})
    policy = submission.get("calibrated-policy-claims", {})
    status = (
        "automated_support_present"
        if mechanism.get("status") == "ready"
        and empirical.get("status") == "bounded"
        and policy.get("status") == "blocked"
        else "manual_review_required"
    )
    return evidence_row(
        EXPECTED_ITEMS[1],
        status,
        (
            f"mechanism={mechanism.get('status', 'missing')}; "
            f"empiricalBridge={empirical.get('status', 'missing')}; "
            f"calibratedPolicy={policy.get('status', 'missing')}"
        ),
        "reports/submission-readiness.md; paper/sections/reggov-body.tex",
        "Read the introduction for rhetorical separation of assumptions, synthetic findings, and empirical bridge limits.",
    )


def literature_positioning_row() -> dict[str, str]:
    rows = read_csv(REPORTS / "literature-positioning-audit.csv")
    counts: dict[str, int] = {}
    for row in rows:
        row_status = row.get("status", "")
        counts[row_status] = counts.get(row_status, 0) + 1
    ready = counts.get("ready", 0)
    partial = counts.get("partial", 0)
    blocked = counts.get("blocked", 0)
    status = "automated_support_present" if rows and blocked == 0 and ready >= 7 else "manual_editorial_review_required"
    return evidence_row(
        EXPECTED_ITEMS[2],
        status,
        f"literatureAuditReady={ready}; literatureAuditPartial={partial}; literatureAuditBlocked={blocked}",
        "reports/literature-positioning-audit.md; paper/sections/reggov-body.tex; paper/references.bib",
        "Judge whether the audited literature coverage is persuasive and sufficiently developed for the target venue.",
    )


def model_specification_row() -> dict[str, str]:
    required_files = [
        ROOT / "docs" / "odd-model.md",
        ROOT / "paper" / "tables" / "composite_weights.tex",
        ROOT / "paper" / "tables" / "switch_rule_snapshot.tex",
        ROOT / "reports" / "claim-posture-audit.md",
    ]
    latex_pass = all(row.get("status") == "pass" for row in read_csv(REPORTS / "latex-log-audit.csv"))
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    status = "automated_support_present" if latex_pass and not missing else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[3],
        status,
        f"latexLogsPass={'yes' if latex_pass else 'no'}; missingSpecArtifacts={'; '.join(missing) or 'none'}",
        "docs/odd-model.md; paper/tables/composite_weights.tex; paper/tables/switch_rule_snapshot.tex; reports/latex-log-audit.md",
        "Compare the main-text model description against the ODD supplement and generated diagnostic tables.",
    )


def synthetic_results_row() -> dict[str, str]:
    policy_rows = read_csv(REPORTS / "policy-claim-language-audit.csv")
    overclaims = [row for row in policy_rows if row.get("status") not in ACCEPTABLE_POLICY_STATUSES]
    claim = keyed_rows(REPORTS / "claim-posture-audit.csv", "gate").get("Calibrated policy-simulation claim", {})
    status = "automated_support_present" if not overclaims and claim.get("status") == "not_cleared" else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[4],
        status,
        f"policy overclaim hits={len(overclaims)}; calibratedPolicyGate={claim.get('status', 'missing')}",
        "reports/policy-claim-language-audit.md; reports/claim-posture-audit.md; reports/substitution-audit.md",
        "Read result prose for overinterpretation despite the mechanical language audit passing.",
    )


def empirical_bridge_row() -> dict[str, str]:
    claim = keyed_rows(REPORTS / "claim-posture-audit.csv", "gate").get("Empirical bridge", {})
    panels = read_csv(REPORTS / "source-panel-inventory.csv")
    source_limited = [row for row in panels if is_source_limited_panel(row)]
    status = "automated_support_present" if claim.get("status") == "bounded" and source_limited else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[5],
        status,
        f"empiricalBridge={claim.get('status', 'missing')}; sourceLimitedPanels={len(source_limited)}",
        "reports/claim-posture-audit.md; reports/source-panel-inventory.md; reports/source-capability-audit.md",
        "Check that the manuscript describes the bridge as bounded source support rather than validation of hidden-channel magnitudes.",
    )


def is_source_limited_panel(row: dict[str, str]) -> bool:
    return row.get("status") == "usable" and row.get("supportLevel") != "direct-bounded"


def layout_visual_row() -> dict[str, str]:
    submission = keyed_rows(REPORTS / "submission-readiness.csv", "gate")
    layout = submission.get("layout-and-visual-audit", {})
    latex_pass = all(row.get("status") == "pass" for row in read_csv(REPORTS / "latex-log-audit.csv"))
    structure_rows = read_csv(REPORTS / "paper-structure-audit.csv")
    structure_failures = [row for row in structure_rows if row.get("status") == "fail"]
    status = (
        "automated_support_present"
        if layout.get("status") == "ready" and latex_pass and structure_rows and not structure_failures
        else "manual_review_required"
    )
    return evidence_row(
        EXPECTED_ITEMS[6],
        status,
        (
            f"layoutVisualGate={layout.get('status', 'missing')}; "
            f"latexLogsPass={'yes' if latex_pass else 'no'}; "
            f"structureFailures={len(structure_failures)}"
        ),
        "reports/paper-layout-audit.md; reports/paper-structure-audit.md; reports/manual-visual-audit.md; reports/latex-log-audit.md",
        "Visually inspect the Wiley PDF one last time, especially figure placement and table readability.",
    )


def limitations_row() -> dict[str, str]:
    targets = read_csv(REPORTS / "causal-calibration-targets.csv")
    blocking = [row for row in targets if row.get("blocksPolicySimulation") == "yes"]
    body = read_text(ROOT / "paper" / "sections" / "reggov-body.tex")
    has_limitations = "Limitations and Future Validation" in body
    has_open_targets = "Ten generated causal-calibration targets remain open" in body
    status = "automated_support_present" if has_limitations and has_open_targets and blocking else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[7],
        status,
        f"limitationsSection={'yes' if has_limitations else 'no'}; openCausalTargets={len(blocking)}; targetLanguage={'yes' if has_open_targets else 'no'}",
        "paper/sections/reggov-body.tex; reports/causal-calibration-targets.md; reports/reviewer-risk-register.md",
        "Judge whether the limitations are specific and candid without sounding like a self-rejection.",
    )


def data_code_row() -> dict[str, str]:
    reggov = keyed_rows(REPORTS / "reggov-guidelines-readiness.csv", "gate")
    data_gate = reggov.get("data-code-availability", {})
    doi_present = bool(find_doi())
    status = "automated_support_present" if data_gate.get("status") == "ready" and doi_present else "external_manual_required"
    return evidence_row(
        EXPECTED_ITEMS[8],
        status,
        f"dataCodeGate={data_gate.get('status', 'missing')}; doiRecorded={'yes' if doi_present else 'no'}",
        "paper/sections/submission-declarations.tex; reports/reggov-guidelines-readiness.md; CITATION.cff; .zenodo.json",
        "Record the DOI once minted; before then, verify the statement keeps DOI absence explicit.",
    )


def archive_handoff_row() -> dict[str, str]:
    rows = read_csv(REPORTS / "archive-handoff-manifest.csv")
    expected_assets = {
        "lobby-capture-wiley-submission.zip",
        "regulation-governance-wiley.pdf",
        "strategic-channel-substitution-regulatory-capture.pdf",
        "supplement.pdf",
    }
    assets = {row.get("releaseAssetName", "") for row in rows if row.get("includeInDoiDeposit") == "yes"}
    checksum_rows = [row for row in rows if row.get("checksumStatus") == "release-asset-checksum-recorded-in-dist"]
    status = "automated_support_present" if expected_assets == assets and len(checksum_rows) == 4 else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[9],
        status,
        f"primaryAssets={len(assets)}/4; releaseAssetChecksumRows={len(checksum_rows)}",
        "reports/archive-handoff-manifest.md; dist/release-asset-checksums.md",
        "Use the checksum files during archive deposition and record the final DOI afterward.",
    )


def zenodo_row() -> dict[str, str]:
    metadata_present = (ROOT / ".zenodo.json").exists() and (ROOT / "CITATION.cff").exists()
    return evidence_row(
        EXPECTED_ITEMS[10],
        "external_manual_required",
        f"metadataPresent={'yes' if metadata_present else 'no'}; unpublishedDraft=manual_not_asserted_by_this_packet",
        ".zenodo.json; CITATION.cff; reports/archive-handoff-manifest.md",
        "Run Zenodo preflight/draft/upload only after a token is configured and the final release is frozen.",
    )


def references_row() -> dict[str, str]:
    references = read_text(ROOT / "paper" / "references.bib")
    body = read_text(ROOT / "paper" / "sections" / "reggov-body.tex")
    bad_phrases = ["planned validation", "TODO", "FIXME"]
    hits = [phrase for phrase in bad_phrases if phrase.lower() in references.lower() or phrase.lower() in body.lower()]
    latex_pass = all(row.get("status") == "pass" for row in read_csv(REPORTS / "latex-log-audit.csv"))
    audit_rows = read_csv(REPORTS / "reference-integrity-audit.csv")
    blocked = sum(1 for row in audit_rows if row.get("status") == "blocked")
    advisory = sum(1 for row in audit_rows if row.get("status") == "advisory")
    ready = sum(1 for row in audit_rows if row.get("status") == "ready")
    status = "automated_support_present" if not hits and latex_pass and audit_rows and blocked == 0 else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[11],
        status,
        (
            f"placeholderPhrases={'; '.join(hits) or 'none'}; "
            f"latexLogsPass={'yes' if latex_pass else 'no'}; "
            f"referenceAuditReady={ready}; referenceAuditAdvisory={advisory}; referenceAuditBlocked={blocked}"
        ),
        "paper/references.bib; reports/reference-integrity-audit.md; reports/latex-log-audit.md",
        "Perform a human bibliography adequacy check for venue fit and scholarly completeness.",
    )


def ai_disclosure_row() -> dict[str, str]:
    declarations = read_text(ROOT / "paper" / "sections" / "submission-declarations.tex")
    wiley = keyed_rows(REPORTS / "wiley-submission-form-readiness.csv", "gate").get("data-and-ai-statements", {})
    lowered = declarations.lower()
    has_ai = (
        "ai use disclosure" in lowered
        and "author reviewed" in lowered
        and "responsible for all text, code, citations, analyses, and conclusions" in lowered
    )
    status = "automated_support_present" if has_ai and wiley.get("status") == "ready" else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[12],
        status,
        f"aiDisclosure={'yes' if has_ai else 'no'}; wileyDataAiGate={wiley.get('status', 'missing')}",
        "paper/sections/submission-declarations.tex; reports/wiley-submission-form-readiness.md",
        "Confirm the disclosure matches the final journal form wording before submission.",
    )


def final_bundle_row() -> dict[str, str]:
    submission = keyed_rows(REPORTS / "submission-readiness.csv", "gate")
    bundle = submission.get("reproducible-review-bundle", {})
    guideline = keyed_rows(REPORTS / "reggov-guidelines-readiness.csv", "gate").get("latex-submission-files", {})
    status = "automated_support_present" if bundle.get("status") == "ready" and guideline.get("status") == "ready" else "manual_review_required"
    return evidence_row(
        EXPECTED_ITEMS[13],
        status,
        f"reviewBundle={bundle.get('status', 'missing')}; latexSubmissionFiles={guideline.get('status', 'missing')}",
        "reports/submission-readiness.md; reports/reggov-guidelines-readiness.md; dist/lobby-capture-wiley-submission.zip",
        "After any edit, rerun the full artifact gate and repeat this read-through evidence check.",
    )


def find_doi() -> str:
    pattern = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
    for path in (
        ROOT / "CITATION.cff",
        ROOT / ".zenodo.json",
        ROOT / "paper" / "sections" / "submission-declarations.tex",
        READTHROUGH,
    ):
        match = pattern.search(read_text(path))
        if match:
            return match.group(0)
    return ""


def overall_row(rows: list[dict[str, str]]) -> dict[str, str]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    blocked = counts.get("blocked", 0)
    status = "blocked" if blocked else "manual_required"
    evidence = "; ".join(f"{key}={counts[key]}" for key in sorted(counts))
    return {
        "item": "overall-final-readthrough-evidence",
        "checklistItem": "Overall automated evidence packet",
        "status": status,
        "automatedEvidence": evidence,
        "evidenceFiles": "reports/final-readthrough-evidence.md; reports/final-human-readthrough.md",
        "remainingHumanAction": "Use this packet to complete the human scholarly read-through; it does not replace signoff.",
    }


def evidence_row(
        checklist_item: str,
        status: str,
        evidence: str,
        evidence_files: str,
        remaining_action: str,
) -> dict[str, str]:
    return {
        "item": "",
        "checklistItem": checklist_item,
        "status": status,
        "automatedEvidence": evidence,
        "evidenceFiles": evidence_files,
        "remainingHumanAction": remaining_action,
    }


def manuscript_abstract() -> str:
    local = first_abstract(read_text(ROOT / "paper" / "strategic-channel-substitution-regulatory-capture.tex"))
    if local:
        return local
    wiley = wiley_abstract(read_text(ROOT / "paper" / "regulation-governance-wiley.tex"))
    if wiley:
        return wiley
    return first_abstract(read_text(ROOT / "paper" / "sections" / "reggov-body.tex"))


def first_abstract(text: str) -> str:
    match = re.search(r"\\begin\{abstract\}(.+?)\\end\{abstract\}", text, re.DOTALL)
    return match.group(1) if match else ""


def wiley_abstract(text: str) -> str:
    match = re.search(r"\\abstract(?:\[[^\]]*\])?\{(.+?)\}", text, re.DOTALL)
    return match.group(1) if match else ""


def checklist_items(text: str) -> set[str]:
    return {
        match.group(1).strip()
        for match in re.finditer(r"^- \[[ xX]\] (.+?)\s*$", text, re.MULTILINE)
    }


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {
        row.get(key, ""): row
        for row in read_csv(path)
        if row.get(key)
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["item", "checklistItem", "status", "automatedEvidence", "evidenceFiles", "remainingHumanAction"]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    lines = [
        "# Final Read-Through Evidence",
        "",
        (
            "This generated packet maps each unchecked scholarly read-through item to "
            "current automated evidence. It is a reviewer aid, not a human signoff."
        ),
        "",
        "## Summary",
        "",
        f"- Overall status: `{rows[-1]['status']}`",
        "- Status counts: " + "; ".join(f"`{key}={counts[key]}`" for key in sorted(counts)),
        "- Human signoff remains controlled by `reports/final-human-readthrough.md`.",
        "",
        "## Evidence Matrix",
        "",
        "| Item | Status | Automated evidence | Evidence files | Remaining human action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        if row["item"] == "overall-final-readthrough-evidence":
            continue
        lines.append(
            "| {item} | {status} | {evidence} | {files} | {action} |".format(
                item=cell(row["item"]),
                status=cell(row["status"]),
                evidence=cell(row["automatedEvidence"]),
                files=cell(row["evidenceFiles"]),
                action=cell(row["remainingHumanAction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "`automated_support_present` means the generated reports provide useful support "
                "for the checklist item. It does not mean the item is checked or signed."
            ),
            (
                "`manual_editorial_review_required`, `manual_review_required`, and "
                "`external_manual_required` all require human action before final journal submission."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
