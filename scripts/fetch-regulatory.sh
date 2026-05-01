#!/usr/bin/env sh
set -eu
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${REGULATORY_LIVE_CSV:-}" ]; then
    cp "$REGULATORY_LIVE_CSV" "$source_file"
  elif [ -n "${REGULATORY_LIVE_URL:-}" ]; then
    curl -fsSL "$REGULATORY_LIVE_URL" -o "$source_file"
  elif [ "${REGULATORY_SOURCE_NATIVE:-1}" = "1" ]; then
    python3 scripts/fetch-source-data.py regulatory
    exit 0
  else
    echo "Set REGULATORY_LIVE_CSV, REGULATORY_LIVE_URL, or leave REGULATORY_SOURCE_NATIVE=1 before running ./scripts/fetch-regulatory.sh --live." >&2
    exit 2
  fi
  python3 scripts/normalize-calibration.py regulatory "$source_file" data/raw/regulatory-dockets.csv
else
  cp data/fixtures/normalized-regulatory-dockets.csv data/raw/regulatory-dockets.csv
  echo "Wrote data/raw/regulatory-dockets.csv from the normalized fixture. Use --live with REGULATORY_LIVE_CSV or REGULATORY_LIVE_URL for live normalization."
fi
