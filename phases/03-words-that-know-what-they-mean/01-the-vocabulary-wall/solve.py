"""
Phase 3, lesson 1: the vocabulary wall.

Measures the two things standing between the models of phases 1 and 2 and a
better answer.

The first is the one already named: words in the held back messages that
training never saw. The second is quieter and worse, and this lesson is mostly
about it: the representation has no notion that any two words are related, so
even the words it does know arrive with no meaning attached.

Run it with:  python solve.py
"""

import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
FINDINGS = HERE / ".work" / "findings.tsv"

TRAIN_SIZE = 40

# Pairs chosen to make the point: the first two belong to the same world, the
# last two have nothing to do with each other.
PAIRS = [
    ("server", "deployment"),
    ("password", "vault"),
    ("server", "friday"),
    ("password", "tuesday"),
]


def read_messages():
    rows = []

    with open(MESSAGES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.strip()
            if line:
                label, message = line.split("\t")
                rows.append((label, message.split()))

    return rows


def one_hot(word, vocabulary):
    """A word as the representation of phases 1 and 2: all zeros, one 1."""
    return [1.0 if other == word else 0.0 for other in vocabulary]


def distance(first, second):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(first, second)))


def main() -> None:
    rows = read_messages()

    known = {word for _, words in rows[:TRAIN_SIZE] for word in words}
    held_back = rows[TRAIN_SIZE:]

    unseen = [word for _, words in held_back for word in words
              if word not in known]

    everything = sorted({word for _, words in rows for word in words})

    FINDINGS.parent.mkdir(parents=True, exist_ok=True)

    measured = []
    for first, second in PAIRS:
        gap = distance(one_hot(first, everything), one_hot(second, everything))
        measured.append((first, second, gap))

    with open(FINDINGS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("finding\tvalue\n")
        handle.write(f"vocabulary_trained\t{len(known)}\n")
        handle.write(f"unseen_words_in_held_back\t{len(unseen)}\n")

        for first, second, gap in measured:
            handle.write(f"distance_{first}_{second}\t{gap:.6f}\n")

    print(f"Training saw {len(known)} different words.")
    print(f"The held back messages use {len(unseen)} words it never saw.")
    print()
    print("How far apart are these words, in the representation we have been")
    print("using all along?")
    print()

    for first, second, gap in measured:
        print(f"  {first:10} and {second:12} {gap:.6f}")

    print()

    gaps = {round(gap, 9) for _, _, gap in measured}
    print(f"Distinct distances among those four pairs: {len(gaps)}")

    # The same claim, made about the whole vocabulary rather than four pairs.
    sample = everything[:60]
    everywhere = set()

    for index, first in enumerate(sample):
        for second in sample[index + 1:]:
            everywhere.add(round(distance(one_hot(first, everything),
                                          one_hot(second, everything)), 9))

    pairs = len(sample) * (len(sample) - 1) // 2
    print(f"Distinct distances among {pairs:,} pairs of the first "
          f"{len(sample)} words: {len(everywhere)}")
    print(f"That one distance is {sorted(everywhere)[0]:.6f}, which is the "
          f"square root of 2.")


if __name__ == "__main__":
    main()
