#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${FEC_LIVE_CSV:-}" ]; then
    cp "$FEC_LIVE_CSV" "$source_file"
  elif [ -n "${FEC_LIVE_URL:-}" ]; then
    curl -fsSL "$FEC_LIVE_URL" -o "$source_file"
  elif [ "${FEC_SOURCE_NATIVE:-1}" = "1" ]; then
    python3 scripts/fetch-source-data.py fec
    exit 0
  else
    echo "Set FEC_LIVE_CSV, FEC_LIVE_URL, or leave FEC_SOURCE_NATIVE=1 before running ./scripts/fetch-fec.sh --live." >&2
    exit 2
  fi
  python3 scripts/normalize-calibration.py fec "$source_file" data/raw/fec-campaign-finance.csv
else
  cp data/fixtures/normalized-fec-campaign-finance.csv data/raw/fec-campaign-finance.csv
  echo "Wrote data/raw/fec-campaign-finance.csv from the normalized fixture. Use --live with FEC_LIVE_CSV or FEC_LIVE_URL for live normalization."
fi
