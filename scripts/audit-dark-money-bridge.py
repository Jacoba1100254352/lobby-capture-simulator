#!/usr/bin/env python3
"""Audit the dark-money bridge and adjacent hidden-channel source rows.

The paper uses public rows to bound hidden-channel mechanisms, but public
nonprofit filings do not reveal underlying donor identities. This report makes
that boundary explicit by separating IRS EO BMF opaque-capacity proxy rows,
ProPublica/IRS Schedule I nonprofit-routing rows, OpenFEC outside-spending
rows, electoral-communication rows, and IRS 527 rows.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPORTS = Path("reports")
SNAPSHOT = Path("data/snapshots/2024-env")
NORMALIZED = SNAPSHOT / "normalized"
LIVE_STATUS = SNAPSHOT / "live-run-status.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args()

    normalized = args.snapshot / "normalized"
    statuses = read_live_status(args.snapshot / LIVE_STATUS.name)
    dark_rows = read_rows(normalized / "dark-money.csv")
    capacity_rows = [row for row in dark_rows if is_capacity_proxy(row)]
    nonprofit_routing_rows = [row for row in dark_rows if is_direct_hidden_routing(row)]
    fec_rows = read_rows(normalized / "fec-campaign-finance.csv")
    intermediary_rows = read_rows(normalized / "intermediaries.csv")

    rows = [
        audit_money_rows(
            "dark-money-capacity-proxy",
            "dark-money",
            statuses,
            capacity_rows,
            "IRS EO BMF 501(c)(4)/(c)(6) opaque-capacity bridge",
            "proxy",
            "capacity proxy for opaque nonprofit advocacy; not direct hidden-donor routing",
        ),
        audit_money_rows(
            "propublica-nonprofit-routing",
            "dark-money",
            statuses,
            nonprofit_routing_rows,
            "ProPublica Nonprofit Explorer and IRS Form 990 Schedule I grant-routing rows",
            "direct nonprofit-routing",
            "public nonprofit transfer evidence; not donor identity evidence",
        ),
        audit_money_rows(
            "openfec-super-pac",
            "fec-schedule-e",
            statuses,
            [row for row in fec_rows if row.get("flowType") == "SUPER_PAC"],
            "OpenFEC Schedule E independent-expenditure pressure",
            "direct outside-spending",
            "observable outside spending; not direct dark-money or hidden-donor evidence",
        ),
        audit_money_rows(
            "openfec-electoral-communications",
            "fec-electoral-communications",
            statuses,
            [
                row
                for row in fec_rows
                if row.get("flowType") in {"ELECTIONEERING", "COMMUNICATION_COST"}
            ],
            "OpenFEC electioneering and communication-cost bridge",
            "direct electoral-communication",
            "observable electoral communications; adjacent evidence, not hidden-donor routing",
        ),
        audit_intermediary_rows(
            "irs-527-political-organizations",
            "intermediary",
            statuses,
            [
                row
                for row in intermediary_rows
                if "527" in row.get("subsection", "") or "8872" in row.get("sourceType", "")
            ],
            "IRS POFD Form 8872 political-organization filings",
            "direct 527 filings",
            "campaign-adjacent intermediary evidence; keep separate from 501(c)(4)/(c)(6) dark-money evidence",
        ),
        audit_intermediary_rows(
            "nonprofit-association-capacity",
            "intermediary",
            statuses,
            [
                row
                for row in intermediary_rows
                if row.get("sourceType") == "irs-eo-bmf-capacity"
                or row.get("subsection") in {"501(c)(3)", "501(c)(4)", "501(c)(6)"}
            ],
            "IRS EO BMF nonprofit and association capacity rows",
            "proxy",
            "organizational capacity proxy; not routing, donor, or expenditure evidence",
        ),
        audit_intermediary_rows(
            "nyc-cfb-campaign-intermediaries",
            "intermediary",
            statuses,
            [row for row in intermediary_rows if row.get("sourceType") == "nyc-cfb-intermediary"],
            "NYC CFB campaign-intermediary rows",
            "direct local intermediary",
            "direct local campaign-intermediary records; not national hidden-channel magnitude evidence",
        ),
    ]
    add_amount_shares(rows)

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "dark-money-bridge-audit.csv", rows)
    write_markdown(args.reports / "dark-money-bridge-audit.md", rows)
    print(f"Wrote {args.reports / 'dark-money-bridge-audit.csv'}")
    print(f"Wrote {args.reports / 'dark-money-bridge-audit.md'}")
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


def audit_money_rows(
        source: str,
        status_key: str,
        statuses: dict[str, dict[str, str]],
        rows: list[dict[str, str]],
        role: str,
        evidence: str,
        claim_boundary: str,
) -> dict[str, str]:
    amount_total = sum(number(row.get("amount")) for row in rows)
    proxy_rows = [row for row in rows if is_capacity_proxy(row)]
    direct_rows = [row for row in rows if is_direct_hidden_routing(row)]
    c4_rows = [row for row in rows if "501(c)(4)" in row.get("committeeType", "")]
    c6_rows = [row for row in rows if "501(c)(6)" in row.get("committeeType", "")]
    return {
        "source": source,
        "snapshotStatus": snapshot_status(status_key, statuses, rows),
        "evidence": evidence,
        "role": role,
        "rows": str(len(rows)),
        "amount": format_float(amount_total),
        "bridgeAmountShare": "0.0000",
        "weightedTraceability": format_float(weighted_average(rows, "traceability", "amount")),
        "weightedLargeDonorShare": format_float(weighted_average(rows, "largeDonorShare", "amount")),
        "donorDisclosureMean": "0.0000",
        "directRoutingRows": str(len(direct_rows)),
        "capacityProxyRows": str(len(proxy_rows)),
        "c4Rows": str(len(c4_rows)),
        "c6Rows": str(len(c6_rows)),
        "distinctSources": str(count_distinct(rows, "source")),
        "claimBoundary": claim_boundary,
        "statusNote": statuses.get(status_key, {}).get("notes", ""),
    }


def audit_intermediary_rows(
        source: str,
        status_key: str,
        statuses: dict[str, dict[str, str]],
        rows: list[dict[str, str]],
        role: str,
        evidence: str,
        claim_boundary: str,
) -> dict[str, str]:
    amount_total = sum(number(row.get("politicalSpend")) for row in rows)
    c4_rows = [row for row in rows if row.get("subsection") == "501(c)(4)"]
    c6_rows = [row for row in rows if row.get("subsection") == "501(c)(6)"]
    return {
        "source": source,
        "snapshotStatus": snapshot_status(status_key, statuses, rows),
        "evidence": evidence,
        "role": role,
        "rows": str(len(rows)),
        "amount": format_float(amount_total),
        "bridgeAmountShare": "0.0000",
        "weightedTraceability": "0.0000",
        "weightedLargeDonorShare": "0.0000",
        "donorDisclosureMean": format_float(average([number(row.get("donorDisclosure")) for row in rows])),
        "directRoutingRows": "0",
        "capacityProxyRows": str(len(rows)) if evidence == "proxy" else "0",
        "c4Rows": str(len(c4_rows)),
        "c6Rows": str(len(c6_rows)),
        "distinctSources": str(count_distinct(rows, "organization")),
        "claimBoundary": claim_boundary,
        "statusNote": statuses.get(status_key, {}).get("notes", ""),
    }


def snapshot_status(status_key: str, statuses: dict[str, dict[str, str]], rows: list[dict[str, str]]) -> str:
    status = statuses.get(status_key, {}).get("status")
    if status:
        return status
    return "missing" if not rows else "unknown"


def add_amount_shares(rows: list[dict[str, str]]) -> None:
    total = sum(number(row["amount"]) for row in rows)
    for row in rows:
        row["bridgeAmountShare"] = format_float(safe_divide(number(row["amount"]), total))


def is_capacity_proxy(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("committeeType", ""),
            row.get("spendingPurpose", ""),
            row.get("sourceUrl", ""),
        ]
    ).lower()
    return "capacity proxy" in text or "eo_dc.csv" in text


def is_direct_hidden_routing(row: dict[str, str]) -> bool:
    if row.get("flowType") != "DARK_MONEY":
        return False
    return not is_capacity_proxy(row)


def count_distinct(rows: list[dict[str, str]], key: str) -> int:
    return len({row.get(key, "").strip() for row in rows if row.get(key, "").strip()})


def weighted_average(rows: list[dict[str, str]], value_key: str, weight_key: str) -> float:
    weighted_sum = sum(number(row.get(value_key)) * number(row.get(weight_key)) for row in rows)
    weight_total = sum(number(row.get(weight_key)) for row in rows)
    return safe_divide(weighted_sum, weight_total)


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
        "amount",
        "bridgeAmountShare",
        "weightedTraceability",
        "weightedLargeDonorShare",
        "donorDisclosureMean",
        "directRoutingRows",
        "capacityProxyRows",
        "c4Rows",
        "c6Rows",
        "distinctSources",
        "claimBoundary",
        "statusNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    dark = next((row for row in rows if row["source"] == "dark-money-capacity-proxy"), {})
    nonprofit_routing = next((row for row in rows if row["source"] == "propublica-nonprofit-routing"), {})
    super_pac = next((row for row in rows if row["source"] == "openfec-super-pac"), {})
    electoral = next((row for row in rows if row["source"] == "openfec-electoral-communications"), {})
    section_527 = next((row for row in rows if row["source"] == "irs-527-political-organizations"), {})
    lines = [
        "# Dark-Money Bridge Audit",
        "",
        (
            "This audit separates proxy capacity rows from adjacent observed electoral and "
            "intermediary rows. It also separates public Form 990 Schedule I nonprofit-routing "
            "transfers from hidden-donor identity evidence. It is a guardrail against treating "
            "opaque nonprofit capacity, Super PAC spending, electioneering, communication-cost, "
            "or IRS 527 rows as direct hidden-donor evidence."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            f"The committed dark-money bridge contains {dark.get('rows', '0')} IRS EO BMF "
            f"capacity-proxy rows, including {dark.get('c4Rows', '0')} 501(c)(4) rows and "
            f"{dark.get('c6Rows', '0')} 501(c)(6) rows. It contains "
            f"{nonprofit_routing.get('directRoutingRows', '0')} non-proxy nonprofit-routing "
            "transfer rows from public Schedule I filings, but zero observed hidden-donor "
            "identity rows. "
            f"Adjacent observed panels include {super_pac.get('rows', '0')} Super PAC rows, "
            f"{electoral.get('rows', '0')} electioneering or communication-cost rows, and "
            f"{section_527.get('rows', '0')} IRS 527 political-organization rows. Hidden-donor "
            "magnitude claims remain bounded until donor, transfer, or nonprofit-expenditure "
            "coverage is broadened beyond this top-EIN routing slice."
        ),
        "",
        "| Source | Status | Evidence | Role | Rows | Amount | Share | Traceability | Donor disclosure | Direct routing | Proxy rows | C4 | C6 | Distinct sources | Boundary |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {snapshotStatus} | {evidence} | {role} | {rows} | {amount} | "
            "{bridgeAmountShare} | {weightedTraceability} | {donorDisclosureMean} | "
            "{directRoutingRows} | {capacityProxyRows} | {c4Rows} | {c6Rows} | "
            "{distinctSources} | {claimBoundary} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
