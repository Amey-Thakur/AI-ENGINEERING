"""
Phase 7, lesson 1: the check.

It computes every interval itself and compares yours, allowing a fifth of a
percentage point either way so that a different number of halvings does not
fail you. It also checks the two ends behave: a score of 0 has to start at 0
and a perfect score has to reach 100.

Run it with:  python check.py
"""

import sys
from math import exp, lgamma, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASUREMENTS = HERE / "measurements.tsv"
INTERVALS = HERE / ".work" / "intervals.tsv"

ALPHA = 0.05
HALVINGS = 60
TOLERANCE = 0.2


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def log_choose(n, k):
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def chance_of_at_least(k, n, rate):
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(k, n + 1))


def chance_of_at_most(k, n, rate):
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(0, k + 1))


def pin_down(rising, target):
    low, high = 0.0, 1.0

    for _ in range(HALVINGS):
        middle = (low + high) / 2

        if rising(middle) < target:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def interval(k, n):
    low = 0.0 if k == 0 else pin_down(
        lambda rate: chance_of_at_least(k, n, rate), ALPHA / 2)
    high = 1.0 if k == n else pin_down(
        lambda rate: -chance_of_at_most(k, n, rate), -ALPHA / 2)

    return low * 100, high * 100


def main() -> None:
    wanted = {}

    for line in MEASUREMENTS.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            what, right, asked = line.rstrip("\n").split("\t")
            wanted[what] = interval(int(right), int(asked))

    if not INTERVALS.exists():
        fail(
            "there is no .work/intervals.tsv",
            "for every measurement, report the lowest and highest true rate "
            "that could have produced it",
        )

    lines = INTERVALS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["what"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 5:
            fail(
                f"line {number} has {len(parts)} columns, and needs 5",
                "the measurement, how many right, how many asked, then the "
                "low and high ends as percentages",
            )

        try:
            yours[parts[0]] = (float(parts[3]), float(parts[4]))
        except ValueError:
            fail(
                f"line {number} has an end that is not a number",
                "write the two ends as percentages, so 51.9 rather than 0.519",
            )

    for what, (low, high) in wanted.items():
        if what not in yours:
            fail(
                f"there is no row for {what!r}",
                f"report all {len(wanted)} measurements",
            )

        mine_low, mine_high = yours[what]

        if abs(mine_low - low) > TOLERANCE or abs(mine_high - high) > TOLERANCE:
            fail(
                f"for {what!r} you report {mine_low:.1f} to {mine_high:.1f} "
                f"and it should be {low:.1f} to {high:.1f}",
                "the low end is the rate that would score this high or "
                "higher only 2.5% of the time, and the high end is the rate "
                "that would score this low or lower only 2.5% of the time",
            )

        if not 0.0 <= mine_low <= mine_high <= 100.0:
            fail(
                f"for {what!r} the interval {mine_low:.1f} to {mine_high:.1f} "
                f"is not a rate that runs upwards",
                "both ends are percentages between 0 and 100, and the low "
                "end comes first",
            )

    zeros = [what for what, (low, _) in yours.items() if low == 0.0]

    if not zeros:
        fail(
            "no measurement has a low end of exactly 0",
            "a score of 0 out of 20 is compatible with a system that is "
            "never right, so its interval has to start at 0",
        )

    widest = max(wanted, key=lambda what: wanted[what][1] - wanted[what][0])
    narrowest = min(wanted, key=lambda what: wanted[what][1] - wanted[what][0])

    print(f"PASS  {len(wanted)} intervals, the widest {widest!r} spanning "
          f"{wanted[widest][1] - wanted[widest][0]:.0f} points and the "
          f"narrowest {narrowest!r} spanning "
          f"{wanted[narrowest][1] - wanted[narrowest][0]:.0f}")


if __name__ == "__main__":
    main()
