#!/usr/bin/env python3
"""Approximate the Regulation & Governance manuscript word count."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper"
MIN_PREFERRED = 8000
MAX_PREFERRED = 10000
MAX_NORMAL = 11000
LOCAL_MANUSCRIPT = PAPER_DIR / "strategic-channel-substitution-regulatory-capture.tex"


def expand_inputs(path: Path, seen: set[Path] | None = None) -> str:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = path.read_text(encoding="utf-8")

    def replace_input(match: re.Match[str]) -> str:
        raw_name = match.group(1).strip()
        name = raw_name if raw_name.endswith(".tex") else f"{raw_name}.tex"
        input_path = (path.parent / name).resolve()
        if not input_path.exists():
            return ""
        return expand_inputs(input_path, seen)

    return re.sub(r"\\input\{([^}]+)\}", replace_input, text)


def strip_latex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", " ", text)
    text = re.sub(r"\\begin\{(?:equation|align|displaymath)\*?\}.*?\\end\{(?:equation|align|displaymath)\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\$.*?\$", " ", text, flags=re.S)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", r" \1 ", text)
    text = re.sub(r"[{}_^~&]", " ", text)
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z0-9'-]*", strip_latex(text)))


def main() -> int:
    manuscript = expand_inputs(LOCAL_MANUSCRIPT)
    bbl_path = LOCAL_MANUSCRIPT.with_suffix(".bbl")
    if bbl_path.exists():
        manuscript += "\n" + bbl_path.read_text(encoding="utf-8", errors="ignore")
    words = count_words(manuscript)
    print(
        "Approximate manuscript word count: "
        f"{words} / preferred {MIN_PREFERRED}-{MAX_PREFERRED}; normal upper {MAX_NORMAL}"
    )
    if words < MIN_PREFERRED:
        print(
            "Below the Regulation & Governance reported preferred "
            f"{MIN_PREFERRED}-{MAX_PREFERRED}-word range.",
            file=sys.stderr,
        )
        return 1
    if words > MAX_NORMAL:
        print(
            "Over the Regulation & Governance normal upper limit "
            f"of {MAX_NORMAL} words.",
            file=sys.stderr,
        )
        return 1
    if words > MAX_PREFERRED:
        print(
            "Above the Regulation & Governance preferred "
            f"{MIN_PREFERRED}-{MAX_PREFERRED}-word range but below the "
            f"{MAX_NORMAL}-word normal upper limit.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
