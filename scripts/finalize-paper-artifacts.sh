#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

max_passes="${LOBBY_CAPTURE_FINALIZE_ARTIFACT_PASSES:-3}"

run_source_control_reports() {
  python3 scripts/write-first-wave-cross-venue-adjudication.py --raw data/snapshots/2024-env/normalized
  python3 scripts/promote-first-wave-reviewed-entity-products.py
  python3 scripts/audit-first-wave-source-products.py
  python3 scripts/audit-first-wave-source-readiness.py
}

run_boundary_reports() {
  python3 scripts/write-first-wave-procurement-source-acquisition.py
  python3 scripts/audit-candidate-source-leakage.py
  python3 scripts/write-first-wave-manual-adjudication-plan.py
  python3 scripts/write-procurement-causal-upgrade-packet.py
  python3 scripts/write-substitution-causal-upgrade-packet.py
  python3 scripts/write-comment-causal-upgrade-packet.py
  python3 scripts/write-venue-causal-upgrade-packet.py
}

run_control_reports() {
  run_source_control_reports
  run_boundary_reports
}

run_distribution_stack() {
  ./scripts/build-submission-package.sh
  ./scripts/check-submission-package.sh
  python3 scripts/write-archive-handoff-manifest.py
  python3 scripts/audit-wiley-submission-form-readiness.py
  python3 scripts/audit-reggov-guidelines-readiness.py
  python3 scripts/build-doi-deposit-package.py
  python3 scripts/prepare-zenodo-deposit.py
  python3 scripts/audit-doi-deposit-readiness.py
  python3 scripts/audit-mechanism-review-circulation.py
}

run_package_stack() {
  run_control_reports
  run_distribution_stack
}

run_rendered_artifact_reports() {
  make tables \
    figures \
    paper-build \
    paper-wiley-build \
    paper-supplement-build \
    paper-word-count \
    paper-layout-audit \
    paper-structure-audit \
    latex-log-audit
}

scrub_copy_suffix_artifacts() {
  for scan_root in paper reports dist; do
    [ -d "$scan_root" ] || continue
    find "$scan_root" -type f \( \
      -name '* [0-9]*.aux' -o \
      -name '* [0-9]*.bbl' -o \
      -name '* [0-9]*.blg' -o \
      -name '* [0-9]*.bst' -o \
      -name '* [0-9]*.cff' -o \
      -name '* [0-9]*.cls' -o \
      -name '* [0-9]*.csv' -o \
      -name '* [0-9]*.eps' -o \
      -name '* [0-9]*.json' -o \
      -name '* [0-9]*.log' -o \
      -name '* [0-9]*.md' -o \
      -name '* [0-9]*.out' -o \
      -name '* [0-9]*.pag' -o \
      -name '* [0-9]*.pdf' -o \
      -name '* [0-9]*.sty' -o \
      -name '* [0-9]*.svg' -o \
      -name '* [0-9]*.tex' -o \
      -name '* [0-9]*.txt' -o \
      -name '* [0-9]*.zip' \
    \) -print -delete
  done
}

run_finalization_pass() {
  run_source_control_reports
  run_rendered_artifact_reports
  run_boundary_reports
  python3 scripts/write-reviewer-risk-register.py
  python3 scripts/write-final-readthrough-evidence.py
  run_distribution_stack
}

pass=1
while [ "$pass" -le "$max_passes" ]; do
  echo "Finalizing paper artifacts pass $pass/$max_passes"
  run_finalization_pass
  scrub_copy_suffix_artifacts
  if python3 scripts/check-paper-artifacts.py; then
    exit 0
  fi
  pass=$((pass + 1))
done

echo "Paper artifact finalization did not converge after $max_passes passes." >&2
exit 1
