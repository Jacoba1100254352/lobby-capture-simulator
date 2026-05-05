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
python3 - "$WILEY_DIR/USG.cls" "$WILEY_BUILD_DIR/USG.cls" <<'PY'
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")

# The Wiley bundle is a generic authoring template, but USG.cls currently
# hard-codes sample journal art and an Open Access badge into the title page.
# Patch only the generated build copy so the downloaded template remains intact.
text = re.sub(
    r"\n\s*\\node\[anchor=north east,inner sep=0mm\]\s*\n\s*"
    r"\(LOG1\) at \(\[yshift=-11\.75mm\]current page header area\.north east\)"
    r"\{\\includegraphics\[width=56mm\]\{allergy\.eps\}\};",
    "\n",
    text,
)
text = text.replace(
    r"  \raisebox{-2\@p@t}{\includegraphics[width=0.70in]{images/openaccess}}%",
    r"  % Open Access badge removed for neutral peer-review draft.%",
)
text = text.replace(
    r"{\it \@journal}, \@copyyear;v\@volume:\@FirstPg--\@LastPg%",
    r"{\it \@journal}\ peer-review manuscript%",
)
text = text.replace(
    r"\href{https://doi.org/\thearticledoi}{https://doi.org/\thearticledoi}",
    r"\phantom{https://doi.org/}",
)
text = text.replace(
    "\\ProcessOptions\n\\LoadClass[fleqn,twoside]{article}%",
    "\\ProcessOptions\n\\def\\@classoptionslist{}%\n\\LoadClass[fleqn,twoside]{article}%\n\\let\\@unusedoptionlist\\@empty%",
)
text = text.replace(
    "\\historydates{{\\FIfont%\\titlepageheadfont%\n"
    "  \\ifx\\@received\\@empty\\@dummy@received\\else\\@dummy@received\\authorsep\\fi%\n"
    "  \\ifx\\@revised\\@empty\\@dummy@revised\\else\\@dummy@revised\\authorsep\\fi%\n"
    "  \\ifx\\@accepted\\@empty\\@dummy@accepted\\else\\@dummy@accepted\\fi%\n"
    "%  \\ifx\\@pubdate\\@empty\\@dummy@pubdate\\else\\@pubdate\\fi%\n"
    "}}%",
    "\\historydates{}%",
)
if "allergy.eps" in text:
    raise SystemExit("patched Wiley class still references allergy.eps")
if "Received:" in text and "\\historydates{}%" not in text:
    raise SystemExit("patched Wiley class still emits placeholder history dates")
target.write_text(text, encoding="utf-8")
PY

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
  rm -f "$PAPER_DIR"/*-eps-converted-to.pdf
}
trap cleanup EXIT HUP INT TERM

cd "$PAPER_DIR"
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
bibtex regulation-governance-wiley
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
TEXINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
BIBINPUTS=".:.wiley-template/Optimal-Design-layout//:" \
BSTINPUTS=".wiley-build//:.wiley-template/Optimal-Design-layout//:" \
pdflatex -interaction=nonstopmode regulation-governance-wiley.tex
