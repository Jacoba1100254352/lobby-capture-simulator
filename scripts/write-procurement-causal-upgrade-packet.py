#!/usr/bin/env python3
"""Write the procurement causal-upgrade handoff packet.

The packet consolidates the procurement-specific first-wave target, source
products, acquisition tasks, manual-review blockers, and denominator caveats.
It is a publication-control artifact, not source evidence.
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
TARGET_KEY = "procurement-modification-causal-capture"
OUTPUT_CSV = REPORTS / "procurement-causal-upgrade-packet.csv"
OUTPUT_MD = REPORTS / "procurement-causal-upgrade-packet.md"

PRODUCT_ORDER = [
    "sam-fpds-action-history-crosswalk",
    "procurement-offer-competition-enrichment",
    "gao-protest-overlay",
    "sam-exclusion-overlay",
    "procurement-firewall-overlay",
]

PRODUCT_DESIGN_ROLES = {
    "sam-fpds-action-history-crosswalk": {
        "role": "outcome_panel_and_coding_crosswalk",
        "causalUse": (
            "Defines post-award action timing, modification coding, obligation "
            "changes, and source-system record linkage before modification rows "
            "can be treated as outcomes."
        ),
        "promotionRequirement": (
            "Promote only after a reviewed SAM/FPDS or Contract Awards action-history "
            "panel is reconciled to USAspending identifiers and clears source-product, "
            "source-readiness, manual-adjudication, leakage, and artifact gates."
        ),
    },
    "procurement-offer-competition-enrichment": {
        "role": "competition_control_and_stratification",
        "causalUse": (
            "Supplies competition and offer-count controls so modification, protest, "
            "and firewall diagnostics are not confounded with award competitiveness."
        ),
        "promotionRequirement": (
            "Promote only after the source-product gate sees source competition and "
            "offer-count fields populated with PIID/UEI linkage, source-system "
            "provenance, broad row coverage, and crosswalk confidence."
        ),
    },
    "gao-protest-overlay": {
        "role": "integrity_outcome_overlay",
        "causalUse": (
            "Adds observed dispute outcomes and issue coding that can be linked to "
            "award/action rows as procurement-integrity outcomes or controls."
        ),
        "promotionRequirement": (
            "Promote only after the source-product gate sees GAO decision rows "
            "reviewed against source pages or PDFs and linked to agency, vendor, "
            "PIID/UEI where possible, dates, outcome, issue codes, and source URL."
        ),
    },
    "sam-exclusion-overlay": {
        "role": "integrity_enforcement_overlay",
        "causalUse": (
            "Separates vendor exclusion or debarment status from modification and "
            "protest outcomes so integrity-enforcement exposure is explicit."
        ),
        "promotionRequirement": (
            "Promote only after the source-product gate sees reviewed SAM exclusion "
            "rows carrying UEI, recipient, exclusion type, start/end dates, excluding "
            "agency, source provenance, and reviewer/date evidence where required."
        ),
    },
    "procurement-firewall-overlay": {
        "role": "institutional_control_overlay",
        "causalUse": (
            "Encodes dated procurement-integrity controls and covered-official rules "
            "for use as institutional-control exposure, not as compliance evidence."
        ),
        "promotionRequirement": (
            "The committed EPAAR row is schema-ready but bounded to EPA control-design "
            "evidence; broader agency firewall coverage still requires dated official "
            "policy rows before it can support a panel design."
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
        "Procurement modification capture",
    )
    source_products = keyed_rows(REPORTS / "first-wave-source-products.csv", "productKey")
    acquisition_rows = keyed_rows(REPORTS / "first-wave-procurement-source-acquisition.csv", "productKey")
    manual_rows = keyed_rows(REPORTS / "first-wave-manual-adjudication-plan.csv", "productKey")
    denominator_rows = read_csv(REPORTS / "procurement-denominator-audit.csv")
    composition_rows = read_csv(REPORTS / "procurement-modification-composition-audit.csv")

    packet_rows = [
        packet_row(
            product_key,
            source_products.get(product_key, {}),
            acquisition_rows.get(product_key, {}),
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
        denominator_rows,
        composition_rows,
        metadata,
    )
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {OUTPUT_MD}")
    return 0


def packet_row(
    product_key: str,
    product: dict[str, str],
    acquisition: dict[str, str],
    manual: dict[str, str],
    target: dict[str, str],
    protocol: dict[str, str],
    readiness: dict[str, str],
    dependency: dict[str, str],
) -> dict[str, str]:
    role = PRODUCT_DESIGN_ROLES[product_key]
    product_status = product.get("productStatus") or acquisition.get("sourceProductStatus") or "missing"
    candidate_rows = manual.get("candidateRows", "0") if product_status == "candidate_unreviewed" else "0"
    reviewed_rows = manual.get("reviewedRows", "0") if product_status == "candidate_unreviewed" else ""
    row_shortfall = manual.get("rowShortfall", "")
    if not row_shortfall:
        row_shortfall = shortfall(product.get("observedRows", ""), product.get("minimumRows", ""))
    gate_state = (
        "schema_ready_bounded_control"
        if product_key == "procurement-firewall-overlay" and product_status == "schema_ready"
        else "candidate_worklist_not_evidence"
    )
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
        "sourceProductStatus": product_status,
        "evidenceGateState": gate_state,
        "observedRows": product.get("observedRows", ""),
        "minimumRows": product.get("minimumRows", acquisition.get("minimumRows", "")),
        "rowShortfall": row_shortfall,
        "candidateRows": candidate_rows,
        "reviewedRows": reviewed_rows,
        "requiredLinkage": acquisition.get("requiredLinkage", product.get("requiredColumns", "")),
        "sourceSurface": official_surface(acquisition),
        "causalDesignUse": role["causalUse"],
        "promotionRequirement": role["promotionRequirement"],
        "manualReviewFocus": manual.get("firstReviewBatchFocus", product.get("manualReviewChecklist", "")),
        "promotionBlockers": manual.get("promotionBlockers", acquisition.get("currentBlocker", "")),
        "promotionCommand": manual.get(
            "promotionCommand",
            "make first-wave-source-products first-wave-source-readiness procurement-causal-upgrade-packet paper-artifacts-check",
        ),
        "currentBoundedUse": readiness.get("claimBoundary", target.get("permittedUse", "")),
        "allowedCurrentClaim": target.get("allowedCurrentClaim", dependency.get("permittedUse", "")),
        "barredClaim": target.get("barredClaim", dependency.get("avoidClaim", "")),
        "claimUpgradeTrigger": target.get("claimUpgradeTrigger", protocol.get("clearanceCriterion", "")),
        "clearanceCriterion": protocol.get("clearanceCriterion", target.get("clearanceCriterion", "")),
        "claimBoundary": product.get("claimBoundary", acquisition.get("claimBoundary", "")),
        "nextAction": acquisition.get("acquisitionStep", product.get("nextAction", target.get("nextAction", ""))),
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
        "sourceSurface",
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
    denominator_rows: list[dict[str, str]],
    composition_rows: list[dict[str, str]],
    metadata: dict[str, str],
) -> None:
    status_counts = Counter(row["sourceProductStatus"] for row in rows)
    candidate_count = sum(1 for row in rows if row["evidenceGateState"] == "candidate_worklist_not_evidence")
    bounded_control_count = sum(1 for row in rows if row["evidenceGateState"] == "schema_ready_bounded_control")
    lines = [
        "# Procurement Causal Upgrade Packet",
        "",
        "This generated packet consolidates the open procurement-modification causal-calibration target, first-wave source products, source-acquisition instructions, manual-adjudication blockers, and denominator caveats. It is a handoff control, not source evidence, and it does not clear calibrated policy-simulation or causal procurement-capture claims.",
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
        f"- Candidate worklists, not evidence: `{candidate_count}`",
        f"- Schema-ready bounded controls: `{bounded_control_count}`",
        "- Overall claim boundary: `denominator-mapped procurement diagnostics only; no causal procurement-modification capture estimate clears from this packet`",
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
            "## Denominator Separation",
            "",
            "The denominator and composition audits remain separate from causal calibration. USAspending action and bulk rows support bounded distributional diagnostics; they do not become a SAM/FPDS-calibrated causal panel without the product promotions above.",
            "",
            "| Source | Status | Role | Rows | Modified action share | Modified award share | Amount-weighted modified share | Competition known | Promotion | Boundary |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in denominator_rows:
        if row.get("source") not in {
            "usaspending-procurement-actions",
            "usaspending-procurement-bulk-summary",
            "sam-contract-awards",
        }:
            continue
        lines.append(
            "| {source} | {snapshotStatus} | {role} | {rows} | {modifiedActionShare} | {modifiedAwardShare} | {amountWeightedModificationShare} | {knownCompetitionShare} | {promotionReadiness} | {claimBoundary} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Composition Caveat",
            "",
            composition_caveat(composition_rows),
            "",
            "## Regeneration Rule",
            "",
            "After any source-product edit, rerun `make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan procurement-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check`. A successful source download, SAM export audit, or candidate overlay refresh is not enough unless the source-product, readiness, manual-adjudication, leakage, and artifact gates all pass.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def composition_caveat(rows: list[dict[str, str]]) -> str:
    by_source = {
        row.get("source", ""): row
        for row in rows
        if row.get("groupType") == "source"
    }
    action = by_source.get("usaspending-procurement-actions", {})
    bulk = by_source.get("usaspending-procurement-bulk-summary", {})
    sam = by_source.get("sam-contract-awards", {})
    return (
        "Current composition diagnostics report separate source routes: "
        f"USAspending action rows have modified-action share {action.get('modifiedActionShare', 'missing')} "
        f"and amount-weighted modified share {action.get('amountWeightedModificationShare', 'missing')}; "
        f"the archived USAspending bulk summary has modified-action share {bulk.get('modifiedActionShare', 'missing')} "
        f"and amount-weighted modified share {bulk.get('amountWeightedModificationShare', 'missing')}; "
        f"SAM.gov Contract Awards has {sam.get('rows', '0')} committed rows. These route-specific figures remain "
        "denominator diagnostics, not causal capture estimates."
    )


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


def official_surface(row: dict[str, str]) -> str:
    source = row.get("preferredOfficialSource", "")
    url = row.get("officialSourceUrl", "")
    return f"{source} ({url})" if source and url else source or url


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
