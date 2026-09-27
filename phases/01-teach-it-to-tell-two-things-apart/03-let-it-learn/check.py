"""
Lesson 3: the check.

It reads the weights you learned, builds a classifier out of them, and scores
it on the messages. It does not look at how you trained, only at whether the
numbers you ended up with actually decide anything.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
WEIGHTS = HERE / ".work" / "weights.tsv"

BIAS = "__bias__"

# The hand written rule in lesson 2 scored 95%. A learned model that cannot
# clear 90% on the very data it learned from has not learned.
NEEDED = 0.90


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
                rows.append((label, set(message.split())))

    return rows


def read_weights():
    lines = WEIGHTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["word"]:
        lines = lines[1:]

    weights, bias = {}, 0.0

    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is a word, a tab, and its weight",
            )

        try:
            value = float(parts[1])
        except ValueError:
            fail(
                f"line {number} has a weight that is not a number: {parts[1]!r}",
                "weights are numbers, and may be negative",
            )

        if parts[0] == BIAS:
            bias = value
        else:
            weights[parts[0]] = value

    return weights, bias


def main() -> None:
    if not WEIGHTS.exists():
        fail(
            "there is no .work/weights.tsv",
            "write one row per word with the weight you learned, plus a row "
            f"called {BIAS} for the bias",
        )

    weights, bias = read_weights()

    if not weights:
        fail(
            "weights.tsv has no words in it",
            "the file needs a row per word your training touched",
        )

    if all(value == 0 for value in weights.values()):
        fail(
            "every weight is zero, so the model decides nothing",
            "the weights only move when the current ones get a message wrong: "
            "check that your update runs on a mistake",
        )

    rows = read_messages()
    right = 0

    for label, words in rows:
        total = bias + sum(weights.get(word, 0) for word in words)
        right += (total > 0) == (label == "question")

    score = right / len(rows)

    if score < NEEDED:
        fail(
            f"the learned weights get {right} of {len(rows)} right, {score:.1%}, "
            f"and they need {NEEDED:.0%}",
            "check that you move the weights towards the right answer on a "
            "mistake, and that you make more than one pass over the messages",
        )

    print(f"PASS  {len(weights)} weights, {right} of {len(rows)} right, {score:.1%}")


if __name__ == "__main__":
    main()
