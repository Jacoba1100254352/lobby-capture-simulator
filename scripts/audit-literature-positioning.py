#!/usr/bin/env python3
"""Audit whether the manuscript is positioned against the needed literatures."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
BODY = ROOT / "paper" / "sections" / "reggov-body.tex"
REFERENCES = ROOT / "paper" / "references.bib"
OUTPUT_CSV = REPORTS / "literature-positioning-audit.csv"
OUTPUT_MD = REPORTS / "literature-positioning-audit.md"


CATEGORIES = [
    {
        "category": "lobbying-and-access",
        "purpose": "Locate the mechanism model in lobbying, access, and expertise research.",
        "signals": ["lobby", "access", "expertise", "influence economy"],
        "required_keys": [
            "baumgartner2009lobbying",
            "hallDeardorff2006",
            "deFigueiredoRichter2014",
            "bertrand2014whom",
        ],
        "minimum_keys": 3,
    },
    {
        "category": "capture-and-governance",
        "purpose": "Connect capture mechanisms to regulatory-governance theory.",
        "signals": ["regulatory capture", "governance", "institutional vulnerability"],
        "required_keys": [
            "stigler1971economicRegulation",
            "dalbo2006capture",
            "carpenterMoss2014",
            "black2008polycentric",
            "leviFaur2011regulation",
        ],
        "minimum_keys": 4,
    },
    {
        "category": "venue-substitution",
        "purpose": "Show why cross-venue movement is theoretically motivated.",
        "signals": ["venue", "substitution", "adjacent venues", "stage-and-channel"],
        "required_keys": [
            "baumgartnerJones1993",
            "pralle2003venue",
            "carpenterMoss2014",
        ],
        "minimum_keys": 2,
    },
    {
        "category": "money-in-politics",
        "purpose": "Anchor campaign finance, outside spending, dark money, and access channels.",
        "signals": ["campaign finance", "dark money", "outside spending", "public financing"],
        "required_keys": [
            "grossmanHelpman1994",
            "ansolabehere2003littleMoney",
            "gordonHafer2005",
            "kallaBroockman2016",
            "brennanDarkMoney2025",
        ],
        "minimum_keys": 4,
    },
    {
        "category": "rulemaking-and-comments",
        "purpose": "Anchor rulemaking, participation, comments, and procedural controls.",
        "signals": ["rulemaking", "comment", "technical", "procedural"],
        "required_keys": [
            "mccubbins1987administrative",
            "golden1998rulemaking",
            "west2004formal",
            "yackeeYackee2006",
            "balla1998administrative",
            "naughton2009commenter",
            "acusMassComments2021",
            "nyagFakeComments2021",
        ],
        "minimum_keys": 5,
    },
    {
        "category": "revolving-door-and-intermediaries",
        "purpose": "Position post-government access and intermediary routing as substitution channels.",
        "signals": ["revolving-door", "intermediaries", "messengers", "association"],
        "required_keys": [
            "lapiraThomas2017",
            "oecdLobbying2021",
            "carpenterMoss2014",
        ],
        "minimum_keys": 2,
    },
    {
        "category": "abm-and-validation",
        "purpose": "Justify mechanism simulation, ODD-style documentation, and validation boundaries.",
        "signals": ["agent-based", "mechanism model", "odd", "validation"],
        "required_keys": [
            "epstein1999generative",
            "windrum2007empirical",
            "grimm2010odd",
        ],
        "minimum_keys": 3,
    },
    {
        "category": "public-data-bridge",
        "purpose": "Show that empirical-source claims are source-backed but bounded.",
        "signals": ["public administrative data", "source moments", "validation gaps", "bounded"],
        "required_keys": [
            "ldaData",
            "fecData",
            "federalRegisterApi",
            "regulationsGovApi",
            "nycCfbData",
            "seattleVouchers",
            "irsEoBmf",
            "usaspending",
        ],
        "minimum_keys": 6,
    },
]


def main() -> int:
    body = read_text(BODY)
    references = read_text(REFERENCES)
    cited_keys = extract_cited_keys(body)
    bibliography_keys = extract_bibliography_keys(references)
    rows = [category_row(category, body, cited_keys, bibliography_keys) for category in CATEGORIES]
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_CSV, rows)
    OUTPUT_MD.write_text(markdown(rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 1 if any(row["status"] == "blocked" for row in rows) else 0


def category_row(
        category: dict[str, object],
        body: str,
        cited_keys: set[str],
        bibliography_keys: set[str],
) -> dict[str, str]:
    lowered = body.lower()
    signals = [signal for signal in category["signals"] if signal.lower() in lowered]
    required_keys = list(category["required_keys"])
    missing_bibliography = [key for key in required_keys if key not in bibliography_keys]
    cited_required = [key for key in required_keys if key in cited_keys]
    missing_citations = [key for key in required_keys if key not in cited_keys]
    minimum_keys = int(category["minimum_keys"])
    if missing_bibliography:
        status = "blocked"
        detail = "required bibliography keys are missing"
    elif len(cited_required) >= minimum_keys and signals:
        status = "ready"
        detail = "minimum citation and manuscript-signal coverage present"
    elif cited_required and signals:
        status = "partial"
        detail = "some citation and manuscript-signal coverage present"
    else:
        status = "blocked"
        detail = "category lacks either citation coverage or manuscript signals"
    return {
        "category": str(category["category"]),
        "status": status,
        "purpose": str(category["purpose"]),
        "bodySignals": "; ".join(signals) or "none",
        "requiredCitationKeys": "; ".join(required_keys),
        "citedRequiredKeys": "; ".join(cited_required) or "none",
        "missingRequiredCitationKeys": "; ".join(missing_citations) or "none",
        "missingBibliographyKeys": "; ".join(missing_bibliography) or "none",
        "detail": detail,
    }


def extract_cited_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}", text):
        for key in match.group(1).split(","):
            cleaned = key.strip()
            if cleaned:
                keys.add(cleaned)
    return keys


def extract_bibliography_keys(text: str) -> set[str]:
    return set(re.findall(r"@[a-zA-Z]+\{([^,\s]+)", text))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "category",
        "status",
        "purpose",
        "bodySignals",
        "requiredCitationKeys",
        "citedRequiredKeys",
        "missingRequiredCitationKeys",
        "missingBibliographyKeys",
        "detail",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown(rows: list[dict[str, str]]) -> str:
    counts = {
        status: sum(1 for row in rows if row["status"] == status)
        for status in ("ready", "partial", "blocked")
    }
    lines = [
        "# Literature Positioning Audit",
        "",
        (
            "This audit checks whether the manuscript cites and uses the scholarly "
            "neighborhoods needed for a regulatory-governance mechanism-model paper. "
            "It does not judge prose quality or venue persuasiveness."
        ),
        "",
        "## Summary",
        "",
        f"- Ready categories: `{counts['ready']}`.",
        f"- Partial categories: `{counts['partial']}`.",
        f"- Blocked categories: `{counts['blocked']}`.",
        "",
        "| Category | Status | Purpose | Body signals | Cited required keys | Missing cited keys |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {category} | {status} | {purpose} | {signals} | {cited} | {missing} |".format(
                category=cell(row["category"]),
                status=cell(row["status"]),
                purpose=cell(row["purpose"]),
                signals=cell(row["bodySignals"]),
                cited=cell(row["citedRequiredKeys"]),
                missing=cell(row["missingRequiredCitationKeys"]),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            (
                "`ready` means the manuscript includes at least the minimum required "
                "citation keys for that literature category and contains relevant "
                "body-text signals. A human reader still needs to judge whether the "
                "positioning is persuasive and sufficiently developed for the target venue."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


if __name__ == "__main__":
    raise SystemExit(main())
