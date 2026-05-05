#!/usr/bin/env python3
"""Extract direct source moments from normalized calibration tables."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


SNAPSHOT = Path("data/snapshots/2024-env/normalized")
FIXTURES = Path("data/fixtures")
OUTPUT = Path("reports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    rows = []
    rows.extend(extract_scope("snapshot", args.snapshot, ""))
    rows.extend(extract_scope("fixture", args.fixtures, "normalized-"))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "source-moments.csv", rows)
    write_markdown(args.output / "source-moments.md", rows)
    print(f"Wrote {args.output / 'source-moments.csv'}")
    print(f"Wrote {args.output / 'source-moments.md'}")
    return 0


def extract_scope(scope: str, root: Path, prefix: str) -> list[dict[str, str]]:
    rows = []
    rows.extend(lda_moments(scope, root / f"{prefix}lda-lobbying.csv"))
    rows.extend(fec_moments(scope, root / f"{prefix}fec-campaign-finance.csv"))
    rows.extend(regulatory_moments(scope, root / f"{prefix}regulatory-dockets.csv"))
    rows.extend(usaspending_moments(scope, root / f"{prefix}usaspending-awards.csv"))
    rows.extend(revolving_door_moments(scope, root / f"{prefix}revolving-door.csv"))
    return rows


def lda_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "lda", "ldaRows", 0.0, "observed", f"{path} missing or empty")]
    amounts = [number(row.get("amount")) for row in rows]
    by_client = grouped_amount(rows, "client")
    by_registrant = grouped_amount(rows, "registrant")
    by_sector = grouped_amount(rows, "issueDomain")
    total = sum(amounts)
    return [
        moment(scope, "lda", "ldaRows", len(rows), "observed", "normalized LDA rows"),
        moment(scope, "lda", "ldaTotalSpend", total, "observed", "sum of normalized LDA amount"),
        moment(scope, "lda", "lobbyingClientTop1Share", top_share(by_client, 1), "observed", "largest client share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingClientTop3Share", top_share(by_client, 3), "observed", "top three clients share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingRegistrantTop3Share", top_share(by_registrant, 3), "observed", "top three registrants share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingSectorTopShare", top_share(by_sector, 1), "observed", "largest issue-domain share of normalized LDA amount"),
        moment(scope, "lda", "lobbyingDisclosureLagMean", average([number(row.get("disclosureLag")) for row in rows]), "observed", "mean normalized LDA disclosure lag"),
    ]


def fec_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "fec", "fecRows", 0.0, "observed", f"{path} missing or empty")]
    by_source = grouped_amount(rows, "source")
    by_recipient = grouped_amount(rows, "recipient")
    amounts = [number(row.get("amount")) for row in rows]
    total = sum(amounts)
    dark_rows = [row for row in rows if row.get("flowType", "").upper() in {"DARK_MONEY", "SUPER_PAC"}]
    public_rows = [row for row in rows if row.get("flowType", "").upper() in {"PUBLIC_MATCH", "DEMOCRACY_VOUCHER"}]
    return [
        moment(scope, "fec", "fecRows", len(rows), "observed", "normalized OpenFEC rows"),
        moment(scope, "fec", "fecTotalReceipts", total, "observed", "sum of normalized FEC amount"),
        moment(scope, "fec", "fecDonorTop1Share", top_share(by_source, 1), "observed", "largest donor share of normalized FEC amount"),
        moment(scope, "fec", "fecDonorTop3Share", top_share(by_source, 3), "observed", "top three donor share of normalized FEC amount"),
        moment(scope, "fec", "fecRecipientTop3Share", top_share(by_recipient, 3), "observed", "top three recipient share of normalized FEC amount"),
        moment(scope, "fec", "fecLargeDonorWeightedShare", weighted(rows, "largeDonorShare", "amount"), "observed_proxy", "amount-weighted normalized large donor share"),
        moment(scope, "fec", "moneyFlowTraceability", weighted(rows, "traceability", "amount"), "observed_proxy", "amount-weighted traceability across all normalized FEC rows"),
        moment(scope, "fec", "darkMoneyDirectVisibility", weighted(dark_rows, "traceability", "amount"), "inferred", "amount-weighted traceability among DARK_MONEY and SUPER_PAC rows"),
        moment(scope, "fec", "darkMoneySourceShare", safe_divide(sum(number(row.get("amount")) for row in dark_rows), total), "observed_proxy", "DARK_MONEY and SUPER_PAC share of normalized FEC amount"),
        moment(scope, "fec", "publicFinancingSourceShare", safe_divide(sum(number(row.get("amount")) for row in public_rows), total), "observed_proxy", "public-match or voucher share of normalized FEC amount"),
    ]


def regulatory_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "regulatory", "regulatoryRows", 0.0, "observed", f"{path} missing or empty")]
    by_docket = grouped_amount(rows, "docketId", "commentVolume")
    return [
        moment(scope, "regulatory", "regulatoryRows", len(rows), "observed", "normalized regulatory rows"),
        moment(scope, "regulatory", "commentVolumeMean", average([number(row.get("commentVolume")) for row in rows]), "observed_proxy", "mean normalized comment volume"),
        moment(scope, "regulatory", "commentVolumeTop1DocketShare", top_share(by_docket, 1), "observed_proxy", "largest docket share of normalized comments"),
        moment(scope, "regulatory", "commentTemplateShareMean", average([number(row.get("templateShare")) for row in rows]), "observed_proxy", "mean normalized template share"),
        moment(scope, "regulatory", "commentAuthenticationShareMean", average([number(row.get("authenticationShare")) for row in rows]), "observed_proxy", "mean normalized authentication share"),
        moment(scope, "regulatory", "technicalClaimCredibilityMean", average([number(row.get("technicalClaimCredibility")) for row in rows]), "proxy", "mean normalized technical claim credibility"),
    ]


def usaspending_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "usaspending", "procurementRows", 0.0, "observed", f"{path} missing or empty")]
    by_recipient = grouped_amount(rows, "recipient")
    by_agency = grouped_amount(rows, "agency")
    by_sub_agency = grouped_amount(rows, "subAgency")
    total = sum(number(row.get("amount")) for row in rows)
    return [
        moment(scope, "usaspending", "procurementRows", len(rows), "observed", "normalized USAspending award rows"),
        moment(scope, "usaspending", "procurementTotalAwards", total, "observed", "sum of normalized USAspending award amount"),
        moment(scope, "usaspending", "procurementRecipientTop1Share", top_share(by_recipient, 1), "observed", "largest recipient share of normalized award amount"),
        moment(scope, "usaspending", "procurementRecipientTop3Share", top_share(by_recipient, 3), "observed", "top three recipients share of normalized award amount"),
        moment(scope, "usaspending", "procurementAgencyTop1Share", top_share(by_agency, 1), "observed", "largest awarding agency share of normalized award amount"),
        moment(scope, "usaspending", "procurementSubAgencyTop3Share", top_share(by_sub_agency, 3), "observed", "top three sub-agencies share of normalized award amount"),
        moment(scope, "usaspending", "procurementAwardCount", sum(number(row.get("awardCount")) for row in rows), "observed", "sum of normalized award or transaction counts"),
    ]


def revolving_door_moments(scope: str, path: Path) -> list[dict[str, str]]:
    rows = read_rows(path)
    if not rows:
        return [moment(scope, "revolving-door", "revolvingDoorRows", 0.0, "observed", f"{path} missing or empty")]
    former_rows = [row for row in rows if row.get("formerOfficialRole", "").strip()]
    by_agency = grouped_count(rows, "agency")
    return [
        moment(scope, "revolving-door", "revolvingDoorRows", len(rows), "observed", "normalized revolving-door rows"),
        moment(scope, "revolving-door", "revolvingDoorFormerOfficialShare", safe_divide(len(former_rows), len(rows)), "observed_proxy", "share of rows with former official role"),
        moment(scope, "revolving-door", "revolvingDoorAgencyTop1Share", top_share(by_agency, 1), "observed_proxy", "largest agency share of normalized revolving-door rows"),
        moment(scope, "revolving-door", "revolvingDoorCoolingOffUnderOneYearShare", safe_divide(sum(1 for row in rows if number(row.get("coolingOffMonths")) < 12), len(rows)), "observed_proxy", "share of rows with cooling-off interval below one year"),
        moment(scope, "revolving-door", "revolvingDoorInfluenceMean", average([number(row.get("influenceShare")) for row in rows]), "proxy", "mean normalized influence share from source panel"),
    ]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def grouped_amount(rows: list[dict[str, str]], key: str, amount_key: str = "amount") -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row.get(key, "") or "unknown"] += number(row.get(amount_key))
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


def weighted(rows: list[dict[str, str]], value_key: str, weight_key: str) -> float:
    total = sum(number(row.get(weight_key)) for row in rows)
    if total <= 0.0:
        return 0.0
    return sum(number(row.get(value_key)) * number(row.get(weight_key)) for row in rows) / total


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0.0 else 0.0


def number(value: object) -> float:
    try:
        return float(str(value or "0").replace(",", ""))
    except ValueError:
        return 0.0


def moment(scope: str, source: str, metric: str, value: float | int, evidence_type: str, notes: str) -> dict[str, str]:
    return {
        "scope": scope,
        "source": source,
        "metric": metric,
        "value": f"{float(value):.4f}",
        "evidenceType": evidence_type,
        "notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["scope", "source", "metric", "value", "evidenceType", "notes"]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Source Moments",
        "",
        "These are direct moments from normalized calibration tables. They are source diagnostics, not causal estimates.",
        "",
    ]
    warnings = representativeness_warnings(rows)
    if warnings:
        lines.extend(["## Representativeness Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend([
        "| Scope | Source | Metric | Value | Evidence | Notes |",
        "| --- | --- | --- | ---: | --- | --- |",
    ])
    for row in rows:
        lines.append(
            f"| {row['scope']} | {row['source']} | `{row['metric']}` | {row['value']} | {row['evidenceType']} | {row['notes']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def representativeness_warnings(rows: list[dict[str, str]]) -> list[str]:
    warnings: list[str] = []
    lda_rows = metric_value(rows, "snapshot", "lda", "ldaRows")
    if lda_rows < 50:
        warnings.append(
            f"Snapshot LDA row count is {lda_rows:.0f}; treat LDA concentration and disclosure-lag moments as smoke-test diagnostics."
        )
    for metric_name in ("lobbyingClientTop1Share", "lobbyingClientTop3Share", "lobbyingRegistrantTop3Share"):
        value = metric_value(rows, "snapshot", "lda", metric_name)
        if value >= 0.95:
            warnings.append(
                f"Snapshot `{metric_name}` is {value:.4f}; this usually indicates a very narrow or incomplete LDA slice."
            )
    fec_rows = metric_value(rows, "snapshot", "fec", "fecRows")
    if fec_rows < 500:
        warnings.append(
            f"Snapshot FEC row count is {fec_rows:.0f}; use FEC moments as panel diagnostics rather than representative election-cycle estimates."
        )
    if metric_value(rows, "snapshot", "fec", "darkMoneySourceShare") == 0.0:
        warnings.append("Snapshot FEC rows contain no DARK_MONEY or SUPER_PAC flow share; dark-money calibration still depends on benchmark and scenario assumptions.")
    if metric_value(rows, "snapshot", "fec", "publicFinancingSourceShare") == 0.0:
        warnings.append("Snapshot FEC rows contain no public-match or democracy-voucher flow share; public-financing calibration still depends on external benchmarks.")
    revolving_rows = metric_value(rows, "snapshot", "revolving-door", "revolvingDoorRows")
    if revolving_rows <= 10:
        warnings.append(
            f"Snapshot revolving-door row count is {revolving_rows:.0f}; replace the fixture/export stub before using revolving-door moments as empirical anchors."
        )
    return warnings


def metric_value(rows: list[dict[str, str]], scope: str, source: str, metric_name: str) -> float:
    for row in rows:
        if row["scope"] == scope and row["source"] == source and row["metric"] == metric_name:
            return number(row["value"])
    return 0.0


if __name__ == "__main__":
    raise SystemExit(main())
