#!/usr/bin/env python3
"""Report simple diagnostics for formulaic academic prose.

Usage:
    python style_audit.py passage.txt
    Get-Content passage.txt -Raw | python style_audit.py -
    python style_audit.py passage.txt --json

The metrics are editing aids, not authorship or AI-detector predictions.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*|[\u3400-\u9fff]")
SENTENCE_RE = re.compile(r"[^.!?。！？]+[.!?。！？]+|[^.!?。！？]+$")
PARAGRAPH_RE = re.compile(r"\n\s*\n+")

CONNECTORS = (
    "furthermore",
    "moreover",
    "additionally",
    "however",
    "therefore",
)

PHRASES = (
    "it is worth noting that",
    "it is important to note",
    "plays a crucial role",
    "plays a pivotal role",
    "plays a vital role",
    "delve into",
    "shed light on",
    "in today's world",
    "in recent years",
    "with the rapid development of",
    "综上所述",
    "值得注意的是",
    "总而言之",
    "众所周知",
    "不难发现",
    "在当今社会",
    "随着",
)


def normalize_for_analysis(text: str) -> str:
    """Remove common Markdown scaffolding that would distort prose metrics."""
    kept_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^\s{0,3}#{1,6}\s+", line):
            continue
        if re.match(r"^\s*(?:[-*_]\s*){3,}$", line):
            continue
        if re.match(r"^\s*\|.*\|\s*$", line):
            continue
        if re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", line):
            continue
        line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"(?<!\\)[*_`]{1,3}", "", line)
        kept_lines.append(line)
    return "\n".join(kept_lines)


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def sentences(text: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(text) if tokens(match.group(0))]


def population_sd(values: list[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def normalized_opener(sentence: str, width: int = 3) -> str:
    opener_tokens = [token.lower() for token in tokens(sentence)[:width]]
    return " ".join(opener_tokens)


def audit(text: str) -> dict[str, object]:
    analyzed_text = normalize_for_analysis(text)
    sentence_list = sentences(analyzed_text)
    sentence_lengths = [len(tokens(sentence)) for sentence in sentence_list]
    word_count = len(tokens(analyzed_text))

    lowered = analyzed_text.lower()
    connector_counts = {
        connector: len(re.findall(rf"\b{re.escape(connector)}\b", lowered))
        for connector in CONNECTORS
    }
    connector_total = sum(connector_counts.values())
    connector_density = connector_total / word_count * 1000 if word_count else 0.0

    phrase_flags = {}
    for phrase in PHRASES:
        if re.search(r"[\u3400-\u9fff]", phrase):
            count = analyzed_text.count(phrase)
        else:
            count = len(re.findall(re.escape(phrase), lowered))
        if count:
            phrase_flags[phrase] = count

    opener_counts = Counter(
        opener
        for sentence in sentence_list
        if (opener := normalized_opener(sentence))
    )
    repeated_openers = [
        {"opener": opener, "count": count}
        for opener, count in opener_counts.most_common()
        if count > 1
    ][:10]

    paragraph_list = [
        paragraph.strip()
        for paragraph in PARAGRAPH_RE.split(analyzed_text.strip())
        if tokens(paragraph)
    ]
    paragraph_sentence_counts = [len(sentences(paragraph)) for paragraph in paragraph_list]
    extreme_paragraphs = sum(
        count <= 3 or count >= 8 for count in paragraph_sentence_counts
    )
    extreme_share = (
        extreme_paragraphs / len(paragraph_sentence_counts)
        if paragraph_sentence_counts
        else 0.0
    )

    return {
        "word_count": word_count,
        "sentence_count": len(sentence_list),
        "sentence_length": {
            "mean": round(sum(sentence_lengths) / len(sentence_lengths), 2)
            if sentence_lengths
            else 0.0,
            "sd": round(population_sd(sentence_lengths), 2),
            "min": min(sentence_lengths, default=0),
            "max": max(sentence_lengths, default=0),
        },
        "connector_counts": connector_counts,
        "connector_density_per_1000_words": round(connector_density, 2),
        "phrase_flags": phrase_flags,
        "repeated_openers": repeated_openers,
        "paragraph_count": len(paragraph_list),
        "paragraph_sentence_counts": paragraph_sentence_counts,
        "extreme_paragraph_share": round(extreme_share, 2),
        "disclaimer": "Diagnostics only; not an authorship or AI-detector prediction.",
    }


def read_text(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8-sig")


def render_text(report: dict[str, object]) -> str:
    sentence_length = report["sentence_length"]
    connector_counts = report["connector_counts"]
    phrase_flags = report["phrase_flags"]
    repeated_openers = report["repeated_openers"]

    lines = [
        f"Words: {report['word_count']}",
        f"Sentences: {report['sentence_count']}",
        (
            "Sentence length: "
            f"mean {sentence_length['mean']}, SD {sentence_length['sd']}, "
            f"range {sentence_length['min']}–{sentence_length['max']}"
        ),
        (
            "Connector density: "
            f"{report['connector_density_per_1000_words']} per 1,000 words "
            f"({sum(connector_counts.values())} total)"
        ),
        (
            "Paragraphs: "
            f"{report['paragraph_count']}; extreme-length share "
            f"{report['extreme_paragraph_share']}"
        ),
        f"Phrase flags: {json.dumps(phrase_flags, ensure_ascii=False)}",
        f"Repeated openers: {json.dumps(repeated_openers, ensure_ascii=False)}",
        str(report["disclaimer"]),
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default="-", help="UTF-8 text file or - for stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    try:
        text = read_text(args.source)
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))

    report = audit(text)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
