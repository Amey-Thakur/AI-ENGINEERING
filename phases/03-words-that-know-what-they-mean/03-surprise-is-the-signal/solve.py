"""
Phase 3, lesson 3: surprise is the signal.

Replaces each raw co-occurrence count with how surprising that co-occurrence
is, and finds the neighbours again.

Nothing else changes. Same corpus, same window, same cosine. Only the number in
each cell is different, and that is enough to turn a broken representation into
one that works.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import log, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
NEIGHBOURS = HERE / ".work" / "neighbours.tsv"

WINDOW = 4
MINIMUM = 4

PROBES = ("server", "deploy", "customer", "test", "meeting", "incident")
SHOW = 5


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def pairs(sentences):
    """Every (word, nearby word) seen, with how often, and the totals."""
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

    return together, word_total, context_total, grand


def surprise(together, word_total, context_total, grand):
    """How much more often two words appear together than chance predicts.

    Chance says the pair should turn up as often as one word's share times the
    other's. Divide what happened by that, take the logarithm so that twice as
    surprising is one step rather than double, and throw away anything below
    zero: "these appear together less than chance" is mostly noise at this
    corpus size, and keeping it fills every profile with words that were simply
    absent.
    """
    profiles = defaultdict(dict)

    for (word, near), count in together.items():
        expected = (word_total[word] * context_total[near]) / grand
        value = log(count / expected)

        if value > 0:
            profiles[word][near] = value

    return profiles


def closeness(first, second):
    shared = set(first) & set(second)

    if not shared:
        return 0.0

    top = sum(first[word] * second[word] for word in shared)
    size = sqrt(sum(value * value for value in first.values()))
    other = sqrt(sum(value * value for value in second.values()))

    return top / (size * other)


def main() -> None:
    sentences = read_corpus()
    together, word_total, context_total, grand = pairs(sentences)
    profiles = surprise(together, word_total, context_total, grand)

    frequency = Counter(word for sentence in sentences for word in sentence)
    vocabulary = sorted(word for word in profiles if frequency[word] >= MINIMUM)

    NEIGHBOURS.parent.mkdir(parents=True, exist_ok=True)

    found = {}
    for probe in PROBES:
        ranked = sorted(
            ((closeness(profiles[probe], profiles[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )
        found[probe] = ranked[:SHOW]

    with open(NEIGHBOURS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tneighbour\tcloseness\n")

        for probe in PROBES:
            for score, other in found[probe]:
                handle.write(f"{probe}\t{other}\t{score:.6f}\n")

    print("What sits near 'server', now ranked by surprise rather than count:")

    ranked_context = sorted(profiles["server"].items(),
                            key=lambda pair: (-pair[1], pair[0]))

    for word, value in ranked_context[:8]:
        print(f"  {word:12} {value:.2f}   (seen together "
              f"{together[('server', word)]} time"
              f"{'s' if together[('server', word)] != 1 else ''})")

    print()
    print("Nearest neighbours:")
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
    print(f"Words appearing in at least three of those {len(PROBES)} lists: "
          f"{', '.join(sorted(everywhere)) if everywhere else 'none'}")


if __name__ == "__main__":
    main()
