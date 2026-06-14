#!/usr/bin/env python3
"""Map first-wave causal protocols to current source-product readiness."""

from __future__ import annotations

import csv
from pathlib import Path


REPORTS = Path("reports")
PROTOCOLS = REPORTS / "first-wave-causal-protocols.csv"
SOURCE_CAPABILITIES = REPORTS / "source-capability-audit.csv"
SOURCE_PANELS = REPORTS / "source-panel-inventory.csv"
SOURCE_MOMENTS = REPORTS / "source-moments.csv"
PROCUREMENT_REFRESH = REPORTS / "procurement-refresh-readiness.csv"


TARGET_ORDER = [
    "substitution-elasticity",
    "procurement-modification-causal-capture",
    "comment-authenticity-and-uptake-effect",
    "venue-shifting-detection-effect",
]


def main() -> int:
    protocols = keyed_rows(PROTOCOLS, "targetKey")
    capabilities = keyed_rows(SOURCE_CAPABILITIES, "capability")
    panels = keyed_rows(SOURCE_PANELS, "panel")
    moments = source_moments(SOURCE_MOMENTS)
    procurement = keyed_rows(PROCUREMENT_REFRESH, "item")

    rows = [
        readiness_row(target, protocols, capabilities, panels, moments, procurement)
        for target in TARGET_ORDER
        if target in protocols
    ]
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "first-wave-source-readiness.csv", rows)
    write_markdown(REPORTS / "first-wave-source-readiness.md", rows)
    print("Wrote reports/first-wave-source-readiness.csv")
    print("Wrote reports/first-wave-source-readiness.md")
    return 0


def keyed_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get(key, ""): row for row in csv.DictReader(source)}


def source_moments(path: Path) -> dict[str, dict[str, str]]:
    moments: dict[str, dict[str, str]] = {}
    if not path.exists():
        return moments
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            metric = row.get("metric", "")
            if not metric:
                continue
            if metric not in moments:
                moments[metric] = row
            elif row.get("scope") == "snapshot" and moments[metric].get("scope") != "snapshot":
                moments[metric] = row
    return moments


def readiness_row(
    target: str,
    protocols: dict[str, dict[str, str]],
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
) -> dict[str, str]:
    builders = {
        "substitution-elasticity": substitution_row,
        "procurement-modification-causal-capture": procurement_row,
        "comment-authenticity-and-uptake-effect": comment_row,
        "venue-shifting-detection-effect": venue_row,
    }
    row = builders[target](capabilities, panels, moments, procurement)
    protocol = protocols[target]
    return {
        "targetKey": target,
        "protocolStatus": protocol.get("protocolStatus", ""),
        "sourceReadiness": row["sourceReadiness"],
        "currentSourceProducts": row["currentSourceProducts"],
        "boundedOrProxySupport": row["boundedOrProxySupport"],
        "missingSourceProducts": row["missingSourceProducts"],
        "blockingIssue": row["blockingIssue"],
        "claimBoundary": row["claimBoundary"],
        "nextAction": row["nextAction"],
    }


def substitution_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
) -> dict[str, str]:
    return {
        "sourceReadiness": "partial_source_support_not_estimation_ready",
        "currentSourceProducts": "; ".join([
            metric_text(moments, "ldaRows", "LDA visible-lobbying rows"),
            metric_text(moments, "outsideSpendingRows", "OpenFEC outside-spending rows"),
            metric_text(moments, "electoralCommunicationRows", "OpenFEC electoral-communication rows"),
            metric_text(moments, "regulatoryRows", "Regulations.gov/Federal Register rows"),
            metric_text(moments, "procurementActionRows", "USAspending action rows"),
            metric_text(moments, "intermediaryRows", "intermediary rows"),
        ]),
        "boundedOrProxySupport": "; ".join([
            panel_text(panels, "Direct dark money"),
            panel_text(panels, "Intermediaries"),
            panel_text(panels, "Revolving door"),
        ]),
        "missingSourceProducts": "; ".join([
            "named reform-shock event file",
            "canonical actor-issue-time spine across at least three venues",
            "pre/post comparison groups for exposed and unaffected actors or jurisdictions",
            "meeting-log or contact-register panel, or an explicit missing-channel design note",
        ]),
        "blockingIssue": "Public surfaces exist, but the committed snapshot does not yet define an event panel that can estimate substitution elasticity.",
        "claimBoundary": "May guide a source-anchored substitution design; does not validate hidden-channel magnitudes or causal substitution effects.",
        "nextAction": "Choose one named reform shock, build the actor-issue-time linkage file, and record exposed plus comparison actors before inspecting outcome movement.",
    }


def procurement_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
) -> dict[str, str]:
    sam_capability = capabilities.get("sam-contract-awards-action-history", {})
    representative_sam = procurement.get("representative-sam-fpds-action-history", {})
    return {
        "sourceReadiness": "blocked_by_sam_fps_crosswalk_and_overlays",
        "currentSourceProducts": "; ".join([
            metric_text(moments, "procurementBulkTransactionRows", "USAspending bulk transaction rows"),
            metric_text(moments, "procurementActionRows", "USAspending action rows"),
            metric_text(moments, "procurementKnownPiidShare", "known PIID share"),
            metric_text(moments, "procurementExPostModificationShare", "ex-post modification share"),
            metric_text(moments, "procurementSingleBidShare", "single-bid share"),
        ]),
        "boundedOrProxySupport": "; ".join([
            capability_text(sam_capability),
            status_text("representative SAM/FPDS action history", representative_sam.get("status", "")),
        ]),
        "missingSourceProducts": "; ".join([
            "SAM/FPDS action-history export or keyed pull",
            "USAspending-to-SAM modification-code crosswalk",
            "GAO protest overlay",
            "SAM exclusion overlay",
            "procurement firewall or integrity-control overlay",
        ]),
        "blockingIssue": "USAspending denominators are present, but representative SAM/FPDS coding and protest/exclusion/firewall overlays remain absent.",
        "claimBoundary": "Supports procurement denominator and stress diagnostics only; does not support causal procurement-modification capture claims.",
        "nextAction": "Normalize a SAM/FPDS export through the existing importer, then reconcile modification fields against USAspending before adding protest, exclusion, and firewall overlays.",
    }


def comment_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
) -> dict[str, str]:
    return {
        "sourceReadiness": "partial_source_support_not_estimation_ready",
        "currentSourceProducts": "; ".join([
            metric_text(moments, "regulatoryRows", "Regulations.gov/Federal Register rows"),
            metric_text(moments, "commentTemplateShareMean", "mean template share"),
            metric_text(moments, "commentAuthenticationShareMean", "mean authentication share"),
            metric_text(moments, "commentFloodingIndex", "comment-flooding index"),
        ]),
        "boundedOrProxySupport": (
            "Rulemaking comments: source-moment-only "
            f"({metric_text(moments, 'regulatoryRows', 'regulatory rows')}; no separate source-panel row)"
        ),
        "missingSourceProducts": "; ".join([
            "comment-body corpus",
            "duplicate/template cluster assignments",
            "submitter authenticity fields where available",
            "agency response text",
            "final-rule text linkage",
            "treated/untreated or before/after docket marker",
        ]),
        "blockingIssue": "Docket schema and volume moments exist, but body-level duplicate clusters and agency-response uptake links are not yet committed.",
        "claimBoundary": "Supports rulemaking information-distortion design and source moments only; does not estimate comment-authenticity effects.",
        "nextAction": "Select a docket family, archive comment bodies and duplicate clusters, then link comments to response sections and final-rule text before estimating uptake.",
    }


def venue_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
) -> dict[str, str]:
    return {
        "sourceReadiness": "partial_identifier_support_not_linkage_ready",
        "currentSourceProducts": "; ".join([
            metric_text(moments, "ldaRows", "LDA rows"),
            metric_text(moments, "fecRows", "FEC rows"),
            metric_text(moments, "regulatoryRows", "docket rows"),
            metric_text(moments, "procurementActionRows", "procurement action rows"),
            metric_text(moments, "intermediaryRows", "intermediary rows"),
            metric_text(moments, "revolvingDoorRows", "revolving-door proxy rows"),
        ]),
        "boundedOrProxySupport": "; ".join([
            panel_text(panels, "Direct dark money"),
            panel_text(panels, "Intermediaries"),
            panel_text(panels, "Revolving door"),
        ]),
        "missingSourceProducts": "; ".join([
            "canonical actor identifier table",
            "alias-resolution rules and manual audit sample",
            "issue-code crosswalk across venues",
            "false-positive and false-negative review log",
            "linked actor-issue-venue-time output table",
        ]),
        "blockingIssue": "Multiple public surfaces are present, but the committed snapshot lacks an audited entity-resolution spine.",
        "claimBoundary": "Can support a detection-measurement workplan; cannot prove venue shifting changed outcomes.",
        "nextAction": "Build an alias table linking LDA clients, FEC spenders, docket submitters, vendors, intermediaries, and access proxies, then audit false matches before promoting the panel.",
    }


def metric_text(moments: dict[str, dict[str, str]], metric: str, label: str) -> str:
    row = moments.get(metric, {})
    value = row.get("value", "")
    if not value:
        return f"{label}=missing"
    return f"{label}={format_number(value)}"


def panel_text(panels: dict[str, dict[str, str]], panel: str) -> str:
    row = panels.get(panel, {})
    if not row:
        return f"{panel}: missing"
    return (
        f"{panel}: {row.get('supportLevel', 'unknown')} "
        f"({row.get('status', 'unknown')}; {row.get('metric', 'metric')}={format_number(row.get('value', ''))})"
    )


def capability_text(row: dict[str, str]) -> str:
    if not row:
        return "SAM/FPDS capability: missing"
    return (
        f"{row.get('capability', 'capability')}: {row.get('capabilityStatus', 'unknown')} "
        f"(snapshotRows={format_number(row.get('snapshotRows', ''))})"
    )


def status_text(label: str, status: str) -> str:
    return f"{label}: {status or 'missing'}"


def format_number(value: str) -> str:
    if value == "":
        return "missing"
    try:
        number = float(value)
    except ValueError:
        return value
    if number.is_integer():
        return str(int(number))
    return f"{number:.4f}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "targetKey",
        "protocolStatus",
        "sourceReadiness",
        "currentSourceProducts",
        "boundedOrProxySupport",
        "missingSourceProducts",
        "blockingIssue",
        "claimBoundary",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    ready = [row for row in rows if row["sourceReadiness"] == "ready_to_estimate"]
    blocked = [row for row in rows if row["sourceReadiness"].startswith("blocked")]
    partial = [row for row in rows if row not in ready and row not in blocked]
    lines = [
        "# First-Wave Source Readiness",
        "",
        "This audit maps the first-wave causal protocols to committed source products. It is a pre-estimation gate: source products can support protocol design, but no row clears calibrated policy-simulation claims or causal effect language.",
        "",
        "## Summary",
        "",
        f"- Protocols audited: `{len(rows)}`",
        f"- Ready to estimate: `{len(ready)}`",
        f"- Partial source support: `{len(partial)}`",
        f"- Blocked by missing source products: `{len(blocked)}`",
        "- Policy-simulation status: `not_cleared`",
        "",
        "## Readiness Matrix",
        "",
        "| Target | Source readiness | Current source products | Missing source products | Blocking issue |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {targetKey} | {sourceReadiness} | {currentSourceProducts} | {missingSourceProducts} | {blockingIssue} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Boundaries and Next Actions",
        "",
        "| Target | Bounded or proxy support | Claim boundary | Next action |",
        "| --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {targetKey} | {boundedOrProxySupport} | {claimBoundary} | {nextAction} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
