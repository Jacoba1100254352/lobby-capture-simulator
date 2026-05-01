#!/usr/bin/env sh
set -eu
mkdir -p data/raw
cp data/fixtures/normalized-regulatory-dockets.csv data/raw/regulatory-dockets.csv
echo "Wrote data/raw/regulatory-dockets.csv from the normalized fixture. Replace this with live Federal Register/Regulations.gov normalization when field mapping is finalized."
