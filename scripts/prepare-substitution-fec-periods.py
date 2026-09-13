#!/usr/bin/env python3
"""Prepare complete native half-years from latest FEC report periods.

This is an observed alternate-channel outcome, not a substitution estimator.
Amended and unknown-version rows remain in the raw acquisition snapshot.
"""

import csv
import hashlib
import importlib.util
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
MEASURES = ["candidateContributionsDollars", "independentExpendituresDollars", "totalDisbursementsDollars"]
FIELDS = ["canonicalActorId", "committeeId", "halfYear", "periodStart", "periodEnd", "reportCount", "completeCoverage", "eventClass", *MEASURES, "sourceRecordIds", "selectionBasis", "adjudicationIds", "linkStatus", "claimBoundary"]
COVERAGE_FIELDS = ["canonicalActorId", "committeeId", "halfYear", "periodStart", "periodEnd", "status", "reasonCodes", "rawReportCount", "latestReportCount", "eligibleReportCount", "acceptedReportCount", "missingRawOutcomeCells", "unknownVersionRecordIds", "sourceRecordIds", "adjudicationIds", "detail", "claimBoundary"]


class PeriodError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def is_latest(row):
    return row["mostRecent"] == "true" and row["isAmended"] == "false"


def prepare(rows):
    selected = [r for r in rows if is_latest(r)]
    groups = defaultdict(list)
    for row in selected:
        start, end = date.fromisoformat(row["periodStart"]), date.fromisoformat(row["periodEnd"])
        half = 1 if start.month <= 6 else 2
        if (start.year, half) != (end.year, 1 if end.month <= 6 else 2):
            raise PeriodError("straddling_report", "FEC report straddles half-years; transaction dates required")
        if end < start:
            raise PeriodError("reversed_period", "Reversed FEC coverage period")
        groups[(row["canonicalActorId"], row["committeeId"], start.year, half)].append(row)
    prepared = []
    for (actor, committee, year, half), reports in sorted(groups.items()):
        start = date(year, 1 if half == 1 else 7, 1)
        end = date(year, 6, 30) if half == 1 else date(year, 12, 31)
        expected = start
        for row in sorted(reports, key=lambda r: r["periodStart"]):
            if date.fromisoformat(row["periodStart"]) != expected:
                raise PeriodError("gap_or_overlap", "Gap or overlap in selected FEC reports; no complete half-year")
            expected = date.fromisoformat(row["periodEnd"]) + timedelta(days=1)
        if expected != end + timedelta(days=1):
            raise PeriodError("incomplete_trailing_coverage", "Incomplete trailing FEC half-year coverage")
        if any(not row[field] for row in reports for field in MEASURES):
            raise PeriodError("missing_outcome", "Missing FEC outcome is not an observed zero")
        result = {
            "canonicalActorId": actor, "committeeId": committee,
            "halfYear": f"{year}H{half}", "periodStart": start.isoformat(), "periodEnd": end.isoformat(),
            "reportCount": str(len(reports)), "completeCoverage": "true",
            "eventClass": "pre" if end < date(2007,9,14) else "post" if start > date(2007,9,14) else "straddles_event_excluded",
            "sourceRecordIds": ";".join(sorted(r["sourceRecordId"] for r in reports)),
            "selectionBasis": "api_flags", "adjudicationIds": "",
            "linkStatus": "historical_affiliation_candidate",
            "claimBoundary": "Observed PAC half-year totals only; no treatment/control design or causal substitution effect; affiliation and principal funding identity remain separate.",
        }
        for field in MEASURES:
            amounts = [Decimal(row[field]) for row in reports]
            if any(not value.is_finite() for value in amounts):
                raise PeriodError("nonfinite_outcome", "Nonfinite FEC outcome")
            result[field] = format(sum(amounts), ".2f")
        prepared.append(result)
    return prepared, len(rows) - len(selected)


def record_fingerprint(row):
    """Bind adjudication to source contents, excluding retrieval time and prose."""
    fields = ["canonicalActorId", "committeeId", "sourceRecordId", "periodStart", "periodEnd", "receiptDate", "amendmentIndicator", "mostRecent", "isAmended", "amendmentChain", *MEASURES]
    return hashlib.sha256(json.dumps({f: row.get(f, "") for f in fields}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def apply_adjudications(rows, reviews):
    """Narrow, source-bound exception for supplemental loan paperwork only.

    Raw acquisition flags and values are never edited. A changed report forces
    renewed review rather than silently reusing an old version decision.
    """
    effective = {(r["committeeId"], r["sourceRecordId"]): dict(r) for r in rows}
    touched, ids = set(), set()
    for review in reviews:
        parent_key = (review["committeeId"], review["retainedRecordId"])
        supplement_key = (review["committeeId"], review["supplementRecordId"])
        if not review["adjudicationId"] or review["adjudicationId"] in ids or parent_key == supplement_key or touched.intersection([parent_key, supplement_key]):
            raise ValueError("Duplicate or overlapping FEC adjudication")
        ids.add(review["adjudicationId"])
        touched.update([parent_key, supplement_key])
        if parent_key not in effective or supplement_key not in effective:
            raise ValueError("Adjudicated FEC source record missing")
        parent, supplement = effective[parent_key], effective[supplement_key]
        if review["decision"] != "supplemental_loan_paperwork_only" or not review["reviewer"] or not review["rationale"]:
            raise ValueError("Incomplete or unsupported FEC version adjudication")
        date.fromisoformat(review["reviewDate"])
        for prefix in ("retained", "supplement"):
            if not re.fullmatch(r"[0-9a-f]{64}", review[f"{prefix}PdfSha256"]) or not review[f"{prefix}PagesReviewed"] or not review[f"{prefix}SourceUrl"].startswith("https://docquery.fec.gov/pdf/"):
                raise ValueError("Missing FEC adjudication primary-source provenance")
        if record_fingerprint(parent) != review["retainedRecordFingerprint"] or record_fingerprint(supplement) != review["supplementRecordFingerprint"]:
            raise ValueError("FEC adjudication stale: source contents changed")
        if any(parent[f] != supplement[f] or parent[f] != review[f] for f in ("canonicalActorId", "periodStart", "periodEnd")):
            raise ValueError("FEC supplement identity/coverage mismatch")
        if parent["mostRecent"] != "true" or parent["isAmended"] != "true" or supplement["mostRecent"] not in {"none", ""} or supplement["isAmended"] != "false" or supplement["amendmentIndicator"] != "A" or any(supplement[f] for f in MEASURES):
            raise ValueError("FEC supplement adjudication does not match the reviewed source condition")
        parent["isAmended"] = "false"
        supplement["mostRecent"] = "false"
        for row in (parent, supplement):
            row["adjudicationId"] = review["adjudicationId"]
    return effective


def paper_version_review(rows, review):
    spec = importlib.util.spec_from_file_location("fec_paper_review", ROOT / "scripts/review-substitution-fec-paper.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_review(rows, review)


def prepare_with_coverage(rows, cohort, adjudications=(), paper_review=None):
    """Retain every expected committee-half-year, including unavailable outcomes.

    The cohort is an explicit acquisition frame, not a treatment/control frame.
    Invalid structure aborts the build. Source gaps quarantine only the affected
    native half-years and must appear in the companion coverage ledger.
    """
    bounds = {}
    for member in cohort:
        key = (member["canonicalActorId"], member["committeeId"])
        first, last = int(member["startYear"]), int(member["endYear"])
        if not all(key) or first > last or key in bounds:
            raise ValueError("Invalid or duplicate FEC acquisition cohort member")
        bounds[key] = (date(first, 1, 1), date(last, 12, 31))
    if not bounds or len({key[1] for key in bounds}) != len(bounds):
        raise ValueError("FEC cohort must give each committee exactly one candidate actor")
    keys = [(r["committeeId"], r["sourceRecordId"]) for r in rows]
    if len(set(keys)) != len(keys) or any(not source_id for _, source_id in keys):
        raise ValueError("Empty or duplicate FEC source-record key")
    grouped = defaultdict(list)
    for row in rows:
        key = (row["canonicalActorId"], row["committeeId"])
        if key not in bounds:
            raise ValueError("FEC source row outside acquisition cohort")
        start, end = date.fromisoformat(row["periodStart"]), date.fromisoformat(row["periodEnd"])
        lower, upper = bounds[key]
        if end < start or start < lower or end > upper:
            raise ValueError("Invalid or out-of-frame FEC source period")
        if any(row[field] not in {"true", "false", "none", ""} for field in ("mostRecent", "isAmended")):
            raise ValueError("Unexpected FEC version flag")
        grouped[key].append(row)
    effective = apply_adjudications(rows, adjudications)
    if paper_review is not None:
        decisions, paper_checks = paper_version_review(rows, paper_review)
        for source_id, most_recent in decisions.items():
            row = effective[(paper_review["committeeId"], source_id)]
            if row.get("adjudicationId"):
                raise ValueError("Overlapping FEC supplement and paper-version reviews")
            row["mostRecent"] = str(most_recent).lower()
            row["paperVersionReviewId"] = paper_review["reviewId"]
            row["sourcePeriodConflict"] = source_id in paper_checks["periodConflictReportIds"]
    prepared, coverage = [], []
    for (actor, committee), (lower, upper) in sorted(bounds.items()):
        for year in range(lower.year, upper.year + 1):
            for half in (1, 2):
                start = date(year, 1 if half == 1 else 7, 1)
                end = date(year, 6, 30) if half == 1 else date(year, 12, 31)
                # Cross-half-year reports affect every intersected half-year.
                native = [r for r in grouped[(actor, committee)] if r["periodStart"] <= end.isoformat() and r["periodEnd"] >= start.isoformat()]
                resolved = [effective[(r["committeeId"], r["sourceRecordId"])] for r in native]
                review_ids = ";".join(sorted({r[field] for r in resolved for field in ("adjudicationId", "paperVersionReviewId") if r.get(field)}))
                paper_versions = any(r.get("paperVersionReviewId") for r in resolved)
                latest = [r for r in resolved if is_latest(r)]
                unknown = [r for r in resolved if not is_latest(r) and r["mostRecent"] != "false" and r["isAmended"] != "true"]
                reasons, detail, candidate = [], [], []
                if not native:
                    reasons.append("missing_reports")
                    detail.append("No acquired report for this expected half-year; not zero spending.")
                else:
                    if any(r.get("sourcePeriodConflict") for r in resolved):
                        reasons.append("source_period_conflict")
                        detail.append("Dated itemized transactions extend beyond the report header's end date. The raw-date gap is not evidence of absent activity; no corrected coverage end is established.")
                    if unknown:
                        reasons.append("unresolved_version")
                        detail.append("A non-superseded report lacks an affirmative latest/non-amended designation.")
                    if not latest:
                        reasons.append("no_latest_reports")
                    else:
                        try:
                            candidate, _ = prepare(resolved)
                        except PeriodError as error:
                            reasons.append(error.code)
                            detail.append(str(error))
                accepted = bool(candidate) and not reasons
                if paper_versions:
                    detail.append("Version flags reconciled from the source-bound filings endpoint; raw report flags, dates and amounts are unchanged. Financial-source validation remains separate.")
                if accepted:
                    if len(candidate) != 1 or candidate[0]["halfYear"] != f"{year}H{half}":
                        raise ValueError("Unexpected FEC partition result")
                    candidate[0]["adjudicationIds"] = review_ids
                    if review_ids:
                        candidate[0]["selectionBasis"] = "cross_endpoint_version_flags" if paper_versions else "source_reviewed_supplement"
                    prepared.extend(candidate)
                coverage.append({
                    "canonicalActorId": actor, "committeeId": committee,
                    "halfYear": f"{year}H{half}", "periodStart": start.isoformat(), "periodEnd": end.isoformat(),
                    "status": "observed_complete" if accepted else "missing_source" if not native else "unresolved",
                    "reasonCodes": ";".join(reasons), "rawReportCount": str(len(native)),
                    "latestReportCount": str(sum(is_latest(r) for r in native)), "eligibleReportCount": str(len(latest)), "acceptedReportCount": str(len(latest) if accepted else 0),
                    "missingRawOutcomeCells": str(sum(not r[field] for r in native for field in MEASURES)),
                    "unknownVersionRecordIds": ";".join(sorted(r["sourceRecordId"] for r in unknown)),
                    "sourceRecordIds": ";".join(sorted(r["sourceRecordId"] for r in native)),
                    "adjudicationIds": review_ids,
                    "detail": " ".join(detail) if detail else "Complete report coverage with source-reviewed supplement adjudication." if accepted and review_ids else "Complete source-marked report coverage." if accepted else "No usable latest reports.",
                    "claimBoundary": "Acquisition-frame coverage only; unresolved outcomes are not zeros; no treatment/control assignment or causal effect.",
                })
    return prepared, coverage


def main():
    with (DATA / "substitution-fec-report-panel.csv").open(newline="", encoding="utf-8") as source:
        raw = list(csv.DictReader(source))
    with (DATA / "substitution-fec-acquisition-cohort.csv").open(newline="", encoding="utf-8") as source:
        cohort = list(csv.DictReader(source))
    with (DATA / "substitution-fec-version-adjudications.csv").open(newline="", encoding="utf-8") as source:
        adjudications = list(csv.DictReader(source))
    paper_review = json.loads((DATA / "substitution-fec-paper-review.json").read_text())
    rows, coverage = prepare_with_coverage(raw, cohort, adjudications, paper_review)
    for name, records, fields in [
        ("substitution-fec-halfyear-panel.csv", rows, FIELDS),
        ("substitution-fec-halfyear-coverage.csv", coverage, COVERAGE_FIELDS),
    ]:
        with (DATA / name).open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
    print(f"Prepared {len(rows)} of {len(coverage)} expected native half-years; unresolved/missing periods remain in the coverage ledger.")


if __name__ == "__main__":
    main()
