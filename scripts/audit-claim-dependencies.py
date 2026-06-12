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
        "panels": ["Direct dark money", "Outside spending", "Intermediaries", "Revolving door", "Procurement identifiers"],
        "moments": [("outsideSpendingRows", 250.0), ("intermediaryRows", 50.0), ("revolvingDoorRows", 100.0)],
        "permitted": "Mechanism tests and source-aware stress diagnostics for channel substitution.",
        "avoid": "Do not present hidden substitution magnitudes as empirically validated.",
        "next": "Replace thin hidden-channel panels with direct routing, personnel, and transaction exports.",
    },
    {
        "key": "public-financing-counterweight",
        "family": "Public-financing counterweight",
        "panels": ["Public financing"],
        "moments": [("publicFinancingRows", 50.0), ("publicFinancingSourceShare", 0.01)],
        "permitted": "Thin program-row anchor for countervailing campaign-finance mechanisms.",
        "avoid": "Do not claim representative national public-financing uptake.",
        "next": "Add NYC, Seattle, federal, and additional local program rows with archived source files.",
    },
    {
        "key": "revolving-door-cooling-off",
        "family": "Revolving-door access",
        "panels": ["Revolving door"],
        "moments": [("revolvingDoorRows", 100.0), ("revolvingDoorConfidenceMean", 0.50)],
        "permitted": "Proxy-backed stress diagnostics for covered-position and cooling-off exposure.",
        "avoid": "Do not treat LDA covered-position rows as representative post-employment movement.",
        "next": "Add OGE, FACA, witness, LegiStorm/OpenSecrets, or archived personnel movement exports.",
    },
    {
        "key": "hidden-channel-magnitude",
        "family": "Hidden-channel magnitude",
        "panels": ["Direct dark money", "Electoral communications", "Revolving door"],
        "moments": [("darkMoneySourceShare", 0.01), ("electoralCommunicationRows", 1.0)],
        "strict": True,
        "permitted": "Missingness and proxy-gap diagnosis for hidden-channel mechanisms.",
        "avoid": "Do not treat bounded electoral-communication rows as hidden-donor or hidden-channel magnitude evidence.",
        "next": "Add direct hidden-donor or nonprofit-routing evidence plus broader electoral-communication coverage.",
    },
    {
        "key": "procurement-modification-capture",
        "family": "Procurement modification capture",
        "panels": ["Procurement concentration bridge", "Procurement action history", "Procurement modification risk"],
        "moments": [("procurementBridgeAgencyCount", 2.0), ("procurementActionRows", 1.0), ("procurementExPostModificationShare", 0.01)],
        "strict": True,
        "permitted": "Coverage warning and schema check for modification and concentration pathways.",
        "avoid": "Do not claim calibrated national procurement-modification incidence or capture rates.",
        "next": "Populate representative SAM/FPDS action-level transaction denominators and validate modifications.",
    },
    {
        "key": "calibrated-policy-simulation",
        "family": "Calibrated policy simulation",
        "panels": [
            "Direct dark money",
            "Electoral communications",
            "Public financing",
            "Revolving door",
            "Procurement concentration bridge",
            "Procurement action history",
            "Procurement modification risk",
        ],
        "moments": [("electoralCommunicationRows", 1.0), ("procurementActionRows", 1.0)],
        "strict": True,
        "permitted": "Not cleared; the current article can only use mechanism diagnostics and bounded source moments.",
        "avoid": "Do not describe the artifact as a calibrated policy-effect simulator.",
        "next": "Clear the P1/P2 source gaps and rerun validation before using calibrated policy language.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--tables", type=Path, default=TABLES)
    args = parser.parse_args()

    panels = read_panels(args.reports / SOURCE_PANEL_INVENTORY.name)
    moments = read_moments(args.reports / SOURCE_MOMENTS.name)
    rows = [claim_row(claim, panels, moments) for claim in CLAIMS]

    args.reports.mkdir(parents=True, exist_ok=True)
    args.tables.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "claim-source-dependency.csv", rows)
    write_markdown(args.reports / "claim-source-dependency.md", rows)
    write_latex(args.tables / "claim_source_dependency.tex", rows)
    print(f"Wrote {args.reports / 'claim-source-dependency.csv'}")
    print(f"Wrote {args.reports / 'claim-source-dependency.md'}")
    print(f"Wrote {args.tables / 'claim_source_dependency.tex'}")
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


def claim_row(
        claim: dict[str, object],
        panels: dict[str, dict[str, str]],
        moments: dict[str, float],
) -> dict[str, str]:
    panel_names = list(claim.get("panels", []))
    panel_rows = [panels.get(name, {"panel": name, "status": "missing", "note": "panel absent from inventory"}) for name in panel_names]
    weak = [row for row in panel_rows if row.get("status") in WEAK_STATUSES]
    blocking = [row for row in panel_rows if row.get("status") in BLOCKING_STATUSES]
    moment_results = moment_checks(list(claim.get("moments", [])), moments)
    failed_moments = [item for item in moment_results if not item["passed"]]

    strict = bool(claim.get("strict", False))
    if failed_moments or (strict and (weak or blocking)) or blocking:
        status = "not_cleared"
    elif weak:
        status = "bounded"
    else:
        status = "cleared"

    strong_dependencies = [row.get("panel", "") for row in panel_rows if row.get("status") == "usable"]
    weak_dependencies = [
        f"{row.get('panel', '')} ({row.get('status', 'missing')})"
        for row in weak
    ]
    missing_dependencies = [
        f"{item['metric']}<{item['minimum']:.4g}"
        for item in failed_moments
    ]
    source_support = support_sentence(status, strong_dependencies, weak_dependencies, missing_dependencies)
    return {
        "claimKey": str(claim["key"]),
        "claimFamily": str(claim["family"]),
        "status": status,
        "sourceSupport": source_support,
        "strongDependencies": "; ".join(strong_dependencies) if strong_dependencies else "none",
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
) -> str:
    if status == "cleared":
        return "Source dependencies are usable for the stated mechanism or distributional diagnostic."
    issues = []
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
        "strongDependencies",
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
        "| Claim family | Strong dependencies | Weak dependencies | Moment checks |",
        "| --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {claimFamily} | {strongDependencies} | {weakDependencies} | {momentChecks} |".format(
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


def posture_label(status: str) -> str:
    return {
        "cleared": "cleared",
        "bounded": "bounded",
        "not_cleared": "not cleared",
    }.get(status, status)


def table_support(row: dict[str, str]) -> str:
    return {
        "strategic-substitution-mechanism": "Thin direct dark-money and revolving-door panels.",
        "public-financing-counterweight": "Thin public-financing program panel.",
        "revolving-door-cooling-off": "Thin LDA-derived revolving-door proxy.",
        "hidden-channel-magnitude": "Thin direct dark-money and revolving-door proxies; bounded electoral-communication bridge present.",
        "procurement-modification-capture": "No action rows; modification moment below threshold.",
        "calibrated-policy-simulation": "Hidden-channel and procurement-action dependencies not cleared.",
    }.get(row["claimKey"], row["sourceSupport"])


def table_use(row: dict[str, str]) -> str:
    return {
        "strategic-substitution-mechanism": "Mechanism stress tests.",
        "public-financing-counterweight": "Thin countervailing-finance anchor.",
        "revolving-door-cooling-off": "Proxy-backed cooling-off diagnostics.",
        "hidden-channel-magnitude": "Missingness and proxy-gap diagnosis only.",
        "procurement-modification-capture": "Coverage warning and schema check.",
        "calibrated-policy-simulation": "Not a policy-effect claim.",
    }.get(row["claimKey"], row["permittedUse"])


def table_next(row: dict[str, str]) -> str:
    return {
        "strategic-substitution-mechanism": "Direct routing, personnel, and action exports.",
        "public-financing-counterweight": "Broader public-program rows.",
        "revolving-door-cooling-off": "OGE, FACA, witness, or personnel exports.",
        "hidden-channel-magnitude": "Direct hidden-donor/nonprofit-routing rows plus broader electoral-communication coverage.",
        "procurement-modification-capture": "Representative SAM/FPDS action rows.",
        "calibrated-policy-simulation": "Clear P1/P2 source gaps.",
    }.get(row["claimKey"], row["nextEvidence"])


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


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
