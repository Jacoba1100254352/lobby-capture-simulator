# First-Wave Source Product Templates

These files are acquisition templates for the source products named by `reports/first-wave-source-products.md`.

- Template products: `16`
- CSV header templates: `15`
- Markdown design-note templates: `1`
- Production source-product directory: `data/calibration/first-wave/`

Do not treat these templates as evidence. They are stored under `docs/source-product-templates/first-wave/` so the production audit continues to require real source files with rows, provenance, protocol-specific coverage, field-level quality checks, and product-level semantic gates.

Regenerate this directory with:

```sh
make first-wave-source-product-templates
```

Use `manifest.csv` or `manifest.md` to map each template to its production path, required schema, minimum-row rule, semantic gate, acceptable source families, field-level quality checks, and claim boundary.
