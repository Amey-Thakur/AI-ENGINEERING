"""
Phase 4, lesson 4: a model that generalises.

Trains a language model that represents each word as a handful of numbers
rather than as a slot, so that what it learns about one word carries to words
used like it. Everything from phase 2 and phase 3 meets here.

The data is split three ways rather than two. Training fits the weights, the
validation part decides when to stop, and the test part is not looked at until
the end. That third split exists because choosing when to stop is itself a
decision informed by data, and a score chosen on the data it is measured on is
not a score.

Run it with:  python solve.py
"""

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


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def marked(sentences):
    return [[START] + sentence + [END] for sentence in sentences]


def pairs(sentences, known):
    """Adjacent pairs, with rare words folded into one unknown token.

    Folding keeps the model small enough to train in plain Python, and it is
    what real systems do as well: no vocabulary can hold every word, so there
    is always a token meaning "something I do not have".
    """
    def fold(word):
        return word if word in known else UNKNOWN

    return [(fold(first), fold(second))
            for sentence in sentences
            for first, second in zip(sentence, sentence[1:])]


def perplexity(data, probability):
    carried = 0.0

    for first, second in data:
        chance = probability(first, second)

        if chance <= 0:
            return inf

        carried += log(chance)

    return exp(-carried / len(data))


def start_numbers(rows, width):
    """Fixed starting values: uneven, small, and the same on every machine."""
    return [[0.05 * (((row * 7 + column * 13) % 17) - 8) / 8
             for column in range(width)]
            for row in range(rows)]


def main() -> None:
    sentences = read_corpus()

    training = marked(sentences[:TRAIN_UNTIL])
    validation = marked(sentences[TRAIN_UNTIL:VALIDATE_UNTIL])
    testing = marked(sentences[VALIDATE_UNTIL:])

    counted = Counter(word for sentence in training for word in sentence)
    known = {word for word, _ in counted.most_common(KEEP_WORDS)}

    train_pairs = pairs(training, known)
    validation_pairs = pairs(validation, known)
    test_pairs = pairs(testing, known)

    vocabulary = sorted(known | {UNKNOWN})
    position = {word: index for index, word in enumerate(vocabulary)}
    size = len(vocabulary)

    # The counting model from lesson 2, on this same vocabulary, to beat.
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
        unigram = (single[second] + 1) / (total + size)
        return 0.5 * bigram + 0.5 * unigram

    # A vector per word, and a scoring row per word. Every word the model
    # meets adjusts its vector, and words used alike drift together, which is
    # how evidence about one reaches another.
    meanings = start_numbers(size, DIMENSIONS)
    scorers = start_numbers(size, DIMENSIONS)
    offsets = [0.0] * size

    def spread(first):
        """Scores for every possible next word, turned into probabilities."""
        vector = meanings[position[first]]
        scores = [sum(row[index] * vector[index] for index in range(DIMENSIONS))
                  + offset
                  for row, offset in zip(scorers, offsets)]

        # Subtract the largest before exponentiating: same answer, and it
        # cannot overflow.
        largest = max(scores)
        raised = [exp(score - largest) for score in scores]
        summed = sum(raised)

        return vector, [value / summed for value in raised]

    def neural(first, second):
        return spread(first)[1][position[second]]

    history = []
    best = (inf, 0, None)

    for epoch in range(1, EPOCHS + 1):
        for first, second in train_pairs:
            vector, chances = spread(first)

            # The gradient of the loss with respect to each score is simply
            # the predicted chance, minus one for the word that actually came.
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
        history.append((epoch, score))

        if score < best[0]:
            best = (score, epoch,
                    ([row[:] for row in meanings],
                     [row[:] for row in scorers],
                     offsets[:]))

    meanings, scorers, offsets = best[2]

    counting_test = perplexity(test_pairs, counting)
    neural_test = perplexity(test_pairs, neural)

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("measure\tvalue\n")
        handle.write(f"vocabulary\t{size}\n")
        handle.write(f"best_epoch\t{best[1]}\n")
        handle.write(f"counting_test\t{counting_test:.4f}\n")
        handle.write(f"neural_test\t{neural_test:.4f}\n")

    print(f"vocabulary {size}, {len(train_pairs)} pairs to train on, "
          f"{len(validation_pairs)} to validate, {len(test_pairs)} to test")
    print()
    print("  epoch   perplexity on validation")

    for epoch, score in history:
        mark = "   <- best" if epoch == best[1] else ""
        print(f"  {epoch:5}   {score:8.2f}{mark}")

    print()
    print(f"Stopped at epoch {best[1]}, chosen on validation and nothing else.")
    print()
    print("On the test part, which nothing has looked at until now:")
    print()
    print(f"  counting, mix 0.5   {counting_test:6.2f}")
    print(f"  neural              {neural_test:6.2f}")


if __name__ == "__main__":
    main()
