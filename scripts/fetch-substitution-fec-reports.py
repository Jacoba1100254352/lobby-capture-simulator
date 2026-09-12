#!/usr/bin/env python3
"""Fetch public, report-period PAC outcomes for a bounded LDA-to-FEC design link.

No contributor identities, raw API payloads, credentials, or query secrets are
saved. Preserve report periods and amendment metadata; do not allocate to
quarters or interpret PAC disbursements as the lobbying principal's transfers.
"""

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
FIRST_WAVE = ROOT / "data/calibration/first-wave"
DEFAULT_COMMITTEE = "C00007450"
DEFAULT_ACTOR = "cand-d5522e62fad7"
OUTCOMES = {
    "candidateContributionsDollars": "fed_candidate_committee_contributions_period",
    "independentExpendituresDollars": "independent_expenditures_period",
    "totalDisbursementsDollars": "total_disbursements_period",
}
FIELDS = [
    "canonicalActorId", "committeeId", "committeeName", "reportYear", "reportType",
    "fileNumber", "sourceRecordId", "periodStart", "periodEnd", "receiptDate", "amendmentIndicator",
    "mostRecent", "isAmended", "amendmentChain", *OUTCOMES, "sourceUrl",
    "sourceRetrievedAt", "linkStatus", "claimBoundary",
]
HISTORY_FIELDS = [
    "canonicalActorId", "committeeId", "cycle", "committeeName", "affiliatedName",
    "organizationType", "sourceUrl", "sourceRetrievedAt", "linkStatus", "claimBoundary",
]
BOUNDARY = (
    "Observed political-committee report-period amounts only; historical affiliation "
    "is a bounded actor-link candidate, not principal funding identity, treatment "
    "assignment, or evidence of causal channel substitution."
)


def amount(value):
    if value is None or value == "":
        return ""
    number = Decimal(str(value))
    if not number.is_finite():
        raise ValueError("Nonfinite FEC amount")
    return format(number, ".2f")


def normalize(record, actor_id, retrieved_at):
    file_number = record.get("file_number")
    image_number = record.get("beginning_image_number")
    if file_number is None and not image_number:
        raise ValueError("FEC report has neither filing number nor source image identifier")
    row = {
        "canonicalActorId": actor_id,
        "committeeId": record["committee_id"],
        "committeeName": record.get("committee_name", ""),
        "reportYear": str(record["report_year"]),
        "reportType": record["report_type"],
        "fileNumber": str(file_number) if file_number is not None else "",
        "sourceRecordId": f"file:{file_number}" if file_number is not None else f"image:{image_number}",
        "periodStart": (record.get("coverage_start_date") or "")[:10],
        "periodEnd": (record.get("coverage_end_date") or "")[:10],
        "receiptDate": (record.get("receipt_date") or "")[:10],
        "amendmentIndicator": record.get("amendment_indicator", ""),
        "mostRecent": str(record.get("most_recent", "")).lower(),
        "isAmended": str(record.get("is_amended", "")).lower(),
        "amendmentChain": ";".join(str(value) for value in (record.get("amendment_chain") or [])),
        "sourceUrl": record.get("html_url") or record.get("pdf_url") or "",
        "sourceRetrievedAt": retrieved_at,
        "linkStatus": "historical_affiliation_candidate",
        "claimBoundary": BOUNDARY,
    }
    for column, field in OUTCOMES.items():
        row[column] = amount(record.get(field))
    if not row["periodStart"] or not row["periodEnd"] or row["periodStart"] > row["periodEnd"]:
        raise ValueError("Invalid FEC report coverage dates")
    return row


def fetch_all(resource, params, api_key):
    records = []
    for page in range(1, 101):
        query = {**params, "per_page": 100, "page": page, "api_key": api_key}
        url = "https://api.open.fec.gov/v1/" + resource + "?" + urlencode(query)
        try:
            request = Request(url, headers={"User-Agent": "lobby-capture-simulator/0.1"})
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
        except HTTPError as error:
            raise RuntimeError(f"FEC {resource}: HTTP {error.code}; no credentials logged") from None
        except Exception as error:
            raise RuntimeError(f"FEC {resource}: {type(error).__name__}; no credentials logged") from None
        records.extend(payload["results"])
        if page >= int(payload["pagination"]["pages"]):
            return records
    raise RuntimeError("FEC pagination limit reached; refusing a partial snapshot")


def write_rows(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--committee-id", default=DEFAULT_COMMITTEE)
    parser.add_argument("--canonical-actor-id", default=DEFAULT_ACTOR)
    parser.add_argument("--years", nargs="+", type=int, default=[2003, 2004, 2005, 2006, 2007, 2008])
    parser.add_argument("--output", type=Path, default=FIRST_WAVE / "substitution-fec-report-panel.csv")
    parser.add_argument("--history-output", type=Path, default=FIRST_WAVE / "substitution-fec-affiliation-history.csv")
    args = parser.parse_args()
    key = os.environ.get("FEC_API_KEY", "")
    if not key:
        raise SystemExit("FEC_API_KEY is required; no request made")
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    histories, reports = [], []
    for cycle in sorted({year + year % 2 for year in args.years}):
        resource = f"committee/{args.committee_id}/history/{cycle}/"
        for record in fetch_all(resource, {}, key):
            if record["committee_id"] != args.committee_id or record["cycle"] != cycle:
                raise ValueError("FEC history identity mismatch")
            histories.append(dict(zip(HISTORY_FIELDS, [
                args.canonical_actor_id, record["committee_id"], str(cycle), record["name"],
                record.get("affiliated_committee_name") or "", record.get("organization_type_full") or "",
                f"https://www.fec.gov/data/committee/{args.committee_id}/?cycle={cycle}",
                retrieved_at, "historical_affiliation_candidate", BOUNDARY,
            ])))
    for year in args.years:
        for record in fetch_all(f"committee/{args.committee_id}/reports/", {"year": year}, key):
            if record["committee_id"] != args.committee_id or record["report_year"] != year:
                raise ValueError("FEC report identity/year mismatch")
            reports.append(normalize(record, args.canonical_actor_id, retrieved_at))
    if not reports or len({r["sourceRecordId"] for r in reports}) != len(reports):
        raise ValueError("Empty or duplicated FEC report snapshot")
    reports.sort(key=lambda r: (r["periodStart"], r["periodEnd"], r["fileNumber"]))
    write_rows(args.output, reports, FIELDS)
    write_rows(args.history_output, histories, HISTORY_FIELDS)
    print(f"Wrote {len(reports)} report-period rows and {len(histories)} historical affiliations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
