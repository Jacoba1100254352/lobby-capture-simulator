#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

max_passes="${LOBBY_CAPTURE_FINALIZE_ARTIFACT_PASSES:-3}"

run_package_stack() {
  ./scripts/build-submission-package.sh
  ./scripts/check-submission-package.sh
  python3 scripts/write-archive-handoff-manifest.py
  python3 scripts/audit-wiley-submission-form-readiness.py
  python3 scripts/audit-reggov-guidelines-readiness.py
  python3 scripts/build-doi-deposit-package.py
  python3 scripts/prepare-zenodo-deposit.py
  python3 scripts/audit-doi-deposit-readiness.py
}

run_finalization_pass() {
  run_package_stack
  python3 scripts/write-final-readthrough-evidence.py
  run_package_stack
}

pass=1
while [ "$pass" -le "$max_passes" ]; do
  echo "Finalizing paper artifacts pass $pass/$max_passes"
  run_finalization_pass
  if python3 scripts/check-paper-artifacts.py; then
    exit 0
  fi
  pass=$((pass + 1))
done

echo "Paper artifact finalization did not converge after $max_passes passes." >&2
exit 1
