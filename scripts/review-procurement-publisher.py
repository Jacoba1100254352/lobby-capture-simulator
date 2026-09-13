#!/usr/bin/env python3
"""Reproduce a bounded current-publisher check, not a historical award clearance."""

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from datetime import date, datetime
from html.parser import HTMLParser


VA_URL = "https://department.va.gov/procurement-acquisition-and-logistics/strategic-acquisition-center/sac-medical-surgical-prime-vendor-program-mspv-updated/"
TRAINING_URL = "https://www.acq.osd.mil/asda/dpc/ce/p2p/docs/training-presentations/2024/P2P%202024%20-%20FPDS%20Reporting%20Basics%20-%20Procurement%20Awards.pdf"
GUIDANCE_URLS = {
    "2023-01-31": "https://www.acq.osd.mil/dpap/dars/pgi/pgi_htm/r20230427/PGI204_6.htm",
    "2024-05-30": "https://www.acq.osd.mil/dpap/dars/pgi/pgi_pdf/r20240530/PGI204_6.pdf",
}
HEADING = "MSPV GenZ V1 Delivery Orders (DO) List of Contacts"
HEADER = ["VISN #", "Delivery Order and Performance Period"]
PARENT_KEY = "CONT_IDV_36C10X23D0032_3600"
PARENT_MEMBER = "IDV_36C10X23D0032_TransactionHistory_1.csv"
PARENT_FIELDS = ["contract_transaction_unique_key", "contract_award_unique_key", "award_id_piid",
                 "modification_number", "parent_award_id_piid", "action_date", "awarding_sub_agency_code",
                 "recipient_uei", "award_type", "idv_type_code", "multiple_or_single_award_idv_code",
                 "type_of_idc_code", "solicitation_identifier", "solicitation_procedures_code",
                 "number_of_offers_received", "federal_action_obligation"]
AREAS = ["VISN 1", "VISN 2", "VISN 4", "VISN 5", "VISN 6", "VISN 7",
         "VISN 8 excluding Puerto Rico", "VISN 9", "VISN 10", "VISN 12",
         "VISN 15", "VISN 16", "VISN 17", "VISN 19", "VISN 20", "VISN 21",
         "VISN 22", "VISN 23", "Puerto Rico", "Other Government Agencies (OGAs)"]


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Tables(HTMLParser):
    """Read native table cells without executing HTML or retaining staff contacts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.text_parts = [], []
        self.table, self.row, self.cell = None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if self.table is not None:
                raise ValueError("Nested publisher table requires explicit review")
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []
        elif tag in {"p", "br", "div"} and self.cell is not None:
            self.cell.append(" ")

    def handle_data(self, data):
        self.text_parts.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None
        elif tag in {"p", "div"} and self.cell is not None:
            self.cell.append(" ")


def project_rows(native_rows):
    """Separate publisher labels and performance dates, never infer action dates."""
    rows = []
    for ordinal, cells in enumerate(native_rows, start=1):
        if len(cells) != 2:
            raise ValueError("Publisher table column drift")
        identity = re.fullmatch(r"(.+?) (Medline Industries, LP|Concordance Healthcare Solutions LLC)", cells[0])
        details = re.fullmatch(
            r"Delivery Order: (36C10X\d{2}D\d{4}) (36C10X\d{2}N\d{4}) Performance Period: "
            r"(\d{2}/\d{2}/\d{4})\s*[-\u2013\u2014]\s*(\d{2}/\d{2}/\d{4})", cells[1])
        if identity is None or details is None:
            raise ValueError("Publisher native cell cannot be parsed without review")
        start, end = (datetime.strptime(value, "%m/%d/%Y").date().isoformat()
                      for value in details.groups()[2:])
        if start > end:
            raise ValueError("Publisher performance chronology is invalid")
        rows.append({"rowNumber": ordinal, "serviceAreaNative": identity[1],
                     "awardeeNative": identity[2], "parentPiid": details[1], "piid": details[2],
                     "performanceStartDate": start, "performanceEndDate": end})
    return rows


def parse_html(raw):
    parser = Tables()
    parser.feed(raw.decode("utf-8"))
    text = " ".join(" ".join(parser.text_parts).split())
    tables = [table for table in parser.tables if table and table[0] == HEADER]
    updated = re.search(r"Date last updated: ([A-Za-z]+ \d{1,2}, \d{4})", text)
    if len(tables) != 1 or updated is None or HEADING not in text:
        raise ValueError("Missing or ambiguous bounded publisher table/date")
    native = tables[0][1:]
    return {"pageUpdatedDate": datetime.strptime(updated[1], "%B %d, %Y").date().isoformat(),
            "nativeRows": native, "rows": project_rows(native)}


def parent_archive_projection(raw):
    """Profile all CSV members but project only the declared parent action history."""
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError("Parent archive CRC failed")
        members, projection, offer_headers = [], None, None
        for name in archive.namelist():
            if not name.endswith('.csv'):
                continue
            data = archive.read(name)
            reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
            rows = list(reader)
            members.append({"name": name, "sha256": hashlib.sha256(data).hexdigest(),
                            "rows": len(rows), "columns": len(reader.fieldnames)})
            if name == PARENT_MEMBER:
                offer_headers = [column for column in reader.fieldnames if 'offer' in column.lower()]
                projection = [{"csvRowIncludingHeader": index,
                               "fullRowFingerprint": fingerprint(row),
                               "fields": {key: row[key] for key in PARENT_FIELDS}}
                              for index, row in enumerate(rows, start=2)]
        if projection is None:
            raise ValueError("Missing declared parent transaction member")
        return {"csvMembers": members, "transactions": projection, "offerHeaders": offer_headers}


def parent_diagnostics(source, original_review, raw_archive=None, raw_history=None):
    """Keep parent offers and solicitation separate from child-order observations."""
    if (source["awardKey"] != PARENT_KEY or source["downloadEndpoint"] != "https://api.usaspending.gov/api/v2/download/idv/"
            or source["historyEndpoint"] != "https://api.usaspending.gov/api/v2/transactions/"
            or source["downloadRequest"] != {"award_id": PARENT_KEY, "file_format": "csv"}
            or source["historyRequest"] != {"award_id": PARENT_KEY, "page": 1, "limit": 100, "sort": "action_date", "order": "asc"}
            or source["transactionMember"] != PARENT_MEMBER
            or source["scope"] != "2026_retrieval_of_parent_actions_not_2024_archive_or_order_provenance"):
        raise ValueError("Parent source request or temporal scope mismatch")
    for field in ("archiveSha256", "historyRawSha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", source[field]):
            raise ValueError("Missing parent source hash")
    history = source["historyResponse"]
    if history["page_metadata"] != {"page": 1, "next": None, "previous": None, "hasNext": False, "hasPrevious": False}:
        raise ValueError("Incomplete parent history pagination")
    records = history["results"]
    by_id = {row["id"]: row for row in records}
    transactions = source["transactions"]
    rows = [row["fields"] for row in transactions]
    if (len(rows) != 7 or len(by_id) != len(records) or len(rows) != len(records)
            or {"CONT_TX_" + row["contract_transaction_unique_key"] for row in rows} != set(by_id)
            or len({row["contract_transaction_unique_key"] for row in rows}) != len(rows)
            or sorted(row["csvRowIncludingHeader"] for row in transactions) != list(range(2, 9))):
        raise ValueError("Parent transaction frame or identity mismatch")
    originals = [row for row in rows if row["modification_number"] == '0']
    if len(originals) != 1 or originals[0]["action_date"] != "2023-05-23":
        raise ValueError("Parent original action missing or replaced")
    for row in rows:
        api = by_id['CONT_TX_' + row['contract_transaction_unique_key']]
        if (row["contract_award_unique_key"] != PARENT_KEY or row["award_id_piid"] != "36C10X23D0032"
                or row["parent_award_id_piid"] != "" or row["recipient_uei"] != "DMPAKJ9N9K66"
                or row["awarding_sub_agency_code"] != "3600" or api["type"] != "IDV_B_B"
                or api["action_date"] != row["action_date"] or api["modification_number"] != row["modification_number"]
                or [row[k] for k in ("idv_type_code", "multiple_or_single_award_idv_code", "type_of_idc_code")] != ['B', 'M', 'B']
                or row["number_of_offers_received"] != '6' or row["solicitation_identifier"] != '36C10X23R0007'):
            raise ValueError("Parent reported identity, type or offer context mismatch")
    job, status = source["downloadJob"], source["downloadStatus"]
    members = source["csvMembers"]
    if (status["status"] != 'finished' or len(members) != 3
            or status["total_rows"] != sum(m["rows"] for m in members)
            or status["total_columns"] != sum(m["columns"] for m in members)
            or status["file_name"] != job["file_name"] or status["file_url"] != job["file_url"]
            or job["file_url"] != 'https://files.usaspending.gov/generated_downloads/' + job["file_name"]
            or job["status_url"] != 'https://api.usaspending.gov/api/v2/download/status?file_name=' + job["file_name"]
            or source["offerHeaders"] != ['number_of_offers_received']):
        raise ValueError("Parent download completeness or offer-header context mismatch")
    for award in original_review["awards"]:
        row = award["originalProjection"]
        if (row["parent_award_id_piid"] != "36C10X23D0032" or row["parent_award_agency_id"] != "3600"
                or row["solicitation_identifier"] != "" or row["number_of_offers_received"] not in {'2', '4'}):
            raise ValueError("Parent context cannot overwrite child source fields")
    if raw_archive is not None:
        actual = parent_archive_projection(raw_archive)
        if (hashlib.sha256(raw_archive).hexdigest() != source["archiveSha256"]
                or any(actual[key] != source[key] for key in actual)):
            raise ValueError("Raw parent archive/projection mismatch")
    if raw_history is not None and (hashlib.sha256(raw_history).hexdigest() != source["historyRawSha256"]
                                   or json.loads(raw_history) != history):
        raise ValueError("Raw parent history mismatch")
    return {"parentActions": len(rows), "parentOriginalActionDate": originals[0]["action_date"],
            "parentOriginalReportedOffers": int(originals[0]["number_of_offers_received"]),
            "parentMultipleAwardCode": originals[0]["multiple_or_single_award_idv_code"],
            "parentOfferSourceValuesRecovered": 0}


def guidance_diagnostics(guidance, raw_guidance=None):
    """Authenticate optional bytes, not historical publication or VA applicability."""
    boundary = {
        "scope": "archived_dod_guidance_not_va_record_or_complete_dictionary",
        "independentReviewStatus": "pending", "vaApplicabilityEstablished": False,
        "fieldIntroductionDateEstablished": False, "xmlCodeMappingEstablished": False,
        "recordSpecificOfferSourceRecovered": False, "offerDiscrepancyResolved": False,
        "historicalCaptureTimeVerified": False,
    }
    if any(guidance.get(k) != v for k, v in boundary.items()):
        raise ValueError("Historical guidance scope or promotion mismatch")
    if not guidance.get("selection") or not guidance.get("interpretation"):
        raise ValueError("Historical guidance selection or interpretation missing")
    sources = guidance.get("sources", [])
    if ([s.get("revisionDateDisplayed") for s in sources] != list(GUIDANCE_URLS)
            or guidance.get("section") != "PGI 204.606(3)(xiv)(M)(1)-(2)"):
        raise ValueError("Historical guidance source frame or section mismatch")
    expected_fields = {
        "Number of Offers Received": "specific_order_count_for_multiple_award_orders",
        "IDV Number of Offers": "original_contract_count_displayed_separately",
        "Number of Offers Source": "system_generated_action_entry_or_parent_prepopulation",
    }
    for source in sources:
        revision = source["revisionDateDisplayed"]
        if (source.get("url") != GUIDANCE_URLS[revision]
                or source.get("archivePathDate") != {"2023-01-31": "2023-04-27",
                                                     "2024-05-30": "2024-05-30"}[revision]
                or not re.fullmatch(r"[0-9a-f]{64}", source.get("rawSha256", ""))
                or source.get("fieldInterpretations") != expected_fields
                or not source.get("reviewScope") or not source.get("sourceCautions")
                or source.get("sourceVintage") != "2026_retrieval_of_archive_labelled_guidance"
                or not date.fromisoformat(revision) < date(2024, 5, 31)
                or not date.fromisoformat(source["retrievedDate"]) > date(2024, 5, 31)):
            raise ValueError("Historical guidance provenance or field distinction mismatch")
        if revision == "2024-05-30" and (
                source.get("pdfPageCount") != 27 or source.get("reviewedPdfPages") != [1, 22, 23]
                or source.get("printedPageLabels") != ["204.6-1", "204.6-22", "204.6-23"]):
            raise ValueError("Historical guidance PDF review scope mismatch")
    if raw_guidance is not None:
        if set(raw_guidance) - set(GUIDANCE_URLS):
            raise ValueError("Unknown historical guidance raw source")
        for source in sources:
            raw = raw_guidance.get(source["revisionDateDisplayed"])
            if raw is not None and hashlib.sha256(raw).hexdigest() != source["rawSha256"]:
                raise ValueError("Raw historical guidance hash mismatch")
    return {"archivedGuidanceSources": len(sources),
            "oldestReviewedGuidanceRevision": min(GUIDANCE_URLS),
            "historicalGuidanceFieldDistinctions": len(expected_fields),
            "vaGuidanceApplicabilityEstablished": False}


def validate(review, original_review, provisional_links, docket_sources, raw_html=None, training_pdf=None,
             parent_archive=None, parent_history=None, raw_guidance=None):
    """Check projections and optional acquired bytes; human review stays separate."""
    if (review.get("schema") != "gao-procurement-publisher-review-v1"
            or review.get("originalReviewFingerprint") != fingerprint(original_review)
            or review.get("reviewFingerprint") != fingerprint(
                {k: v for k, v in review.items() if k != "reviewFingerprint"})):
        raise ValueError("Stale publisher review fingerprint or original-action baseline")
    boundary = {"independentReviewStatus": "pending", "baselineUnchanged": True,
                "solicitationIdentityPromoted": False, "awardSpecificDatesPromoted": False,
                "historicalExclusionsPromoted": False, "offerDiscrepancyResolved": False,
                "representativeSamExport": False, "causalEffect": "not_identified"}
    if any(review.get(k) != value for k, value in boundary.items()):
        raise ValueError("Unsupported publisher promotion or claim boundary")
    for key in ("selection", "sourceAuthentication", "scope", "reviewer"):
        if not review.get(key):
            raise ValueError("Missing publisher selection/review provenance")
    va = review["vaSource"]
    if (va["url"] != VA_URL or va["tableHeading"] != HEADING or va["header"] != HEADER
            or va["pageUpdatedDate"] != "2026-08-27"
            or not date.fromisoformat(va["pageUpdatedDate"]) <= date.fromisoformat(review["reviewDate"])
            or va["snapshotScope"] != "current_page_not_contemporaneous_2024_archive"):
        raise ValueError("Publisher source/date scope mismatch")
    rows = project_rows(va["nativeRows"])
    if (rows != va["rows"] or [r["serviceAreaNative"] for r in rows] != AREAS
            or va["nativeRowsFingerprint"] != fingerprint(va["nativeRows"])):
        raise ValueError("Incomplete publisher frame or stale native projection")
    training = review["offerSourceDocumentation"]
    if (training["url"] != TRAINING_URL or training["reviewedPdfPages"] != [1, 41]
            or training["pdfPageCount"] != 68 or training["documentYear"] != 2024
            or training["reportedServicePackDeploymentDate"] != "2024-01-27"
            or training["reportedDictionaryAdditions"] != ["Type Of Set-aside Source", "Number Of Offers Received Source"]
            or training["evidenceScope"] != "dictionary_documentation_not_field_introduction_or_record_values"
            or training["recordSpecificOfferSourceRecovered"] is not False
            or training["completeHistoricalDictionaryRecovered"] is not False):
        raise ValueError("Historical documentation scope or source mismatch")
    for source in (va, training):
        if not re.fullmatch(r"[0-9a-f]{64}", source["rawSha256"]):
            raise ValueError("Missing publisher raw hash")
    if raw_html is not None:
        parsed = parse_html(raw_html)
        if (hashlib.sha256(raw_html).hexdigest() != va["rawSha256"]
                or any(parsed[k] != va[k] for k in parsed)):
            raise ValueError("Raw publisher HTML hash or projection mismatch")
    if training_pdf is not None and hashlib.sha256(training_pdf).hexdigest() != training["rawSha256"]:
        raise ValueError("Raw training PDF hash mismatch")
    guidance = guidance_diagnostics(review.get("historicalOfferGuidance", {}), raw_guidance)
    by_key = defaultdict(list)
    for row in rows:
        by_key[(row["parentPiid"], row["piid"])].append(row)
    aliases = {"Other Government Agencies (OGAs)": "OGA"}
    corroboration, matched_piids, absent = [], set(), []
    for award in original_review["awards"]:
        piid = award["piid"]
        matches = by_key.get((award["originalProjection"]["parent_award_id_piid"], piid), [])
        if not matches:
            absent.append(piid)
            continue
        if len(matches) != 1:
            raise ValueError("Ambiguous publisher identity for pilot award")
        row = matches[0]
        area = aliases.get(row["serviceAreaNative"], row["serviceAreaNative"])
        if area != award["provisionalServiceArea"] or row["awardeeNative"] != "Medline Industries, LP":
            raise ValueError("Publisher service-area or awardee disagrees with pilot")
        matched_piids.add(piid)
        corroboration.append({"piid": piid, "serviceArea": area,
                              "publisherRowNumber": row["rowNumber"],
                              "originalMappingBasis": award["mappingStatus"],
                              "publisherEvidence": "explicit_current_service_area_label",
                              "independentReviewStatus": "pending"})
    duplicates = {piid: [r["serviceAreaNative"] for r in group]
                  for (_, piid), group in by_key.items() if len(group) > 1}
    # The repeated newer PIID is preserved, not corrected or assigned to the old VISN 8 award.
    if (duplicates != {"36C10X25N0014": ["VISN 7", "VISN 8 excluding Puerto Rico"]}
            or sorted(matched_piids) != ["36C10X24N0074", "36C10X24N0088", "36C10X24N0108"]
            or absent != ["36C10X24N0089"]):
        raise ValueError("Publisher duplicate/unmatched identity requires new source review")
    supported = [r for r in provisional_links if r["piid"] in matched_piids]
    footnotes = {r["serviceArea"]: r["caseNumbers"]
                 for r in docket_sources["decisionReview"]["serviceAreaFootnotes"]}
    expected_pairs = {(a["piid"], a["provisionalServiceArea"], case)
                      for a in original_review["awards"] for case in footnotes[a["provisionalServiceArea"]]}
    if (original_review["docketSourceFingerprint"] != fingerprint(docket_sources)
            or {(r["piid"], r["serviceArea"], r["decisionCaseId"]) for r in provisional_links} != expected_pairs
            or len(provisional_links) != len(expected_pairs)
            or any(r["status"] != "provisional_not_promoted" for r in provisional_links)):
        raise ValueError("Publisher follow-up requires unchanged complete provisional links")
    parent = parent_diagnostics(review["parentVehicleSource"], original_review, parent_archive, parent_history)
    return {
        "publisherRows": len(rows), "uniqueParentChildKeys": len(by_key),
        "duplicateCurrentKeys": duplicates, "pilotAwardsCorroborated": len(corroboration),
        "previousAmountOnlyAwardsCorroborated": sum(not a["explicitServiceArea"] and a["piid"] in matched_piids
                                                    for a in original_review["awards"]),
        "pilotPiidsAbsentFromCurrentTable": absent,
        "corroboratedProvisionalPairs": len(supported),
        "distinctCorroboratedDockets": len({r["decisionCaseId"] for r in supported}),
        **parent, **guidance, "offerSourceDocumentedIn2024": True, "recordSpecificOfferSourcesRecovered": 0,
        "independentlyReviewedMappings": 0, "awardSpecificDatesPromoted": 0,
        "historicalExclusionsPromoted": 0, "causalEffect": "not_identified",
    }, corroboration
