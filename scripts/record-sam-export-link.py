#!/usr/bin/env python3
"""Record a short-lived SAM.gov Contract Awards export link in .env.

SAM.gov emailed async-export links expire quickly. This helper turns the pasted
email or URL into the exact environment variables used by the export audit while
keeping API keys out of the URL and out of terminal output.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV = ROOT / ".env"
EXPORT_URL_RE = re.compile(r"https://api\.sam\.gov/contract-awards/v1/download\?[^\s)>\]]+")
VALID_MINUTES_RE = re.compile(r"valid\s+for\s+(\d+)\s+minutes?", re.IGNORECASE)
EMAIL_DATE_RE = re.compile(r"^Date:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
TRACKED_KEYS = [
    "SAM_CONTRACT_AWARDS_LIVE_CSV",
    "SAM_CONTRACT_AWARDS_LIVE_URL",
    "SAM_CONTRACT_AWARDS_LIVE_URL_GENERATED_AT",
    "SAM_CONTRACT_AWARDS_LIVE_URL_EXPIRES_AT",
    "SAM_CONTRACT_AWARDS_LIVE_URL_VALID_MINUTES",
    "SAM_CONTRACT_AWARDS_LIVE_URL_RECORDED_AT",
    "SAM_CONTRACT_AWARDS_LIVE_URL_TIME_SOURCE",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV, help="Environment file to update.")
    parser.add_argument("--url", help="SAM.gov Contract Awards download URL.")
    parser.add_argument("--input", type=Path, help="File containing the SAM.gov email or URL. Use '-' for stdin.")
    parser.add_argument(
        "--generated-at",
        help="UTC ISO timestamp for when the export URL was generated. Overrides any email Date header.",
    )
    parser.add_argument("--expires-at", help="UTC ISO timestamp for when the export URL expires.")
    parser.add_argument("--valid-minutes", type=int, help="Token validity window in minutes.")
    parser.add_argument(
        "--keep-live-csv",
        action="store_true",
        help="Do not clear SAM_CONTRACT_AWARDS_LIVE_CSV when recording a URL.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print redacted changes without writing .env.")
    args = parser.parse_args()

    source_text = input_text(args)
    raw_url = args.url or extract_url(source_text)
    if not raw_url:
        raise SystemExit("No SAM.gov Contract Awards download URL found in --url, --input, or stdin.")

    normalized_url = normalize_download_url(raw_url)
    valid_minutes = args.valid_minutes or extract_valid_minutes(source_text) or 60
    recorded_at = utc_now()
    email_date = extract_email_date(source_text)
    if args.generated_at:
        generated_at = parse_timestamp(args.generated_at)
        time_source = "explicit_generated_at"
    elif email_date:
        generated_at = email_date
        time_source = "email_date_header"
    else:
        generated_at = recorded_at
        time_source = "recorded_at_fallback"
    expires_at = parse_timestamp(args.expires_at) if args.expires_at else generated_at + timedelta(minutes=valid_minutes)

    updates = {
        "SAM_CONTRACT_AWARDS_LIVE_URL": normalized_url,
        "SAM_CONTRACT_AWARDS_LIVE_URL_GENERATED_AT": format_utc(generated_at),
        "SAM_CONTRACT_AWARDS_LIVE_URL_EXPIRES_AT": format_utc(expires_at),
        "SAM_CONTRACT_AWARDS_LIVE_URL_VALID_MINUTES": str(valid_minutes),
        "SAM_CONTRACT_AWARDS_LIVE_URL_RECORDED_AT": format_utc(recorded_at),
        "SAM_CONTRACT_AWARDS_LIVE_URL_TIME_SOURCE": time_source,
    }
    if not args.keep_live_csv:
        updates["SAM_CONTRACT_AWARDS_LIVE_CSV"] = ""

    if args.dry_run:
        print_summary(args.env, updates, generated_at, expires_at, recorded_at, time_source, dry_run=True)
        return 0

    write_env(args.env, updates)
    print_summary(args.env, updates, generated_at, expires_at, recorded_at, time_source, dry_run=False)
    return 0


def input_text(args: argparse.Namespace) -> str:
    chunks: list[str] = []
    if args.input:
        if str(args.input) == "-":
            chunks.append(sys.stdin.read())
        else:
            chunks.append(args.input.read_text(encoding="utf-8"))
    elif not args.url and not sys.stdin.isatty():
        chunks.append(sys.stdin.read())
    return "\n".join(chunks)


def extract_url(text: str) -> str:
    match = EXPORT_URL_RE.search(text)
    return match.group(0).rstrip(".,") if match else ""


def extract_valid_minutes(text: str) -> int:
    match = VALID_MINUTES_RE.search(text)
    if not match:
        return 0
    return int(match.group(1))


def extract_email_date(text: str) -> datetime | None:
    match = EMAIL_DATE_RE.search(text)
    if not match:
        return None
    try:
        parsed = parsedate_to_datetime(match.group(1).strip())
    except (TypeError, ValueError, IndexError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def normalize_download_url(raw_url: str) -> str:
    parsed = urlsplit(raw_url.strip())
    if parsed.scheme != "https" or parsed.netloc != "api.sam.gov" or parsed.path != "/contract-awards/v1/download":
        raise SystemExit("URL must be a SAM.gov Contract Awards download URL.")
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    token = query.get("token", "").strip()
    if not token:
        raise SystemExit("SAM.gov download URL must contain a token parameter.")
    query["api_key"] = "REPLACE_WITH_API_KEY"
    ordered = [("api_key", query["api_key"]), ("token", token)]
    for key, value in sorted(query.items()):
        if key not in {"api_key", "token"}:
            ordered.append((key, value))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(ordered), ""))


def parse_timestamp(value: str) -> datetime:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as error:
        raise SystemExit(f"Invalid timestamp: {value}") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def utc_now() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=0)


def format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_env(path: Path, updates: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    next_lines: list[str] = []
    for line in lines:
        key = env_key(line)
        if key in updates:
            next_lines.append(f"{key}={shell_quote(updates[key])}")
            seen.add(key)
        else:
            next_lines.append(line)
    for key in TRACKED_KEYS:
        if key in updates and key not in seen:
            next_lines.append(f"{key}={shell_quote(updates[key])}")
    path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def env_key(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return ""
    if stripped.startswith("export "):
        stripped = stripped[len("export "):].lstrip()
    if "=" not in stripped:
        return ""
    key = stripped.split("=", 1)[0].strip()
    return key if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key) else ""


def shell_quote(value: str) -> str:
    if value == "":
        return ""
    if re.match(r"^[A-Za-z0-9_./:@%+=,?&-]+$", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def redacted_url(url: str) -> str:
    parsed = urlsplit(url)
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        query.append((key, "REDACTED" if key in {"api_key", "token"} else value))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), ""))


def print_summary(
    env_path: Path,
    updates: dict[str, str],
    generated_at: datetime,
    expires_at: datetime,
    recorded_at: datetime,
    time_source: str,
    *,
    dry_run: bool,
) -> None:
    verb = "Would update" if dry_run else "Updated"
    print(f"{verb} {env_path}")
    print(f"SAM_CONTRACT_AWARDS_LIVE_URL={redacted_url(updates['SAM_CONTRACT_AWARDS_LIVE_URL'])}")
    print(f"SAM_CONTRACT_AWARDS_LIVE_URL_GENERATED_AT={format_utc(generated_at)}")
    print(f"SAM_CONTRACT_AWARDS_LIVE_URL_EXPIRES_AT={format_utc(expires_at)}")
    print(f"SAM_CONTRACT_AWARDS_LIVE_URL_VALID_MINUTES={updates['SAM_CONTRACT_AWARDS_LIVE_URL_VALID_MINUTES']}")
    print(f"SAM_CONTRACT_AWARDS_LIVE_URL_RECORDED_AT={format_utc(recorded_at)}")
    print(f"SAM_CONTRACT_AWARDS_LIVE_URL_TIME_SOURCE={time_source}")
    if updates.get("SAM_CONTRACT_AWARDS_LIVE_CSV", None) == "":
        print("SAM_CONTRACT_AWARDS_LIVE_CSV cleared so the emailed URL is used.")
    if time_source == "recorded_at_fallback":
        print(
            "WARNING: no email Date header or --generated-at timestamp was found; "
            "expiration is estimated from when this helper ran. If the email is not new, "
            "request a fresh SAM.gov export link."
        )
    print("Next: make sam-procurement-refresh")


if __name__ == "__main__":
    raise SystemExit(main())
