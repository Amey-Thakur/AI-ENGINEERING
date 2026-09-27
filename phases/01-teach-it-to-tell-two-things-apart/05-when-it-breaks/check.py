"""
Lesson 5: the check.

It rebuilds your model from your weights, works out which held back messages it
gets wrong, and compares that with the list you wrote. Your model may be any
good or bad; the list has to be the truth about it.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
WEIGHTS = HERE / ".work" / "weights.tsv"
ERRORS = HERE / ".work" / "errors.tsv"

TRAIN_SIZE = 40
BIAS = "__bias__"


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


def read_weights():
    if not WEIGHTS.exists():
        fail(
            "there is no .work/weights.tsv",
            "train on the first 40 messages and write the weights out, as in "
            "lesson 4",
        )

    weights, bias = {}, 0.0

    for line in WEIGHTS.read_text(encoding="utf-8").strip().splitlines():
        parts = line.split("\t")

        if len(parts) != 2:
            continue

        try:
            value = float(parts[1])
        except ValueError:
            continue

        if parts[0] == BIAS:
            bias = value
        else:
            weights[parts[0]] = value

    if not weights:
        fail(
            "no usable weights were found",
            "each row is a word, a tab, and a number",
        )

    return weights, bias


def main() -> None:
    weights, bias = read_weights()

    if not ERRORS.exists():
        fail(
            "there is no .work/errors.tsv",
            "list every held back message your model gets wrong, with what it "
            "really is, what the model called it, and the score",
        )

    held_back = read_messages()[TRAIN_SIZE:]

    truth = {}
    for label, message in held_back:
        total = bias + sum(weights.get(word, 0) for word in set(message.split()))
        guess = "question" if total > 0 else "statement"

        if guess != label:
            truth[message] = (label, guess)

    lines = ERRORS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["message"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 3:
            fail(
                f"line {number} has {len(parts)} columns, and needs at least 3",
                "each row is the message, what it really is, what the model "
                "called it, and the score",
            )

        yours[parts[0].strip()] = (parts[1].strip(), parts[2].strip())

    missing = sorted(set(truth) - set(yours))
    if missing:
        fail(
            f"your model gets {len(missing)} message(s) wrong that are not in "
            f"your list, the first being {missing[0]!r}",
            "list every held back message the model gets wrong, not a selection",
        )

    extra = sorted(set(yours) - set(truth))
    if extra:
        fail(
            f"your list has {len(extra)} message(s) your model actually gets "
            f"right, the first being {extra[0]!r}",
            "check you are scoring the held back messages, rows 41 to 60",
        )

    for message, (label, guess) in truth.items():
        if yours[message] != (label, guess):
            fail(
                f"for {message!r} you wrote {yours[message]}, but the model "
                f"really calls it a {guess} when it is a {label}",
                "copy what your model actually did, not what it should do",
            )

    print(f"PASS  {len(truth)} failures found and every one described correctly")


if __name__ == "__main__":
    main()
