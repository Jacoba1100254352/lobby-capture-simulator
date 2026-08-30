#!/usr/bin/env python3
"""Write the substitution causal-upgrade handoff packet.

The packet consolidates the central substitution-elasticity first-wave target,
source products, manual-review blockers, and access-channel missingness. It is
a publication-control artifact, not source evidence.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import datetime
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
FIRST_WAVE_DIR = Path("data/calibration/first-wave")
TARGET_KEY = "substitution-elasticity"
OUTPUT_CSV = REPORTS / "substitution-causal-upgrade-packet.csv"
OUTPUT_MD = REPORTS / "substitution-causal-upgrade-packet.md"

PRODUCT_ORDER = [
    "substitution-reform-shocks",
    "actor-issue-time-spine",
    "substitution-comparison-groups",
    "meeting-log-or-missing-channel-note",
]

PRODUCT_DESIGN_ROLES = {
    "substitution-reform-shocks": {
        "role": "reform_shock_design_anchor",
        "causalUse": (
            "Defines the named HLOGA reform shock, affected actor and issue rules, "
            "comparison rule, and treatment date before any source-linked event "
            "study can be designed."
        ),
        "evidenceGateState": "schema_ready_design_anchor_not_effect_evidence",
        "promotionRequirement": (
            "Retain the HLOGA source provenance, but do not treat a dated reform "
            "row as effect evidence; the row is not observed substitution evidence; "
            "provision-specific treatment "
            "windows and matched actor-issue outcomes must be adjudicated first."
        ),
    },
    "actor-issue-time-spine": {
        "role": "cross_channel_outcome_spine",
        "causalUse": (
            "Normalizes actor, issue, period, venue, and activity rows across at "
            "least three venues so visible-channel movement can later be compared "
            "with alternate-channel activity."
        ),
        "evidenceGateState": "reviewed_treated_control_actor_time_panel_source_ready_not_effect_clearance",
        "promotionRequirement": (
            "The actor-time spine now preserves reviewed exact-ID source links, "
            "observed HLOGA pre/post treated LDA rows, and Colorado state-lobbying "
            "control rows. It is a source-ready design input, not effect evidence; "
            "estimation still requires the pre-specified model, falsification checks, "
            "sensitivity checks, and review before any claim upgrade."
        ),
    },
    "substitution-comparison-groups": {
        "role": "treated_and_comparison_assignment",
        "causalUse": (
            "Separates exposed, comparison, and excluded actors or jurisdictions "
            "around the named reform shock so substitution estimates are not just "
            "common-shock before/after contrasts."
        ),
        "evidenceGateState": "reviewed_treated_control_assignment_source_ready_not_effect_clearance",
        "promotionRequirement": (
            "The assignment file now separates treated federal LDA clients, "
            "Colorado unaffected-jurisdiction controls, and excluded rows with "
            "observed pre/post source windows. It clears the source-product design "
            "gate only; effect estimation and calibrated policy claims remain barred "
            "until model and falsification results are reviewed."
        ),
    },
    "meeting-log-or-missing-channel-note": {
        "role": "access_channel_missingness_boundary",
        "causalUse": (
            "Documents that private meeting/contact substitution remains mostly "
            "unobserved and must be excluded, bounded as latent access pressure, "
            "or proxied only under an explicit sensitivity design."
        ),
        "evidenceGateState": "missing_channel_design_note_not_estimation_panel",
        "promotionRequirement": (
            "Keep this as an omitted-channel boundary unless a broader machine-"
            "readable meeting/contact panel with actor, issue, date, source-record, "
            "completeness, and outcome linkage fields is added."
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
    estimation_rows = keyed_rows(REPORTS / "substitution-estimation-diagnostics.csv", "diagnosticId")

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
        estimation_rows,
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
            "make first-wave-source-products first-wave-source-readiness substitution-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check",
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
    estimation_rows: dict[str, dict[str, str]],
    metadata: dict[str, str],
) -> None:
    status_counts = Counter(row["sourceProductStatus"] for row in rows)
    candidate_count = sum(1 for row in rows if row["sourceProductStatus"] == "candidate_unreviewed")
    boundary_count = len(rows) - candidate_count
    leakage = leakage_rows.get("manual-adjudication-burden", {})
    triage = leakage_rows.get("candidate-review-triage", {})
    shock_window = shock_window_summary()
    historical_access = historical_source_access_summary()
    effect_gate = estimation_rows.get("overall_effect_model_and_falsification_gate", {})
    primary_estimate = estimation_rows.get("primary_actor_quarter_did", {})
    pretrend = estimation_rows.get("single_interval_pretrend_check", {})
    placebo = estimation_rows.get("clean_pre_hloga_2007q2_placebo", {})
    leave_one = estimation_rows.get("leave_one_actor_stability", {})
    lines = [
        "# Substitution Causal Upgrade Packet",
        "",
        "This generated packet consolidates the open substitution-elasticity causal-calibration target, HLOGA reform-shock anchor, reviewed exact-ID actor-time slice, treated/control comparison-assignment rows, meeting/contact missingness boundary, and remaining effect-estimation blockers. It is a handoff control, not effect evidence, and it does not clear calibrated policy-simulation or causal substitution-elasticity claims.",
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
        f"- Reviewed, design, or missing-channel boundary products, not effect evidence: `{boundary_count}`",
        f"- Effect-model and falsification gate: `{effect_gate.get('status', 'missing')}`",
        "- Overall claim boundary: `mechanism stress tests and qualitative substitution warnings only; no causal substitution-elasticity estimate clears from this packet`",
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
        "## Shock-Window Consistency",
        "",
        f"- Reform event: {shock_window['event']}",
        f"- Actor-time source window: {shock_window['actorWindow']}",
        f"- Actor-time pre/post coverage: {shock_window['actorCoverage']}",
        f"- Assignment coverage: {shock_window['assignmentCoverage']}",
        f"- Estimation consequence: {shock_window['consequence']}",
        f"- Historical source-access probe: {historical_access}",
        "",
        "## Effect-Model Diagnostic Result",
        "",
        f"- Overall diagnostic gate: `{effect_gate.get('status', 'missing')}`",
        f"- Primary descriptive contrast: estimate=`{primary_estimate.get('estimate', 'missing')}`; actor-bootstrap 95% interval=`[{primary_estimate.get('lower95', 'missing')}, {primary_estimate.get('upper95', 'missing')}]`; status=`{primary_estimate.get('status', 'missing')}`",
        f"- Pre-trend diagnostic: estimate=`{pretrend.get('estimate', 'missing')}`; status=`{pretrend.get('status', 'missing')}`",
        f"- Clean placebo diagnostic: estimate=`{placebo.get('estimate', 'missing')}`; status=`{placebo.get('status', 'missing')}`",
        f"- Leave-one-actor diagnostic: range=`[{leave_one.get('lower95', 'missing')}, {leave_one.get('upper95', 'missing')}]`; status=`{leave_one.get('status', 'missing')}`",
        "- Interpretation: the source-ready panel is sufficient to run the first descriptive estimator, but treatment/source confounding, incompatible outcome semantics, issue-code mismatch, two clean pre quarters, non-independent placebo evidence, interval uncertainty, and a leave-one-actor sign reversal keep the effect-model and falsification gates closed.",
        "- Detailed packet: `reports/substitution-estimation-diagnostics.md`",
        "- Claim consequence: `diagnostic preparation and failure-mode evidence only; no causal HLOGA effect or cross-channel substitution elasticity`",
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
            "## Candidate Leakage Boundary",
            "",
            f"- Manual-adjudication burden: {leakage.get('value', 'missing')}",
            f"- Candidate-review triage: {triage.get('value', 'missing')}",
            f"- Leakage boundary: {leakage.get('notes', 'candidate rows remain candidate-only worklists where still present')}",
            "- Interpretation: actor-issue-time rows now contain reviewed exact-ID source links plus observed treated and control pre/post rows, and comparison-group rows separate treated, control, and excluded assignments. They are source-ready design inputs, not effect estimates. The first estimator and falsification packet now exists, but its structural, pre-trend, placebo, uncertainty, and leave-one-actor gates do not clear effect or calibrated policy claims.",
            "",
            "## Access-Channel Missingness",
            "",
            "The meeting/contact note clears only a design-note requirement. It records that private or semi-private access is mostly unobserved, that the thin public meeting surface is not a representative contact-register panel, and that future substitution designs must compare excluded, latent, LDA-proxied, and thin-public-meeting sensitivity cases before any stronger claim.",
            "",
            "## Regeneration Rule",
            "",
            "After any source-product edit, rerun `make first-wave-source-products first-wave-source-readiness first-wave-manual-adjudication-plan substitution-estimation-diagnostics substitution-causal-upgrade-packet candidate-source-leakage-audit paper-artifacts-check`. A HLOGA reform-shock row, an actor-time refresh, or a comparison-group refresh is not enough unless the source-product, readiness, estimator, falsification, sensitivity, leakage, and artifact gates all pass.",
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


def shock_window_summary() -> dict[str, str]:
    shocks = read_csv(FIRST_WAVE_DIR / "substitution-reform-shocks.csv")
    actor_rows = read_csv(FIRST_WAVE_DIR / "actor-issue-time-spine.csv")
    comparison_rows = read_csv(FIRST_WAVE_DIR / "substitution-comparison-groups.csv")
    if not shocks:
        return {
            "event": "missing substitution reform-shock row",
            "actorWindow": "missing actor-issue-time spine",
            "actorCoverage": "no treatment date available",
            "assignmentCoverage": "no comparison-group rows available",
            "consequence": "source-product gate cannot clear until the reform shock, actor-time spine, and comparison groups are populated.",
        }

    shock = shocks[0]
    event_id = shock.get("reformEventId", "missing")
    treatment_start = parse_date(shock.get("treatmentStartDate", ""))
    event_label = f"{event_id} treatmentStartDate={shock.get('treatmentStartDate', 'missing')}"

    dated_actor_rows = []
    pre_rows = 0
    post_rows = 0
    if treatment_start is not None:
        for row in actor_rows:
            start = parse_date(row.get("periodStart", ""))
            end = parse_date(row.get("periodEnd", ""))
            if start is None or end is None:
                continue
            dated_actor_rows.append((start, end))
            if end < treatment_start:
                pre_rows += 1
            if start >= treatment_start:
                post_rows += 1

    if dated_actor_rows:
        actor_window = (
            f"{min(start for start, _ in dated_actor_rows).date().isoformat()} to "
            f"{max(end for _, end in dated_actor_rows).date().isoformat()} "
            f"({len(dated_actor_rows)} dated rows)"
        )
    else:
        actor_window = "no dated actor-issue-time rows"

    actor_coverage = f"preRows={pre_rows}; postRows={post_rows}"
    treated_rows = sum(
        1 for row in comparison_rows
        if any(token in row.get("comparisonGroup", "").lower() for token in ("treated", "treatment", "exposed"))
    )
    comparison_count = sum(
        1 for row in comparison_rows
        if any(token in row.get("comparisonGroup", "").lower() for token in ("comparison", "control", "unaffected"))
    )
    excluded_rows = sum(
        1 for row in comparison_rows
        if row.get("comparisonGroup", "").lower().startswith("excluded")
    )
    assignment_coverage = (
        f"treatedOrExposedRows={treated_rows}; comparisonOrControlRows={comparison_count}; "
        f"excludedRows={excluded_rows}"
    )
    if pre_rows and post_rows and treated_rows and comparison_count:
        consequence = (
            "shock-window and assignment scaffolds are present; estimation still depends on "
            "the source-readiness, leakage, falsification, and artifact gates."
        )
    else:
        consequence = (
            "the reviewed exact-ID slice is not an estimation panel because observed actor-time "
            "rows do not yet straddle the HLOGA treatment start with treated and comparison assignments."
        )
    return {
        "event": event_label,
        "actorWindow": actor_window,
        "actorCoverage": actor_coverage,
        "assignmentCoverage": assignment_coverage,
        "consequence": consequence,
    }


def historical_source_access_summary() -> str:
    rows = read_csv(REPORTS / "substitution-historical-source-access.csv")
    panel_rows = read_csv(REPORTS / "substitution-historical-lda-panel.csv")
    control_rows = read_csv(REPORTS / "substitution-state-lobbying-control-panel.csv")
    panel_text = ""
    if panel_rows:
        prepost_actors = sum(1 for row in panel_rows if row.get("status") == "prepost_source_rows")
        panel_source_rows = sum(int_or_zero(row.get("panelRows", "0")) for row in panel_rows)
        panel_pre_rows = sum(int_or_zero(row.get("preRows", "0")) for row in panel_rows)
        panel_post_rows = sum(int_or_zero(row.get("postRows", "0")) for row in panel_rows)
        panel_text = (
            f" Optional historical LDA panel: actors with pre/post rows={prepost_actors}, "
            f"panel rows={panel_source_rows}, preRows={panel_pre_rows}, postRows={panel_post_rows}; "
            "treated visible-lobbying source rows only."
        )
    control_text = ""
    if control_rows:
        prepost_controls = sum(1 for row in control_rows if row.get("status") == "prepost_control_source_rows")
        control_source_rows = sum(int_or_zero(row.get("sourceRows", "0")) for row in control_rows)
        control_pre_rows = sum(int_or_zero(row.get("preRows", "0")) for row in control_rows)
        control_post_rows = sum(int_or_zero(row.get("postRows", "0")) for row in control_rows)
        control_text = (
            f" Optional Colorado state-lobbying control panel: clients with pre/post rows={prepost_controls}, "
            f"panel rows={control_source_rows}, preRows={control_pre_rows}, postRows={control_post_rows}; "
            "unaffected-jurisdiction source rows only."
        )
    if not rows:
        return (
            "not run; optional live diagnostic target is "
            "`make substitution-historical-source-access`."
            + panel_text
            + control_text
        )
    status_counts = Counter(row.get("status", "missing") for row in rows)
    actor_rows = [row for row in rows if row.get("item") == "accepted-actor-lda-api-probe"]
    post_only = sum(1 for row in actor_rows if row.get("status") == "post_only_observed")
    prepost = sum(1 for row in actor_rows if row.get("status") == "prepost_probe_observed")
    api_counts = [row for row in rows if row.get("item") == "lda-api-period-count"]
    pre_count = sum(
        int_or_zero(row.get("observedCount", "0"))
        for row in api_counts
        if row.get("coverageRole") == "pre_hloga"
    )
    post_count = sum(
        int_or_zero(row.get("observedCount", "0"))
        for row in api_counts
        if row.get("coverageRole") == "post_hloga"
    )
    legacy_blocked = status_counts.get("blocked_host_unresolved", 0)
    return (
        f"ran optional live diagnostic; LDA API aggregate pre-HLOGA rows={pre_count}, "
        f"post-HLOGA rows={post_count}, accepted actor probes post-only={post_only}, "
        f"pre/post={prepost}, legacy Senate XML downloads blocked={legacy_blocked}. "
        "This is acquisition evidence only, not a source-product promotion."
        + panel_text
        + control_text
    )


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def shortfall(observed: str, minimum: str) -> str:
    try:
        return str(max(0, int(float(minimum or 0)) - int(float(observed or 0))))
    except ValueError:
        return ""


def int_or_zero(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def format_counts(counts: Counter[str]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def md(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
