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
from datetime import datetime, timedelta, timezone
import importlib.util
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
FETCHER = ROOT / "scripts" / "fetch-source-data.py"
REPORTS = ROOT / "reports"
DEFAULT_REPRESENTATIVE_AGENCIES = [
    "Environmental Protection Agency",
    "Department of Energy",
    "Department of the Interior",
    "Department of Agriculture",
    "Department of Transportation",
    "Department of Defense",
    "Department of Health and Human Services",
    "Department of Veterans Affairs",
    "Department of Homeland Security",
    "National Aeronautics and Space Administration",
    "General Services Administration",
    "Department of Commerce",
]
REQUIRED_ACTION_HISTORY_FIELDS = [
    "PIID or award identifier",
    "UEI or recipient identifier",
    "awarding agency and subtier",
    "recipient name",
    "action or signed date",
    "obligation or action amount",
    "modification number",
    "competition or extent-competed code",
    "number of offers when available",
]
NEXT_ACCESS_RE = re.compile(r'"nextAccessTime"\s*:\s*"([^"]+)"')
HTTP_STATUS_RE = re.compile(r"HTTP\s+(\d{3})")


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

    freshness = sam_export_url_freshness() if args.url and not args.input else {"status": "not_applicable", "evidence": ""}
    if freshness["status"] == "expired":
        rows = expired_export_url_rows(freshness)
        args.reports.mkdir(parents=True, exist_ok=True)
        write_csv(args.reports / "sam-contract-awards-export-audit.csv", rows)
        write_expired_url_markdown(args.reports / "sam-contract-awards-export-audit.md", rows, args, freshness)
        print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.csv'}")
        print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.md'}")
        return 1

    try:
        with tempfile.TemporaryDirectory(prefix="lobby-sam-export-audit-") as tmp:
            fetcher = load_fetcher()
            input_path = resolved_input(args, Path(tmp), fetcher)
            raw_records = fetcher.sam_contract_awards_records_from_export_file(input_path)
            normalized_rows = fetcher.dedupe_usaspending_action_rows(
                fetcher.normalize_sam_contract_award_records(
                    raw_records
                )
            )
    except SystemExit as error:
        if not args.url or args.input:
            raise
        message = str(error)
        rows = download_failure_rows(message, freshness)
        args.reports.mkdir(parents=True, exist_ok=True)
        write_csv(args.reports / "sam-contract-awards-export-audit.csv", rows)
        write_download_failure_markdown(args.reports / "sam-contract-awards-export-audit.md", rows, args, message, freshness)
        print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.csv'}")
        print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.md'}")
        return 1

    metrics = export_metrics(normalized_rows)
    metrics.update(raw_field_metrics(fetcher, raw_records))
    rows = checklist_rows(args, metrics)
    if args.url and not args.input:
        rows.insert(1, export_link_freshness_row(freshness))
    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "sam-contract-awards-export-audit.csv", rows)
    write_markdown(args.reports / "sam-contract-awards-export-audit.md", rows, metrics, args)
    print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.csv'}")
    print(f"Wrote {args.reports / 'sam-contract-awards-export-audit.md'}")
    return 0 if rows[0]["status"] in {"candidate", "diagnostic"} else 1


def resolved_input(args: argparse.Namespace, tmp: Path, fetcher) -> Path:
    if args.input:
        return args.input
    if not args.url:
        raise SystemExit(
            "Set SAM_CONTRACT_AWARDS_LIVE_CSV/SAM_CONTRACT_AWARDS_LIVE_URL or pass --input/--url."
        )
    target = tmp / "sam-contract-awards-export"
    return fetcher.download_sam_contract_awards_export_url(args.url, target)


def download_failure_rows(message: str, freshness: dict[str, str]) -> list[dict[str, str]]:
    status, reason = classify_download_failure(message)
    http_status = first_match(HTTP_STATUS_RE, message)
    next_access = first_match(NEXT_ACCESS_RE, message)
    retry_window_missed = quota_reset_after_link_expiry(next_access, freshness)
    rows = [
        {
            "item": "promotion-readiness",
            "status": status,
            "value": reason,
            "threshold": "downloadable export URL",
            "notes": "No SAM/FPDS rows were promoted into the frozen snapshot.",
            "nextAction": download_failure_next_action(status, next_access, retry_window_missed),
        },
        export_link_freshness_row(freshness),
        {
            "item": "download-status",
            "status": status,
            "value": f"HTTP {http_status}" if http_status else "request failed",
            "threshold": "HTTP 200 with CSV, JSON, or ZIP payload",
            "notes": "The emailed async-export URL must be reachable before export-shape checks can run.",
            "nextAction": (
                "Request a fresh export after the upstream reset because this emailed token expires first."
                if retry_window_missed
                else "Retry the emailed URL after the upstream reset or request a fresh export."
            ),
        },
    ]
    if next_access:
        rows.append(
            {
                "item": "next-access-time",
                "status": "manual_required",
                "value": next_access,
                "threshold": "current time after SAM reset",
                "notes": "SAM.gov returned this quota reset time.",
                "nextAction": (
                    f"Wait until {next_access}, then request a fresh SAM.gov export email."
                    if retry_window_missed
                    else f"Retry after {next_access}; if the 60-minute token expired, request a new SAM export email."
                ),
            }
        )
    if retry_window_missed:
        rows.append(
            {
                "item": "export-link-retry-window",
                "status": "manual_required",
                "value": "quota reset occurs after emailed token expiry",
                "threshold": "SAM reset before expiresAt",
                "notes": freshness.get("evidence", "freshness metadata unavailable"),
                "nextAction": (
                    "After the quota reset, request a fresh SAM.gov export email, record it with "
                    "make sam-contract-awards-record-export-link, then rerun the audit."
                ),
            }
        )
    return rows


def expired_export_url_rows(freshness: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "item": "promotion-readiness",
            "status": "manual_required",
            "value": "SAM.gov emailed export URL appears expired",
            "threshold": "fresh SAM.gov download URL",
            "notes": "No SAM/FPDS rows were promoted into the frozen snapshot.",
            "nextAction": (
                "Request a fresh SAM.gov export email, record it with "
                "make sam-contract-awards-record-export-link, then rerun the audit."
            ),
        },
        export_link_freshness_row(freshness),
    ]


def export_link_freshness_row(freshness: dict[str, str]) -> dict[str, str]:
    status = freshness.get("status", "unknown")
    if status == "fresh":
        row_status = "ready"
        next_action = "Rerun this audit after recording any new emailed SAM.gov export link."
    elif status == "expired":
        row_status = "manual_required"
        next_action = "Request and record a fresh SAM.gov export link before retrying the audit."
    else:
        row_status = "manual_required"
        next_action = (
            "Record the SAM.gov export link with make sam-contract-awards-record-export-link "
            "or make sam-contract-awards-record-fresh-link so timestamp metadata is available."
        )
    return {
        "item": "export-link-freshness",
        "status": row_status,
        "value": freshness.get("evidence", ""),
        "threshold": "matches current SAM_CONTRACT_AWARDS_LIVE_URL metadata",
        "notes": "Non-secret timestamp metadata used to detect stale audits after a new emailed link is recorded.",
        "nextAction": next_action,
    }


def classify_download_failure(message: str) -> tuple[str, str]:
    lowered = message.lower()
    if (
        first_match(NEXT_ACCESS_RE, message)
        or "exceeded your quota" in lowered
        or "message throttled out" in lowered
        or '"code":"900804"' in lowered
        or '"code": "900804"' in lowered
    ):
        next_access = first_match(NEXT_ACCESS_RE, message)
        if next_access:
            return "quota_blocked", f"SAM.gov quota blocked until {next_access}"
        return "quota_blocked", "SAM.gov quota blocked; retry after the upstream reset time"
    http_status = first_match(HTTP_STATUS_RE, message)
    if http_status == "403":
        return "blocked", "SAM.gov rejected the export URL or API key"
    if http_status == "404":
        return "blocked", "SAM.gov export URL was not found or the token expired"
    if http_status:
        return "blocked", f"SAM.gov export download failed with HTTP {http_status}"
    return "blocked", "SAM.gov export download failed"


def download_failure_next_action(status: str, next_access: str, retry_window_missed: bool = False) -> str:
    if status == "quota_blocked" and retry_window_missed and next_access:
        return f"Wait until {next_access}, then request a fresh emailed export because this token expires before the quota reset."
    if status == "quota_blocked" and next_access:
        return f"Retry after {next_access}; request a fresh emailed export if this token has expired."
    if status == "quota_blocked":
        return "Retry after the SAM.gov quota reset time; request a fresh emailed export if this token has expired."
    return "Request a fresh SAM.gov Contract Awards export and rerun this audit."


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1) if match else ""


def quota_reset_after_link_expiry(next_access: str, freshness: dict[str, str]) -> bool:
    reset = parse_sam_next_access(next_access)
    expires = parse_time(freshness.get("expiresAt", ""))
    return bool(reset and expires and reset >= expires)


def parse_sam_next_access(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    if value.endswith(" UTC"):
        value = value[:-4]
    try:
        return datetime.strptime(value, "%Y-%b-%d %H:%M:%S%z").astimezone(timezone.utc)
    except ValueError:
        return None


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


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


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
            (key, "REDACTED") if sensitive_query_key(key) else (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def sensitive_query_key(key: str) -> bool:
    lowered = key.lower()
    return lowered in {"token", "access_token"} or "key" in lowered or "secret" in lowered


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
            "## Next Export Specification",
            "",
            *next_export_specification(rows, metrics, args),
            "",
            "## Promotion Command",
            "",
            "If the export is a candidate, promote it with:",
            "",
            "```sh",
            "SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/export.csv ./scripts/run-2024-env-live-snapshot.sh",
            "# or, for SAM.gov emailed async-extract links:",
            "SAM_CONTRACT_AWARDS_LIVE_URL='https://api.sam.gov/contract-awards/v1/download?api_key=REPLACE_WITH_API_KEY&token=...' ./scripts/run-2024-env-live-snapshot.sh",
            "make snapshot-2024-env source-moments validate calibration-queue procurement-refresh-readiness paper-artifacts-check",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_download_failure_markdown(
        path: Path,
        rows: list[dict[str, str]],
        args: argparse.Namespace,
        message: str,
        freshness: dict[str, str],
) -> None:
    source = redact_url(args.url)
    retry_window_missed = any(row["item"] == "export-link-retry-window" for row in rows)
    lines = [
        "# SAM Contract Awards Export Audit",
        "",
        (
            "This operational audit attempted to download a SAM.gov Contract Awards export "
            "from an emailed async-extract link before any snapshot promotion. The download "
            "did not produce a CSV, JSON, or ZIP payload, so no export-shape checks were run "
            "and no SAM/FPDS rows were promoted."
        ),
        "",
        f"- Source: `{source}`",
        f"- Download result: `{rows[0]['status']}`",
        f"- Reason: `{rows[0]['value']}`",
        f"- Link freshness at audit time: `{freshness.get('status', 'not_applicable')}`",
        f"- Freshness evidence: `{freshness.get('evidence', '')}`",
        *(
            ["- Link retry window: `missed; SAM reset occurs after the emailed token expiry`"]
            if retry_window_missed else []
        ),
        "",
        "## Download Failure Checklist",
        "",
        "| Item | Status | Value | Threshold | Notes | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {item} | {status} | {value} | {threshold} | {notes} | {nextAction} |".format(**escaped)
        )
    lines.extend(
        [
            "",
            "## Redacted Error",
            "",
            "```text",
            redact_error_message(message),
            "```",
            "",
            "## Next Action",
            "",
            (
                "After SAM.gov allows another request, request a fresh SAM.gov Contract Awards export email, "
                "record it with `make sam-contract-awards-record-export-link < sam-email.txt`, and rerun "
                "`make sam-contract-awards-export-audit`."
                if retry_window_missed
                else "After SAM.gov allows another request, rerun "
                "`SAM_CONTRACT_AWARDS_LIVE_URL='https://api.sam.gov/contract-awards/v1/download?api_key=REPLACE_WITH_API_KEY&token=...' "
                "make sam-contract-awards-export-audit`. If the emailed token has expired, request a fresh export email first."
            ),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_expired_url_markdown(
        path: Path,
        rows: list[dict[str, str]],
        args: argparse.Namespace,
        freshness: dict[str, str],
) -> None:
    source = redact_url(args.url)
    lines = [
        "# SAM Contract Awards Export Audit",
        "",
        (
            "This operational audit did not download the configured SAM.gov Contract "
            "Awards export because the local timestamp metadata says the emailed "
            "async-extract link has expired. No export-shape checks were run and no "
            "SAM/FPDS rows were promoted."
        ),
        "",
        f"- Source: `{source}`",
        f"- Link freshness: `{freshness['status']}`",
        f"- Freshness evidence: `{freshness['evidence']}`",
        "",
        "## Export Link Checklist",
        "",
        "| Item | Status | Value | Threshold | Notes | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {item} | {status} | {value} | {threshold} | {notes} | {nextAction} |".format(**escaped)
        )
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            (
                "Request a fresh SAM.gov Contract Awards export email, save the email body to "
                "`sam-email.txt`, run `make sam-contract-awards-record-export-link < sam-email.txt`, "
                "then rerun `make sam-contract-awards-export-audit` while the link is still fresh."
            ),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def redact_error_message(message: str) -> str:
    redacted = re.sub(r"(api_key=)[^&\s]+", r"\1REDACTED", message)
    redacted = re.sub(r"(token=)[^&\s]+", r"\1REDACTED", redacted)
    redacted = re.sub(r"(access_token=)[^&\s]+", r"\1REDACTED", redacted)
    return redacted


def next_export_specification(rows: list[dict[str, str]], metrics: dict[str, object], args: argparse.Namespace) -> list[str]:
    blockers = {row["item"]: row for row in rows if row["status"] == "blocked"}
    lines = [
        (
            "A promotable SAM/FPDS action-history export must clear the hard gates above "
            "before it is used as the primary procurement action panel."
        ),
        "",
        "- Coverage target: fiscal-year 2024 action-history rows across at least "
        f"`{args.min_agencies}` agencies, at least `{args.min_rows}` rows, at least "
        f"`{args.min_awards}` distinct PIID/award identifiers, and at least "
        f"`{args.min_date_span_days}` days of action-date span.",
        "- Representative agency seed: " + "; ".join(DEFAULT_REPRESENTATIVE_AGENCIES) + ".",
        "- Required field families: " + "; ".join(REQUIRED_ACTION_HISTORY_FIELDS) + ".",
        (
            "- Validation command: "
            "`SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/export.zip make sam-contract-awards-export-audit`, "
            "or set `SAM_CONTRACT_AWARDS_LIVE_URL` to the SAM.gov emailed download link."
        ),
    ]
    if not blockers:
        lines.append(
            "- Current result: no hard export-shape blockers. Inspect warnings and diagnostics before snapshot promotion."
        )
        return lines
    lines.append("- Current blockers to fix before promotion:")
    for item in ("agency-breadth", "date-span", "action-date-coverage", "row-count", "distinct-awards"):
        if item in blockers:
            row = blockers[item]
            lines.append(f"  - `{item}`: observed `{row['value']}`, required `{row['threshold']}`.")
    if "action-date-coverage" in blockers and float(metrics.get("rawSolicitationDateShare", 0.0)) > 0.0:
        lines.append(
            "  - The raw export contains solicitation dates but not action-date candidates; "
            "use an awards/action-history export surface, not a solicitation-only extract."
        )
    if float(metrics.get("rawAmountFieldShare", 0.0)) <= 0.0:
        lines.append(
            "  - The raw export has no recognized obligation/amount field; include action obligation or current award value columns."
        )
    return lines


def sam_export_url_freshness() -> dict[str, str]:
    generated_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_GENERATED_AT", "")
    expires_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_EXPIRES_AT", "")
    recorded_raw = env("SAM_CONTRACT_AWARDS_LIVE_URL_RECORDED_AT", "")
    time_source = env("SAM_CONTRACT_AWARDS_LIVE_URL_TIME_SOURCE", "") or "missing"
    ttl_minutes = int_env("SAM_CONTRACT_AWARDS_LIVE_URL_VALID_MINUTES", 60)
    if ttl_minutes <= 0:
        ttl_minutes = 60
    generated = parse_time(generated_raw)
    expires = parse_time(expires_raw)
    recorded = parse_time(recorded_raw)
    if not expires and generated:
        expires = generated + timedelta(minutes=ttl_minutes)
    if not generated and not expires:
        return {
            "status": "unknown",
            "evidence": freshness_evidence(None, None, ttl_minutes, recorded, time_source),
            "generatedAt": "",
            "expiresAt": "",
            "recordedAt": fmt_time(recorded),
            "timeSource": time_source,
            "ttlMinutes": str(ttl_minutes),
        }
    if generated_raw and not generated:
        return {
            "status": "unknown",
            "evidence": freshness_evidence("unparseable", expires, ttl_minutes, recorded, time_source),
            "generatedAt": "",
            "expiresAt": fmt_time(expires),
            "recordedAt": fmt_time(recorded),
            "timeSource": time_source,
            "ttlMinutes": str(ttl_minutes),
        }
    if expires_raw and not expires:
        return {
            "status": "unknown",
            "evidence": freshness_evidence(generated, "unparseable", ttl_minutes, recorded, time_source),
            "generatedAt": fmt_time(generated),
            "expiresAt": "",
            "recordedAt": fmt_time(recorded),
            "timeSource": time_source,
            "ttlMinutes": str(ttl_minutes),
        }
    assert expires is not None
    status = "fresh" if datetime.now(timezone.utc) < expires else "expired"
    return {
        "status": status,
        "evidence": freshness_evidence(generated, expires, ttl_minutes, recorded, time_source),
        "generatedAt": fmt_time(generated),
        "expiresAt": fmt_time(expires),
        "recordedAt": fmt_time(recorded),
        "timeSource": time_source,
        "ttlMinutes": str(ttl_minutes),
    }


def freshness_evidence(
        generated: datetime | str | None,
        expires: datetime | str | None,
        ttl_minutes: int,
        recorded: datetime | None,
        time_source: str,
) -> str:
    generated_text = generated if isinstance(generated, str) else fmt_time(generated) or "missing"
    expires_text = expires if isinstance(expires, str) else fmt_time(expires) or "missing"
    return (
        f"generatedAt={generated_text}; expiresAt={expires_text}; "
        f"ttlMinutes={ttl_minutes}; recordedAt={fmt_time(recorded) or 'missing'}; "
        f"timeSource={time_source}"
    )


def parse_time(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    normalized = value
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fmt_time(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
