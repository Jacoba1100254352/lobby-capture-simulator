#!/usr/bin/env bash
set -euo pipefail

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

raw_dir="${SOURCE_RAW_DIR:-data/raw/source-payloads/2024-env}"
mkdir -p data/raw "$raw_dir"
status_file="$tmpdir/live-run-status.csv"
printf "source,status,notes\n" > "$status_file"

append_csv() {
  local source_file="$1"
  local destination="$2"
  if [ ! -s "$source_file" ]; then
    return
  fi
  if [ ! -s "$destination" ]; then
    cp "$source_file" "$destination"
  else
    tail -n +2 "$source_file" >> "$destination"
  fi
}

rm -f data/raw/lda-lobbying.csv data/raw/fec-campaign-finance.csv data/raw/regulatory-dockets.csv

for period in first_quarter second_quarter third_quarter fourth_quarter; do
  SOURCE_RAW_DIR="$raw_dir/lda-$period" \
  LDA_YEAR="${LDA_YEAR:-2024}" \
  LDA_PERIOD="$period" \
  LDA_ISSUE_CODE="${LDA_ISSUE_CODE:-ENV}" \
  DEFAULT_ISSUE_DOMAIN="${DEFAULT_ISSUE_DOMAIN:-energy}" \
  LDA_PAGE_SIZE="${LDA_PAGE_SIZE:-100}" \
  LDA_MAX_PAGES="${LDA_MAX_PAGES:-25}" \
    python3 scripts/fetch-source-data.py lda --output "$tmpdir/lda-$period.csv"
  append_csv "$tmpdir/lda-$period.csv" data/raw/lda-lobbying.csv
  printf "lda-%s,ok,normalized rows appended\n" "$period" >> "$status_file"
done

for committee in C00010603 C00042366 C00000935 C00003418 C00027466 C00075820; do
  if SOURCE_RAW_DIR="$raw_dir/fec-$committee" \
    FEC_API_KEY="${FEC_API_KEY:-DEMO_KEY}" \
    FEC_CYCLE="${FEC_CYCLE:-2024}" \
    FEC_COMMITTEE_ID="$committee" \
    FEC_PAGE_SIZE="${FEC_PAGE_SIZE:-100}" \
      python3 scripts/fetch-source-data.py fec --output "$tmpdir/fec-$committee.csv"; then
    append_csv "$tmpdir/fec-$committee.csv" data/raw/fec-campaign-finance.csv
    printf "fec-%s,ok,normalized rows appended\n" "$committee" >> "$status_file"
  else
    printf "fec-%s,unavailable,OpenFEC public demo key or upstream rate limit blocked this committee\n" "$committee" >> "$status_file"
  fi
done

if SOURCE_RAW_DIR="$raw_dir/regulations-gov" \
  REGULATIONS_API_KEY="${REGULATIONS_API_KEY:-DEMO_KEY}" \
  REGULATORY_AGENCY="${REGULATORY_AGENCY:-EPA}" \
  REGULATORY_DATE_FROM="${REGULATORY_DATE_FROM:-2024-01-01}" \
  REGULATORY_DATE_TO="${REGULATORY_DATE_TO:-2024-12-31}" \
  REGULATORY_PAGE_SIZE="${REGULATORY_PAGE_SIZE:-100}" \
    python3 scripts/fetch-source-data.py regulatory --output "$tmpdir/regulations-gov.csv"; then
  append_csv "$tmpdir/regulations-gov.csv" data/raw/regulatory-dockets.csv
  printf "regulations-gov,ok,normalized rows appended\n" >> "$status_file"
else
  printf "regulations-gov,unavailable,public demo key or upstream rate limit blocked this source\n" >> "$status_file"
fi

if SOURCE_RAW_DIR="$raw_dir/federal-register" \
  REGULATORY_SOURCE=federal-register \
  REGULATORY_SEARCH_TERM="${REGULATORY_SEARCH_TERM:-Environmental Protection Agency}" \
  REGULATORY_DATE_FROM="${REGULATORY_DATE_FROM:-2024-01-01}" \
  REGULATORY_DATE_TO="${REGULATORY_DATE_TO:-2024-12-31}" \
  REGULATORY_PAGE_SIZE="${REGULATORY_PAGE_SIZE:-100}" \
    python3 scripts/fetch-source-data.py regulatory --output "$tmpdir/federal-register.csv"; then
  append_csv "$tmpdir/federal-register.csv" data/raw/regulatory-dockets.csv
  printf "federal-register,ok,normalized rows appended\n" >> "$status_file"
else
  printf "federal-register,unavailable,upstream request returned no rows or failed\n" >> "$status_file"
fi

mkdir -p data/snapshots/2024-env
cp "$status_file" data/snapshots/2024-env/live-run-status.csv
python3 scripts/create-2024-env-snapshot.py
python3 scripts/extract-source-moments.py
