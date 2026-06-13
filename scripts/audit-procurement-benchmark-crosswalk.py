#!/usr/bin/env python3
"""Crosswalk procurement benchmarks to observed USAspending denominators."""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
RAW_BULK = ROOT / "data" / "raw" / "usaspending-procurement-bulk-transactions.csv"
CROSSWALK_JSON = ROOT / "data" / "snapshots" / "2024-env" / "normalized" / "usaspending-procurement-benchmark-crosswalk.json"

OLD_RECIPIENT_LOW = 0.25
OLD_RECIPIENT_HIGH = 0.40
OLD_MODIFICATION_LOW = 0.01
OLD_MODIFICATION_HIGH = 0.05


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--raw-csv", type=Path, default=RAW_BULK)
    parser.add_argument("--crosswalk-json", type=Path, default=CROSSWALK_JSON)
    parser.add_argument("--write-crosswalk", action="store_true")
    args = parser.parse_args()

    if args.write_crosswalk:
        payload = build_crosswalk(args.raw_csv)
        args.crosswalk_json.parent.mkdir(parents=True, exist_ok=True)
        args.crosswalk_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        payload = read_or_build_crosswalk(args.crosswalk_json, args.raw_csv)

    rows = payload_rows(payload)
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "procurement-benchmark-crosswalk.csv", rows)
    write_markdown(args.reports / "procurement-benchmark-crosswalk.md", payload, rows)
    print(f"Wrote {args.reports / 'procurement-benchmark-crosswalk.csv'}")
    print(f"Wrote {args.reports / 'procurement-benchmark-crosswalk.md'}")
    return 0


def read_or_build_crosswalk(path: Path, raw_csv: Path) -> dict[str, object]:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    if raw_csv.exists():
        return build_crosswalk(raw_csv)
    raise SystemExit(
        f"Missing {path.relative_to(ROOT)} and {raw_csv.relative_to(ROOT)}; "
        "run this script with --write-crosswalk where the raw USAspending CSV is available."
    )


def build_crosswalk(raw_csv: Path) -> dict[str, object]:
    if not raw_csv.exists():
        raise SystemExit(f"Missing raw USAspending bulk CSV: {raw_csv}")
    groups: dict[tuple[str, str], dict[str, object]] = {}

    with raw_csv.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            amount = abs_number(row.get("amount"))
            modified = is_modified(row)
            recipient = clean(row.get("recipient"), "Unknown recipient")
            agency = clean(row.get("agency"), "Unknown agency")
            award_type = clean(row.get("awardType"), "Unknown award type")
            award_id = clean(row.get("piid") or row.get("awardId"), "")
            group_keys = (
                ("all", "all"),
                ("agency", agency),
                ("awardType", award_type),
                ("agencyAwardType", f"{agency}||{award_type}"),
            )
            for dimension, value in group_keys:
                add_row(groups, dimension, value, amount, recipient, award_id, modified)

    rows = [finalize_group(dimension, value, group) for (dimension, value), group in groups.items()]
    rows.sort(key=lambda row: (dimension_rank(row["dimension"]), -row["amount"], row["value"]))
    selected_rows = select_rows(rows)
    return {
        "schema": "usaspending-procurement-benchmark-crosswalk-v1",
        "createdAt": generated_at(),
        "source": "data/raw/usaspending-procurement-bulk-transactions.csv",
        "oldBenchmarks": {
            "procurementRecipientTop3Share": {"low": OLD_RECIPIENT_LOW, "high": OLD_RECIPIENT_HIGH},
            "procurementExPostModificationShare": {"low": OLD_MODIFICATION_LOW, "high": OLD_MODIFICATION_HIGH},
        },
        "recommendedRanges": recommended_ranges(rows),
        "rows": selected_rows,
    }


def add_row(
    groups: dict[tuple[str, str], dict[str, object]],
    dimension: str,
    value: str,
    amount: float,
    recipient: str,
    award_id: str,
    modified: bool,
) -> None:
    key = (dimension, value)
    group = groups.setdefault(
        key,
        {
            "rowCount": 0,
            "modifiedRows": 0,
            "amount": 0.0,
            "modifiedAmount": 0.0,
            "recipientAmounts": defaultdict(float),
            "awards": set(),
            "modifiedAwards": set(),
        },
    )
    group["rowCount"] += 1
    group["amount"] += amount
    group["recipientAmounts"][recipient] += amount
    if award_id:
        group["awards"].add(award_id)
    if modified:
        group["modifiedRows"] += 1
        group["modifiedAmount"] += amount
        if award_id:
            group["modifiedAwards"].add(award_id)


def finalize_group(dimension: str, value: str, group: dict[str, object]) -> dict[str, object]:
    amount = float(group["amount"])
    row_count = int(group["rowCount"])
    awards = group["awards"]
    modified_awards = group["modifiedAwards"]
    recipient_amounts = group["recipientAmounts"]
    assert isinstance(awards, set)
    assert isinstance(modified_awards, set)
    assert isinstance(recipient_amounts, defaultdict)
    return {
        "dimension": dimension,
        "value": value,
        "rowCount": row_count,
        "awardCount": len(awards),
        "amount": amount,
        "top3RecipientShare": top_share(recipient_amounts, amount, 3),
        "modifiedActionShare": safe_divide(int(group["modifiedRows"]), row_count),
        "modifiedAwardShare": safe_divide(len(modified_awards), len(awards)),
        "amountWeightedModificationShare": safe_divide(float(group["modifiedAmount"]), amount),
        "recipientBenchmarkClass": recipient_benchmark_class(top_share(recipient_amounts, amount, 3)),
        "modificationBenchmarkClass": modification_benchmark_class(
            safe_divide(int(group["modifiedRows"]), row_count),
            safe_divide(len(modified_awards), len(awards)),
            safe_divide(float(group["modifiedAmount"]), amount),
        ),
    }


def select_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    selected.extend(row for row in rows if row["dimension"] == "all")
    selected.extend(row for row in rows if row["dimension"] == "agency")
    selected.extend(row for row in rows if row["dimension"] == "awardType")
    agency_award = [
        row for row in rows
        if row["dimension"] == "agencyAwardType" and float(row["amount"]) >= 1000.0
    ]
    selected.extend(sorted(agency_award, key=lambda row: float(row["top3RecipientShare"]), reverse=True)[:40])
    return selected


def recommended_ranges(rows: list[dict[str, object]]) -> dict[str, object]:
    agency_rows = [row for row in rows if row["dimension"] == "agency"]
    award_type_rows = [row for row in rows if row["dimension"] == "awardType"]
    agency_award_rows = [
        row for row in rows
        if row["dimension"] == "agencyAwardType" and float(row["amount"]) >= 1000.0
    ]
    all_row = next(row for row in rows if row["dimension"] == "all")
    return {
        "procurementRecipientTop3Share": {
            "bulkAggregate": round(float(all_row["top3RecipientShare"]), 6),
            "agencyRange": value_range(agency_rows, "top3RecipientShare"),
            "awardTypeRange": value_range(award_type_rows, "top3RecipientShare"),
            "agencyAwardTypeHighAmountRange": value_range(agency_award_rows, "top3RecipientShare"),
            "recommendedValidationLow": 0.05,
            "recommendedValidationMid": 0.25,
            "recommendedValidationHigh": 0.55,
            "interpretation": "The old 0.25-0.40 benchmark fits high-concentration agency or award-type slices, not the 12-agency aggregate.",
        },
        "procurementExPostModificationShare": {
            "bulkActionRowShare": round(float(all_row["modifiedActionShare"]), 6),
            "bulkDistinctAwardShare": round(float(all_row["modifiedAwardShare"]), 6),
            "bulkAmountWeightedShare": round(float(all_row["amountWeightedModificationShare"]), 6),
            "agencyActionRowRange": value_range(agency_rows, "modifiedActionShare"),
            "awardTypeActionRowRange": value_range(award_type_rows, "modifiedActionShare"),
            "agencyAwardTypeHighAmountActionRowRange": value_range(agency_award_rows, "modifiedActionShare"),
            "recommendedValidationLow": 0.10,
            "recommendedValidationMid": 0.17,
            "recommendedValidationHigh": 0.90,
            "interpretation": "The old 0.01-0.05 benchmark is a delta/stress-screen concept and should not be used as an absolute transaction-incidence range.",
        },
    }


def value_range(rows: list[dict[str, object]], field: str) -> dict[str, float]:
    values = [float(row[field]) for row in rows]
    if not values:
        return {"min": 0.0, "max": 0.0}
    return {"min": round(min(values), 6), "max": round(max(values), 6)}


def payload_rows(payload: dict[str, object]) -> list[dict[str, str]]:
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return []
    output = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        output.append(
            {
                "dimension": str(row.get("dimension", "")),
                "value": str(row.get("value", "")),
                "rowCount": str(int(float(row.get("rowCount", 0) or 0))),
                "awardCount": str(int(float(row.get("awardCount", 0) or 0))),
                "amount": f4(row.get("amount", 0)),
                "top3RecipientShare": f4(row.get("top3RecipientShare", 0)),
                "modifiedActionShare": f4(row.get("modifiedActionShare", 0)),
                "modifiedAwardShare": f4(row.get("modifiedAwardShare", 0)),
                "amountWeightedModificationShare": f4(row.get("amountWeightedModificationShare", 0)),
                "recipientBenchmarkClass": str(row.get("recipientBenchmarkClass", "")),
                "modificationBenchmarkClass": str(row.get("modificationBenchmarkClass", "")),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "dimension",
        "value",
        "rowCount",
        "awardCount",
        "amount",
        "top3RecipientShare",
        "modifiedActionShare",
        "modifiedAwardShare",
        "amountWeightedModificationShare",
        "recipientBenchmarkClass",
        "modificationBenchmarkClass",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, payload: dict[str, object], rows: list[dict[str, str]]) -> None:
    ranges = payload.get("recommendedRanges", {})
    recipient = ranges.get("procurementRecipientTop3Share", {}) if isinstance(ranges, dict) else {}
    modification = ranges.get("procurementExPostModificationShare", {}) if isinstance(ranges, dict) else {}
    lines = [
        "# Procurement Benchmark Crosswalk",
        "",
        "This audit maps procurement source moments to the denominator used to compute them. It separates aggregate USAspending transaction-history moments from agency, award-type, and agency-by-award-type slices so validation does not compare unlike quantities.",
        "",
        "## Benchmark Remapping",
        "",
        f"- Top-3 recipient concentration: bulk aggregate `{fmt(recipient.get('bulkAggregate'))}`; agency range `{range_text(recipient.get('agencyRange'))}`; award-type range `{range_text(recipient.get('awardTypeRange'))}`; high-amount agency/award-type range `{range_text(recipient.get('agencyAwardTypeHighAmountRange'))}`.",
        f"- The old top-contractor benchmark `{OLD_RECIPIENT_LOW:.2f}-{OLD_RECIPIENT_HIGH:.2f}` is retained as a high-concentration slice diagnostic, not as the configured-agency aggregate denominator.",
        f"- Modification incidence: action-row `{fmt(modification.get('bulkActionRowShare'))}`; distinct-award `{fmt(modification.get('bulkDistinctAwardShare'))}`; amount-weighted `{fmt(modification.get('bulkAmountWeightedShare'))}`.",
        f"- The old ex-post modification benchmark `{OLD_MODIFICATION_LOW:.2f}-{OLD_MODIFICATION_HIGH:.2f}` is retained as a delta/stress-screen concept, not as an absolute transaction-incidence range.",
        "",
        "## Selected Crosswalk Rows",
        "",
        "| Dimension | Value | Rows | Awards | Amount | Top-3 Recipients | Modified Actions | Modified Awards | Amount-Wtd Mod. | Recipient Class | Modification Class |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        if row["dimension"] == "agencyAwardType" and float(row["top3RecipientShare"]) < OLD_RECIPIENT_LOW:
            continue
        lines.append(
            f"| {row['dimension']} | {md(row['value'])} | {row['rowCount']} | {row['awardCount']} | {row['amount']} | {row['top3RecipientShare']} | {row['modifiedActionShare']} | {row['modifiedAwardShare']} | {row['amountWeightedModificationShare']} | {row['recipientBenchmarkClass']} | {row['modificationBenchmarkClass']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def recipient_benchmark_class(value: float) -> str:
    if value < OLD_RECIPIENT_LOW:
        return "below old top-contractor range"
    if value <= OLD_RECIPIENT_HIGH:
        return "inside old top-contractor range"
    return "above old top-contractor range"


def modification_benchmark_class(action_share: float, award_share: float, amount_share: float) -> str:
    if action_share <= OLD_MODIFICATION_HIGH:
        return "inside old absolute range"
    if award_share <= OLD_MODIFICATION_HIGH:
        return "award-share inside old range"
    if amount_share <= OLD_MODIFICATION_HIGH:
        return "amount-share inside old range"
    return "above old absolute range"


def top_share(values: defaultdict[str, float], total: float, count: int) -> float:
    if total <= 0:
        return 0.0
    return sum(sorted(values.values(), reverse=True)[:count]) / total


def is_modified(row: dict[str, str]) -> bool:
    modification = clean(row.get("modificationNumber"), "").lower()
    return str(row.get("exPostModification", "")).lower() == "true" or modification not in {
        "",
        "0",
        "none",
        "null",
        "nan",
    }


def abs_number(value: object) -> float:
    try:
        return abs(float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def clean(value: object, default: str) -> str:
    text = str(value or "").strip()
    return text if text else default


def dimension_rank(dimension: object) -> int:
    return {"all": 0, "agency": 1, "awardType": 2, "agencyAwardType": 3}.get(str(dimension), 9)


def f4(value: object) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return "0.0000"


def fmt(value: object) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return "n/a"


def range_text(value: object) -> str:
    if not isinstance(value, dict):
        return "n/a"
    return f"{fmt(value.get('min'))}-{fmt(value.get('max'))}"


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def generated_at() -> str:
    return os.environ.get(
        "LOBBY_CAPTURE_REPORT_TIMESTAMP",
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
