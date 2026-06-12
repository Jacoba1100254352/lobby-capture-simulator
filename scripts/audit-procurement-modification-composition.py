#!/usr/bin/env python3
"""Audit composition of procurement modification rows.

The source-moment layer reports a nonzero modification share from the committed
USAspending transaction/action panel. That number is useful, but reviewers need
to know whether it reflects a representative SAM/FPDS denominator or a bounded
source-sample composition effect. This report decomposes modified actions by
source, agency, award type, and recipient concentration.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


REPORTS = Path("reports")
SNAPSHOT = Path("data/snapshots/2024-env")
LIVE_STATUS = SNAPSHOT / "live-run-status.csv"

SOURCES = [
    {
        "source": "usaspending-procurement-actions",
        "path": "usaspending-procurement-actions.csv",
        "role": "primary bounded action panel",
        "claimBoundary": "bounded USAspending transaction/action diagnostics; not representative SAM/FPDS modification calibration",
    },
    {
        "source": "sam-contract-awards",
        "path": "sam-contract-awards.csv",
        "role": "optional SAM/FPDS-style action panel",
        "claimBoundary": "calibration-grade only after representative SAM/FPDS action-history rows are archived",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args()

    normalized = args.snapshot / "normalized"
    statuses = read_live_status(args.snapshot / LIVE_STATUS.name)

    rows: list[dict[str, str]] = []
    source_rows: dict[str, list[dict[str, str]]] = {}
    for source in SOURCES:
        path = normalized / str(source["path"])
        current_rows = read_rows(path)
        source_rows[str(source["source"])] = current_rows
        rows.append(composition_row(source, "source", str(source["source"]), current_rows, current_rows, statuses))

    primary = source_rows.get("usaspending-procurement-actions", [])
    rows.extend(grouped_rows("usaspending-procurement-actions", primary, "agency", 12))
    rows.extend(grouped_rows("usaspending-procurement-actions", primary, "awardType", 12))
    rows.extend(grouped_rows("usaspending-procurement-actions", primary, "recipient", 8))

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "procurement-modification-composition-audit.csv", rows)
    write_markdown(args.reports / "procurement-modification-composition-audit.md", rows)
    print(f"Wrote {args.reports / 'procurement-modification-composition-audit.csv'}")
    print(f"Wrote {args.reports / 'procurement-modification-composition-audit.md'}")
    return 0


def read_live_status(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get("source", ""): row for row in csv.DictReader(source)}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def grouped_rows(source_name: str, all_rows: list[dict[str, str]], group_key: str, limit: int) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_rows:
        group_value = row.get(group_key, "").strip() or "unknown"
        groups[group_value].append(row)
    sorted_groups = sorted(
        groups.items(),
        key=lambda item: sum(number(row.get("amount")) for row in item[1]),
        reverse=True,
    )
    source = {
        "source": source_name,
        "role": f"{group_key} composition",
        "claimBoundary": "within-panel composition diagnostic; not a representative national procurement modification rate",
    }
    return [
        composition_row(source, group_key, group_value, group_rows, all_rows, {})
        for group_value, group_rows in sorted_groups[:limit]
    ]


def composition_row(
    source: dict[str, object],
    group_type: str,
    group_value: str,
    rows: list[dict[str, str]],
    panel_rows: list[dict[str, str]],
    statuses: dict[str, dict[str, str]],
) -> dict[str, str]:
    modified_rows = [row for row in rows if is_modified(row)]
    initial_rows = [row for row in rows if not is_modified(row)]
    amount = sum(number(row.get("amount")) for row in rows)
    modified_amount = sum(number(row.get("amount")) for row in modified_rows)
    panel_amount = sum(number(row.get("amount")) for row in panel_rows)
    panel_modified_amount = sum(number(row.get("amount")) for row in panel_rows if is_modified(row))
    status = statuses.get(str(source.get("source", "")), {})
    return {
        "source": str(source.get("source", "")),
        "snapshotStatus": status.get("status", "missing" if not panel_rows and group_type == "source" else "derived"),
        "role": str(source.get("role", "")),
        "groupType": group_type,
        "groupValue": group_value,
        "rows": str(len(rows)),
        "modifiedRows": str(len(modified_rows)),
        "initialRows": str(len(initial_rows)),
        "modifiedActionShare": format_float(safe_divide(len(modified_rows), len(rows))),
        "amount": format_float(amount),
        "modifiedAmount": format_float(modified_amount),
        "amountWeightedModificationShare": format_float(safe_divide(modified_amount, amount)),
        "panelAmountShare": format_float(safe_divide(amount, panel_amount)),
        "panelModifiedAmountShare": format_float(safe_divide(modified_amount, panel_modified_amount)),
        "knownPiidShare": format_float(share_with_value(rows, "piid")),
        "knownUeiShare": format_float(share_with_value(rows, "uei")),
        "knownCompetitionShare": format_float(known_competition_share(rows)),
        "singleKnownOfferRows": str(sum(1 for row in rows if one_known_offer(row))),
        "priceOnlyRows": str(sum(1 for row in rows if flag(row.get("priceOnlyAward")))),
        "exclusionRows": str(sum(1 for row in rows if flag(row.get("exclusionFlag")))),
        "protestRows": str(sum(1 for row in rows if flag(row.get("protestFiled")))),
        "claimBoundary": str(source.get("claimBoundary", "")),
        "statusNote": status.get("notes", ""),
    }


def is_modified(row: dict[str, str]) -> bool:
    return flag(row.get("exPostModification")) or modification_sequence(row.get("modificationNumber")) > 0


def one_known_offer(row: dict[str, str]) -> bool:
    offers = number(row.get("numberOfOffers"))
    return 0.0 < offers <= 1.0


def known_competition_share(rows: list[dict[str, str]]) -> float:
    return safe_divide(
        sum(1 for row in rows if row.get("competitionType", "").strip().lower() not in {"", "unknown", "none", "null"}),
        len(rows),
    )


def share_with_value(rows: list[dict[str, str]], key: str) -> float:
    return safe_divide(sum(1 for row in rows if row.get(key, "").strip()), len(rows))


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def flag(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def modification_sequence(value: object) -> int:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return 0
    digits = ""
    for char in reversed(text):
        if char.isdigit():
            digits = char + digits
        elif digits:
            break
    if digits:
        return int(digits)
    return int(number(text))


def format_float(value: float) -> str:
    return f"{value:.4f}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "source",
        "snapshotStatus",
        "role",
        "groupType",
        "groupValue",
        "rows",
        "modifiedRows",
        "initialRows",
        "modifiedActionShare",
        "amount",
        "modifiedAmount",
        "amountWeightedModificationShare",
        "panelAmountShare",
        "panelModifiedAmountShare",
        "knownPiidShare",
        "knownUeiShare",
        "knownCompetitionShare",
        "singleKnownOfferRows",
        "priceOnlyRows",
        "exclusionRows",
        "protestRows",
        "claimBoundary",
        "statusNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    by_source = {
        row["source"]: row
        for row in rows
        if row["groupType"] == "source"
    }
    primary = by_source.get("usaspending-procurement-actions", {})
    sam = by_source.get("sam-contract-awards", {})
    top_agency = max(
        (row for row in rows if row["groupType"] == "agency"),
        key=lambda row: number(row["modifiedAmount"]),
        default={},
    )
    top_award_type = max(
        (row for row in rows if row["groupType"] == "awardType"),
        key=lambda row: number(row["modifiedAmount"]),
        default={},
    )
    lines = [
        "# Procurement Modification Composition Audit",
        "",
        (
            "This audit decomposes the procurement modification source moment by source route, "
            "agency, award type, and recipient concentration. It is designed to keep the "
            "bounded USAspending action panel separate from any future representative SAM/FPDS "
            "action-history denominator."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            f"The active USAspending action panel has {primary.get('rows', '0')} rows, "
            f"a modified-action share of {primary.get('modifiedActionShare', '0.0000')}, "
            f"and an amount-weighted modification share of {primary.get('amountWeightedModificationShare', '0.0000')}. "
            f"The largest modified-amount agency group is `{top_agency.get('groupValue', 'none')}` "
            f"with {top_agency.get('panelModifiedAmountShare', '0.0000')} of modified amount; "
            f"the largest modified-amount award-type group is `{top_award_type.get('groupValue', 'none')}` "
            f"with {top_award_type.get('panelModifiedAmountShare', '0.0000')} of modified amount. "
            f"SAM.gov Contract Awards has {sam.get('rows', '0')} committed rows. This composition audit "
            "does not clear the procurement-modification source gap; it explains why the current "
            "modified-action share remains a bounded sample diagnostic rather than a representative "
            "SAM/FPDS modification-incidence estimate."
        ),
        "",
        "## Source Route Summary",
        "",
        "| Source | Rows | Modified rows | Modified share | Amount-weighted modified share | PIID | UEI | Competition known | Boundary |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in [item for item in rows if item["groupType"] == "source"]:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {source} | {rows} | {modifiedRows} | {modifiedActionShare} | "
            "{amountWeightedModificationShare} | {knownPiidShare} | {knownUeiShare} | "
            "{knownCompetitionShare} | {claimBoundary} |".format(**escaped)
        )
    lines.extend(
        [
            "",
            "## Composition Groups",
            "",
            "| Group type | Group | Rows | Modified rows | Modified share | Modified amount share | Amount-weighted modified share |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    group_rows = [
        row for row in rows
        if row["groupType"] in {"agency", "awardType", "recipient"}
    ]
    for row in group_rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {groupType} | {groupValue} | {rows} | {modifiedRows} | "
            "{modifiedActionShare} | {panelModifiedAmountShare} | "
            "{amountWeightedModificationShare} |".format(**escaped)
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
