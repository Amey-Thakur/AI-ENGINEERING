"""
Phase 3, lesson 2: the check.

It counts the corpus itself and works out the neighbours, then compares with
what you reported. The window and the minimum count are fixed by the lesson, so
there is one right answer.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
NEIGHBOURS = HERE / ".work" / "neighbours.tsv"

WINDOW = 4
MINIMUM = 4
PROBES = ("server", "deploy", "customer", "test", "meeting")
TOLERANCE = 1e-3


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def contexts():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

    counts = defaultdict(Counter)

    for sentence in sentences:
        for position, word in enumerate(sentence):
            start = max(0, position - WINDOW)
            stop = min(len(sentence), position + WINDOW + 1)

            for other in range(start, stop):
                if other != position:
                    counts[word][sentence[other]] += 1

    frequency = Counter(word for sentence in sentences for word in sentence)
    return counts, frequency


def closeness(first, second):
    shared = set(first) & set(second)

    if not shared:
        return 0.0

    together = sum(first[word] * second[word] for word in shared)
    size = sqrt(sum(value * value for value in first.values()))
    other = sqrt(sum(value * value for value in second.values()))

    return together / (size * other)


def main() -> None:
    if not NEIGHBOURS.exists():
        fail(
            "there is no .work/neighbours.tsv",
            "for each probe word, report its nearest neighbours and how close "
            "they are",
        )

    lines = NEIGHBOURS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["word"]:
        lines = lines[1:]

    yours = defaultdict(list)
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 3:
            fail(
                f"line {number} has {len(parts)} columns, not 3",
                "each row is the word, a neighbour, and how close they are",
            )

        try:
            yours[parts[0].strip()].append((parts[1].strip(), float(parts[2])))
        except ValueError:
            fail(
                f"line {number} has a closeness that is not a number: "
                f"{parts[2]!r}",
                "closeness is a number between 0 and 1",
            )

    counts, frequency = contexts()
    vocabulary = sorted(word for word in counts if frequency[word] >= MINIMUM)

    for probe in PROBES:
        if probe not in yours:
            fail(
                f"there are no neighbours reported for {probe!r}",
                f"report all {len(PROBES)} probe words",
            )

        ranked = sorted(
            ((closeness(counts[probe], counts[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )

        best_score, best_word = ranked[0]
        reported_word, reported_score = yours[probe][0]

        if reported_word != best_word:
            fail(
                f"for {probe!r} you report {reported_word!r} as the nearest "
                f"word, and counting gives {best_word!r}",
                f"use a window of {WINDOW} words either side, within a "
                f"sentence, and cosine over the raw counts",
            )

        if abs(reported_score - best_score) > TOLERANCE:
            fail(
                f"for {probe!r} you report a closeness of {reported_score:.4f}, "
                f"and counting gives {best_score:.4f}",
                "cosine divides the shared total by the length of both vectors",
            )

    print(f"PASS  the nearest neighbour of all {len(PROBES)} probe words "
          f"matches an independent count")


if __name__ == "__main__":
    main()
