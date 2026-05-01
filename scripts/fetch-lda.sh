#!/usr/bin/env sh
set -eu
mkdir -p data/raw
cp data/fixtures/normalized-lda-lobbying.csv data/raw/lda-lobbying.csv
echo "Wrote data/raw/lda-lobbying.csv from the normalized fixture. Replace this with live LDA export normalization when API credentials and field mapping are finalized."
