"""
Phase 2, lesson 3: the check.

It measures the slopes itself, from the same starting weights, and compares
them with the ones you reported. Gradients are a fact about the network, so
there is one right answer here and the check knows it independently.

Run it with:  python check.py
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADIENTS = HERE / ".work" / "gradients.tsv"

XOR = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

START = {
    "h1_w1": 0.50, "h1_w2": -0.40, "h1_b": 0.10,
    "h2_w1": -0.30, "h2_w2": 0.60, "h2_b": -0.20,
    "out_h1": 0.70, "out_h2": -0.50, "out_b": 0.15,
}

NUDGE = 1e-5
TOLERANCE = 1e-4


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def sigmoid(total):
    return 1.0 / (1.0 + math.exp(-total))


def predict(point, weights):
    first, second = point

    h1 = sigmoid(first * weights["h1_w1"] + second * weights["h1_w2"]
                 + weights["h1_b"])
    h2 = sigmoid(first * weights["h2_w1"] + second * weights["h2_w2"]
                 + weights["h2_b"])

    return sigmoid(h1 * weights["out_h1"] + h2 * weights["out_h2"]
                   + weights["out_b"])


def loss(weights):
    total = 0.0

    for point, label in XOR:
        gap = predict(point, weights) - label
        total += gap * gap

    return total / len(XOR)


def slope(weights, name):
    nudged = dict(weights)

    nudged[name] = weights[name] + NUDGE
    higher = loss(nudged)

    nudged[name] = weights[name] - NUDGE
    lower = loss(nudged)

    return (higher - lower) / (2 * NUDGE)


def main() -> None:
    if not GRADIENTS.exists():
        fail(
            "there is no .work/gradients.tsv",
            "report, for every weight, its value and the slope of the loss "
            "against it",
        )

    lines = GRADIENTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["weight"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 3:
            fail(
                f"line {number} has {len(parts)} columns, not 3",
                "each row is the weight name, its value, and its gradient",
            )

        try:
            yours[parts[0].strip()] = (float(parts[1]), float(parts[2]))
        except ValueError:
            fail(
                f"line {number} has something that is not a number: {line!r}",
                "the value and the gradient are both numbers",
            )

    for name in START:
        if name not in yours:
            fail(
                f"there is no row for {name}",
                f"all {len(START)} weights need a row",
            )

        value, reported = yours[name]

        if abs(value - START[name]) > 1e-6:
            fail(
                f"{name} is reported at {value}, and the lesson starts it at "
                f"{START[name]}",
                "measure the slopes at the starting weights, before any step",
            )

        truth = slope(START, name)

        if abs(reported - truth) > TOLERANCE:
            fail(
                f"the slope for {name} is reported as {reported:+.6f}, and "
                f"measuring gives {truth:+.6f}",
                "nudge the weight up and down by the same small amount, and "
                "divide the change in loss by the total distance moved",
            )

        # A sign error is the easiest mistake to make here and the most
        # confusing later, because training then climbs instead of descending.
        if reported != 0 and (reported > 0) != (truth > 0):
            fail(
                f"the slope for {name} has the wrong sign",
                "a positive slope means the loss rises as the weight rises, "
                "so the weight should move down",
            )

    print(f"PASS  all {len(START)} gradients match an independent measurement")


if __name__ == "__main__":
    main()
