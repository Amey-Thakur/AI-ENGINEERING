"""
Phase 3, lesson 5: the check.

It scores your predictions itself and compares them with the accuracy you
reported, and works out the hand written rule independently. A result that is
worse than everything before it still passes. A comparison that hides that
does not.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
SCORES = HERE / ".work" / "scores.tsv"
PREDICTIONS = HERE / ".work" / "predictions.tsv"

TRAIN_SIZE = 40
TOLERANCE = 0.02

OPENERS = {
    "what", "how", "why", "who", "where", "when", "which",
    "is", "are", "was", "were", "do", "does", "did",
    "can", "could", "should", "would", "will", "have", "has",
}


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


def read_rows(path, name):
    if not path.exists():
        fail(f"there is no .work/{path.name}", f"write {name}")

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return [line.split("\t") for line in lines if line.strip()]


def main() -> None:
    held_back = read_messages()[TRAIN_SIZE:]
    truth = {message: label for label, message in held_back}

    rows = read_rows(PREDICTIONS, "a prediction for every held back message")

    if rows and rows[0][0] == "predicted":
        rows = rows[1:]

    if len(rows) != len(held_back):
        fail(
            f"you predicted {len(rows)} messages, and {len(held_back)} were "
            f"held back",
            "predict rows 41 to 60, one row each",
        )

    right = 0
    for number, parts in enumerate(rows, start=2):
        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is the prediction, a tab, then the message",
            )

        guess, message = parts[0].strip(), parts[1].strip()

        if message not in truth:
            fail(
                f"line {number} is not a held back message: {message!r}",
                "predict the last twenty messages",
            )

        right += guess == truth[message]

    measured = right / len(held_back)

    reported = {}
    for parts in read_rows(SCORES, "what each approach scored"):
        if len(parts) == 2 and parts[0] != "measure":
            try:
                reported[parts[0].strip()] = float(parts[1])
            except ValueError:
                fail(
                    f"the value for {parts[0]} is not a number: {parts[1]!r}",
                    "every value in scores.tsv is a number",
                )

    if "vectors_test" not in reported:
        fail(
            "scores.tsv has no vectors_test row",
            "report what the word vectors scored on the held back messages",
        )

    if abs(reported["vectors_test"] - measured) > TOLERANCE:
        fail(
            f"you report {reported['vectors_test']:.1%} on the held back "
            f"messages, and your predictions score {measured:.1%}",
            "report the number your model produced, whatever it is",
        )

    rule_right = sum(
        1 for label, message in held_back
        if ("question" if message.split()[0] in OPENERS else "statement") == label
    )
    rule = rule_right / len(held_back)

    if "hand_rule_test" not in reported:
        fail(
            "scores.tsv has no hand_rule_test row",
            "a result means nothing without the thing it is being compared to",
        )

    if abs(reported["hand_rule_test"] - rule) > TOLERANCE:
        fail(
            f"you report the hand written rule at "
            f"{reported['hand_rule_test']:.1%}, and it scores {rule:.1%}",
            "score the rule from phase 1 on these same twenty messages",
        )

    verdict = "worse than" if measured < rule else "at least"
    print(f"PASS  word vectors {right} of {len(held_back)}, {measured:.1%}, "
          f"reported honestly as {verdict} the rule's {rule:.1%}")


if __name__ == "__main__":
    main()
