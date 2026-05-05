#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
DIST_DIR="$ROOT_DIR/dist"
STAGING_DIR="$DIST_DIR/lobby-capture-wiley-submission"
ZIP_PATH="$DIST_DIR/lobby-capture-wiley-submission.zip"
TEMPLATE_DIR="$PAPER_DIR/.wiley-template/Optimal-Design-layout"
BUILD_DIR="$PAPER_DIR/.wiley-build"

if ! python3 - "$ROOT_DIR" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
paper = root / "paper"
pdf = paper / "regulation-governance-wiley.pdf"
build_class = paper / ".wiley-build" / "USG.cls"
inputs = [
    paper / "regulation-governance-wiley.tex",
    paper / "references.bib",
    root / "scripts" / "build-wiley-paper.sh",
    *sorted((paper / "sections").glob("*.tex")),
    *sorted((paper / "tables").glob("*.tex")),
    *sorted((paper / "figures").glob("*.tex")),
    *sorted((paper / "figures").glob("Figure_*.pdf")),
]
if not pdf.exists() or not build_class.exists():
    raise SystemExit(1)
pdf_mtime = pdf.stat().st_mtime
if any(path.exists() and path.stat().st_mtime > pdf_mtime + 1 for path in inputs):
    raise SystemExit(1)
PY
then
  "$ROOT_DIR/scripts/build-wiley-paper.sh"
fi

rm -rf "$STAGING_DIR" "$ZIP_PATH"
mkdir -p "$STAGING_DIR"

cp "$PAPER_DIR/regulation-governance-wiley.tex" "$STAGING_DIR/main.tex"
cp "$PAPER_DIR/regulation-governance-wiley.pdf" "$STAGING_DIR/main.pdf"
cp "$PAPER_DIR/references.bib" "$STAGING_DIR/references.bib"
cp -R "$PAPER_DIR/sections" "$STAGING_DIR/sections"
cp -R "$PAPER_DIR/tables" "$STAGING_DIR/tables"
mkdir -p "$STAGING_DIR/supporting-information"
cp "$ROOT_DIR/docs/odd-model.md" "$STAGING_DIR/supporting-information/ODD-model.md"
cp "$ROOT_DIR/docs/scenario-catalog.md" "$STAGING_DIR/supporting-information/scenario-catalog.md"
cp "$ROOT_DIR/docs/validation.md" "$STAGING_DIR/supporting-information/validation-plan.md"
cp "$ROOT_DIR/reports/source-moments.md" "$STAGING_DIR/supporting-information/source-moments.md"
cp "$ROOT_DIR/reports/validation-summary.md" "$STAGING_DIR/supporting-information/validation-summary.md"
cp "$ROOT_DIR/reports/substitution-audit.md" "$STAGING_DIR/supporting-information/substitution-audit.md"
cp "$ROOT_DIR/reports/calibration-queue.md" "$STAGING_DIR/supporting-information/calibration-queue.md"
mkdir -p "$STAGING_DIR/figures"
cp "$PAPER_DIR"/figures/Figure_*.pdf "$STAGING_DIR/figures/"
cp "$PAPER_DIR"/figures/*.tex "$STAGING_DIR/figures/"

cp "$BUILD_DIR/USG.cls" "$STAGING_DIR/USG.cls"
find "$TEMPLATE_DIR" -maxdepth 1 -type f \( -iname '*.sty' -o -iname '*.bst' \) -exec cp {} "$STAGING_DIR/" \;
cp "$BUILD_DIR/wileyNJD-Chicago.bst" "$STAGING_DIR/wileyNJD-Chicago.bst"
if [ -f "$STAGING_DIR/LETTERSP.STY" ]; then
  mv "$STAGING_DIR/LETTERSP.STY" "$STAGING_DIR/lettersp.sty.tmp"
  mv "$STAGING_DIR/lettersp.sty.tmp" "$STAGING_DIR/lettersp.sty"
elif [ -f "$TEMPLATE_DIR/LETTERSP.STY" ]; then
  cp "$TEMPLATE_DIR/LETTERSP.STY" "$STAGING_DIR/lettersp.sty"
fi
if [ ! -f "$STAGING_DIR/lettersp.sty" ]; then
  printf 'Missing lettersp.sty in Wiley submission staging directory.\n' >&2
  exit 2
fi
mkdir -p "$STAGING_DIR/images"
cp "$TEMPLATE_DIR/images/Wiley_logo.eps" "$STAGING_DIR/images/"

cat > "$STAGING_DIR/SUBMISSION_README.txt" <<'EOF'
Lobby Capture Simulator Wiley LaTeX submission package

Root manuscript: main.tex
Compiled PDF: main.pdf

The included USG.cls is a generated copy of Wiley's USG class with template sample journal art and the generic Open Access badge removed for neutral peer-review rendering. The downloaded Wiley template remains unmodified in the repository.

Supporting information: supporting-information/

Compile from this directory with:
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
EOF

(cd "$STAGING_DIR" && zip -qr "$ZIP_PATH" .)
printf 'Wrote %s\n' "$ZIP_PATH"
