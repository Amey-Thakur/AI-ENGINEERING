"""
Phase 2, lesson 4: the check.

It computes the gradients by nudging, independently, and compares them with the
ones your backward pass produced. If your derivatives have a sign error or a
missing term, this is where it shows up, which is exactly the job gradient
checking does in real work.

Run it with:  python check.py
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPARISON = HERE / ".work" / "comparison.tsv"

XOR = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

START = {
    "h1_w1": 0.50, "h1_w2": -0.40, "h1_b": 0.10,
    "h2_w1": -0.30, "h2_w2": 0.60, "h2_b": -0.20,
    "out_h1": 0.70, "out_h2": -0.50, "out_b": 0.15,
}

NUDGE = 1e-5

# A hand written backward pass that agrees with a nudge to this much is right.
# Anything looser hides a real mistake; anything tighter fails on rounding.
TOLERANCE = 1e-6


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def sigmoid(total):
    return 1.0 / (1.0 + math.exp(-total))


def loss(weights):
    total = 0.0

    for (first, second), label in XOR:
        h1 = sigmoid(first * weights["h1_w1"] + second * weights["h1_w2"]
                     + weights["h1_b"])
        h2 = sigmoid(first * weights["h2_w1"] + second * weights["h2_w2"]
                     + weights["h2_b"])
        out = sigmoid(h1 * weights["out_h1"] + h2 * weights["out_h2"]
                      + weights["out_b"])

        total += (out - label) ** 2

    return total / len(XOR)


def by_nudging(name):
    nudged = dict(START)

    nudged[name] = START[name] + NUDGE
    higher = loss(nudged)

    nudged[name] = START[name] - NUDGE
    lower = loss(nudged)

    return (higher - lower) / (2 * NUDGE)


def main() -> None:
    if not COMPARISON.exists():
        fail(
            "there is no .work/comparison.tsv",
            "report, for every weight, the gradient from your backward pass "
            "and the gradient from nudging",
        )

    lines = COMPARISON.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["weight"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 3:
            fail(
                f"line {number} has {len(parts)} columns, and needs at least 3",
                "each row is the weight, the backward gradient, and the nudged one",
            )

        try:
            yours[parts[0].strip()] = (float(parts[1]), float(parts[2]))
        except ValueError:
            fail(
                f"line {number} has something that is not a number: {line!r}",
                "both gradients are numbers",
            )

    worst = 0.0

    for name in START:
        if name not in yours:
            fail(
                f"there is no row for {name}",
                f"all {len(START)} weights need a row",
            )

        backward, nudged = yours[name]
        truth = by_nudging(name)

        if abs(nudged - truth) > 1e-4:
            fail(
                f"the nudged gradient for {name} is reported as {nudged:+.6f}, "
                f"and measuring gives {truth:+.6f}",
                "measure at the starting weights, before taking any step",
            )

        gap = abs(backward - truth)
        worst = max(worst, gap)

        if gap > TOLERANCE:
            hint = ("the sign is wrong, so training would climb rather than "
                    "descend") if (backward > 0) != (truth > 0) else (
                "check the sigmoid slope, s times one minus s, and that each "
                "weight's gradient is its delta times the value it multiplied")

            fail(
                f"your backward pass gives {backward:+.6f} for {name}, and "
                f"nudging gives {truth:+.6f}",
                hint,
            )

    print(f"PASS  all {len(START)} backward gradients agree with nudging "
          f"to within {worst:.0e}")


if __name__ == "__main__":
    main()
