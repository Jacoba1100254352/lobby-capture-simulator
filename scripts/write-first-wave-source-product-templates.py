#!/usr/bin/env python3
"""Write acquisition templates for first-wave source products."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from typing import Any


ROOT = Path(".")
TEMPLATE_ROOT = Path("docs/source-product-templates/first-wave")
AUDIT_SCRIPT = Path(__file__).with_name("audit-first-wave-source-products.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=TEMPLATE_ROOT)
    args = parser.parse_args()

    products = load_products()
    output = args.root / args.output
    output.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, str]] = []
    for spec in products:
        template_path = output / Path(spec.expected_path).name
        if spec.required_columns:
            write_csv_template(template_path, spec)
            template_type = "csv_header_template"
        else:
            write_text_template(template_path, spec)
            template_type = "markdown_design_note_template"
        manifest_rows.append(manifest_row(args.output / template_path.name, spec, template_type))

    write_manifest_csv(output / "manifest.csv", manifest_rows)
    write_manifest_markdown(output / "manifest.md", manifest_rows)
    write_readme(output / "README.md", manifest_rows)
    print(f"Wrote first-wave source-product templates under {output}")
    return 0


def load_products() -> tuple[Any, ...]:
    spec = importlib.util.spec_from_file_location("first_wave_source_product_audit", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {AUDIT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.PRODUCTS


def write_csv_template(path: Path, spec: Any) -> None:
    fieldnames = [*spec.required_columns, *spec.optional_columns]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination, lineterminator="\n")
        writer.writerow(fieldnames)


def write_text_template(path: Path, spec: Any) -> None:
    terms = ", ".join(spec.text_required_terms)
    text = f"""# {spec.label.title()} Template

Production path: `{spec.expected_path}`
Required terms for the production note: {terms}

This template is an acquisition aid only. The production note must explain the actual source search, source availability, missingness pattern, and substitution-handling decision before this product can clear the source-product gate.

## Meeting Or Contact Source Availability

Describe the meeting logs, contact registers, calendars, visitor logs, or equivalent source surfaces reviewed.

## Missingness Assessment

Describe source gaps, unavailable records, coverage periods, actor/agency exclusions, and why the missing channel cannot be observed directly in the present product.

## Substitution Handling

Explain how the omitted or partial meeting/contact channel is handled in substitution estimates and what sensitivity check is required before promoting the protocol.

## Provenance

- Source URLs:
- Extracted at:
- Reviewer:
- Notes:
"""
    path.write_text(text, encoding="utf-8")


def manifest_row(template_path: Path, spec: Any, template_type: str) -> dict[str, str]:
    required = "; ".join(spec.required_columns) if spec.required_columns else "text terms: " + "; ".join(spec.text_required_terms)
    return {
        "targetKey": spec.target_key,
        "productKey": spec.product_key,
        "productLabel": spec.label,
        "priority": spec.priority,
        "templateType": template_type,
        "templatePath": template_path.as_posix(),
        "productionPath": spec.expected_path,
        "requiredColumnsOrTerms": required,
        "optionalColumns": "; ".join(spec.optional_columns),
        "minimumRows": str(spec.minimum_rows),
        "semanticChecks": "; ".join(spec.semantic_checks),
        "acceptableSources": spec.acceptable_sources,
        "validationRule": spec.validation_rule,
        "claimBoundary": spec.claim_boundary,
        "nextAction": spec.next_action,
    }


def write_manifest_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "targetKey",
        "productKey",
        "productLabel",
        "priority",
        "templateType",
        "templatePath",
        "productionPath",
        "requiredColumnsOrTerms",
        "optionalColumns",
        "minimumRows",
        "semanticChecks",
        "acceptableSources",
        "validationRule",
        "claimBoundary",
        "nextAction",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_manifest_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# First-Wave Source Product Template Manifest",
        "",
        "These templates are acquisition scaffolds for the first-wave source-product gate. They are intentionally stored under `docs/source-product-templates/first-wave/` rather than `data/calibration/first-wave/` so they cannot satisfy the production source-product audit.",
        "",
        "| Target | Product | Template | Production path | Required schema or terms | Minimum rows | Semantic checks | Next action |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {targetKey} | {productLabel} | `{templatePath}` | `{productionPath}` | {requiredColumnsOrTerms} | {minimumRows} | {semanticChecks} | {nextAction} |".format(
                **{key: md(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_readme(path: Path, rows: list[dict[str, str]]) -> None:
    csv_count = sum(1 for row in rows if row["templateType"] == "csv_header_template")
    text_count = sum(1 for row in rows if row["templateType"] == "markdown_design_note_template")
    text = f"""# First-Wave Source Product Templates

These files are acquisition templates for the source products named by `reports/first-wave-source-products.md`.

- Template products: `{len(rows)}`
- CSV header templates: `{csv_count}`
- Markdown design-note templates: `{text_count}`
- Production source-product directory: `data/calibration/first-wave/`

Do not treat these templates as evidence. They are stored under `docs/source-product-templates/first-wave/` so the production audit continues to require real source files with rows, provenance, protocol-specific coverage, field-level quality checks, and product-level semantic gates. Partial reviewed files can narrow the work queue, but they do not clear the gate until minimum-row and product-specific semantic checks pass.

Regenerate this directory with:

```sh
make first-wave-source-product-templates
```

Use `manifest.csv` or `manifest.md` to map each template to its production path, required schema, minimum-row rule, semantic gate, acceptable source families, field-level quality checks, and claim boundary.
"""
    path.write_text(text, encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
