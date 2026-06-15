#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
DIST_DIR="$ROOT_DIR/dist"
STAGING_DIR="$DIST_DIR/lobby-capture-wiley-submission"
ZIP_PATH="$DIST_DIR/lobby-capture-wiley-submission.zip"
TEMPLATE_DIR="$PAPER_DIR/.wiley-template/Optimal-Design-layout"
BUILD_DIR="$PAPER_DIR/.wiley-build"
SUBMISSION_BASENAME="strategic-channel-substitution-regulatory-capture"

if ! python3 - "$ROOT_DIR" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
paper = root / "paper"
pdf = paper / "regulation-governance-wiley.pdf"
supplement_pdf = paper / "supplement.pdf"
build_class = paper / ".wiley-build" / "USG.cls"
inputs = [
    paper / "regulation-governance-wiley.tex",
    paper / "supplement.tex",
    paper / "references.bib",
    root / "scripts" / "build-wiley-paper.sh",
    *sorted((paper / "sections").glob("*.tex")),
    *sorted((paper / "tables").glob("*.tex")),
    *sorted((paper / "figures").glob("*.tex")),
    *sorted((paper / "figures").glob("Figure_*.pdf")),
]
if not pdf.exists() or not supplement_pdf.exists() or not build_class.exists():
    raise SystemExit(1)
pdf_mtime = pdf.stat().st_mtime
if any(path.exists() and path.stat().st_mtime > pdf_mtime + 1 for path in inputs):
    raise SystemExit(1)
PY
then
  "$ROOT_DIR/scripts/build-wiley-paper.sh"
fi

if [ ! -f "$PAPER_DIR/supplement.pdf" ]; then
  (cd "$PAPER_DIR" && pdflatex -interaction=nonstopmode supplement.tex && pdflatex -interaction=nonstopmode supplement.tex)
fi

if [ -d "$DIST_DIR" ]; then
  find "$DIST_DIR" -maxdepth 1 -type f -name 'lobby-capture-wiley-submission [0-9]*.zip' -exec rm -f {} +
fi
rm -rf "$STAGING_DIR" "$ZIP_PATH"
mkdir -p "$STAGING_DIR"

cp "$PAPER_DIR/regulation-governance-wiley.tex" "$STAGING_DIR/$SUBMISSION_BASENAME.tex"
cp "$PAPER_DIR/regulation-governance-wiley.pdf" "$STAGING_DIR/$SUBMISSION_BASENAME.pdf"
cp "$PAPER_DIR/supplement.tex" "$STAGING_DIR/supplement.tex"
cp "$PAPER_DIR/supplement.pdf" "$STAGING_DIR/supplement.pdf"
cp "$PAPER_DIR/references.bib" "$STAGING_DIR/references.bib"
cp -R "$PAPER_DIR/sections" "$STAGING_DIR/sections"
cp -R "$PAPER_DIR/tables" "$STAGING_DIR/tables"
mkdir -p "$STAGING_DIR/supporting-information"
cp "$ROOT_DIR/docs/odd-model.md" "$STAGING_DIR/supporting-information/ODD-model.md"
cp "$ROOT_DIR/docs/scenario-catalog.md" "$STAGING_DIR/supporting-information/scenario-catalog.md"
cp "$ROOT_DIR/docs/validation.md" "$STAGING_DIR/supporting-information/validation-plan.md"
cp "$ROOT_DIR/docs/source-data-roadmap.md" "$STAGING_DIR/supporting-information/source-data-roadmap.md"
cp "$ROOT_DIR/reports/source-moments.md" "$STAGING_DIR/supporting-information/source-moments.md"
cp "$ROOT_DIR/reports/source-panel-inventory.md" "$STAGING_DIR/supporting-information/source-panel-inventory.md"
cp "$ROOT_DIR/reports/source-capability-audit.md" "$STAGING_DIR/supporting-information/source-capability-audit.md"
cp "$ROOT_DIR/reports/dark-money-bridge-audit.md" "$STAGING_DIR/supporting-information/dark-money-bridge-audit.md"
cp "$ROOT_DIR/reports/intermediary-bridge-audit.md" "$STAGING_DIR/supporting-information/intermediary-bridge-audit.md"
cp "$ROOT_DIR/reports/revolving-door-bridge-audit.md" "$STAGING_DIR/supporting-information/revolving-door-bridge-audit.md"
cp "$ROOT_DIR/reports/procurement-denominator-audit.md" "$STAGING_DIR/supporting-information/procurement-denominator-audit.md"
cp "$ROOT_DIR/reports/procurement-modification-composition-audit.md" "$STAGING_DIR/supporting-information/procurement-modification-composition-audit.md"
cp "$ROOT_DIR/reports/procurement-benchmark-crosswalk.md" "$STAGING_DIR/supporting-information/procurement-benchmark-crosswalk.md"
cp "$ROOT_DIR/reports/procurement-refresh-readiness.md" "$STAGING_DIR/supporting-information/procurement-refresh-readiness.md"
cp "$ROOT_DIR/reports/claim-boundary-audit.md" "$STAGING_DIR/supporting-information/claim-boundary-audit.md"
cp "$ROOT_DIR/reports/claim-source-dependency.md" "$STAGING_DIR/supporting-information/claim-source-dependency.md"
cp "$ROOT_DIR/reports/causal-calibration-targets.md" "$STAGING_DIR/supporting-information/causal-calibration-targets.md"
cp "$ROOT_DIR/reports/first-wave-causal-protocols.md" "$STAGING_DIR/supporting-information/first-wave-causal-protocols.md"
cp "$ROOT_DIR/reports/first-wave-source-readiness.md" "$STAGING_DIR/supporting-information/first-wave-source-readiness.md"
cp "$ROOT_DIR/reports/claim-posture-audit.md" "$STAGING_DIR/supporting-information/claim-posture-audit.md"
cp "$ROOT_DIR/reports/validation-summary.md" "$STAGING_DIR/supporting-information/validation-summary.md"
cp "$ROOT_DIR/reports/substitution-audit.md" "$STAGING_DIR/supporting-information/substitution-audit.md"
cp "$ROOT_DIR/reports/lobby-capture-portfolio.md" "$STAGING_DIR/supporting-information/portfolio-screen.md"
cp "$ROOT_DIR/reports/calibration-queue.md" "$STAGING_DIR/supporting-information/calibration-queue.md"
cp "$ROOT_DIR/reports/calibration-readiness.md" "$STAGING_DIR/supporting-information/calibration-readiness.md"
cp "$ROOT_DIR/reports/policy-claim-language-audit.md" "$STAGING_DIR/supporting-information/policy-claim-language-audit.md"
cp "$ROOT_DIR/reports/submission-readiness.md" "$STAGING_DIR/supporting-information/submission-readiness.md"
cp "$ROOT_DIR/reports/latex-log-audit.md" "$STAGING_DIR/supporting-information/latex-log-audit.md"
cp "$ROOT_DIR/reports/paper-layout-audit.md" "$STAGING_DIR/supporting-information/paper-layout-audit.md"
cp "$ROOT_DIR/reports/manual-visual-audit.md" "$STAGING_DIR/supporting-information/manual-visual-audit.md"
cp "$ROOT_DIR/reports/final-human-readthrough.md" "$STAGING_DIR/supporting-information/final-human-readthrough.md"
cp "$ROOT_DIR/CITATION.cff" "$STAGING_DIR/supporting-information/CITATION.cff"
cp "$ROOT_DIR/.zenodo.json" "$STAGING_DIR/supporting-information/zenodo.json"
mkdir -p "$STAGING_DIR/supporting-information/report-data"
for report_artifact in "$ROOT_DIR"/reports/*.csv "$ROOT_DIR"/reports/*.md "$ROOT_DIR"/reports/*.manifest.json; do
  if [ -e "$report_artifact" ]; then
    case "$(basename "$report_artifact")" in
      archive-handoff-manifest.*) continue ;;
      doi-deposit-readiness.*) continue ;;
      wiley-submission-form-readiness.*) continue ;;
      reggov-guidelines-readiness.*) continue ;;
      sam-contract-awards-export-audit.*) continue ;;
      sam-contract-awards-preflight.*) continue ;;
      usaspending-transaction-download-strata.*) continue ;;
    esac
    cp "$report_artifact" "$STAGING_DIR/supporting-information/report-data/"
  fi
done
mkdir -p "$STAGING_DIR/figures"
cp "$PAPER_DIR"/figures/Figure_*.pdf "$STAGING_DIR/figures/"
cp "$PAPER_DIR"/figures/Figure_*.svg "$STAGING_DIR/figures/"
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

Root manuscript: strategic-channel-substitution-regulatory-capture.tex
Compiled PDF: strategic-channel-substitution-regulatory-capture.pdf
Supplement: supplement.tex and supplement.pdf

The included USG.cls is a generated copy of Wiley's USG class with template sample journal art and the generic Open Access badge removed for neutral peer-review rendering. The downloaded Wiley template remains unmodified in the repository.

Supporting information: supporting-information/
Package manifest: supporting-information/submission-package-manifest.json and supporting-information/submission-package-manifest.md

Compile from this directory with:
pdflatex -interaction=nonstopmode strategic-channel-substitution-regulatory-capture.tex
bibtex strategic-channel-substitution-regulatory-capture
pdflatex -interaction=nonstopmode strategic-channel-substitution-regulatory-capture.tex
pdflatex -interaction=nonstopmode strategic-channel-substitution-regulatory-capture.tex
pdflatex -interaction=nonstopmode strategic-channel-substitution-regulatory-capture.tex
pdflatex -interaction=nonstopmode strategic-channel-substitution-regulatory-capture.tex
EOF

python3 "$ROOT_DIR/scripts/write-submission-package-manifest.py" "$STAGING_DIR" "$ROOT_DIR"
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
printf 'Wrote %s\n' "$ZIP_PATH"
