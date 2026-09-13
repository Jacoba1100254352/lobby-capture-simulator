#!/usr/bin/env python3
"""Compare separate export partitions without adding overlapping rows to the panel.

Default mode validates the source-reviewed ledger. --scan additionally reads
the specified 34 ignored archives and reproduces the complete-row comparison.
"""

import argparse
from collections import Counter
import csv
from datetime import date, timedelta
import hashlib
from io import TextIOWrapper
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
DIRECTORY = "data/raw/usaspending-transaction-downloads"
MANIFEST = ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-bulk-summary.json"
LEDGER = DATA / "procurement-bulk-partition-comparison.json"
AGENCY = "Department of Agriculture"
FIELDS = (
    "award_id_piid", "parent_award_id_piid", "modification_number", "federal_action_obligation",
    "action_date", "recipient_name", "recipient_uei", "awarding_agency_name", "awarding_sub_agency_name",
    "award_type", "type_of_contract_pricing", "extent_competed", "number_of_offers_received",
)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def partition_dates():
    return [("2024-07-01", "2024-07-31"),
            *[(f"2024-08-{day:02d}", f"2024-08-{day:02d}") for day in range(1, 32)],
            ("2024-09-01", "2024-09-30")]


def archive_name(start, end):
    return f"department-of-agriculture-{start}-{end}.zip"


def multiset_hash(rows):
    """Order-independent digest retaining every exact value and multiplicity."""
    digest = hashlib.sha256()
    for row, count in sorted(rows.items()):
        digest.update((json.dumps([row, count], ensure_ascii=True, separators=(",", ":")) + "\n").encode())
    return digest.hexdigest()


def compare(quarter, partitions):
    only_quarter, only_parts = quarter - partitions, partitions - quarter
    return {"quarterRows": quarter.total(), "partitionRows": partitions.total(),
            "commonRows": (quarter & partitions).total(),
            "quarterOnlyRows": only_quarter.total(), "partitionOnlyRows": only_parts.total(),
            "quarterDuplicateValueRows": quarter.total() - len(quarter),
            "partitionDuplicateValueRows": partitions.total() - len(partitions),
            "quarterMultisetSha256": multiset_hash(quarter),
            "partitionMultisetSha256": multiset_hash(partitions)}


def read_archive(path, start, end):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rows, members, excluded = Counter(), [], []
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, "Archive integrity failure")
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate archive member names")
        for info in archive.infolist():
            if "PrimeTransactions" not in info.filename or not info.filename.endswith(".csv"):
                excluded.append({"name": info.filename, "byteSize": info.file_size})
                continue
            with archive.open(info.filename) as stream:
                reader = csv.reader(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
                require(next(reader) == list(FIELDS), "Source header differs from reviewed field set")
                count = 0
                for row in reader:
                    require(len(row) == len(FIELDS), "Malformed source row")
                    require(row[7] == AGENCY and first <= date.fromisoformat(row[4]) <= last,
                            "Source row outside agency/date partition")
                    rows[tuple(row)] += 1
                    count += 1
                members.append({"name": info.filename, "zipMemberTime": list(info.date_time), "rows": count})
    require(members, "No prime transaction member")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "Archive changed during scan")
    return rows, {"archiveName": path.name, "sha256": digest, "byteSize": path.stat().st_size,
                  "startDate": start, "endDate": end, "rows": rows.total(),
                  "distinctValueRows": len(rows), "rowMultisetSha256": multiset_hash(rows),
                  "primeMembers": members, "excludedMembers": excluded}


def scan():
    directory = ROOT / DIRECTORY
    start, end = "2024-07-01", "2024-09-30"
    quarter, quarter_record = read_archive(directory / archive_name(start, end), start, end)
    combined, records = Counter(), []
    for first, last in partition_dates():
        rows, record = read_archive(directory / archive_name(first, last), first, last)
        combined.update(rows)
        records.append(record)
    return {"quarterArchive": quarter_record, "partitionArchives": records,
            "comparison": compare(quarter, combined)}


def validate(review, manifest):
    require(review["reviewFingerprint"] == fingerprint({k: v for k, v in review.items() if k != "reviewFingerprint"}),
            "Partition review fingerprint mismatch")
    require(review["schema"] == "procurement-bulk-partition-comparison-v1"
            and review["sourceHeader"] == list(FIELDS) and review["archiveDirectory"] == DIRECTORY,
            "Unknown comparison contract")
    require(review["manifestSha256"] == hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            "Frozen manifest changed")
    q = review["quarterArchive"]
    matches = [r for r in manifest["strata"] if r["downloadFile"] == DIRECTORY + "/" + q["archiveName"]]
    require(len(matches) == 1, "Quarter archive is not uniquely manifest-selected")
    baseline = matches[0]
    require(q["sha256"] == baseline["zipSha256"] and q["rows"] == int(baseline["normalizedRows"]),
            "Quarter source differs from frozen archive")
    parts = review["partitionArchives"]
    require([(r["startDate"], r["endDate"]) for r in parts] == partition_dates(), "Incomplete partition frame")
    coverage = Counter()
    for record in [q, *parts]:
        require(record["archiveName"] == archive_name(record["startDate"], record["endDate"]), "Archive/date mismatch")
        require(record["rows"] == sum(m["rows"] for m in record["primeMembers"]), "Archive member count mismatch")
        require(0 <= record["distinctValueRows"] <= record["rows"], "Invalid distinct-value count")
        if record is not q:
            first, last = date.fromisoformat(record["startDate"]), date.fromisoformat(record["endDate"])
            coverage.update(first + timedelta(days=i) for i in range((last-first).days+1))
    require(len(coverage) == 92 and set(coverage.values()) == {1}, "Partition date gap or overlap")
    comparison = review["comparison"]
    require(comparison["quarterRows"] == q["rows"]
            and comparison["partitionRows"] == sum(p["rows"] for p in parts), "Comparison count mismatch")
    require(comparison["quarterOnlyRows"] == comparison["partitionOnlyRows"] == 0
            and comparison["commonRows"] == q["rows"]
            and comparison["quarterMultisetSha256"] == comparison["partitionMultisetSha256"] == q["rowMultisetSha256"],
            "Saved comparison no longer establishes equal row multisets")
    require(review["plannedRows"] == int(baseline["transactionCount"])
            and review["unresolvedCountDifference"] == review["plannedRows"] - q["rows"], "Planned-count gap changed")
    require(review["boundary"] == {
        "countTimeMembershipRecovered": False, "missingRecordIdentitiesEstablished": False,
        "causeEstablished": False, "upstreamDeploymentVersionVerified": False,
        "independentReview": "pending", "representativeSamExport": False,
        "frozenPanelChanged": False, "additionalPanelRows": 0,
        "historicalExclusionIntervalsEstablished": False, "causalEffect": "not_identified",
    }, "Comparison evidence boundary changed")
    return {"alternativeArchives": len(parts), "inclusiveDays": len(coverage),
            "matchedCompleteRows": comparison["commonRows"], "comparedFields": len(FIELDS),
            "unmatchedRows": comparison["quarterOnlyRows"] + comparison["partitionOnlyRows"],
            "unresolvedAgricultureCountDifference": review["unresolvedCountDifference"],
            "missingRecordIdentitiesEstablished": False, "additionalPanelRows": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", action="store_true")
    args = parser.parse_args()
    review = json.loads(LEDGER.read_text())
    result = validate(review, json.loads(MANIFEST.read_text()))
    if args.scan:
        require(scan() == {k: review[k] for k in ("quarterArchive", "partitionArchives", "comparison")},
                "Fresh archive comparison differs from reviewed evidence")
    result["localArchivesChecked"] = args.scan
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
