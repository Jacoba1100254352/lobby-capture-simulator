#!/usr/bin/env python3
"""Run a minimal redacted SAM.gov Contract Awards access/quota preflight.

This command is intentionally separate from deterministic paper builds. It
checks whether the configured local SAM key can reach Contract Awards before a
full live snapshot spends time and quota. The generated report is operational
state, not empirical source evidence.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ENV_FILE = ROOT / ".env"
FETCHER = ROOT / "scripts" / "fetch-source-data.py"
CLASSIFIER = ROOT / "scripts" / "classify-source-failure.py"

API_KEY_RE = re.compile(r"(api_key=)[^&\s]+")
SAM_KEY_RE = re.compile(r"(SAM_API_KEY=)[^\s]+")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument("--env-file", type=Path, default=ENV_FILE)
    parser.add_argument("--agency", default="")
    parser.add_argument("--page-size", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=0)
    parser.add_argument("--hard-timeout-seconds", type=int, default=0)
    parser.add_argument("--extract-mode", choices=["0", "1"], default="")
    parser.add_argument("--fail-on-unavailable", action="store_true")
    args = parser.parse_args()

    env = os.environ.copy()
    load_dotenv(args.env_file, env)
    row = run_preflight(args, env)

    args.reports.mkdir(parents=True, exist_ok=True)
    write_csv(args.reports / "sam-contract-awards-preflight.csv", row)
    write_markdown(args.reports / "sam-contract-awards-preflight.md", row)
    print(f"Wrote {args.reports / 'sam-contract-awards-preflight.csv'}")
    print(f"Wrote {args.reports / 'sam-contract-awards-preflight.md'}")

    if args.fail_on_unavailable and row["status"] not in {"ok"}:
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


def run_preflight(args: argparse.Namespace, env: dict[str, str]) -> dict[str, str]:
    if not env.get("SAM_API_KEY", "").strip():
        return {
            "source": "sam-contract-awards",
            "status": "missing",
            "rows": "0",
            "nextAccessTime": "",
            "notes": "SAM_API_KEY is not set in the local environment; no request was made.",
        }

    agency = args.agency or env.get("SAM_CONTRACT_AWARDS_PREFLIGHT_AGENCY", "").strip()
    if not agency:
        agency = first_csv_value(env.get("SAM_CONTRACT_AWARDS_AGENCIES", "")) or "Environmental Protection Agency"
    page_size = str(args.page_size or int_env(env, "SAM_CONTRACT_AWARDS_PREFLIGHT_PAGE_SIZE", 1))
    timeout = str(args.timeout_seconds or int_env(env, "SAM_CONTRACT_AWARDS_PREFLIGHT_TIMEOUT_SECONDS", 20))
    hard_timeout = str(args.hard_timeout_seconds or int_env(env, "SAM_CONTRACT_AWARDS_PREFLIGHT_HARD_TIMEOUT_SECONDS", 30))
    extract_mode = args.extract_mode or env.get("SAM_CONTRACT_AWARDS_PREFLIGHT_EXTRACT_MODE", "0").strip() or "0"

    with tempfile.TemporaryDirectory(prefix="lobby-sam-preflight-") as tmp:
        tmpdir = Path(tmp)
        output = tmpdir / "sam-contract-awards.csv"
        log = tmpdir / "sam-contract-awards.log"
        command_env = env.copy()
        command_env.update({
            "SOURCE_RAW_DIR": str(tmpdir / "raw"),
            "SOURCE_FETCH_RETRIES": env.get("SAM_CONTRACT_AWARDS_PREFLIGHT_RETRIES", "1"),
            "SOURCE_FETCH_TIMEOUT_SECONDS": timeout,
            "SOURCE_FETCH_HARD_TIMEOUT_SECONDS": hard_timeout,
            "SOURCE_FETCH_CURL_FALLBACK": env.get("SOURCE_FETCH_CURL_FALLBACK", "1"),
            "SAM_CONTRACT_AWARDS_EXTRACT_MODE": extract_mode,
            "SAM_CONTRACT_AWARDS_PAGE_SIZE": page_size,
            "SAM_CONTRACT_AWARDS_MAX_PAGES": "1",
            "SAM_CONTRACT_AWARDS_OFFSET_STARTS": "0",
            "SAM_CONTRACT_AWARDS_AGENCIES": agency,
        })
        command = [sys.executable, str(FETCHER), "sam-contract-awards", "--output", str(output)]
        context = (
            f"preflight agency={agency}; pageSize={page_size}; extractMode={extract_mode}; "
            "no raw payload promoted"
        )
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=command_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=int(hard_timeout) + 15,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            log.write_text(redact(error.stdout or ""), encoding="utf-8")
            return {
                "source": "sam-contract-awards",
                "status": "unavailable",
                "rows": "0",
                "nextAccessTime": "",
                "notes": f"SAM.gov Contract Awards preflight exceeded subprocess timeout; {context}",
            }
        log.write_text(redact(completed.stdout), encoding="utf-8")
        if completed.returncode == 0:
            rows = normalized_row_count(output)
            status = "ok" if rows > 0 else "empty"
            return {
                "source": "sam-contract-awards",
                "status": status,
                "rows": str(rows),
                "nextAccessTime": "",
                "notes": f"{context}; normalized rows returned={rows}",
            }
        status, notes = classify_failure(log)
        return {
            "source": "sam-contract-awards",
            "status": status,
            "rows": "0",
            "nextAccessTime": next_access_time(notes),
            "notes": f"{notes}; {context}",
        }


def classify_failure(log: Path) -> tuple[str, str]:
    module = load_classifier()
    text = log.read_text(encoding="utf-8", errors="replace")
    return module.classify_failure("sam-contract-awards", text)


def load_classifier():
    spec = importlib.util.spec_from_file_location("classify_source_failure", CLASSIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CLASSIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as source:
        return max(sum(1 for _ in csv.DictReader(source)), 0)


def write_csv(path: Path, row: dict[str, str]) -> None:
    fields = ["source", "status", "rows", "nextAccessTime", "notes"]
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)


def write_markdown(path: Path, row: dict[str, str]) -> None:
    lines = [
        "# SAM Contract Awards Preflight",
        "",
        "This live preflight is an operational quota/access check, not a source moment or calibration input.",
        "",
        f"- Status: `{row['status']}`.",
        f"- Rows returned: `{row['rows']}`.",
    ]
    if row["nextAccessTime"]:
        lines.append(f"- Next access time: `{row['nextAccessTime']}`.")
    lines.extend([
        f"- Notes: {row['notes']}",
        "",
        "Do not commit raw SAM payloads or promote this report as empirical evidence. If the preflight is `ok`, run `scripts/run-2024-env-live-snapshot.sh` with the intended representative SAM/FPDS settings and then rerun the full paper artifact gate.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def redact(text: str) -> str:
    return SAM_KEY_RE.sub(r"\1REDACTED", API_KEY_RE.sub(r"\1REDACTED", text))


def next_access_time(notes: str) -> str:
    marker = "until "
    if marker not in notes:
        return ""
    return notes.split(marker, 1)[1].strip()


def first_csv_value(value: str) -> str:
    return next((item.strip() for item in value.split(",") if item.strip()), "")


def int_env(env: dict[str, str], name: str, default: int) -> int:
    try:
        return int(env.get(name, str(default)))
    except ValueError:
        return default


if __name__ == "__main__":
    raise SystemExit(main())
