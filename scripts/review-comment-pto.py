#!/usr/bin/env python3
"""Trace a published PTO input revision without executing the source workbook.

Optional source-byte checks read native OOXML values and formula records. They
do not calculate Excel formulas, run VBA, or independently adjudicate sources.
"""

import argparse
import base64
from datetime import datetime, timezone
from decimal import Decimal
from email.utils import parsedate_to_datetime
import hashlib
import io
import json
from pathlib import Path
import posixpath
from xml.etree import ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/calibration/first-wave"
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
RANGES = {
    "A2b_Aux Sizing": ["M3", "O3", "O5", "M6", "N6", "O6", "N9", "M12", "N12", "O12", "M13", "N13", "O13"],
    "A2_Aux Load": ["B25", "D25", "I6", "J6", "I25", "J25"],
}
DENOMINATOR_RANGES = {
    "A2b_Aux Sizing": ["O3", "O12"],
    "A2_Aux Load": ["B25", "J25", "K6", "K25"],
    "A3a_Cost": ["B25", "J3", "J5", "J6", "J25", "K3", "K5", "K6", "K25", "R3", "R5", "R7", "R25"],
}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def native_cells(raw, ranges):
    """Read selected cells without calculating formulas or running VBA."""
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        require(archive.testzip() is None, "Workbook ZIP integrity failure")
        strings = ["".join(t.text or "" for t in item.findall(".//x:t", NS))
                   for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        rels = {r.attrib["Id"]: r.attrib["Target"]
                for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        result, native = {}, {}
        for sheet in workbook.find("x:sheets", NS):
            name = sheet.attrib["name"]
            if name not in ranges:
                continue
            target = rels[sheet.attrib[RID]]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            cells = {}
            for cell in ET.fromstring(archive.read(member)).findall("x:sheetData/x:row/x:c", NS):
                value = cell.findtext("x:v", default=None, namespaces=NS)
                if cell.attrib.get("t") == "s" and value is not None:
                    value = strings[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall("x:is//x:t", NS))
                formula = cell.find("x:f", NS)
                cells[cell.attrib["r"]] = {
                    "type": cell.attrib.get("t"), "value": value,
                    "formula": None if formula is None else formula.text,
                    "formulaAttributes": None if formula is None else formula.attrib,
                }
            native[name] = cells
            result[name] = {"member": member, "cells": {key: cells[key] for key in ranges[name]}}
        require(set(native) == set(ranges), "Missing reviewed worksheet")
        return result, native


def workbook_evidence(raw):
    """Preserve formula children and caches separately; resolve one input lookup."""
    result, native = native_cells(raw, RANGES)
    sizing, load = native["A2b_Aux Sizing"], native["A2_Aux Load"]
    expected = "INDEX('A2b_Aux Sizing'!$M$7:$O$40,MATCH(I25,'A2b_Aux Sizing'!$N$7:$N$40,0),MATCH($J$6,'A2b_Aux Sizing'!$M$6:$O$6,0))"
    require(load["J25"]["formula"] == expected, "Unreviewed PTO lookup formula")
    require(sizing["O6"]["value"] == load["J6"]["value"] == "PTO %", "PTO lookup header mismatch")
    pto_id = load["I25"]["value"]
    matches = [row for row in range(7, 41) if sizing.get(f"N{row}", {}).get("value") == pto_id]
    require(len(matches) == 1, "Missing or ambiguous PTO ID")
    row = matches[0]
    source = sizing[f"O{row}"]
    require(source["formulaAttributes"] is None, "PTO source is not a literal input")
    value, cached = float(source["value"]), float(load["J25"]["value"])
    require(0 <= value <= 1 and value == cached, "PTO source and cached fraction mismatch")
    return {"sheets": result, "lookup": {
        "vehicleId": load["B25"]["value"], "ptoId": int(pto_id),
        "auxiliaryType": sizing[f"M{row}"]["value"],
        "sourceSheet": "A2b_Aux Sizing", "sourceCell": f"O{row}",
        "lookupSheet": "A2_Aux Load", "lookupCell": "J25",
        "inputFraction": value, "cachedFraction": cached,
    }}


def denominator_calculation(sheets):
    """Reconcile stored proposal fuel components, not the whole model or final rule."""
    sizing, load, cost = (sheets[name]["cells"] for name in DENOMINATOR_RANGES)
    require(load["B25"]["value"] == cost["B25"]["value"] == "19C_Mix_Cl8_MP", "Different calculation vehicle")
    require(cost["J6"]["value"] == "Gallons Per Year_driving (Diesel)"
            and cost["K6"]["value"] == load["K6"]["value"] == "Gallons Per Year_PTO (Diesel)"
            and cost["J5"]["value"] == cost["K5"]["value"] == "gal/year", "Fuel denominator labels differ")
    require(cost["K25"]["formula"] == "'A2_Aux Load'!J25*J25"
            and cost["K25"]["formulaAttributes"] == {}, "PTO multiplication formula differs")
    require(cost["R7"]["formula"] == "(J7+K7)*Diesel_Pr_1"
            and cost["R7"]["formulaAttributes"] == {"t": "shared", "ref": "R7:R38", "si": "3"}
            and cost["R25"]["formula"] is None
            and cost["R25"]["formulaAttributes"] == {"t": "shared", "si": "3"}, "Fuel addition formula family differs")
    fraction, driving, pto = (Decimal(c["value"]) for c in (load["J25"], cost["J25"], cost["K25"]))
    require(all(v.is_finite() for v in (fraction, driving, pto)) and 0 <= fraction <= 1 and driving > 0,
            "Invalid cached fuel components")
    require(sizing["O12"]["formulaAttributes"] is None and Decimal(sizing["O12"]["value"]) == fraction,
            "PTO input differs from lookup cache")
    require(abs(fraction * driving - pto) <= Decimal("0.000000001")
            and Decimal(load["K25"]["value"]) == pto, "PTO gallons do not reconcile with stored driving fuel")
    return {"vehicleId": cost["B25"]["value"], "inputFractionOfDriving": str(fraction),
            "cachedDrivingGallonsPerYear": str(driving), "cachedPtoGallonsPerYear": str(pto),
            "derivedDrivingPlusPtoGallonsPerYear": str(driving + pto),
            "derivedPtoFractionOfDrivingPlusPto": str(pto / (driving + pto))}


def denominator_evidence(raw):
    sheets, _ = native_cells(raw, DENOMINATOR_RANGES)
    return {"sheets": sheets, "calculation": denominator_calculation(sheets)}


def validate(review):
    require(review["reviewFingerprint"] == fingerprint({k: v for k, v in review.items() if k != "reviewFingerprint"}),
            "PTO review fingerprint mismatch")
    require(review["schema"] == "comment-pto-model-review-v1", "Unknown PTO review schema")
    existing = json.loads((DATA / "comment-publisher-remaining-review.json").read_text())
    require(review["existingReviewFingerprint"] == existing["reviewFingerprint"], "Existing request review changed")
    require(review["requestId"] == "mema-1570-r35", "PTO follow-up is off-frame")
    for key in ("response", "ria"):
        require(review["documents"][key]["sha256"] == existing["documents"][key]["sha256"], "Published source identity changed")
    current, archived = review["workbook"], review["archive"]
    require(current["sha256"] == archived["sha256"] and current["byteSize"] == archived["byteSize"],
            "Archived and current workbook identity differs")
    captured = datetime.strptime(archived["timestamp"], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    require(parsedate_to_datetime(archived["mementoDatetime"]) == captured, "Archive timestamp differs from Memento")
    require(archived["sha1Base32"] == archived["cdxDigest"], "Archive index digest mismatch")
    lookup = review["nativeEvidence"]["lookup"]
    require(lookup["vehicleId"] == review["comparison"]["vehicleId"], "Comparison vehicle identity differs")
    comparison = review["comparison"]
    require(lookup["inputFraction"] * 100 == comparison["proposalPercent"], "Workbook and draft baseline differ")
    require(sum(comparison["submittedRangePercent"]) / 2 == comparison["finalPercent"], "Final midpoint differs")
    require(comparison["changePercentagePoints"] == comparison["finalPercent"] - comparison["proposalPercent"],
            "Percentage-point difference is incorrect")
    docket = review["docketAttachments"]
    require(current["byteSize"] != docket["proposal"]["byteSize"], "Proposal docket version needs renewed review")
    require(docket["finalModel"]["docOrder"] == 1 and docket["finalCalculator"]["docOrder"] == 2,
            "Model and output calculator confused")
    require(all(docket[k]["downloadStatus"] == "http_403_not_acquired" for k in docket), "Unreviewed docket source state")
    require(review["boundary"] == {
        "newRequests": 0, "independentReview": "pending", "originalCommentDocketBytesVerified": False,
        "proposalDocketWorkbookBytesVerified": False, "finalWorkbookRead": False,
        "workbookRecalculated": False, "macrosExecuted": False,
        "causalEffect": "not_identified", "simulatorCalibrationEligible": False,
    }, "PTO comparison boundary changed")
    denominator = review["proposalDenominatorReview"]["nativeEvidence"]
    require(denominator_calculation(denominator["sheets"]) == denominator["calculation"],
            "Stored proposal denominator calculation differs")
    require(Decimal(denominator["calculation"]["inputFractionOfDriving"]) * 100 == comparison["proposalPercent"],
            "Proposal denominator input differs from published comparison")
    return {"existingRequestFollowups": 1, "proposalPtoPercent": comparison["proposalPercent"],
            "finalPublishedPtoPercent": comparison["finalPercent"],
            "changePercentagePoints": comparison["changePercentagePoints"],
            "archiveByteMatch": True, "finalWorkbookRead": False,
            "proposalPtoPercentOfDrivingPlusPto": float(Decimal(denominator["calculation"]["derivedPtoFractionOfDrivingPlusPto"]) * 100),
            "causalEffect": "not_identified"}


def verify_workbooks(review, current_path, archive_path):
    for key, path in (("workbook", current_path), ("archive", archive_path)):
        raw = path.read_bytes()
        require(len(raw) == review[key]["byteSize"] and hashlib.sha256(raw).hexdigest() == review[key]["sha256"],
                f"{key} bytes differ from reviewed source")
        require(workbook_evidence(raw) == review["nativeEvidence"], "Native workbook evidence differs")
        require(denominator_evidence(raw) == review["proposalDenominatorReview"]["nativeEvidence"],
                "Native proposal denominator evidence differs")
        if key == "archive":
            require(base64.b32encode(hashlib.sha1(raw).digest()).decode().rstrip("=") == review[key]["cdxDigest"],
                    "Archived payload does not match index digest")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--archived-workbook", type=Path)
    args = parser.parse_args()
    require(bool(args.workbook) == bool(args.archived_workbook), "Supply both source workbooks")
    review = json.loads((DATA / "comment-pto-model-review.json").read_text())
    result = validate(review)
    if args.workbook:
        verify_workbooks(review, args.workbook, args.archived_workbook)
    result["localWorkbookBytesChecked"] = bool(args.workbook)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
