#!/usr/bin/env python3
"""Build candidate cross-venue actor links from the frozen source snapshot.

The output is intentionally a candidate report, not a production calibration
source product. It helps reviewers and future source work inspect which actors
could seed the first-wave entity-resolution spine without treating automated
name normalization as verified linkage evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "snapshots" / "2024-env" / "normalized"
REPORTS = ROOT / "reports"

STOPWORDS = {
    "A",
    "AN",
    "AND",
    "CO",
    "COMPANY",
    "CORP",
    "CORPORATION",
    "INC",
    "INCORPORATED",
    "L L C",
    "LIMITED",
    "LLC",
    "LLP",
    "LP",
    "LTD",
    "OF",
    "PLC",
    "THE",
}
IGNORED_KEYS = {
    "EPA",
    "ENVIRONMENTAL PROTECTION AGENCY",
    "OPAQUE ISSUE ADVOCACY CAPACITY",
    "NYC CAMPAIGN FINANCE BOARD",
}
MAX_SOURCE_RECORD_SAMPLES = 8
TOP_MARKDOWN_ROWS = 40


@dataclass(frozen=True)
class SourceSpec:
    filename: str
    source_system: str
    venue: str
    name_columns: tuple[str, ...]
    amount_columns: tuple[str, ...] = ()
    issue_column: str = "issueDomain"
    id_columns: tuple[str, ...] = ()


SOURCE_SPECS = (
    SourceSpec(
        "lda-lobbying.csv",
        "LDA",
        "visible_lobbying",
        ("client", "registrant"),
        ("amount",),
    ),
    SourceSpec(
        "fec-campaign-finance.csv",
        "OpenFEC",
        "electoral_money",
        ("source", "recipient"),
        ("amount",),
        id_columns=("sourceRecordId",),
    ),
    SourceSpec(
        "dark-money.csv",
        "IRS/ProPublica dark-money bridge",
        "opaque_nonprofit_or_dark_money",
        ("source", "recipient"),
        ("amount",),
        id_columns=("sourceRecordId",),
    ),
    SourceSpec(
        "intermediaries.csv",
        "Intermediary bridge",
        "intermediary",
        ("organization", "recipient"),
        ("politicalSpend", "revenue"),
        id_columns=("ein",),
    ),
    SourceSpec(
        "public-financing.csv",
        "Public financing",
        "countervailing_finance",
        ("source", "recipient"),
        ("amount",),
        id_columns=("sourceRecordId",),
    ),
    SourceSpec(
        "revolving-door.csv",
        "LDA revolving-door proxy",
        "revolving_door",
        ("organization",),
        ("influenceShare",),
        id_columns=("sourceRecordId",),
    ),
    SourceSpec(
        "usaspending-procurement-national-actions.csv",
        "USAspending national actions",
        "procurement",
        ("recipient",),
        ("amount",),
        id_columns=("awardId", "piid", "uei"),
    ),
    SourceSpec(
        "usaspending-procurement-actions.csv",
        "USAspending agency actions",
        "procurement",
        ("recipient",),
        ("amount",),
        id_columns=("awardId", "piid", "uei"),
    ),
    SourceSpec(
        "usaspending-awards.csv",
        "USAspending awards",
        "procurement",
        ("recipient",),
        ("amount",),
        id_columns=("awardId", "piid", "uei"),
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    args = parser.parse_args()

    snapshot = args.snapshot if args.snapshot.is_absolute() else args.root / args.snapshot
    reports = args.reports if args.reports.is_absolute() else args.root / args.reports
    records = list(iter_candidate_records(snapshot))
    grouped = summarize_candidates(records)
    summary_rows = [row for row in grouped if int(row["sourceSystemCount"]) >= 2]
    reports.mkdir(parents=True, exist_ok=True)
    write_csv(reports / "first-wave-linkage-candidates.csv", summary_rows)
    write_csv(reports / "first-wave-linkage-candidate-records.csv", records)
    write_markdown(reports / "first-wave-linkage-candidates.md", summary_rows, records)
    print(f"Wrote {reports / 'first-wave-linkage-candidates.csv'}")
    print(f"Wrote {reports / 'first-wave-linkage-candidate-records.csv'}")
    print(f"Wrote {reports / 'first-wave-linkage-candidates.md'}")
    return 0


def iter_candidate_records(snapshot: Path) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for spec in SOURCE_SPECS:
        path = snapshot / spec.filename
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as source:
            for index, row in enumerate(csv.DictReader(source), start=1):
                for column in spec.name_columns:
                    raw_name = row.get(column, "")
                    normalized = normalize_name(raw_name)
                    if not usable_key(normalized):
                        continue
                    output.append(
                        {
                            "candidateActorId": candidate_id(normalized),
                            "normalizedName": normalized,
                            "displayName": clean_display_name(raw_name),
                            "sourceSystem": spec.source_system,
                            "venue": spec.venue,
                            "sourceFile": spec.filename,
                            "sourceColumn": column,
                            "sourceRecordId": source_record_id(row, spec, index),
                            "issueDomain": row.get(spec.issue_column, ""),
                            "activityAmount": format_float(first_numeric(row, spec.amount_columns)),
                            "matchRule": "normalized-name-exact",
                            "candidateOnly": "true",
                            "claimBoundary": (
                                "manual-review seed only; does not clear first-wave source-product, "
                                "causal-calibration, or venue-shifting detection gates"
                            ),
                        }
                    )
    return output


def summarize_candidates(records: list[dict[str, str]]) -> list[dict[str, str]]:
    by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in records:
        by_key[row["candidateActorId"]].append(row)

    rows: list[dict[str, str]] = []
    for candidate, members in by_key.items():
        source_systems = sorted({row["sourceSystem"] for row in members})
        venues = sorted({row["venue"] for row in members})
        issues = sorted({row["issueDomain"] for row in members if row["issueDomain"]})
        total_amount = sum(parse_float(row.get("activityAmount", "")) for row in members)
        display_counter = Counter(row["displayName"] for row in members if row["displayName"])
        display_name = display_counter.most_common(1)[0][0] if display_counter else members[0]["normalizedName"]
        samples = []
        for row in members[:MAX_SOURCE_RECORD_SAMPLES]:
            samples.append(
                f"{row['sourceSystem']}:{row['sourceFile']}:{row['sourceRecordId']}:{row['sourceColumn']}"
            )
        rows.append(
            {
                "candidateActorId": candidate,
                "normalizedName": members[0]["normalizedName"],
                "displayName": display_name,
                "sourceSystemCount": str(len(source_systems)),
                "sourceSystems": "; ".join(source_systems),
                "venueCount": str(len(venues)),
                "venues": "; ".join(venues),
                "candidateType": "cross_venue" if len(venues) >= 2 else "same_venue_multi_source",
                "sourceRecordCount": str(len(members)),
                "issueDomains": "; ".join(issues),
                "totalActivityAmount": format_float(total_amount),
                "sourceRecordSamples": " | ".join(samples),
                "candidateUse": "seed canonical actor table, alias review sample, and linked actor-issue-venue-time panel",
                "reviewAction": (
                    "manually adjudicate aliases, source identifiers, false positives, and issue comparability "
                    "before promoting any row under data/calibration/first-wave/"
                ),
                "claimBoundary": (
                    "candidate-only automated name overlap; not evidence of common control, venue shifting, "
                    "or causal substitution"
                ),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -int(row["venueCount"]),
            -int(row["sourceSystemCount"]),
            -parse_float(row["totalActivityAmount"]),
            row["normalizedName"],
        ),
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if rows:
        fieldnames = list(rows[0])
    elif path.name.endswith("candidate-records.csv"):
        fieldnames = [
            "candidateActorId",
            "normalizedName",
            "displayName",
            "sourceSystem",
            "venue",
            "sourceFile",
            "sourceColumn",
            "sourceRecordId",
            "issueDomain",
            "activityAmount",
            "matchRule",
            "candidateOnly",
            "claimBoundary",
        ]
    else:
        fieldnames = [
            "candidateActorId",
            "normalizedName",
            "displayName",
            "sourceSystemCount",
            "sourceSystems",
            "venueCount",
            "venues",
            "candidateType",
            "sourceRecordCount",
            "issueDomains",
            "totalActivityAmount",
            "sourceRecordSamples",
            "candidateUse",
            "reviewAction",
            "claimBoundary",
        ]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], records: list[dict[str, str]]) -> None:
    source_counts = Counter(row["sourceSystem"] for row in records)
    venue_counts = Counter(row["venue"] for row in records)
    cross_venue_count = sum(1 for row in rows if row.get("candidateType") == "cross_venue")
    pair_counts: Counter[tuple[str, str]] = Counter()
    cross_venue_pair_counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        systems = [item.strip() for item in row["sourceSystems"].split(";") if item.strip()]
        for left_index, left in enumerate(systems):
            for right in systems[left_index + 1 :]:
                pair_counts[(left, right)] += 1
                if row.get("candidateType") == "cross_venue":
                    cross_venue_pair_counts[(left, right)] += 1

    lines = [
        "# First-Wave Linkage Candidates",
        "",
        "This report mines the frozen normalized source snapshot for automated actor-name overlaps that could seed the first-wave venue-shifting and substitution source products. It is a candidate-generation artifact only: these rows do not clear the first-wave source-product gate, calibrated-policy claims, or venue-shifting detection claims.",
        "",
        "## Summary",
        "",
        "- Candidate status: `candidate_only_not_source_product`",
        f"- Candidate source records scanned: `{len(records)}`",
        f"- Cross-source candidate actors: `{len(rows)}`",
        f"- Cross-venue candidate actors: `{cross_venue_count}`",
        f"- Source systems represented: `{len(source_counts)}`",
        f"- Venues represented: `{len(venue_counts)}`",
        "- Production promotion path: manually adjudicate candidates into `data/calibration/first-wave/canonical-actor-identifiers.csv`, `alias-resolution-audit-sample.csv`, `false-match-review-log.csv`, and `linked-actor-issue-venue-time.csv` before any estimation.",
        "",
        "## Source Coverage",
        "",
        "| Source system | Candidate records |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {source} | {count} |" for source, count in sorted(source_counts.items()))
    lines.extend([
        "",
        "## Venue Coverage",
        "",
        "| Venue | Candidate records |",
        "| --- | ---: |",
    ])
    lines.extend(f"| {venue} | {count} |" for venue, count in sorted(venue_counts.items()))
    lines.extend([
        "",
        "## Cross-Source Pair Counts",
        "",
        "| Source pair | Candidate actors |",
        "| --- | ---: |",
    ])
    for (left, right), count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))[:20]:
        lines.append(f"| {left} + {right} | {count} |")
    if not pair_counts:
        lines.append("| none | 0 |")

    lines.extend([
        "",
        "## Cross-Venue Source Pair Counts",
        "",
        "| Source pair | Cross-venue candidate actors |",
        "| --- | ---: |",
    ])
    for (left, right), count in sorted(cross_venue_pair_counts.items(), key=lambda item: (-item[1], item[0]))[:20]:
        lines.append(f"| {left} + {right} | {count} |")
    if not cross_venue_pair_counts:
        lines.append("| none | 0 |")

    lines.extend([
        "",
        "## Top Candidate Actors",
        "",
        "| Candidate | Type | Sources | Venues | Records | Activity | Review action |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ])
    for row in rows[:TOP_MARKDOWN_ROWS]:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_md(row["displayName"]),
                    row["candidateType"],
                    escape_md(row["sourceSystems"]),
                    escape_md(row["venues"]),
                    row["sourceRecordCount"],
                    row["totalActivityAmount"],
                    escape_md(row["reviewAction"]),
                ]
            )
            + " |"
        )
    if not rows:
        lines.append("| none |  |  |  | 0 | 0.0000 | Add source rows before linkage review. |")

    lines.extend([
        "",
        "## Claim Boundary",
        "",
        "Automated normalized-name overlap is not evidence that records refer to the same legal entity, funder, beneficial owner, or coordinated influence strategy. The report is useful because it turns the next empirical task into a reviewable worklist, not because it validates substitution magnitudes. Any promoted first-wave source product must preserve manual decisions, false-positive and false-negative checks, issue-code comparability, and source-record provenance.",
        "",
        "## Next Steps",
        "",
        "1. Review the highest-coverage candidates and assign durable `canonicalActorId` values.",
        "2. Populate the alias-resolution audit sample with positive and negative decisions.",
        "3. Map a narrow issue ontology across LDA, electoral, intermediary, nonprofit, procurement, and rulemaking surfaces.",
        "4. Generate the linked actor-issue-venue-time table only after the manual audit records false-match risk.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize_name(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9&/ ]+", " ", value or "").upper()
    text = text.replace("&", " AND ").replace("/", " ")
    text = re.sub(r"\bL\s+L\s+C\b", "LLC", text)
    words = [word for word in re.split(r"\s+", text) if word]
    words = [word for word in words if word not in STOPWORDS]
    return re.sub(r"\s+", " ", " ".join(words)).strip()


def usable_key(value: str) -> bool:
    if len(value) < 3:
        return False
    if value in IGNORED_KEYS:
        return False
    if value.isdigit():
        return False
    return True


def candidate_id(normalized: str) -> str:
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]
    return f"cand-{digest}"


def clean_display_name(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def source_record_id(row: dict[str, str], spec: SourceSpec, index: int) -> str:
    values = [row.get(column, "").strip() for column in spec.id_columns if row.get(column, "").strip()]
    return "|".join(values) if values else f"row-{index}"


def first_numeric(row: dict[str, str], columns: tuple[str, ...]) -> float:
    for column in columns:
        value = parse_float(row.get(column, ""))
        if value:
            return value
    return 0.0


def parse_float(value: str) -> float:
    try:
        return float(str(value).replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def format_float(value: float) -> str:
    return f"{value:.4f}"


def escape_md(value: str) -> str:
    return (value or "").replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
