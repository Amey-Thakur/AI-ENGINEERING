"""
Phase 3, lesson 2: the company a word keeps.

Counts which words appear near which other words, then uses those counts to
look for the nearest neighbours of a few probe words.

It does not work. That is the lesson: raw counting produces a representation
dominated by the words that are simply common, and seeing exactly how it fails
is what makes the fix in the next lesson obvious rather than magic.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
NEIGHBOURS = HERE / ".work" / "neighbours.tsv"

# How many words either side count as "near".
WINDOW = 4

# A word seen three times has a context of three words, which is noise.
MINIMUM = 4

PROBES = ("server", "deploy", "customer", "test", "meeting")
SHOW = 5


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def contexts(sentences):
    """For each word, a count of every word appearing near it."""
    counts = defaultdict(Counter)

    for sentence in sentences:
        for position, word in enumerate(sentence):
            start = max(0, position - WINDOW)
            stop = min(len(sentence), position + WINDOW + 1)

            for other in range(start, stop):
                if other != position:
                    counts[word][sentence[other]] += 1

    return counts


def closeness(first, second):
    """Cosine: how much two context profiles point the same way."""
    shared = set(first) & set(second)

    if not shared:
        return 0.0

    together = sum(first[word] * second[word] for word in shared)
    size = sqrt(sum(value * value for value in first.values()))
    other = sqrt(sum(value * value for value in second.values()))

    return together / (size * other)


def main() -> None:
    sentences = read_corpus()
    counts = contexts(sentences)

    frequency = Counter(word for sentence in sentences for word in sentence)
    vocabulary = sorted(word for word in counts if frequency[word] >= MINIMUM)

    NEIGHBOURS.parent.mkdir(parents=True, exist_ok=True)

    found = {}
    for probe in PROBES:
        ranked = sorted(
            ((closeness(counts[probe], counts[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )
        found[probe] = ranked[:SHOW]

    with open(NEIGHBOURS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tneighbour\tcloseness\n")

        for probe in PROBES:
            for score, other in found[probe]:
                handle.write(f"{probe}\t{other}\t{score:.6f}\n")

    words = sum(len(sentence) for sentence in sentences)

    print(f"{len(sentences)} sentences, {words} words, "
          f"{len(frequency)} distinct")
    print(f"{len(vocabulary)} words appear at least {MINIMUM} times")
    print()
    print("What sits near 'server', most often first:")

    for word, count in counts["server"].most_common(8):
        print(f"  {word:12} {count}")

    print()
    print("Nearest neighbours, by raw counts:")
    print()

    for probe in PROBES:
        listed = ", ".join(f"{other} {score:.2f}" for score, other in found[probe])
        print(f"  {probe:10} {listed}")

    common = Counter()
    for probe in PROBES:
        for _, other in found[probe]:
            common[other] += 1

    everywhere = [word for word, count in common.items() if count >= 3]

    print()
    print(f"Words appearing in at least three of those five lists: "
          f"{', '.join(sorted(everywhere)) if everywhere else 'none'}")


if __name__ == "__main__":
    main()
