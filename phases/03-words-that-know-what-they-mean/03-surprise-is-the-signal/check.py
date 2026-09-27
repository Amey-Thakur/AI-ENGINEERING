"""
Phase 3, lesson 3: the check.

It recomputes the surprise weighting and the neighbours itself, and compares
the nearest word for each probe with what you reported.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from math import log, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
NEIGHBOURS = HERE / ".work" / "neighbours.tsv"

WINDOW = 4
MINIMUM = 4
PROBES = ("server", "deploy", "customer", "test", "meeting", "incident")
TOLERANCE = 1e-3

# Words that mean nothing on their own. If these dominate the neighbours, the
# weighting has not been applied.
FILLER = {"the", "and", "was", "a", "an", "is", "to", "of", "in", "on", "it"}


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def profiles():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

    together = Counter()
    word_total = Counter()
    context_total = Counter()
    grand = 0

    for sentence in sentences:
        for position, word in enumerate(sentence):
            start = max(0, position - WINDOW)
            stop = min(len(sentence), position + WINDOW + 1)

            for other in range(start, stop):
                if other == position:
                    continue

                near = sentence[other]
                together[(word, near)] += 1
                word_total[word] += 1
                context_total[near] += 1
                grand += 1

    built = defaultdict(dict)

    for (word, near), count in together.items():
        expected = (word_total[word] * context_total[near]) / grand
        value = log(count / expected)

        if value > 0:
            built[word][near] = value

    frequency = Counter(word for sentence in sentences for word in sentence)
    return built, frequency


def closeness(first, second):
    shared = set(first) & set(second)

    if not shared:
        return 0.0

    top = sum(first[word] * second[word] for word in shared)
    size = sqrt(sum(value * value for value in first.values()))
    other = sqrt(sum(value * value for value in second.values()))

    return top / (size * other)


def main() -> None:
    if not NEIGHBOURS.exists():
        fail(
            "there is no .work/neighbours.tsv",
            "report the nearest neighbours of each probe word, using the "
            "surprise weighting rather than the raw counts",
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
                f"line {number} has a closeness that is not a number",
                "closeness is a number",
            )

    built, frequency = profiles()
    vocabulary = sorted(word for word in built if frequency[word] >= MINIMUM)

    for probe in PROBES:
        if probe not in yours:
            fail(
                f"there are no neighbours reported for {probe!r}",
                f"report all {len(PROBES)} probe words",
            )

        ranked = sorted(
            ((closeness(built[probe], built[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )

        best_score, best_word = ranked[0]
        reported_word, reported_score = yours[probe][0]

        if reported_word != best_word:
            hint = ("that is a filler word, which is what the raw counts gave "
                    "in the last lesson: check the weighting is applied") \
                if reported_word in FILLER else \
                ("divide each count by what chance predicts, take the "
                 "logarithm, and keep only what is above zero")

            fail(
                f"for {probe!r} you report {reported_word!r} as nearest, and "
                f"recomputing gives {best_word!r}",
                hint,
            )

        if abs(reported_score - best_score) > TOLERANCE:
            fail(
                f"for {probe!r} you report {reported_score:.4f}, and "
                f"recomputing gives {best_score:.4f}",
                "use the same window and minimum count as the lesson",
            )

    print(f"PASS  the nearest neighbour of all {len(PROBES)} probes matches "
          f"an independent computation")


if __name__ == "__main__":
    main()
