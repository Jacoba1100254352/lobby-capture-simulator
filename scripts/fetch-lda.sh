#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${LDA_LIVE_CSV:-}" ]; then
    cp "$LDA_LIVE_CSV" "$source_file"
  elif [ -n "${LDA_LIVE_URL:-}" ]; then
    curl -fsSL "$LDA_LIVE_URL" -o "$source_file"
  elif [ "${LDA_SOURCE_NATIVE:-1}" = "1" ]; then
    python3 scripts/fetch-source-data.py lda
    exit 0
  else
    echo "Set LDA_LIVE_CSV, LDA_LIVE_URL, or leave LDA_SOURCE_NATIVE=1 before running ./scripts/fetch-lda.sh --live." >&2
    exit 2
  fi
  python3 scripts/normalize-calibration.py lda "$source_file" data/raw/lda-lobbying.csv
else
  cp data/fixtures/normalized-lda-lobbying.csv data/raw/lda-lobbying.csv
  echo "Wrote data/raw/lda-lobbying.csv from the normalized fixture. Use --live with LDA_LIVE_CSV or LDA_LIVE_URL for live normalization."
fi
