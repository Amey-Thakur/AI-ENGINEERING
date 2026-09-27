"""
Phase 3, lesson 1: the check.

It counts the vocabulary and measures the distances itself, then compares with
what you reported.

Run it with:  python check.py
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
FINDINGS = HERE / ".work" / "findings.tsv"

TRAIN_SIZE = 40
TOLERANCE = 1e-4

PAIRS = [
    ("server", "deployment"),
    ("password", "vault"),
    ("server", "friday"),
    ("password", "tuesday"),
]


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_messages():
    rows = []

    with open(MESSAGES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.strip()
            if line:
                label, message = line.split("\t")
                rows.append((label, message.split()))

    return rows


def main() -> None:
    if not FINDINGS.exists():
        fail(
            "there is no .work/findings.tsv",
            "report the size of the training vocabulary, how many held back "
            "words are new, and the distance between each pair",
        )

    lines = FINDINGS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["finding"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is the name of a finding and its value",
            )

        try:
            yours[parts[0].strip()] = float(parts[1])
        except ValueError:
            fail(
                f"line {number} has a value that is not a number: {parts[1]!r}",
                "every finding here is a number",
            )

    rows = read_messages()
    known = {word for _, words in rows[:TRAIN_SIZE] for word in words}
    unseen = [word for _, words in rows[TRAIN_SIZE:] for word in words
              if word not in known]

    expected = {
        "vocabulary_trained": float(len(known)),
        "unseen_words_in_held_back": float(len(unseen)),
    }

    # In a one-hot representation every distinct pair is the same distance
    # apart, and that distance is the square root of two.
    for first, second in PAIRS:
        expected[f"distance_{first}_{second}"] = math.sqrt(2)

    for name, want in expected.items():
        if name not in yours:
            fail(
                f"there is no row for {name}",
                "report every finding the lesson asks for",
            )

        if abs(yours[name] - want) > TOLERANCE:
            fail(
                f"{name} is reported as {yours[name]:g}, and it is {want:g}",
                "count the words seen in the first 40 messages, and measure "
                "the distance between one-hot vectors",
            )

    distances = {round(yours[f"distance_{a}_{b}"], 6) for a, b in PAIRS}

    if len(distances) != 1:
        fail(
            f"the four pairs come out at {len(distances)} different distances",
            "in a one-hot representation every distinct pair is equally far "
            "apart, so all four should be identical",
        )

    print(f"PASS  {len(known)} words trained, {len(unseen)} unseen, and all "
          f"four pairs exactly {math.sqrt(2):.6f} apart")


if __name__ == "__main__":
    main()
