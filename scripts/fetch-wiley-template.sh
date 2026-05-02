#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
TEMPLATE_DIR="$ROOT_DIR/paper/.wiley-template"
ZIP_PATH="$TEMPLATE_DIR/WileyDesign.zip"
URL="${WILEY_TEMPLATE_URL:-https://authors.wiley.com/asset/WileyDesign.zip}"

mkdir -p "$TEMPLATE_DIR"

if [ ! -f "$ZIP_PATH" ]; then
  curl -L --fail --silent --show-error "$URL" -o "$ZIP_PATH"
fi

unzip -q -o "$ZIP_PATH" -d "$TEMPLATE_DIR"

printf 'Wiley LaTeX template is available at %s\n' "$TEMPLATE_DIR"
