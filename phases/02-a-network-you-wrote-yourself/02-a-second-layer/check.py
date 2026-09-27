"""
Phase 2, lesson 2: the check.

It builds a network from your weights and runs all four XOR points through it.
Your weights do not have to match anyone else's: many networks solve this, and
any of them passes.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NETWORK = HERE / ".work" / "network.tsv"

XOR = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

NEEDED = ("hidden_either", "hidden_both", "output")


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def unit(first, second, weights):
    w1, w2, bias = weights
    return 1 if first * w1 + second * w2 + bias > 0 else 0


def main() -> None:
    if not NETWORK.exists():
        fail(
            "there is no .work/network.tsv",
            "write one row per unit: its name, its two weights, and its bias",
        )

    lines = NETWORK.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["unit"]:
        lines = lines[1:]

    units = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 4:
            fail(
                f"line {number} has {len(parts)} columns, not 4",
                "each row is the unit name, two weights, and a bias",
            )

        try:
            units[parts[0].strip()] = tuple(float(part) for part in parts[1:])
        except ValueError:
            fail(
                f"line {number} has a weight that is not a number",
                "weights and biases are numbers, and may be negative",
            )

    for name in NEEDED:
        if name not in units:
            fail(
                f"there is no unit called {name}",
                f"the network needs three units: {', '.join(NEEDED)}",
            )

    wrong = []
    for point, label in XOR:
        first = unit(point[0], point[1], units["hidden_either"])
        second = unit(point[0], point[1], units["hidden_both"])
        answer = unit(first, second, units["output"])

        if answer != label:
            wrong.append((point, answer, label))

    if wrong:
        point, answer, label = wrong[0]
        fail(
            f"the network gets {len(wrong)} of {len(XOR)} points wrong, "
            f"starting with {point}, where it says {answer} and should say {label}",
            "the hidden units have to ask different questions: if both compute "
            "the same thing, the output layer has nothing to work with",
        )

    # A network whose hidden units are identical has not really got two of
    # them, and would fail on a harder problem for a reason worth knowing now.
    if units["hidden_either"] == units["hidden_both"]:
        fail(
            "both hidden units have identical weights",
            "they need to detect different things, or the second adds nothing",
        )

    print(f"PASS  all {len(XOR)} XOR points correct, which no single line could do")


if __name__ == "__main__":
    main()
