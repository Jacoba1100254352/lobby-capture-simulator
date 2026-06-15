#!/usr/bin/env python3
"""Synthesize publication-readiness gates into one review-bundle audit."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CITATION_CFF = ROOT / "CITATION.cff"
ZENODO_JSON = ROOT / ".zenodo.json"
SUBMISSION_DECLARATIONS = ROOT / "paper" / "sections" / "submission-declarations.tex"
FINAL_HUMAN_READTHROUGH = REPORTS / "final-human-readthrough.md"
REGGOV_AUTHOR_GUIDELINES_URL = "https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html"
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def main() -> int:
    rows = readiness_rows()
    write_csv(REPORTS / "submission-readiness.csv", rows)
    write_markdown(REPORTS / "submission-readiness.md", rows)
    print("Wrote reports/submission-readiness.csv")
    print("Wrote reports/submission-readiness.md")
    return 0


def readiness_rows() -> list[dict[str, str]]:
    posture = keyed_rows(REPORTS / "claim-posture-audit.csv", "gate")
    calibration = keyed_rows(REPORTS / "calibration-readiness.csv", "gate")
    claim_dependencies = keyed_rows(REPORTS / "claim-source-dependency.csv", "claimKey")
    causal_targets = read_csv(REPORTS / "causal-calibration-targets.csv")
    policy_hits = read_csv(REPORTS / "policy-claim-language-audit.csv")
    latex_logs = read_csv(REPORTS / "latex-log-audit.csv")
    layout = read_text(REPORTS / "paper-layout-audit.md")
    visual = read_text(REPORTS / "manual-visual-audit.md")

    open_causal = [row for row in causal_targets if row.get("blocksPolicySimulation") == "yes"]
    overclaims = [
        row for row in policy_hits
        if row.get("status") not in {"bounded_context", "required_boundary_present"}
    ]
    bounded_dependencies = [
        row for row in claim_dependencies.values()
        if row.get("status") == "bounded"
    ]
    not_cleared_dependencies = [
        row for row in claim_dependencies.values()
        if row.get("status") == "not_cleared"
    ]

    mechanism = posture.get("Mechanism-model article", {})
    empirical = posture.get("Empirical bridge", {})
    policy = posture.get("Calibrated policy-simulation claim", {})
    reproducibility = posture.get("Reproducibility and layout bundle", {})
    calibration_policy = calibration.get("calibrated-policy-readiness", {})

    layout_ok = "- Failures: `0`" in layout
    visual_ok = "scripted pass" in visual and "layout pass" in visual
    latex_logs_ok = bool(latex_logs) and all(row.get("status") == "pass" for row in latex_logs)
    unresolved_latex = sum(int(row.get("unresolvedCount", "0") or "0") for row in latex_logs)
    policy_language_ok = len(overclaims) == 0

    policy_evidence = policy.get("evidence", "missing policy posture")
    if "open causal targets=" not in policy_evidence:
        policy_evidence = f"{policy_evidence}; open causal targets={len(open_causal)}"

    rows = [
        gate(
            "mechanism-manuscript",
            "ready" if mechanism.get("status") == "cleared" else "blocked",
            mechanism.get("evidence", "missing claim-posture evidence"),
            "The paper may be reviewed as a transparent mechanism-model article when this gate is ready.",
            mechanism.get("nextAction", "Regenerate claim-posture audit."),
        ),
        gate(
            "empirical-bridge-scope",
            "bounded" if empirical.get("status") == "bounded" else empirical.get("status", "missing"),
            empirical.get("evidence", "missing empirical-bridge evidence"),
            "Source rows constrain distributional anchors and validation gaps, not hidden-channel magnitudes.",
            empirical.get("nextAction", "Regenerate claim-posture audit."),
        ),
        gate(
            "calibrated-policy-claims",
            "blocked" if policy.get("status") == "not_cleared" and calibration_policy.get("status") == "blocked" else "check",
            policy_evidence,
            "The package must not be described as estimating calibrated reform effects while this gate is blocked.",
            policy.get("nextAction", "Clear causal-calibration targets before using calibrated policy language."),
        ),
        gate(
            "claim-source-dependencies",
            "bounded" if bounded_dependencies and not_cleared_dependencies else "check",
            f"bounded dependencies={len(bounded_dependencies)}; not-cleared dependencies={len(not_cleared_dependencies)}",
            "Bounded claim families can support mechanism stress tests but not representative hidden-channel claims.",
            "Keep the claim-source dependency audit in the submission bundle and clear bounded dependencies before stronger claims.",
        ),
        gate(
            "policy-language-audit",
            "ready" if policy_language_ok else "blocked",
            f"overclaim or missing-boundary hits={len(overclaims)}",
            "The manuscript and supplement should not contain unbounded causal, calibrated-policy, ranking, or representativeness language.",
            "Revise flagged language and rerun the policy-claim audit.",
        ),
        gate(
            "layout-and-visual-audit",
            "ready" if layout_ok and visual_ok and latex_logs_ok else "blocked",
            (
                f"layout failures={'0' if layout_ok else 'unknown/nonzero'}; "
                f"visual checklist={'pass' if visual_ok else 'check'}; "
                f"latex unresolved={unresolved_latex}"
            ),
            "Figures, tables, generated PDFs, and final LaTeX logs pass the automated layout, label-readability, and unresolved-log checks.",
            "Inspect and rerun the visual/layout audits after any figure, table, or LaTeX change.",
        ),
        gate(
            "reproducible-review-bundle",
            "ready" if reproducibility.get("status") == "cleared" else "blocked",
            reproducibility.get("evidence", "missing reproducibility/layout claim-posture evidence"),
            "The release bundle is suitable for review only after the full paper artifact gate passes.",
            reproducibility.get("nextAction", "Rerun make paper-artifacts-check."),
        ),
        final_journal_submission_gate(),
    ]
    rows.append(overall_row(rows, len(open_causal)))
    return rows


def gate(name: str, status: str, evidence: str, implication: str, next_action: str) -> dict[str, str]:
    return {
        "gate": name,
        "status": status,
        "evidence": evidence,
        "submissionImplication": implication,
        "nextAction": next_action,
    }


def overall_row(rows: list[dict[str, str]], open_causal_targets: int) -> dict[str, str]:
    statuses = {row["gate"]: row["status"] for row in rows}
    ready_gates = {
        "mechanism-manuscript",
        "policy-language-audit",
        "layout-and-visual-audit",
        "reproducible-review-bundle",
    }
    ready = all(statuses.get(gate_name) == "ready" for gate_name in ready_gates)
    bounded_ok = statuses.get("empirical-bridge-scope") == "bounded"
    policy_blocked = statuses.get("calibrated-policy-claims") == "blocked"
    dependency_bounded = statuses.get("claim-source-dependencies") == "bounded"
    if ready and bounded_ok and policy_blocked and dependency_bounded:
        status = "ready_for_mechanism_review"
        implication = (
            "The review bundle is ready to circulate as a mechanism-model package "
            "with a bounded empirical bridge; it is not a calibrated policy-effect submission "
            "or a final journal-submission signoff."
        )
    else:
        status = "blocked"
        implication = "One or more review-bundle gates is not in the expected state."
    return gate(
        "overall-submission-posture",
        status,
        f"open causal-calibration targets={open_causal_targets}",
        implication,
        "Before final journal submission, clear the final-journal-submission gate.",
    )


def final_journal_submission_gate() -> dict[str, str]:
    archive_doi = find_archive_doi()
    release_metadata_present = release_metadata_present_in_archival_files()
    readthrough = final_human_readthrough_state()
    author_page = live_author_page_refresh_state()
    human_signoff = readthrough["complete"]
    author_page_ready = author_page["ready"]
    status = "ready" if archive_doi and human_signoff and author_page_ready else "manual_required"
    missing_actions: list[str] = []
    if not archive_doi:
        missing_actions.append("mint or record a DOI archive, such as Zenodo or OSF")
    if not human_signoff:
        missing_actions.append(
            f"complete and sign off a human scholarly read-through in {FINAL_HUMAN_READTHROUGH.relative_to(ROOT)}"
        )
    if not author_page_ready:
        missing_actions.append(
            "open and record the live Regulation & Governance author-page refresh"
        )
    next_action = "; ".join(missing_actions) if missing_actions else "Final submission externalities are cleared."
    return gate(
        "final-journal-submission",
        status,
        (
            f"release metadata={'present' if release_metadata_present else 'missing'}; "
            f"DOI archive={'present: ' + archive_doi if archive_doi else 'not detected'}; "
            f"human scholarly read-through={readthrough['evidence']}; "
            f"live author-page refresh={author_page['evidence']}"
        ),
        (
            "Final journal submission requires archive, human editorial signoff, and live author-page refresh; "
            "mechanism-review circulation can proceed without treating this gate as cleared."
        ),
        next_action,
    )


def find_archive_doi() -> str:
    for path in (CITATION_CFF, ZENODO_JSON, SUBMISSION_DECLARATIONS):
        match = DOI_PATTERN.search(read_text(path))
        if match:
            return match.group(0)
    return ""


def release_metadata_present_in_archival_files() -> bool:
    citation = read_text(CITATION_CFF)
    zenodo = read_text(ZENODO_JSON)
    return "github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/" in citation and (
        "github.com/Jacoba1100254352/lobby-capture-simulator/releases/tag/" in zenodo
    )


def final_human_readthrough_state() -> dict[str, str | bool]:
    text = read_text(FINAL_HUMAN_READTHROUGH)
    current_release = current_release_tag()
    if not text:
        return {
            "complete": False,
            "evidence": "not signed off; file missing",
        }
    status = field_value(text, "status").lower()
    signed_off_by = field_value(text, "signed-off-by")
    signed_off_date = field_value(text, "signed-off-date")
    reviewed_release = field_value(text, "reviewed-release")
    reviewed_commit = field_value(text, "reviewed-commit")
    if (
        status == "complete"
        and signed_off_by
        and signed_off_date
        and reviewed_commit
        and reviewed_release == current_release
    ):
        return {
            "complete": True,
            "evidence": f"complete for {reviewed_release}",
        }
    details = [
        f"status={status or 'missing'}",
        f"reviewed-release={reviewed_release or 'missing'}",
    ]
    if reviewed_release and reviewed_release != current_release:
        details.append(f"expected-release={current_release or 'missing'}")
    if status == "complete":
        if not signed_off_by:
            details.append("signer=missing")
        if not signed_off_date:
            details.append("date=missing")
        if not reviewed_commit:
            details.append("commit=missing")
    return {
        "complete": False,
        "evidence": f"not signed off ({'; '.join(details)})",
    }


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
        "evidence": ("ready: " if ready else "manual_required: ") + evidence,
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


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in read_csv(path) if key in row}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=["gate", "status", "evidence", "submissionImplication", "nextAction"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    summary = rows[-1]
    lines = [
        "# Submission Readiness Audit",
        "",
        "This audit synthesizes the generated claim, validation, layout, visual, and policy-language gates into one submission decision surface. It does not replace peer review or a final human read-through.",
        "",
        "## Overall Posture",
        "",
        f"- Status: `{summary['status']}`",
        f"- Evidence: {summary['evidence']}",
        f"- Submission implication: {summary['submissionImplication']}",
        f"- Next action: {summary['nextAction']}",
        "",
        "## Gate Summary",
        "",
        "| Gate | Status | Evidence | Submission implication | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows[:-1]:
        lines.append(
            "| {gate} | {status} | {evidence} | {submissionImplication} | {nextAction} |".format(
                gate=escape(row["gate"]),
                status=escape(row["status"]),
                evidence=escape(row["evidence"]),
                submissionImplication=escape(row["submissionImplication"]),
                nextAction=escape(row["nextAction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "A `ready_for_mechanism_review` posture means the release can be read as a mechanism-model manuscript with bounded source bridges. It does not clear calibrated policy-effect claims, representative hidden-channel magnitudes, or final venue-specific editorial acceptance.",
            "",
            "## Final Journal Submission Boundary",
            "",
            "The `final-journal-submission` gate records external submission requirements that cannot be cleared by simulator tests alone: DOI archiving, a human scholarly read-through, and live Regulation & Governance author-page refresh. This gate is deliberately separate from mechanism-review readiness so the bundle can circulate for review without implying final journal-submission signoff.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
