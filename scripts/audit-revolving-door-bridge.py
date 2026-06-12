#!/usr/bin/env python3
"""Audit the revolving-door bridge used by source-moment validation.

The committed snapshot derives revolving-door rows from LDA covered-position
fields. Those rows are useful for covered-position and cooling-off diagnostics,
but they are not a representative post-employment personnel-movement panel.
This report keeps that boundary visible in the review bundle.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
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
    rows = read_rows(normalized / "revolving-door.csv")

    report_rows = [
        audit_rows(
            "lda-covered-position-access-proxy",
            "revolving-door",
            statuses,
            [row for row in rows if is_lda_covered_position(row)],
            "source-native LDA covered-position derivation",
            "covered-position and cooling-off exposure proxy",
            "supports covered-position mechanism diagnostics; not representative post-employment movement",
        ),
        audit_rows(
            "documented-post-employment-movement",
            "revolving-door",
            statuses,
            [row for row in rows if is_documented_personnel_movement(row)],
            "documented personnel-movement export",
            "direct post-employment movement evidence",
            "required before claiming representative post-employment movement or access intensity",
        ),
        audit_rows(
            "fixture-schema-rows",
            "revolving-door",
            statuses,
            [row for row in rows if is_fixture(row)],
            "schema fixture fallback",
            "fixture",
            "schema and parser continuity only; not empirical calibration evidence",
        ),
        audit_rows(
            "cooling-off-under-one-year",
            "revolving-door",
            statuses,
            [row for row in rows if number(row.get("coolingOffMonths")) < 12],
            "cooling-off interval diagnostic",
            "covered-position interval proxy",
            "use as a stress diagnostic, not a measured cooling-off violation rate",
        ),
        audit_rows(
            "procurement-linked-roles",
            "revolving-door",
            statuses,
            [row for row in rows if is_procurement_linked(row)],
            "procurement-linked personnel bridge",
            "role-text proxy",
            "requires OGE, contract-office, or personnel-source overlays before procurement revolving-door claims",
        ),
    ]

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "revolving-door-bridge-audit.csv", report_rows)
    write_markdown(args.reports / "revolving-door-bridge-audit.md", report_rows)
    print(f"Wrote {args.reports / 'revolving-door-bridge-audit.csv'}")
    print(f"Wrote {args.reports / 'revolving-door-bridge-audit.md'}")
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
        status_key: str,
        statuses: dict[str, dict[str, str]],
        rows: list[dict[str, str]],
        role: str,
        evidence: str,
        claim_boundary: str,
) -> dict[str, str]:
    by_agency = grouped_count(rows, "agency")
    return {
        "source": source,
        "snapshotStatus": snapshot_status(status_key, statuses, rows),
        "evidence": evidence,
        "role": role,
        "rows": str(len(rows)),
        "distinctPeople": str(count_distinct(rows, "person")),
        "distinctOrganizations": str(count_distinct(rows, "organization")),
        "distinctAgencies": str(count_distinct(rows, "agency")),
        "topAgencyShare": format_float(top_share(by_agency, 1)),
        "coveredPositionRows": str(sum(1 for row in rows if is_lda_covered_position(row))),
        "documentedMovementRows": str(sum(1 for row in rows if is_documented_personnel_movement(row))),
        "fixtureRows": str(sum(1 for row in rows if is_fixture(row))),
        "formerOfficialRoleRows": str(sum(1 for row in rows if row.get("formerOfficialRole", "").strip())),
        "coolingOffUnderOneYearRows": str(sum(1 for row in rows if number(row.get("coolingOffMonths")) < 12)),
        "confidenceMean": format_float(average([number(row.get("confidence")) for row in rows])),
        "influenceMean": format_float(average([number(row.get("influenceShare")) for row in rows])),
        "influenceWeightedFormerOfficialShare": format_float(weighted_indicator(rows, "formerOfficialRole", "influenceShare")),
        "claimBoundary": claim_boundary,
        "statusNote": statuses.get(status_key, {}).get("notes", ""),
    }


def snapshot_status(status_key: str, statuses: dict[str, dict[str, str]], rows: list[dict[str, str]]) -> str:
    if not rows:
        return "not-present"
    status = statuses.get(status_key, {}).get("status")
    if status:
        return status
    return "unknown"


def is_lda_covered_position(row: dict[str, str]) -> bool:
    return row.get("sourceType", "").strip().lower() == "lda-covered-position"


def is_fixture(row: dict[str, str]) -> bool:
    return "fixture" in row.get("sourceType", "").lower()


def is_documented_personnel_movement(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("sourceType", ""),
            row.get("positionType", ""),
            row.get("sourceUrl", ""),
        ]
    ).lower()
    if is_lda_covered_position(row) or is_fixture(row):
        return False
    markers = [
        "post-employment",
        "personnel-movement",
        "post-government",
        "opensecrets",
        "legistorm",
        "oge",
        "faca",
        "witness",
        "propublica",
    ]
    return any(marker in text for marker in markers)


def is_procurement_linked(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("sector", ""),
            row.get("agency", ""),
            row.get("formerOfficialRole", ""),
            row.get("positionType", ""),
            row.get("organization", ""),
        ]
    ).lower()
    markers = ["procurement", "contract", "acquisition", "vendor", "award"]
    return any(marker in text for marker in markers)


def grouped_count(rows: list[dict[str, str]], key: str) -> dict[str, float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row.get(key, "") or "unknown"] += 1.0
    return dict(grouped)


def top_share(counts: dict[str, float], count: int) -> float:
    total = sum(counts.values())
    if total <= 0.0:
        return 0.0
    return sum(sorted(counts.values(), reverse=True)[:count]) / total


def count_distinct(rows: list[dict[str, str]], key: str) -> int:
    return len({row.get(key, "").strip() for row in rows if row.get(key, "").strip()})


def weighted_indicator(rows: list[dict[str, str]], key: str, weight_key: str) -> float:
    weighted_sum = sum((1.0 if row.get(key, "").strip() else 0.0) * number(row.get(weight_key)) for row in rows)
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
        "distinctPeople",
        "distinctOrganizations",
        "distinctAgencies",
        "topAgencyShare",
        "coveredPositionRows",
        "documentedMovementRows",
        "fixtureRows",
        "formerOfficialRoleRows",
        "coolingOffUnderOneYearRows",
        "confidenceMean",
        "influenceMean",
        "influenceWeightedFormerOfficialShare",
        "claimBoundary",
        "statusNote",
    ]
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lda = next((row for row in rows if row["source"] == "lda-covered-position-access-proxy"), {})
    documented = next((row for row in rows if row["source"] == "documented-post-employment-movement"), {})
    cooling = next((row for row in rows if row["source"] == "cooling-off-under-one-year"), {})
    lines = [
        "# Revolving-Door Bridge Audit",
        "",
        (
            "This audit separates LDA covered-position access proxies from documented "
            "post-employment personnel-movement rows and from fixture rows."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            f"The committed revolving-door bridge contains {lda.get('rows', '0')} LDA-derived "
            f"covered-position rows across {lda.get('distinctPeople', '0')} people, "
            f"{lda.get('distinctOrganizations', '0')} organizations, and "
            f"{lda.get('distinctAgencies', '0')} agency or office labels. It contains "
            f"{documented.get('rows', '0')} documented post-employment movement rows. "
            f"The cooling-off-under-one-year diagnostic has {cooling.get('rows', '0')} rows. "
            "Revolving-door magnitude and access-intensity claims remain bounded until OGE, FACA, "
            "witness, LegiStorm/OpenSecrets, ProPublica-style, or other documented personnel "
            "movement exports are archived."
        ),
        "",
        "| Source | Status | Evidence | Role | Rows | People | Orgs | Agencies | Top agency | Covered-position | Documented movement | Fixture | Under 1yr | Confidence | Influence | Boundary |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {snapshotStatus} | {evidence} | {role} | {rows} | "
            "{distinctPeople} | {distinctOrganizations} | {distinctAgencies} | "
            "{topAgencyShare} | {coveredPositionRows} | {documentedMovementRows} | "
            "{fixtureRows} | {coolingOffUnderOneYearRows} | {confidenceMean} | "
            "{influenceMean} | {claimBoundary} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
