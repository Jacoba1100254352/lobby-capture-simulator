#!/usr/bin/env python3
"""Write the venue-shifting causal-upgrade handoff packet.

The packet consolidates the venue-shifting first-wave target, reviewed exact-ID
entity-resolution slice, issue comparability blockers, false-match review
requirements, and no-linkage-clearance boundary. It is a publication-control
artifact, not effect evidence.
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
TARGET_KEY = "venue-shifting-detection-effect"
OUTPUT_CSV = REPORTS / "venue-causal-upgrade-packet.csv"
OUTPUT_MD = REPORTS / "venue-causal-upgrade-packet.md"

PRODUCT_ORDER = [
    "canonical-actor-identifiers",
    "alias-resolution-audit-sample",
    "issue-code-crosswalk",
    "false-match-review-log",
    "linked-actor-issue-venue-time",
]

PRODUCT_DESIGN_ROLES = {
    "canonical-actor-identifiers": {
        "role": "reviewed_exact_id_entity_resolution_spine",
        "causalUse": (
            "Would define canonical actors and source-system identifiers across "
            "LDA, FEC, docket, procurement, intermediary, and access-proxy rows."
        ),
        "evidenceGateState": "reviewed_identifier_spine_source_product_ready_not_effect_clearance",
        "promotionRequirement": (
            "The expanded exact-ID actor rows clear the canonical actor source-product "
            "minimum. Preserve source identifiers, source-system provenance, and "
            "parent/subsidiary ambiguity flags, then add a dated venue-shifting or "
            "detection shock plus outcome movement before treating the panel as effect "
            "evidence."
        ),
    },
    "alias-resolution-audit-sample": {
        "role": "reviewed_alias_audit_slice",
        "causalUse": (
            "Would document exact and fuzzy alias matches, manual accept/reject "
            "decisions, reviewer provenance, and source-record identifiers."
        ),
        "evidenceGateState": "reviewed_alias_audit_source_product_ready_not_effect_clearance",
        "promotionRequirement": (
            "The exact-ID alias rows carry reviewed decisions and reviewer/date "
            "provenance. They support the source-ready linkage panel, but full effect "
            "clearance still depends on a dated detection design, outcome movement, "
            "and falsification checks."
        ),
    },
    "issue-code-crosswalk": {
        "role": "issue_comparability_crosswalk",
        "causalUse": (
            "Would make lobbying issue codes, docket terms, procurement codes, and "
            "electoral-purpose terms comparable before cross-venue movement is read "
            "as substitution."
        ),
        "evidenceGateState": "reviewed_issue_taxonomy_crosswalk_source_product_ready_not_effect_clearance",
        "promotionRequirement": (
            "The reviewed issue crosswalk maps the exact-ID slice to LDA, docket, "
            "NAICS, PSC, and FEC purpose-term source families for comparability input, "
            "but it does not clear observed outcome movement or causal venue-shifting "
            "gates."
        ),
    },
    "false-match-review-log": {
        "role": "reviewed_false_positive_negative_linkage_audit",
        "causalUse": (
            "Would record accepted and rejected linkage examples, error types, "
            "confidence evidence, and notes needed to bound false-positive and "
            "false-negative linkage risk."
        ),
        "evidenceGateState": "reviewed_false_match_sample_source_product_ready_not_effect_clearance",
        "promotionRequirement": (
            "The sample includes accepted and rejected linkage examples and clears the "
            "source-product gate, but venue estimation remains blocked until a dated "
            "detection shock, outcome movement definition, and sensitivity design are "
            "specified."
        ),
    },
    "linked-actor-issue-venue-time": {
        "role": "reviewed_exact_id_linked_panel_slice",
        "causalUse": (
            "Would join canonical actors, comparable issues, venues, periods, "
            "activity measures, source systems, source records, and match "
            "confidence into an actor-issue-venue-time panel."
        ),
        "evidenceGateState": "reviewed_linked_panel_source_product_ready_not_effect_clearance",
        "promotionRequirement": (
            "The linked rows are reviewed exact-ID source records and clear the linked "
            "panel row threshold, but the panel still lacks a dated detection shock, "
            "observed outcome movement, and falsification structure required before "
            "venue-shifting estimates can be reported."
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
        "Strategic substitution mechanism",
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
            "make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan venue-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check",
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
    candidate_count = sum(1 for row in rows if row["sourceProductStatus"] == "candidate_unreviewed")
    leakage = leakage_rows.get("manual-adjudication-burden", {})
    triage = leakage_rows.get("candidate-review-triage", {})
    lines = [
        "# Venue Causal Upgrade Packet",
        "",
        "This generated packet consolidates the venue-shifting-detection causal-calibration target, reviewed exact-ID canonical actor identifiers, alias-resolution audit sample, issue-code crosswalk, false-match review log, linked actor-issue-venue-time slice, and remaining promotion requirements. It is a handoff control, not effect evidence, and it does not clear calibrated policy-simulation or causal venue-shifting claims.",
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
        f"- Candidate linkage products, not evidence: `{candidate_count}`",
        "- Overall claim boundary: `synthetic cross-venue detection diagnostics only; no causal venue-shifting or total-influence estimate clears from this packet`",
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
            "## Entity-Resolution Boundary",
            "",
            f"- Manual-adjudication burden: {leakage.get('value', 'missing')}",
            f"- Candidate-review triage: {triage.get('value', 'missing')}",
            f"- Source-product gate: {readiness.get('sourceProductGate', 'missing')}",
            "- Interpretation: the canonical actor, issue crosswalk, alias, false-match, and linked actor-issue-venue-time files now include reviewed exact-ID or taxonomy evidence and clear their source-product schema and row-count gates. This is still not observed venue-shifting effect evidence and cannot support cross-venue substitution, total-influence distortion, or calibrated policy-effect claims until a dated detection design, outcome movement, readiness, leakage, and artifact gates pass.",
            "",
            "## Issue-Comparability And False-Match Missingness",
            "",
            "The current linked panel is a reviewed exact-ID slice with a reviewed issue-taxonomy crosswalk, not a complete cross-venue estimation panel. Parent/subsidiary ambiguity, dated detection shocks, observed outcome movement, and broader venue coverage must still be expanded before venue-shifting estimates can be reported.",
            "",
            "## Regeneration Rule",
            "",
            "After any source-product edit, rerun `make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan venue-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check`. A refreshed identifier spine, alias sample, issue crosswalk, false-match log, or linked panel is not enough unless the source-product, readiness, manual-adjudication, leakage, and artifact gates all pass.",
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
