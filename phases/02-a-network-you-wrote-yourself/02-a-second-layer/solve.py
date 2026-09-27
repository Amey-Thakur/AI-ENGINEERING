"""
Phase 2, lesson 2: a second layer.

Builds a two layer network by hand, with weights chosen rather than learned,
and shows it getting all four XOR points right.

Choosing the weights by hand matters here. Lesson 1 proved no single line can
do this, and the interesting question is what a second layer adds. If the
weights were learned you would be watching two things at once and could not
tell which was responsible. Here nothing learns, so anything that works is the
architecture working.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
NETWORK = HERE / ".work" / "network.tsv"

XOR = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

# Each row is one unit: what it weights its two inputs by, and its bias.
UNITS = {
    # Fires when at least one input is on. That is OR, and OR is a line.
    "hidden_either": (1.0, 1.0, -0.5),

    # Fires when both inputs are on. That is AND, and AND is a line too.
    "hidden_both": (1.0, 1.0, -1.5),

    # Reads the two above rather than the original inputs: either, and not
    # both. Also a line, but drawn over better questions.
    "output": (1.0, -1.0, -0.5),
}


def unit(first, second, weights):
    """One weighted sum and a threshold. The same piece as phase 1."""
    w1, w2, bias = weights
    return 1 if first * w1 + second * w2 + bias > 0 else 0


def run(point):
    """The forward pass: inputs to hidden layer, hidden layer to answer."""
    either = unit(point[0], point[1], UNITS["hidden_either"])
    both = unit(point[0], point[1], UNITS["hidden_both"])
    answer = unit(either, both, UNITS["output"])

    return either, both, answer


def main() -> None:
    NETWORK.parent.mkdir(parents=True, exist_ok=True)

    with open(NETWORK, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("unit\tw1\tw2\tbias\n")

        for name, (w1, w2, bias) in UNITS.items():
            handle.write(f"{name}\t{w1:g}\t{w2:g}\t{bias:g}\n")

    right = 0
    rows = []

    for point, label in XOR:
        either, both, answer = run(point)
        right += answer == label
        rows.append((point, either, both, answer, label))

    print("  in      either  both     out   wanted")
    for point, either, both, answer, label in rows:
        mark = "" if answer == label else "   <- wrong"
        print(f"  {point[0]}, {point[1]}      {either}      {both}"
              f"        {answer}       {label}{mark}")

    print()
    print(f"{right} of {len(XOR)} right")
    print()
    print("Where the four points sit after the first layer:")

    moved = {}
    for point, label in XOR:
        either, both, _ = run(point)
        moved.setdefault((either, both), []).append((point, label))

    for position in sorted(moved):
        entries = moved[position]
        described = ", ".join(f"{p[0]}{p[1]}" for p, _ in entries)
        labels = {label for _, label in entries}
        print(f"  {position} <- {described}   wanted: "
              f"{', '.join(str(label) for label in sorted(labels))}")


if __name__ == "__main__":
    main()
