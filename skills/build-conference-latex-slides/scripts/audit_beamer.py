#!/usr/bin/env python3
"""Static checks for academic Beamer conference decks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MECHANICAL_LABELS = (
    "Related work:",
    "Trade-war evidence:",
    "Construction references:",
    "Classification reference:",
    "Design reference:",
    "Related categorization evidence:",
    "foundations:",
)


def remove_balanced_command(text: str, command: str) -> str:
    marker = f"\\{command}{{"
    result: list[str] = []
    cursor = 0
    while True:
        start = text.find(marker, cursor)
        if start < 0:
            result.append(text[cursor:])
            break
        result.append(text[cursor:start])
        depth = 1
        index = start + len(marker)
        while index < len(text) and depth:
            if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
                depth += 1
            elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
                depth -= 1
            index += 1
        cursor = index
    return "".join(result)


def strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        match = re.search(r"(?<!\\)%", line)
        lines.append(line[: match.start()] if match else line)
    return "\n".join(lines)


def frame_bodies(text: str) -> list[str]:
    return re.findall(
        r"\\begin\{frame\}(?:\[[^\]]*\])?(.*?)\\end\{frame\}",
        text,
        flags=re.DOTALL,
    )


def audit(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    clean = strip_comments(raw)
    appendix_at = clean.find("\\appendix")
    main = clean if appendix_at < 0 else clean[:appendix_at]
    visible_main = remove_balanced_command(main, "note")
    frames = frame_bodies(clean)
    main_frames = frame_bodies(main)

    slidecite_lines = [
        line.strip()
        for line in visible_main.splitlines()
        if re.match(r"^\s*\\slidecite\{", line)
    ]
    mechanical = [
        label for label in MECHANICAL_LABELS if label.lower() in visible_main.lower()
    ]
    titles = re.findall(r"\\frametitle\{([^{}]+)\}", clean)
    title_frame = frames[0] if frames else ""
    title_has_session_details = bool(
        re.search(
            r"(Room\s+\d+|\b\d{1,2}:\d{2}\s*--\s*\d{1,2}:\d{2}\b|"
            r"Corporate Finance:\s*)",
            title_frame,
            flags=re.IGNORECASE,
        )
    )
    generic_thanks = any(
        re.fullmatch(r"\s*(thank you|thanks)\s*", title, flags=re.IGNORECASE)
        for title in titles
    )

    warnings: list[str] = []
    if mechanical:
        warnings.append(
            "Mechanical visible citation labels in main talk: " + ", ".join(mechanical)
        )
    if len(slidecite_lines) > 1:
        warnings.append(
            f"Main talk has {len(slidecite_lines)} standalone slide citations; "
            "keep only sources that must remain fully visible."
        )
    if title_has_session_details:
        warnings.append("Title page contains session, room, or time details.")
    if generic_thanks:
        warnings.append("Deck contains a generic Thank You/Thanks frame title.")
    if "\\note{[Sources]" not in clean:
        warnings.append("No structured [Sources] speaker notes found.")
    if not frames:
        warnings.append("No Beamer frames detected.")

    return {
        "path": str(path.resolve()),
        "frame_count": len(frames),
        "main_frame_count": len(main_frames),
        "appendix_frame_count": len(frames) - len(main_frames),
        "frametitles": titles,
        "main_visible_slidecite_count": len(slidecite_lines),
        "main_visible_slidecites": slidecite_lines,
        "mechanical_citation_labels": mechanical,
        "title_has_session_details": title_has_session_details,
        "generic_thank_you": generic_thanks,
        "source_note_count": clean.count("\\note{[Sources]"),
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex_file", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not args.tex_file.is_file():
        parser.error(f"file not found: {args.tex_file}")

    report = audit(args.tex_file)
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"File: {report['path']}")
        print(
            "Frames: "
            f"{report['frame_count']} "
            f"(main {report['main_frame_count']}, "
            f"appendix {report['appendix_frame_count']})"
        )
        print(
            "Visible standalone citations in main talk: "
            f"{report['main_visible_slidecite_count']}"
        )
        print(f"Structured source notes: {report['source_note_count']}")
        warnings = report["warnings"]
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"- {warning}")
        else:
            print("Warnings: none")

    return 1 if args.strict and report["warnings"] else 0


if __name__ == "__main__":
    sys.exit(main())
