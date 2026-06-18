#!/usr/bin/env python3
"""Map manuscript claim families to their empirical source dependencies."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPORTS = Path("reports")
TABLES = Path("paper/tables")
SOURCE_PANEL_INVENTORY = REPORTS / "source-panel-inventory.csv"
SOURCE_MOMENTS = REPORTS / "source-moments.csv"
CAUSAL_CALIBRATION_TARGETS = REPORTS / "causal-calibration-targets.csv"

WEAK_STATUSES = {"thin", "warning", "fixture-only", "missing"}
BLOCKING_STATUSES = {"warning", "fixture-only", "missing"}

CLAIMS = [
    {
        "key": "lobbying-disclosure-surface",
        "family": "Lobbying disclosure surface",
        "panels": [],
        "moments": [("ldaRows", 50.0), ("lobbyingClientTop3Share", 0.0)],
        "permitted": "Distributional anchor for visible lobbying concentration and disclosure timing.",
        "avoid": "Do not generalize beyond the 2024 EPA/ENV source slice.",
        "next": "Broaden issue codes and agencies after the environmental slice remains stable.",
    },
    {
        "key": "visible-electoral-money",
        "family": "Visible electoral money",
        "panels": ["Outside spending"],
        "moments": [("fecRows", 100.0), ("outsideSpendingRows", 250.0)],
        "permitted": "Distributional anchor for observed receipts and independent-expenditure pressure.",
        "avoid": "Do not treat visible FEC rows as direct dark-money or hidden-donor evidence.",
        "next": "Add lobbyist bundling, broader electoral-communication coverage, and state/local overlays.",
    },
    {
        "key": "rulemaking-comment-record",
        "family": "Rulemaking comments",
        "panels": [],
        "moments": [("regulatoryRows", 50.0), ("commentTemplateShareMean", 0.0), ("commentAuthenticationShareMean", 0.0)],
        "permitted": "Distributional anchor for docket volume, template saturation, and comment-authenticity diagnostics.",
        "avoid": "Do not infer causal comment effects or full agency-wide comment quality.",
        "next": "Expand docket-level duplicate/authenticity checks and agency coverage.",
    },
    {
        "key": "procurement-identifier-competition",
        "family": "Procurement identifiers",
        "panels": ["Procurement identifiers"],
        "moments": [("procurementRows", 50.0), ("procurementKnownPiidShare", 0.90), ("procurementSingleBidShare", 0.0)],
        "permitted": "Schema and distributional anchor for award identifiers, competition fields, and vendor matching.",
        "avoid": "Do not use identifier coverage as evidence of post-award modification incidence.",
        "next": "Broaden SAM/FPDS fields and link exclusions, protests, and firewalls.",
    },
    {
        "key": "strategic-substitution-mechanism",
        "family": "Strategic substitution mechanism",
        "panels": ["Direct dark money", "Outside spending", "Intermediaries", "IRS 527 political organizations", "Revolving door", "Procurement identifiers"],
        "moments": [("outsideSpendingRows", 250.0), ("intermediaryRows", 50.0), ("intermediary527Rows", 1.0), ("revolvingDoorRows", 100.0)],
        "boundWeakPanels": True,
        "boundLimitedSupport": True,
        "permitted": "Mechanism tests and source-aware stress diagnostics for channel substitution.",
        "avoid": "Do not present hidden substitution magnitudes as empirically validated.",
        "next": "Broaden bounded nonprofit-routing, personnel, and transaction exports.",
    },
    {
        "key": "public-financing-counterweight",
        "family": "Public-financing counterweight",
        "panels": ["Public financing"],
        "moments": [("publicFinancingRows", 50.0), ("publicFinancingProgramCount", 2.0)],
        "boundLimitedSupport": True,
        "permitted": "Bounded local-program anchor for countervailing campaign-finance mechanisms.",
        "avoid": "Do not claim representative national public-financing uptake.",
        "next": "Add federal, state, and additional local program rows with archived source files.",
    },
    {
        "key": "revolving-door-cooling-off",
        "family": "Revolving-door access",
        "panels": ["Revolving door"],
        "moments": [("revolvingDoorRows", 100.0), ("revolvingDoorConfidenceMean", 0.50)],
        "boundLimitedSupport": True,
        "permitted": "Proxy-backed stress diagnostics for covered-position and cooling-off exposure.",
        "avoid": "Do not treat LDA covered-position rows as representative post-employment movement.",
        "next": "Add OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports.",
    },
    {
        "key": "hidden-channel-magnitude",
        "family": "Hidden-channel magnitude",
        "panels": ["Direct dark money", "Electoral communications", "Revolving door"],
        "moments": [("darkMoneyDirectRoutingRows", 1.0), ("electoralCommunicationRows", 1.0)],
        "strict": True,
        "maxStatus": "bounded",
        "boundedSupport": "Bounded by top-EIN Schedule I routing coverage and unobserved donor identities.",
        "permitted": "Bounded nonprofit-routing and missingness diagnostics for hidden-channel mechanisms.",
        "avoid": "Do not treat the top-EIN Schedule I slice or bounded electoral-communication rows as representative hidden-channel magnitude or donor-identity evidence.",
        "next": "Broaden nonprofit-routing, direct donor, and electoral-communication coverage beyond the current top-EIN slice.",
    },
    {
        "key": "procurement-modification-capture",
        "family": "Procurement modification capture",
        "panels": ["Procurement concentration panel", "Procurement action history", "Procurement modification risk"],
        "moments": [("procurementConcentrationPanelAgencyCount", 2.0), ("procurementNationalActionRows", 1.0), ("procurementActionRows", 1.0), ("procurementExPostModificationShare", 0.01), ("procurementModifiedAwardShare", 0.01)],
        "strict": True,
        "maxStatus": "bounded",
        "boundedSupport": "Denominator-mapped USAspending bulk rows support distributional diagnostics; SAM/FPDS coding reconciliation and causal capture validation remain future work.",
        "permitted": "Denominator-mapped distributional diagnostics for modification and concentration pathways.",
        "avoid": "Do not claim causal procurement-modification capture rates or representative policy effects.",
        "next": "Crosswalk USAspending modification coding against SAM/FPDS action-history definitions and add protest, exclusion, and firewall overlays.",
    },
    {
        "key": "calibrated-policy-simulation",
        "family": "Calibrated policy simulation",
        "panels": [
            "Direct dark money",
            "Electoral communications",
            "Public financing",
            "IRS 527 political organizations",
            "Revolving door",
            "Procurement concentration panel",
            "Procurement action history",
            "Procurement modification risk",
        ],
        "moments": [("darkMoneyDirectRoutingRows", 1.0), ("electoralCommunicationRows", 1.0), ("intermediary527Rows", 1.0), ("procurementNationalActionRows", 1.0), ("procurementActionRows", 1.0)],
        "strict": True,
        "maxStatus": "bounded",
        "boundedSupport": "Cleared source panels support the mechanism article, but calibrated policy simulation still lacks causal calibration of hidden-channel and reform-effect magnitudes.",
        "permitted": "Not cleared; the current article can only use mechanism diagnostics and bounded source moments.",
        "avoid": "Do not describe the artifact as a calibrated policy-effect simulator.",
        "next": "Add causal calibration targets and independent validation before using calibrated policy-simulation language.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--tables", type=Path, default=TABLES)
    args = parser.parse_args()

    panels = read_panels(args.reports / SOURCE_PANEL_INVENTORY.name)
    moments = read_moments(args.reports / SOURCE_MOMENTS.name)
    causal_blockers = read_causal_blockers(args.reports / CAUSAL_CALIBRATION_TARGETS.name)
    rows = [claim_row(claim, panels, moments, causal_blockers) for claim in CLAIMS]

    args.reports.mkdir(parents=True, exist_ok=True)
    args.tables.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "claim-source-dependency.csv", rows)
    write_markdown(args.reports / "claim-source-dependency.md", rows)
    write_latex(args.tables / "claim_source_dependency.tex", rows)
    write_claim_ladder_latex(args.tables / "claim_ladder.tex", rows, causal_blockers)
    print(f"Wrote {args.reports / 'claim-source-dependency.csv'}")
    print(f"Wrote {args.reports / 'claim-source-dependency.md'}")
    print(f"Wrote {args.tables / 'claim_source_dependency.tex'}")
    print(f"Wrote {args.tables / 'claim_ladder.tex'}")
    return 0


def read_panels(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing source-panel inventory: {path}")
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get("panel", ""): row for row in csv.DictReader(source)}


def read_moments(path: Path) -> dict[str, float]:
    moments: dict[str, float] = {}
    if not path.exists():
        return moments
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row.get("scope") != "snapshot":
                continue
            metric = row.get("metric", "")
            value = row.get("value", "")
            if metric and value:
                moments[metric] = float(value)
    return moments


def read_causal_blockers(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return [
            row for row in csv.DictReader(source)
            if row.get("blocksPolicySimulation", "yes") == "yes"
        ]


def claim_row(
        claim: dict[str, object],
        panels: dict[str, dict[str, str]],
        moments: dict[str, float],
        causal_blockers: list[dict[str, str]],
) -> dict[str, str]:
    panel_names = list(claim.get("panels", []))
    panel_rows = [panels.get(name, {"panel": name, "status": "missing", "note": "panel absent from inventory"}) for name in panel_names]
    weak = [row for row in panel_rows if row.get("status") in WEAK_STATUSES]
    blocking = [row for row in panel_rows if row.get("status") in BLOCKING_STATUSES]
    moment_results = moment_checks(list(claim.get("moments", [])), moments)
    failed_moments = [item for item in moment_results if not item["passed"]]

    strict = bool(claim.get("strict", False))
    bound_weak_panels = bool(claim.get("boundWeakPanels", False))
    bound_limited_support = bool(claim.get("boundLimitedSupport", False))
    limited_support = [
        row for row in panel_rows
        if row.get("status") == "usable"
        and row.get("supportLevel", support_level(row)) != "direct-bounded"
    ]
    if failed_moments or (strict and (weak or blocking)) or (blocking and not bound_weak_panels):
        status = "not_cleared"
    elif weak or (bound_limited_support and limited_support):
        status = "bounded"
    else:
        status = "cleared"
    max_status = str(claim.get("maxStatus", ""))
    if max_status == "bounded" and status == "cleared":
        status = "bounded"
    if claim.get("key") == "calibrated-policy-simulation" and causal_blockers:
        status = "not_cleared"

    usable_dependencies = [row.get("panel", "") for row in panel_rows if row.get("status") == "usable"]
    limited_dependencies = [
        f"{row.get('panel', '')} ({row.get('supportLevel', support_level(row))})"
        for row in limited_support
    ]
    weak_dependencies = [
        f"{row.get('panel', '')} ({row.get('status', 'missing')})"
        for row in weak
    ]
    missing_dependencies = [
        f"{item['metric']}<{item['minimum']:.4g}"
        for item in failed_moments
    ]
    source_support = support_sentence(status, usable_dependencies, weak_dependencies, missing_dependencies, limited_dependencies)
    if status == "bounded" and claim.get("boundedSupport"):
        source_support = str(claim["boundedSupport"])
    if claim.get("key") == "calibrated-policy-simulation" and causal_blockers:
        source_support = (
            f"Not cleared while {len(causal_blockers)} causal-calibration targets block policy simulation; "
            "current source panels support only mechanism diagnostics and bounded source moments."
        )
    return {
        "claimKey": str(claim["key"]),
        "claimFamily": str(claim["family"]),
        "status": status,
        "sourceSupport": source_support,
        "usableDependencies": "; ".join(usable_dependencies) if usable_dependencies else "none",
        "limitedDependencies": "; ".join(limited_dependencies) if limited_dependencies else "none",
        "weakDependencies": "; ".join(weak_dependencies) if weak_dependencies else "none",
        "momentChecks": "; ".join(format_moment(item) for item in moment_results) if moment_results else "none",
        "permittedUse": str(claim["permitted"]),
        "avoidClaim": str(claim["avoid"]),
        "nextEvidence": str(claim["next"]),
    }


def moment_checks(
        specs: list[tuple[str, float]],
        moments: dict[str, float],
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for metric, minimum in specs:
        value = moments.get(metric)
        results.append(
            {
                "metric": metric,
                "minimum": minimum,
                "value": value,
                "passed": value is not None and value >= minimum,
            }
        )
    return results


def support_sentence(
        status: str,
        strong: list[str],
        weak: list[str],
        missing: list[str],
        limited: list[str],
) -> str:
    if status == "cleared":
        return "Source dependencies are usable for the stated mechanism or distributional diagnostic."
    issues = []
    if limited:
        issues.append("source-limited usable panels: " + ", ".join(limited))
    if weak:
        issues.append("weak panels: " + ", ".join(weak))
    if missing:
        issues.append("missing moment thresholds: " + ", ".join(missing))
    if not issues:
        issues.append("claim remains source-limited")
    prefix = "Bounded by" if status == "bounded" else "Not cleared because of"
    return f"{prefix} {'; '.join(issues)}."


def format_moment(item: dict[str, object]) -> str:
    value = item["value"]
    value_text = "missing" if value is None else f"{float(value):.4g}"
    mark = "ok" if item["passed"] else "gap"
    return f"{item['metric']}={value_text} ({mark})"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "claimKey",
        "claimFamily",
        "status",
        "sourceSupport",
        "usableDependencies",
        "limitedDependencies",
        "weakDependencies",
        "momentChecks",
        "permittedUse",
        "avoidClaim",
        "nextEvidence",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ("cleared", "bounded", "not_cleared")}
    lines = [
        "# Claim-Source Dependency Audit",
        "",
        "This audit maps manuscript claim families to the source panels and source moments they depend on. It is generated from `reports/source-panel-inventory.csv` and `reports/source-moments.csv` so empirical support cannot drift silently from the paper text.",
        "",
        "## Summary",
        "",
        f"- Cleared claim families: `{counts['cleared']}`",
        f"- Bounded claim families: `{counts['bounded']}`",
        f"- Not-cleared claim families: `{counts['not_cleared']}`",
        "",
        "| Claim family | Status | Source support | Permitted use | Claim to avoid | Next evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {claimFamily} | {status} | {sourceSupport} | {permittedUse} | {avoidClaim} | {nextEvidence} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Dependency Details",
        "",
        "| Claim family | Status | Usable dependencies | Source-limited usable dependencies | Weak dependencies | Moment checks |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {claimFamily} | {status} | {usableDependencies} | {limitedDependencies} | {weakDependencies} | {momentChecks} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_latex(path: Path, rows: list[dict[str, str]]) -> None:
    selected = [row for row in rows if row["status"] in {"bounded", "not_cleared"}]
    lines = [
        "% Generated by scripts/audit-claim-dependencies.py; source=reports/claim-source-dependency.csv",
        "\\begingroup",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{longtable}{p{0.20\\textwidth}p{0.12\\textwidth}p{0.24\\textwidth}p{0.20\\textwidth}p{0.16\\textwidth}}",
        "\\caption{Claim-source dependency audit for bounded or not-cleared claim families. Cleared rows remain in the generated Markdown/CSV report; the table highlights the empirical dependencies most likely to matter in review.}\\label{tab:claim-source-dependency}\\\\",
        "\\toprule",
        "Claim family & Posture & Source support & Permitted use & Next evidence \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "Claim family & Posture & Source support & Permitted use & Next evidence \\\\",
        "\\midrule",
        "\\endhead",
    ]
    for row in selected:
        lines.append(
            " & ".join(
                latex_escape(value)
                for value in (
                    row["claimFamily"],
                    posture_label(row["status"]),
                    table_support(row),
                    table_use(row),
                    table_next(row),
                )
            )
            + " \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{longtable}", "\\endgroup", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_claim_ladder_latex(
        path: Path,
        rows: list[dict[str, str]],
        causal_blockers: list[dict[str, str]],
) -> None:
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ("cleared", "bounded", "not_cleared")}
    blocker_count = len(causal_blockers)
    ladder_rows = [
        (
            "Internal mechanism diagnostics",
            "cleared",
            "Compare model modes, scenario stress tests, substitution warnings, and design diagnostics under stated assumptions.",
            "Do not read synthetic capture, hidden capture, or total distortion as observed misconduct or welfare loss.",
            "Falsification and parameter discipline require linked substitution episodes, but the mechanism claim does not require policy-effect identification.",
        ),
        (
            "Observable source moments",
            f"{counts['cleared']} cleared; {counts['bounded']} bounded families",
            "Use public rows as distributional anchors, schema checks, source-moment diagnostics, and claim-boundary evidence.",
            "Do not generalize bounded panels into representative hidden-channel magnitudes or national public-financing uptake.",
            "Broaden source panels and keep direct, proxy, denominator-mapped, and program-bounded evidence classes separate.",
        ),
        (
            "Hidden and substitution mechanisms",
            "bounded",
            "Use bounded routing, intermediary, revolving-door, procurement, and missingness diagnostics to stress-test substitution pathways.",
            "Do not claim empirically validated hidden substitution magnitudes, donor identities, or post-employment movement rates.",
            "Add donor-routing coverage, personnel-movement exports, cross-venue actor links, and procurement overlays.",
        ),
        (
            "Calibrated policy-effect claims",
            "not cleared",
            "Exclude calibrated reform-effect, representative capture-rate, and definitive portfolio-ranking claims from this article.",
            "Do not describe the simulator as estimating which real-world reforms work.",
            f"Clear the causal-calibration target matrix ({blocker_count} open targets) and rerun claim-source audits before upgrading claim strength.",
        ),
    ]
    lines = [
        "% Generated by scripts/audit-claim-dependencies.py; source=reports/claim-source-dependency.csv",
        "\\begin{table*}[tbp]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        (
            "\\begin{tabular}{"
            ">{\\raggedright\\arraybackslash}p{0.16\\textwidth}"
            ">{\\raggedright\\arraybackslash}p{0.12\\textwidth}"
            ">{\\raggedright\\arraybackslash}p{0.24\\textwidth}"
            ">{\\raggedright\\arraybackslash}p{0.20\\textwidth}"
            ">{\\raggedright\\arraybackslash}p{0.20\\textwidth}"
            "}"
        ),
        "\\toprule",
        "Claim tier & Current posture & Permitted use in this article & Claim not supported & Upgrade evidence \\\\",
        "\\midrule",
    ]
    for row in ladder_rows:
        lines.append(" & ".join(latex_escape(value) for value in row) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Claim ladder separating synthetic mechanism diagnostics, bounded source moments, hidden-channel mechanisms, and calibration-blocked claim tiers. The statuses are generated from the claim-source dependency and causal-calibration audits.}",
            "\\label{tab:claim-ladder}",
            "\\end{table*}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def posture_label(status: str) -> str:
    return {
        "cleared": "cleared",
        "bounded": "bounded",
        "not_cleared": "not cleared",
    }.get(status, status)


def table_support(row: dict[str, str]) -> str:
    return {
        "strategic-substitution-mechanism": "Substitution panels are usable but include direct/proxy, proxy, and proxy-thin limits.",
        "public-financing-counterweight": "Bounded local public-financing program panel.",
        "revolving-door-cooling-off": "LDA-derived covered-position bridge.",
        "hidden-channel-magnitude": "Top-EIN Schedule I nonprofit-routing rows present; donor identities remain unobserved.",
        "procurement-modification-capture": "Denominator-mapped bulk and action rows present; causal capture validation remains future work.",
        "calibrated-policy-simulation": "Causal-calibration target matrix still blocks policy-effect claims; source panels support only mechanism diagnostics.",
    }.get(row["claimKey"], row["sourceSupport"])


def table_use(row: dict[str, str]) -> str:
    return {
        "strategic-substitution-mechanism": "Mechanism stress tests.",
        "public-financing-counterweight": "Bounded countervailing-finance anchor.",
        "revolving-door-cooling-off": "Proxy-backed cooling-off diagnostics.",
        "hidden-channel-magnitude": "Bounded routing and missingness diagnostics only.",
        "procurement-modification-capture": "Denominator-mapped diagnostics.",
        "calibrated-policy-simulation": "Not a policy-effect claim.",
    }.get(row["claimKey"], row["permittedUse"])


def table_next(row: dict[str, str]) -> str:
    return {
        "strategic-substitution-mechanism": "Broader routing, personnel, and action exports.",
        "public-financing-counterweight": "Federal, state, and additional local rows.",
        "revolving-door-cooling-off": "OGE, FACA, witness, or personnel exports.",
        "hidden-channel-magnitude": "Broader routing and donor-identity coverage.",
        "procurement-modification-capture": "SAM/FPDS coding and protest/firewall overlays.",
        "calibrated-policy-simulation": "Independent causal calibration targets.",
    }.get(row["claimKey"], row["nextEvidence"])


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def support_level(panel: dict[str, str]) -> str:
    status = panel.get("status", "missing")
    if status in {"missing", "fixture-only"}:
        return "schema-only"
    if status in {"warning", "thin"}:
        return status
    if status != "usable":
        return "limited"

    evidence = panel.get("evidenceClass", "").lower()
    if "proxy/thin" in evidence:
        return "proxy-thin"
    if "direct/proxy" in evidence:
        return "direct-proxy-bounded"
    if "denominator-mapped" in evidence:
        return "denominator-bounded"
    if "proxy" in evidence:
        return "proxy-bounded"
    if "program" in evidence:
        return "program-bounded"
    if "when present" in evidence:
        return "conditional-direct"
    if "direct" in evidence:
        return "direct-bounded"
    return "source-bounded"


def latex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
        .replace("<", "$<$")
        .replace(">", "$>$")
    )


if __name__ == "__main__":
    raise SystemExit(main())
