"""
File: tools/run_lessons.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Runs every lesson and reports which ones still work.

For each lesson it empties the working folder, runs solve.py, then runs
check.py, with the network closed for both. That sequence is the quality bar of
this course. If a solution stops working, this fails. If a check is too loose to
notice a wrong answer, the lesson it guards is not finished.

Usage:
    python tools/run_lessons.py                 every lesson
    python tools/run_lessons.py phases/00       one phase, or one lesson
    python tools/run_lessons.py --list          name them and stop
"""

from __future__ import annotations

import argparse
import shutil
import sys

import lesson


def clean(directory) -> None:
    """Each run starts from nothing, so nothing passes on yesterday's files."""
    work = directory / ".work"

    if work.exists():
        shutil.rmtree(work, ignore_errors=True)

    work.mkdir(parents=True, exist_ok=True)


def indent(text: str) -> str:
    return "\n".join("      " + line for line in text.splitlines()) or "      (silent)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the lessons.")
    parser.add_argument("selector", nargs="?", help="a phase or lesson path")
    parser.add_argument("--list", action="store_true", help="name them and stop")
    arguments = parser.parse_args()

    selected = lesson.find(arguments.selector)

    if not selected:
        print("No lessons matched.", file=sys.stderr)
        return 1

    if arguments.list:
        for directory in selected:
            print(lesson.name(directory))
        return 0

    env = lesson.environment()
    failures: list[tuple[str, str]] = []
    total = 0.0

    for directory in selected:
        where = lesson.name(directory)
        gaps = lesson.missing(directory)

        if gaps:
            print(f"FAIL  {where}")
            print(f"      missing {', '.join(gaps)}")
            failures.append((where, f"missing {', '.join(gaps)}"))
            continue

        clean(directory)

        for script in ("solve.py", "check.py"):
            ok, output, seconds = lesson.run(directory, script, env)
            total += seconds

            if not ok:
                print(f"FAIL  {where}  {script}")
                print(indent(output))
                failures.append((where, f"{script} failed"))
                break
        else:
            print(f"pass  {where}")

    print()
    print(f"{len(selected) - len(failures)} of {len(selected)} lessons pass, "
          f"{total:.1f}s total")

    if failures:
        print()
        print("Failed:")
        for where, reason in failures:
            print(f"  {where}: {reason}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
