"""
File: tools/progress.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Shows how far you have got, and what is next.

Progress here means one thing only: a check that passes. Not a lesson opened,
not a video watched, not a box ticked. Something you made, that a program looked
at and agreed was right. That is the only kind of progress worth counting,
because it is the only kind you cannot fool yourself about.

The board it prints is deliberately quiet. There are no points, no levels and
no streak to protect, because those measure attendance rather than skill and
they punish the week you were ill. What it shows is what you have proved, what
is next, and nothing else.

Usage:
    python tools/progress.py            the board
    python tools/progress.py --json     the same, for other tools to read
"""

from __future__ import annotations

import argparse
import json
import shutil

import lesson

FULL = "#"
EMPTY = "."


def title(directory) -> str:
    """A lesson's heading, taken from its own first line."""
    page = directory / "README.md"

    for line in page.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            # Lesson headings are numbered. The number is already in the path.
            if ". " in heading[:4]:
                return heading.split(". ", 1)[1]
            return heading

    return directory.name


def phase_title(directory) -> str:
    page = directory / "README.md"

    if page.exists():
        for line in page.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()

    return directory.name


def evaluate() -> list[dict]:
    """Runs every check and records what passed. Solutions are not run."""
    env = lesson.environment()
    results = []

    for directory in lesson.find():
        passed, output, _ = lesson.run(directory, "check.py", env)

        results.append({
            "phase": directory.parent.name,
            "lesson": directory.name,
            "path": lesson.name(directory),
            "title": title(directory),
            "passed": passed,
            "reason": "" if passed else first_reason(output),
        })

    return results


def first_reason(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("FAIL"):
            return line[4:].strip()

    return output.splitlines()[0] if output.splitlines() else "did not run"


def board(results: list[dict]) -> None:
    by_phase: dict[str, list[dict]] = {}

    for result in results:
        by_phase.setdefault(result["phase"], []).append(result)

    width = shutil.get_terminal_size((80, 20)).columns
    print()
    print("AI Engineering")
    print("=" * min(width, 72))
    print()

    for phase, entries in by_phase.items():
        done = sum(1 for entry in entries if entry["passed"])
        bar = FULL * done + EMPTY * (len(entries) - done)
        name = phase_title(lesson.PHASES / phase)

        print(f"  {name}")
        print(f"  {bar}  {done}/{len(entries)}")

        for entry in entries:
            mark = "done" if entry["passed"] else "    "
            print(f"    {mark}  {entry['title']}")
            if entry["reason"]:
                print(f"          {entry['reason']}")

        print()

    done = sum(1 for result in results if result["passed"])
    print("-" * min(width, 72))
    print(f"  {done} of {len(results)} checks pass")

    remaining = [result for result in results if not result["passed"]]

    if remaining:
        print(f"  Next: {remaining[0]['path']}")
    else:
        print("  Everything in the course so far is proved. Nothing is left undone.")

    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Show how far you have got.")
    parser.add_argument("--json", action="store_true", help="machine readable")
    arguments = parser.parse_args()

    results = evaluate()

    if arguments.json:
        print(json.dumps({
            "passed": sum(1 for result in results if result["passed"]),
            "total": len(results),
            "lessons": results,
        }, indent=2))
        return 0

    board(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
