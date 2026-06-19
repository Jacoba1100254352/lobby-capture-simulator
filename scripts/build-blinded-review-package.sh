#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
DIST_DIR="$ROOT_DIR/dist"
STAGING_DIR="$DIST_DIR/lobby-capture-wiley-blinded-review"
ZIP_PATH="$DIST_DIR/lobby-capture-wiley-blinded-review.zip"
TEMPLATE_DIR="$PAPER_DIR/.wiley-template/Optimal-Design-layout"
BUILD_DIR="$PAPER_DIR/.wiley-build"
BLIND_BASENAME="strategic-channel-substitution-regulatory-capture-blinded"
export TZ=UTC
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1777939200}"
export FORCE_SOURCE_DATE="${FORCE_SOURCE_DATE:-1}"

resolve_binary() {
  name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi
  for dir in \
    /usr/local/texlive/2026basic/bin/universal-darwin \
    /usr/local/texlive/2025basic/bin/universal-darwin \
    /Library/TeX/texbin \
    /opt/homebrew/bin \
    /usr/local/bin; do
    if [ -x "$dir/$name" ]; then
      printf '%s\n' "$dir/$name"
      return 0
    fi
  done
  printf 'Required binary not found: %s\n' "$name" >&2
  return 1
}

PDFLATEX="$(resolve_binary pdflatex)"
BIBTEX="$(resolve_binary bibtex)"

if [ ! -f "$BUILD_DIR/USG.cls" ] || [ ! -f "$BUILD_DIR/wileyNJD-Chicago.bst" ]; then
  "$ROOT_DIR/scripts/build-wiley-paper.sh"
fi

if [ ! -f "$BUILD_DIR/USG.cls" ] || [ ! -f "$BUILD_DIR/wileyNJD-Chicago.bst" ]; then
  printf 'Missing generated Wiley class or bibliography style after build.\n' >&2
  exit 2
fi

if [ ! -f "$PAPER_DIR/regulation-governance-wiley-anonymous.tex" ]; then
  printf 'Missing anonymous Wiley wrapper.\n' >&2
  exit 2
fi

cd "$PAPER_DIR"
rm -f regulation-governance-wiley-anonymous.aux \
  regulation-governance-wiley-anonymous.bbl \
  regulation-governance-wiley-anonymous.blg \
  regulation-governance-wiley-anonymous.log \
  regulation-governance-wiley-anonymous.out \
  regulation-governance-wiley-anonymous.pag \
  regulation-governance-wiley-anonymous.pdf \
  supplement-anonymous.aux \
  supplement-anonymous.log \
  supplement-anonymous.out \
  supplement-anonymous.pdf \
  regulation-governance-title-page.aux \
  regulation-governance-title-page.log \
  regulation-governance-title-page.out \
  regulation-governance-title-page.pdf

TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
"$PDFLATEX" -interaction=nonstopmode regulation-governance-wiley-anonymous.tex
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
"$BIBTEX" regulation-governance-wiley-anonymous
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
"$PDFLATEX" -interaction=nonstopmode regulation-governance-wiley-anonymous.tex
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
"$PDFLATEX" -interaction=nonstopmode regulation-governance-wiley-anonymous.tex
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
"$PDFLATEX" -interaction=nonstopmode regulation-governance-wiley-anonymous.tex
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
"$PDFLATEX" -interaction=nonstopmode regulation-governance-wiley-anonymous.tex

"$PDFLATEX" -interaction=nonstopmode supplement-anonymous.tex
"$PDFLATEX" -interaction=nonstopmode supplement-anonymous.tex
"$PDFLATEX" -interaction=nonstopmode regulation-governance-title-page.tex
"$PDFLATEX" -interaction=nonstopmode regulation-governance-title-page.tex

rm -rf "$STAGING_DIR" "$ZIP_PATH"
mkdir -p "$STAGING_DIR"

cp "$PAPER_DIR/regulation-governance-wiley-anonymous.tex" "$STAGING_DIR/$BLIND_BASENAME.tex"
cp "$PAPER_DIR/regulation-governance-wiley-anonymous.pdf" "$STAGING_DIR/$BLIND_BASENAME.pdf"
cp "$PAPER_DIR/supplement-anonymous.tex" "$STAGING_DIR/supplement-blinded.tex"
cp "$PAPER_DIR/supplement-anonymous.pdf" "$STAGING_DIR/supplement-blinded.pdf"
cp "$PAPER_DIR/regulation-governance-title-page.tex" "$STAGING_DIR/title-page.tex"
cp "$PAPER_DIR/regulation-governance-title-page.pdf" "$STAGING_DIR/title-page.pdf"
cp "$PAPER_DIR/references.bib" "$STAGING_DIR/references.bib"
cp -R "$PAPER_DIR/sections" "$STAGING_DIR/sections"

python3 - "$PAPER_DIR/sections/submission-declarations.tex" "$STAGING_DIR/sections/submission-declarations.tex" <<'PY'
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")
pattern = re.compile(r"\\ifdefined\\blindreview\n(?P<blind>.*?)\n\\else\n.*?\n\\fi", re.DOTALL)

def replace(match: re.Match[str]) -> str:
    return match.group("blind")

redacted, count = pattern.subn(replace, text, count=1)
if count != 1:
    raise SystemExit("Could not redact blind-review branch in submission declarations")
for token in ("Jacob Anderson", "jacobdanderson", "Jacoba1100254352", "github.com/Jacoba1100254352"):
    if token in redacted:
        raise SystemExit(f"Redacted declarations still contain identifying token: {token}")
target.write_text(redacted, encoding="utf-8")
PY

cp -R "$PAPER_DIR/tables" "$STAGING_DIR/tables"
mkdir -p "$STAGING_DIR/figures"
cp "$PAPER_DIR"/figures/Figure_*.pdf "$STAGING_DIR/figures/"
cp "$PAPER_DIR"/figures/Figure_*.svg "$STAGING_DIR/figures/"
cp "$PAPER_DIR"/figures/*.tex "$STAGING_DIR/figures/"

mkdir -p "$STAGING_DIR/supporting-information"
cp "$ROOT_DIR/docs/odd-model.md" "$STAGING_DIR/supporting-information/ODD-model.md"
cp "$ROOT_DIR/docs/scenario-catalog.md" "$STAGING_DIR/supporting-information/scenario-catalog.md"
cp "$ROOT_DIR/docs/validation.md" "$STAGING_DIR/supporting-information/validation-plan.md"
cp "$ROOT_DIR/docs/source-data-roadmap.md" "$STAGING_DIR/supporting-information/source-data-roadmap.md"

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
  printf 'Missing lettersp.sty in blinded review staging directory.\n' >&2
  exit 2
fi
mkdir -p "$STAGING_DIR/images"
cp "$TEMPLATE_DIR/images/Wiley_logo.eps" "$STAGING_DIR/images/"

cat > "$STAGING_DIR/BLINDED_REVIEW_README.txt" <<EOF
Lobby Capture Simulator blinded review package

Anonymous main manuscript: $BLIND_BASENAME.tex
Anonymous main PDF: $BLIND_BASENAME.pdf
Anonymous supplement: supplement-blinded.tex and supplement-blinded.pdf
Separate title page: title-page.tex and title-page.pdf

The main manuscript and supplement are rendered with author and public repository
identifiers withheld for double-anonymized review. The title page is separate
and contains author/correspondence information for editorial office use.

Compile from this directory with:
export TZ=UTC SOURCE_DATE_EPOCH=1777939200 FORCE_SOURCE_DATE=1
pdflatex -interaction=nonstopmode $BLIND_BASENAME.tex
bibtex $BLIND_BASENAME
pdflatex -interaction=nonstopmode $BLIND_BASENAME.tex
pdflatex -interaction=nonstopmode $BLIND_BASENAME.tex
pdflatex -interaction=nonstopmode $BLIND_BASENAME.tex
pdflatex -interaction=nonstopmode $BLIND_BASENAME.tex
pdflatex -interaction=nonstopmode supplement-blinded.tex
pdflatex -interaction=nonstopmode supplement-blinded.tex
pdflatex -interaction=nonstopmode title-page.tex
pdflatex -interaction=nonstopmode title-page.tex
EOF

python3 "$ROOT_DIR/scripts/write-blinded-review-package-manifest.py" "$STAGING_DIR" "$ROOT_DIR"
python3 - "$STAGING_DIR" "$ZIP_PATH" <<'PY'
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

staging = Path(sys.argv[1])
zip_path = Path(sys.argv[2])
fixed_timestamp = (2026, 5, 5, 0, 0, 0)
paths = sorted(
    (path for path in staging.rglob("*") if path.is_file()),
    key=lambda path: path.relative_to(staging).as_posix(),
)
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in paths:
        relative = path.relative_to(staging).as_posix()
        info = zipfile.ZipInfo(relative, fixed_timestamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        mode = 0o755 if os.access(path, os.X_OK) else 0o644
        info.external_attr = mode << 16
        archive.writestr(info, path.read_bytes())
PY
rm -rf "$STAGING_DIR"
printf 'Wrote %s\n' "$ZIP_PATH"
