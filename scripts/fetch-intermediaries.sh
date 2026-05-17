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
    tmpdir="$(mktemp -d)"
    cleanup() { rm -rf "$tmpdir"; }
    trap cleanup EXIT
    python3 scripts/fetch-source-data.py nyc-intermediaries --output "$tmpdir/nyc-intermediaries.csv"
    python3 scripts/fetch-source-data.py irs-eo-bmf --output "$tmpdir/irs-eo-bmf.csv"
    cp "$tmpdir/nyc-intermediaries.csv" data/raw/intermediaries.csv
    tail -n +2 "$tmpdir/irs-eo-bmf.csv" >> data/raw/intermediaries.csv
    echo "Wrote data/raw/intermediaries.csv from NYC CFB and IRS EO BMF source-native rows."
    exit 0
  fi
  python3 scripts/normalize-calibration.py intermediary "$source_file" data/raw/intermediaries.csv
else
  cp data/fixtures/normalized-intermediaries.csv data/raw/intermediaries.csv
  echo "Wrote data/raw/intermediaries.csv from the normalized fixture. Use --live with INTERMEDIARY_LIVE_CSV or INTERMEDIARY_LIVE_URL for nonprofit, 527, think-tank, or association exports."
fi
