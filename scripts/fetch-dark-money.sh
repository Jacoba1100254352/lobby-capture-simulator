#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${DARK_MONEY_LIVE_CSV:-}" ]; then
    cp "$DARK_MONEY_LIVE_CSV" "$source_file"
    python3 scripts/normalize-calibration.py dark-money "$source_file" data/raw/dark-money.csv
  elif [ -n "${DARK_MONEY_LIVE_URL:-}" ]; then
    curl -fsSL "$DARK_MONEY_LIVE_URL" -o "$source_file"
    python3 scripts/normalize-calibration.py dark-money "$source_file" data/raw/dark-money.csv
  else
    python3 scripts/fetch-source-data.py irs-dark-money-capacity --output data/raw/dark-money.csv
  fi
else
  echo "No dark-money fixture is committed. Use --live with DARK_MONEY_LIVE_CSV, DARK_MONEY_LIVE_URL, or the IRS EO BMF source-native bridge." >&2
  exit 2
fi
