#!/usr/bin/env python3
"""Generate a reviewer-facing claim-boundary audit from source-panel coverage."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


SOURCE_PANEL_INVENTORY = Path("reports/source-panel-inventory.csv")
VALIDATION_SUMMARY = Path("reports/validation-summary.csv")
OUTPUT = Path("reports")

WEAK_STATUSES = {"thin", "warning", "fixture-only", "missing"}

CLAIM_RULES = {
    "usable": {
        "claimBoundary": (
            "May support mechanism diagnostics and distributional anchoring within the "
            "stated source scope."
        ),
        "forbiddenClaim": (
            "Do not present as a causal estimate or nationally representative policy effect."
        ),
    },
    "thin": {
        "claimBoundary": (
            "May support source-aware plausibility checks only; magnitude claims must be "
            "phrased as proxy-backed or thin."
        ),
        "forbiddenClaim": (
            "Do not present as article-level calibration or validation of hidden-channel magnitude."
        ),
    },
    "warning": {
        "claimBoundary": (
            "May be used as a coverage warning and schema diagnostic; do not use the moment "
            "as a stable empirical rate."
        ),
        "forbiddenClaim": (
            "Do not treat the warning metric as calibration-grade evidence."
        ),
    },
    "fixture-only": {
        "claimBoundary": (
            "May show that the parser, schema, and model path exist; it does not support "
            "empirical magnitude claims."
        ),
        "forbiddenClaim": (
            "Do not cite fixture values as source coverage or calibration evidence."
        ),
    },
    "missing": {
        "claimBoundary": (
            "May be discussed only as a missing source panel or future validation target."
        ),
        "forbiddenClaim": (
            "Do not imply observed source coverage, empirical anchoring, or validation."
        ),
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-panel-inventory", type=Path, default=SOURCE_PANEL_INVENTORY)
    parser.add_argument("--validation-summary", type=Path, default=VALIDATION_SUMMARY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    panels = read_panels(args.source_panel_inventory)
    validation_counts = read_validation_counts(args.validation_summary)
    rows = [claim_row(panel) for panel in panels]
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "claim-boundary-audit.csv", rows)
    write_markdown(args.output / "claim-boundary-audit.md", rows, validation_counts)
    print(f"Wrote {args.output / 'claim-boundary-audit.csv'}")
    print(f"Wrote {args.output / 'claim-boundary-audit.md'}")
    return 0


def read_panels(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing source-panel inventory: {path}")
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_validation_counts(path: Path) -> dict[str, int]:
    counts = {"fit": 0, "partial": 0, "miss": 0, "source_gap": 0, "unknown": 0, "not_applicable": 0}
    if not path.exists():
        return counts
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            status = row.get("status", "")
            if status in counts:
                counts[status] += 1
    return counts


def claim_row(panel: dict[str, str]) -> dict[str, str]:
    status = panel.get("status", "missing")
    rule = CLAIM_RULES.get(status, CLAIM_RULES["missing"])
    return {
        "panel": panel.get("panel", ""),
        "mechanism": panel.get("mechanism", ""),
        "evidenceClass": panel.get("evidenceClass", ""),
        "status": status,
        "supportLevel": support_level(panel),
        "claimBoundary": rule["claimBoundary"],
        "forbiddenClaim": rule["forbiddenClaim"],
        "requiredNextEvidence": panel.get("nextAction", ""),
    }


def support_level(panel: dict[str, str]) -> str:
    status = panel.get("status", "missing")
    if status in {"missing", "fixture-only"}:
        return "schema-only"
    if status == "warning":
        return "warning"
    if status == "thin":
        return "thin"
    if status != "usable":
        return "limited"

    evidence = panel.get("evidenceClass", "").lower()
    if "proxy/thin" in evidence:
        return "proxy-thin"
    if "direct/proxy" in evidence:
        return "direct-proxy-bounded"
    if "denominator-mapped" in evidence:
        return "denominator-bounded"
    if "proxy" in evidence:
        return "proxy-bounded"
    if "program" in evidence:
        return "program-bounded"
    if "when present" in evidence:
        return "conditional-direct"
    if "direct" in evidence:
        return "direct-bounded"
    return "source-bounded"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "panel",
        "mechanism",
        "evidenceClass",
        "status",
        "supportLevel",
        "claimBoundary",
        "forbiddenClaim",
        "requiredNextEvidence",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], validation_counts: dict[str, int]) -> None:
    weak_rows = [row for row in rows if row["status"] in WEAK_STATUSES]
    bounded_rows = [
        row for row in rows
        if row["status"] == "usable" and row["supportLevel"] != "direct-bounded"
    ]
    lines = [
        "# Claim Boundary Audit",
        "",
        "This audit maps each empirical source panel to the manuscript claim boundary it can support. It is generated from `reports/source-panel-inventory.csv`, so source-coverage changes update the claim ledger before paper artifacts are rebuilt.",
        "",
        "## Validation Status Summary",
        "",
        f"- Fit: `{validation_counts['fit']}`",
        f"- Partial: `{validation_counts['partial']}`",
        f"- Miss: `{validation_counts['miss']}`",
        f"- Source gap: `{validation_counts['source_gap']}`",
        f"- Unknown: `{validation_counts['unknown']}`",
        f"- Not applicable: `{validation_counts['not_applicable']}`",
        "",
        "## Claim Rules",
        "",
        "| Panel | Mechanism | Evidence | Status | Support level | Permitted claim boundary | Claim to avoid | Required next evidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {panel} | {mechanism} | {evidenceClass} | {status} | {supportLevel} | {claimBoundary} | {forbiddenClaim} | {requiredNextEvidence} |".format(
                **{key: markdown_cell(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Weak-Panel Gate",
        "",
        f"- Weak panels requiring explicit claim limits: `{len(weak_rows)}`",
    ])
    for row in weak_rows:
        lines.append(
            f"- `{row['panel']}` ({row['status']}): {row['claimBoundary']}"
        )
    lines.extend([
        "",
        "## Bounded-Evidence Gate",
        "",
        f"- Usable panels with proxy, denominator, program, or mixed evidence limits: `{len(bounded_rows)}`",
    ])
    for row in bounded_rows:
        lines.append(
            f"- `{row['panel']}` ({row['supportLevel']}): {row['claimBoundary']}"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
