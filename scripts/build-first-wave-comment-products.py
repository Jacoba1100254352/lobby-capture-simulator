#!/usr/bin/env python3
"""Build first-wave comment corpus and duplicate/template source products.

This is a bounded networked acquisition helper for the comment-authenticity
first-wave protocol. It intentionally writes only normalized public fields to
`data/calibration/first-wave/`; raw API payloads and private API keys are not
written to the repository.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "calibration" / "first-wave"
DEFAULT_DOCKET = "EPA-R08-OAR-2024-0389"
USER_AGENT = "lobby-capture-simulator/0.1"
TECHNICAL_TERMS = (
    "standard",
    "emission",
    "emissions",
    "visibility",
    "regional haze",
    "implementation plan",
    "state implementation plan",
    "sip",
    "source",
    "control",
    "technology",
    "cost",
    "analysis",
    "permit",
    "compliance",
    "risk",
    "health",
    "environmental",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docket-id", default=os.environ.get("REGULATIONS_COMMENT_DOCKET_ID", DEFAULT_DOCKET))
    parser.add_argument("--agency", default=os.environ.get("REGULATIONS_COMMENT_AGENCY", "EPA"))
    parser.add_argument("--max-comments", type=int, default=int_env("REGULATIONS_COMMENT_MAX_ROWS", 500))
    parser.add_argument("--page-size", type=int, default=int_env("REGULATIONS_COMMENT_PAGE_SIZE", 250))
    parser.add_argument("--workers", type=int, default=int_env("REGULATIONS_COMMENT_DETAIL_WORKERS", 4))
    parser.add_argument("--base", default=os.environ.get("REGULATIONS_API_BASE", "https://api.regulations.gov/v4"))
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    api_key = os.environ.get("REGULATIONS_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set REGULATIONS_API_KEY before building first-wave comment products.")
    if args.max_comments < 1:
        raise SystemExit("--max-comments must be positive.")
    if args.page_size < 5:
        raise SystemExit("--page-size must be at least 5 for Regulations.gov.")
    if args.workers < 1:
        raise SystemExit("--workers must be positive.")

    comment_ids = search_comment_ids(args.base.rstrip("/"), api_key, args.docket_id, args.agency, args.max_comments, args.page_size)
    if len(comment_ids) < args.max_comments:
        raise SystemExit(
            f"Only found {len(comment_ids)} comments for {args.docket_id}; "
            f"{args.max_comments} required for the first-wave source-product gate."
        )

    details = fetch_comment_details(args.base.rstrip("/"), api_key, comment_ids, args.workers)
    corpus_rows = [comment_corpus_row(args.base.rstrip("/"), detail) for detail in details]
    cluster_rows = comment_cluster_rows(corpus_rows, details)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.output_dir / "comment-body-corpus.csv",
        [
            "docketId",
            "commentId",
            "submitterName",
            "organization",
            "postedDate",
            "bodyText",
            "sourceUrl",
            "attachmentText",
            "withdrawn",
            "notes",
        ],
        corpus_rows,
    )
    write_csv(
        args.output_dir / "comment-template-clusters.csv",
        [
            "docketId",
            "commentId",
            "clusterId",
            "clusterMethod",
            "duplicateScore",
            "isTemplate",
            "technicalContentScore",
            "authenticitySignal",
            "clusterRepresentativeId",
            "reviewer",
            "notes",
        ],
        cluster_rows,
    )
    print(f"Wrote {args.output_dir / 'comment-body-corpus.csv'}")
    print(f"Wrote {args.output_dir / 'comment-template-clusters.csv'}")
    return 0


def search_comment_ids(base: str, api_key: str, docket_id: str, agency: str, limit: int, page_size: int) -> list[str]:
    ids: list[str] = []
    page = 1
    while len(ids) < limit:
        params = {
            "filter[docketId]": docket_id,
            "page[size]": str(min(page_size, 250)),
            "page[number]": str(page),
            "sort": "postedDate,documentId",
        }
        payload = get_json(f"{base}/comments?{urlencode(params)}", api_key)
        for item in payload.get("data", []):
            if not isinstance(item, dict):
                continue
            attributes = item.get("attributes", {}) if isinstance(item.get("attributes"), dict) else {}
            if agency and attributes.get("agencyId") not in {"", None, agency}:
                continue
            comment_id = str(item.get("id", "")).strip()
            if comment_id:
                ids.append(comment_id)
                if len(ids) >= limit:
                    break
        meta = payload.get("meta", {}) if isinstance(payload.get("meta"), dict) else {}
        if not meta.get("hasNextPage") or not payload.get("data"):
            break
        page += 1
    return ids[:limit]


def fetch_comment_details(base: str, api_key: str, comment_ids: list[str], workers: int) -> list[dict[str, object]]:
    rows_by_id: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fetch_comment_detail, base, api_key, comment_id): comment_id
            for comment_id in comment_ids
        }
        for future in as_completed(futures):
            comment_id = futures[future]
            rows_by_id[comment_id] = future.result()
    return [rows_by_id[comment_id] for comment_id in comment_ids]


def fetch_comment_detail(base: str, api_key: str, comment_id: str) -> dict[str, object]:
    payload = retry_json(f"{base}/comments/{comment_id}", api_key)
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise RuntimeError(f"Regulations.gov detail payload for {comment_id} did not contain a data object.")
    return data


def retry_json(url: str, api_key: str) -> dict[str, object]:
    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            return get_json(url, api_key)
        except HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503, 504}:
                detail = error.read().decode("utf-8", errors="replace")[:400]
                raise RuntimeError(f"GET {redact(url)} failed with HTTP {error.code}: {detail}") from error
        except (URLError, TimeoutError, ConnectionError) as error:
            last_error = error
        time.sleep(min(20.0, 1.5 * attempt * attempt))
    raise RuntimeError(f"GET {redact(url)} failed after retries: {last_error}")


def get_json(url: str, api_key: str) -> dict[str, object]:
    request = Request(url, headers={"X-Api-Key": api_key, "User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, dict):
        raise RuntimeError(f"GET {redact(url)} returned a non-object payload.")
    return payload


def comment_corpus_row(base: str, detail: dict[str, object]) -> dict[str, str]:
    attributes = detail.get("attributes") if isinstance(detail.get("attributes"), dict) else {}
    comment_id = str(detail.get("id", "")).strip()
    body = public_comment_text(str(attributes.get("comment") or ""))
    duplicate_comments = int_value(attributes.get("duplicateComments"))
    notes = [
        "source=Regulations.gov v4 comment detail",
        f"retrievedAt={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"commentOnDocumentId={attributes.get('commentOnDocumentId') or ''}",
        f"duplicateComments={duplicate_comments}",
    ]
    organization = str(attributes.get("organization") or attributes.get("govAgency") or "").strip()
    if not organization:
        organization = "not provided by public Regulations.gov fields"
        notes.append("organizationMissing=true")
    return {
        "docketId": str(attributes.get("docketId") or ""),
        "commentId": comment_id,
        "submitterName": submitter_name(attributes),
        "organization": organization,
        "postedDate": str(attributes.get("postedDate") or ""),
        "bodyText": body,
        "sourceUrl": f"https://www.regulations.gov/comment/{comment_id}",
        "attachmentText": "",
        "withdrawn": boolean_text(attributes.get("withdrawn")),
        "notes": "; ".join(notes),
    }


def comment_cluster_rows(corpus_rows: list[dict[str, str]], details: list[dict[str, object]]) -> list[dict[str, str]]:
    normalized_to_rows: dict[str, list[dict[str, str]]] = {}
    duplicate_counts: dict[str, int] = {}
    for row, detail in zip(corpus_rows, details):
        attributes = detail.get("attributes") if isinstance(detail.get("attributes"), dict) else {}
        normalized = normalized_comment(row["bodyText"])
        normalized_to_rows.setdefault(normalized, []).append(row)
        duplicate_counts[row["commentId"]] = int_value(attributes.get("duplicateComments"))
    max_duplicate = max(duplicate_counts.values(), default=1)
    representatives = {
        normalized: sorted(item["commentId"] for item in rows)[0]
        for normalized, rows in normalized_to_rows.items()
    }
    result = []
    for row in corpus_rows:
        normalized = normalized_comment(row["bodyText"])
        hash_id = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]
        observed_duplicate = max(duplicate_counts.get(row["commentId"], 1), len(normalized_to_rows.get(normalized, [])))
        duplicate_score = 0.0 if observed_duplicate <= 1 else math.log1p(observed_duplicate) / max(math.log1p(max_duplicate), 1.0)
        result.append(
            {
                "docketId": row["docketId"],
                "commentId": row["commentId"],
                "clusterId": f"rg-comment-cluster-{hash_id}",
                "clusterMethod": "normalized-text-sha1-plus-regulations-duplicate-count-v1",
                "duplicateScore": f"{min(1.0, duplicate_score):.4f}",
                "isTemplate": boolean_text(observed_duplicate > 1),
                "technicalContentScore": f"{technical_content_score(row['bodyText']):.4f}",
                "authenticitySignal": f"public_comment_body_present; duplicateComments={duplicate_counts.get(row['commentId'], 1)}",
                "clusterRepresentativeId": representatives.get(normalized, row["commentId"]),
                "reviewer": "script:build-first-wave-comment-products",
                "notes": "Reproducible pre-review clustering; not agency uptake coding.",
            }
        )
    return result


def public_comment_text(value: str) -> str:
    text = html.unescape(value)
    text = re.sub(r"(?i)<br\\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \\t\\r\\f\\v]+", " ", text)
    text = re.sub(r" *\\n+ *", "\n", text)
    return text.strip()


def normalized_comment(value: str) -> str:
    lowered = html.unescape(value).lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(lowered.split())


def technical_content_score(value: str) -> float:
    normalized = normalized_comment(value)
    if not normalized:
        return 0.0
    hits = sum(1 for term in TECHNICAL_TERMS if term in normalized)
    length_bonus = min(0.35, len(normalized.split()) / 1200.0)
    return min(1.0, (hits / max(len(TECHNICAL_TERMS), 1)) + length_bonus)


def submitter_name(attributes: dict[str, object]) -> str:
    first = str(attributes.get("firstName") or "").strip()
    last = str(attributes.get("lastName") or "").strip()
    if first or last:
        return " ".join(part for part in (first, last) if part)
    title = str(attributes.get("title") or "").strip()
    prefix = "Comment submitted by "
    if title.startswith(prefix):
        return title[len(prefix):].strip()
    return title


def int_value(value: object) -> int:
    try:
        return int(float(str(value or "0")))
    except ValueError:
        return 0


def boolean_text(value: object) -> str:
    if isinstance(value, str):
        return "true" if value.strip().lower() in {"1", "true", "yes", "y"} else "false"
    return "true" if bool(value) else "false"


def int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def redact(url: str) -> str:
    return re.sub(r"(api_key=)[^&]+", r"\1REDACTED", url)


if __name__ == "__main__":
    raise SystemExit(main())
