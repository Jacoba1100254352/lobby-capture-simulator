#!/usr/bin/env python3
"""Build candidate-only response/final-rule linkage seeds from comment products.

This offline helper reads the committed comment corpus and template-cluster
products, then writes a manual-review worklist for linking comments to agency
response sections and final-rule text. It deliberately does not claim observed
agency uptake or clear the comment-authenticity source-readiness gate.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "calibration" / "first-wave"
MAX_LINKAGE_ROWS = 80
CANDIDATE_STATUS = "candidate_unreviewed_not_estimation_ready"
LINKAGE_BOUNDARY = (
    "candidate-only response/final-rule linkage scaffold; response sections "
    "and final-rule movement are not manually linked; does not clear the "
    "comment-authenticity uptake, first-wave source-product, or "
    "causal-calibration gates"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    args = parser.parse_args()

    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    corpus_rows = read_rows(source_dir / "comment-body-corpus.csv")
    cluster_rows = read_rows(source_dir / "comment-template-clusters.csv")
    if not corpus_rows:
        raise SystemExit(f"Missing or empty comment corpus: {source_dir / 'comment-body-corpus.csv'}")
    if not cluster_rows:
        raise SystemExit(f"Missing or empty comment clusters: {source_dir / 'comment-template-clusters.csv'}")

    linkage_rows = agency_response_final_rule_linkage_rows(corpus_rows, cluster_rows)
    write_csv(
        source_dir / "agency-response-final-rule-linkage.csv",
        [
            "docketId",
            "commentId",
            "responseSectionId",
            "responseText",
            "finalRuleId",
            "finalRuleDate",
            "uptakeCode",
            "textSimilarity",
            "ruleCitation",
            "reviewer",
            "notes",
            "candidateOnly",
            "candidateStatus",
        ],
        linkage_rows,
    )
    print(f"Wrote {source_dir / 'agency-response-final-rule-linkage.csv'}")
    return 0


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def agency_response_final_rule_linkage_rows(
    corpus_rows: list[dict[str, str]],
    cluster_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    clusters_by_comment = {row["commentId"]: row for row in cluster_rows if row.get("commentId")}
    selected_rows = sorted(
        corpus_rows,
        key=lambda row: (
            -float_value(clusters_by_comment.get(row.get("commentId", ""), {}).get("duplicateScore", "0")),
            -float_value(clusters_by_comment.get(row.get("commentId", ""), {}).get("technicalContentScore", "0")),
            row.get("commentId", ""),
        ),
    )[:MAX_LINKAGE_ROWS]
    rows = []
    for index, row in enumerate(selected_rows, start=1):
        comment_id = row.get("commentId", "")
        docket_id = row.get("docketId", "")
        cluster = clusters_by_comment.get(comment_id, {})
        rows.append(
            {
                "docketId": docket_id,
                "commentId": comment_id,
                "responseSectionId": f"candidate-response-section-{index:04d}",
                "responseText": "manual response-to-comments section linkage required before uptake coding",
                "finalRuleId": f"{docket_id}-candidate-final-rule",
                "finalRuleDate": candidate_final_rule_date(row.get("postedDate", "")),
                "uptakeCode": CANDIDATE_STATUS,
                "textSimilarity": "0.0000",
                "ruleCitation": f"https://www.regulations.gov/docket/{docket_id}",
                "reviewer": "script:build-first-wave-comment-linkage-seeds",
                "notes": (
                    f"{LINKAGE_BOUNDARY}; clusterId={cluster.get('clusterId', '')}; "
                    f"duplicateScore={cluster.get('duplicateScore', '')}; "
                    f"technicalContentScore={cluster.get('technicalContentScore', '')}"
                ),
                "candidateOnly": "true",
                "candidateStatus": CANDIDATE_STATUS,
            }
        )
    return rows


def float_value(value: object) -> float:
    try:
        return float(str(value or "0"))
    except ValueError:
        return 0.0


def candidate_final_rule_date(posted_date: str) -> str:
    text = (posted_date or "").strip()
    if len(text) >= 10:
        return text[:10]
    return "2024-01-01"


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
