#!/usr/bin/env python3
"""Profile new empirical evidence without promoting it into causal calibration."""

import csv
import importlib.util
from collections import Counter, defaultdict
from datetime import date, timedelta
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
