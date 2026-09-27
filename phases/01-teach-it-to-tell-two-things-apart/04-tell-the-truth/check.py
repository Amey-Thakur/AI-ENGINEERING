"""
Lesson 4: the check.

This one is unusual. It does not mainly ask whether your model is good. It asks
whether the number you wrote down is the number you actually got.

It rebuilds your classifier from your weights, scores it on the held back
messages itself, and compares that with what you reported. A model that scores
badly still passes. A report that does not match the model does not.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
WEIGHTS = HERE / ".work" / "weights.tsv"
SCORES = HERE / ".work" / "scores.tsv"

TRAIN_SIZE = 40
BIAS = "__bias__"

# Low on purpose. The lesson is about honesty, not about a high score.
NEEDED = 0.60
TOLERANCE = 0.02


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


def read_table(path, name):
    if not path.exists():
        fail(
            f"there is no .work/{path.name}",
            f"write {name}",
        )

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return [line.split("\t") for line in lines if line.strip()]


def main() -> None:
    weight_rows = read_table(WEIGHTS, "the weights you trained")
    score_rows = read_table(SCORES, "the scores you measured")

    weights, bias = {}, 0.0

    for parts in weight_rows[1:] if weight_rows[0][0] == "word" else weight_rows:
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
            "no usable weights were found in weights.tsv",
            "each row is a word, a tab, and a number",
        )

    reported = {}
    for parts in score_rows:
        if len(parts) == 4 and parts[0] in ("train", "test"):
            try:
                reported[parts[0]] = float(parts[3])
            except ValueError:
                fail(
                    f"the accuracy on the {parts[0]} row is not a number: {parts[3]!r}",
                    "write the accuracy as a decimal, such as 0.7500",
                )

    if "test" not in reported:
        fail(
            "scores.tsv has no test row",
            "report the split, how many were right, how many there were, and "
            "the accuracy, for both train and test",
        )

    rows = read_messages()
    held_back = rows[TRAIN_SIZE:]

    right = 0
    for label, words in held_back:
        total = bias + sum(weights.get(word, 0) for word in words)
        right += (total > 0) == (label == "question")

    truth = right / len(held_back)

    # The honesty check.
    if abs(truth - reported["test"]) > TOLERANCE:
        fail(
            f"you reported {reported['test']:.1%} on the held back messages, "
            f"but your weights score {truth:.1%} on them",
            "score the model on rows 41 to 60 only, and report what you measure",
        )

    if truth < NEEDED:
        fail(
            f"the model scores {truth:.1%} on messages it never saw, and it "
            f"needs {NEEDED:.0%}",
            "train on the first 40 rows only, for several passes, then score "
            "on the last 20",
        )

    print(f"PASS  {right} of {len(held_back)} right on messages it never saw, "
          f"{truth:.1%}, and that is what you reported")


if __name__ == "__main__":
    main()
