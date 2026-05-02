#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${USASPENDING_LIVE_CSV:-}" ]; then
    cp "$USASPENDING_LIVE_CSV" "$source_file"
  elif [ -n "${USASPENDING_LIVE_URL:-}" ]; then
    curl -fsSL "$USASPENDING_LIVE_URL" -o "$source_file"
  elif [ "${USASPENDING_SOURCE_NATIVE:-1}" = "1" ]; then
    python3 scripts/fetch-source-data.py usaspending
    exit 0
  else
    echo "Set USASPENDING_LIVE_CSV, USASPENDING_LIVE_URL, or leave USASPENDING_SOURCE_NATIVE=1 before running ./scripts/fetch-usaspending.sh --live." >&2
    exit 2
  fi
  python3 scripts/normalize-calibration.py usaspending "$source_file" data/raw/usaspending-awards.csv
else
  cp data/fixtures/normalized-usaspending-awards.csv data/raw/usaspending-awards.csv
  echo "Wrote data/raw/usaspending-awards.csv from the normalized fixture. Use --live for USAspending API normalization."
fi
