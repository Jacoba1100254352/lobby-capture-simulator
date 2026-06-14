#!/usr/bin/env python3
"""List independent causal targets required before policy-simulation claims clear."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


REPORTS = Path("reports")
CLAIM_SOURCE_DEPENDENCY = REPORTS / "claim-source-dependency.csv"

TARGETS = [
    {
        "targetKey": "hidden-donor-routing-magnitude",
        "priority": "P1",
        "mechanism": "Hidden donor routing through nonprofits, associations, and adjacent outside-spending vehicles",
        "estimand": "Share and concentration of concealed or indirectly traceable donor-linked money that reaches electoral, lobbying, or public-information channels",
        "requiredEvidence": "Representative routing network with source, recipient, timing, transfer amount, political use, and donor-identity or beneficial-owner linkage where legally observable",
        "candidateSources": "IRS Form 990 XML Schedule I/R; IRS 8871/8872; OpenFEC Schedule E, electioneering, and communication-cost rows; state campaign-finance exports; curated investigative or beneficial-owner datasets",
        "currentSupport": "Bounded top-EIN Schedule I transfer rows, OpenFEC outside-spending rows, and opaque-capacity proxies",
        "status": "bounded_proxy_only",
        "permittedUse": "Bounded routing and missingness diagnostics",
        "clearanceCriterion": "Representative routing rows spanning multiple organization classes with donor-linkage metadata or an explicit defensible missingness model",
        "nextAction": "Broaden nonprofit-routing rows beyond the top-EIN slice and add donor-linkage or beneficial-owner coverage where public sources permit.",
        "upgradeTier": "second-wave",
        "firstStudyDesign": "Construct a multi-class nonprofit and 527 routing panel, then estimate missingness and transfer concentration rather than treating capacity proxies as hidden spending.",
        "minimumDataProduct": "Form 990 Schedule I/R or equivalent transfer rows for more than the top-EIN slice, IRS 8871/8872 rows beyond the bounded alphabetic slice, and linkage flags separating observed transfers from donor-identity gaps.",
        "manuscriptImpact": "Would strengthen hidden-channel magnitude bounds; it still would not by itself estimate reform effects without a design that links routing changes to a reform shock.",
    },
    {
        "targetKey": "substitution-elasticity",
        "priority": "P1",
        "mechanism": "Strategic movement from restricted visible channels into hidden, intermediary, venue, or technical channels",
        "estimand": "Change in alternate-channel spending, contact, or influence pressure after a disclosure, finance, access, or cooling-off reform binds",
        "requiredEvidence": "Before/after or cross-jurisdiction design linking reform timing to channel-specific activity by common actors and issues",
        "candidateSources": "State lobbying and campaign-finance reforms; municipal disclosure changes; LDA filings; OpenFEC spending; docket comment records; meeting logs; procurement action records",
        "currentSupport": "Synthetic mechanism comparison, sensitivity sweeps, and source moments for individual channels",
        "status": "open_design_needed",
        "permittedUse": "Mechanism stress tests and qualitative substitution warnings",
        "clearanceCriterion": "At least one external quasi-experimental or panel design that estimates cross-channel substitution direction for a named reform family",
        "nextAction": "Build a cross-source event panel around one reform shock and track visible, intermediary, dark-money, comment, and procurement channels by actor and issue.",
        "upgradeTier": "first-wave",
        "firstStudyDesign": "Use a named disclosure, access, finance, or cooling-off reform shock and compare pre/post channel activity for matched actors and issues against unaffected actors or jurisdictions.",
        "minimumDataProduct": "Actor-issue-time panel linking at least three channels, such as LDA clients, OpenFEC spenders, docket submitters, procurement vendors, meeting-log participants, or nonprofit intermediaries.",
        "manuscriptImpact": "Would directly test the paper's central substitution mechanism and could upgrade the article from a pure mechanism demonstration toward a source-anchored substitution diagnostic.",
    },
    {
        "targetKey": "procurement-modification-causal-capture",
        "priority": "P1",
        "mechanism": "Post-award specification changes, modifications, protests, exclusions, and firewall leakage",
        "estimand": "Effect of lobbying/vendor-network exposure on post-award modification, protest, exclusion, single-bid, or firewall outcomes conditional on agency, award type, and contract size",
        "requiredEvidence": "SAM/FPDS-style action history with PIID/UEI, modification coding, action dates, competition, offer counts, exclusions, protests, firewall indicators, and linked lobbying/vendor exposure",
        "candidateSources": "SAM.gov Contract Awards; FPDS/USAspending transaction history; GAO bid protests; SAM exclusions; agency procurement-integrity/firewall records; LDA client and issue records",
        "currentSupport": "USAspending bulk denominator crosswalk, action-row diagnostics, distinct-award diagnostics, amount-weighted diagnostics, and optional SAM importer",
        "status": "denominator_mapped_not_causal",
        "permittedUse": "Denominator-mapped procurement diagnostics",
        "clearanceCriterion": "A reconciled SAM/FPDS action-history panel linked to exposure variables and at least one causal or matched comparison design",
        "nextAction": "Crosswalk USAspending and SAM/FPDS modification codes, then add protest, exclusion, offer-count, and firewall overlays.",
        "upgradeTier": "first-wave",
        "firstStudyDesign": "Create a matched award/action panel comparing exposed vendors or issue areas with otherwise similar awards, controlling for agency, award type, size, timing, and competition fields.",
        "minimumDataProduct": "PIID/UEI action-history rows with modification coding, offer counts, competition flags, protest/exclusion overlays, and a documented crosswalk between USAspending and SAM/FPDS action definitions.",
        "manuscriptImpact": "Would turn the procurement bridge from denominator-mapped diagnostics into the most concrete empirical domain for testing capture-adjacent outcomes.",
    },
    {
        "targetKey": "revolving-door-access-effect",
        "priority": "P1",
        "mechanism": "Former-official access, advisory influence, and cooling-off evasion",
        "estimand": "Effect of covered-position or post-employment movement on access, venue choice, enforcement forbearance, or rule/procurement outcomes",
        "requiredEvidence": "Person-level movement, employer/client linkage, covered-position metadata, cooling-off dates, contact or venue records, and outcome timing",
        "candidateSources": "OGE disclosures; LDA covered-position fields; LegiStorm/OpenSecrets career histories; FACA rosters; witness records; calendars and meeting logs where available",
        "currentSupport": "LDA-derived covered-position rows and revolving-door proxy diagnostics",
        "status": "bounded_proxy_only",
        "permittedUse": "Proxy-backed cooling-off and bridge diagnostics",
        "clearanceCriterion": "Documented personnel-movement panel with timing and outcome linkage, not only covered-position indicators",
        "nextAction": "Add OGE, FACA, witness, or personnel-movement exports and preserve person-entity identifiers for linkage.",
        "upgradeTier": "second-wave",
        "firstStudyDesign": "Link person-level movement into regulated entities, advisory committees, witnesses, or lobbying roles to later access, venue choice, enforcement, rulemaking, or procurement outcomes.",
        "minimumDataProduct": "Person-entity-time records with covered-position metadata, movement dates, employer/client linkage, access or venue events, and outcome timing.",
        "manuscriptImpact": "Would replace LDA covered-position proxies with a documented access bridge and reduce reviewer concern that revolving-door mechanisms are only synthetic.",
    },
    {
        "targetKey": "public-financing-countervailing-effect",
        "priority": "P2",
        "mechanism": "Public financing, matching funds, and democracy vouchers as countervailing participation",
        "estimand": "Effect of public financing participation on donor concentration, candidate dependence, spending mix, and modeled capture pressure",
        "requiredEvidence": "Candidate-level public-financing participation, public-fund amounts, private donor mix, spending, and comparable non-participant races",
        "candidateSources": "NYC CFB; Seattle Democracy Voucher data; state and municipal public-financing programs; OpenFEC candidate finance and election results",
        "currentSupport": "NYC matching-fund rows and Seattle voucher rows",
        "status": "local_program_panel_only",
        "permittedUse": "Bounded countervailing-finance anchors",
        "clearanceCriterion": "Multi-program candidate-level panel with participant/non-participant comparison and donor-mix outcomes",
        "nextAction": "Add state and local public-financing panels and link them to candidate finance and election context.",
        "upgradeTier": "second-wave",
        "firstStudyDesign": "Compare participant and non-participant candidates across multiple public-financing programs with race, office, and election-cycle controls.",
        "minimumDataProduct": "Candidate-level public-funds participation, public payment or voucher totals, private donor mix, spending, office, election cycle, and comparable non-participant rows.",
        "manuscriptImpact": "Would strengthen countervailing-participation assumptions and clarify whether the public-financing mechanism is locally bounded or broader.",
    },
    {
        "targetKey": "comment-authenticity-and-uptake-effect",
        "priority": "P2",
        "mechanism": "Comment flooding, authenticity rules, technical submissions, and substantive uptake",
        "estimand": "Effect of duplicate compression or authenticity screening on unique information, review burden, substantive uptake, and final rule movement",
        "requiredEvidence": "Docket-level comments with duplicate/template clusters, submitter authenticity indicators, technical-content classification, agency response or final-rule linkage",
        "candidateSources": "Regulations.gov; Federal Register; agency docket files; ACUS/agency mass-comment reports; FTC/FCC/EPA docket-specific corpora",
        "currentSupport": "Regulations.gov/Federal Register schema rows, comment-volume concentration, and synthetic comment-triage diagnostics",
        "status": "bounded_source_moments",
        "permittedUse": "Comment-record and mechanism diagnostics",
        "clearanceCriterion": "Docket-level panel with observed duplicate clusters and agency response/final-rule linkage",
        "nextAction": "Add docket corpora with duplicate/template detection and link comments to agency response text or final-rule changes.",
        "upgradeTier": "first-wave",
        "firstStudyDesign": "Build docket-level before/after or treated/untreated comparisons around duplicate compression, authentication rules, or high-template comment campaigns, then link unique information to agency response text.",
        "minimumDataProduct": "Comment corpus with duplicate/template clusters, submitter or authenticity fields where available, technical-content labels, agency response text, final-rule linkage, and docket timing.",
        "manuscriptImpact": "Would provide a concrete rulemaking domain for information-distortion and comment-flooding mechanisms using public records rather than only synthetic diagnostics.",
    },
    {
        "targetKey": "enforcement-deterrence-effect",
        "priority": "P2",
        "mechanism": "Audits, sanctions, disclosure-error detection, and regulatory enforcement capacity",
        "estimand": "Effect of audit probability, detection delay, sanction severity, or enforcement backlog on visible and hidden influence behavior",
        "requiredEvidence": "Enforcement actions, audit/referral queues, penalties, delays, respondent links, and pre/post behavior by regulated or political actors",
        "candidateSources": "FEC enforcement and audit data; OCE/ethics records; DOJ/FARA enforcement; agency enforcement databases; inspector-general reports",
        "currentSupport": "Reporting-error detection and campaign-sanction incidence benchmarks plus model enforcement diagnostics",
        "status": "bounded_source_moments",
        "permittedUse": "Disclosure/audit plausibility checks",
        "clearanceCriterion": "Linked enforcement-outcome panel with actor-level behavior before and after audits, referrals, or sanctions",
        "nextAction": "Add enforcement-event rows with actor identifiers, delay, penalty, and follow-on behavior measures.",
        "upgradeTier": "second-wave",
        "firstStudyDesign": "Track actor behavior before and after audits, referrals, sanctions, or enforcement delays and compare with similar actors not facing enforcement events.",
        "minimumDataProduct": "Enforcement-event rows with actor identifiers, alleged violation or referral type, dates, delay, penalty, and follow-on lobbying, spending, disclosure, or procurement behavior.",
        "manuscriptImpact": "Would strengthen enforcement-capacity and deterrence assumptions, especially where current model behavior depends on audit probability and sanction severity.",
    },
    {
        "targetKey": "meeting-disclosure-and-access-effect",
        "priority": "P2",
        "mechanism": "Real-time disclosure, machine-readable meeting logs, and access opacity",
        "estimand": "Effect of meeting-log completeness and timeliness on access concentration, network opacity, and subsequent channel substitution",
        "requiredEvidence": "Machine-readable meeting/contact logs with actor identifiers, issue tags, timing, completeness metadata, and policy or procurement outcomes",
        "candidateSources": "Agency meeting logs; EU/UK/transparency registers for comparative panels; state or municipal contact registers; White House/agency visitor logs where available",
        "currentSupport": "Synthetic network opacity and legibility diagnostics; no committed representative meeting-log panel",
        "status": "open_source_panel_needed",
        "permittedUse": "Synthetic opacity and legibility diagnostics",
        "clearanceCriterion": "Observed meeting-log panel linked to actor networks and outcomes, with missingness or completeness diagnostics",
        "nextAction": "Add one machine-readable meeting-log panel and preserve actor, issue, date, and outcome linkage fields.",
        "upgradeTier": "second-wave",
        "firstStudyDesign": "Use one jurisdiction or agency with machine-readable meeting logs to test whether meeting disclosure changes access concentration, network opacity, or follow-on channel movement.",
        "minimumDataProduct": "Meeting or contact rows with actor names, issue tags, dates, agency/office, completeness metadata, and linkage to lobbying, docket, procurement, or enforcement records.",
        "manuscriptImpact": "Would give the cross-venue detection and access-opacity mechanisms an observed network surface rather than only synthetic legibility diagnostics.",
    },
    {
        "targetKey": "intermediary-network-effect",
        "priority": "P2",
        "mechanism": "Associations, think tanks, sponsored experts, 527s, and nonprofit intermediaries",
        "estimand": "Effect of intermediary centrality or sponsored-messenger routing on policy, comment, campaign, or procurement outcomes",
        "requiredEvidence": "Intermediary membership, grants, transfers, filings, public submissions, campaign activity, and actor-outcome linkage",
        "candidateSources": "IRS Form 990 XML; Schedule I/R; IRS 527 filings; NYC CFB intermediaries; think-tank grant disclosures; docket submitter records",
        "currentSupport": "NYC intermediary rows, IRS EO BMF capacity proxies, bounded IRS 527 rows, and top-EIN Schedule I rows",
        "status": "bounded_proxy_only",
        "permittedUse": "Intermediary capacity and routing diagnostics",
        "clearanceCriterion": "Representative intermediary network with routing, issue, and outcome linkage rather than capacity proxies alone",
        "nextAction": "Broaden Form 990 XML and 527 coverage, separate capacity from transfer routing, and link intermediaries to submissions or spending.",
        "upgradeTier": "second-wave",
        "firstStudyDesign": "Build an intermediary routing graph from transfers, filings, public submissions, and campaign activity, then test whether centrality predicts channel substitution or outcome pressure.",
        "minimumDataProduct": "Intermediary-actor-transfer rows, 527 filings, Form 990 Schedule I/R rows, docket or campaign links, issue tags, and a separated capacity-versus-routing classification.",
        "manuscriptImpact": "Would make the think-tank, association, and sponsored-messenger mechanisms more concrete and reduce reliance on capacity proxies.",
    },
    {
        "targetKey": "venue-shifting-detection-effect",
        "priority": "P2",
        "mechanism": "Cross-venue detection for movement among rulemaking, procurement, litigation, campaign, and lobbying arenas",
        "estimand": "Effect of cross-venue entity resolution and disclosure matching on detected substitution and total influence distortion",
        "requiredEvidence": "Shared actor identifiers across lobbying, campaign, docket, procurement, litigation, enforcement, and meeting-log records with issue and time windows",
        "candidateSources": "LDA; OpenFEC; Regulations.gov; Federal Register; USAspending/SAM; court/protest dockets; enforcement databases; meeting logs",
        "currentSupport": "Synthetic cross-venue detection index and source-specific identifiers",
        "status": "open_linkage_needed",
        "permittedUse": "Synthetic cross-venue detection diagnostics",
        "clearanceCriterion": "Entity-resolution spine linking at least three venues with audited false-positive/false-negative handling",
        "nextAction": "Build an identifier spine across LDA clients, FEC committees/spenders, docket submitters, vendors, and enforcement/protest actors.",
        "upgradeTier": "first-wave",
        "firstStudyDesign": "Create an auditable entity-resolution spine across three or more public venues and measure how much apparent substitution becomes visible when records are linked.",
        "minimumDataProduct": "Canonical actor identifiers linking LDA clients/registrants, FEC committees or spenders, docket submitters, vendors/UEIs, enforcement or protest actors, plus false-match audit samples.",
        "manuscriptImpact": "Would strengthen the venue-shifting detection claim and provide a practical measurement artifact for the model's cross-venue governance design argument.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    dependency_rows = read_csv(args.reports / CLAIM_SOURCE_DEPENDENCY.name)
    rows = target_rows(dependency_rows)
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "causal-calibration-targets.csv", rows)
    write_markdown(args.reports / "causal-calibration-targets.md", rows)
    print(f"Wrote {args.reports / 'causal-calibration-targets.csv'}")
    print(f"Wrote {args.reports / 'causal-calibration-targets.md'}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def target_rows(dependency_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dependency_status = {
        row.get("claimKey", ""): row.get("status", "")
        for row in dependency_rows
    }
    policy_status = dependency_status.get("calibrated-policy-simulation", "missing")
    rows: list[dict[str, str]] = []
    for target in TARGETS:
        row = dict(target)
        row["policyClaimStatus"] = policy_status
        row["blocksPolicySimulation"] = "yes" if target["status"] != "cleared" else "no"
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "targetKey",
        "priority",
        "upgradeTier",
        "mechanism",
        "estimand",
        "requiredEvidence",
        "candidateSources",
        "currentSupport",
        "status",
        "permittedUse",
        "clearanceCriterion",
        "nextAction",
        "firstStudyDesign",
        "minimumDataProduct",
        "manuscriptImpact",
        "policyClaimStatus",
        "blocksPolicySimulation",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = Counter(row["status"] for row in rows)
    priorities = Counter(row["priority"] for row in rows)
    tiers = Counter(row["upgradeTier"] for row in rows)
    blockers = [row for row in rows if row["blocksPolicySimulation"] == "yes"]
    upgrade_order = {"first-wave": 0, "second-wave": 1, "later": 2}
    row_order = {row["targetKey"]: index for index, row in enumerate(rows)}
    first_wave = [row for row in rows if row.get("upgradeTier") == "first-wave"]
    all_upgrades = sorted(
        rows,
        key=lambda row: (
            upgrade_order.get(row.get("upgradeTier", "later"), 99),
            row_order[row["targetKey"]],
        ),
    )
    lines = [
        "# Causal Calibration Targets",
        "",
        "This audit names the independent causal evidence required before the project can claim calibrated reform effects or representative national hidden-channel magnitudes. The current manuscript can use these rows as a policy-simulation boundary, not as evidence that the model estimates causal effects.",
        "",
        "## Summary",
        "",
        f"- Targets: `{len(rows)}`",
        f"- Blocking calibrated policy-simulation claims: `{len(blockers)}`",
        f"- P1 targets: `{priorities.get('P1', 0)}`",
        f"- P2 targets: `{priorities.get('P2', 0)}`",
        f"- First-wave empirical upgrades: `{tiers.get('first-wave', 0)}`",
        f"- Second-wave empirical upgrades: `{tiers.get('second-wave', 0)}`",
        f"- Cleared targets: `{counts.get('cleared', 0)}`",
        f"- Policy claim status: `{rows[0].get('policyClaimStatus', 'missing') if rows else 'missing'}`",
        "",
        "## Minimum Viable Causal Upgrade Path",
        "",
        "The first-wave rows are the shortest source-to-manuscript path for making the next version less dependent on synthetic stress tests. Clearing one of them would improve the empirical bridge for a specific mechanism; it would not clear calibrated policy-simulation claims unless the clearance criterion and claim-source dependencies also clear.",
        "",
        "| Target | Priority | First study design | Minimum data product | Manuscript impact |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in first_wave:
        lines.append(
            "| {targetKey} | {priority} | {firstStudyDesign} | {minimumDataProduct} | {manuscriptImpact} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Full Upgrade Queue",
            "",
            "| Target | Tier | Priority | Current support | First study design |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in all_upgrades:
        lines.append(
            "| {targetKey} | {upgradeTier} | {priority} | {currentSupport} | {firstStudyDesign} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Target Matrix",
            "",
            "| Target | Priority | Tier | Status | Estimand | Current support | Clearance criterion | Next action |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {targetKey} | {priority} | {upgradeTier} | {status} | {estimand} | {currentSupport} | {clearanceCriterion} | {nextAction} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Source Families",
            "",
        ]
    )
    for row in rows:
        lines.append(f"- `{row['targetKey']}`: {row['candidateSources']}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
