"""
Phase 2, lesson 5: the check.

It scores your predictions itself and compares that with the accuracy you
reported, and it works out the hand written rule's score independently. The
network may do badly and still pass. A comparison that flatters it will not.

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

    prediction_rows = read_rows(PREDICTIONS, "your network's prediction for "
                                             "every held back message")

    if prediction_rows and prediction_rows[0][0] == "predicted":
        prediction_rows = prediction_rows[1:]

    if len(prediction_rows) != len(held_back):
        fail(
            f"you predicted {len(prediction_rows)} messages, and there are "
            f"{len(held_back)} held back",
            "predict rows 41 to 60, one row each",
        )

    right = 0
    for number, parts in enumerate(prediction_rows, start=2):
        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is the prediction, a tab, then the message",
            )

        guess, message = parts[0].strip(), parts[1].strip()

        if message not in truth:
            fail(
                f"line {number} is not a held back message: {message!r}",
                "predict the last twenty messages, the ones training never saw",
            )

        right += guess == truth[message]

    measured = right / len(held_back)

    score_rows = read_rows(SCORES, "the accuracy of each model you compared")
    reported = {}

    for parts in score_rows:
        if len(parts) == 4 and parts[0] not in ("model",):
            try:
                reported[parts[0].strip()] = float(parts[3])
            except ValueError:
                fail(
                    f"the accuracy for {parts[0]} is not a number: {parts[3]!r}",
                    "write accuracy as a decimal, such as 0.7500",
                )

    if "network_test" not in reported:
        fail(
            "scores.tsv has no network_test row",
            "report the network on the held back messages, and the hand "
            "written rule on the same ones",
        )

    if abs(reported["network_test"] - measured) > TOLERANCE:
        fail(
            f"you report the network scoring {reported['network_test']:.1%} on "
            f"the held back messages, and your predictions score {measured:.1%}",
            "report the number your model actually produced",
        )

    rule_right = sum(
        1 for label, message in held_back
        if ("question" if message.split()[0] in OPENERS else "statement") == label
    )
    rule_score = rule_right / len(held_back)

    if "hand_rule_test" not in reported:
        fail(
            "scores.tsv has no hand_rule_test row",
            "a new model has to be compared against the old one, or the "
            "number means nothing",
        )

    if abs(reported["hand_rule_test"] - rule_score) > TOLERANCE:
        fail(
            f"you report the hand written rule scoring "
            f"{reported['hand_rule_test']:.1%}, and it scores {rule_score:.1%}",
            "score the rule from phase 1 lesson 2 on these same twenty messages",
        )

    print(f"PASS  network {right} of {len(held_back)}, {measured:.1%}, "
          f"reported honestly against the rule's {rule_score:.1%}")


if __name__ == "__main__":
    main()
