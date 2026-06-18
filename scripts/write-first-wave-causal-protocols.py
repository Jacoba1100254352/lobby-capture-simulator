#!/usr/bin/env python3
"""Write operational protocols for first-wave causal calibration targets."""

from __future__ import annotations

import csv
from pathlib import Path


REPORTS = Path("reports")
PAPER_TABLES = Path("paper/tables")
CAUSAL_TARGETS = REPORTS / "causal-calibration-targets.csv"


PROTOCOLS = {
    "substitution-elasticity": {
        "protocolStatus": "protocol_ready_source_pending",
        "unitOfAnalysis": "actor-issue-month or actor-issue-quarter",
        "treatmentOrShock": "binding disclosure, access, finance, cooling-off, or venue-integrity reform affecting one actor/issue set before comparable alternatives",
        "comparisonDesign": "event-study or difference-in-differences panel with matched unaffected actors, issues, or jurisdictions",
        "primaryOutcomes": "visible lobbying spend/contact, outside spending, docket submissions, procurement activity, intermediary routing, and hidden/substitution proxy load",
        "linkageKeys": "canonical actor id, issue code, client name, committee/spender id, docket id, UEI/recipient id, jurisdiction, and event date",
        "minimumSources": "LDA clients, OpenFEC spenders, Regulations.gov/Federal Register dockets, procurement vendors, meeting logs or nonprofit/intermediary rows",
        "falsificationChecks": "pre-trend tests, placebo reform dates, unaffected issue placebo rows, and actor types not plausibly exposed to the reform",
        "sensitivityChecks": "alternative event windows, actor matching rules, issue-code coarsening, and exclusion of high-outlier spenders",
        "threatModel": "simultaneous political shocks, endogenous reform adoption, entity-resolution errors, and unobserved private contacts",
        "claimUpgradeBoundary": "Can support a source-anchored substitution diagnostic for the named reform family; cannot establish national hidden-channel magnitudes alone.",
        "committedScaffold": "HLOGA reform-shock row, meeting/contact missing-channel note, and candidate actor-time plus comparison-group seeds.",
        "firstPromotionGate": "Adjudicate aliases, issues, exposure groups, and pre/post windows; replace candidate rows with observed actor-issue activity across at least three venues.",
        "whyItMatters": "Directly tests whether pressure moves from a restricted visible channel into alternate channels after a named reform shock.",
    },
    "procurement-modification-causal-capture": {
        "protocolStatus": "protocol_ready_source_pending",
        "unitOfAnalysis": "award-action, award-recipient-quarter, or agency-award-type panel",
        "treatmentOrShock": "lobbying/vendor-network exposure before post-award actions or procurement-integrity reform exposure",
        "comparisonDesign": "matched award/action panel controlling for agency, award type, size, timing, competition, and recipient history",
        "primaryOutcomes": "modification incidence, single-bid or limited-competition exposure, protest incidence, exclusion flags, firewall coverage, and amount-weighted modification load",
        "linkageKeys": "PIID, UEI, recipient name, agency, award type, action date, fiscal year, LDA client/issue, protest docket, and exclusion identifier",
        "minimumSources": "SAM.gov Contract Awards or FPDS action history, USAspending transaction rows, GAO protest rows, SAM exclusions, agency firewall records, and LDA client/issue rows",
        "falsificationChecks": "pre-award placebo modifications, low-discretion award classes, agencies without plausible exposure, and non-policy issue placebo links",
        "sensitivityChecks": "row-weighted, distinct-award, and amount-weighted denominators; agency fixed effects; competition-field completeness thresholds",
        "threatModel": "procurement coding inconsistency, unobserved contract complexity, reverse causality from troubled awards to lobbying, and missing protest/firewall data",
        "claimUpgradeBoundary": "Can strengthen procurement-domain capture-adjacent diagnostics; cannot justify broad calibrated capture effects without exposure timing and outcome linkage.",
        "committedScaffold": "USAspending action and bulk denominators, optional SAM importer, and acquisition plan for SAM/FPDS, protests, exclusions, and firewalls.",
        "firstPromotionGate": "Acquire a promotable SAM/FPDS action-history crosswalk and add GAO protest, SAM exclusion, offer-count, and firewall overlays.",
        "whyItMatters": "Turns procurement from denominator-mapped diagnostics into an outcome panel with timing, integrity controls, and exposure linkage.",
    },
    "comment-authenticity-and-uptake-effect": {
        "protocolStatus": "protocol_ready_source_pending",
        "unitOfAnalysis": "docket-comment, submitter-docket, or docket-rule stage",
        "treatmentOrShock": "duplicate compression, authenticity rule, mass-comment campaign, or docket triage procedure affecting comment processing",
        "comparisonDesign": "treated/untreated docket comparison or before/after design around authentication, deduplication, or high-template campaign events",
        "primaryOutcomes": "unique-information share, template saturation, technical-content share, review burden, agency-response uptake, and final-rule text movement",
        "linkageKeys": "docket id, comment id, submitter id/name, organization, issue terms, posted date, response section, rule id, and final-rule date",
        "minimumSources": "Regulations.gov comments, Federal Register rules, agency response text, duplicate/template clusters, authenticity fields where available, and technical-content labels",
        "falsificationChecks": "dockets without mass-comment exposure, non-substantive procedural comments, placebo response sections, and pre-campaign comment waves",
        "sensitivityChecks": "duplicate-clustering thresholds, technical-content classifiers, response-text matching rules, and excluding late or withdrawn comments",
        "threatModel": "missing comment bodies, bot or identity uncertainty, agency selection into authentication tools, and conflating volume with substantive influence",
        "claimUpgradeBoundary": "Can anchor rulemaking information-distortion mechanisms for observed dockets; cannot generalize to all agencies or hidden influence channels alone.",
        "committedScaffold": "Bounded Regulations.gov comment-body corpus, duplicate/template cluster assignments, and candidate response/final-rule linkage scaffold.",
        "firstPromotionGate": "Manually link clustered comments to agency response sections and final-rule text, then review uptake codes and text-similarity fields.",
        "whyItMatters": "Connects comment flooding and authenticity filters to agency uptake rather than only to docket volume or template saturation.",
    },
    "venue-shifting-detection-effect": {
        "protocolStatus": "protocol_ready_source_pending",
        "unitOfAnalysis": "canonical actor-issue-venue-time record",
        "treatmentOrShock": "availability of cross-venue entity resolution, disclosure matching, or meeting-log linkage for an actor/issue set",
        "comparisonDesign": "linkage-yield and detection design comparing single-source diagnostics with linked multi-venue actor/issue panels",
        "primaryOutcomes": "detected cross-venue movement, previously hidden actor overlap, network opacity, substitution-risk reclassification, and false-match rate",
        "linkageKeys": "canonical actor id, aliases, client/registrant id, committee/spender id, docket submitter id, UEI/vendor id, meeting participant, issue code, and date",
        "minimumSources": "LDA, OpenFEC, Regulations.gov/Federal Register, USAspending/SAM, enforcement or protest rows, meeting logs, and audited alias tables",
        "falsificationChecks": "manual false-positive/false-negative samples, same-name different-entity traps, unrelated issue placebo links, and withheld-source validation",
        "sensitivityChecks": "strict versus fuzzy matching, issue-window width, alias normalization rules, and venue subsets with and without meeting/procurement rows",
        "threatModel": "entity-resolution bias, common-name collisions, missing private channels, and inflated substitution when issue codes are too broad",
        "claimUpgradeBoundary": "Can support a detection and measurement contribution for cross-venue substitution; cannot by itself prove that substitution changed outcomes.",
        "committedScaffold": "Candidate canonical-actor, alias-review, issue-crosswalk, false-match, and linked actor-issue-venue-time seed files.",
        "firstPromotionGate": "Complete manual false-positive and false-negative audits, adjudicate issue comparability, and promote a reviewed linked panel.",
        "whyItMatters": "Shows how much apparent substitution becomes visible only after actors and issues are resolved across public venues.",
    },
}

PAPER_SUMMARIES = {
    "substitution-elasticity": {
        "label": "Substitution elasticity",
        "unit": "Actor-issue-month or quarter",
        "design": "Event-study or difference-in-differences around a binding reform shock.",
        "validity": "Pre-trends, placebo dates, unaffected issues, and alternate matching windows.",
        "scaffold": "HLOGA shock row plus candidate actor-time seeds.",
        "promotion": "Adjudicate exposed/comparison actors and observed pre/post activity across three or more venues.",
        "claim": "Named-reform substitution diagnostic.",
    },
    "procurement-modification-causal-capture": {
        "label": "Procurement modification",
        "unit": "Award-action or award-recipient-quarter",
        "design": "Matched award/action panel with agency, award-type, size, timing, and competition controls.",
        "validity": "Low-discretion placebo awards, agency fixed effects, and row/award/amount denominators.",
        "scaffold": "USAspending denominators plus optional SAM importer.",
        "promotion": "Promote SAM/FPDS crosswalk, protest, exclusion, offer-count, and firewall overlays.",
        "claim": "Procurement-domain capture-adjacent diagnostic.",
    },
    "comment-authenticity-and-uptake-effect": {
        "label": "Comment authenticity and uptake",
        "unit": "Docket-comment or docket-rule stage",
        "design": "Treated/untreated or before/after docket comparison around authentication or deduplication.",
        "validity": "No-mass-comment placebo dockets, response-section placebos, and duplicate-threshold sensitivity.",
        "scaffold": "Comment corpus, duplicate clusters, and candidate response-linkage file.",
        "promotion": "Review response/final-rule links, uptake codes, and text-similarity fields.",
        "claim": "Observed-docket information-distortion diagnostic.",
    },
    "venue-shifting-detection-effect": {
        "label": "Venue-shifting detection",
        "unit": "Actor-issue-venue-time record",
        "design": "Compare single-source diagnostics with linked multi-venue actor/issue panels.",
        "validity": "Manual false-match audits, unrelated issue placebos, and strict/fuzzy matching sensitivity.",
        "scaffold": "Candidate actor, alias, issue, false-match, and linked-panel seeds.",
        "promotion": "Complete false-match review and promote a reviewed actor-issue-venue-time panel.",
        "claim": "Cross-venue detection and measurement diagnostic.",
    },
}


def main() -> int:
    target_rows = read_csv(CAUSAL_TARGETS)
    protocols = protocol_rows(target_rows)
    REPORTS.mkdir(parents=True, exist_ok=True)
    PAPER_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(REPORTS / "first-wave-causal-protocols.csv", protocols)
    write_markdown(REPORTS / "first-wave-causal-protocols.md", protocols)
    write_latex(PAPER_TABLES / "first_wave_causal_protocols.tex", protocols)
    print("Wrote reports/first-wave-causal-protocols.csv")
    print("Wrote reports/first-wave-causal-protocols.md")
    print("Wrote paper/tables/first_wave_causal_protocols.tex")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def protocol_rows(target_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    first_wave_targets = [
        row for row in target_rows
        if row.get("upgradeTier") == "first-wave"
    ]
    rows: list[dict[str, str]] = []
    for target in first_wave_targets:
        target_key = target.get("targetKey", "")
        protocol = PROTOCOLS.get(target_key)
        if not protocol:
            continue
        rows.append({
            "targetKey": target_key,
            "priority": target.get("priority", ""),
            "status": target.get("status", ""),
            "estimand": target.get("estimand", ""),
            "clearanceCriterion": target.get("clearanceCriterion", ""),
            **protocol,
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "targetKey",
        "priority",
        "status",
        "protocolStatus",
        "unitOfAnalysis",
        "treatmentOrShock",
        "comparisonDesign",
        "primaryOutcomes",
        "linkageKeys",
        "minimumSources",
        "falsificationChecks",
        "sensitivityChecks",
        "threatModel",
        "committedScaffold",
        "firstPromotionGate",
        "whyItMatters",
        "estimand",
        "clearanceCriterion",
        "claimUpgradeBoundary",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# First-Wave Causal Protocols",
        "",
        "This report operationalizes the first-wave rows from `reports/causal-calibration-targets.md`. It does not clear calibrated policy-simulation claims. It specifies the minimum empirical designs needed before a later manuscript can move from mechanism checking toward source-anchored causal calibration.",
        "",
        "## Summary",
        "",
        f"- Protocols: `{len(rows)}`",
        f"- Protocol-ready/source-pending rows: `{sum(1 for row in rows if row['protocolStatus'] == 'protocol_ready_source_pending')}`",
        "- Policy-simulation status: `not_cleared`",
        "",
        "## Protocol Matrix",
        "",
        "| Target | Unit | Treatment or shock | Comparison design | Primary outcomes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {targetKey} | {unitOfAnalysis} | {treatmentOrShock} | {comparisonDesign} | {primaryOutcomes} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Linkage and Validity Checks",
        "",
        "| Target | Linkage keys | Minimum sources | Falsification checks | Sensitivity checks |",
        "| --- | --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {targetKey} | {linkageKeys} | {minimumSources} | {falsificationChecks} | {sensitivityChecks} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        "| Target | Threat model | Claim-upgrade boundary | Clearance criterion |",
        "| --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {targetKey} | {threatModel} | {claimUpgradeBoundary} | {clearanceCriterion} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Promotion Gates",
        "",
        "These rows identify the concrete scaffold already in the repository and the first manual gate that must clear before the protocol can be used for estimation.",
        "",
        "| Target | Committed scaffold | First promotion gate | Why it matters |",
        "| --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {targetKey} | {committedScaffold} | {firstPromotionGate} | {whyItMatters} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_latex(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "% Generated by scripts/write-first-wave-causal-protocols.py; do not edit by hand.",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\caption{First-wave causal calibration protocols.}",
        "\\label{tab:first-wave-causal-protocols}",
        "\\begin{tabular}{p{0.16\\textwidth}p{0.24\\textwidth}p{0.30\\textwidth}p{0.20\\textwidth}}",
        "\\toprule",
        "Target & Current scaffold & First promotion gate & Claim boundary \\\\",
        "\\midrule",
    ]
    for row in rows:
        summary = PAPER_SUMMARIES[row["targetKey"]]
        lines.append(
            "{} & {} & {} & {} \\\\".format(
                tex(summary["label"]),
                tex(summary["scaffold"]),
                tex(summary["promotion"]),
                tex(summary["claim"]),
            )
        )
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def tex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in str(value))


if __name__ == "__main__":
    raise SystemExit(main())
