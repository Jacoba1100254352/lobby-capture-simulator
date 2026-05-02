#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
WILEY_DIR="$PAPER_DIR/.wiley-template/Optimal-Design-layout"

if [ ! -f "$WILEY_DIR/USG.cls" ]; then
  "$ROOT_DIR/scripts/fetch-wiley-template.sh"
fi

missing=""
for package in dashrule.sty multirow.sty cuted.sty floatpag.sty dblfloatfix.sty soul.sty xargs.sty tcolorbox.sty varwidth.sty tikzpagenodes.sty boites.sty wrapfig.sty; do
  if ! kpsewhich "$package" >/dev/null 2>&1; then
    missing="$missing $package"
  fi
done

if [ -n "$missing" ]; then
  printf 'Wiley template fetched, but the local TeX install is missing:%s\n' "$missing" >&2
  printf 'Install a fuller TeX Live distribution or the missing packages, then rerun make paper-wiley.\n' >&2
  exit 2
fi

cd "$PAPER_DIR"
TEXINPUTS=".wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
bibtex regulation-governance-wiley
TEXINPUTS=".wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
TEXINPUTS=".wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
