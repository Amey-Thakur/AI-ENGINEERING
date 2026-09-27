"""
Lesson 2: the check.

It scores your predictions against the real labels. It does not care what your
rule is, only that it beats guessing by a clear margin, so any sensible rule
passes and a coin toss does not.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
PREDICTIONS = HERE / ".work" / "predictions.tsv"

# Always guessing the commoner kind scores 50% on this data. A rule worth
# writing has to be well clear of that.
NEEDED = 0.80

LABELS = {"question", "statement"}


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
                rows.append((label, message))

    return rows


def main() -> None:
    if not PREDICTIONS.exists():
        fail(
            "there is no .work/predictions.tsv",
            "write one row per message: your prediction, a tab, the message",
        )

    lines = PREDICTIONS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["predicted"]:
        lines = lines[1:]

    rows = read_messages()

    if len(lines) != len(rows):
        fail(
            f"you predicted {len(lines)} messages, and there are {len(rows)}",
            "every message needs exactly one prediction, in the order they appear",
        )

    right = 0
    truth = {message: label for label, message in rows}

    for number, line in enumerate(lines, start=1):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is your prediction, a tab, then the message",
            )

        guess, message = parts[0].strip(), parts[1].strip()

        if guess not in LABELS:
            fail(
                f"line {number} predicts {guess!r}",
                "a prediction is either question or statement",
            )

        if message not in truth:
            fail(
                f"line {number} has a message that is not in the data: {message!r}",
                "copy the messages through unchanged, so each prediction can be scored",
            )

        right += guess == truth[message]

    score = right / len(rows)

    if score < NEEDED:
        fail(
            f"the rule gets {right} of {len(rows)} right, {score:.1%}, "
            f"and it needs {NEEDED:.0%}",
            "look at which words the last lesson showed leaning towards a "
            "question, and at where they sit in the sentence",
        )

    print(f"PASS  {right} of {len(rows)} right, {score:.1%}, against 50% for guessing")


if __name__ == "__main__":
    main()
