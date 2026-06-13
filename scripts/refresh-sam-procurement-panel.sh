#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

. ./scripts/load-env.sh

mode="${SAM_PROCUREMENT_REFRESH_MODE:-auto}"
run_artifacts=1
skip_preflight=0
dry_run=0

usage() {
  cat <<'EOF'
Usage: scripts/refresh-sam-procurement-panel.sh [options]

Quota-aware wrapper for the remaining SAM/FPDS procurement refresh.

Options:
  --mode auto|manual-export|extract|offset
      auto uses a configured SAM_CONTRACT_AWARDS_LIVE_CSV/LIVE_URL when present,
      otherwise it uses the keyed asynchronous extract path.
  --skip-preflight
      Skip the one-row SAM Contract Awards preflight before keyed API modes.
  --no-artifacts
      Stop after the live snapshot/source-moment refresh instead of running the
      full paper-artifacts-check gate.
  --dry-run
      Print the commands that would run without touching network or files.
  -h, --help
      Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      mode="${2:-}"
      shift 2
      ;;
    --mode=*)
      mode="${1#--mode=}"
      shift
      ;;
    --skip-preflight)
      skip_preflight=1
      shift
      ;;
    --no-artifacts)
      run_artifacts=0
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$mode" in
  auto|manual-export|extract|offset) ;;
  *)
    echo "Unsupported refresh mode: $mode" >&2
    usage >&2
    exit 2
    ;;
esac

if [ "$mode" = "auto" ]; then
  if [ -n "${SAM_CONTRACT_AWARDS_LIVE_CSV:-}" ] || [ -n "${SAM_CONTRACT_AWARDS_LIVE_URL:-}" ]; then
    mode="manual-export"
  else
    mode="extract"
  fi
fi

run_cmd() {
  if [ "$dry_run" = "1" ]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

preflight_value() {
  local field="$1"
  python3 - "$field" <<'PY'
import csv
import sys
from pathlib import Path

field = sys.argv[1]
path = Path("reports/sam-contract-awards-preflight.csv")
if not path.exists():
    print("")
    raise SystemExit(0)
with path.open(newline="", encoding="utf-8") as source:
    row = next(csv.DictReader(source), {})
print(row.get(field, ""))
PY
}

require_ok_preflight() {
  if [ "$skip_preflight" = "1" ]; then
    echo "Skipping SAM preflight by request."
    return
  fi
  run_cmd make sam-contract-awards-preflight
  if [ "$dry_run" = "1" ]; then
    return
  fi
  local status
  local next_access
  local notes
  status="$(preflight_value status)"
  next_access="$(preflight_value nextAccessTime)"
  notes="$(preflight_value notes)"
  case "$status" in
    ok)
      echo "SAM preflight ok; proceeding with $mode refresh."
      ;;
    quota_blocked)
      echo "SAM preflight is quota-blocked. Next access time: ${next_access:-unknown}." >&2
      echo "$notes" >&2
      exit 75
      ;;
    missing)
      echo "SAM preflight missing required local configuration." >&2
      echo "$notes" >&2
      exit 1
      ;;
    "")
      echo "SAM preflight did not write reports/sam-contract-awards-preflight.csv." >&2
      exit 1
      ;;
    *)
      echo "SAM preflight status is '$status'; not promoting a live procurement refresh." >&2
      echo "$notes" >&2
      exit 1
      ;;
  esac
}

run_artifact_gate_if_requested() {
  if [ "$run_artifacts" = "1" ]; then
    run_cmd make paper-artifacts-check
  else
    echo "Skipped paper-artifacts-check. Run it before committing or using refreshed source rows in the paper."
  fi
}

case "$mode" in
  manual-export)
    if [ -z "${SAM_CONTRACT_AWARDS_LIVE_CSV:-}" ] && [ -z "${SAM_CONTRACT_AWARDS_LIVE_URL:-}" ]; then
      echo "Manual export mode requires SAM_CONTRACT_AWARDS_LIVE_CSV or SAM_CONTRACT_AWARDS_LIVE_URL." >&2
      exit 1
    fi
    run_cmd make sam-contract-awards-export-audit
    run_cmd ./scripts/run-2024-env-live-snapshot.sh
    run_artifact_gate_if_requested
    ;;
  extract)
    require_ok_preflight
    run_cmd env \
      SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 \
      SAM_CONTRACT_AWARDS_EXTRACT_MODE=1 \
      SAM_CONTRACT_AWARDS_EXTRACT_FORMAT="${SAM_CONTRACT_AWARDS_EXTRACT_FORMAT:-json}" \
      SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID="${SAM_CONTRACT_AWARDS_EXTRACT_EMAIL_ID:-Yes}" \
      ./scripts/run-2024-env-live-snapshot.sh
    run_artifact_gate_if_requested
    ;;
  offset)
    require_ok_preflight
    run_cmd env \
      SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1 \
      SAM_CONTRACT_AWARDS_EXTRACT_MODE=0 \
      ./scripts/run-2024-env-live-snapshot.sh
    run_artifact_gate_if_requested
    ;;
esac
