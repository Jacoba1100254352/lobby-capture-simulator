#!/usr/bin/env python3
"""Write the mechanism-review circulation readiness audit.

This report is the deterministic handoff surface for the review-bundle posture.
It verifies that automated build, package, and claim-boundary gates are passing
while final journal-submission and calibrated policy-effect claims remain
separate unless their explicit prerequisites have cleared.
"""

from __future__ import annotations

import csv
import sys
import zipfile
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paper_release_metadata import (
    RELEASE_METADATA_FIELDS,
    metadata_summary_lines,
    release_metadata,
    with_release_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"
OUTPUT_CSV = REPORTS / "mechanism-review-circulation-readiness.csv"
OUTPUT_MD = REPORTS / "mechanism-review-circulation-readiness.md"

SUBMISSION_ZIP = DIST / "lobby-capture-wiley-submission.zip"
BLINDED_REVIEW_ZIP = DIST / "lobby-capture-wiley-blinded-review.zip"
DOI_DEPOSIT_PACKAGE = DIST / "lobby-capture-doi-deposit-package.zip"


def main() -> int:
    metadata = release_metadata()
    rows = with_release_metadata(readiness_rows(), metadata)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown(rows, metadata), encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 1 if any(row["status"] == "blocked" for row in rows) else 0


def readiness_rows() -> list[dict[str, str]]:
    submission = keyed_rows(REPORTS / "submission-readiness.csv", "gate")
    doi = keyed_rows(REPORTS / "doi-deposit-readiness.csv", "gate")
    reviewer = keyed_rows(REPORTS / "reviewer-risk-register.csv", "riskId")
    leakage = keyed_rows(REPORTS / "candidate-source-leakage-audit.csv", "item")
    final_evidence = keyed_rows(REPORTS / "final-readthrough-evidence.csv", "item")
    claim_dependency = keyed_rows(REPORTS / "claim-source-dependency.csv", "claimKey")
    source_readiness = read_csv(REPORTS / "first-wave-source-readiness.csv")
    causal_targets = read_csv(REPORTS / "causal-calibration-targets.csv")
    wiley_form = keyed_rows(REPORTS / "wiley-submission-form-readiness.csv", "gate")
    blinded_review = keyed_rows(REPORTS / "blinded-review-package-readiness.csv", "gate")
    reggov = keyed_rows(REPORTS / "reggov-guidelines-readiness.csv", "gate")

    rows = [
        review_posture_row(submission),
        automated_artifact_row(submission, wiley_form, blinded_review, reggov),
        package_surface_row(doi),
        claim_boundary_row(submission, claim_dependency, causal_targets),
        source_product_boundary_row(leakage, source_readiness),
        reviewer_risk_row(reviewer),
        final_readthrough_evidence_row(final_evidence),
        final_submission_boundary_row(submission, doi, reggov),
    ]
    rows.append(overall_row(rows))
    return rows


def review_posture_row(submission: dict[str, dict[str, str]]) -> dict[str, str]:
    overall = submission.get("overall-submission-posture", {})
    mechanism = submission.get("mechanism-manuscript", {})
    empirical = submission.get("empirical-bridge-scope", {})
    calibrated = submission.get("calibrated-policy-claims", {})
    ready = (
        overall.get("status") == "ready_for_mechanism_review"
        and mechanism.get("status") == "ready"
        and empirical.get("status") == "bounded"
        and calibrated.get("status") == "blocked"
    )
    return row(
        "review-posture",
        "ready" if ready else "blocked",
        (
            f"overall={overall.get('status', 'missing')}; "
            f"mechanism={mechanism.get('status', 'missing')}; "
            f"empiricalBridge={empirical.get('status', 'missing')}; "
            f"calibratedPolicy={calibrated.get('status', 'missing')}"
        ),
        "Circulate only as a mechanism-model review bundle with a bounded empirical bridge.",
    )


def automated_artifact_row(
    submission: dict[str, dict[str, str]],
    wiley_form: dict[str, dict[str, str]],
    blinded_review: dict[str, dict[str, str]],
    reggov: dict[str, dict[str, str]],
) -> dict[str, str]:
    required_submission = {
        "policy-language-audit": "ready",
        "layout-and-visual-audit": "ready",
        "reproducible-review-bundle": "ready",
    }
    bad_submission = [
        f"{gate}={submission.get(gate, {}).get('status', 'missing')}"
        for gate, expected in required_submission.items()
        if submission.get(gate, {}).get("status") != expected
    ]
    wiley_blocked = statuses_matching(wiley_form, "blocked")
    blinded_not_ready = [
        gate for gate, item in blinded_review.items() if item.get("status") != "ready"
    ]
    reggov_blocked = statuses_matching(reggov, "blocked")
    ready = not bad_submission and not wiley_blocked and not blinded_not_ready and not reggov_blocked
    return row(
        "automated-artifact-build-and-package-gates",
        "ready" if ready else "blocked",
        (
            f"submissionGates={'; '.join(bad_submission) or 'ready'}; "
            f"wileyBlocked={len(wiley_blocked)}; "
            f"blindedNotReady={len(blinded_not_ready)}; "
            f"reggovBlocked={len(reggov_blocked)}"
        ),
        "Rerun make paper-artifacts-check after any source, paper, package, or readiness edit.",
    )


def package_surface_row(doi: dict[str, dict[str, str]]) -> dict[str, str]:
    package_paths = {
        "wiley-submission": SUBMISSION_ZIP,
        "blinded-review": BLINDED_REVIEW_ZIP,
        "doi-deposit": DOI_DEPOSIT_PACKAGE,
    }
    missing = [name for name, path in package_paths.items() if not path.exists()]
    corrupt = [name for name, path in package_paths.items() if path.exists() and not zip_ok(path)]
    doi_package_ready = doi.get("doi-deposit-package", {}).get("status") == "ready"
    ready = not missing and not corrupt and doi_package_ready
    return row(
        "package-surfaces",
        "ready" if ready else "blocked",
        (
            f"missing={','.join(missing) or 'none'}; "
            f"corrupt={','.join(corrupt) or 'none'}; "
            f"doiPackage={doi.get('doi-deposit-package', {}).get('status', 'missing')}"
        ),
        "Keep the Wiley submission ZIP, blinded review ZIP, and DOI handoff ZIP buildable and inspectable.",
    )


def claim_boundary_row(
    submission: dict[str, dict[str, str]],
    claim_dependency: dict[str, dict[str, str]],
    causal_targets: list[dict[str, str]],
) -> dict[str, str]:
    calibrated = submission.get("calibrated-policy-claims", {}).get("status", "missing")
    dependency = claim_dependency.get("calibrated-policy-simulation", {}).get("status", "missing")
    target_statuses = Counter(row.get("policyClaimStatus", "missing") for row in causal_targets)
    blocking_targets = sum(1 for item in causal_targets if item.get("blocksPolicySimulation") == "yes")
    ready = (
        calibrated == "blocked"
        and dependency == "not_cleared"
        and causal_targets
        and target_statuses.get("not_cleared", 0) == len(causal_targets)
        and blocking_targets == len(causal_targets)
    )
    return row(
        "calibrated-policy-claim-boundary",
        "ready" if ready else "blocked",
        (
            f"submissionCalibrated={calibrated}; "
            f"dependency={dependency}; "
            f"causalTargets={len(causal_targets)}; "
            f"policyClaimStatuses={dict(target_statuses)}; "
            f"blocksPolicySimulation={blocking_targets}"
        ),
        "Do not strengthen calibrated policy-effect language until causal targets and source-panel upgrades clear.",
    )


def source_product_boundary_row(
    leakage: dict[str, dict[str, str]],
    source_readiness: list[dict[str, str]],
) -> dict[str, str]:
    leakage_failures = [
        item for item, row_data in leakage.items() if row_data.get("status") != "pass"
    ]
    gate_counts = Counter(row.get("sourceProductGate", "missing") for row in source_readiness)
    ready_to_estimate = [
        row for row in source_readiness
        if row.get("sourceReadiness") == "ready_to_estimate"
        or row.get("sourceProductGate") == "ready_to_estimate"
    ]
    ready = not leakage_failures and source_readiness and not ready_to_estimate
    return row(
        "candidate-source-product-boundary",
        "ready" if ready else "blocked",
        (
            f"candidateLeakageFailures={len(leakage_failures)}; "
            f"sourceProductGates={dict(gate_counts)}; "
            f"readyToEstimateTargets={len(ready_to_estimate)}"
        ),
        "Keep candidate-only source products marked until manual adjudication promotes reviewed rows.",
    )


def reviewer_risk_row(reviewer: dict[str, dict[str, str]]) -> dict[str, str]:
    overall = reviewer.get("overall-reviewer-risk-posture", {})
    blocked = statuses_matching(reviewer, "blocked")
    empty_fields = []
    for risk_id, item in reviewer.items():
        for field in ("reviewerConcern", "evidence", "currentResponse", "claimBoundary", "nextAction"):
            if not item.get(field, "").strip():
                empty_fields.append(f"{risk_id}.{field}")
    ready = (
        overall.get("status") == "bounded_for_mechanism_review"
        and not blocked
        and not empty_fields
    )
    return row(
        "reviewer-risk-boundary",
        "ready" if ready else "blocked",
        (
            f"overall={overall.get('status', 'missing')}; "
            f"blockedRisks={len(blocked)}; "
            f"emptyFields={len(empty_fields)}"
        ),
        "Keep reviewer-facing objections mapped to evidence, claim boundaries, and unresolved actions.",
    )


def final_readthrough_evidence_row(final_evidence: dict[str, dict[str, str]]) -> dict[str, str]:
    blocked = statuses_matching(final_evidence, "blocked")
    status_counts = Counter(row.get("status", "missing") for row in final_evidence.values())
    overall = final_evidence.get("overall-final-readthrough-evidence", {})
    ready = (
        final_evidence
        and not blocked
        and overall.get("status") == "manual_required"
        and status_counts.get("automated_support_present", 0) > 0
    )
    return row(
        "final-readthrough-evidence-boundary",
        "ready" if ready else "blocked",
        (
            f"statusCounts={dict(status_counts)}; "
            f"overall={overall.get('status', 'missing')}; "
            f"blocked={len(blocked)}"
        ),
        "Use the automated evidence packet for human read-through; do not treat it as signoff.",
    )


def final_submission_boundary_row(
    submission: dict[str, dict[str, str]],
    doi: dict[str, dict[str, str]],
    reggov: dict[str, dict[str, str]],
) -> dict[str, str]:
    submission_final = submission.get("final-journal-submission", {}).get("status", "missing")
    doi_final = doi.get("final-journal-submission", {}).get("status", "missing")
    doi_record = doi.get("doi-record", {}).get("status", "missing")
    human = doi.get("human-readthrough", {}).get("status", "missing")
    live_author_page = reggov.get("live-reggov-author-page-refresh", {}).get("status", "missing")
    explicitly_manual = (
        submission_final == "manual_required"
        and doi_final == "manual_required"
        and (doi_record != "ready" or human != "ready" or live_author_page != "ready")
    )
    fully_ready = (
        submission_final == "ready"
        and doi_final == "ready"
        and doi_record == "ready"
        and human == "ready"
        and live_author_page == "ready"
    )
    ready = explicitly_manual or fully_ready
    return row(
        "final-journal-submission-boundary",
        "ready" if ready else "blocked",
        (
            f"submissionFinal={submission_final}; "
            f"doiFinal={doi_final}; "
            f"doiRecord={doi_record}; "
            f"humanReadthrough={human}; "
            f"liveAuthorPage={live_author_page}"
        ),
        "Leave final journal submission uncleared until DOI, human signoff, and same-day live author-page evidence are recorded.",
    )


def overall_row(rows: list[dict[str, str]]) -> dict[str, str]:
    blocked = [item for item in rows if item["status"] == "blocked"]
    return row(
        "overall-mechanism-review-circulation",
        "ready_for_mechanism_review" if not blocked else "blocked",
        f"checkedGates={len(rows)}; blocked={len(blocked)}",
        (
            "Circulate the package as a mechanism-review bundle only; calibrated policy-effect "
            "and final journal-submission claims remain outside the cleared posture."
        ),
    )


def row(gate: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def statuses_matching(rows: dict[str, dict[str, str]], status: str) -> list[str]:
    return [key for key, item in rows.items() if item.get("status") == status]


def zip_ok(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except (OSError, zipfile.BadZipFile):
        return False


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path) if row.get(key)}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        *RELEASE_METADATA_FIELDS,
        "gate",
        "status",
        "evidence",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]], metadata: dict[str, str]) -> str:
    overall = next(
        (row for row in rows if row["gate"] == "overall-mechanism-review-circulation"),
        {},
    )
    counts = Counter(row["status"] for row in rows)
    lines = [
        "# Mechanism-Review Circulation Readiness",
        "",
        "This generated audit consolidates the local automated evidence for mechanism-review circulation. It is not a DOI record, not a human scholarly signoff, and not a calibrated policy-effect clearance.",
        "",
        "## Summary",
        "",
        *metadata_summary_lines(metadata),
        f"- Status: `{overall.get('status', 'missing')}`",
        f"- Blocked gates: `{counts.get('blocked', 0)}`",
        "- Boundary: calibrated policy-effect claims remain blocked unless causal targets and source-panel upgrades clear.",
        "- Boundary: final journal-submission claims remain uncleared unless DOI deposit, human read-through signoff, and same-day external checklist evidence are recorded.",
        "- Mechanism-review condition: all automated artifact, build, packaging, and claim-boundary checks represented here are passing.",
        "",
        "## Gate Summary",
        "",
        "| Gate | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {gate} | {status} | {evidence} | {nextAction} |".format(
                gate=item["gate"],
                status=item["status"],
                evidence=item["evidence"],
                nextAction=item["nextAction"],
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this report after `make paper-artifacts-check` as the compact release-control surface for mechanism-review circulation. A `ready_for_mechanism_review` overall status means the local bundle is suitable for mechanism-model review under the stated evidence boundaries. It does not mean a journal submission is final, a DOI has been minted, or real-world calibrated reform effects have been estimated.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
