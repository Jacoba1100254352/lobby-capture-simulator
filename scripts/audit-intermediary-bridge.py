#!/usr/bin/env python3
"""Audit intermediary source rows used by source-moment validation.

The committed snapshot includes several useful intermediary-adjacent panels:
local campaign-intermediary records, IRS EO BMF nonprofit/association capacity
rows, and IRS POFD Form 8872 political-organization rows. It does not include
representative Form 990 nonprofit-routing rows. This report keeps those
distinctions visible before model outputs are interpreted as hidden-channel
evidence.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPORTS = Path("reports")
SNAPSHOT = Path("data/snapshots/2024-env")
LIVE_STATUS = SNAPSHOT / "live-run-status.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args()

    statuses = read_live_status(args.snapshot / LIVE_STATUS.name)
    rows = read_rows(args.snapshot / "normalized" / "intermediaries.csv")

    report_rows = [
        audit_rows(
            "nyc-cfb-campaign-intermediaries",
            statuses,
            [row for row in rows if row.get("sourceType") == "nyc-cfb-intermediary"],
            "NYC CFB campaign-intermediary rows",
            "direct local intermediary",
            "direct local campaign-intermediary records; not national nonprofit routing or hidden-channel magnitude evidence",
            rows,
        ),
        audit_rows(
            "irs-eo-bmf-nonprofit-capacity",
            statuses,
            [row for row in rows if row.get("sourceType") == "irs-eo-bmf-capacity"],
            "IRS EO BMF nonprofit and association capacity rows",
            "proxy",
            "organizational capacity proxy; not Form 990 routing, donor, grant-network, or expenditure evidence",
            rows,
        ),
        audit_rows(
            "irs-527-political-organizations",
            statuses,
            [row for row in rows if is_irs_527(row)],
            "IRS POFD Form 8872 political-organization filings",
            "direct 527 filings",
            "campaign-adjacent political-organization evidence; keep separate from 501(c)(4)/(c)(6) hidden-donor evidence",
            rows,
        ),
        audit_rows(
            "form990-nonprofit-routing",
            statuses,
            [row for row in rows if is_form990_routing(row)],
            "Form 990 nonprofit-routing, grantmaking, and contractor records",
            "direct nonprofit routing",
            "required before claiming representative nonprofit routing, grant networks, or think-tank/association money paths",
            rows,
        ),
        audit_rows(
            "association-capacity",
            statuses,
            [row for row in rows if row.get("subsection") == "501(c)(6)"],
            "501(c)(6) trade-association capacity rows",
            "proxy",
            "trade-association capacity proxy; not membership, donor, grant-routing, or direct advocacy-expenditure evidence",
            rows,
        ),
        audit_rows(
            "social-welfare-capacity",
            statuses,
            [row for row in rows if row.get("subsection") == "501(c)(4)"],
            "501(c)(4) social-welfare capacity rows",
            "proxy",
            "opaque social-welfare capacity proxy; not direct hidden spending or donor routing",
            rows,
        ),
        audit_rows(
            "think-tank-charitable-capacity",
            statuses,
            [row for row in rows if row.get("subsection") == "501(c)(3)"],
            "501(c)(3) charitable, think-tank, and nonprofit capacity rows",
            "proxy",
            "charitable or think-tank capacity proxy; not donor, grant-routing, or sponsored-research flow evidence",
            rows,
        ),
    ]

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "intermediary-bridge-audit.csv", report_rows)
    write_markdown(args.reports / "intermediary-bridge-audit.md", report_rows)
    print(f"Wrote {args.reports / 'intermediary-bridge-audit.csv'}")
    print(f"Wrote {args.reports / 'intermediary-bridge-audit.md'}")
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


def audit_rows(
    source: str,
    statuses: dict[str, dict[str, str]],
    rows: list[dict[str, str]],
    role: str,
    evidence: str,
    claim_boundary: str,
    all_rows: list[dict[str, str]],
) -> dict[str, str]:
    total_revenue = sum(number(row.get("revenue")) for row in all_rows)
    total_political_spend = sum(number(row.get("politicalSpend")) for row in all_rows)
    total_grantmaking = sum(number(row.get("grantmaking")) for row in all_rows)
    revenue = sum(number(row.get("revenue")) for row in rows)
    political_spend = sum(number(row.get("politicalSpend")) for row in rows)
    grantmaking = sum(number(row.get("grantmaking")) for row in rows)
    return {
        "source": source,
        "snapshotStatus": snapshot_status(statuses, rows),
        "evidence": evidence,
        "role": role,
        "rows": str(len(rows)),
        "distinctOrganizations": str(count_distinct(rows, "organization")),
        "distinctRecipients": str(count_distinct(rows, "recipient")),
        "distinctEins": str(count_distinct(rows, "ein")),
        "revenue": format_float(revenue),
        "politicalSpend": format_float(political_spend),
        "grantmaking": format_float(grantmaking),
        "panelRevenueShare": format_float(safe_divide(revenue, total_revenue)),
        "politicalSpendShare": format_float(safe_divide(political_spend, total_political_spend)),
        "grantmakingShare": format_float(safe_divide(grantmaking, total_grantmaking)),
        "donorDisclosureMean": format_float(average([number(row.get("donorDisclosure")) for row in rows])),
        "c3Rows": str(sum(1 for row in rows if row.get("subsection") == "501(c)(3)")),
        "c4Rows": str(sum(1 for row in rows if row.get("subsection") == "501(c)(4)")),
        "c6Rows": str(sum(1 for row in rows if row.get("subsection") == "501(c)(6)")),
        "c527Rows": str(sum(1 for row in rows if is_irs_527(row))),
        "form990Rows": str(sum(1 for row in rows if is_form990_routing(row))),
        "capacityProxyRows": str(sum(1 for row in rows if is_capacity_proxy(row))),
        "directRoutingRows": str(sum(1 for row in rows if is_direct_routing(row))),
        "claimBoundary": claim_boundary,
        "statusNote": statuses.get("intermediary", {}).get("notes", ""),
    }


def snapshot_status(statuses: dict[str, dict[str, str]], rows: list[dict[str, str]]) -> str:
    if not rows:
        return "not-present"
    return statuses.get("intermediary", {}).get("status", "unknown")


def is_irs_527(row: dict[str, str]) -> bool:
    return row.get("subsection") == "527" or "8872" in row.get("sourceType", "").lower()


def is_form990_routing(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("sourceType", ""),
            row.get("sourceUrl", ""),
        ]
    ).lower()
    return "990" in text or "form990" in text or "form 990" in text


def is_capacity_proxy(row: dict[str, str]) -> bool:
    return row.get("sourceType") == "irs-eo-bmf-capacity"


def is_direct_routing(row: dict[str, str]) -> bool:
    return is_form990_routing(row)


def count_distinct(rows: list[dict[str, str]], key: str) -> int:
    return len({row.get(key, "").strip() for row in rows if row.get(key, "").strip()})


def average(values: list[float]) -> float:
    return safe_divide(sum(values), len(values))


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def format_float(value: float) -> str:
    return f"{value:.4f}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "source",
        "snapshotStatus",
        "evidence",
        "role",
        "rows",
        "distinctOrganizations",
        "distinctRecipients",
        "distinctEins",
        "revenue",
        "politicalSpend",
        "grantmaking",
        "panelRevenueShare",
        "politicalSpendShare",
        "grantmakingShare",
        "donorDisclosureMean",
        "c3Rows",
        "c4Rows",
        "c6Rows",
        "c527Rows",
        "form990Rows",
        "capacityProxyRows",
        "directRoutingRows",
        "claimBoundary",
        "statusNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {row["source"]: int(row["rows"]) for row in rows}
    total_form990_rows = sum(int(row["form990Rows"]) for row in rows)
    lines = [
        "# Intermediary Bridge Audit",
        "",
        (
            "This audit separates local campaign-intermediary records, nonprofit and "
            "association capacity proxies, IRS 527 political-organization filings, "
            "and Form 990 nonprofit-routing evidence in the committed 2024 snapshot."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            "The committed intermediary bridge contains "
            f"{counts.get('nyc-cfb-campaign-intermediaries', 0)} NYC CFB campaign-intermediary rows, "
            f"{counts.get('irs-eo-bmf-nonprofit-capacity', 0)} IRS EO BMF nonprofit/association capacity rows, "
            f"and {counts.get('irs-527-political-organizations', 0)} IRS POFD Form 8872 political-organization rows. "
            f"It contains {total_form990_rows} Form 990 nonprofit-routing rows. Intermediary-substitution "
            "magnitude claims remain bounded until representative Form 990, grantmaking, vendor, donor, "
            "association, or think-tank routing records are archived; the current bridge is not "
            "representative nonprofit routing evidence."
        ),
        "",
        "## Source Split",
        "",
        (
            "| Source | Evidence | Rows | Direct routing rows | Capacity proxy rows | "
            "527 rows | Form 990 rows | Political spend share | Grantmaking share | Claim boundary |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        escaped = {key: markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {source} | {evidence} | {rows} | {directRoutingRows} | "
            "{capacityProxyRows} | {c527Rows} | {form990Rows} | "
            "{politicalSpendShare} | {grantmakingShare} | {claimBoundary} |".format(**escaped)
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
