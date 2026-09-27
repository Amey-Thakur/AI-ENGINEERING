"""
Phase 3, lesson 4: the check.

This one checks a property rather than a number, on purpose.

A direction found by power iteration is just as valid pointing the other way,
and two correct implementations can order their directions differently. So
comparing your numbers against stored ones would fail honest work. What has to
survive compression is the structure: words used alike stay close, words used
differently stay apart. That is what is tested.

Run it with:  python check.py
"""

import sys
from math import sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
VECTORS = HERE / ".work" / "vectors.tsv"

# The profiles started at 608 numbers. Anything near that has not compressed.
MOST = 64

# Each row: a word, something it should be close to, something it should not.
# Every one is a fact about the corpus rather than about any implementation.
STRUCTURE = [
    ("server", "memory", "agenda"),
    ("deploy", "staging", "customer"),
    ("test", "bug", "server"),
    ("incident", "postmortem", "agenda"),
    ("meeting", "agenda", "memory"),
    ("customer", "account", "staging"),
]


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def closeness(first, second):
    left = sqrt(sum(value * value for value in first))
    right = sqrt(sum(value * value for value in second))

    if not left or not right:
        return 0.0

    return sum(a * b for a, b in zip(first, second)) / (left * right)


def main() -> None:
    if not VECTORS.exists():
        fail(
            "there is no .work/vectors.tsv",
            "write one row per common word: the word, then its squeezed vector",
        )

    lines = VECTORS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[0] == "word":
        lines = lines[1:]

    vectors = {}
    width = None

    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 3:
            fail(
                f"line {number} has {len(parts)} columns",
                "each row is a word followed by its numbers",
            )

        try:
            vectors[parts[0].strip()] = [float(value) for value in parts[1:]]
        except ValueError:
            fail(
                f"line {number} has a value that is not a number",
                "every column after the word is a number",
            )

        if width is None:
            width = len(parts) - 1
        elif len(parts) - 1 != width:
            fail(
                f"line {number} has {len(parts) - 1} numbers and earlier rows "
                f"have {width}",
                "every word needs a vector of the same length",
            )

    if width is None:
        fail("vectors.tsv has no words in it", "write a row per common word")

    if width > MOST:
        fail(
            f"each word still has {width} numbers",
            f"the point is compression: bring it under {MOST}",
        )

    for word, near, far in STRUCTURE:
        for needed in (word, near, far):
            if needed not in vectors:
                fail(
                    f"there is no vector for {needed!r}",
                    "include every word appearing at least 4 times in the corpus",
                )

        close = closeness(vectors[word], vectors[near])
        distant = closeness(vectors[word], vectors[far])

        if close <= distant:
            fail(
                f"{word!r} is no closer to {near!r} ({close:+.2f}) than to "
                f"{far!r} ({distant:+.2f})",
                "compression has lost the structure: check the surprise "
                "weighting is applied before squeezing, and that each new "
                "direction is kept clear of the ones already found",
            )

    print(f"PASS  {len(vectors)} words in {width} numbers each, and all "
          f"{len(STRUCTURE)} relationships survived the squeeze")


if __name__ == "__main__":
    main()
