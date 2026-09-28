"""
File: tools/check_determinism.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Proves that a lesson prints the same thing on every run.

Every number shown in this course is compared against what the code actually
prints, which only means anything if the code prints the same thing every
time. Most of the ways it can fail to are quiet:

    max(set(labels), key=labels.count)

That picks a different winner on different runs when two labels tie, because
the order of a set of strings follows their hashes, and Python randomises
string hashes for every process unless told not to. A lesson written that way
passes on the machine it was written on, passes in review, and then fails on
one push in three with a diff nobody can reproduce.

The same applies to a dictionary built from a set, a sort with no tie break,
anything derived from a clock or a process id, and anything reading a machine
path. What they share is that they are invisible until the day they are not.

So each solution is run twice with deliberately different string hashing, and
the two outputs must match exactly. A lesson that disagrees with itself is
reported with the first line that differs.

Usage:
    python tools/check_determinism.py
    python tools/check_determinism.py phases/07
"""

from __future__ import annotations

import sys
from pathlib import Path

import lesson

#: Spread out on purpose. Neighbouring seeds often order a small set of short
#: strings the same way, so 0 and 1 together catch almost nothing: the tie that
#: prompted this file survives both and breaks at 5.
SEEDS = ("0", "5", "42")

#: Enough of a line to recognise it, without wrapping a terminal.
EXCERPT = 68


def first_difference(left: str, right: str) -> tuple[int, str, str]:
    """The line number and both versions of the first line that differs."""
    ours = left.splitlines()
    theirs = right.splitlines()

    for number, (mine, yours) in enumerate(zip(ours, theirs), start=1):
        if mine != yours:
            return number, mine, yours

    shorter = min(len(ours), len(theirs))
    longer = ours if len(ours) > len(theirs) else theirs

    return shorter + 1, "", longer[shorter] if longer[shorter:] else ""


def excerpt(line: str) -> str:
    line = line.strip()

    return line if len(line) <= EXCERPT else line[:EXCERPT - 3] + "..."


def main() -> int:
    selector = sys.argv[1] if len(sys.argv) > 1 else None
    lessons = lesson.find(selector)

    if not lessons:
        print(f"FAIL  no lesson matches {selector!r}")
        return 1

    unstable = 0

    for directory in lessons:
        outputs = []
        broke = False

        for seed in SEEDS:
            environment = lesson.environment()
            environment["PYTHONHASHSEED"] = seed
            ok, output, _ = lesson.run(directory, "solve.py", environment)

            if not ok:
                print(f"FAIL  {lesson.name(directory)} did not run with "
                      f"PYTHONHASHSEED={seed}")
                print(f"      {excerpt(output.splitlines()[-1] if output else '')}")
                unstable += 1
                broke = True
                break

            outputs.append(output)

        if broke:
            continue

        odd = next((index for index, output in enumerate(outputs)
                    if output != outputs[0]), None)

        if odd is not None:
            number, mine, yours = first_difference(outputs[0], outputs[odd])
            print(f"FAIL  {lesson.name(directory)} prints something different "
                  f"on another run, from line {number}")
            print(f"      with seed {SEEDS[0]}: {excerpt(mine)}")
            print(f"      with seed {SEEDS[odd]}: {excerpt(yours)}")
            print("      something in the lesson depends on the order of a "
                  "set, a clock, or the machine")
            unstable += 1

    print()
    print(f"{len(lessons) - unstable} of {len(lessons)} lessons print the "
          f"same thing on every run")

    return 1 if unstable else 0


if __name__ == "__main__":
    raise SystemExit(main())
