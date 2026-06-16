#!/usr/bin/env python3
"""Audit first-wave causal source products against executable schemas."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(".")
REPORTS = Path("reports")
TEMPLATE_ROOT = Path("docs/source-product-templates/first-wave")
PLACEHOLDER_VALUES = {
    "",
    "example",
    "example value",
    "placeholder",
    "sample",
    "tbd",
    "todo",
    "to do",
    "unknown",
    "n/a",
    "na",
    "none",
}
BOOLEAN_VALUES = {"true", "false", "yes", "no", "1", "0"}


@dataclass(frozen=True)
class ProductSpec:
    target_key: str
    product_key: str
    label: str
    priority: str
    requirement_level: str
    expected_path: str
    acceptable_sources: str
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...]
    minimum_rows: int
    validation_rule: str
    semantic_checks: tuple[str, ...]
    claim_boundary: str
    next_action: str
    text_required_terms: tuple[str, ...] = ()


PRODUCTS: tuple[ProductSpec, ...] = (
    ProductSpec(
        target_key="substitution-elasticity",
        product_key="substitution-reform-shocks",
        label="named reform-shock event file",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/substitution-reform-shocks.csv",
        acceptable_sources="state, municipal, federal, or agency reform records with an observed effective date",
        required_columns=(
            "reformEventId",
            "eventName",
            "jurisdiction",
            "policyDomain",
            "reformType",
            "eventDate",
            "treatmentStartDate",
            "affectedActorRule",
            "affectedIssueRule",
            "comparisonRule",
            "sourceUrl",
            "sourceExtractedAt",
        ),
        optional_columns=("legalCitation", "notes"),
        minimum_rows=1,
        validation_rule="CSV must define a named reform shock, affected actors/issues, a comparison rule, dates, and source provenance.",
        semantic_checks=(
            "at least one dated reform event",
            "nonempty treatment and comparison rules",
        ),
        claim_boundary="Required before estimating cross-channel substitution elasticity for a named reform family.",
        next_action="Choose one reform shock and encode actor, issue, treatment, comparison, and timing rules before linking outcomes.",
    ),
    ProductSpec(
        target_key="substitution-elasticity",
        product_key="actor-issue-time-spine",
        label="canonical actor-issue-time spine across at least three venues",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/actor-issue-time-spine.csv",
        acceptable_sources="LDA, OpenFEC, Regulations.gov/Federal Register, USAspending/SAM, meeting logs, nonprofit or intermediary rows",
        required_columns=(
            "canonicalActorId",
            "issueCode",
            "periodStart",
            "periodEnd",
            "venue",
            "activityType",
            "activityMeasure",
            "activityAmount",
            "sourceSystem",
            "sourceRecordId",
            "exposureGroup",
            "reformEventId",
        ),
        optional_columns=("activityUnits", "jurisdiction", "matchConfidence", "notes"),
        minimum_rows=100,
        validation_rule="CSV must link actors, issues, periods, venues, source records, and reform exposure.",
        semantic_checks=(
            "at least three distinct venues",
            "at least two analysis periods",
            "at least five canonical actors",
        ),
        claim_boundary="Required before visible-channel drops can be compared with movement into alternate venues.",
        next_action="Normalize at least three venues onto a common actor, issue, and period key.",
    ),
    ProductSpec(
        target_key="substitution-elasticity",
        product_key="substitution-comparison-groups",
        label="pre/post comparison groups for exposed and unaffected actors or jurisdictions",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/substitution-comparison-groups.csv",
        acceptable_sources="matched actor, issue, jurisdiction, or agency panels derived from the reform-shock file",
        required_columns=(
            "reformEventId",
            "canonicalActorId",
            "issueCode",
            "comparisonGroup",
            "matchingVariables",
            "prePeriodStart",
            "prePeriodEnd",
            "postPeriodStart",
            "postPeriodEnd",
        ),
        optional_columns=("matchScore", "exclusionReason", "notes"),
        minimum_rows=20,
        validation_rule="CSV must separate exposed, comparison, and excluded rows with pre/post windows.",
        semantic_checks=(
            "includes exposed or treated rows",
            "includes comparison or control rows",
            "pre and post windows are populated",
        ),
        claim_boundary="Required before substitution estimates can be distinguished from common shocks.",
        next_action="Define matched unaffected actors, issues, jurisdictions, or agencies and preserve exclusions.",
    ),
    ProductSpec(
        target_key="substitution-elasticity",
        product_key="meeting-log-or-missing-channel-note",
        label="meeting-log or contact-register panel, or explicit missing-channel design note",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/meeting-log-channel-note.md",
        acceptable_sources="machine-readable meeting logs, contact registers, calendars, visitor logs, or a missingness design note",
        required_columns=(),
        optional_columns=(),
        minimum_rows=0,
        validation_rule="Markdown note must explain meeting/contact availability, missingness, and how the omitted channel is handled.",
        semantic_checks=(
            "documented meeting/contact source search",
            "explicit missingness assessment",
            "substitution handling decision",
        ),
        claim_boundary="Required so substitution estimates do not silently ignore private-access movement.",
        next_action="Add a meeting/contact panel or document a defensible missing-channel design before estimation.",
        text_required_terms=("meeting", "missing", "substitution"),
    ),
    ProductSpec(
        target_key="procurement-modification-causal-capture",
        product_key="sam-fpds-action-history-crosswalk",
        label="SAM/FPDS action-history export or keyed pull",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/sam-fpds-action-history-crosswalk.csv",
        acceptable_sources="SAM.gov Contract Awards, FPDS, USAspending transaction rows, and importer crosswalk logs",
        required_columns=(
            "piid",
            "uei",
            "agency",
            "subtier",
            "recipientName",
            "actionDate",
            "actionObligation",
            "modificationNumber",
            "actionType",
            "extentCompeted",
            "numberOfOffers",
            "usaspendingRecordId",
            "samRecordId",
            "crosswalkConfidence",
        ),
        optional_columns=("awardType", "naics", "psc", "sourceUrl", "notes"),
        minimum_rows=5000,
        validation_rule="CSV must reconcile action dates, obligations, modifications, competition, offers, and source identifiers.",
        semantic_checks=(
            "at least 1000 distinct PIID/award identifiers",
            "at least six awarding agencies",
            "at least 270 days of action-date span",
            "nonempty action-obligation values",
        ),
        claim_boundary="Required before procurement modification rows can be treated as a causal outcome panel.",
        next_action="Use a promotable SAM/FPDS action-history export and reconcile modification coding with USAspending.",
    ),
    ProductSpec(
        target_key="procurement-modification-causal-capture",
        product_key="gao-protest-overlay",
        label="GAO protest overlay",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/gao-protest-overlay.csv",
        acceptable_sources="GAO bid protest decisions or archived protest metadata",
        required_columns=(
            "protestId",
            "piid",
            "uei",
            "agency",
            "filedDate",
            "decisionDate",
            "outcome",
            "issueCodes",
            "sourceUrl",
        ),
        optional_columns=("docketNumber", "protesterName", "awardeeName", "notes"),
        minimum_rows=25,
        validation_rule="CSV must link protests to awards, vendors, agencies, dates, outcomes, and source records.",
        semantic_checks=(
            "PIID or vendor linkage for each protest",
            "filed and decision dates populated",
            "outcome coding populated",
        ),
        claim_boundary="Required before protest exposure can be used as a procurement-integrity outcome or control.",
        next_action="Archive protest rows and link them to PIID/UEI where possible.",
    ),
    ProductSpec(
        target_key="procurement-modification-causal-capture",
        product_key="sam-exclusion-overlay",
        label="SAM exclusion overlay",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/sam-exclusion-overlay.csv",
        acceptable_sources="SAM.gov exclusions, agency suspension/debarment records, or archived exclusion extracts",
        required_columns=(
            "exclusionId",
            "uei",
            "recipientName",
            "exclusionType",
            "startDate",
            "endDate",
            "agency",
            "sourceUrl",
        ),
        optional_columns=("cause", "terminationDate", "notes"),
        minimum_rows=25,
        validation_rule="CSV must link exclusion status to vendor identifiers and dates.",
        semantic_checks=(
            "UEI linkage for each exclusion",
            "start and end dates populated",
            "exclusion type populated",
        ),
        claim_boundary="Required before exclusion status can be used to separate capture risk from integrity enforcement.",
        next_action="Add exclusion rows with UEI linkage and timing coverage.",
    ),
    ProductSpec(
        target_key="procurement-modification-causal-capture",
        product_key="procurement-firewall-overlay",
        label="procurement firewall or integrity-control overlay",
        priority="P1",
        requirement_level="required",
        expected_path="data/calibration/first-wave/procurement-firewall-overlay.csv",
        acceptable_sources="agency procurement-integrity rules, firewall memoranda, blind-review policies, or audit controls",
        required_columns=(
            "firewallRuleId",
            "agency",
            "subtier",
            "awardType",
            "effectiveDate",
            "coveredOfficials",
            "controlType",
            "sourceUrl",
        ),
        optional_columns=("expirationDate", "coverageRule", "notes"),
        minimum_rows=1,
        validation_rule="CSV must encode integrity controls, coverage, effective dates, and sources.",
        semantic_checks=(
            "at least one dated control rule",
            "agency and covered-official fields populated",
        ),
        claim_boundary="Required before procurement firewall reforms can be evaluated as observed institutional controls.",
        next_action="Encode agency/subtier controls and effective dates for the award classes in the procurement panel.",
    ),
    ProductSpec(
        target_key="comment-authenticity-and-uptake-effect",
        product_key="comment-body-corpus",
        label="comment-body corpus",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/comment-body-corpus.csv",
        acceptable_sources="Regulations.gov comments, agency docket files, or archived comment exports",
        required_columns=(
            "docketId",
            "commentId",
            "submitterName",
            "organization",
            "postedDate",
            "bodyText",
            "sourceUrl",
        ),
        optional_columns=("attachmentText", "withdrawn", "notes"),
        minimum_rows=500,
        validation_rule="CSV must preserve comment identifiers, submitter fields, posting dates, text, and source provenance.",
        semantic_checks=(
            "body text available for each comment",
            "at least one docket family",
            "source provenance populated",
        ),
        claim_boundary="Required before duplicate, authenticity, or uptake mechanisms can be estimated from observed comments.",
        next_action="Archive body-level comments for one docket family before clustering or response linkage.",
    ),
    ProductSpec(
        target_key="comment-authenticity-and-uptake-effect",
        product_key="duplicate-template-clusters",
        label="duplicate/template cluster assignments",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/comment-template-clusters.csv",
        acceptable_sources="deduplication scripts, agency duplicate-compression outputs, or reproducible text-clustering runs",
        required_columns=(
            "docketId",
            "commentId",
            "clusterId",
            "clusterMethod",
            "duplicateScore",
            "isTemplate",
            "technicalContentScore",
            "authenticitySignal",
        ),
        optional_columns=("clusterRepresentativeId", "reviewer", "notes"),
        minimum_rows=500,
        validation_rule="CSV must assign comments to duplicate/template clusters with method and score fields.",
        semantic_checks=(
            "at least two cluster identifiers",
            "duplicate scores are numeric",
            "template flags are boolean",
        ),
        claim_boundary="Required before comment flooding or authenticity filters can be treated as observed, not simulated, mechanisms.",
        next_action="Run duplicate/template detection and preserve method, thresholds, and uncertainty fields.",
    ),
    ProductSpec(
        target_key="comment-authenticity-and-uptake-effect",
        product_key="agency-response-final-rule-linkage",
        label="agency response text and final-rule linkage",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/agency-response-final-rule-linkage.csv",
        acceptable_sources="Federal Register final rules, agency response-to-comments documents, docket attachments, or agency rule files",
        required_columns=(
            "docketId",
            "commentId",
            "responseSectionId",
            "responseText",
            "finalRuleId",
            "finalRuleDate",
            "uptakeCode",
            "textSimilarity",
        ),
        optional_columns=("ruleCitation", "reviewer", "notes"),
        minimum_rows=50,
        validation_rule="CSV must link comment units to response sections and final-rule text movement.",
        semantic_checks=(
            "response section identifiers populated",
            "final-rule identifiers populated",
            "uptake coding populated",
        ),
        claim_boundary="Required before the model can compare comment authenticity with observed agency uptake.",
        next_action="Link clustered comments to response sections and final-rule language before estimating uptake effects.",
    ),
    ProductSpec(
        target_key="venue-shifting-detection-effect",
        product_key="canonical-actor-identifiers",
        label="canonical actor identifier table",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/canonical-actor-identifiers.csv",
        acceptable_sources="entity-resolution spine across LDA, FEC, docket, procurement, intermediary, and meeting-log identifiers",
        required_columns=(
            "canonicalActorId",
            "primaryName",
            "actorType",
            "ldaClientId",
            "fecCommitteeId",
            "uei",
            "docketSubmitterId",
            "intermediaryId",
            "sourceSystems",
        ),
        optional_columns=("parentActorId", "country", "state", "notes"),
        minimum_rows=100,
        validation_rule="CSV must preserve canonical IDs and source-system identifiers for cross-venue linkage.",
        semantic_checks=(
            "at least three represented source systems",
            "canonical actor identifiers are unique enough for linkage",
        ),
        claim_boundary="Required before venue-shifting detection can be interpreted as linked actor behavior.",
        next_action="Create a canonical actor spine and keep source-system identifiers auditable.",
    ),
    ProductSpec(
        target_key="venue-shifting-detection-effect",
        product_key="alias-resolution-audit-sample",
        label="alias-resolution rules and manual audit sample",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/alias-resolution-audit-sample.csv",
        acceptable_sources="manual review samples, entity-resolution logs, or source-specific alias tables",
        required_columns=(
            "auditId",
            "canonicalActorId",
            "aliasName",
            "sourceSystem",
            "sourceRecordId",
            "matchRule",
            "manualDecision",
            "reviewer",
            "reviewDate",
        ),
        optional_columns=("confidenceScore", "notes"),
        minimum_rows=50,
        validation_rule="CSV must record reviewed aliases, source records, match rules, decisions, and reviewer/date fields.",
        semantic_checks=(
            "manual decisions populated",
            "reviewer and review dates populated",
            "fuzzy and exact match rules represented where used",
        ),
        claim_boundary="Required before false matches can be bounded in venue-shifting estimates.",
        next_action="Sample fuzzy and exact matches, record manual decisions, and retain false-positive/false-negative examples.",
    ),
    ProductSpec(
        target_key="venue-shifting-detection-effect",
        product_key="issue-code-crosswalk",
        label="issue-code crosswalk across venues",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/issue-code-crosswalk.csv",
        acceptable_sources="LDA issue codes, docket terms, NAICS/PSC codes, FEC purpose terms, and manual issue ontology",
        required_columns=(
            "issueCode",
            "ldaIssueCode",
            "policyDomain",
            "docketTerms",
            "naicsCodes",
            "pscCodes",
            "fecPurposeTerms",
            "notes",
        ),
        optional_columns=("reviewer", "reviewDate"),
        minimum_rows=3,
        validation_rule="CSV must map issue concepts across lobbying, rulemaking, procurement, and electoral records.",
        semantic_checks=(
            "at least three issue concepts",
            "at least lobbying, rulemaking, procurement, and electoral mapping fields considered",
        ),
        claim_boundary="Required before movement across venues can be assigned to comparable issues.",
        next_action="Define a narrow issue ontology and crosswalk it across public source taxonomies.",
    ),
    ProductSpec(
        target_key="venue-shifting-detection-effect",
        product_key="false-match-review-log",
        label="false-positive and false-negative review log",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/false-match-review-log.csv",
        acceptable_sources="manual adjudication logs from entity-resolution and issue-matching runs",
        required_columns=(
            "reviewId",
            "canonicalActorId",
            "candidateRecordId",
            "sourceSystem",
            "issueCode",
            "decision",
            "errorType",
            "notes",
        ),
        optional_columns=("reviewer", "reviewDate", "confidenceScore"),
        minimum_rows=25,
        validation_rule="CSV must preserve reviewed linkage errors and decisions.",
        semantic_checks=(
            "positive and negative linkage decisions represented",
            "error type populated",
        ),
        claim_boundary="Required before cross-venue detection can report audited linkage uncertainty.",
        next_action="Audit positive and negative linkage samples and record error classes before promoting the panel.",
    ),
    ProductSpec(
        target_key="venue-shifting-detection-effect",
        product_key="linked-actor-issue-venue-time",
        label="linked actor-issue-venue-time output table",
        priority="P2",
        requirement_level="required",
        expected_path="data/calibration/first-wave/linked-actor-issue-venue-time.csv",
        acceptable_sources="derived panel from the canonical actor table, issue crosswalk, and venue source records",
        required_columns=(
            "canonicalActorId",
            "issueCode",
            "venue",
            "periodStart",
            "periodEnd",
            "activityType",
            "activityMeasure",
            "sourceSystem",
            "sourceRecordId",
            "matchConfidence",
        ),
        optional_columns=("activityAmount", "jurisdiction", "notes"),
        minimum_rows=500,
        validation_rule="CSV must be the auditable linked panel used by venue-shifting diagnostics.",
        semantic_checks=(
            "at least three distinct venues",
            "linked source records populated",
            "match-confidence values are numeric",
        ),
        claim_boundary="Required before single-source and linked multi-venue diagnostics can be compared.",
        next_action="Generate the linked actor-issue-venue-time panel after actor and issue linkage pass manual audit.",
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    rows = [audit_product(args.root, spec) for spec in PRODUCTS]
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "first-wave-source-products.csv", rows)
    write_markdown(args.reports / "first-wave-source-products.md", rows)
    print(f"Wrote {args.reports / 'first-wave-source-products.csv'}")
    print(f"Wrote {args.reports / 'first-wave-source-products.md'}")
    return 0


def audit_product(root: Path, spec: ProductSpec) -> dict[str, str]:
    path = root / spec.expected_path
    if not path.exists():
        status = "missing_required" if spec.requirement_level == "required" else "missing_optional"
        observed_rows = ""
        observed_columns: tuple[str, ...] = ()
        missing_columns = spec.required_columns
        quality_issues = 0
        semantic_issues: tuple[str, ...] = ()
        validation_notes = "Expected source product is not present."
    elif path.suffix.lower() == ".csv":
        observed_rows, observed_columns, missing_columns, quality_issues, semantic_issues, validation_notes = audit_csv(path, spec)
        if missing_columns:
            status = "schema_missing_columns"
        elif observed_rows < spec.minimum_rows:
            status = "empty_schema"
            validation_notes = (
                f"Schema columns are present, but observed rows {observed_rows} "
                f"are below minimum {spec.minimum_rows}."
            )
        elif quality_issues or semantic_issues:
            status = "schema_quality_issues"
        else:
            status = "schema_ready"
    else:
        observed_rows, observed_columns, missing_columns, validation_notes = audit_text(path, spec)
        quality_issues = 0
        semantic_issues = ()
        status = "text_missing_terms" if missing_columns else "text_ready"

    return {
        "targetKey": spec.target_key,
        "productKey": spec.product_key,
        "productLabel": spec.label,
        "priority": spec.priority,
        "requirementLevel": spec.requirement_level,
        "expectedPath": spec.expected_path,
        "templatePath": template_path_for(spec),
        "acceptableSources": spec.acceptable_sources,
        "requiredColumns": "; ".join(spec.required_columns) if spec.required_columns else "text terms: " + "; ".join(spec.text_required_terms),
        "optionalColumns": "; ".join(spec.optional_columns),
        "minimumRows": str(spec.minimum_rows),
        "productStatus": status,
        "observedRows": str(observed_rows) if observed_rows != "" else "",
        "observedColumns": "; ".join(observed_columns),
        "missingColumns": "; ".join(missing_columns),
        "qualityIssueCount": str(quality_issues),
        "semanticIssueCount": str(len(semantic_issues)),
        "semanticChecks": "; ".join(spec.semantic_checks),
        "semanticIssues": "; ".join(semantic_issues),
        "validationRule": spec.validation_rule,
        "validationNotes": validation_notes,
        "claimBoundary": spec.claim_boundary,
        "nextAction": spec.next_action,
    }


def audit_csv(path: Path, spec: ProductSpec) -> tuple[int, tuple[str, ...], tuple[str, ...], int, tuple[str, ...], str]:
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            observed_columns = tuple(reader.fieldnames or ())
            rows = list(reader)
    except OSError as error:
        return 0, (), spec.required_columns, 1, (), f"Could not read CSV: {error}"
    observed = set(observed_columns)
    missing = tuple(column for column in spec.required_columns if column not in observed)
    if missing:
        note = "Missing required schema columns."
    else:
        quality_issues = csv_quality_issues(rows, spec)
        semantic_issues = semantic_quality_issues(rows, spec)
        if quality_issues or semantic_issues:
            fragments = []
            if quality_issues:
                fragments.append(f"{quality_issues} field-level quality issues")
            if semantic_issues:
                fragments.append(f"{len(semantic_issues)} semantic gate issues: {', '.join(semantic_issues)}")
            note = "Required schema columns are present, but " + "; ".join(fragments) + "."
        else:
            note = "Required schema columns, field-level quality checks, and semantic gates pass."
        return len(rows), observed_columns, missing, quality_issues, semantic_issues, note
    return len(rows), observed_columns, missing, 0, (), note


def csv_quality_issues(rows: list[dict[str, str]], spec: ProductSpec) -> int:
    issues = 0
    for row in rows:
        for column in spec.required_columns:
            value = normalize_cell(row.get(column, ""))
            lowered = value.lower()
            if lowered in PLACEHOLDER_VALUES:
                issues += 1
                continue
            if is_date_column(column) and not is_valid_date(value):
                issues += 1
            if is_url_column(column) and not is_valid_url(value):
                issues += 1
            if is_numeric_column(column) and not is_valid_number(value):
                issues += 1
            if is_boolean_column(column) and lowered not in BOOLEAN_VALUES:
                issues += 1
        for column in spec.optional_columns:
            value = normalize_cell(row.get(column, ""))
            if not value:
                continue
            lowered = value.lower()
            if lowered in {"todo", "tbd", "placeholder", "example", "sample"}:
                issues += 1
            if is_date_column(column) and not is_valid_date(value):
                issues += 1
            if is_url_column(column) and not is_valid_url(value):
                issues += 1
            if is_numeric_column(column) and not is_valid_number(value):
                issues += 1
            if is_boolean_column(column) and lowered not in BOOLEAN_VALUES:
                issues += 1
    return issues


def semantic_quality_issues(rows: list[dict[str, str]], spec: ProductSpec) -> tuple[str, ...]:
    """Return product-level gate failures that row/field checks cannot see."""
    if not rows:
        return ()
    checks: list[str] = []
    product = spec.product_key
    if product == "actor-issue-time-spine":
        checks.extend([
            distinct_check(rows, "venue", 3, "fewer than three distinct venues"),
            distinct_check(rows, "periodStart", 2, "fewer than two analysis periods"),
            distinct_check(rows, "canonicalActorId", 5, "fewer than five canonical actors"),
        ])
    elif product == "substitution-comparison-groups":
        groups = {normalize_cell(row.get("comparisonGroup", "")).lower() for row in rows}
        if not any(token in group for group in groups for token in ("exposed", "treated", "treatment")):
            checks.append("no exposed or treated comparison-group rows")
        if not any(token in group for group in groups for token in ("comparison", "control", "unaffected")):
            checks.append("no comparison or control rows")
    elif product == "sam-fpds-action-history-crosswalk":
        checks.extend([
            distinct_check(rows, "piid", 1000, "fewer than 1000 distinct PIID/award identifiers"),
            distinct_check(rows, "agency", 6, "fewer than six awarding agencies"),
        ])
        span = date_span_days(rows, "actionDate")
        if span < 270:
            checks.append(f"action-date span {span} days is below 270")
        if value_share(rows, "actionObligation") < 0.80:
            checks.append("action-obligation coverage below 0.80")
    elif product == "comment-template-clusters":
        checks.append(distinct_check(rows, "clusterId", 2, "fewer than two template/duplicate clusters"))
    elif product == "canonical-actor-identifiers":
        systems = source_system_values(rows)
        if len(systems) < 3:
            checks.append("fewer than three represented source systems")
    elif product == "alias-resolution-audit-sample":
        checks.append(distinct_check(rows, "matchRule", 1, "no match rule represented"))
    elif product == "issue-code-crosswalk":
        checks.append(distinct_check(rows, "issueCode", 3, "fewer than three issue concepts"))
    elif product == "false-match-review-log":
        decisions = {normalize_cell(row.get("decision", "")).lower() for row in rows}
        positive = {"accept", "accepted", "match", "matched", "true_positive", "true positive"}
        negative = {"reject", "rejected", "nonmatch", "non-match", "false_positive", "false positive", "false_negative", "false negative"}
        if not decisions & positive:
            checks.append("no positive linkage decisions represented")
        if not decisions & negative:
            checks.append("no negative or error linkage decisions represented")
    elif product == "linked-actor-issue-venue-time":
        checks.extend([
            distinct_check(rows, "venue", 3, "fewer than three distinct venues"),
            distinct_check(rows, "canonicalActorId", 5, "fewer than five canonical actors"),
        ])
    return tuple(check for check in checks if check)


def distinct_check(rows: list[dict[str, str]], column: str, minimum: int, message: str) -> str:
    return "" if len(distinct_values(rows, column)) >= minimum else message


def distinct_values(rows: list[dict[str, str]], column: str) -> set[str]:
    return {
        value
        for value in (normalize_cell(row.get(column, "")) for row in rows)
        if value and value.lower() not in PLACEHOLDER_VALUES
    }


def date_span_days(rows: list[dict[str, str]], column: str) -> int:
    dates = [
        parsed
        for parsed in (parse_iso_date(normalize_cell(row.get(column, ""))) for row in rows)
        if parsed is not None
    ]
    if len(dates) < 2:
        return 0
    return (max(dates) - min(dates)).days


def parse_iso_date(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def value_share(rows: list[dict[str, str]], column: str) -> float:
    if not rows:
        return 0.0
    present = [
        row for row in rows
        if normalize_cell(row.get(column, "")).lower() not in PLACEHOLDER_VALUES
    ]
    return len(present) / len(rows)


def source_system_values(rows: list[dict[str, str]]) -> set[str]:
    systems: set[str] = set()
    for row in rows:
        value = normalize_cell(row.get("sourceSystems", ""))
        for part in re_split_source_systems(value):
            normalized = part.strip().lower()
            if normalized and normalized not in PLACEHOLDER_VALUES:
                systems.add(normalized)
    return systems


def re_split_source_systems(value: str) -> list[str]:
    normalized = value.replace("|", ";").replace(",", ";")
    return normalized.split(";")


def normalize_cell(value: str | None) -> str:
    return "" if value is None else str(value).strip()


def is_date_column(column: str) -> bool:
    lowered = column.lower()
    return (
        lowered.endswith("date")
        or lowered.endswith("at")
        or "periodstart" in lowered
        or "periodend" in lowered
    )


def is_url_column(column: str) -> bool:
    return column.lower().endswith("url")


def is_numeric_column(column: str) -> bool:
    lowered = column.lower()
    return any(
        marker in lowered
        for marker in (
            "amount",
            "obligation",
            "score",
            "share",
            "confidence",
            "similarity",
            "numberofoffers",
            "measure",
        )
    )


def is_boolean_column(column: str) -> bool:
    lowered = column.lower()
    return lowered.startswith("is") or lowered in {"withdrawn"}


def is_valid_date(value: str) -> bool:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        datetime.fromisoformat(normalized)
        return True
    except ValueError:
        return False


def is_valid_url(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith("https://") or lowered.startswith("http://")


def is_valid_number(value: str) -> bool:
    try:
        float(value.replace(",", ""))
        return True
    except ValueError:
        return False


def audit_text(path: Path, spec: ProductSpec) -> tuple[int, tuple[str, ...], tuple[str, ...], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return 0, (), spec.text_required_terms, f"Could not read text source product: {error}"
    lowered = text.lower()
    missing_terms = tuple(term for term in spec.text_required_terms if term.lower() not in lowered)
    observed_terms = tuple(term for term in spec.text_required_terms if term.lower() in lowered)
    if missing_terms:
        note = "Text source product is missing required terms."
    else:
        note = "Text source product contains the required missing-channel design terms."
    return len([line for line in text.splitlines() if line.strip()]), observed_terms, missing_terms, note


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "targetKey",
        "productKey",
        "productLabel",
        "priority",
        "requirementLevel",
        "expectedPath",
        "templatePath",
        "acceptableSources",
        "requiredColumns",
        "optionalColumns",
        "minimumRows",
        "productStatus",
        "observedRows",
        "observedColumns",
        "missingColumns",
        "qualityIssueCount",
        "semanticIssueCount",
        "semanticChecks",
        "semanticIssues",
        "validationRule",
        "validationNotes",
        "claimBoundary",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    ready = [row for row in rows if row["productStatus"] in {"schema_ready", "text_ready"}]
    missing = [row for row in rows if row["productStatus"].startswith("missing")]
    schema_issues = [
        row for row in rows
        if row["productStatus"] not in {"schema_ready", "text_ready"}
        and not row["productStatus"].startswith("missing")
    ]
    quality_issue_products = [
        row for row in rows
        if row.get("qualityIssueCount", "0") not in {"", "0"}
    ]
    semantic_issue_products = [
        row for row in rows
        if row.get("semanticIssueCount", "0") not in {"", "0"}
    ]
    target_keys = sorted({row["targetKey"] for row in rows})
    ready_targets = [
        target for target in target_keys
        if all(
            row["productStatus"] in {"schema_ready", "text_ready"}
            for row in rows
            if row["targetKey"] == target and row["requirementLevel"] == "required"
        )
    ]
    lines = [
        "# First-Wave Source Products",
        "",
        "This generated schema/acquisition gate turns the first-wave causal protocols into concrete source products. It checks whether each required file exists, whether CSV columns or text terms match the expected schema, and whether a product has enough rows to be usable for estimation. Passing this gate would still not clear calibrated policy-simulation claims without the protocol-specific causal design and claim-source audits.",
        "",
        "## Summary",
        "",
        f"- Source products audited: `{len(rows)}`",
        f"- Schema/text ready products: `{len(ready)}`",
        f"- Missing products: `{len(missing)}`",
        f"- Present products with schema issues: `{len(schema_issues)}`",
        f"- Products with field-level quality issues: `{len(quality_issue_products)}`",
        f"- Products with semantic gate issues: `{len(semantic_issue_products)}`",
        f"- Targets with all required products ready: `{len(ready_targets)}`",
        "- Policy-simulation status: `not_cleared`",
        "",
        "## Product Matrix",
        "",
        "| Target | Product | Status | Expected path | Template path | Required schema | Minimum rows | Semantic checks | Next action |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {targetKey} | {productLabel} | {productStatus} | `{expectedPath}` | `{templatePath}` | {requiredColumns} | {minimumRows} | {semanticChecks} | {nextAction} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Semantic Gate Notes",
        "",
        "Semantic checks are product-level safeguards that prevent tiny or structurally incomplete files from clearing a causal source gate merely because required columns are present.",
        "",
        "| Target | Product | Semantic issue count | Semantic issues | Validation notes |",
        "| --- | --- | ---: | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {targetKey} | {productLabel} | {semanticIssueCount} | {semanticIssues} | {validationNotes} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Product Boundaries",
        "",
        "| Target | Product | Acceptable sources | Validation rule | Claim boundary |",
        "| --- | --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            "| {targetKey} | {productLabel} | {acceptableSources} | {validationRule} | {claimBoundary} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def template_path_for(spec: ProductSpec) -> str:
    return (TEMPLATE_ROOT / Path(spec.expected_path).name).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
