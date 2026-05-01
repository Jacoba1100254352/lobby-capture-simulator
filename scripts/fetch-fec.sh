#!/usr/bin/env sh
set -eu
mkdir -p data/raw
cp data/fixtures/normalized-fec-campaign-finance.csv data/raw/fec-campaign-finance.csv
echo "Wrote data/raw/fec-campaign-finance.csv from the normalized fixture. Replace this with live FEC export normalization when API credentials and field mapping are finalized."
