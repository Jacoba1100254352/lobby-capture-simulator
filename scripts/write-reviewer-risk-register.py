#!/usr/bin/env python3
"""Write a reviewer-facing risk register from generated readiness reports.

The register is not a new empirical claim. It is a compact map from likely
reviewer objections to the current evidence, claim boundary, and next action.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CSV_OUT = REPORTS / "reviewer-risk-register.csv"
MD_OUT = REPORTS / "reviewer-risk-register.md"
FIXED_GENERATED_AT = "2026-05-05T00:00:00Z"
FIELDNAMES = [
    "riskId",
    "reviewerConcern",
    "status",
    "evidence",
    "currentResponse",
    "claimBoundary",
    "nextAction",
]


def main() -> int:
    required = [
        "submission-readiness.csv",
        "calibration-readiness.csv",
        "claim-source-dependency.csv",
        "causal-calibration-targets.csv",
        "source-capability-audit.csv",
        "source-panel-inventory.csv",
        "procurement-refresh-readiness.csv",
        "first-wave-procurement-source-acquisition.csv",
        "final-human-readthrough-audit.csv",
        "policy-claim-language-audit.csv",
        "validation-summary.csv",
    ]
    missing = [name for name in required if not (REPORTS / name).exists()]
    if missing:
        raise SystemExit(f"Missing input reports: {', '.join(missing)}")

    context = load_context()
    rows = risk_rows(context)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(CSV_OUT, rows)
    MD_OUT.write_text(markdown(rows, context), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")
    return 0


def load_context() -> dict[str, object]:
    submission = keyed_rows("submission-readiness.csv", "gate")
    calibration = keyed_rows("calibration-readiness.csv", "gate")
    claim_dependencies = read_rows("claim-source-dependency.csv")
    causal_targets = keyed_rows("causal-calibration-targets.csv", "targetKey")
    capabilities = keyed_rows("source-capability-audit.csv", "capability")
    panels = read_rows("source-panel-inventory.csv")
    procurement = keyed_rows("procurement-refresh-readiness.csv", "item")
    procurement_acquisition = keyed_rows("first-wave-procurement-source-acquisition.csv", "productKey")
    final_readthrough = keyed_rows("final-human-readthrough-audit.csv", "item")
    policy_language = read_rows("policy-claim-language-audit.csv")
    validation = read_rows("validation-summary.csv")
    return {
        "submission": submission,
        "calibration": calibration,
        "claim_dependencies": claim_dependencies,
        "causal_targets": causal_targets,
        "capabilities": capabilities,
        "panels": panels,
        "procurement": procurement,
        "procurement_acquisition": procurement_acquisition,
        "final_readthrough": final_readthrough,
        "policy_language": policy_language,
        "validation": validation,
    }


def risk_rows(context: dict[str, object]) -> list[dict[str, str]]:
    submission: dict[str, dict[str, str]] = context["submission"]  # type: ignore[assignment]
    calibration: dict[str, dict[str, str]] = context["calibration"]  # type: ignore[assignment]
    claim_dependencies: list[dict[str, str]] = context["claim_dependencies"]  # type: ignore[assignment]
    causal_targets: dict[str, dict[str, str]] = context["causal_targets"]  # type: ignore[assignment]
    capabilities: dict[str, dict[str, str]] = context["capabilities"]  # type: ignore[assignment]
    panels: list[dict[str, str]] = context["panels"]  # type: ignore[assignment]
    procurement: dict[str, dict[str, str]] = context["procurement"]  # type: ignore[assignment]
    procurement_acquisition: dict[str, dict[str, str]] = context["procurement_acquisition"]  # type: ignore[assignment]
    final_readthrough: dict[str, dict[str, str]] = context["final_readthrough"]  # type: ignore[assignment]
    policy_language: list[dict[str, str]] = context["policy_language"]  # type: ignore[assignment]
    validation: list[dict[str, str]] = context["validation"]  # type: ignore[assignment]

    dependency_counts = status_counts(claim_dependencies, "status")
    target_counts = status_counts(causal_targets.values(), "status")
    panel_status_counts = status_counts(panels, "status")
    support_counts = status_counts(panels, "supportLevel")
    validation_counts = status_counts(validation, "status")
    overclaim_hits = sum(
        1
        for row in policy_language
        if "overclaim" in row.get("status", "").lower()
        or "missing_required_boundary" in row.get("status", "").lower()
    )

    overall_status = "bounded_for_mechanism_review"
    if submission.get("overall-submission-posture", {}).get("status") != "ready_for_mechanism_review":
        overall_status = "open"
    if final_readthrough.get("overall-final-human-readthrough", {}).get("status") == "ready":
        final_gate = "ready"
    else:
        final_gate = final_readthrough.get("overall-final-human-readthrough", {}).get("status", "manual_required")

    rows = [
        row(
            "overall-reviewer-risk-posture",
            "Does the bundle have a coherent review posture?",
            overall_status,
            join(
                f"submission={submission.get('overall-submission-posture', {}).get('status', 'missing')}",
                f"mechanism={calibration.get('mechanism-model-readiness', {}).get('status', 'missing')}",
                f"empiricalBridge={calibration.get('empirical-bridge-readiness', {}).get('status', 'missing')}",
                f"calibratedPolicy={calibration.get('calibrated-policy-readiness', {}).get('status', 'missing')}",
                f"finalHumanReadthrough={final_gate}",
            ),
            "The package is positioned for mechanism-model review, with final journal submission and calibrated policy-effect claims separated.",
            "Review-bundle readiness is not the same as DOI deposition, human signoff, or calibrated policy simulation.",
            "Complete final human read-through and DOI/archive steps before external journal submission; keep calibrated policy claims out of scope until causal targets clear.",
        ),
        row(
            "self-confirming-substitution-result",
            "Does the simulator simply find substitution because substitution was hard-coded?",
            "mitigated",
            join(
                "mechanism comparison report is generated",
                f"mechanism readiness={calibration.get('mechanism-model-readiness', {}).get('status', 'missing')}",
                f"substitution-elasticity target={causal_targets.get('substitution-elasticity', {}).get('status', 'missing')}",
            ),
            "The model-mode comparison isolates substitution by holding the reform family constant across visible-scalar, multi-channel/no-substitution, and substitution-enabled modes.",
            "The result is a mechanism diagnostic under explicit assumptions, not an empirical discovery of real-world substitution elasticity.",
            causal_targets.get("substitution-elasticity", {}).get(
                "nextAction",
                "Estimate substitution elasticity from a cross-source reform-shock panel before using calibrated substitution magnitudes.",
            ),
        ),
        row(
            "composite-diagnostic-construct-validity",
            "Is total influence distortion an overloaded or double-counted composite?",
            "mitigated",
            join(
                f"policy-language overclaim hits={overclaim_hits}",
                f"validation statuses={compact_counts(validation_counts)}",
                "composite weights and diagnostic variants are generated in manuscript tables",
            ),
            "The manuscript treats total distortion and design loss as transparent grouped diagnostics, with raw component reports and alternate weighting variants retained.",
            "Composite values support within-model sensitivity and portfolio screening, not welfare estimation or independent causal decomposition.",
            "Keep reporting component diagnostics with the composite and calibrate weights only after external outcome and burden evidence is available.",
        ),
        row(
            "empirical-bridge-hidden-channel-support",
            "Are hidden donor, dark-money, and intermediary channels empirically constrained enough?",
            "bounded",
            join(
                f"claim dependencies={compact_counts(dependency_counts)}",
                f"direct-dark-money capability={capabilities.get('direct-dark-money-routing', {}).get('capabilityStatus', 'missing')}",
                f"hidden-donor target={causal_targets.get('hidden-donor-routing-magnitude', {}).get('status', 'missing')}",
            ),
            "Direct/proxy dark-money and nonprofit-routing rows constrain mechanism diagnostics, while the claim-source dependency audit blocks representative hidden-channel magnitude claims.",
            "Hidden-channel rows are a bounded plausibility scaffold, not a representative donor-routing panel.",
            causal_targets.get("hidden-donor-routing-magnitude", {}).get(
                "nextAction",
                "Broaden nonprofit routing and donor-linkage rows before treating hidden-channel magnitudes as empirically supported.",
            ),
        ),
        row(
            "procurement-modification-causal-validity",
            "Does the procurement bridge support claims about capture through contract modifications?",
            "open_calibration",
            join(
                f"SAM capability={capabilities.get('sam-contract-awards-action-history', {}).get('capabilityStatus', 'missing')}",
                f"SAM snapshot={capabilities.get('sam-contract-awards-action-history', {}).get('snapshotStatus', 'missing')}",
                f"USAspending action rows={capabilities.get('usaspending-stratified-action-panel', {}).get('snapshotRows', 'missing')}",
                f"procurement target={causal_targets.get('procurement-modification-causal-capture', {}).get('status', 'missing')}",
                f"refresh status={procurement.get('primary-action-panel', procurement.get('sam-live-status', {})).get('status', 'missing')}",
                f"acquisition products={len(procurement_acquisition)}",
            ),
            "The project separates denominator-mapped USAspending action diagnostics from SAM/FPDS action-history promotion and now maps the missing protest, exclusion, offer-count, and firewall overlays to official acquisition paths.",
            "Procurement modification results are bounded diagnostics until SAM/FPDS coding, offer counts, protests, exclusions, firewall indicators, and exposure designs clear.",
            (
                "Use reports/first-wave-procurement-source-acquisition.md to populate the SAM/FPDS action-history crosswalk, "
                "GAO protest overlay, SAM exclusion overlay, offer-count/competition enrichment, and procurement-firewall overlay; "
                "then rerun first-wave source-product, source-readiness, and paper-artifacts gates."
            ),
        ),
        row(
            "agent-based-institutional-depth",
            "Is the model agent-based enough on the institutional side?",
            "bounded",
            join(
                "lobby organizations and funders are the primary adaptive actors",
                "institutional behavior is represented through arenas, susceptibility, enforcement, and reform controls",
            ),
            "The paper states the model is influence-supply-side centered and uses institutional arenas as structured response surfaces.",
            "The model should not be represented as a rich official-level behavioral simulation.",
            "Add heterogeneous regulator, candidate, procurement-official, and enforcement-agency decision rules only after the influence-channel mechanism remains stable.",
        ),
        row(
            "result-generalizability",
            "Are stress-test results being generalized beyond the scenario and source scope?",
            "bounded",
            join(
                f"panel statuses={compact_counts(panel_status_counts)}",
                f"support levels={compact_counts(support_counts)}",
                f"bounded dependencies={dependency_counts.get('bounded', 0)}",
                f"not-cleared dependencies={dependency_counts.get('not_cleared', 0)}",
            ),
            "Scenario reports are interpreted as mechanism stress tests and are paired with source-panel and claim-dependency limits.",
            "The current empirical bridge supports distributional anchors and gap diagnostics, not population-level reform-effect estimates.",
            "Broaden source panels and clear causal targets before generalizing scenario rankings or hidden-channel magnitudes.",
        ),
        row(
            "policy-ranking-overinterpretation",
            "Do portfolio screens read as policy recommendations?",
            "mitigated",
            join(
                f"policy-language overclaim hits={overclaim_hits}",
                f"calibrated policy gate={calibration.get('calibrated-policy-readiness', {}).get('status', 'missing')}",
                f"calibrated-policy submission gate={submission.get('calibrated-policy-claims', {}).get('status', 'missing')}",
            ),
            "The portfolio screen is framed as a design diagnostic under stated weights rather than a definitive reform ranking.",
            "No portfolio row should be read as an estimated real-world policy effect.",
            "Keep policy language tied to diagnostic tradeoffs, and rerun the language audit after any manuscript rewrite.",
        ),
        row(
            "reproducibility-package-integrity",
            "Can reviewers reproduce and inspect the package evidence?",
            "mitigated",
            join(
                f"reproducible bundle={submission.get('reproducible-review-bundle', {}).get('status', 'missing')}",
                "Full Wiley package, blinded review package, DOI package, archive handoff, and package manifests are checked by paper-artifacts gate",
            ),
            "The generated ZIP and DOI handoff contain report data, checksums, citation metadata, and supporting information for review.",
            "A reproducible review bundle does not by itself imply DOI publication or journal final-submission signoff.",
            "Attach the release asset checksums to the DOI workflow and complete the final human read-through before submission.",
        ),
        row(
            "journal-finalization",
            "Are final submission steps complete?",
            "manual_required",
            join(
                f"final-journal-submission={submission.get('final-journal-submission', {}).get('status', 'missing')}",
                f"finalHumanReadthrough={final_gate}",
                f"overallSubmission={submission.get('overall-submission-posture', {}).get('status', 'missing')}",
            ),
            "The paper bundle is prepared for mechanism-review circulation but records final human signoff and DOI/archive deposition as separate gates.",
            "Do not describe the package as fully submitted or DOI-archived until those external steps are complete and recorded.",
            sentence_case(
                submission.get("final-journal-submission", {}).get(
                    "nextAction",
                    "Complete final human read-through, DOI archive recording, and venue upload checks.",
                )
            ),
        ),
    ]
    return rows


def row(
    risk_id: str,
    concern: str,
    status: str,
    evidence: str,
    response: str,
    boundary: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "riskId": risk_id,
        "reviewerConcern": concern,
        "status": status,
        "evidence": evidence,
        "currentResponse": response,
        "claimBoundary": boundary,
        "nextAction": next_action,
    }


def read_rows(name: str) -> list[dict[str, str]]:
    path = REPORTS / name
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def keyed_rows(name: str, key: str) -> dict[str, dict[str, str]]:
    rows = read_rows(name)
    return {row.get(key, ""): row for row in rows if row.get(key)}


def status_counts(rows: object, field: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:  # type: ignore[assignment]
        if not isinstance(row, dict):
            continue
        value = str(row.get(field, "")).strip() or "missing"
        counter[value] += 1
    return counter


def compact_counts(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return "; ".join(f"{key}={counter[key]}" for key in sorted(counter))


def join(*parts: str) -> str:
    return "; ".join(part for part in parts if part)


def sentence_case(value: str) -> str:
    text = value.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]], context: dict[str, object]) -> str:
    status_counts = Counter(row["status"] for row in rows)
    submission: dict[str, dict[str, str]] = context["submission"]  # type: ignore[assignment]
    lines = [
        "# Reviewer Risk Register",
        "",
        "This generated report maps likely reviewer objections to the current evidence boundary. "
        "It is a review-control artifact, not an additional empirical result.",
        "",
        "## Summary",
        "",
        f"- Generated at: `{FIXED_GENERATED_AT}`",
        f"- Overall posture: `{rows[0]['status']}`",
        f"- Submission-readiness posture: `{submission.get('overall-submission-posture', {}).get('status', 'missing')}`",
        f"- Status counts: `{compact_counts(status_counts)}`",
        "",
        "## Risks",
        "",
        "| Risk | Status | Reviewer concern | Evidence | Current response | Claim boundary | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                escape_markdown_cell(item[key])
                for key in (
                    "riskId",
                    "status",
                    "reviewerConcern",
                    "evidence",
                    "currentResponse",
                    "claimBoundary",
                    "nextAction",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Read this register with `reports/submission-readiness.md`, "
            "`reports/claim-source-dependency.md`, and `reports/causal-calibration-targets.md`. "
            "A `mitigated` row means the current manuscript or package has an explicit response. "
            "A `bounded` row means the mechanism-review claim is allowed only within a stated evidence boundary. "
            "An `open_calibration` row identifies work required before calibrated policy-simulation claims can clear. "
            "A `manual_required` row records a final-submission action outside the deterministic build.",
            "",
        ]
    )
    return "\n".join(lines)


def escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
