#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
ZIP_PATH="${1:-$ROOT_DIR/dist/lobby-capture-wiley-submission.zip}"
SUBMISSION_BASENAME="strategic-channel-substitution-regulatory-capture"

if [ ! -f "$ZIP_PATH" ]; then
  printf 'Missing submission package: %s\n' "$ZIP_PATH" >&2
  exit 2
fi

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/lobby-capture-submission-check.XXXXXX")"
cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT HUP INT TERM

unzip -q "$ZIP_PATH" -d "$WORK_DIR"

required_file() {
  if [ ! -f "$WORK_DIR/$1" ]; then
    printf 'Submission package is missing required file: %s\n' "$1" >&2
    exit 3
  fi
}

required_file "$SUBMISSION_BASENAME.tex"
required_file "$SUBMISSION_BASENAME.pdf"
required_file "supplement.tex"
required_file "supplement.pdf"
required_file "references.bib"
required_file "USG.cls"
required_file "lettersp.sty"
required_file "wileyNJD-Chicago.bst"

run_step() {
  label="$1"
  shift
  stdout_path="$WORK_DIR/$label.stdout"
  if ! "$@" > "$stdout_path" 2>&1; then
    printf 'Submission package compile step failed: %s\n' "$label" >&2
    cat "$stdout_path" >&2
    exit 6
  fi
}

run_pdflatex() {
  label="$1"
  tex_file="$2"
  run_step "$label" pdflatex -interaction=nonstopmode "$tex_file"
}

(
  cd "$WORK_DIR"
  run_pdflatex manuscript-pass1 "$SUBMISSION_BASENAME.tex"
  run_step manuscript-bibtex bibtex "$SUBMISSION_BASENAME"
  run_pdflatex manuscript-pass2 "$SUBMISSION_BASENAME.tex"
  run_pdflatex manuscript-pass3 "$SUBMISSION_BASENAME.tex"
  run_pdflatex manuscript-pass4 "$SUBMISSION_BASENAME.tex"
  run_pdflatex manuscript-pass5 "$SUBMISSION_BASENAME.tex"

  run_pdflatex supplement-pass1 supplement.tex
  run_pdflatex supplement-pass2 supplement.tex
)

scan_log() {
  log_path="$WORK_DIR/$1"
  if [ ! -f "$log_path" ]; then
    printf 'Expected LaTeX log was not produced: %s\n' "$1" >&2
    exit 4
  fi
  if grep -E 'Undefined control sequence|LaTeX Error|Emergency stop|Fatal error|undefined citations|undefined references|No file .*\.bbl|Rerun to get citations correct|Label\(s\) may have changed|Citation\(s\) may have changed' "$log_path"; then
    printf 'Submission package compile log contains unresolved LaTeX errors or rerun warnings: %s\n' "$1" >&2
    exit 5
  fi
}

scan_log "$SUBMISSION_BASENAME.log"
scan_log "supplement.log"

printf 'Submission package compiles standalone: %s\n' "$ZIP_PATH"
