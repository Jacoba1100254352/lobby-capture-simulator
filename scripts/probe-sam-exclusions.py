#!/usr/bin/env python3
"""Run a minimal redacted SAM.gov Exclusions API access/quota preflight.

This command is intentionally operational. It checks whether the configured
local SAM key can reach the public Exclusions API and records enough response
shape to guide later manual source-product work. It does not promote exclusion
rows into calibration files or the frozen paper snapshot.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ENV_FILE = ROOT / ".env"
DEFAULT_BASE = "https://api.sam.gov/entity-information/v4"
NEXT_ACCESS_RE = re.compile(r'"nextAccessTime"\s*:\s*"([^"]+)"')
SECRET_QUERY_KEYS = {"api_key", "access_token", "token", "key"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--env-file", type=Path, default=ENV_FILE)
    parser.add_argument("--base-url", default="")
    parser.add_argument("--query", default="")
    parser.add_argument("--page", type=int, default=-1)
    parser.add_argument("--page-size", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=0)
    parser.add_argument("--fail-on-unavailable", action="store_true")
    args = parser.parse_args()

    env = os.environ.copy()
    load_dotenv(args.env_file, env)
    row, samples = run_preflight(args, env)

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "sam-exclusions-preflight.csv", row)
    write_markdown(args.reports / "sam-exclusions-preflight.md", row, samples)
    print(f"Wrote {args.reports / 'sam-exclusions-preflight.csv'}")
    print(f"Wrote {args.reports / 'sam-exclusions-preflight.md'}")

    if args.fail_on_unavailable and row["status"] != "ok":
        return 1
    return 0


def load_dotenv(path: Path, env: dict[str, str]) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if not env.get(key):
            env[key] = value


def run_preflight(args: argparse.Namespace, env: dict[str, str]) -> tuple[dict[str, str], list[dict[str, str]]]:
    api_key = env.get("SAM_API_KEY", "").strip()
    if not api_key:
        return (
            {
                "source": "sam-exclusions",
                "status": "missing",
                "records": "0",
                "nextAccessTime": "",
                "endpoint": endpoint_url(args, env, "REDACTED"),
                "query": configured_query(args, env) or "none",
                "notes": "SAM_API_KEY is not set in the local environment; no request was made.",
            },
            [],
        )

    url = endpoint_url(args, env, api_key)
    redacted_url = redact_url(url)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": env.get(
                "SAM_EXCLUSIONS_USER_AGENT",
                "lobby-capture-simulator/1.0 (+https://github.com/Jacoba1100254352/lobby-capture-simulator)",
            ),
        },
    )
    timeout = args.timeout_seconds or int_env(env, "SAM_EXCLUSIONS_TIMEOUT_SECONDS", 20)
    try:
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        status, notes, next_access = classify_error(error.code, detail)
        return (
            {
                "source": "sam-exclusions",
                "status": status,
                "records": "0",
                "nextAccessTime": next_access,
                "endpoint": redacted_url,
                "query": configured_query(args, env) or "none",
                "notes": f"{notes}; HTTP {error.code}; no raw payload promoted",
            },
            [],
        )
    except (URLError, TimeoutError, OSError) as error:
        reason = getattr(error, "reason", str(error))
        return (
            {
                "source": "sam-exclusions",
                "status": "unavailable",
                "records": "0",
                "nextAccessTime": "",
                "endpoint": redacted_url,
                "query": configured_query(args, env) or "none",
                "notes": f"SAM.gov Exclusions request failed: {reason}; no raw payload promoted",
            },
            [],
        )

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        return (
            {
                "source": "sam-exclusions",
                "status": "unavailable",
                "records": "0",
                "nextAccessTime": "",
                "endpoint": redacted_url,
                "query": configured_query(args, env) or "none",
                "notes": f"SAM.gov Exclusions returned non-JSON data: {error}; no raw payload promoted",
            },
            [],
        )

    records = exclusion_records(payload)
    samples = [sample_record(record) for record in records[:5]]
    status = "ok" if records else "empty"
    return (
        {
            "source": "sam-exclusions",
            "status": status,
            "records": str(len(records)),
            "nextAccessTime": "",
            "endpoint": redacted_url,
            "query": configured_query(args, env) or "none",
            "notes": f"public Exclusions API preflight; page-only operational check; no raw payload promoted; responseKeys={payload_keys(payload)}",
        },
        samples,
    )


def endpoint_url(args: argparse.Namespace, env: dict[str, str], api_key: str) -> str:
    base = (args.base_url or env.get("SAM_EXCLUSIONS_API_BASE") or DEFAULT_BASE).rstrip("/")
    query = configured_query(args, env)
    params = {
        "api_key": api_key,
        "page": str(args.page if args.page >= 0 else int_env(env, "SAM_EXCLUSIONS_PAGE", 0)),
        "size": str(args.page_size or int_env(env, "SAM_EXCLUSIONS_PAGE_SIZE", 10)),
    }
    if query:
        params["q"] = query
    return f"{base}/exclusions?{urlencode(params)}"


def configured_query(args: argparse.Namespace, env: dict[str, str]) -> str:
    return (args.query or env.get("SAM_EXCLUSIONS_QUERY") or "").strip()


def classify_error(status_code: int, detail: str) -> tuple[str, str, str]:
    next_access = first_match(NEXT_ACCESS_RE, detail)
    lowered = detail.lower()
    if status_code == 429 or next_access or "exceeded your quota" in lowered or "message throttled out" in lowered:
        notes = f"SAM.gov quota blocked until {next_access}" if next_access else "SAM.gov Exclusions request returned quota/throttle response"
        return "quota_blocked", notes, next_access
    if status_code in {401, 403}:
        return "unavailable", "SAM.gov Exclusions request failed authorization or access checks", ""
    return "unavailable", "SAM.gov Exclusions request failed", ""


def exclusion_records(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if not isinstance(payload, dict):
        return []
    for key in (
        "exclusions",
        "exclusionRecords",
        "entityExclusions",
        "results",
        "data",
        "records",
        "content",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            return [record for record in value if isinstance(record, dict)]
    embedded = payload.get("_embedded")
    if isinstance(embedded, dict):
        for value in embedded.values():
            if isinstance(value, list):
                return [record for record in value if isinstance(record, dict)]
    for value in payload.values():
        if isinstance(value, dict):
            nested = exclusion_records(value)
            if nested:
                return nested
    return []


def sample_record(record: dict[str, object]) -> dict[str, str]:
    return {
        "exclusionId": first_text(record, "exclusionId", "id", "exclusionIdentifier", "recordId"),
        "uei": first_text(record, "uei", "ueiSAM", "uniqueEntityId", "uniqueEntityIdentifier"),
        "recipientName": first_text(record, "recipientName", "legalBusinessName", "entityName", "name"),
        "exclusionType": first_text(record, "exclusionType", "classification", "type", "nature"),
        "startDate": first_text(record, "startDate", "activationDate", "effectiveDate"),
        "endDate": first_text(record, "endDate", "terminationDate", "inactiveDate"),
        "agency": first_text(record, "agency", "excludingAgency", "agencyName", "officeName"),
    }


def first_text(record: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = nested_get(record, key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def nested_get(record: dict[str, object], key: str) -> object:
    if key in record:
        return record[key]
    lowered = key.lower()
    for candidate, value in record.items():
        if candidate.lower() == lowered:
            return value
    for value in record.values():
        if isinstance(value, dict):
            nested = nested_get(value, key)
            if nested not in (None, ""):
                return nested
    return None


def write_csv(path: Path, row: dict[str, str]) -> None:
    fields = ["source", "status", "records", "nextAccessTime", "endpoint", "query", "notes"]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)


def write_markdown(path: Path, row: dict[str, str], samples: list[dict[str, str]]) -> None:
    lines = [
        "# SAM Exclusions Preflight",
        "",
        "This live preflight is an operational quota/access check for the public SAM.gov Exclusions API. It is not a source moment, calibration input, or promoted exclusion overlay.",
        "",
        "## Summary",
        "",
        f"- Status: `{row['status']}`",
        f"- Records returned: `{row['records']}`",
        f"- Next access time: `{row['nextAccessTime'] or 'none'}`",
        f"- Endpoint: `{row['endpoint']}`",
        f"- Query: `{row['query']}`",
        f"- Notes: {row['notes']}",
        f"- Generated at: `{now_utc()}`",
        "",
        "## Promotion Rule",
        "",
        "Rows from this preflight can become exclusion-overlay evidence only after reviewed UEI, recipient, exclusion type, dates, agency, cause, and source-provenance fields are populated in `data/calibration/first-wave/sam-exclusion-overlay.csv`, followed by `make first-wave-source-products`, `make first-wave-source-readiness`, and `make paper-artifacts-check`.",
        "",
        "## Sample Shape",
        "",
        "| Exclusion ID | UEI | Recipient | Type | Start | End | Agency |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if samples:
        for sample in samples:
            lines.append(
                "| {exclusionId} | {uei} | {recipientName} | {exclusionType} | {startDate} | {endDate} | {agency} |".format(
                    **{key: md(value) for key, value in sample.items()}
                )
            )
    else:
        lines.append("| none |  |  |  |  |  |  |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def payload_keys(payload: object) -> str:
    if isinstance(payload, dict):
        return ";".join(sorted(str(key) for key in payload.keys())[:12])
    if isinstance(payload, list):
        return "list"
    return type(payload).__name__


def redact_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, "REDACTED") if key.lower() in SECRET_QUERY_KEYS or "key" in key.lower() else (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1) if match else ""


def int_env(env: dict[str, str], name: str, default: int) -> int:
    try:
        return int(env.get(name, str(default)))
    except ValueError:
        return default


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
