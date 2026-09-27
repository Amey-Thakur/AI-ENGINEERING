"""
Phase 4, lesson 4: the check.

It trains the same model itself, picks the same stopping point from the
validation part, and compares the test perplexity with what you reported.
Everything here is deterministic, so there is one right answer.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from math import exp, inf, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
RESULTS = HERE / ".work" / "results.tsv"

TRAIN_UNTIL = 160
VALIDATE_UNTIL = 190
KEEP_WORDS = 100
DIMENSIONS = 8
RATE = 0.15
EPOCHS = 12

START = "<s>"
END = "</s>"
UNKNOWN = "<unk>"

RELATIVE = 0.02


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def measure():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

    def marked(part):
        return [[START] + sentence + [END] for sentence in part]

    training = marked(sentences[:TRAIN_UNTIL])
    validation = marked(sentences[TRAIN_UNTIL:VALIDATE_UNTIL])
    testing = marked(sentences[VALIDATE_UNTIL:])

    counted = Counter(word for sentence in training for word in sentence)
    known = {word for word, _ in counted.most_common(KEEP_WORDS)}

    def pairs(part):
        def fold(word):
            return word if word in known else UNKNOWN

        return [(fold(first), fold(second))
                for sentence in part
                for first, second in zip(sentence, sentence[1:])]

    train_pairs, validation_pairs, test_pairs = (
        pairs(training), pairs(validation), pairs(testing))

    vocabulary = sorted(known | {UNKNOWN})
    position = {word: index for index, word in enumerate(vocabulary)}
    size = len(vocabulary)

    following = defaultdict(Counter)
    context = Counter()
    single = Counter()
    total = 0

    for first, second in train_pairs:
        following[first][second] += 1
        context[first] += 1
        single[second] += 1
        total += 1

    def counting(first, second):
        bigram = following[first][second] / context[first] if context[first] else 0.0
        return 0.5 * bigram + 0.5 * (single[second] + 1) / (total + size)

    def start(rows, width):
        return [[0.05 * (((row * 7 + column * 13) % 17) - 8) / 8
                 for column in range(width)]
                for row in range(rows)]

    meanings = start(size, DIMENSIONS)
    scorers = start(size, DIMENSIONS)
    offsets = [0.0] * size

    def spread(first):
        vector = meanings[position[first]]
        scores = [sum(row[i] * vector[i] for i in range(DIMENSIONS)) + offset
                  for row, offset in zip(scorers, offsets)]
        largest = max(scores)
        raised = [exp(score - largest) for score in scores]
        summed = sum(raised)
        return vector, [value / summed for value in raised]

    def perplexity(data, probability):
        carried = 0.0

        for first, second in data:
            chance = probability(first, second)

            if chance <= 0:
                return inf

            carried += log(chance)

        return exp(-carried / len(data))

    def neural(first, second):
        return spread(first)[1][position[second]]

    best = (inf, 0, None)

    for epoch in range(1, EPOCHS + 1):
        for first, second in train_pairs:
            vector, chances = spread(first)
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

        score = perplexity(validation_pairs, neural)

        if score < best[0]:
            best = (score, epoch,
                    ([row[:] for row in meanings],
                     [row[:] for row in scorers], offsets[:]))

    meanings, scorers, offsets = best[2]

    return {
        "vocabulary": float(size),
        "best_epoch": float(best[1]),
        "counting_test": perplexity(test_pairs, counting),
        "neural_test": perplexity(test_pairs, neural),
    }


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report the vocabulary size, the epoch you stopped at, and the "
            "test perplexity of both models",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["measure"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is a name and a number",
            )

        try:
            yours[parts[0].strip()] = float(parts[1])
        except ValueError:
            fail(
                f"line {number} has a value that is not a number: {parts[1]!r}",
                "every value here is a number",
            )

    expected = measure()

    for name in ("vocabulary", "best_epoch"):
        if name not in yours:
            fail(f"there is no row for {name}", "report all four measures")

        if yours[name] != expected[name]:
            fail(
                f"{name} is reported as {yours[name]:g}, and it should be "
                f"{expected[name]:g}",
                "keep the 100 commonest training words plus an unknown token, "
                "and choose the epoch with the lowest validation perplexity",
            )

    for name in ("counting_test", "neural_test"):
        if name not in yours:
            fail(f"there is no row for {name}", "report all four measures")

        want = expected[name]

        if abs(yours[name] - want) > want * RELATIVE:
            fail(
                f"{name} is reported as {yours[name]:.2f}, and training gives "
                f"{want:.2f}",
                "measure on the test part only, using the weights from the "
                "epoch the validation part chose",
            )

    if expected["neural_test"] >= expected["counting_test"]:
        fail(
            "the neural model did not beat counting on the test part",
            "check the stopping epoch is taken from validation rather than "
            "from the last epoch",
        )

    gain = 1 - expected["neural_test"] / expected["counting_test"]
    print(f"PASS  stopped at epoch {expected['best_epoch']:.0f}, test "
          f"perplexity {expected['neural_test']:.2f} against counting's "
          f"{expected['counting_test']:.2f}, {gain:.0%} better")


if __name__ == "__main__":
    main()
