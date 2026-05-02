#!/usr/bin/env sh
set -eu
. ./scripts/load-env.sh
mkdir -p data/raw
if [ "${1:-}" = "--live" ]; then
  source_file="$(mktemp)"
  cleanup() { rm -f "$source_file"; }
  trap cleanup EXIT
  if [ -n "${REVOLVING_DOOR_LIVE_CSV:-}" ]; then
    cp "$REVOLVING_DOOR_LIVE_CSV" "$source_file"
  elif [ -n "${REVOLVING_DOOR_LIVE_URL:-}" ]; then
    curl -fsSL "$REVOLVING_DOOR_LIVE_URL" -o "$source_file"
  else
    echo "Set REVOLVING_DOOR_LIVE_CSV or REVOLVING_DOOR_LIVE_URL before running ./scripts/fetch-revolving-door.sh --live. OPENSECRETS_API_KEY is documented in .env for future source-native work, but this importer currently expects a licensed/exported CSV." >&2
    exit 2
  fi
  python3 scripts/normalize-calibration.py revolving-door "$source_file" data/raw/revolving-door.csv
else
  cp data/fixtures/normalized-revolving-door.csv data/raw/revolving-door.csv
  echo "Wrote data/raw/revolving-door.csv from the normalized fixture. Use --live with REVOLVING_DOOR_LIVE_CSV or REVOLVING_DOOR_LIVE_URL for licensed/source exports."
fi
