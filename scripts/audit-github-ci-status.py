#!/usr/bin/env python3
"""Verify that the current main commit and release tag have passing GitHub CI.

This is a post-release, networked operational audit. It complements the local
paper artifact gate and the release-asset audit by recording whether GitHub
Actions has validated the same commit and tag that the release metadata names.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CITATION = ROOT / "CITATION.cff"
OUT_CSV = REPORTS / "github-ci-status-audit.csv"
OUT_MD = REPORTS / "github-ci-status-audit.md"


def main() -> int:
    release_tag = release_tag_from_citation()
    head_sha = git_output(["rev-parse", "HEAD"])
    tag_sha, tag_error = git_maybe_output(["rev-parse", f"{release_tag}^{{commit}}"])
    runs, gh_error = github_runs()
    rows = audit_rows(release_tag, head_sha, tag_sha, tag_error, runs, gh_error)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_CSV, rows)
    OUT_MD.write_text(markdown(release_tag, head_sha, rows, gh_error), encoding="utf-8")
    print(f"Wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    if gh_error:
        print(gh_error, file=sys.stderr)
        return 2
    if any(row["status"] == "blocked" for row in rows):
        return 1
    if any(row["status"] == "manual_required" for row in rows):
        return 1
    return 0


def release_tag_from_citation() -> str:
    for line in CITATION.read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    raise SystemExit("Could not find version in CITATION.cff")


def github_runs() -> tuple[list[dict[str, object]], str]:
    try:
        output = subprocess.check_output(
            [
                "gh",
                "run",
                "list",
                "--workflow",
                "CI",
                "--limit",
                "100",
                "--json",
                "databaseId,headBranch,headSha,status,conclusion,workflowName,createdAt,url",
            ],
            cwd=ROOT,
            text=True,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        stderr = getattr(error, "stderr", "") or str(error)
        return [], "could not query GitHub Actions with gh: " + stderr.strip()
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as error:
        return [], f"could not parse gh run list JSON: {error}"
    if not isinstance(parsed, list):
        return [], "gh run list returned unexpected JSON shape"
    return [run for run in parsed if isinstance(run, dict)], ""


def audit_rows(
    release_tag: str,
    head_sha: str,
    tag_sha: str,
    tag_error: str,
    runs: list[dict[str, object]],
    gh_error: str,
) -> list[dict[str, str]]:
    rows = [
        tag_target_row(release_tag, head_sha, tag_sha, tag_error),
        run_row("main-ci", "main", head_sha, runs, gh_error),
        run_row("release-tag-ci", release_tag, head_sha, runs, gh_error),
    ]
    return rows


def tag_target_row(release_tag: str, head_sha: str, tag_sha: str, tag_error: str) -> dict[str, str]:
    if tag_error:
        return item(
            "release-tag-target",
            "blocked",
            "local-git",
            release_tag,
            head_sha,
            "",
            "missing",
            "missing",
            "",
            f"release tag could not be resolved: {tag_error}",
            "Create or fetch the release tag before treating CI and release assets as synchronized.",
        )
    status = "ready" if tag_sha == head_sha else "blocked"
    evidence = "tag points at current HEAD" if status == "ready" else f"tagSha={tag_sha}; headSha={head_sha}"
    return item(
        "release-tag-target",
        status,
        "local-git",
        release_tag,
        head_sha,
        "",
        "completed" if status == "ready" else "mismatch",
        "success" if status == "ready" else "mismatch",
        "",
        evidence,
        "Keep the release tag on the exact commit used for the paper bundle.",
    )


def run_row(
    gate: str,
    branch: str,
    expected_sha: str,
    runs: list[dict[str, object]],
    gh_error: str,
) -> dict[str, str]:
    if gh_error:
        return item(
            gate,
            "manual_required",
            "CI",
            branch,
            expected_sha,
            "",
            "not_checked",
            "",
            "",
            gh_error,
            "Authenticate gh or rerun this audit after GitHub Actions can be queried.",
        )
    run = latest_run(branch, expected_sha, runs)
    if not run:
        return item(
            gate,
            "manual_required",
            "CI",
            branch,
            expected_sha,
            "",
            "missing",
            "missing",
            "",
            "no CI run found for expected branch/tag and commit",
            "Wait for GitHub Actions to create the run, push/fetch the expected ref, or rerun this audit.",
        )
    run_status = str(run.get("status", ""))
    conclusion = str(run.get("conclusion", ""))
    if run_status != "completed":
        status = "manual_required"
        next_action = "Wait for the GitHub Actions run to complete, then rerun this audit."
    elif conclusion == "success":
        status = "ready"
        next_action = "Retain this CI evidence with the release and DOI handoff records."
    else:
        status = "blocked"
        next_action = "Inspect the failed GitHub Actions run and fix the repository before final submission."
    evidence = f"workflow={run.get('workflowName', '')}; createdAt={run.get('createdAt', '')}"
    return item(
        gate,
        status,
        str(run.get("workflowName", "CI")),
        branch,
        expected_sha,
        str(run.get("databaseId", "")),
        run_status,
        conclusion,
        str(run.get("url", "")),
        evidence,
        next_action,
    )


def latest_run(branch: str, expected_sha: str, runs: list[dict[str, object]]) -> dict[str, object]:
    matches = [
        run
        for run in runs
        if str(run.get("headBranch", "")) == branch
        and str(run.get("headSha", "")).startswith(expected_sha)
    ]
    return matches[0] if matches else {}


def git_output(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_maybe_output(args: list[str]) -> tuple[str, str]:
    try:
        return git_output(args), ""
    except subprocess.CalledProcessError as error:
        return "", str(error)


def item(
    gate: str,
    status: str,
    workflow: str,
    branch_or_tag: str,
    head_sha: str,
    run_id: str,
    run_status: str,
    conclusion: str,
    url: str,
    evidence: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "gate": gate,
        "status": status,
        "workflow": workflow,
        "branchOrTag": branch_or_tag,
        "headSha": head_sha,
        "runId": run_id,
        "runStatus": run_status,
        "conclusion": conclusion,
        "url": url,
        "evidence": evidence,
        "nextAction": next_action,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "gate",
                "status",
                "workflow",
                "branchOrTag",
                "headSha",
                "runId",
                "runStatus",
                "conclusion",
                "url",
                "evidence",
                "nextAction",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def markdown(release_tag: str, head_sha: str, rows: list[dict[str, str]], gh_error: str) -> str:
    counts = status_counts(rows)
    overall = "blocked" if counts.get("blocked", 0) else "manual_required" if counts.get("manual_required", 0) else "verified"
    lines = [
        "# GitHub CI Status Audit",
        "",
        "This post-release audit records whether GitHub Actions validated the current main commit and release tag. It is separate from the deterministic local paper build.",
        "",
        "## Summary",
        "",
        f"- Release tag: `{release_tag}`",
        f"- Current HEAD: `{head_sha[:12]}`",
        f"- GitHub query status: `{'error' if gh_error else 'ok'}`",
        f"- Overall status: `{overall}`",
        f"- Ready: `{counts.get('ready', 0)}`",
        f"- Manual required: `{counts.get('manual_required', 0)}`",
        f"- Blocked: `{counts.get('blocked', 0)}`",
        "",
        "## Gate Matrix",
        "",
        "| Gate | Status | Branch or tag | Commit | Run | Run status | Conclusion | Evidence | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        run = f"[{row['runId']}]({row['url']})" if row["runId"] and row["url"] else row["runId"]
        lines.append(
            "| {gate} | {status} | {branch} | {sha} | {run} | {run_status} | {conclusion} | {evidence} | {next_action} |".format(
                gate=md(row["gate"]),
                status=md(row["status"]),
                branch=md(row["branchOrTag"]),
                sha=md(row["headSha"][:12]),
                run=md(run),
                run_status=md(row["runStatus"]),
                conclusion=md(row["conclusion"]),
                evidence=md(row["evidence"]),
                next_action=md(row["nextAction"]),
            )
        )
    if gh_error:
        lines.extend(["", "## Query Error", "", "```text", gh_error, "```"])
    return "\n".join(lines) + "\n"


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get("status", "")
        counts[status] = counts.get(status, 0) + 1
    return counts


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
