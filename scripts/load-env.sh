#!/usr/bin/env sh
if [ -f .env ]; then
  env_tmp="$(mktemp "${TMPDIR:-/tmp}/lobby-capture-env.XXXXXX")"
  : > "$env_tmp"
  while IFS= read -r line || [ -n "$line" ]; do
    stripped="$(printf '%s' "$line" | sed 's/^[[:space:]]*//')"
    case "$stripped" in
      ""|\#*) continue ;;
    esac
    assignment="$stripped"
    case "$assignment" in
      export\ *) assignment="${assignment#export }" ;;
    esac
    case "$assignment" in
      *=*) ;;
      *) continue ;;
    esac
    key="${assignment%%=*}"
    case "$key" in
      ""|[0-9]*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_]*)
        continue
        ;;
    esac
    eval "already_set=\${$key+x}"
    if [ -z "$already_set" ]; then
      printf '%s\n' "$stripped" >> "$env_tmp"
    fi
  done < .env
  set -a
  . "$env_tmp"
  set +a
  rm -f "$env_tmp"
fi
