#!/usr/bin/env python3
"""Prepare complete native half-years from latest FEC report periods.

This is an observed alternate-channel outcome, not a substitution estimator.
Amended and unknown-version rows remain in the raw acquisition snapshot.
"""

import csv
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
MEASURES = ["candidateContributionsDollars", "independentExpendituresDollars", "totalDisbursementsDollars"]
FIELDS = ["canonicalActorId", "committeeId", "halfYear", "periodStart", "periodEnd", "reportCount", "completeCoverage", "eventClass", *MEASURES, "sourceRecordIds", "linkStatus", "claimBoundary"]


def prepare(rows):
    selected = [r for r in rows if r["mostRecent"] == "true" and r["isAmended"] == "false"]
    groups = defaultdict(list)
    for row in selected:
        start, end = date.fromisoformat(row["periodStart"]), date.fromisoformat(row["periodEnd"])
        half = 1 if start.month <= 6 else 2
        if (start.year, half) != (end.year, 1 if end.month <= 6 else 2):
            raise ValueError("FEC report straddles half-years; transaction dates required")
        if end < start:
            raise ValueError("Reversed FEC coverage period")
        groups[(row["canonicalActorId"], row["committeeId"], start.year, half)].append(row)
    prepared = []
    for (actor, committee, year, half), reports in sorted(groups.items()):
        start = date(year, 1 if half == 1 else 7, 1)
        end = date(year, 6, 30) if half == 1 else date(year, 12, 31)
        expected = start
        for row in sorted(reports, key=lambda r: r["periodStart"]):
            if date.fromisoformat(row["periodStart"]) != expected:
                raise ValueError("Gap or overlap in selected FEC reports; no complete half-year")
            expected = date.fromisoformat(row["periodEnd"]) + timedelta(days=1)
        if expected != end + timedelta(days=1):
            raise ValueError("Incomplete trailing FEC half-year coverage")
        if any(not row[field] for row in reports for field in MEASURES):
            raise ValueError("Missing FEC outcome is not an observed zero")
        result = {
            "canonicalActorId": actor, "committeeId": committee,
            "halfYear": f"{year}H{half}", "periodStart": start.isoformat(), "periodEnd": end.isoformat(),
            "reportCount": str(len(reports)), "completeCoverage": "true",
            "eventClass": "pre" if end < date(2007,9,14) else "post" if start > date(2007,9,14) else "straddles_event_excluded",
            "sourceRecordIds": ";".join(sorted(r["sourceRecordId"] for r in reports)),
            "linkStatus": "historical_affiliation_candidate",
            "claimBoundary": "Observed PAC half-year totals only; no treatment/control design or causal substitution effect; affiliation and principal funding identity remain separate.",
        }
        for field in MEASURES:
            amounts = [Decimal(row[field]) for row in reports]
            if any(not value.is_finite() for value in amounts):
                raise ValueError("Nonfinite FEC outcome")
            result[field] = format(sum(amounts), ".2f")
        prepared.append(result)
    return prepared, len(rows) - len(selected)


def main():
    with (DATA / "substitution-fec-report-panel.csv").open(newline="", encoding="utf-8") as source:
        raw = list(csv.DictReader(source))
    rows, excluded = prepare(raw)
    if not rows:
        raise ValueError("No complete FEC half-years")
    with (DATA / "substitution-fec-halfyear-panel.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Prepared {len(rows)} complete native half-years; excluded {excluded} superseded/unknown report versions.")


if __name__ == "__main__":
    main()
