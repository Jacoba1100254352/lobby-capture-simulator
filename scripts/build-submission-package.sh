#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
DIST_DIR="$ROOT_DIR/dist"
STAGING_DIR="$DIST_DIR/lobby-capture-wiley-submission"
ZIP_PATH="$DIST_DIR/lobby-capture-wiley-submission.zip"
TEMPLATE_DIR="$PAPER_DIR/.wiley-template/Optimal-Design-layout"
BUILD_DIR="$PAPER_DIR/.wiley-build"

if [ ! -f "$PAPER_DIR/regulation-governance-wiley.pdf" ]; then
  "$ROOT_DIR/scripts/build-wiley-paper.sh"
fi

rm -rf "$STAGING_DIR" "$ZIP_PATH"
mkdir -p "$STAGING_DIR"

cp "$PAPER_DIR/regulation-governance-wiley.tex" "$STAGING_DIR/main.tex"
cp "$PAPER_DIR/regulation-governance-wiley.pdf" "$STAGING_DIR/main.pdf"
cp "$PAPER_DIR/references.bib" "$STAGING_DIR/references.bib"
cp -R "$PAPER_DIR/sections" "$STAGING_DIR/sections"
cp -R "$PAPER_DIR/tables" "$STAGING_DIR/tables"
mkdir -p "$STAGING_DIR/figures"
cp "$PAPER_DIR"/figures/Figure_*.pdf "$STAGING_DIR/figures/"
cp "$PAPER_DIR"/figures/*.tex "$STAGING_DIR/figures/"

cp "$BUILD_DIR/USG.cls" "$STAGING_DIR/USG.cls"
cp "$BUILD_DIR/wileyNJD-Chicago.bst" "$STAGING_DIR/wileyNJD-Chicago.bst"
find "$TEMPLATE_DIR" -maxdepth 1 -type f \( -name '*.sty' -o -name '*.bst' \) -exec cp {} "$STAGING_DIR/" \;
mkdir -p "$STAGING_DIR/images"
cp "$TEMPLATE_DIR/images/Wiley_logo.eps" "$STAGING_DIR/images/"

cat > "$STAGING_DIR/SUBMISSION_README.txt" <<'EOF'
Lobby Capture Simulator Wiley LaTeX submission package

Root manuscript: main.tex
Compiled PDF: main.pdf

The included USG.cls is a generated copy of Wiley's USG class with template sample journal art and the generic Open Access badge removed for neutral peer-review rendering. The downloaded Wiley template remains unmodified in the repository.

Compile from this directory with:
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
EOF

(cd "$DIST_DIR" && zip -qr "$(basename "$ZIP_PATH")" "$(basename "$STAGING_DIR")")
printf 'Wrote %s\n' "$ZIP_PATH"
