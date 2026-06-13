#!/usr/bin/env python3
"""Synthesize publication-readiness gates into one review-bundle audit."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


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
            "ready" if layout_ok and visual_ok else "blocked",
            f"layout failures={'0' if layout_ok else 'unknown/nonzero'}; visual checklist={'pass' if visual_ok else 'check'}",
            "Figures, tables, and generated PDFs pass the automated layout and label-readability checks.",
            "Inspect and rerun the visual/layout audits after any figure, table, or LaTeX change.",
        ),
        gate(
            "reproducible-review-bundle",
            "ready" if reproducibility.get("status") == "cleared" else "blocked",
            reproducibility.get("evidence", "missing reproducibility/layout claim-posture evidence"),
            "The release bundle is suitable for review only after the full paper artifact gate passes.",
            reproducibility.get("nextAction", "Rerun make paper-artifacts-check."),
        ),
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
            "with a bounded empirical bridge; it is not a calibrated policy-effect submission."
        )
    else:
        status = "blocked"
        implication = "One or more review-bundle gates is not in the expected state."
    return gate(
        "overall-submission-posture",
        status,
        f"open causal-calibration targets={open_causal_targets}",
        implication,
        "Before final journal submission, complete a human scholarly read-through and add a DOI archive if the venue requires one.",
    )


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
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
