"""
Phase 2, lesson 1: the check.

It runs its own search, on a coarser grid, and works out for itself what the
best any line can do on each problem. Then it compares that with what you
reported. It is not holding a stored answer.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / ".work" / "results.tsv"

AND_GATE = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
XOR_GATE = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]

# Coarser than the lesson's grid, because a coarse grid is enough to find the
# answer and this has to run quickly.
LOW, HIGH, SCALE = -8, 8, 2


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def best_possible(problem):
    best = 0

    for first in range(LOW, HIGH + 1):
        for second in range(LOW, HIGH + 1):
            for bias in range(LOW, HIGH + 1):
                right = 0

                for point, label in problem:
                    total = (point[0] * first + point[1] * second + bias) / SCALE
                    right += (1 if total > 0 else 0) == label

                best = max(best, right)

                if best == len(problem):
                    return best

    return best


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report, for each problem, the best score any single line reached",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["problem"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 3:
            fail(
                f"line {number} has {len(parts)} columns, not 3",
                "each row is the problem name, the best score, and the total",
            )

        try:
            yours[parts[0].strip().lower()] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(
                f"line {number} has something that is not a whole number",
                "the second and third columns count points",
            )

    for name, problem in (("and", AND_GATE), ("xor", XOR_GATE)):
        if name not in yours:
            fail(
                f"there is no row for {name}",
                "report both problems",
            )

        best, total = yours[name]

        if total != len(problem):
            fail(
                f"you say {name} has {total} points, and it has {len(problem)}",
                "each of these problems is four points",
            )

        truth = best_possible(problem)

        if best != truth:
            fail(
                f"you report the best line on {name} getting {best} of {total}, "
                f"and searching finds {truth}",
                "score every combination on the grid and keep the highest, "
                "rather than training one model and reporting how it did",
            )

    print(f"PASS  AND {yours['and'][0]} of 4, XOR {yours['xor'][0]} of 4, "
          f"both confirmed by an independent search")


if __name__ == "__main__":
    main()
