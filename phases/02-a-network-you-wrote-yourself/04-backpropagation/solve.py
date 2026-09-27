"""
Phase 2, lesson 4: backpropagation.

Computes every gradient in a single pass backwards through the network, and
then checks each one against the nudging method from lesson 3.

That check is the point of the lesson as much as the algorithm is. Backward
passes are written by hand, hand written derivatives have sign errors in them,
and a sign error does not crash: it trains slowly, or climbs, and looks like a
bad idea rather than a bug. Comparing against a nudge catches it in seconds.

Run it with:  python solve.py
"""

import math
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


def sigmoid(total):
    return 1.0 / (1.0 + math.exp(-total))


def forward(point, weights):
    """The forward pass, keeping every intermediate value.

    The values are kept because the backward pass needs them. That is not an
    implementation detail: it is why training a network costs so much more
    memory than running one.
    """
    first, second = point

    z1 = first * weights["h1_w1"] + second * weights["h1_w2"] + weights["h1_b"]
    h1 = sigmoid(z1)

    z2 = first * weights["h2_w1"] + second * weights["h2_w2"] + weights["h2_b"]
    h2 = sigmoid(z2)

    zo = h1 * weights["out_h1"] + h2 * weights["out_h2"] + weights["out_b"]
    out = sigmoid(zo)

    return h1, h2, out


def loss(weights):
    total = 0.0

    for point, label in XOR:
        _, _, out = forward(point, weights)
        total += (out - label) ** 2

    return total / len(XOR)


def backward(weights):
    """Every gradient, in one pass backwards from the answer to the inputs."""
    gradients = {name: 0.0 for name in weights}

    for point, label in XOR:
        first, second = point
        h1, h2, out = forward(point, weights)

        # How the loss changes with the answer, then with the total that made
        # it. The sigmoid's slope at a point is s * (1 - s), which is why the
        # forward values were kept.
        d_loss_d_out = 2 * (out - label) / len(XOR)
        delta_out = d_loss_d_out * out * (1 - out)

        # A weight's gradient is its delta times whatever it multiplied.
        gradients["out_h1"] += delta_out * h1
        gradients["out_h2"] += delta_out * h2
        gradients["out_b"] += delta_out

        # Hand the blame back. Each hidden unit is responsible in proportion
        # to the weight through which it spoke.
        delta_h1 = delta_out * weights["out_h1"] * h1 * (1 - h1)
        delta_h2 = delta_out * weights["out_h2"] * h2 * (1 - h2)

        gradients["h1_w1"] += delta_h1 * first
        gradients["h1_w2"] += delta_h1 * second
        gradients["h1_b"] += delta_h1

        gradients["h2_w1"] += delta_h2 * first
        gradients["h2_w2"] += delta_h2 * second
        gradients["h2_b"] += delta_h2

    return gradients


def by_nudging(weights, name):
    """Lesson 3's method, kept so this lesson can be checked against it."""
    nudged = dict(weights)

    nudged[name] = weights[name] + NUDGE
    higher = loss(nudged)

    nudged[name] = weights[name] - NUDGE
    lower = loss(nudged)

    return (higher - lower) / (2 * NUDGE)


def main() -> None:
    weights = dict(START)

    computed = backward(weights)
    measured = {name: by_nudging(weights, name) for name in weights}

    COMPARISON.parent.mkdir(parents=True, exist_ok=True)

    with open(COMPARISON, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("weight\tbackward\tnudged\tdifference\n")

        for name in START:
            gap = abs(computed[name] - measured[name])
            handle.write(f"{name}\t{computed[name]:.9f}\t"
                         f"{measured[name]:.9f}\t{gap:.2e}\n")

    print("  weight     backward       nudged      difference")

    worst = 0.0
    for name in START:
        gap = abs(computed[name] - measured[name])
        worst = max(worst, gap)
        print(f"  {name:9} {computed[name]:+.6f}   {measured[name]:+.6f}   "
              f"{gap:.1e}")

    print()
    print(f"Largest disagreement: {worst:.1e}")
    print()

    passes_backward = 1
    passes_nudging = 2 * len(START)

    print(f"Backward pass: {passes_backward} pass over the data for all "
          f"{len(START)} gradients")
    print(f"Nudging:       {passes_nudging} passes for the same {len(START)}")
    print(f"For a network with a million weights, that is 1 against 2,000,000.")


if __name__ == "__main__":
    main()
