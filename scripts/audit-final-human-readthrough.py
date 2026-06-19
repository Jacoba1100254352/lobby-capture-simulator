#!/usr/bin/env python3
"""Audit the final human read-through record as a structured gate.

The manual signoff file is allowed to remain pending for mechanism-review
circulation. This audit makes that pending state explicit and fails only on
malformed or internally inconsistent handoff evidence.
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
REGGOV_AUTHOR_GUIDELINES_URL = "https://onlinelibrary.wiley.com/page/journal/17485991/homepage/forauthors.html"
VERSION_PATTERN = re.compile(r"^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DATE_RELEASED_PATTERN = re.compile(r"^date-released:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
NO_SUPERSEDING_VALUES = {
    "none",
    "no",
    "none identified",
    "no superseding instructions",
}

REQUIRED_FIELDS = [
    "status",
    "reviewed-release",
    "venue-target",
    "author-guidelines-url",
]

SIGNOFF_FIELDS = [
    "signed-off-by",
    "signed-off-date",
    "reviewed-commit",
    "doi-archive",
]

LIVE_AUTHOR_PAGE_FIELDS = [
    "author-guidelines-checked-by",
    "author-guidelines-checked-date",
    "author-guidelines-superseding-instructions",
]

EXPECTED_LIVE_CHECKLIST = [
    "Open the live author page named in `author-guidelines-url` immediately before journal submission.",
    "Confirm the target journal, article type, word limit, title-page expectations, disclosure expectations, supporting-information expectations, and LaTeX/package requirements still match the generated bundle.",
    "Record checker, date, and superseding-instruction status in the fields above.",
]

EXPECTED_SCHOLARLY_CHECKLIST = [
    "Abstract states the mechanism-model contribution without implying calibrated policy-effect estimation.",
    "Introduction separates model assumptions, synthetic results, and empirical bridge scope.",
    "Literature positioning explains the regulatory-governance contribution relative to lobbying, capture, venue-shifting, and ABM validation work.",
    "Model specification is internally consistent with the ODD-style supplement and does not leave unresolved equations, parameters, or diagnostic definitions.",
    "Results describe synthetic mechanism behavior and do not present reform rankings as real-world policy estimates.",
    "Empirical bridge language is bounded to source moments, source-panel coverage, and validation-gap diagnostics.",
    "Tables and figures are referenced in order, readable in the Wiley PDF, and not duplicative or misleading.",
    "Limitations identify open source panels, causal-calibration targets, and construct-validity risks without self-rejecting submission language.",
    "Data and Code Availability names the exact release, repository, license, DOI archive if available, and excluded private/raw credentialed payloads.",
    "Archive-handoff manifest checksums match the final release assets and DOI-deposit asset set.",
    "Zenodo deposit preflight and any unpublished draft metadata match the signed-off release before a DOI record is published.",
    'References are complete enough for the target venue and do not contain placeholder or "planned validation" entries.',
    "AI Use Disclosure and declarations match journal expectations.",
    "The final release ZIP, PDFs, supplement, reports, and metadata match the signed-off release tag.",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--input", type=Path, help="Override final-human-readthrough.md path.")
    parser.add_argument("--output-csv", type=Path, help="Override CSV output path.")
    parser.add_argument("--output-md", type=Path, help="Override Markdown output path.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero on manual-required rows as well as blocked rows.")
    args = parser.parse_args()

    root = args.root.resolve()
    readthrough = args.input or root / "reports" / "final-human-readthrough.md"
    out_csv = args.output_csv or root / "reports" / "final-human-readthrough-audit.csv"
    out_md = args.output_md or root / "reports" / "final-human-readthrough-audit.md"

    rows = audit_rows(root, readthrough)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    write_csv(out_csv, rows)
    out_md.write_text(markdown(root, readthrough, rows), encoding="utf-8")
    print(f"Wrote {out_csv.relative_to(root) if out_csv.is_relative_to(root) else out_csv}")
    print(f"Wrote {out_md.relative_to(root) if out_md.is_relative_to(root) else out_md}")

    blocked = any(row["status"] == "blocked" for row in rows)
    manual = any(row["status"] == "manual_required" for row in rows)
    if blocked or (args.strict and manual):
        return 1
    return 0


def audit_rows(root: Path, path: Path) -> list[dict[str, str]]:
    text = read_text(path)
    release_tag = release_tag_from_citation(root)
    release_date = release_date_from_citation(root)
    fields = {name: field_value(text, name) for name in REQUIRED_FIELDS + SIGNOFF_FIELDS + LIVE_AUTHOR_PAGE_FIELDS}
    status = fields["status"].strip().lower()
    completed_status = status == "complete"
    rows: list[dict[str, str]] = []

    if not text:
        return [
            row(
                "overall-final-human-readthrough",
                "record",
                "blocked",
                f"file missing: {path}",
                "Restore reports/final-human-readthrough.md before final-submission readiness can be audited.",
            )
        ]

    rows.append(
        row(
            "status",
            "metadata",
            "ready" if status in {"pending", "complete"} else "blocked",
            f"status={status or 'missing'}",
            "Use status=pending for review-bundle circulation and status=complete only after all manual checks are signed.",
        )
    )
    for name in REQUIRED_FIELDS:
        if name == "status":
            continue
        value = fields[name]
        rows.append(required_field_row(name, value, release_tag))

    for name in SIGNOFF_FIELDS:
        value = fields[name]
        if completed_status:
            field_ready = bool(value)
            if name == "doi-archive":
                field_ready = bool(DOI_PATTERN.search(value))
            rows.append(
                row(
                    name,
                    "human-signoff",
                    "ready" if field_ready else "blocked",
                    f"{name}={'present' if value else 'missing'}",
                    "Complete all signoff fields before setting status=complete.",
                )
            )
        else:
            rows.append(
                row(
                    name,
                    "human-signoff",
                    "manual_required",
                    f"{name}={'present' if value else 'missing'}",
                    "Fill this field during the final human scholarly read-through.",
                )
            )

    for name in LIVE_AUTHOR_PAGE_FIELDS:
        value = fields[name]
        live_ready = bool(value)
        if name == "author-guidelines-superseding-instructions":
            live_ready = value.strip().lower() in NO_SUPERSEDING_VALUES
        elif name == "author-guidelines-checked-date":
            live_ready = live_author_check_date_ready(value, release_date)
        rows.append(
            row(
                name,
                "live-author-page",
                "ready" if live_ready else "blocked" if completed_status else "manual_required",
                live_evidence(name, value, release_date),
                "Recheck the live Regulation & Governance author page and record any superseding instructions before final submission.",
            )
        )

    checklist = checklist_items(text)
    rows.extend(checklist_rows("live-author-page-checklist", EXPECTED_LIVE_CHECKLIST, checklist, completed_status))
    rows.extend(checklist_rows("scholarly-readthrough-checklist", EXPECTED_SCHOLARLY_CHECKLIST, checklist, completed_status))
    rows.append(overall_row(rows, status, release_tag))
    return rows


def required_field_row(name: str, value: str, release_tag: str) -> dict[str, str]:
    if name == "reviewed-release":
        ready = bool(value) and value == release_tag
        evidence = f"reviewed-release={value or 'missing'}; expected-release={release_tag or 'missing'}"
        action = "Set reviewed-release to the current release tag before final signoff."
    elif name == "venue-target":
        ready = value == "Regulation & Governance"
        evidence = f"venue-target={value or 'missing'}"
        action = "Keep the venue target aligned with the Regulation & Governance manuscript template."
    elif name == "author-guidelines-url":
        ready = value == REGGOV_AUTHOR_GUIDELINES_URL
        evidence = f"url={'matches' if ready else value or 'missing'}"
        action = "Record the official Regulation & Governance author-guidelines URL."
    else:
        ready = bool(value)
        evidence = f"{name}={'present' if value else 'missing'}"
        action = "Fill the required field."
    return row(name, "metadata", "ready" if ready else "blocked", evidence, action)


def checklist_rows(
    category: str,
    expected_items: list[str],
    checklist: dict[str, bool],
    completed_status: bool,
) -> list[dict[str, str]]:
    rows = []
    for index, text in enumerate(expected_items, start=1):
        if text not in checklist:
            status = "blocked"
            evidence = "missing from final-human-readthrough.md"
            action = "Restore this checklist item before release handoff."
        elif checklist[text]:
            status = "ready"
            evidence = "checked"
            action = "Retain this checked item with the signed release record."
        else:
            status = "blocked" if completed_status else "manual_required"
            evidence = "unchecked"
            action = "Complete and check this item during the human scholarly read-through."
        rows.append(row(f"{category}-{index:02d}", category, status, evidence + f"; item={text}", action))
    return rows


def overall_row(rows: list[dict[str, str]], status: str, release_tag: str) -> dict[str, str]:
    blocked = [item for item in rows if item["status"] == "blocked"]
    manual = [item for item in rows if item["status"] == "manual_required"]
    checked = sum(1 for item in rows if item["category"].endswith("checklist") and item["status"] == "ready")
    total_checklist = len(EXPECTED_LIVE_CHECKLIST) + len(EXPECTED_SCHOLARLY_CHECKLIST)
    if blocked:
        final_status = "blocked"
        action = "Fix malformed or inconsistent read-through evidence before using this release for final submission."
    elif status == "complete" and not manual:
        final_status = "ready"
        action = "Human scholarly read-through is structurally complete for the release."
    else:
        final_status = "manual_required"
        action = "Complete unchecked scholarly items and signoff fields before final journal submission."
    evidence = (
        f"release={release_tag or 'missing'}; status={status or 'missing'}; "
        f"blocked={len(blocked)}; manual_required={len(manual)}; "
        f"checkedChecklistItems={checked}/{total_checklist}"
    )
    return row("overall-final-human-readthrough", "record", final_status, evidence, action)


def checklist_items(text: str) -> dict[str, bool]:
    items: dict[str, bool] = {}
    for match in re.finditer(r"^- \[([ xX])\] (.+?)\s*$", text, re.MULTILINE):
        items[match.group(2).strip()] = match.group(1).lower() == "x"
    return items


def live_evidence(name: str, value: str, release_date: date | None = None) -> str:
    if name == "author-guidelines-superseding-instructions":
        normalized = value.strip().lower()
        if normalized in NO_SUPERSEDING_VALUES:
            return "superseding-instructions=none"
        return f"superseding-instructions={value or 'missing'}"
    if name == "author-guidelines-checked-date":
        parsed = parse_iso_date(value)
        release = release_date.isoformat() if release_date else "missing"
        if not value:
            return f"checked-date=missing; release-date={release}"
        if not parsed:
            return f"checked-date=invalid:{value}; release-date={release}"
        stale = bool(release_date and parsed < release_date)
        return f"checked-date={parsed.isoformat()}; release-date={release}; stale={'yes' if stale else 'no'}"
    return f"{name}={'present' if value else 'missing'}"


def field_value(text: str, field_name: str) -> str:
    match = re.search(
        rf"^[^\S\n]*{re.escape(field_name)}[^\S\n]*:[^\S\n]*(.*?)[^\S\n]*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def release_tag_from_citation(root: Path) -> str:
    match = VERSION_PATTERN.search(read_text(root / "CITATION.cff"))
    return match.group(1).strip() if match else ""


def release_date_from_citation(root: Path) -> date | None:
    match = DATE_RELEASED_PATTERN.search(read_text(root / "CITATION.cff"))
    if not match:
        return None
    return parse_iso_date(match.group(1).strip())


def live_author_check_date_ready(value: str, release_date: date | None) -> bool:
    checked = parse_iso_date(value)
    if not checked:
        return False
    if release_date and checked < release_date:
        return False
    return True


def parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def row(item: str, category: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "item": item,
        "category": category,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["item", "category", "status", "evidence", "nextAction"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(root: Path, readthrough: Path, rows: list[dict[str, str]]) -> str:
    overall = rows[-1]
    counts: dict[str, int] = {}
    for item in rows:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    lines = [
        "# Final Human Read-Through Audit",
        "",
        "This deterministic audit turns the manual final-submission read-through record into structured rows. It may report manual-required items for a review bundle; it reports blocked items only when the record is malformed or internally inconsistent.",
        "",
        "## Summary",
        "",
        f"- Source: `{readthrough.relative_to(root) if readthrough.is_relative_to(root) else readthrough}`",
        f"- Overall status: `{overall['status']}`",
        f"- Evidence: {overall['evidence']}",
        f"- Ready rows: `{counts.get('ready', 0)}`",
        f"- Manual-required rows: `{counts.get('manual_required', 0)}`",
        f"- Blocked rows: `{counts.get('blocked', 0)}`",
        "",
        "## Audit Rows",
        "",
        "| Item | Category | Status | Evidence | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {item} | {category} | {status} | {evidence} | {nextAction} |".format(
                item=md(item["item"]),
                category=md(item["category"]),
                status=md(item["status"]),
                evidence=md(item["evidence"]),
                nextAction=md(item["nextAction"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
