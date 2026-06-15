#!/usr/bin/env python3
"""Screen a downloaded SAM.gov Contract Awards export before snapshot promotion.

This is an operational guardrail for the remaining procurement source gap. It
normalizes a candidate export through the same parser used by the live snapshot
runner, then reports whether the panel looks broad enough to promote as a
representative SAM/FPDS action-history denominator. It does not write raw
payloads or alter the frozen paper snapshot.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import importlib.util
import os
from pathlib import Path
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
FETCHER = ROOT / "scripts" / "fetch-source-data.py"
REPORTS = ROOT / "reports"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=env_path("SAM_CONTRACT_AWARDS_LIVE_CSV"))
    parser.add_argument("--url", default=os.environ.get("SAM_CONTRACT_AWARDS_LIVE_URL", "").strip())
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--min-rows", type=int, default=int_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_ROWS", 5000))
    parser.add_argument("--min-awards", type=int, default=int_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_AWARDS", 1000))
    parser.add_argument("--min-agencies", type=int, default=int_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_AGENCIES", 6))
    parser.add_argument("--min-date-span-days", type=int, default=int_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_DATE_SPAN_DAYS", 270))
    parser.add_argument("--min-piid-share", type=float, default=float_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_PIID_SHARE", 0.95))
    parser.add_argument("--min-uei-share", type=float, default=float_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_UEI_SHARE", 0.50))
    parser.add_argument("--min-action-date-share", type=float, default=float_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_ACTION_DATE_SHARE", 0.80))
    parser.add_argument("--min-competition-share", type=float, default=float_env("SAM_CONTRACT_AWARDS_EXPORT_MIN_COMPETITION_SHARE", 0.25))
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="lobby-sam-export-audit-") as tmp:
        input_path = resolved_input(args, Path(tmp))
        fetcher = load_fetcher()
        raw_records = fetcher.sam_contract_awards_records_from_export_file(input_path)
        normalized_rows = fetcher.dedupe_usaspending_action_rows(
            fetcher.normalize_sam_contract_award_records(
                raw_records
            )
        )

    metrics = export_metrics(normalized_rows)
    metrics.update(raw_field_metrics(fetcher, raw_records))
    rows = checklist_rows(args, metrics)
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "sam-contract-awards-export-audit.csv", rows)
    write_markdown(args.reports / "sam-contract-awards-export-audit.md", rows, metrics, args)
    print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.csv'}")
    print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.md'}")
    return 0 if rows[0]["status"] in {"candidate", "diagnostic"} else 1


def resolved_input(args: argparse.Namespace, tmp: Path) -> Path:
    if args.input:
        return args.input
    if not args.url:
        raise SystemExit(
            "Set SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL or pass --input/--url."
        )
    target = tmp / "sam-contract-awards-export"
    with urlopen(args.url, timeout=60) as response:
        target.write_bytes(response.read())
    return target


def load_fetcher():
    spec = importlib.util.spec_from_file_location("fetch_source_data", FETCHER)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Unable to load {FETCHER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export_metrics(rows: list[dict[str, object]]) -> dict[str, object]:
    agencies = values(rows, "agency")
    recipients = values(rows, "recipient")
    awards = {award_key(row) for row in rows if award_key(row)}
    dates = [parsed for parsed in (parse_date(str(row.get("actionDate", ""))) for row in rows) if parsed]
    modified_rows = [row for row in rows if is_modified(row)]
    modified_awards = {award_key(row) for row in modified_rows if award_key(row)}
    amount_total = sum(number(row.get("amount")) for row in rows)
    amount_modified = sum(number(row.get("amount")) for row in modified_rows)
    return {
        "rows": len(rows),
        "agencyCount": len(agencies),
        "recipientCount": len(recipients),
        "distinctAwardCount": len(awards),
        "knownPiidShare": share_with_value(rows, "piid"),
        "knownUeiShare": share_with_value(rows, "uei"),
        "actionDateShare": share_with_value(rows, "actionDate"),
        "knownCompetitionShare": known_competition_share(rows),
        "knownOfferShare": known_offer_share(rows),
        "modifiedActionShare": safe_divide(len(modified_rows), len(rows)),
        "modifiedAwardShare": safe_divide(len(modified_awards), len(awards)),
        "amountWeightedModificationShare": safe_divide(amount_modified, amount_total),
        "topAgencyRowShare": top_group_share(rows, "agency", amount_weighted=False),
        "topAgencyAmountShare": top_group_share(rows, "agency", amount_weighted=True),
        "topRecipientAmountShare": top_group_share(rows, "recipient", amount_weighted=True),
        "dateFrom": min(dates).date().isoformat() if dates else "",
        "dateTo": max(dates).date().isoformat() if dates else "",
        "dateSpanDays": (max(dates) - min(dates)).days if len(dates) >= 2 else 0,
    }


def checklist_rows(args: argparse.Namespace, metrics: dict[str, object]) -> list[dict[str, str]]:
    checks = [
        hard_check("row-count", metrics["rows"], args.min_rows, ">=", "rows available for denominator stability"),
        hard_check("distinct-awards", metrics["distinctAwardCount"], args.min_awards, ">=", "distinct PIID/award identifiers"),
        hard_check("agency-breadth", metrics["agencyCount"], args.min_agencies, ">=", "multi-agency breadth for representative action histories"),
        hard_check("date-span", metrics["dateSpanDays"], args.min_date_span_days, ">=", "coverage across most of the fiscal year"),
        hard_check("piid-coverage", metrics["knownPiidShare"], args.min_piid_share, ">=", "PIID coverage for action-history grouping"),
        hard_check("action-date-coverage", metrics["actionDateShare"], args.min_action_date_share, ">=", "action-date coverage for time-window validation"),
        soft_check("uei-coverage", metrics["knownUeiShare"], args.min_uei_share, ">=", "UEI coverage for recipient matching"),
        soft_check("competition-coverage", metrics["knownCompetitionShare"], args.min_competition_share, ">=", "competition fields for procurement-firewall diagnostics"),
        metric_row("modified-action-share", metrics["modifiedActionShare"], "diagnostic", "not a pass/fail threshold; compare to source-moment benchmark"),
        metric_row("modified-award-share", metrics["modifiedAwardShare"], "diagnostic", "distinct-award modification denominator"),
        metric_row("amount-weighted-modification-share", metrics["amountWeightedModificationShare"], "diagnostic", "amount-weighted modification denominator"),
        metric_row("top-agency-row-share", metrics["topAgencyRowShare"], "diagnostic", "concentration diagnostic"),
        metric_row("top-agency-amount-share", metrics["topAgencyAmountShare"], "diagnostic", "concentration diagnostic"),
        metric_row("top-recipient-amount-share", metrics["topRecipientAmountShare"], "diagnostic", "concentration diagnostic"),
        metric_row(
            "raw-action-date-candidate-share",
            metrics["rawActionDateCandidateShare"],
            "diagnostic",
            "raw export coverage for fields mapped to actionDate",
        ),
        metric_row(
            "raw-solicitation-date-share",
            metrics["rawSolicitationDateShare"],
            "diagnostic",
            "raw export coverage for solicitationDate; not an action-date substitute",
        ),
        metric_row(
            "raw-amount-field-share",
            metrics["rawAmountFieldShare"],
            "diagnostic",
            "raw export coverage for fields mapped to amount",
        ),
    ]
    blockers = [row for row in checks if row["status"] == "blocked"]
    warnings = [row for row in checks if row["status"] == "warning"]
    if blockers:
        summary_status = "blocked"
        next_action = "Do not promote this export into the frozen snapshot; broaden the SAM/FPDS action-history export and rerun this audit."
    elif warnings:
        summary_status = "diagnostic"
        next_action = "The export clears hard breadth checks but has coverage warnings; inspect diagnostics before promotion."
    else:
        summary_status = "candidate"
        next_action = "Candidate export can be promoted through scripts/run-2024-env-live-snapshot.sh, followed by paper-artifacts-check."
    summary = {
        "item": "promotion-readiness",
        "status": summary_status,
        "value": f"blockers={len(blockers)}; warnings={len(warnings)}",
        "threshold": "no hard blockers",
        "notes": "Operational screen only; final claim clearance still requires snapshot regeneration and validation.",
        "nextAction": next_action,
    }
    return [summary] + checks


def raw_field_metrics(fetcher, records: list[dict[str, object]]) -> dict[str, object]:
    action_paths = (
        "awardDetails.transactionData.approvedDate",
        "coreData.dateSigned",
        "dateSigned",
        "Date Signed",
        "Award Date",
        "Last Modified Date",
        "approvedDate",
        "Approved Date",
        "actionDate",
    )
    amount_paths = (
        "awardDetails.dollars.actionObligation",
        "awardDetails.dollars.dollarsObligated",
        "awardDetails.dollars.baseAndAllOptionsValue",
        "awardDetails.dollars.currentTotalValueOfAward",
        "awardDetails.totalContractDollars.totalActionObligation",
        "dollarsObligated",
        "actionObligation",
        "Action Obligation",
        "Federal Action Obligation",
        "Total Action Obligation",
        "Dollars Obligated",
        "Current Total Value of Award",
        "totalDollarsObligated",
    )
    return {
        "rawRecordCount": len(records),
        "rawActionDateCandidateShare": raw_path_share(fetcher, records, action_paths),
        "rawSolicitationDateShare": raw_path_share(fetcher, records, ("coreData.solicitationDate", "solicitationDate")),
        "rawAmountFieldShare": raw_path_share(fetcher, records, amount_paths),
    }


def raw_path_share(fetcher, records: list[dict[str, object]], paths: tuple[str, ...]) -> float:
    matched = sum(1 for record in records if fetcher.first_text(record, *paths, default=""))
    return safe_divide(matched, len(records))


def hard_check(item: str, value: object, threshold: object, op: str, notes: str) -> dict[str, str]:
    passed = compare(value, threshold, op)
    return {
        "item": item,
        "status": "ready" if passed else "blocked",
        "value": format_value(value),
        "threshold": f"{op} {format_value(threshold)}",
        "notes": notes,
        "nextAction": "ok" if passed else "broaden the export before snapshot promotion",
    }


def soft_check(item: str, value: object, threshold: object, op: str, notes: str) -> dict[str, str]:
    passed = compare(value, threshold, op)
    return {
        "item": item,
        "status": "ready" if passed else "warning",
        "value": format_value(value),
        "threshold": f"{op} {format_value(threshold)}",
        "notes": notes,
        "nextAction": "ok" if passed else "inspect before promotion; not a hard blocker by itself",
    }


def metric_row(item: str, value: object, status: str, notes: str) -> dict[str, str]:
    return {
        "item": item,
        "status": status,
        "value": format_value(value),
        "threshold": "reported",
        "notes": notes,
        "nextAction": "compare against source moments and denominator audit after snapshot promotion",
    }


def compare(value: object, threshold: object, op: str) -> bool:
    if op == ">=":
        return float(value) >= float(threshold)
    raise AssertionError(op)


def values(rows: list[dict[str, object]], key: str) -> set[str]:
    return {str(row.get(key, "")).strip() for row in rows if str(row.get(key, "")).strip()}


def award_key(row: dict[str, object]) -> str:
    for key in ("piid", "awardId"):
        value = str(row.get(key, "")).strip()
        if value:
            return value
    return ""


def is_modified(row: dict[str, object]) -> bool:
    return str(row.get("exPostModification", "")).lower() == "true" or modification_sequence(row.get("modificationNumber")) > 0


def modification_sequence(value: object) -> int:
    text = str(value or "").strip()
    if not text or text.lower() in {"0", "0.0", "none", "null", "nan"}:
        return 0
    digits = ""
    for char in reversed(text):
        if char.isdigit():
            digits = char + digits
        elif digits:
            break
    return int(digits) if digits else 0


def number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def share_with_value(rows: list[dict[str, object]], key: str) -> float:
    return safe_divide(sum(1 for row in rows if str(row.get(key, "")).strip()), len(rows))


def known_competition_share(rows: list[dict[str, object]]) -> float:
    unknown = {"", "unknown", "none", "null"}
    return safe_divide(
        sum(1 for row in rows if str(row.get("competitionType", "")).strip().lower() not in unknown),
        len(rows),
    )


def known_offer_share(rows: list[dict[str, object]]) -> float:
    return safe_divide(sum(1 for row in rows if number(row.get("numberOfOffers")) > 0), len(rows))


def top_group_share(rows: list[dict[str, object]], key: str, *, amount_weighted: bool) -> float:
    grouped: dict[str, float] = {}
    for row in rows:
        group = str(row.get(key, "")).strip() or "unknown"
        grouped[group] = grouped.get(group, 0.0) + (number(row.get("amount")) if amount_weighted else 1.0)
    total = sum(grouped.values())
    if total <= 0.0:
        return 0.0
    return max(grouped.values(), default=0.0) / total


def parse_date(value: str) -> datetime | None:
    text = value.strip()
    for candidate in (text, text[:10], text[:20]):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue
    return None


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def float_env(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


def env_path(name: str) -> Path | None:
    value = os.environ.get(name, "").strip()
    return Path(value) if value else None


def format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def redact_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, "REDACTED") if "key" in key.lower() else (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["item", "status", "value", "threshold", "notes", "nextAction"]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], metrics: dict[str, object], args: argparse.Namespace) -> None:
    source = str(args.input) if args.input else redact_url(args.url)
    lines = [
        "# SAM Contract Awards Export Audit",
        "",
        (
            "This operational audit screens a downloaded SAM.gov Contract Awards export before "
            "it is promoted into the frozen paper snapshot. It does not clear any claim by "
            "itself; claim clearance still requires snapshot regeneration, validation, and the "
            "paper artifact gate."
        ),
        "",
        f"- Source: `{source}`",
        f"- Rows: `{metrics['rows']}`",
        f"- Agencies: `{metrics['agencyCount']}`",
        f"- Distinct PIID/award identifiers: `{metrics['distinctAwardCount']}`",
        f"- Date span: `{metrics['dateFrom']}` to `{metrics['dateTo']}` ({metrics['dateSpanDays']} days)",
        f"- Modified action share: `{format_value(metrics['modifiedActionShare'])}`",
        f"- Modified award share: `{format_value(metrics['modifiedAwardShare'])}`",
        f"- Amount-weighted modification share: `{format_value(metrics['amountWeightedModificationShare'])}`",
        "",
        "## Export Shape Diagnostics",
        "",
        f"- Raw award records parsed: `{metrics['rawRecordCount']}`",
        f"- Raw action-date candidate coverage: `{format_value(metrics['rawActionDateCandidateShare'])}`",
        f"- Raw solicitation-date coverage: `{format_value(metrics['rawSolicitationDateShare'])}`",
        f"- Raw amount-field coverage: `{format_value(metrics['rawAmountFieldShare'])}`",
        (
            "- Interpretation: solicitation dates can explain why a SAM export looks time-bounded, "
            "but they are not action dates and cannot clear the action-history date gate."
        ),
        "",
        "## Promotion Checklist",
        "",
        "| Item | Status | Value | Threshold | Notes | Next action |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {item} | {status} | {value} | {threshold} | {notes} | {nextAction} |".format(**escaped)
        )
    lines.extend(
        [
            "",
            "## Promotion Command",
            "",
            "If the export is a candidate, promote it with:",
            "",
            "```sh",
            "SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/export.csv ./scripts/run-2024-env-live-snapshot.sh",
            "make snapshot-2024-env source-moments validate calibration-queue procurement-refresh-readiness paper-artifacts-check",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
