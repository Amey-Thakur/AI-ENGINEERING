"""
Phase 3, lesson 4: fewer numbers that say more.

Squeezes each word's profile from six hundred numbers down to twenty four, by
finding the directions the data actually varies along and describing every word
by where it sits on those.

The method is power iteration, which is how this is really done on matrices too
large to handle any other way. Multiply, project away what has already been
found, normalise, repeat.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import log, sin, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
VECTORS = HERE / ".work" / "vectors.tsv"

WINDOW = 4
MINIMUM = 4

DIMENSIONS = 24
ITERATIONS = 40

PROBES = ("server", "deploy", "customer", "test", "meeting", "incident")
SHOW = 5


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def weighted_profiles(sentences):
    """Lesson 3's surprise weighted profiles, rebuilt here."""
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

    profiles = defaultdict(dict)

    for (word, near), count in together.items():
        expected = (word_total[word] * context_total[near]) / grand
        value = log(count / expected)

        if value > 0:
            profiles[word][near] = value

    return profiles


def normalise(vector):
    size = sqrt(sum(value * value for value in vector))
    return [value / size for value in vector] if size else vector


def directions(rows, width):
    """The directions the profiles vary along most, strongest first.

    Multiplying a vector by the matrix and then by its transpose stretches it
    most along the direction of greatest variation, so repeating that and
    normalising walks any starting vector towards it. Each new direction is
    kept clear of the ones already found, so they do not all collapse onto the
    same answer.
    """
    found = []

    for index in range(DIMENSIONS):
        # A fixed, uneven starting vector: different for each direction, and
        # identical on every machine.
        current = normalise([sin(index * 7.0 + slot * 0.7) + 0.1
                             for slot in range(width)])

        for _ in range(ITERATIONS):
            carried = [0.0] * width

            for row in rows.values():
                along = sum(value * current[slot] for slot, value in row.items())

                if along:
                    for slot, value in row.items():
                        carried[slot] += value * along

            for earlier in found:
                overlap = sum(a * b for a, b in zip(carried, earlier))
                carried = [a - overlap * b for a, b in zip(carried, earlier)]

            current = normalise(carried)

        found.append(current)

    return found


def closeness(first, second):
    left = sqrt(sum(value * value for value in first))
    right = sqrt(sum(value * value for value in second))

    if not left or not right:
        return 0.0

    return sum(a * b for a, b in zip(first, second)) / (left * right)


def main() -> None:
    sentences = read_corpus()
    profiles = weighted_profiles(sentences)

    words = sorted(profiles)
    contexts = sorted({near for profile in profiles.values() for near in profile})
    slot = {near: index for index, near in enumerate(contexts)}

    rows = {word: {slot[near]: value for near, value in profiles[word].items()}
            for word in words}

    axes = directions(rows, len(contexts))

    vectors = {
        word: [sum(value * axis[position] for position, value in rows[word].items())
               for axis in axes]
        for word in words
    }

    frequency = Counter(word for sentence in sentences for word in sentence)
    vocabulary = sorted(word for word in words if frequency[word] >= MINIMUM)

    VECTORS.parent.mkdir(parents=True, exist_ok=True)

    with open(VECTORS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\t" + "\t".join(f"d{index}"
                                          for index in range(DIMENSIONS)) + "\n")

        for word in vocabulary:
            numbers = "\t".join(f"{value:.6f}" for value in vectors[word])
            handle.write(f"{word}\t{numbers}\n")

    before = sum(len(profiles[word]) for word in vocabulary)
    after = len(vocabulary) * DIMENSIONS

    print(f"{len(words)} words, {len(contexts)} contexts")
    print(f"Every word was {len(contexts)} numbers, mostly zero. "
          f"Now it is {DIMENSIONS}.")
    print(f"Stored values for the {len(vocabulary)} common words: "
          f"{before} before, {after} after")
    print()
    print("Nearest neighbours, on the squeezed vectors:")
    print()

    for probe in PROBES:
        ranked = sorted(
            ((closeness(vectors[probe], vectors[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )[:SHOW]

        listed = ", ".join(f"{other} {score:.2f}" for score, other in ranked)
        print(f"  {probe:10} {listed}")


if __name__ == "__main__":
    main()
