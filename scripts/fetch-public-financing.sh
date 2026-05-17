#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${PUBLIC_FINANCING_LIVE_CSV:-}" ]; then
    cp "$PUBLIC_FINANCING_LIVE_CSV" "$source_file"
  elif [ -n "${PUBLIC_FINANCING_LIVE_URL:-}" ]; then
    curl -fsSL "$PUBLIC_FINANCING_LIVE_URL" -o "$source_file"
  else
    python3 scripts/fetch-source-data.py nyc-public-financing --output data/raw/public-financing.csv
    exit 0
  fi
  python3 scripts/normalize-calibration.py fec "$source_file" data/raw/public-financing.csv
else
  cp data/fixtures/normalized-public-financing.csv data/raw/public-financing.csv
  echo "Wrote data/raw/public-financing.csv from the normalized fixture. Use --live with PUBLIC_FINANCING_LIVE_CSV or PUBLIC_FINANCING_LIVE_URL for live normalization."
fi
