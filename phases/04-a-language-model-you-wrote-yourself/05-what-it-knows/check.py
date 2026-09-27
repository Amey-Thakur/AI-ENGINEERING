"""
Phase 4, lesson 5: the check.

It trains the same model itself and compares the nearest neighbour of each
probe word with what you reported. Training is deterministic, so there is one
right answer.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from math import exp, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
NEIGHBOURS = HERE / ".work" / "neighbours.tsv"

TRAIN_UNTIL = 160
KEEP_WORDS = 100
DIMENSIONS = 8
RATE = 0.15
EPOCHS = 4

START = "<s>"
END = "</s>"
UNKNOWN = "<unk>"

PROBES = ("server", "the", "was", "customer", "test")
TOLERANCE = 1e-3


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def learned():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

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
    size = len(vocabulary)

    def start(rows, width):
        return [[0.05 * (((row * 7 + column * 13) % 17) - 8) / 8
                 for column in range(width)]
                for row in range(rows)]

    meanings = start(size, DIMENSIONS)
    scorers = start(size, DIMENSIONS)
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

    return vocabulary, {word: meanings[position[word]] for word in vocabulary}


def closeness(first, second):
    left = sqrt(sum(value * value for value in first))
    right = sqrt(sum(value * value for value in second))

    if not left or not right:
        return 0.0

    return sum(a * b for a, b in zip(first, second)) / (left * right)


def main() -> None:
    if not NEIGHBOURS.exists():
        fail(
            "there is no .work/neighbours.tsv",
            "report the nearest neighbours of each probe word, in the vectors "
            "the language model learned",
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
                "closeness is a number between -1 and 1",
            )

    vocabulary, vectors = learned()

    for probe in PROBES:
        if probe not in yours:
            fail(
                f"there are no neighbours reported for {probe!r}",
                f"report all {len(PROBES)} probe words",
            )

        ranked = sorted(
            ((closeness(vectors[probe], vectors[other]), other)
             for other in vocabulary if other != probe),
            key=lambda pair: (-pair[0], pair[1]),
        )

        best_score, best_word = ranked[0]
        reported_word, reported_score = yours[probe][0]

        if reported_word != best_word:
            fail(
                f"for {probe!r} you report {reported_word!r} as nearest, and "
                f"training gives {best_word!r}",
                f"train for exactly {EPOCHS} epochs from the fixed starting "
                f"numbers, and compare the word vectors rather than the "
                f"scoring rows",
            )

        if abs(reported_score - best_score) > TOLERANCE:
            fail(
                f"for {probe!r} you report {reported_score:.4f} and training "
                f"gives {best_score:.4f}",
                "use cosine between the learned word vectors",
            )

    print(f"PASS  the nearest neighbour of all {len(PROBES)} probes matches a "
          f"model trained independently")


if __name__ == "__main__":
    main()
