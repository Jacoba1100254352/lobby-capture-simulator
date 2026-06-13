#!/usr/bin/env python3
"""Audit procurement action denominators used by source-moment validation.

This report keeps the procurement-modification bridge explicit. The source
moments can report a modification share, but reviewers also need to see the
denominator, source route, agency breadth, and why the panel is still bounded
rather than calibration-grade.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


REPORTS = Path("reports")
SNAPSHOT = Path("data/snapshots/2024-env")
NORMALIZED = SNAPSHOT / "normalized"
LIVE_STATUS = SNAPSHOT / "live-run-status.csv"

SAM_REPRESENTATIVE_THRESHOLDS = {
    "rows": 5000,
    "distinctAwardCount": 1000,
    "agencyCount": 6,
    "dateSpanDays": 270,
    "knownPiidShare": 0.95,
    "actionDateShare": 0.80,
}

SAM_REPRESENTATIVE_WARNINGS = {
    "knownUeiShare": 0.50,
    "knownCompetitionShare": 0.25,
}

ACTION_HISTORY_DATE_SPAN_SOURCES = {
    "usaspending-procurement-actions",
    "usaspending-procurement-national-actions",
    "usaspending-procurement-bulk-summary",
    "sam-contract-awards",
}


SOURCES = [
    {
        "source": "usaspending-procurement-actions",
        "path": NORMALIZED / "usaspending-procurement-actions.csv",
        "role": "primary action denominator",
        "claimBoundary": "bounded transaction/action diagnostics; not representative SAM/FPDS calibration",
    },
    {
        "source": "usaspending-procurement-national-actions",
        "path": NORMALIZED / "usaspending-procurement-national-actions.csv",
        "role": "national-volume concentration denominator",
        "claimBoundary": "national USAspending action concentration diagnostic; not a modification-incidence denominator",
    },
    {
        "source": "usaspending-procurement-bulk-summary",
        "path": NORMALIZED / "usaspending-procurement-bulk-summary.json",
        "role": "archived public transaction-history summary",
        "claimBoundary": "representative public USAspending transaction summary for configured agencies; raw CSV/ZIP archive required for full reproduction",
    },
    {
        "source": "sam-contract-awards",
        "path": NORMALIZED / "sam-contract-awards.csv",
        "role": "optional SAM/FPDS-style action route",
        "claimBoundary": "stronger source route only if active rows are archived in the frozen snapshot",
    },
    {
        "source": "usaspending-procurement-bridge",
        "path": NORMALIZED / "usaspending-procurement-bridge.csv",
        "role": "multi-agency top-award bridge",
        "claimBoundary": "concentration and competition diagnostic; not an action-history denominator",
    },
    {
        "source": "usaspending-awards",
        "statusKey": "usaspending",
        "path": NORMALIZED / "usaspending-awards.csv",
        "role": "EPA award-level surface",
        "claimBoundary": "award identifier and competition surface; not an action-history denominator",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args()

    normalized = args.snapshot / "normalized"
    statuses = read_live_status(args.snapshot / LIVE_STATUS.name)
    rows = [
        audit_source(
            {
                **source,
                "path": normalized / source["path"].name,
            },
            statuses,
        )
        for source in SOURCES
    ]
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "procurement-denominator-audit.csv", rows)
    write_markdown(args.reports / "procurement-denominator-audit.md", rows)
    print(f"Wrote {args.reports / 'procurement-denominator-audit.csv'}")
    print(f"Wrote {args.reports / 'procurement-denominator-audit.md'}")
    return 0


def read_live_status(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {row.get("source", ""): row for row in csv.DictReader(source)}


def audit_source(source: dict[str, object], statuses: dict[str, dict[str, str]]) -> dict[str, str]:
    path = source["path"]
    assert isinstance(path, Path)
    source_name = str(source["source"])
    if path.suffix == ".json":
        return audit_summary_source(source, statuses)
    rows = read_rows(path)
    agency_amount = grouped_amount(rows, "agency")
    recipient_amount = grouped_amount(rows, "recipient")
    agency_count = grouped_count(rows, "agency")
    recipient_count = grouped_count(rows, "recipient")
    modified_rows = [row for row in rows if is_modified(row)]
    initial_rows = [row for row in rows if not is_modified(row)]
    award_groups = grouped_awards(rows)
    modified_awards = [
        group
        for group in award_groups.values()
        if any(is_modified(row) for row in group)
    ]
    dates = [parsed for parsed in (parse_date(row.get("actionDate", "")) for row in rows) if parsed]
    amount_total = sum(number(row.get("amount")) for row in rows)
    amount_modified = sum(number(row.get("amount")) for row in modified_rows)
    agencies = {row.get("agency", "").strip() for row in rows if row.get("agency", "").strip()}
    recipients = {row.get("recipient", "").strip() for row in rows if row.get("recipient", "").strip()}
    status = statuses.get(str(source.get("statusKey", source["source"])), {})
    readiness = sam_representative_readiness(source_name, {
        "rows": len(rows),
        "agencyCount": len(agencies),
        "distinctAwardCount": len(award_groups),
        "dateSpanDays": (max(dates) - min(dates)).days if len(dates) >= 2 else 0,
        "knownPiidShare": share_with_value(rows, "piid"),
        "knownUeiShare": share_with_value(rows, "uei"),
        "actionDateShare": share_with_value(rows, "actionDate"),
        "knownCompetitionShare": known_competition_share(rows),
    })
    return {
        "source": source_name,
        "snapshotStatus": status.get("status", "missing" if not rows else "unknown"),
        "role": str(source["role"]),
        "rows": str(len(rows)),
        "agencyCount": str(len(agencies)),
        "recipientCount": str(len(recipients)),
        "knownPiidShare": format_float(share_with_value(rows, "piid")),
        "knownUeiShare": format_float(share_with_value(rows, "uei")),
        "actionDateShare": format_float(share_with_value(rows, "actionDate")),
        "knownCompetitionShare": format_float(known_competition_share(rows)),
        "dateFrom": min(dates).date().isoformat() if dates else "",
        "dateTo": max(dates).date().isoformat() if dates else "",
        "dateSpanDays": str((max(dates) - min(dates)).days if len(dates) >= 2 else 0),
        "dateSpanDisplay": date_span_display(source_name, dates),
        "initialActionShare": format_float(safe_divide(len(initial_rows), len(rows))),
        "modifiedActionShare": format_float(safe_divide(len(modified_rows), len(rows))),
        "distinctAwardCount": str(len(award_groups)),
        "modifiedAwardCount": str(len(modified_awards)),
        "modifiedAwardShare": format_float(safe_divide(len(modified_awards), len(award_groups))),
        "modificationRowsPerModifiedAward": format_float(safe_divide(len(modified_rows), len(modified_awards))),
        "amountWeightedModificationShare": format_float(safe_divide(amount_modified, amount_total)),
        "topAgencyAmountShare": format_float(top_share(agency_amount, 1)),
        "topAgencyRowShare": format_float(top_share(agency_count, 1)),
        "topAgencyAmountRowGap": format_float(top_share(agency_amount, 1) - top_share(agency_count, 1)),
        "topRecipientAmountShare": format_float(top_share(recipient_amount, 1)),
        "topRecipientRowShare": format_float(top_share(recipient_count, 1)),
        "promotionReadiness": readiness,
        "claimBoundary": str(source["claimBoundary"]),
        "statusNote": status.get("notes", ""),
    }


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def audit_summary_source(source: dict[str, object], statuses: dict[str, dict[str, str]]) -> dict[str, str]:
    path = source["path"]
    assert isinstance(path, Path)
    source_name = str(source["source"])
    summary = read_json(path)
    rows = int(number(summary.get("downloadedNormalizedRows")))
    status = statuses.get(str(source.get("statusKey", source["source"])), {})
    readiness = bulk_representative_readiness(summary)
    date_span_days = int(number(summary.get("dateSpanDays")))
    return {
        "source": source_name,
        "snapshotStatus": status.get("status", "missing" if rows <= 0 else "copied"),
        "role": str(source["role"]),
        "rows": str(rows),
        "agencyCount": str(int(number(summary.get("agencyCount")))),
        "recipientCount": str(int(number(summary.get("recipientCount")))),
        "knownPiidShare": format_float(number(summary.get("knownPiidShare"))),
        "knownUeiShare": format_float(number(summary.get("knownUeiShare"))),
        "actionDateShare": format_float(number(summary.get("actionDateShare"))),
        "knownCompetitionShare": format_float(number(summary.get("knownCompetitionShare"))),
        "dateFrom": str(summary.get("dateFrom", "")),
        "dateTo": str(summary.get("dateTo", "")),
        "dateSpanDays": str(date_span_days),
        "dateSpanDisplay": f"{date_span_days}d" if rows else "0d",
        "initialActionShare": format_float(number(summary.get("initialActionShare"))),
        "modifiedActionShare": format_float(number(summary.get("modifiedActionShare"))),
        "distinctAwardCount": str(int(number(summary.get("distinctAwardCount")))),
        "modifiedAwardCount": str(int(number(summary.get("modifiedAwardCount")))),
        "modifiedAwardShare": format_float(number(summary.get("modifiedAwardShare"))),
        "modificationRowsPerModifiedAward": format_float(number(summary.get("modificationRowsPerModifiedAward"))),
        "amountWeightedModificationShare": format_float(number(summary.get("amountWeightedModificationShare"))),
        "topAgencyAmountShare": format_float(number(summary.get("topAgencyAmountShare"))),
        "topAgencyRowShare": format_float(number(summary.get("topAgencyRowShare"))),
        "topAgencyAmountRowGap": format_float(number(summary.get("topAgencyAmountShare")) - number(summary.get("topAgencyRowShare"))),
        "topRecipientAmountShare": format_float(number(summary.get("topRecipientAmountShare"))),
        "topRecipientRowShare": format_float(number(summary.get("topRecipientRowShare"))),
        "promotionReadiness": readiness,
        "claimBoundary": str(source["claimBoundary"]),
        "statusNote": status.get("notes", str(summary.get("normalizedOutputSha256", ""))),
    }


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def is_modified(row: dict[str, str]) -> bool:
    return flag(row.get("exPostModification")) or modification_sequence(row.get("modificationNumber")) > 0


def grouped_awards(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[procurement_award_key(row)].append(row)
    return dict(grouped)


def procurement_award_key(row: dict[str, str]) -> str:
    for key in ("piid", "awardId"):
        value = row.get(key, "").strip()
        if value:
            return value
    return "|".join(
        [
            row.get("recipient", "").strip(),
            row.get("agency", "").strip(),
            row.get("actionDate", "").strip(),
        ]
    )


def grouped_amount(rows: list[dict[str, str]], key: str) -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row.get(key, "") or "unknown"] += number(row.get("amount"))
    return dict(grouped)


def grouped_count(rows: list[dict[str, str]], key: str) -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row.get(key, "") or "unknown"] += 1.0
    return dict(grouped)


def top_share(amounts: dict[str, float], count: int) -> float:
    total = sum(amounts.values())
    if total <= 0.0:
        return 0.0
    return sum(sorted(amounts.values(), reverse=True)[:count]) / total


def share_with_value(rows: list[dict[str, str]], key: str) -> float:
    return safe_divide(sum(1 for row in rows if row.get(key, "").strip()), len(rows))


def known_competition_share(rows: list[dict[str, str]]) -> float:
    unknown = {"", "unknown", "none", "null"}
    return safe_divide(
        sum(1 for row in rows if row.get("competitionType", "").strip().lower() not in unknown),
        len(rows),
    )


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


def parse_date(value: str) -> datetime | None:
    text = str(value or "").strip()
    for candidate in (text, text[:10], text[:20]):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue
    return None


def sam_representative_readiness(source: str, metrics: dict[str, float | int]) -> str:
    if source != "sam-contract-awards":
        return "not-applicable"
    blockers = [
        name for name, threshold in SAM_REPRESENTATIVE_THRESHOLDS.items()
        if float(metrics.get(name, 0.0)) < float(threshold)
    ]
    if blockers:
        return "blocked"
    warnings = [
        name for name, threshold in SAM_REPRESENTATIVE_WARNINGS.items()
        if float(metrics.get(name, 0.0)) < float(threshold)
    ]
    return "diagnostic" if warnings else "candidate"


def bulk_representative_readiness(summary: dict[str, object]) -> str:
    if not summary:
        return "not-active"
    thresholds = {
        "downloadedNormalizedRows": 500000,
        "distinctAwardCount": 100000,
        "agencyCount": 6,
        "dateSpanDays": 270,
        "knownPiidShare": 0.95,
        "actionDateShare": 0.80,
    }
    blockers = [
        name for name, threshold in thresholds.items()
        if number(summary.get(name)) < float(threshold)
    ]
    if blockers:
        return "blocked"
    warnings = [
        name for name, threshold in {
            "knownUeiShare": 0.50,
            "knownCompetitionShare": 0.10,
        }.items()
        if number(summary.get(name)) < float(threshold)
    ]
    return "diagnostic" if warnings else "candidate"


def date_span_display(source: str, dates: list[datetime]) -> str:
    if source not in ACTION_HISTORY_DATE_SPAN_SOURCES:
        return "n/a"
    if len(dates) < 2:
        return "0d"
    return f"{(max(dates) - min(dates)).days}d"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "source",
        "snapshotStatus",
        "role",
        "rows",
        "agencyCount",
        "recipientCount",
        "knownPiidShare",
        "knownUeiShare",
        "actionDateShare",
        "knownCompetitionShare",
        "dateFrom",
        "dateTo",
        "dateSpanDays",
        "dateSpanDisplay",
        "initialActionShare",
        "modifiedActionShare",
        "distinctAwardCount",
        "modifiedAwardCount",
        "modifiedAwardShare",
        "modificationRowsPerModifiedAward",
        "amountWeightedModificationShare",
        "topAgencyAmountShare",
        "topAgencyRowShare",
        "topAgencyAmountRowGap",
        "topRecipientAmountShare",
        "topRecipientRowShare",
        "promotionReadiness",
        "claimBoundary",
        "statusNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    primary = next(
        (row for row in rows if row["source"] == "usaspending-procurement-actions"),
        {},
    )
    bulk = next(
        (row for row in rows if row["source"] == "usaspending-procurement-bulk-summary"),
        {},
    )
    national = next(
        (row for row in rows if row["source"] == "usaspending-procurement-national-actions"),
        {},
    )
    sam = next((row for row in rows if row["source"] == "sam-contract-awards"), {})
    lines = [
        "# Procurement Denominator Audit",
        "",
        (
            "This audit explains the denominator behind procurement modification and concentration "
            "moments. It separates the active USAspending action panel from the optional SAM.gov "
            "Contract Awards route and from award-level bridge rows. The SAM.gov route supports "
            "synchronous non-adjacent offset page-index strata through "
            "`SAM_CONTRACT_AWARDS_OFFSET_STARTS` and asynchronous extract downloads through "
            "`SAM_CONTRACT_AWARDS_EXTRACT_MODE`; those rows strengthen the snapshot only "
            "when the resulting action-history panel is archived."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            f"The modification denominator is `{primary.get('source', 'none')}` with "
            f"{primary.get('rows', '0')} rows across {primary.get('agencyCount', '0')} agencies. "
            f"Its modified-action share is {primary.get('modifiedActionShare', '0.0000')}; "
            f"{primary.get('modifiedAwardCount', '0')} of {primary.get('distinctAwardCount', '0')} "
            f"distinct PIID/award identifiers have at least one modification "
            f"({primary.get('modifiedAwardShare', '0.0000')}), with "
            f"{primary.get('modificationRowsPerModifiedAward', '0.0000')} modified rows per modified award. "
            f"The national concentration panel is `{national.get('source', 'none')}` with "
            f"{national.get('rows', '0')} rows across {national.get('agencyCount', '0')} agencies. "
            f"In that panel, the largest agency accounts for {national.get('topAgencyRowShare', '0.0000')} "
            f"of rows but {national.get('topAgencyAmountShare', '0.0000')} of amount, and the largest "
            f"recipient accounts for {national.get('topRecipientAmountShare', '0.0000')} of amount. "
            f"SAM.gov Contract Awards status is `{sam.get('snapshotStatus', 'missing')}` with "
            f"{sam.get('rows', '0')} committed rows and promotion readiness "
            f"`{sam.get('promotionReadiness', 'blocked')}`. The USAspending bulk summary has "
            f"{bulk.get('rows', '0')} summarized rows and promotion readiness "
            f"`{bulk.get('promotionReadiness', 'not-active')}`. The procurement-modification claim remains "
            "bounded until a representative action-history denominator is archived and its metric mapping is validated; "
            "the national panel improves concentration diagnostics but is not used as a representative "
            "modification-incidence denominator."
        ),
        "",
        "| Source | Status | Role | Rows | Agencies | Awards | Dates | PIID | UEI | Competition | Modified actions | Modified award share | Amt-wtd mod. | Promotion | Boundary |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {snapshotStatus} | {role} | {rows} | {agencyCount} | "
            "{distinctAwardCount} | {dateSpanDisplay} | {knownPiidShare} | {knownUeiShare} | "
            "{knownCompetitionShare} | {modifiedActionShare} | {modifiedAwardShare} | "
            "{amountWeightedModificationShare} | {promotionReadiness} | {claimBoundary} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
