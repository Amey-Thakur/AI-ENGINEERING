"""
Phase 4, lesson 5: what it knows.

Trains the same model as the last lesson, then stops looking at its predictions
and looks at the vectors it invented along the way.

Nobody asked it to learn what words mean. It was asked to guess the next word.
The vectors are scratch paper it kept in order to do that, and what turns up on
the scratch paper is the point of the lesson.

Run it with:  python solve.py
"""

from collections import Counter
from math import exp, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
NEIGHBOURS = HERE / ".work" / "neighbours.tsv"

TRAIN_UNTIL = 160
KEEP_WORDS = 100
DIMENSIONS = 8
RATE = 0.15

# The epoch the validation part chose in the last lesson.
EPOCHS = 4

START = "<s>"
END = "</s>"
UNKNOWN = "<unk>"

PROBES = ("server", "the", "was", "customer", "test")
SHOW = 4


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def start_numbers(rows, width):
    return [[0.05 * (((row * 7 + column * 13) % 17) - 8) / 8
             for column in range(width)]
            for row in range(rows)]


def train(pairs, position, size):
    """The same training as the last lesson, stopped where validation said."""
    meanings = start_numbers(size, DIMENSIONS)
    scorers = start_numbers(size, DIMENSIONS)
    offsets = [0.0] * size

    for _ in range(EPOCHS):
        for first, second in pairs:
            vector = meanings[position[first]]

            scores = [sum(row[i] * vector[i] for i in range(DIMENSIONS)) + offset
                      for row, offset in zip(scorers, offsets)]
            largest = max(scores)
            raised = [exp(score - largest) for score in scores]
            summed = sum(raised)
            chances = [value / summed for value in raised]

            chances[position[second]] -= 1.0
            carried = [0.0] * DIMENSIONS

            for index, chance in enumerate(chances):
                step = chance * RATE

                if step:
                    row = scorers[index]

                    for slot in range(DIMENSIONS):
                        carried[slot] += step * row[slot]
                        row[slot] -= step * vector[slot]

                    offsets[index] -= step

            for slot in range(DIMENSIONS):
                vector[slot] -= carried[slot]

    return meanings


def closeness(first, second):
    left = sqrt(sum(value * value for value in first))
    right = sqrt(sum(value * value for value in second))

    if not left or not right:
        return 0.0

    return sum(a * b for a, b in zip(first, second)) / (left * right)


def main() -> None:
    sentences = read_corpus()
    training = [[START] + sentence + [END]
                for sentence in sentences[:TRAIN_UNTIL]]

    counted = Counter(word for sentence in training for word in sentence)
    known = {word for word, _ in counted.most_common(KEEP_WORDS)}

    def fold(word):
        return word if word in known else UNKNOWN

    pairs = [(fold(first), fold(second))
             for sentence in training
             for first, second in zip(sentence, sentence[1:])]

    vocabulary = sorted(known | {UNKNOWN})
    position = {word: index for index, word in enumerate(vocabulary)}

    meanings = train(pairs, position, len(vocabulary))
    vectors = {word: meanings[position[word]] for word in vocabulary}

    NEIGHBOURS.parent.mkdir(parents=True, exist_ok=True)

    found = {}
    for probe in PROBES:
        ranked = sorted(
            ((closeness(vectors[probe], vectors[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )
        found[probe] = ranked[:SHOW]

    with open(NEIGHBOURS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tneighbour\tcloseness\n")

        for probe in PROBES:
            for score, other in found[probe]:
                handle.write(f"{probe}\t{other}\t{score:.6f}\n")

    print(f"{len(vocabulary)} words, {DIMENSIONS} numbers each, learned only "
          f"by guessing the next word")
    print()

    for probe in PROBES:
        listed = ", ".join(f"{other} {score:+.2f}"
                           for score, other in found[probe])
        print(f"  {probe:10} {listed}")

    # The closest pairs anywhere, which nobody chose in advance.
    best = []
    for index, word in enumerate(vocabulary):
        for other in vocabulary[index + 1:]:
            best.append((closeness(vectors[word], vectors[other]), word, other))

    best.sort(key=lambda entry: (-entry[0], entry[1], entry[2]))

    print()
    print("The closest pairs in the whole vocabulary:")
    print()

    for score, word, other in best[:6]:
        print(f"  {word:12} and {other:12} {score:+.3f}")


if __name__ == "__main__":
    main()
