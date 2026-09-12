#!/usr/bin/env python3
"""Profile new empirical evidence without promoting it into causal calibration."""

import csv
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
    if len({r['sourceRecordId'] for r in fec}) != len(fec):
        raise ValueError("Duplicate FEC filing keys")
    overlap, gaps, straddles = report_period_diagnostics(fec)
    missing = sum(r[field] == "" for r in fec for field in ("candidateContributionsDollars", "independentExpendituresDollars", "totalDisbursementsDollars"))
    add("alternate-channel-reports", "bounded_affiliation_candidate",
        f"reportRows={len(fec)}; committees={len(set(r['committeeId'] for r in fec))}; affiliationCycles={','.join(r['cycle'] for r in histories)}; overlappingPeriods={overlap}; gapsBetweenReports={gaps}; halfYearStraddlingReports={straddles}; missingOutcomeCells={missing}",
        "Review historical sponsor links and report amendments; obtain transaction dates for straddling periods; one PAC cannot supply treatment-control identification.")
    halfyears = read("substitution-fec-halfyear-panel.csv")
    add("alternate-channel-halfyears", "observed_outcome_not_effect",
        f"completeHalfYears={len(halfyears)}; includedReportVersions={sum(int(r['reportCount']) for r in halfyears)}; eventClasses={dict(Counter(r['eventClass'] for r in halfyears))}",
        "Source-marked latest, non-amended reports only; compare with native LDA periods after actor linkage and exposure validation, without interpreting the excluded event half-year.")
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
