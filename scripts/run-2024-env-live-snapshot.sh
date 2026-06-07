#!/usr/bin/env bash
set -euo pipefail

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

. ./scripts/load-env.sh
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

rm -f data/raw/lda-lobbying.csv data/raw/fec-campaign-finance.csv data/raw/public-financing.csv data/raw/dark-money.csv data/raw/regulatory-dockets.csv data/raw/usaspending-awards.csv data/raw/revolving-door.csv data/raw/intermediaries.csv

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
    FEC_INCLUDE_SCHEDULE_E=0 \
      python3 scripts/fetch-source-data.py fec --output "$tmpdir/fec-$committee.csv"; then
    append_csv "$tmpdir/fec-$committee.csv" data/raw/fec-campaign-finance.csv
    printf "fec-%s,ok,normalized rows appended\n" "$committee" >> "$status_file"
  else
    printf "fec-%s,unavailable,OpenFEC public demo key or upstream rate limit blocked this committee\n" "$committee" >> "$status_file"
  fi
done

if SOURCE_RAW_DIR="$raw_dir/fec-schedule-e" \
  FEC_API_KEY="${FEC_API_KEY:-DEMO_KEY}" \
  FEC_CYCLE="${FEC_CYCLE:-2024}" \
  FEC_ONLY_SCHEDULE_E=1 \
  FEC_INCLUDE_SCHEDULE_E=1 \
  FEC_SCHEDULE_E_MIN_AMOUNT="${FEC_SCHEDULE_E_MIN_AMOUNT:-1000}" \
  FEC_SCHEDULE_E_PAGE_SIZE="${FEC_SCHEDULE_E_PAGE_SIZE:-100}" \
  FEC_SCHEDULE_E_MAX_PAGES="${FEC_SCHEDULE_E_MAX_PAGES:-4}" \
    python3 scripts/fetch-source-data.py fec --output "$tmpdir/fec-schedule-e.csv"; then
  append_csv "$tmpdir/fec-schedule-e.csv" data/raw/fec-campaign-finance.csv
  printf "fec-schedule-e,ok,normalized independent-expenditure rows appended\n" >> "$status_file"
else
  printf "fec-schedule-e,unavailable,OpenFEC Schedule E request failed or returned no rows\n" >> "$status_file"
fi

if [ -n "${PUBLIC_FINANCING_LIVE_CSV:-}" ] || [ -n "${PUBLIC_FINANCING_LIVE_URL:-}" ]; then
  if ./scripts/fetch-public-financing.sh --live; then
    printf "public-financing,ok,normalized configured public-financing bridge written\n" >> "$status_file"
  else
    printf "public-financing,unavailable,configured public-financing source could not be normalized\n" >> "$status_file"
  fi
elif [ "${PUBLIC_FINANCING_SOURCE_NATIVE:-1}" = "1" ]; then
  if SOURCE_RAW_DIR="$raw_dir/nyc-cfb-public-financing" \
    NYC_CFB_ELECTION="${NYC_CFB_ELECTION:-2025}" \
    NYC_CFB_PUBLIC_PAYMENTS_MAX_ROWS="${NYC_CFB_PUBLIC_PAYMENTS_MAX_ROWS:-5000}" \
    NYC_CFB_FINANCIAL_ANALYSIS_MAX_ROWS="${NYC_CFB_FINANCIAL_ANALYSIS_MAX_ROWS:-5000}" \
      python3 scripts/fetch-source-data.py nyc-public-financing --output data/raw/public-financing.csv; then
    printf "public-financing,ok,normalized NYC CFB public-financing rows written\n" >> "$status_file"
  else
    ./scripts/fetch-public-financing.sh
    printf "public-financing,fixture,NYC CFB source-native public-financing request failed; fixture copied for schema continuity\n" >> "$status_file"
  fi
else
  ./scripts/fetch-public-financing.sh
  printf "public-financing,fixture,public-financing bridge fixture copied for source-moment coverage\n" >> "$status_file"
fi

if [ -n "${DARK_MONEY_LIVE_CSV:-}" ] || [ -n "${DARK_MONEY_LIVE_URL:-}" ]; then
  source_file="$tmpdir/dark-money-source.csv"
  if [ -n "${DARK_MONEY_LIVE_CSV:-}" ]; then
    cp "$DARK_MONEY_LIVE_CSV" "$source_file"
  else
    curl -fsSL "$DARK_MONEY_LIVE_URL" -o "$source_file"
  fi
  if python3 scripts/normalize-calibration.py dark-money "$source_file" data/raw/dark-money.csv; then
    printf "dark-money,ok,normalized configured dark-money bridge rows written\n" >> "$status_file"
  else
    printf "dark-money,unavailable,configured dark-money source could not be normalized\n" >> "$status_file"
  fi
elif [ "${DARK_MONEY_SOURCE_NATIVE:-1}" = "1" ]; then
  if SOURCE_RAW_DIR="$raw_dir/irs-dark-money-capacity" \
    IRS_DARK_MONEY_BMF_STATES="${IRS_DARK_MONEY_BMF_STATES:-${IRS_EO_BMF_STATES:-DC}}" \
    IRS_DARK_MONEY_CAPACITY_MAX_ROWS="${IRS_DARK_MONEY_CAPACITY_MAX_ROWS:-800}" \
    IRS_DARK_MONEY_CAPACITY_OUTPUT_ROWS="${IRS_DARK_MONEY_CAPACITY_OUTPUT_ROWS:-250}" \
      python3 scripts/fetch-source-data.py irs-dark-money-capacity --output data/raw/dark-money.csv; then
    printf "dark-money,ok,normalized IRS EO BMF opaque-capacity proxy rows written\n" >> "$status_file"
  else
    printf "dark-money,unavailable,IRS EO BMF opaque-capacity request failed; no dark-money bridge rows written\n" >> "$status_file"
  fi
else
  printf "dark-money,missing,no configured direct dark-money or opaque-capacity source\n" >> "$status_file"
fi

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

if SOURCE_RAW_DIR="$raw_dir/usaspending" \
  USASPENDING_FISCAL_YEAR="${USASPENDING_FISCAL_YEAR:-2024}" \
  USASPENDING_AGENCY="${USASPENDING_AGENCY:-Environmental Protection Agency}" \
  USASPENDING_PAGE_SIZE="${USASPENDING_PAGE_SIZE:-100}" \
  USASPENDING_MAX_PAGES="${USASPENDING_MAX_PAGES:-2}" \
    python3 scripts/fetch-source-data.py usaspending; then
  printf "usaspending,ok,normalized EPA award rows written\n" >> "$status_file"
else
  printf "usaspending,unavailable,upstream USAspending request returned no rows or failed\n" >> "$status_file"
fi

if [ "${USASPENDING_PROCUREMENT_BRIDGE_SOURCE_NATIVE:-1}" = "1" ]; then
  if SOURCE_RAW_DIR="$raw_dir/usaspending-procurement-bridge" \
    USASPENDING_FISCAL_YEAR="${USASPENDING_FISCAL_YEAR:-2024}" \
    USASPENDING_AGENCIES="${USASPENDING_PROCUREMENT_BRIDGE_AGENCIES:-Environmental Protection Agency,Department of Energy,Department of the Interior,Department of Agriculture,Department of Transportation,Department of Defense}" \
    USASPENDING_PAGE_SIZE="${USASPENDING_PROCUREMENT_BRIDGE_PAGE_SIZE:-25}" \
    USASPENDING_MAX_PAGES="${USASPENDING_PROCUREMENT_BRIDGE_MAX_PAGES:-1}" \
    USASPENDING_ENRICH_LIMIT="${USASPENDING_PROCUREMENT_BRIDGE_ENRICH_LIMIT:-150}" \
    USASPENDING_TREAT_LATEST_TRANSACTION_AS_MODIFICATION=1 \
      python3 scripts/fetch-source-data.py usaspending --output data/raw/usaspending-procurement-bridge.csv; then
    printf "usaspending-procurement-bridge,ok,normalized multi-agency procurement bridge rows written\n" >> "$status_file"
  else
    printf "usaspending-procurement-bridge,unavailable,upstream USAspending multi-agency bridge request returned no rows or failed\n" >> "$status_file"
  fi
else
  printf "usaspending-procurement-bridge,missing,multi-agency procurement bridge disabled\n" >> "$status_file"
fi

if [ -n "${REVOLVING_DOOR_LIVE_CSV:-}" ] || [ -n "${REVOLVING_DOOR_LIVE_URL:-}" ]; then
  if ./scripts/fetch-revolving-door.sh --live; then
    printf "revolving-door,ok,normalized configured source export written\n" >> "$status_file"
  else
    printf "revolving-door,unavailable,configured source export could not be normalized\n" >> "$status_file"
  fi
elif [ "${REVOLVING_DOOR_SOURCE_NATIVE:-1}" = "1" ]; then
  if SOURCE_RAW_DIR="$raw_dir/lda-revolving-door" \
    LDA_YEAR="${LDA_YEAR:-2024}" \
    LDA_ISSUE_CODE= \
    REVOLVING_DOOR_LDA_PAGE_SIZE="${REVOLVING_DOOR_LDA_PAGE_SIZE:-100}" \
    REVOLVING_DOOR_LDA_MAX_PAGES="${REVOLVING_DOOR_LDA_MAX_PAGES:-10}" \
      python3 scripts/fetch-source-data.py revolving-door; then
    printf "revolving-door,ok,derived normalized covered-position rows from LDA source\n" >> "$status_file"
  else
    ./scripts/fetch-revolving-door.sh
    printf "revolving-door,fixture,LDA covered-position request failed; fixture copied for schema continuity\n" >> "$status_file"
  fi
else
  ./scripts/fetch-revolving-door.sh
  printf "revolving-door,fixture,no licensed/source export configured; fixture copied for schema continuity\n" >> "$status_file"
fi

if [ -n "${INTERMEDIARY_LIVE_CSV:-}" ] || [ -n "${INTERMEDIARY_LIVE_URL:-}" ]; then
  if ./scripts/fetch-intermediaries.sh --live; then
    printf "intermediary,ok,normalized configured nonprofit/association source export written\n" >> "$status_file"
  else
    printf "intermediary,unavailable,configured intermediary source export could not be normalized\n" >> "$status_file"
  fi
else
  if [ "${INTERMEDIARY_SOURCE_NATIVE:-1}" = "1" ]; then
    intermediary_notes=""
    intermediary_sources=0
    rm -f data/raw/intermediaries.csv
    if SOURCE_RAW_DIR="$raw_dir/nyc-cfb-intermediaries" \
      NYC_CFB_ELECTION="${NYC_CFB_ELECTION:-2025}" \
      NYC_CFB_INTERMEDIARY_MAX_ROWS="${NYC_CFB_INTERMEDIARY_MAX_ROWS:-2500}" \
        python3 scripts/fetch-source-data.py nyc-intermediaries --output "$tmpdir/nyc-intermediaries.csv"; then
      append_csv "$tmpdir/nyc-intermediaries.csv" data/raw/intermediaries.csv
      intermediary_sources=$((intermediary_sources + 1))
      intermediary_notes="${intermediary_notes}NYC CFB intermediary rows; "
    fi
    if SOURCE_RAW_DIR="$raw_dir/irs-eo-bmf" \
      IRS_EO_BMF_STATES="${IRS_EO_BMF_STATES:-DC}" \
      IRS_EO_BMF_MAX_ROWS="${IRS_EO_BMF_MAX_ROWS:-800}" \
      IRS_EO_BMF_FILTERED_MAX_ROWS="${IRS_EO_BMF_FILTERED_MAX_ROWS:-500}" \
        python3 scripts/fetch-source-data.py irs-eo-bmf --output "$tmpdir/irs-eo-bmf.csv"; then
      append_csv "$tmpdir/irs-eo-bmf.csv" data/raw/intermediaries.csv
      intermediary_sources=$((intermediary_sources + 1))
      intermediary_notes="${intermediary_notes}IRS EO BMF nonprofit/association capacity rows; "
    fi
    if [ "$intermediary_sources" -gt 0 ]; then
      printf "intermediary,ok,%s\n" "$intermediary_notes" >> "$status_file"
    else
      ./scripts/fetch-intermediaries.sh
      printf "intermediary,fixture,source-native intermediary requests failed; fixture copied for schema continuity\n" >> "$status_file"
    fi
  else
    ./scripts/fetch-intermediaries.sh
    printf "intermediary,fixture,no nonprofit/association source export configured; fixture copied for schema continuity\n" >> "$status_file"
  fi
fi

mkdir -p data/snapshots/2024-env
cp "$status_file" data/snapshots/2024-env/live-run-status.csv
python3 scripts/create-2024-env-snapshot.py
python3 scripts/extract-source-moments.py
