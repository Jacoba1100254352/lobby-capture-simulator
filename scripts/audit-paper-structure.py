#!/usr/bin/env python3
"""Audit LaTeX figure/table structure beyond PDF layout density.

This report checks the manuscript and supplement source for structural issues
that automated PDF layout checks do not cover: duplicate labels, missing
figure/table labels, mismatched Figure/Table references, out-of-order first
references, and duplicate captions.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
REPORTS = ROOT / "reports"
OUTPUT_CSV = REPORTS / "paper-structure-audit.csv"
OUTPUT_MD = REPORTS / "paper-structure-audit.md"

ENTRYPOINTS = [
    ("main", PAPER / "strategic-channel-substitution-regulatory-capture.tex"),
    ("wiley", PAPER / "regulation-governance-wiley.tex"),
    ("supplement", PAPER / "supplement.tex"),
]

INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\b(Figure|Table)~\\ref\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption(?:\[[^\]]*\])?\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", re.DOTALL)


@dataclass(frozen=True)
class SourceDoc:
    name: str
    path: Path
    text: str


def main() -> int:
    rows: list[dict[str, str]] = []
    for name, path in ENTRYPOINTS:
        if not path.exists():
            rows.append(row(name, "entrypoint", "fail", str(path.relative_to(ROOT)), "Missing LaTeX entrypoint."))
            continue
        doc = SourceDoc(name=name, path=path, text=expand_inputs(path))
        rows.extend(audit_doc(doc))

    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown(rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 1 if any(item["status"] == "fail" for item in rows) else 0


def expand_inputs(path: Path, seen: set[Path] | None = None) -> str:
    seen = seen or set()
    resolved = path.resolve()
    if resolved in seen:
        return f"\n% skipped recursive input: {path}\n"
    seen.add(resolved)
    text = path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        input_path = resolve_input(match.group(1), path)
        if not input_path or not input_path.exists():
            return f"\n% missing input: {match.group(1)}\n"
        return "\n" + expand_inputs(input_path, seen) + "\n"

    return INPUT_RE.sub(replace, text)


def resolve_input(name: str, current: Path) -> Path | None:
    candidate = name if name.endswith(".tex") else f"{name}.tex"
    candidates = [
        PAPER / candidate,
        current.parent / candidate,
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def audit_doc(doc: SourceDoc) -> list[dict[str, str]]:
    labels = collect_labels(doc.text)
    refs = collect_refs(doc.text)
    captions = collect_captions(doc.text)
    rows: list[dict[str, str]] = []

    duplicate_labels = sorted(label for label, positions in labels.items() if len(positions) > 1)
    rows.append(
        row(
            doc.name,
            "duplicate-labels",
            "fail" if duplicate_labels else "pass",
            "; ".join(duplicate_labels) or "none",
            "Ensure every LaTeX label is unique within the expanded source.",
        )
    )

    missing_refs = [label for _kind, label, _pos in refs if label not in labels]
    rows.append(
        row(
            doc.name,
            "missing-reference-labels",
            "fail" if missing_refs else "pass",
            "; ".join(sorted(set(missing_refs))) or "none",
            "Define each referenced table or figure label.",
        )
    )

    mismatches = [
        f"{kind}~\\ref{{{label}}}"
        for kind, label, _pos in refs
        if (kind == "Figure" and not label.startswith("fig:"))
        or (kind == "Table" and not label.startswith("tab:"))
    ]
    rows.append(
        row(
            doc.name,
            "reference-prefixes",
            "fail" if mismatches else "pass",
            "; ".join(mismatches) or "all Figure/Table references use matching label prefixes",
            "Use Figure references only for fig: labels and Table references only for tab: labels.",
        )
    )

    rows.append(first_reference_order_row(doc, "fig", refs, labels))
    rows.append(first_reference_order_row(doc, "tab", refs, labels))

    duplicate_captions = sorted(caption for caption, count in captions.items() if count > 1)
    rows.append(
        row(
            doc.name,
            "duplicate-captions",
            "fail" if duplicate_captions else "pass",
            "; ".join(duplicate_captions) or "none",
            "Keep repeated floats from carrying duplicate captions in the same expanded source.",
        )
    )

    figure_labels = sorted(label for label in labels if label.startswith("fig:"))
    table_labels = sorted(label for label in labels if label.startswith("tab:"))
    referenced = {label for _kind, label, _pos in refs}
    unreferenced = sorted(label for label in figure_labels + table_labels if label not in referenced)
    rows.append(
        row(
            doc.name,
            "unreferenced-floats",
            "info",
            "; ".join(unreferenced) or "none",
            "Included but unreferenced floats are allowed in supporting material; inspect if the main article grows.",
        )
    )
    rows.append(
        row(
            doc.name,
            "summary",
            "info",
            f"figures={len(figure_labels)}; tables={len(table_labels)}; references={len(refs)}",
            "Use this count to spot accidental float drift after manuscript edits.",
        )
    )
    return rows


def collect_labels(text: str) -> dict[str, list[int]]:
    labels: dict[str, list[int]] = {}
    for match in LABEL_RE.finditer(text):
        labels.setdefault(match.group(1), []).append(match.start())
    return labels


def collect_refs(text: str) -> list[tuple[str, str, int]]:
    return [(match.group(1), match.group(2), match.start()) for match in REF_RE.finditer(text)]


def collect_captions(text: str) -> dict[str, int]:
    captions: dict[str, int] = {}
    for match in CAPTION_RE.finditer(text):
        caption = normalize_caption(match.group(1))
        if caption:
            captions[caption] = captions.get(caption, 0) + 1
    return captions


def normalize_caption(value: str) -> str:
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r"\1", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def first_reference_order_row(
    doc: SourceDoc,
    prefix: str,
    refs: list[tuple[str, str, int]],
    labels: dict[str, list[int]],
) -> dict[str, str]:
    kind = "Figure" if prefix == "fig" else "Table"
    first_refs: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for ref_kind, label, ref_pos in refs:
        if ref_kind != kind or not label.startswith(f"{prefix}:") or label in seen or label not in labels:
            continue
        seen.add(label)
        first_refs.append((labels[label][0], ref_pos, label))
    order = [label for _label_pos, _ref_pos, label in first_refs]
    expected = [label for _label_pos, _ref_pos, label in sorted(first_refs)]
    inversions = []
    for index, label in enumerate(order):
        if index < len(expected) and label != expected[index]:
            inversions.append(f"expected {expected[index]} before {label}")
    return row(
        doc.name,
        f"{prefix}-first-reference-order",
        "fail" if inversions else "pass",
        "; ".join(inversions) or f"{kind.lower()} first references follow source order",
        f"Reference {kind.lower()}s in the order they appear in the expanded source.",
    )


def row(document: str, check: str, status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "document": document,
        "check": check,
        "status": status,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["document", "check", "status", "evidence", "nextAction"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    failures = [item for item in rows if item["status"] == "fail"]
    lines = [
        "# Paper Structure Audit",
        "",
        "This audit checks expanded LaTeX sources for figure/table reference structure. It complements the PDF layout audit by checking labels, references, captions, and first-reference order before final visual review.",
        "",
        f"- Rows: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        "",
        "| Document | Check | Status | Evidence | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            "| {document} | {check} | {status} | {evidence} | {nextAction} |".format(
                document=md(item["document"]),
                check=md(item["check"]),
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
