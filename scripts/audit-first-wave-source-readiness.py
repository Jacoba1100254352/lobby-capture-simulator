#!/usr/bin/env python3
"""Map first-wave causal protocols to current source-product readiness."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPORTS = Path("reports")
PROTOCOLS = REPORTS / "first-wave-causal-protocols.csv"
SOURCE_CAPABILITIES = REPORTS / "source-capability-audit.csv"
SOURCE_PANELS = REPORTS / "source-panel-inventory.csv"
SOURCE_MOMENTS = REPORTS / "source-moments.csv"
PROCUREMENT_REFRESH = REPORTS / "procurement-refresh-readiness.csv"
SOURCE_PRODUCTS = REPORTS / "first-wave-source-products.csv"
LINKAGE_CANDIDATES = REPORTS / "first-wave-linkage-candidates.csv"


TARGET_ORDER = [
    "substitution-elasticity",
    "procurement-modification-causal-capture",
    "comment-authenticity-and-uptake-effect",
    "venue-shifting-detection-effect",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    protocols = keyed_rows(args.reports / PROTOCOLS.name, "targetKey")
    capabilities = keyed_rows(args.reports / SOURCE_CAPABILITIES.name, "capability")
    panels = keyed_rows(args.reports / SOURCE_PANELS.name, "panel")
    moments = source_moments(args.reports / SOURCE_MOMENTS.name)
    procurement = keyed_rows(args.reports / PROCUREMENT_REFRESH.name, "item")
    products = product_rows(args.reports / SOURCE_PRODUCTS.name)
    linkage = linkage_candidate_summary(args.reports / LINKAGE_CANDIDATES.name)

    rows = [
        readiness_row(target, protocols, capabilities, panels, moments, procurement, products, linkage)
        for target in TARGET_ORDER
        if target in protocols
    ]
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "first-wave-source-readiness.csv", rows)
    write_markdown(args.reports / "first-wave-source-readiness.md", rows)
    print(f"Wrote {args.reports / 'first-wave-source-readiness.csv'}")
    print(f"Wrote {args.reports / 'first-wave-source-readiness.md'}")
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


def product_rows(path: Path) -> dict[str, list[dict[str, str]]]:
    products: dict[str, list[dict[str, str]]] = {}
    if not path.exists():
        return products
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            target = row.get("targetKey", "")
            if target:
                products.setdefault(target, []).append(row)
    return products


def readiness_row(
    target: str,
    protocols: dict[str, dict[str, str]],
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
    products: dict[str, list[dict[str, str]]],
    linkage: dict[str, str],
) -> dict[str, str]:
    builders = {
        "substitution-elasticity": substitution_row,
        "procurement-modification-causal-capture": procurement_row,
        "comment-authenticity-and-uptake-effect": comment_row,
        "venue-shifting-detection-effect": venue_row,
    }
    row = builders[target](capabilities, panels, moments, procurement, linkage)
    protocol = protocols[target]
    target_products = products.get(target, [])
    product_gate = product_gate_summary(target_products)
    ready_labels = ready_product_labels(target_products)
    if ready_labels:
        row["currentSourceProducts"] = append_text(
            row["currentSourceProducts"],
            "first-wave ready products=" + "; ".join(ready_labels),
        )
    row["nextAction"] = product_aware_next_action(target, row["nextAction"], ready_labels)
    row["blockingIssue"] = product_aware_blocking_issue(target, row["blockingIssue"], ready_labels)
    if product_gate["missingProducts"]:
        row["missingSourceProducts"] = product_gate["missingProducts"]
    return {
        "targetKey": target,
        "protocolStatus": protocol.get("protocolStatus", ""),
        "sourceReadiness": row["sourceReadiness"],
        "sourceProductGate": product_gate["sourceProductGate"],
        "sourceProductEvidence": product_gate["sourceProductEvidence"],
        "currentSourceProducts": row["currentSourceProducts"],
        "boundedOrProxySupport": row["boundedOrProxySupport"],
        "missingSourceProducts": row["missingSourceProducts"],
        "blockingIssue": row["blockingIssue"],
        "claimBoundary": row["claimBoundary"],
        "nextAction": row["nextAction"],
    }


def product_gate_summary(rows: list[dict[str, str]]) -> dict[str, str]:
    if not rows:
        return {
            "sourceProductGate": "schema_gate_missing_report",
            "sourceProductEvidence": "required=missing; ready=0; missing=missing; schemaIssues=missing",
            "missingProducts": "first-wave source-product audit report",
        }
    required = [row for row in rows if row.get("requirementLevel") == "required"]
    ready_statuses = {"schema_ready", "text_ready"}
    ready = [row for row in required if row.get("productStatus") in ready_statuses]
    candidate_unreviewed = [
        row for row in required
        if row.get("productStatus") == "candidate_unreviewed"
    ]
    missing = [row for row in required if row.get("productStatus", "").startswith("missing")]
    schema_issues = [
        row for row in required
        if row.get("productStatus") not in ready_statuses
        and row.get("productStatus") != "candidate_unreviewed"
        and not row.get("productStatus", "").startswith("missing")
    ]
    if len(ready) == len(required) and required:
        gate = "schema_gate_ready"
    elif candidate_unreviewed:
        gate = "candidate_only_blocked"
    elif missing or schema_issues:
        gate = "schema_gate_blocked"
    else:
        gate = "schema_gate_not_evaluated"
    return {
        "sourceProductGate": gate,
        "sourceProductEvidence": (
            f"required={len(required)}; ready={len(ready)}; "
            f"candidateOnly={len(candidate_unreviewed)}; "
            f"missing={len(missing)}; schemaIssues={len(schema_issues)}"
        ),
        "missingProducts": "; ".join(
            row.get("productLabel", row.get("productKey", ""))
            for row in missing + candidate_unreviewed + schema_issues
        ),
    }


def ready_product_labels(rows: list[dict[str, str]]) -> list[str]:
    ready_statuses = {"schema_ready", "text_ready"}
    return [
        row.get("productLabel", row.get("productKey", ""))
        for row in rows
        if row.get("requirementLevel") == "required"
        and row.get("productStatus") in ready_statuses
    ]


def append_text(base: str, addition: str) -> str:
    if not base:
        return addition
    if not addition:
        return base
    return f"{base}; {addition}"


def product_aware_next_action(target: str, default: str, ready_labels: list[str]) -> str:
    ready = set(ready_labels)
    if target == "substitution-elasticity" and "named reform-shock event file" in ready:
        return (
            "Use the committed reform-shock event file and meeting/contact missing-channel note, "
            "then build the actor-issue-time linkage file and exposed plus comparison groups before "
            "inspecting outcome movement."
        )
    if target == "comment-authenticity-and-uptake-effect" and {
        "comment-body corpus",
        "duplicate/template cluster assignments",
    }.issubset(ready):
        return (
            "Use the committed Regulations.gov comment corpus and duplicate/template clusters, "
            "then link clustered comments to agency response sections and final-rule text before "
            "estimating uptake or duplicate-compression effects."
        )
    return default


def product_aware_blocking_issue(target: str, default: str, ready_labels: list[str]) -> str:
    ready = set(ready_labels)
    if target == "comment-authenticity-and-uptake-effect" and {
        "comment-body corpus",
        "duplicate/template cluster assignments",
    }.issubset(ready):
        return (
            "A bounded public comment corpus and duplicate/template clusters are committed, "
            "but agency-response uptake links and final-rule text movement remain absent."
        )
    return default


def linkage_candidate_summary(path: Path) -> dict[str, str]:
    if not path.exists():
        return {
            "count": "0",
            "crossVenueCount": "0",
            "sourceSystemMax": "0",
            "venueMax": "0",
            "sourceText": "cross-venue linkage candidates=missing",
            "boundaryText": "first-wave linkage candidates: missing",
        }
    count = 0
    cross_venue = 0
    max_sources = 0
    max_venues = 0
    source_systems: set[str] = set()
    venues: set[str] = set()
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            count += 1
            if row.get("candidateType") == "cross_venue":
                cross_venue += 1
            max_sources = max(max_sources, int_or_zero(row.get("sourceSystemCount", "")))
            max_venues = max(max_venues, int_or_zero(row.get("venueCount", "")))
            source_systems.update(split_semicolon(row.get("sourceSystems", "")))
            venues.update(split_semicolon(row.get("venues", "")))
    if count == 0:
        return {
            "count": "0",
            "crossVenueCount": "0",
            "sourceSystemMax": "0",
            "venueMax": "0",
            "sourceText": "cross-venue linkage candidates=0",
            "boundaryText": "first-wave linkage candidates: candidate report present with 0 cross-source rows",
        }
    return {
        "count": str(count),
        "crossVenueCount": str(cross_venue),
        "sourceSystemMax": str(max_sources),
        "venueMax": str(max_venues),
        "sourceText": (
            f"candidate cross-source actor keys={count}; cross-venue keys={cross_venue}; "
            f"source systems={len(source_systems)}; venues={len(venues)}"
        ),
        "boundaryText": (
            "first-wave linkage candidates: candidate-only "
            f"({count} cross-source keys; {cross_venue} cross-venue keys; "
            f"maxSources={max_sources}; maxVenues={max_venues})"
        ),
    }


def substitution_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
    linkage: dict[str, str],
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
            linkage["sourceText"],
        ]),
        "boundedOrProxySupport": "; ".join([
            panel_text(panels, "Direct dark money"),
            panel_text(panels, "Intermediaries"),
            panel_text(panels, "Revolving door"),
            linkage["boundaryText"],
        ]),
        "missingSourceProducts": "; ".join([
            "named reform-shock event file",
            "canonical actor-issue-time spine across at least three venues",
            "pre/post comparison groups for exposed and unaffected actors or jurisdictions",
            "meeting-log or contact-register panel, or an explicit missing-channel design note",
        ]),
        "blockingIssue": "Public surfaces exist, but the committed snapshot does not yet define an event panel that can estimate substitution elasticity.",
        "claimBoundary": "May guide a source-anchored substitution design; does not validate hidden-channel magnitudes or causal substitution effects.",
        "nextAction": "Choose one named reform shock, use the candidate-only entity-resolution seed files to prioritize manual actor review, build the actor-issue-time linkage file, and record exposed plus comparison actors before inspecting outcome movement.",
    }


def procurement_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
    linkage: dict[str, str],
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
    linkage: dict[str, str],
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
            "Rulemaking comments: source moments plus first-wave source products when ready "
            f"({metric_text(moments, 'regulatoryRows', 'regulatory rows')})"
        ),
        "missingSourceProducts": "; ".join([
            "comment-body corpus",
            "duplicate/template cluster assignments",
            "submitter authenticity fields where available",
            "agency response text",
            "final-rule text linkage",
            "treated/untreated or before/after docket marker",
        ]),
        "blockingIssue": "Docket schema and volume moments exist, but comment-corpus products and agency-response uptake links must both be committed before estimation.",
        "claimBoundary": "Supports rulemaking information-distortion design and source moments only; does not estimate comment-authenticity effects.",
        "nextAction": "Select a docket family, archive comment bodies and duplicate clusters, then link comments to response sections and final-rule text before estimating uptake.",
    }


def venue_row(
    capabilities: dict[str, dict[str, str]],
    panels: dict[str, dict[str, str]],
    moments: dict[str, dict[str, str]],
    procurement: dict[str, dict[str, str]],
    linkage: dict[str, str],
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
            linkage["sourceText"],
        ]),
        "boundedOrProxySupport": "; ".join([
            panel_text(panels, "Direct dark money"),
            panel_text(panels, "Intermediaries"),
            panel_text(panels, "Revolving door"),
            linkage["boundaryText"],
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
        "nextAction": "Start from the candidate-only entity-resolution seed files, adjudicate aliases linking LDA clients, FEC spenders, docket submitters, vendors, intermediaries, and access proxies, then audit false matches before promoting the panel.",
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


def int_or_zero(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def split_semicolon(value: str) -> set[str]:
    return {item.strip() for item in value.split(";") if item.strip()}


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
        "sourceProductGate",
        "sourceProductEvidence",
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
        "This audit maps the first-wave causal protocols to committed source products. It is a pre-estimation gate: source products can support protocol design, but no row clears calibrated policy-simulation claims or causal effect language. Candidate linkage rows from `reports/first-wave-linkage-candidates.md` and candidate-only seed files under `data/calibration/first-wave/` are manual-review worklists only; they do not satisfy adjudicated production source-product requirements.",
        "",
        "## Summary",
        "",
        f"- Protocols audited: `{len(rows)}`",
        f"- Ready to estimate: `{len(ready)}`",
        f"- Partial source support: `{len(partial)}`",
        f"- Blocked by missing source products: `{len(blocked)}`",
        "- Policy-simulation status: `not_cleared`",
        "- Source-product schema gate: `blocked_until_required_products_exist`",
        "",
        "## Readiness Matrix",
        "",
        "| Target | Source readiness | Source-product gate | Current source products | Missing source products | Blocking issue |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {targetKey} | {sourceReadiness} | {sourceProductGate} ({sourceProductEvidence}) | {currentSourceProducts} | {missingSourceProducts} | {blockingIssue} |".format(
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
