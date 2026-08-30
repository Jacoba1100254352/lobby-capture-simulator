#!/usr/bin/env python3
"""Write the comment causal-upgrade handoff packet.

The packet consolidates the rulemaking-comment first-wave target, source
products, response/final-rule linkage blocker, and no-uptake-clearance
boundary. It is a publication-control artifact, not source evidence.
"""

from __future__ import annotations

import csv
import sys
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


REPORTS = Path("reports")
TARGET_KEY = "comment-authenticity-and-uptake-effect"
OUTPUT_CSV = REPORTS / "comment-causal-upgrade-packet.csv"
OUTPUT_MD = REPORTS / "comment-causal-upgrade-packet.md"

PRODUCT_ORDER = [
    "comment-body-corpus",
    "duplicate-template-clusters",
    "agency-response-final-rule-linkage",
]

PRODUCT_DESIGN_ROLES = {
    "comment-body-corpus": {
        "role": "comment_text_corpus_not_uptake_evidence",
        "causalUse": (
            "Preserves comment text, submitter fields, posting dates, and source "
            "provenance for docket-record diagnostics before any duplicate, "
            "authenticity, or technical-content screen can be linked to outcomes."
        ),
        "evidenceGateState": "schema_ready_comment_corpus_not_effect_evidence",
        "promotionRequirement": (
            "Retain body text and source provenance, but do not treat the comment "
            "body corpus as agency response or final-rule movement evidence; body "
            "text alone is not agency response uptake evidence."
        ),
    },
    "duplicate-template-clusters": {
        "role": "duplicate_template_cluster_scaffold",
        "causalUse": (
            "Defines duplicate/template cluster assignments, duplicate scores, "
            "technical-content scores, and authenticity signals for mechanism "
            "diagnostics around comment flooding and triage."
        ),
        "evidenceGateState": "schema_ready_cluster_scaffold_not_effect_evidence",
        "promotionRequirement": (
            "Use reproducible duplicate/template and technical-content fields for "
            "mechanism diagnostics only until clusters are linked to response "
            "sections and final-rule text; the cluster scaffold is not uptake "
            "evidence."
        ),
    },
    "agency-response-final-rule-linkage": {
        "role": "response_and_final_rule_uptake_linkage",
        "causalUse": (
            "Would link comment and cluster units to response section identifiers, "
            "response text, final-rule identifiers, final-rule dates, uptake coding, "
            "and text-similarity fields."
        ),
        "evidenceGateState": "candidate_worklist_not_evidence",
        "promotionRequirement": (
            "Promote only after response section, final-rule, uptake coding, and "
            "text-similarity values are manually checked against source text with "
            "reviewer/date fields and all source-product, readiness, leakage, and "
            "artifact gates pass."
        ),
    },
}


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    metadata = release_metadata()
    target = find_row(read_csv(REPORTS / "causal-calibration-targets.csv"), "targetKey", TARGET_KEY)
    protocol = find_row(read_csv(REPORTS / "first-wave-causal-protocols.csv"), "targetKey", TARGET_KEY)
    readiness = find_row(read_csv(REPORTS / "first-wave-source-readiness.csv"), "targetKey", TARGET_KEY)
    dependency = find_row(
        read_csv(REPORTS / "claim-source-dependency.csv"),
        "claimFamily",
        "Rulemaking comments",
    )
    products = keyed_rows(REPORTS / "first-wave-source-products.csv", "productKey")
    manual_rows = keyed_rows(REPORTS / "first-wave-manual-adjudication-plan.csv", "productKey")
    leakage_rows = keyed_rows(REPORTS / "candidate-source-leakage-audit.csv", "item")

    packet_rows = [
        packet_row(
            product_key,
            products.get(product_key, {}),
            manual_rows.get(product_key, {}),
            target,
            protocol,
            readiness,
            dependency,
        )
        for product_key in PRODUCT_ORDER
    ]
    output_rows = with_release_metadata(packet_rows, metadata)
    write_csv(OUTPUT_CSV, output_rows)
    write_markdown(
        OUTPUT_MD,
        output_rows,
        target,
        protocol,
        readiness,
        dependency,
        leakage_rows,
        metadata,
    )
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {OUTPUT_MD}")
    return 0


def packet_row(
    product_key: str,
    product: dict[str, str],
    manual: dict[str, str],
    target: dict[str, str],
    protocol: dict[str, str],
    readiness: dict[str, str],
    dependency: dict[str, str],
) -> dict[str, str]:
    role = PRODUCT_DESIGN_ROLES[product_key]
    status = product.get("productStatus", "missing")
    candidate_rows = manual.get("candidateRows", "0") if status == "candidate_unreviewed" else "0"
    reviewed_rows = manual.get("reviewedRows", "0") if status == "candidate_unreviewed" else ""
    row_shortfall = manual.get("rowShortfall", "")
    if not row_shortfall:
        row_shortfall = shortfall(product.get("observedRows", ""), product.get("minimumRows", ""))
    return {
        "targetKey": TARGET_KEY,
        "targetStatus": target.get("status", "missing"),
        "policyClaimStatus": target.get("policyClaimStatus", "missing"),
        "blocksPolicySimulation": target.get("blocksPolicySimulation", "missing"),
        "protocolStatus": protocol.get("protocolStatus", "missing"),
        "sourceReadiness": readiness.get("sourceReadiness", "missing"),
        "sourceProductGate": readiness.get("sourceProductGate", "missing"),
        "productKey": product_key,
        "productLabel": product.get("productLabel", product_key),
        "designRole": role["role"],
        "sourceProductStatus": status,
        "evidenceGateState": role["evidenceGateState"],
        "observedRows": product.get("observedRows", ""),
        "minimumRows": product.get("minimumRows", ""),
        "rowShortfall": row_shortfall,
        "candidateRows": candidate_rows,
        "reviewedRows": reviewed_rows,
        "requiredLinkage": product.get("requiredColumns", ""),
        "acceptableSources": product.get("acceptableSources", ""),
        "causalDesignUse": role["causalUse"],
        "promotionRequirement": role["promotionRequirement"],
        "manualReviewFocus": manual.get("firstReviewBatchFocus", product.get("manualReviewChecklist", "")),
        "promotionBlockers": manual.get("promotionBlockers", product.get("validationNotes", "")),
        "promotionCommand": manual.get(
            "promotionCommand",
            "make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan comment-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check",
        ),
        "currentBoundedUse": readiness.get("claimBoundary", target.get("permittedUse", "")),
        "allowedCurrentClaim": target.get("allowedCurrentClaim", dependency.get("permittedUse", "")),
        "barredClaim": target.get("barredClaim", dependency.get("avoidClaim", "")),
        "claimUpgradeTrigger": target.get("claimUpgradeTrigger", protocol.get("clearanceCriterion", "")),
        "clearanceCriterion": protocol.get("clearanceCriterion", target.get("clearanceCriterion", "")),
        "claimBoundary": product.get("claimBoundary", readiness.get("claimBoundary", "")),
        "nextAction": product.get("nextAction", target.get("nextAction", "")),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        *RELEASE_METADATA_FIELDS,
        "targetKey",
        "targetStatus",
        "policyClaimStatus",
        "blocksPolicySimulation",
        "protocolStatus",
        "sourceReadiness",
        "sourceProductGate",
        "productKey",
        "productLabel",
        "designRole",
        "sourceProductStatus",
        "evidenceGateState",
        "observedRows",
        "minimumRows",
        "rowShortfall",
        "candidateRows",
        "reviewedRows",
        "requiredLinkage",
        "acceptableSources",
        "causalDesignUse",
        "promotionRequirement",
        "manualReviewFocus",
        "promotionBlockers",
        "promotionCommand",
        "currentBoundedUse",
        "allowedCurrentClaim",
        "barredClaim",
        "claimUpgradeTrigger",
        "clearanceCriterion",
        "claimBoundary",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    target: dict[str, str],
    protocol: dict[str, str],
    readiness: dict[str, str],
    dependency: dict[str, str],
    leakage_rows: dict[str, dict[str, str]],
    metadata: dict[str, str],
) -> None:
    status_counts = Counter(row["sourceProductStatus"] for row in rows)
    candidate_count = sum(1 for row in rows if row["evidenceGateState"] == "candidate_worklist_not_evidence")
    schema_boundary_count = len(rows) - candidate_count
    leakage = leakage_rows.get("manual-adjudication-burden", {})
    triage = leakage_rows.get("candidate-review-triage", {})
    lines = [
        "# Comment Causal Upgrade Packet",
        "",
        "This generated packet consolidates the comment-authenticity-and-uptake causal-calibration target, comment-body corpus, duplicate/template cluster assignments, agency response text and final-rule linkage blocker, and manual promotion requirements. It is a handoff control, not source evidence, and it does not clear calibrated policy-simulation or causal comment-uptake claims.",
        "",
        "## Summary",
        "",
        *metadata_summary_lines(metadata),
        f"- Target: `{TARGET_KEY}`",
        f"- Target status: `{target.get('status', 'missing')}`",
        f"- Policy-claim status: `{target.get('policyClaimStatus', 'missing')}`",
        f"- Blocks calibrated policy simulation: `{target.get('blocksPolicySimulation', 'missing')}`",
        f"- Protocol status: `{protocol.get('protocolStatus', 'missing')}`",
        f"- Source readiness: `{readiness.get('sourceReadiness', 'missing')}`",
        f"- Source-product gate: `{readiness.get('sourceProductGate', 'missing')}`",
        f"- Source-product statuses: `{format_counts(status_counts)}`",
        f"- Candidate linkage worklists, not evidence: `{candidate_count}`",
        f"- Schema-ready corpus or cluster scaffolds, not uptake evidence: `{schema_boundary_count}`",
        "- Overall claim boundary: `comment-record and mechanism diagnostics only; no causal comment-authenticity or agency-uptake estimate clears from this packet`",
        "",
        "## Current Claim Boundary",
        "",
        f"- Current support: {target.get('currentSupport', 'missing')}",
        f"- Permitted use: {target.get('permittedUse', dependency.get('permittedUse', 'missing'))}",
        f"- Allowed current claim: {target.get('allowedCurrentClaim', 'missing')}",
        f"- Barred claim: {target.get('barredClaim', dependency.get('avoidClaim', 'missing'))}",
        f"- Claim-upgrade trigger: {target.get('claimUpgradeTrigger', protocol.get('clearanceCriterion', 'missing'))}",
        f"- Clearance criterion: {protocol.get('clearanceCriterion', target.get('clearanceCriterion', 'missing'))}",
        "",
        "## Causal Design Requirements",
        "",
        f"- Unit of analysis: {protocol.get('unitOfAnalysis', 'missing')}",
        f"- Treatment or shock: {protocol.get('treatmentOrShock', 'missing')}",
        f"- Comparison design: {protocol.get('comparisonDesign', 'missing')}",
        f"- Primary outcomes: {protocol.get('primaryOutcomes', 'missing')}",
        f"- Linkage keys: {protocol.get('linkageKeys', 'missing')}",
        f"- Minimum sources: {protocol.get('minimumSources', 'missing')}",
        f"- Falsification checks: {protocol.get('falsificationChecks', 'missing')}",
        f"- Sensitivity checks: {protocol.get('sensitivityChecks', 'missing')}",
        f"- Threat model: {protocol.get('threatModel', 'missing')}",
        "",
        "## Promotion Dependency Matrix",
        "",
        "| Product | Design role | Status | Rows | Shortfall | Evidence gate | Required linkage | Promotion requirement |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {productLabel} | {designRole} | {sourceProductStatus} | {observedRows} | {rowShortfall} | {evidenceGateState} | {requiredLinkage} | {promotionRequirement} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Manual Review Queue",
            "",
            "| Product | Candidate rows | Reviewed rows | First review focus | Promotion blockers |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {productLabel} | {candidateRows} | {reviewedRows} | {manualReviewFocus} | {promotionBlockers} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Candidate Linkage Boundary",
            "",
            f"- Manual-adjudication burden: {leakage.get('value', 'missing')}",
            f"- Candidate-review triage: {triage.get('value', 'missing')}",
            f"- Source-product gate: {readiness.get('sourceProductGate', 'missing')}",
            "- Interpretation: the agency response text and final-rule linkage file is a candidate worklist, not observed agency uptake evidence. Comment-body corpus and duplicate/template cluster assignments support comment-record and mechanism diagnostics only.",
            "",
            "## Response And Final-Rule Missingness",
            "",
            "The current response/final-rule linkage is not a causal uptake panel. It has candidate response sections, final-rule identifiers, uptake codes, and text-similarity fields that must be adjudicated against source text before any estimate of agency-response uptake, final-rule movement, or review burden can be reported.",
            "",
            "## Regeneration Rule",
            "",
            "After any source-product edit, rerun `make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan comment-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check`. A comment corpus refresh, duplicate/template cluster refresh, or candidate response/final-rule refresh is not enough unless the source-product, readiness, manual-adjudication, leakage, and artifact gates all pass.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in read_csv(path) if row.get(key)}


def find_row(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    for row in rows:
        if row.get(key) == value:
            return row
    return {}


def shortfall(observed: str, minimum: str) -> str:
    try:
        return str(max(0, int(float(minimum or 0)) - int(float(observed or 0))))
    except ValueError:
        return ""


def format_counts(counts: Counter[str]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def md(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
