#!/usr/bin/env python3
"""Profile only manifest-selected archived prime transactions; never infer SAM status.

--scan reads the ignored original ZIPs and saves a public compact profile.
Default mode checks the saved profile against the frozen manifest and reproduces
the reports without requiring the archives. It is not a second raw-source audit.
"""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
from io import TextIOWrapper
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/snapshots/2024-env/normalized/usaspending-procurement-bulk-summary.json"
PROFILE = ROOT / "data/calibration/first-wave/procurement-bulk-frame-profile.json"
TYPE_REVIEW = ROOT / "data/calibration/first-wave/procurement-bulk-type-review.json"
FIELDS = (
    "award_id_piid", "parent_award_id_piid", "modification_number",
    "federal_action_obligation", "action_date", "recipient_name", "recipient_uei",
    "awarding_agency_name", "awarding_sub_agency_name", "award_type",
    "type_of_contract_pricing", "extent_competed", "number_of_offers_received",
)
CHILD_TYPES = {"BPA CALL", "PURCHASE ORDER", "DELIVERY ORDER", "DEFINITIVE CONTRACT"}
ROW_FIELDS = (
    "rows", "childDescriptionRows", "blankAwardTypeRows", "otherAwardTypeRows",
    "afterExclusionCompetitionRows", "missingOffersRows", "zeroOffersRows",
    "missingModificationRows", "outsideDateRows", "wrongAgencyRows",
)
MAP_FIELDS = ("missingFields", "awardTypeRows", "competitionRows", "obligationSignRows")
MONEY_FIELDS = ("netObligationDollars", "absoluteObligationDollars")


def sha256(path):
    with path.open("rb") as source:
        digest = hashlib.sha256()
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
        return digest.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_manifest(manifest):
    """Require every declared agency-day exactly once, including leap day."""
    start, end = date.fromisoformat(manifest["dateFrom"]), date.fromisoformat(manifest["dateTo"])
    agencies = manifest["agencyFilter"]
    if isinstance(agencies, str):
        agencies = [value.strip() for value in agencies.split(",")]
    if start > end or not agencies or len(set(agencies)) != len(agencies):
        raise ValueError("Invalid manifest population")
    if len(agencies) != manifest["agencyCount"] or len(manifest["strata"]) != manifest["strataCount"]:
        raise ValueError("Manifest agency/stratum count mismatch")
    coverage = defaultdict(Counter)
    paths = set()
    for row in manifest["strata"]:
        path = Path(row["downloadFile"])
        if (path.is_absolute() or ".." in path.parts or path.suffix != ".zip"
                or path.parts[:3] != ("data", "raw", "usaspending-transaction-downloads")
                or str(path) in paths):
            raise ValueError("Unsafe or duplicate manifest archive path")
        paths.add(str(path))
        if row["agency"] not in agencies or row["status"] != "ready":
            raise ValueError("Unknown agency or unready stratum")
        first, last = date.fromisoformat(row["startDate"]), date.fromisoformat(row["endDate"])
        if first < start or last > end or first > last:
            raise ValueError("Stratum outside manifest dates")
        for offset in range((last - first).days + 1):
            coverage[row["agency"]][first + timedelta(days=offset)] += 1
        expected = int(row["transactionCount"])
        actual = int(row["normalizedRows"])
        if (min(expected, actual) < 0 or int(row["expectedRows"]) != expected
                or int(row["validatedRows"]) != actual
                or int(row["rowCountDrift"]) != actual - expected):
            raise ValueError("Inconsistent manifest stratum counts")
    days = (end - start).days + 1
    if any(len(coverage[a]) != days or any(n != 1 for n in coverage[a].values()) for a in agencies):
        raise ValueError("Manifest agency-date coverage gap or overlap")
    planned = sum(int(row["transactionCount"]) for row in manifest["strata"])
    downloaded = sum(int(row["normalizedRows"]) for row in manifest["strata"])
    drifts = [int(row["rowCountDrift"]) for row in manifest["strata"]]
    if (planned != manifest["plannedTransactionRows"] or downloaded != manifest["downloadedNormalizedRows"]
            or sum(drifts) != manifest["acceptedRowCountDrift"]
            or sum(abs(n) for n in drifts) != manifest["acceptedRowCountDriftAbs"]
            or sum(n != 0 for n in drifts) != manifest["acceptedRowCountDriftStrata"]):
        raise ValueError("Inconsistent manifest aggregate counts")
    return days


def profile_rows(reader, agency, start, end):
    result = {key: 0 for key in ROW_FIELDS}
    maps = {key: Counter() for key in MAP_FIELDS}
    by_type_money = defaultdict(Decimal)
    net = absolute = Decimal(0)
    for row in reader:
        if set(row) != set(FIELDS) or any(value is None for value in row.values()):
            raise ValueError("Malformed source row shape")
        values = {key: value.strip() for key, value in row.items()}
        result["rows"] += 1
        for key, value in values.items():
            if not value:
                maps["missingFields"][key] += 1
        action = date.fromisoformat(values["action_date"])
        result["outsideDateRows"] += not start <= action <= end
        result["wrongAgencyRows"] += values["awarding_agency_name"] != agency
        award_type = values["award_type"]
        maps["awardTypeRows"][award_type] += 1
        if not award_type:
            result["blankAwardTypeRows"] += 1
        elif award_type.upper() in CHILD_TYPES:
            result["childDescriptionRows"] += 1
        else:
            result["otherAwardTypeRows"] += 1
        competition = values["extent_competed"]
        maps["competitionRows"][competition] += 1
        result["afterExclusionCompetitionRows"] += "exclusion" in competition.lower()
        offers = values["number_of_offers_received"]
        if not offers:
            result["missingOffersRows"] += 1
        else:
            offer_count = Decimal(offers)
            if not offer_count.is_finite() or offer_count < 0 or offer_count != int(offer_count):
                raise ValueError("Invalid source offer count")
            result["zeroOffersRows"] += offer_count == 0
        result["missingModificationRows"] += not values["modification_number"]
        try:
            amount = Decimal(values["federal_action_obligation"])
        except InvalidOperation as exc:
            raise ValueError("Invalid source obligation") from exc
        if not amount.is_finite() or amount != amount.quantize(Decimal("0.01")):
            raise ValueError("Nonfinite or sub-cent source obligation")
        net += amount
        absolute += abs(amount)
        by_type_money[award_type] += amount
        maps["obligationSignRows"]["positive" if amount > 0 else "negative" if amount < 0 else "zero"] += 1
    result.update({key: dict(sorted(value.items())) for key, value in maps.items()})
    result.update(netObligationDollars=f"{net:.2f}", absoluteObligationDollars=f"{absolute:.2f}",
                  awardTypeNetObligationDollars={key: f"{value:.2f}" for key, value in sorted(by_type_money.items())})
    return result


def combine(profiles):
    result = {key: sum(row[key] for row in profiles) for key in ROW_FIELDS}
    for key in MAP_FIELDS:
        counts = Counter()
        for row in profiles:
            counts.update(row[key])
        result[key] = dict(sorted(counts.items()))
    for key in MONEY_FIELDS:
        result[key] = f"{sum((Decimal(row[key]) for row in profiles), Decimal(0)):.2f}"
    amounts = defaultdict(Decimal)
    for row in profiles:
        for label, amount in row["awardTypeNetObligationDollars"].items():
            amounts[label] += Decimal(amount)
    result["awardTypeNetObligationDollars"] = {key: f"{value:.2f}" for key, value in sorted(amounts.items())}
    return result


def scan_archive(path, stratum):
    if sha256(path) != stratum["zipSha256"]:
        raise ValueError("Archive hash differs from frozen manifest")
    profiles, members = [], []
    with zipfile.ZipFile(path) as archive:
        selected = [name for name in archive.namelist() if "PrimeTransactions" in name and name.endswith(".csv")]
        if not selected or len(set(selected)) != len(selected):
            raise ValueError("Missing or duplicate prime transaction member")
        for name in selected:
            with archive.open(name) as source:
                reader = csv.DictReader(TextIOWrapper(source, encoding="utf-8-sig", newline=""))
                if reader.fieldnames != list(FIELDS):
                    raise ValueError("Archive source header differs from frozen 13-field contract")
                value = profile_rows(reader, stratum["agency"], date.fromisoformat(stratum["startDate"]), date.fromisoformat(stratum["endDate"]))
                profiles.append(value)
                members.append({"name": name, "rows": value["rows"]})
    result = combine(profiles)
    if result["rows"] != int(stratum["normalizedRows"]):
        raise ValueError("Archive row count differs from frozen manifest")
    if sha256(path) != stratum["zipSha256"]:
        raise ValueError("Archive changed during scan")
    return {"manifestStratum": stratum, "primeMembers": members, "profile": result}


def validate_profile(saved, manifest, manifest_hash):
    days = check_manifest(manifest)
    if (saved["schema"] != "procurement-bulk-frame-profile-v1"
            or saved["manifestSha256"] != manifest_hash
            or saved["sourceCreatedAt"] != manifest["createdAt"]
            or saved["sourceHeader"] != list(FIELDS)
            or saved["inclusiveDaysPerAgency"] != days
            or [row["manifestStratum"] for row in saved["strata"]] != manifest["strata"]):
        raise ValueError("Saved profile provenance differs from frozen manifest")
    for row in saved["strata"]:
        profile = row["profile"]
        n = profile["rows"]
        if (n != int(row["manifestStratum"]["normalizedRows"])
                or not row["primeMembers"] or sum(m["rows"] for m in row["primeMembers"]) != n
                or any("PrimeTransactions" not in m["name"] or not m["name"].endswith(".csv") for m in row["primeMembers"])
                or len({m["name"] for m in row["primeMembers"]}) != len(row["primeMembers"])):
            raise ValueError("Saved profile member or row-count mismatch")
        if any(type(profile[key]) is not int or not 0 <= profile[key] <= n for key in ROW_FIELDS):
            raise ValueError("Invalid profile count")
        if any(type(value) is not int or not 0 <= value <= n for key in MAP_FIELDS for value in profile[key].values()):
            raise ValueError("Invalid profile category count")
        if not set(profile["missingFields"]) <= set(FIELDS):
            raise ValueError("Unknown missingness field")
        if (profile["zeroOffersRows"] + profile["missingOffersRows"] > n
                or profile["childDescriptionRows"] + profile["blankAwardTypeRows"] + profile["otherAwardTypeRows"] != n
                or profile["childDescriptionRows"] != sum(count for label, count in profile["awardTypeRows"].items() if label.upper() in CHILD_TYPES)
                or profile["blankAwardTypeRows"] != profile["awardTypeRows"].get("", 0)
                or any(sum(profile[key].values()) != n for key in ("awardTypeRows", "competitionRows", "obligationSignRows"))
                or profile["blankAwardTypeRows"] != profile["missingFields"].get("award_type", 0)
                or profile["missingOffersRows"] != profile["missingFields"].get("number_of_offers_received", 0)
                or profile["missingModificationRows"] != profile["missingFields"].get("modification_number", 0)
                or profile["afterExclusionCompetitionRows"] != sum(count for label, count in profile["competitionRows"].items() if "exclusion" in label.lower())):
            raise ValueError("Inconsistent profile partitions or missingness")
        amounts = [Decimal(profile[key]) for key in MONEY_FIELDS]
        amounts += list(map(Decimal, profile["awardTypeNetObligationDollars"].values()))
        if (any(not value.is_finite() or value != value.quantize(Decimal("0.01")) for value in amounts)
                or Decimal(profile["absoluteObligationDollars"]) < abs(Decimal(profile["netObligationDollars"]))
                or set(profile["awardTypeNetObligationDollars"]) != set(profile["awardTypeRows"])
                or Decimal(profile["netObligationDollars"]) != sum(map(Decimal, profile["awardTypeNetObligationDollars"].values()))):
            raise ValueError("Inconsistent profile money partitions")
    if saved["total"] != combine([row["profile"] for row in saved["strata"]]):
        raise ValueError("Saved profile total mismatch")
    if saved["profileFingerprint"] != fingerprint(saved["strata"]):
        raise ValueError("Saved profile fingerprint mismatch")
    return saved["total"]


def validate_type_review(review, saved, raw_root=None):
    """Check saved evidence joins; optionally recheck the excerpt in its ZIP."""
    source = review["archive"]
    matches = [row for row in saved["strata"] if row["manifestStratum"]["downloadFile"] == source["downloadFile"]]
    if len(matches) != 1 or source["zipSha256"] != matches[0]["manifestStratum"]["zipSha256"]:
        raise ValueError("Type review archive provenance mismatch")
    members = {m["name"]: m["rows"] for m in matches[0]["primeMembers"]}
    if source["member"] not in members or not 1 <= source["dataRowNumber"] <= members[source["member"]]:
        raise ValueError("Type review source location mismatch")
    row, detail = source["row"], review["awardDetail"]["projection"]
    if (set(row) != set(FIELDS) or row["award_type"] != ""
            or row["award_id_piid"] != detail["piid"]
            or row["recipient_uei"] != detail["recipient_uei"]
            or row["recipient_name"] != detail["recipient_name"]
            or row["awarding_agency_name"] != detail["awarding_agency_name"]
            or detail["category"] != "idv" or not detail["type"].startswith("IDV_")
            or review["awardDetail"]["url"] != f"https://api.usaspending.gov/api/v2/awards/{detail['generated_unique_award_id']}/"
            or len(review["awardDetail"]["responseSha256"]) != 64
            or review["independentReview"] != "pending"):
        raise ValueError("Type review identity or scope mismatch")
    date.fromisoformat(review["retrievedDate"])
    if raw_root is not None:
        path = raw_root / source["downloadFile"]
        if sha256(path) != source["zipSha256"]:
            raise ValueError("Type review archive hash mismatch")
        with zipfile.ZipFile(path) as archive, archive.open(source["member"]) as stream:
            reader = csv.DictReader(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
            for number, raw in enumerate(reader, 1):
                if number == source["dataRowNumber"]:
                    if raw != row:
                        raise ValueError("Type review excerpt differs from raw archive")
                    break
            else:
                raise ValueError("Type review row absent from raw archive")
    return detail["type"]


def write_reports(saved, output):
    output.mkdir(parents=True, exist_ok=True)
    columns = ["agency", "startDate", "endDate", "plannedRows", "downloadedRows", "rowCountDrift", *ROW_FIELDS[1:], *MONEY_FIELDS]
    with (output / "procurement-bulk-frame-audit.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, columns)
        writer.writeheader()
        for row in saved["strata"]:
            s, p = row["manifestStratum"], row["profile"]
            writer.writerow({**{key: s[key] for key in ("agency", "startDate", "endDate", "rowCountDrift")},
                             "plannedRows": s["transactionCount"], "downloadedRows": p["rows"],
                             **{key: p[key] for key in (*ROW_FIELDS[1:], *MONEY_FIELDS)}})
    total = saved["total"]
    lines = ["# Archived procurement bulk frame audit", "", "## Dataset and checks", "",
             f"Archived bulk manifest created: {saved['sourceCreatedAt']}. Grain: archived prime transaction CSV rows, not distinct awards.",
             f"Exactly {len(saved['strata'])} manifest-selected ZIPs were scanned with matching SHA-256 and row counts; subaward files and superseded downloads were excluded.",
             f"The manifest covers each declared agency on all {saved['inclusiveDaysPerAgency']} inclusive FY2024 days, without gaps or overlaps.",
             "All 13 source columns were checked, with date/agency containment, missingness, award descriptions, competition and exact-decimal obligation summaries.",
             "Default report reproduction checks the committed profile, not the ignored raw archives; use --scan to repeat the raw audit.", "", "## Findings", "",
             "| Measure | Archived rows | Share of all rows |", "| --- | ---: | ---: |"]
    lines += [f"| {key} | {total[key]:,} | {100 * total[key] / total['rows']:.2f}% |" for key in ROW_FIELDS]
    lines += ["", "| Raw award description | Rows | Net obligation, dollars |", "| --- | ---: | ---: |"]
    lines += [f"| {label or '(blank, unresolved type)'} | {count:,} | {total['awardTypeNetObligationDollars'][label]} |" for label, count in total["awardTypeRows"].items()]
    lines += ["", "| Obligation sign | Rows |", "| --- | ---: |"]
    lines += [f"| {label} | {count:,} |" for label, count in total["obligationSignRows"].items()]
    lines += ["", "## Count/export discrepancies", "", "| Agency | Window | Planned | Exported | Difference |", "| --- | --- | ---: | ---: | ---: |"]
    for row in saved["strata"]:
        s = row["manifestStratum"]
        if int(s["rowCountDrift"]):
            lines.append(f"| {s['agency']} | {s['startDate']} to {s['endDate']} | {s['transactionCount']} | {s['normalizedRows']} | {s['rowCountDrift']} |")
    lines += ["", "## Interpretation, severity and remaining requirements", "",
              "- High, confirmed measurement risk: the collector requests A/B/C/D and IDV types. Blank raw award types become the legacy label `contract`; that label does not establish a child-action type. Do not classify every blank as an IDV. Reconcile A/B/C/D and vehicle records separately using native type codes.",
              "- High, confirmed semantic risk: the legacy bulk `exclusionFlag` tests whether competition text contains `exclusion`. It is not historical SAM vendor exclusion/debarment evidence. The [FPDS competition definition](https://www.fpds.gov/help/Extent_Competed.htm) identifies this as a competition procedure. It does not establish misconduct.",
              "- High, confirmed missingness risk: missing offers become zero in the legacy normalizer, but source blanks are not observed zero offers. No blank modification numbers were found in this scan, although the legacy normalizer also defaults those to `0`. Protest and firewall flags default to false without an observed overlay; they cannot establish absence.",
              "- High linkage limitation: the archived columns omit unique source transaction IDs, numeric awarding/parent subtier codes and native IDV type codes. Parent PIID is present raw but omitted from normalized rows. Row count agreement does not prove unique actions or a complete census; action-level uniqueness has not been tested without full keys.",
              "- Medium, confirmed count discrepancy but unknown cause: two count/export differences were accepted under a live tolerance. No count-time membership list is available here, so source revisions, omitted records and other causes are not adjudicated. Do not describe the difference as identified missing transactions.",
              f"- Signed net obligations are ${total['netObligationDollars']}; absolute obligations are ${total['absoluteObligationDollars']}. These are different summaries. Zero and negative actions remain in the denominator.",
              "- This audit validates archived-file consistency and reveals comparison limits. It does not obtain a SAM export, independently verify source-system completeness, measure protest/exclusion rates, or identify capture effects.", ""]
    lines += ["## Validation assessment", "", "Share with caveats as an archived-data quality report, not an estimation panel. The standalone notebook reproduces profile joins and totals; unit tests exercise malformed records, manifest gaps/overlaps, archive selection, source nulls, signed cents and stale evidence. See the reconciliation note for the separately verified blank-type IDV example and remaining acquisition requirements.", ""]
    (output / "procurement-bulk-frame-audit.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    manifest_hash = sha256(MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    days = check_manifest(manifest)
    if args.scan:
        strata = []
        for index, row in enumerate(manifest["strata"], 1):
            strata.append(scan_archive(ROOT / row["downloadFile"], row))
            print(f"Scanned {index}/{len(manifest['strata'])}: {row['agency']} {row['period']}", flush=True)
        saved = {"schema": "procurement-bulk-frame-profile-v1", "manifestSha256": manifest_hash,
                 "sourceCreatedAt": manifest["createdAt"], "inclusiveDaysPerAgency": days,
                 "sourceHeader": list(FIELDS), "strata": strata,
                 "total": combine([row["profile"] for row in strata]), "profileFingerprint": fingerprint(strata)}
        validate_profile(saved, manifest, manifest_hash)
    else:
        saved = json.loads(PROFILE.read_text(encoding="utf-8"))
        validate_profile(saved, manifest, manifest_hash)
    review = json.loads(TYPE_REVIEW.read_text(encoding="utf-8"))
    validate_type_review(review, saved, ROOT if args.scan else None)
    if sha256(MANIFEST) != manifest_hash:
        raise ValueError("Manifest changed during audit")
    if args.scan:
        PROFILE.write_text(json.dumps(saved, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_reports(saved, args.output)
    print(f"Validated {saved['total']['rows']:,} archived-row profile; no SAM or causal promotion")


if __name__ == "__main__":
    main()
