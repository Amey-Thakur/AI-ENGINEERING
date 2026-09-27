"""
Phase 2, lesson 1: the thing one line cannot do.

Searches every linear model on a grid, on two problems, and reports the best
score either can reach.

This is a proof rather than a demonstration. It does not train a model and
report that training went badly, because that would only show that this
training run went badly. It tries every combination of weights on a fine grid
and shows that none of them gets all four, which is a statement about the model
and not about the search.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / ".work" / "results.tsv"

# Four points, two inputs each. The label is the third number.
AND_GATE = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
XOR_GATE = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

# The grid the search walks: weights and bias from -4 to 4 in steps of a tenth.
LOW, HIGH, STEP = -40, 40, 1
SCALE = 10


def decide(point, first, second, bias):
    """One weighted sum, one threshold. The whole of a linear model."""
    total = point[0] * first + point[1] * second + bias
    return 1 if total > 0 else 0


def best_possible(problem):
    """The most points any linear model on this grid can get right."""
    best = 0
    winner = None

    for first in range(LOW, HIGH + 1, STEP):
        for second in range(LOW, HIGH + 1, STEP):
            for bias in range(LOW, HIGH + 1, STEP):
                weights = (first / SCALE, second / SCALE, bias / SCALE)

                right = sum(
                    1 for point, label in problem
                    if decide(point, *weights) == label
                )

                if right > best:
                    best, winner = right, weights

                    if best == len(problem):
                        return best, winner

    return best, winner


def main() -> None:
    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    combinations = ((HIGH - LOW) // STEP + 1) ** 3
    findings = []

    for name, problem in (("and", AND_GATE), ("xor", XOR_GATE)):
        best, winner = best_possible(problem)
        findings.append((name, best, len(problem), winner))

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("problem\tbest\ttotal\n")
        for name, best, total, _ in findings:
            handle.write(f"{name}\t{best}\t{total}\n")

    print(f"Tried {combinations:,} weight combinations on each problem.")
    print()

    for name, best, total, winner in findings:
        print(f"{name.upper()}")
        print(f"  best any single line can do: {best} of {total}")

        if winner:
            first, second, bias = winner
            print(f"  reached with weights {first:g} and {second:g}, "
                  f"bias {bias:g}")

        print()

    print("AND is separable: one line divides its points and every combination")
    print("that does so is found immediately.")
    print()
    print("XOR is not. No line exists, so the best any of them manages is three")
    print("out of four, and the fourth is always wrong.")


if __name__ == "__main__":
    main()
