"""
Phase 2, lesson 3: how wrong, and in which direction.

Replaces the hard threshold with a smooth curve, measures how wrong the network
is as a single number, and then measures the slope of that number against every
weight by nudging each one and watching what happens.

Nudging is not how real training computes gradients, and it is not meant to be.
It is the definition of a slope, written out, and it needs no calculus to
believe. The next lesson computes the same numbers a thousand times faster, and
checks itself against these.

Run it with:  python solve.py
"""

import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADIENTS = HERE / ".work" / "gradients.tsv"

XOR = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

# Chosen, not random, so this runs the same everywhere. They are deliberately
# asymmetric: two units that start identical stay identical forever.
START = {
    "h1_w1": 0.50, "h1_w2": -0.40, "h1_b": 0.10,
    "h2_w1": -0.30, "h2_w2": 0.60, "h2_b": -0.20,
    "out_h1": 0.70, "out_h2": -0.50, "out_b": 0.15,
}

# How far to nudge a weight when measuring its slope.
NUDGE = 1e-5


def sigmoid(total):
    """The step function, smoothed, so it has a slope everywhere."""
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
    """One number for how wrong the whole network is: mean squared error."""
    total = 0.0

    for point, label in XOR:
        gap = predict(point, weights) - label
        total += gap * gap

    return total / len(XOR)


def slope(weights, name):
    """How much the loss changes as this one weight moves.

    Nudge it up, nudge it down, see how far the loss moved, divide by the
    distance travelled. That is what a slope is.
    """
    nudged = dict(weights)

    nudged[name] = weights[name] + NUDGE
    higher = loss(nudged)

    nudged[name] = weights[name] - NUDGE
    lower = loss(nudged)

    return (higher - lower) / (2 * NUDGE)


def main() -> None:
    weights = dict(START)
    gradients = {name: slope(weights, name) for name in weights}

    GRADIENTS.parent.mkdir(parents=True, exist_ok=True)

    with open(GRADIENTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("weight\tvalue\tgradient\n")
        for name in START:
            handle.write(f"{name}\t{weights[name]:.6f}\t{gradients[name]:.6f}\n")

    print(f"Loss at the start: {loss(weights):.6f}")
    print()
    print("  weight     value     slope     move it")

    for name in START:
        direction = "down" if gradients[name] > 0 else "up"
        print(f"  {name:9} {weights[name]:+.2f}   {gradients[name]:+.6f}   "
              f"{direction}")

    print()

    # Now walk downhill, recording the loss as it goes.
    rate = 0.5
    marks = (1, 10, 100, 1000, 2000, 5000, 10000, 20000)
    walking = dict(weights)

    print("  steps     loss")

    for step in range(1, max(marks) + 1):
        slopes = {name: slope(walking, name) for name in walking}
        walking = {name: walking[name] - rate * slopes[name] for name in walking}

        if step in marks:
            print(f"  {step:6}    {loss(walking):.6f}")

    print()
    print("What it answers now, against what it should:")

    for point, label in XOR:
        print(f"  {point[0]}, {point[1]}   {predict(point, walking):.3f}   "
              f"wanted {label}")


if __name__ == "__main__":
    main()
