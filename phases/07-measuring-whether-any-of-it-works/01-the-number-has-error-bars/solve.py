"""
Phase 7, lesson 1: the number has error bars.

Every score in this course has been a fraction: 15 of 20, 12 of 15, 35 of 38.
This works out what each of those fractions actually establishes about the
system that produced it, by asking which true rates could have produced the
result without anything surprising happening.

There is no sampling and no randomness here. The answer is computed exactly
from the binomial distribution, so it is the same number on every machine.

Run it with:  python solve.py
"""

from math import exp, lgamma, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASUREMENTS = HERE / "measurements.tsv"
INTERVALS = HERE / ".work" / "intervals.tsv"

ALPHA = 0.05
HALVINGS = 40

LADDER = (15, 38, 100, 250, 1000)
TRUE_RATE = 0.8
CANDIDATES = (0.50, 0.60, 0.70, 0.80, 0.90)


def log_choose(n, k):
    """The log of n choose k, which stays finite where the number does not."""
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def chance_of_at_least(k, n, rate):
    """The chance a system this good scores k or more out of n."""
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(k, n + 1))


def chance_of_at_most(k, n, rate):
    """The chance a system this good scores k or fewer out of n."""
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(0, k + 1))


def lowest_rate_that_fits(rising, target):
    """Halve the range until the rate that hits the target is pinned down."""
    low, high = 0.0, 1.0

    for _ in range(HALVINGS):
        middle = (low + high) / 2

        if rising(middle) < target:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def interval(k, n):
    """The rates that could have produced k of n, to 95% confidence."""
    if k == 0:
        low = 0.0
    else:
        low = lowest_rate_that_fits(
            lambda rate: chance_of_at_least(k, n, rate), ALPHA / 2)

    if k == n:
        high = 1.0
    else:
        high = lowest_rate_that_fits(
            lambda rate: -chance_of_at_most(k, n, rate), -ALPHA / 2)

    return low, high


def read_measurements():
    rows = []

    with open(MEASUREMENTS, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")

            if line:
                what, right, asked = line.split("\t")
                rows.append((what, int(right), int(asked)))

    return rows


def main() -> None:
    rows = read_measurements()
    computed = []

    for what, right, asked in rows:
        low, high = interval(right, asked)
        computed.append((what, right, asked, low, high))

    INTERVALS.parent.mkdir(parents=True, exist_ok=True)

    with open(INTERVALS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("what\tright\tasked\tlow\thigh\n")

        for what, right, asked, low, high in computed:
            handle.write(f"{what}\t{right}\t{asked}\t{low * 100:.1f}\t"
                         f"{high * 100:.1f}\n")

    print("Every score in this course, and what it establishes.")
    print()
    print("  measurement                                       score      "
          "could truly be        width")

    for what, right, asked, low, high in computed:
        print(f"  {what:48}  {right:2} of {asked:2}   "
              f"{low:5.1%} to {high:5.1%}   {high - low:5.1%}")

    print()

    widest = max(computed, key=lambda row: row[4] - row[3])
    narrowest = min(computed, key=lambda row: row[4] - row[3])

    print(f"  widest:    {widest[0]}")
    print(f"             {widest[1]} of {widest[2]} pins the true rate to "
          f"within {widest[4] - widest[3]:.0%}")
    print(f"  narrowest: {narrowest[0]}")
    print(f"             {narrowest[1]} of {narrowest[2]} pins it to within "
          f"{narrowest[4] - narrowest[3]:.0%}")
    print()

    print(f"A system that is truly {TRUE_RATE:.0%} right, measured on more "
          f"and more questions:")

    for size in LADDER:
        right = round(TRUE_RATE * size)
        low, high = interval(right, size)
        print(f"  {size:5} questions: {right:4} right, {low:5.1%} to "
              f"{high:5.1%}, so {TRUE_RATE:.0%} give or take "
              f"{(high - low) / 2:4.1%}")

    print()

    observed, size = 12, 15
    print(f"And what {observed} of {size} rules out, which is less than you "
          f"would hope:")

    for rate in CANDIDATES:
        chance = chance_of_at_least(observed, size, rate)
        print(f"  a system truly {rate:5.0%} right scores {observed} or more "
              f"of {size} {chance:6.1%} of the time")


if __name__ == "__main__":
    main()
