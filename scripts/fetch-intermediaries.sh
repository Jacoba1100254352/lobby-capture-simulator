#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${INTERMEDIARY_LIVE_CSV:-}" ]; then
    cp "$INTERMEDIARY_LIVE_CSV" "$source_file"
  elif [ -n "${INTERMEDIARY_LIVE_URL:-}" ]; then
    curl -fsSL "$INTERMEDIARY_LIVE_URL" -o "$source_file"
  else
    echo "Set INTERMEDIARY_LIVE_CSV or INTERMEDIARY_LIVE_URL before running ./scripts/fetch-intermediaries.sh --live. IRS_TEOS_BULK_BASE, IRS_FORM990_BULK_BASE, and PROPUBLICA_NONPROFIT_API_KEY are documented in .env for source-native nonprofit and 527 work, but this importer currently expects a normalized export CSV." >&2
    exit 2
  fi
  python3 scripts/normalize-calibration.py intermediary "$source_file" data/raw/intermediaries.csv
else
  cp data/fixtures/normalized-intermediaries.csv data/raw/intermediaries.csv
  echo "Wrote data/raw/intermediaries.csv from the normalized fixture. Use --live with INTERMEDIARY_LIVE_CSV or INTERMEDIARY_LIVE_URL for nonprofit, 527, think-tank, or association exports."
fi
