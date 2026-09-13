#!/usr/bin/env python3
"""Reproduce a dated organization-link review without carrying blanks forward.

The inventory is a projection of the acquired F1 query, not a census of all
correspondence or proof that a relationship lasted through an outcome period.
PDF checks authenticate local bytes and page counts, not the manual reading.
"""

import argparse
import csv
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
SOURCE = DATA / "substitution-fec-organization-review.json"
FIELDS = ["committee_id", "beginning_image_number", "receipt_date", "form_type",
          "amendment_indicator", "most_recent", "pdf_url", "pages", "file_number"]
BOUNDARY = {
    "unit": "document_relationship_observation",
    "continuousAffiliationEstablished": False,
    "blankMeansNoRelationship": False,
    "principalFundingIdentityEstablished": False,
    "exposureAssigned": False,
    "outcomesOverwritten": False,
    "causalEffect": "not_identified",
}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def project(row):
    return {key: row[key] for key in FIELDS}


def selected_images(rows, start, end):
    """Keep ties at the last pre-window receipt and every in-window filing.

    Current most_recent flags must not discard historical registrations.
    This selection establishes a review frame, not effective-date intervals.
    """
    before = [r for r in rows if r["receipt_date"][:10] < start]
    if not before:
        raise ValueError("No pre-window registration anchor in the acquired query")
    last = max(r["receipt_date"] for r in before)
    return {r["beginning_image_number"] for r in rows
            if r["receipt_date"] == last or start <= r["receipt_date"][:10] <= end}


def validate_review(review, cohort, histories):
    if (review.get("schema") != "substitution-fec-organization-review-v1"
            or review.get("boundary") != BOUNDARY
            or review.get("independentReviewStatus") != "pending"
            or not review.get("reviewer")):
        raise ValueError("Organization review scope or claim boundary changed")
    date.fromisoformat(review["reviewDate"])
    if review["fingerprint"] != fingerprint({k: v for k, v in review.items() if k != "fingerprint"}):
        raise ValueError("Stale organization review fingerprint")
    if review["cohortFingerprint"] != fingerprint(cohort) or review["historyFingerprint"] != fingerprint(histories):
        raise ValueError("Organization review baseline changed")
    members = {r["committeeId"]: r for r in cohort}
    queries = {r["committeeId"]: r for r in review["queries"]}
    if len(members) != len(cohort) or len(queries) != len(review["queries"]) or set(queries) != set(members):
        raise ValueError("Organization review must retain the whole acquisition cohort")
    if any(r["exposureGroup"] != "unassigned_design_candidate" for r in cohort):
        raise ValueError("Acquisition membership cannot assign exposure")
    inventory, expected = {}, set()
    for cid, query in queries.items():
        datetime.fromisoformat(query["retrievedAt"])
        rows = query["records"]
        if (query["url"] != f"https://api.open.fec.gov/v1/filings/?committee_id={cid}&form_type=F1"
                or query["pagination"] != "all_pages_via_fetch_all"
                or len(rows) != query["count"] or query["projectionFingerprint"] != fingerprint(rows)
                or not re.fullmatch(r"[0-9a-f]{64}", query["cacheSha256"])):
            raise ValueError("Incomplete or changed F1 query inventory")
        for row in rows:
            key = (cid, row["beginning_image_number"])
            if (row != project(row) or row["committee_id"] != cid or row["form_type"] != "F1"
                    or not re.fullmatch(r"[0-9]{11,18}", row["beginning_image_number"])
                    or key in inventory or not isinstance(row["pages"], int) or row["pages"] < 1):
                raise ValueError("Duplicate, invalid or off-committee F1 record")
            datetime.fromisoformat(row["receipt_date"])
            inventory[key] = row
        start, end = f'{members[cid]["startYear"]}-01-01', f'{members[cid]["endYear"]}-12-31'
        expected.update((cid, image) for image in selected_images(rows, start, end))
    documents = {(d["committeeId"], d["imageNumber"]): d for d in review["documents"]}
    if len(documents) != len(review["documents"]) or set(documents) != expected:
        raise ValueError("Document selection differs from all in-window plus pre-window anchors")
    for key, document in documents.items():
        row, cid = inventory[key], key[0]
        if (document["canonicalActorId"] != members[cid]["canonicalActorId"]
                or document["sourceUrl"] != row["pdf_url"]
                or document["sourceFingerprint"] != fingerprint(row)
                or document["apiReceiptDate"] != row["receipt_date"][:10]
                or document["pdfPages"] != row["pages"]
                or not re.fullmatch(r"[0-9a-f]{64}", document["pdfSha256"])):
            raise ValueError("Document identity or source binding mismatch")
        if document["pagesReviewed"] != list(range(1, document["pdfPages"] + 1)):
            raise ValueError("Incomplete document page inventory")
        if len(document["pageInventory"]) != document["pdfPages"] or not all(document["pageInventory"]):
            raise ValueError("Missing page inventory descriptions")
        if not document["findings"] or not document["committeeName"]:
            raise ValueError("Missing organization findings")
        for link in document["relationships"]:
            if (link["role"] not in {"connected_organization", "affiliated_committee", "named_relationship_unspecified"}
                    or not link["name"] or not link["evidence"]
                    or link["pdfPage"] not in document["pagesReviewed"]):
                raise ValueError("Unsupported relationship role or page")
        for field in ("documentDate", "signedDate"):
            if document[field]:
                date.fromisoformat(document[field])
    linked = {d["committeeId"] for d in documents.values()
              if any(r["role"] == "connected_organization" for r in d["relationships"])}
    prelinked = {d["committeeId"] for d in documents.values()
                 if d["apiReceiptDate"] < f'{members[d["committeeId"]]["startYear"]}-01-01'
                 and any(r["role"] == "connected_organization" for r in d["relationships"])}
    roles = [r for d in documents.values() for r in d["relationships"]]
    return {
        "queryRecords": len(inventory), "committeesRetained": len(members),
        "selectedDocuments": len(documents), "pagesReviewed": sum(d["pdfPages"] for d in documents.values()),
        "connectedOrganizationObservations": sum(r["role"] == "connected_organization" for r in roles),
        "affiliatedCommitteeObservations": sum(r["role"] == "affiliated_committee" for r in roles),
        "unspecifiedRelationshipObservations": sum(r["role"] == "named_relationship_unspecified" for r in roles),
        "committeesWithExplicitParentObservation": len(linked),
        "committeesWithPreWindowParentObservation": len(prelinked),
        "continuousAffiliationPeriodsCleared": 0,
        "causalEffect": "not_identified",
    }


def verify_files(review, directory):
    """Optional local acquisition check; unavailable files are never a pass."""
    verified, unavailable = [], []
    for query in review["queries"]:
        name = query["committeeId"] + "-filings.json"
        path = directory / name
        if not path.is_file():
            unavailable.append(name)
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != query["cacheSha256"]:
            raise ValueError("F1 acquisition cache hash mismatch")
        cached = json.loads(path.read_text())
        if ({k: cached[k] for k in ("url", "retrievedAt", "count", "pagination")}
                != {k: query[k] for k in ("url", "retrievedAt", "count", "pagination")}
                or [project(r) for r in cached["records"]] != query["records"]):
            raise ValueError("F1 acquisition cache projection mismatch")
        verified.append(name)
    for document in review["documents"]:
        name = document["imageNumber"] + ".pdf"
        path = directory / name
        if not path.is_file():
            unavailable.append(name)
            continue
        content = path.read_bytes()
        if not content.startswith(b"%PDF") or hashlib.sha256(content).hexdigest() != document["pdfSha256"]:
            raise ValueError("Organization PDF bytes mismatch")
        info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
        pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
        if pages is None or int(pages.group(1)) != document["pdfPages"]:
            raise ValueError("Organization PDF page count mismatch")
        verified.append(name)
    return {"verified": verified, "unavailable": unavailable,
            "manualReadingIndependentlyVerified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-directory", type=Path)
    args = parser.parse_args()
    review = json.loads(SOURCE.read_text())
    def read(name):
        with (DATA / name).open(newline="") as source:
            return list(csv.DictReader(source))
    print(json.dumps(validate_review(review, read("substitution-fec-acquisition-cohort.csv"),
                                    read("substitution-fec-affiliation-history.csv")), indent=2))
    if args.raw_directory:
        print(json.dumps(verify_files(review, args.raw_directory), indent=2))


if __name__ == "__main__":
    main()
