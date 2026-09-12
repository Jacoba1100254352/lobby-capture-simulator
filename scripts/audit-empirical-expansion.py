#!/usr/bin/env python3
"""Profile new empirical evidence without promoting it into causal calibration."""

import csv
import importlib.util
import json
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
REPORTS = ROOT / "reports"
FIELDS = ["item", "status", "evidence", "remainingRequirement"]


def read(name):
    with (DATA / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def report_period_diagnostics(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["committeeId"]].append(row)
    overlaps = gaps = straddles = 0
    for periods in groups.values():
        through = None
        for row in sorted(periods, key=lambda r: (r["periodStart"], r["periodEnd"])):
            start, end = date.fromisoformat(row["periodStart"]), date.fromisoformat(row["periodEnd"])
            if end < start:
                raise ValueError("Reversed report period")
            if through is not None:
                overlaps += start <= through
                gaps += start > through + timedelta(days=1)
            through = max(through, end) if through else end
            # Periods crossing a half-year cannot be allocated using their totals.
            straddles += (start.year, start.month > 6) != (end.year, end.month > 6)
    return overlaps, gaps, straddles


def protest_linkage_diagnostics(rows, sources, frozen):
    """Verify a selected decision-to-award bridge, never a protest-rate frame."""
    review = sources["gaoReview"]
    expected = set(review["piids"])
    if not rows or len(rows) != len(expected) or {r["piid"] for r in rows} != expected:
        raise ValueError("Missing, duplicate or off-cohort protest award links")
    searches = [sources["awardSearch"], sources["transactionSearch"]]
    for search in searches:
        if search["response"]["page_metadata"]["hasNext"]:
            raise ValueError("Incomplete selected-award source pagination")
        records = search["response"]["results"]
        if len(records) != len(expected) or {r["Award ID"] for r in records} != expected:
            raise ValueError("Selected source does not contain one record per pilot award")
    awards = {r["Award ID"]: r for r in searches[0]["response"]["results"]}
    actions = {r["Award ID"]: r for r in searches[1]["response"]["results"]}
    details = {r["response"]["piid"]: r["response"] for r in sources["awardDetails"]}
    if len(sources["awardDetails"]) != len(expected) or set(details) != expected:
        raise ValueError("Missing or duplicate selected-award detail records")
    bulk_records = sources["bulkExtract"]["records"]
    if len(bulk_records) != len(expected) or {r["piid"] for r in bulk_records} != expected:
        raise ValueError("Missing or duplicate archived bulk extract records")
    bulk = {r["piid"]: r for r in bulk_records}
    def normalize_name(value):
        return re.sub(r"[^A-Z0-9]", "", value.upper())
    candidate_matches = 0
    for row in rows:
        piid = row["piid"]
        award, action, detail = awards[piid], actions[piid], details[piid]
        if (row["decisionFamilyId"] != review["decisionFamilyId"]
                or row["decisionDate"] != review["decisionDate"]
                or row["filedDate"] or review["filedDate"] is not None
                or row["sourceRetrievedDate"] != sources["retrievedDate"]
                or row["linkageStatus"] != "source_linked_not_estimation_ready"
                or row["independentReviewStatus"] != review["independentReviewStatus"]):
            raise ValueError("Protest provenance or claim boundary mismatch")
        for record in (award, action):
            if (row["uei"] != record["Recipient UEI"]
                    or row["agency"] != record["Awarding Agency"]
                    or row["awardeeName"] != record["Recipient Name"]
                    or row["usaspendingAwardKey"] != record["generated_internal_id"]):
                raise ValueError("Protest award identity mismatch")
        if (row["agency"] != review["agency"]
                or normalize_name(row["awardeeName"]) != normalize_name(review["awardeeName"])
                or row["uei"] != detail["recipient"]["recipient_uei"]
                or row["parentPiid"] != detail["parent_award"]["piid"]
                or row["awardingSubtierCode"] != detail["awarding_agency"]["subtier_agency"]["code"]
                or row["usaspendingAwardKey"] != detail["generated_unique_award_id"]):
            raise ValueError("Decision or parent-award identity mismatch")
        if (row["originalActionDate"] != action["Action Date"]
                or row["originalActionDate"] != detail["date_signed"]
                or not "2023-10-01" <= row["originalActionDate"] <= "2024-09-30"
                or row["modificationNumber"] != action["Mod"] or action["Mod"] != "0"
                or row["performanceStartDate"] != detail["period_of_performance"]["start_date"]):
            raise ValueError("Original-action timing or modification mismatch")
        for field, value in (
                ("actionObligationDollars", action["Transaction Amount"]),
                ("currentAwardTotalObligationDollars", detail["total_obligation"])):
            amount = Decimal(row[field])
            if not amount.is_finite() or amount != Decimal(str(value)):
                raise ValueError("Action versus current-award amount mismatch")
        archived = bulk[piid]
        if (archived["agency"] != row["agency"] or archived["uei"] != row["uei"]
                or archived["actionDate"] != row["originalActionDate"]
                or archived["modificationNumber"] != row["modificationNumber"]
                or Decimal(archived["amount"]) * 1_000_000 != Decimal(row["actionObligationDollars"])):
            raise ValueError("Archived bulk versus live original-action mismatch")
        matches = sum(r["agency"] == row["agency"] and r["piid"] == piid for r in frozen)
        if int(row["frozenCandidateMatches"]) != matches:
            raise ValueError("Stale frozen-panel candidate match count")
        candidate_matches += matches
    return len(rows), len({r["decisionFamilyId"] for r in rows}), candidate_matches


def audit():
    findings = []
    def add(item, status, evidence, requirement):
        findings.append(dict(zip(FIELDS, (item, status, evidence, requirement))))
    lda = read("substitution-expanded-lda-panel.csv")
    if len({r["sourceRecordId"] for r in lda}) != len(lda):
        raise ValueError("Duplicate expanded LDA source-record keys")
    if any(r["exposureGroup"] != "unassigned_design_candidate" for r in lda):
        raise ValueError("Expanded acquisition must not assign treatment/control exposure")
    filings = {r["filingUuid"]: r for r in lda}
    periods = defaultdict(set)
    anomalies = []
    for row in filings.values():
        if row["dtPosted"][:10] < row["periodStart"]:
            anomalies.append(row["filingUuid"])
        if row["filingType"] not in {"RA", "RR"} and row["periodEnd"] < "2007-09-14":
            periods[row["canonicalActorId"]].add((row["periodStart"], row["periodEnd"]))
    add("expanded-lda-history", "source_only",
        f"issueRows={len(lda)}; filingUUIDs={len(filings)}; actors={len(set(r['canonicalActorId'] for r in lda))}; years={','.join(sorted(set(r['filingYear'] for r in lda)))}; observedPrePeriodsByActor=" + ";".join(f"{a}:{len(p)}" for a,p in sorted(periods.items())),
        "Validate amendments and exact actor identities; pre-period counts are native reporting periods, not independent quarters or proof of completeness.")
    add("lda-posting-date-anomaly", "review_required" if anomalies else "none_observed",
        f"postingBeforeCoveredPeriod={len(anomalies)}; filingUUIDs={';'.join(anomalies)}",
        "Review original filings and resolve API/scanned-form disagreements. One 2004 scan is reviewed in the redesign note; its amount is below-threshold, not an observed zero. Do not order amendments or treatment timing solely by dtPosted.")
    fec = read("substitution-fec-report-panel.csv")
    histories = read("substitution-fec-affiliation-history.csv")
    cohort = read("substitution-fec-acquisition-cohort.csv")
    if any(r["exposureGroup"] != "unassigned_design_candidate" for r in cohort):
        raise ValueError("FEC acquisition candidates must not assign treatment/control exposure")
    if not {r["canonicalActorId"] for r in cohort} <= {r["canonicalActorId"] for r in lda}:
        raise ValueError("FEC candidate actor absent from expanded LDA source")
    expected_histories = {(r["canonicalActorId"], r["committeeId"], str(year + year % 2)) for r in cohort for year in range(int(r["startYear"]), int(r["endYear"]) + 1)}
    if len(histories) != len(expected_histories) or {(r["canonicalActorId"], r["committeeId"], r["cycle"]) for r in histories} != expected_histories:
        raise ValueError("Missing, duplicate or off-cohort FEC historical affiliations")
    if len({(r['committeeId'], r['sourceRecordId']) for r in fec}) != len(fec):
        raise ValueError("Duplicate FEC filing keys")
    overlap, gaps, straddles = report_period_diagnostics(fec)
    missing = sum(r[field] == "" for r in fec for field in ("candidateContributionsDollars", "independentExpendituresDollars", "totalDisbursementsDollars"))
    add("alternate-channel-reports", "bounded_affiliation_candidate",
        f"reportRows={len(fec)}; committees={len(set(r['committeeId'] for r in fec))}; affiliationRows={len(histories)}; affiliationCycles={','.join(sorted({r['cycle'] for r in histories}))}; overlappingPeriods={overlap}; gapsBetweenReports={gaps}; halfYearStraddlingReports={straddles}; missingOutcomeCells={missing}",
        "Review historical sponsor links, form-specific measure definitions and report amendments. API amount formatting does not restore cents missing from source extraction. PAC availability does not establish comparable controls.")
    halfyears = read("substitution-fec-halfyear-panel.csv")
    coverage = read("substitution-fec-halfyear-coverage.csv")
    spec = importlib.util.spec_from_file_location("fec_coverage_audit", ROOT / "scripts/prepare-substitution-fec-periods.py")
    periods_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(periods_module)
    adjudications = read("substitution-fec-version-adjudications.csv")
    expected_halfyears, expected_coverage = periods_module.prepare_with_coverage(fec, cohort, adjudications)
    if halfyears != expected_halfyears or coverage != expected_coverage:
        raise ValueError("FEC prepared series or coverage ledger differs from raw-source reproduction")
    unresolved = [r for r in coverage if r["status"] != "observed_complete"]
    add("alternate-channel-coverage", "partial_outcome_coverage" if unresolved else "complete_source_periods_not_design",
        f"expectedCommitteeHalfYears={len(coverage)}; complete={len(halfyears)}; unresolvedOrMissing={len(unresolved)}; completeByCommittee=" + ";".join(f"{r['committeeId']}:{sum(h['committeeId'] == r['committeeId'] for h in halfyears)}" for r in cohort),
        "Keep all declared acquisition-frame periods visible; resolve Benefits Council versions, amounts and missing fields. AAJ 2008H2 uses a source-bound supplemental-loan-paperwork adjudication; independent review remains pending. Missing periods are not zero spending.")
    add("alternate-channel-halfyears", "observed_outcome_not_effect",
        f"completeHalfYears={len(halfyears)}; includedReportVersions={sum(int(r['reportCount']) for r in halfyears)}; sourceReviewedHalfYears={sum(bool(r['adjudicationIds']) for r in halfyears)}; eventClasses={dict(Counter(r['eventClass'] for r in halfyears))}",
        "Latest non-amended reports or explicit source-bound version adjudications, with no unresolved alternative version. Compare with native LDA periods after actor linkage and exposure validation; period completeness is not exhaustive source-image or causal validation.")
    corpus = read("comment-body-corpus.csv")
    if len({r['commentId'] for r in corpus}) != len(corpus):
        raise ValueError("Duplicate comment IDs")
    add("comment-corpus", "source_refreshed",
        f"rows={len(corpus)}; uniqueBodies={len(set(r['bodyText'] for r in corpus))}; emptyBodies={sum(not r['bodyText'] for r in corpus)}",
        "Verify receipt dates separately from posting dates and sample coverage before calculating docket-level rates.")
    pilot = read("comment-uptake-issue-pilot.csv")
    for row in pilot:
        if row["unit"] != "docket_issue" or row["commentId"] or row["responseSectionRead"] != "false":
            raise ValueError("Pilot must not pretend to contain individually linked or read RTC sections")
        if not row["sourcePage"] or not row["reviewDate"] or len(row["sourcePdfSha256"]) != 64:
            raise ValueError("Pilot source provenance missing")
    add("comment-uptake-pilot", "issue_level_only",
        f"observations={len(pilot)}; individualCommentLinks={sum(bool(r['commentId']) for r in pilot)}; changes=" + str(dict(Counter(r['disapprovalGroundChange'] for r in pilot))),
        "Retrieve full response document, link actual comments and complete independent coding review; do not compute an uptake rate from this purposive pilot.")
    protests = read("gao-protest-overlay.csv")
    reviewed = [r for r in protests if "Partial source-page review" in r["notes"]]
    add("gao-partial-adjudication", "not_award_linked",
        f"rows={len(protests)}; partiallyReviewed={len(reviewed)}; verifiedDecisionDates={sum(r['decisionDate'] != 'candidate_unreviewed' for r in protests)}",
        "Link decision-body dates and awarded PIID/UEI; a solicitation number is not a verified award key. No-match is not no-protest.")
    links = read("gao-award-linkage-pilot.csv")
    sources = json.loads((DATA / "gao-award-linkage-source.json").read_text(encoding="utf-8"))
    bulk_summary = json.loads((ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-bulk-summary.json").read_text(encoding="utf-8"))
    if (sources["bulkExtract"]["sourceSha256"] != bulk_summary["normalizedOutputSha256"]
            or sources["bulkExtract"]["sourceCreatedAt"] != bulk_summary["createdAt"]
            or sources["bulkExtract"]["sourceRowCount"] != bulk_summary["downloadedNormalizedRows"]):
        raise ValueError("Bulk pilot provenance differs from frozen bulk manifest")
    with (ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-actions.csv").open(newline="", encoding="utf-8") as source:
        frozen = list(csv.DictReader(source))
    linked, families, matches = protest_linkage_diagnostics(links, sources, frozen)
    partial_keys = Counter((r["agency"], r["piid"], r["modificationNumber"]) for r in frozen)
    add("procurement-frozen-frame", "selected_sample_partial_identifiers",
        f"rows={len(frozen)}; agencies={len({r['agency'] for r in frozen})}; actionDateRange={min(r['actionDate'] for r in frozen)}..{max(r['actionDate'] for r in frozen)}; repeatedPartialKeys={sum(n > 1 for n in partial_keys.values())}; rowsOnRepeatedPartialKeys={sum(n for n in partial_keys.values() if n > 1)}; exactDuplicateRows={len(frozen) - len({tuple(r.values()) for r in frozen})}",
        "Use the fiscal-year 2024 twelve-agency population, not a calendar-year EPA-only frame. Ranked page slices are not a probability sample. Preserve parent/subtier/source transaction identifiers and unrounded dollar obligations in the reconciliation source; repeated partial keys are not proven duplicate actions.")
    add("gao-time-aligned-award-pilot", "source_linked_not_estimation_ready",
        f"linkedAwards={linked}; consolidatedDecisions={families}; frozenPanelCandidateRows={matches}; archivedBulkMatches={len(sources['bulkExtract']['records'])}; observedOriginalActions={linked}; sourceVintage={sources['retrievedDate']}",
        "Obtain independent review, filed dates and a representative award/protest frame. Four awards in one selected consolidated decision are not four independent events; current award totals and latest offer fields are not original-action values.")
    add("overall", "not_identified",
        "New source history, PAC outcomes and issue-level comment coding exist; no provision-exposure control design, representative SAM export or historical exclusion overlay has cleared.",
        "Continue all three tracks. These findings are an interim source/design audit, not completion of the active empirical goal.")
    return findings


def main():
    rows = audit()
    REPORTS.mkdir(exist_ok=True)
    with (REPORTS / "empirical-expansion-audit.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Empirical expansion evidence audit", "", "Current committed source products; no causal-calibration promotion.", ""]
    for row in rows:
        lines.extend([f"## {row['item']}", "", f"Status: `{row['status']}`", "", row['evidence'], "", "Remaining: " + row['remainingRequirement'], ""])
    (REPORTS / "empirical-expansion-audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Audited {len(rows)} evidence/design checks; overall not identified.")


if __name__ == "__main__":
    main()
