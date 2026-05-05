#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
WILEY_DIR="$PAPER_DIR/.wiley-template/Optimal-Design-layout"
WILEY_BUILD_DIR="$PAPER_DIR/.wiley-build"

if [ ! -f "$WILEY_DIR/USG.cls" ]; then
  "$ROOT_DIR/scripts/fetch-wiley-template.sh"
fi

missing=""
for sty in dashrule.sty multirow.sty cuted.sty floatpag.sty dblfloatfix.sty soul.sty xargs.sty tcolorbox.sty varwidth.sty tikzpagenodes.sty boites.sty wrapfig.sty footmisc.sty stix2.sty ifoddpage.sty algpseudocode.sty; do
  if ! kpsewhich "$sty" >/dev/null 2>&1; then
    missing="$missing $sty"
  fi
done

if [ -n "$missing" ]; then
  printf 'Wiley template fetched, but the local TeX install is missing:%s\n' "$missing" >&2
  printf 'Run make wiley-tex-deps, or install a fuller TeX Live distribution, then rerun make paper-wiley.\n' >&2
  exit 2
fi

mkdir -p "$WILEY_BUILD_DIR"
# The current Wiley archive ships a primary Chicago .bst that errors on
# TeX Live 2026; its bundled "-lastoo" fallback is BibTeX-clean. The class
# hard-codes the primary filename, so expose the fallback under that name
# in a generated build directory that appears first in BSTINPUTS.
cp "$WILEY_DIR/wileyNJD-Chicago-lastoo.bst" "$WILEY_BUILD_DIR/wileyNJD-Chicago.bst"

for eps in "$WILEY_DIR"/images/*.eps; do
  base=$(basename "$eps")
  cp "$eps" "$PAPER_DIR/$base"
done
cleanup() {
  for eps in "$WILEY_DIR"/images/*.eps; do
    rm -f "$PAPER_DIR/$(basename "$eps")"
  done
}
trap cleanup EXIT HUP INT TERM

cd "$PAPER_DIR"
TEXINPUTS=".wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
bibtex regulation-governance-wiley
TEXINPUTS=".wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
TEXINPUTS=".wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
