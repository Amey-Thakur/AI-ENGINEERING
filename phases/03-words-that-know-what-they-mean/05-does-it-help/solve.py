"""
Phase 3, lesson 5: does it help?

Takes the word vectors built in this phase, turns each message into one vector,
trains on the first forty and scores on the last twenty.

It does not help. The whole lesson is in finding out exactly why, because the
reasons are three separate and completely general mistakes, and each one is
worth more than the result would have been.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import log, sin, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
MESSAGES = HERE / "messages.tsv"
SCORES = HERE / ".work" / "scores.tsv"
PREDICTIONS = HERE / ".work" / "predictions.tsv"

WINDOW = 4
DIMENSIONS = 24
ITERATIONS = 40

TRAIN_SIZE = 40
PASSES = 300
RATE = 0.1

OPENERS = {
    "what", "how", "why", "who", "where", "when", "which",
    "is", "are", "was", "were", "do", "does", "did",
    "can", "could", "should", "would", "will", "have", "has",
}


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def read_messages():
    rows = []

    with open(MESSAGES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.strip()
            if line:
                label, message = line.split("\t")
                rows.append((1 if label == "question" else 0, message))

    return rows


def normalise(vector):
    size = sqrt(sum(value * value for value in vector))
    return [value / size for value in vector] if size else vector


def build_vectors(sentences):
    """The whole of phase 3, in one function: count, weight, squeeze."""
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

    words = sorted(profiles)
    contexts = sorted({near for profile in profiles.values() for near in profile})
    slot = {near: index for index, near in enumerate(contexts)}
    rows = {word: {slot[near]: value for near, value in profiles[word].items()}
            for word in words}

    axes = []
    for index in range(DIMENSIONS):
        current = normalise([sin(index * 7.0 + position * 0.7) + 0.1
                             for position in range(len(contexts))])

        for _ in range(ITERATIONS):
            carried = [0.0] * len(contexts)

            for row in rows.values():
                along = sum(value * current[position]
                            for position, value in row.items())

                if along:
                    for position, value in row.items():
                        carried[position] += value * along

            for earlier in axes:
                overlap = sum(a * b for a, b in zip(carried, earlier))
                carried = [a - overlap * b for a, b in zip(carried, earlier)]

            current = normalise(carried)

        axes.append(current)

    return {
        word: [sum(value * axis[position] for position, value in rows[word].items())
               for axis in axes]
        for word in words
    }


def as_vector(message, vectors):
    """A message as the average of the vectors of the words in it."""
    known = [vectors[word] for word in message.split() if word in vectors]

    if not known:
        return [0.0] * DIMENSIONS

    return [sum(vector[index] for vector in known) / len(known)
            for index in range(DIMENSIONS)]


def train(examples, width=DIMENSIONS):
    weights = [0.0] * width
    bias = 0.0

    for _ in range(PASSES):
        for features, label, _ in examples:
            total = bias + sum(w * f for w, f in zip(weights, features))

            if (1 if total > 0 else 0) != label:
                direction = 1 if label == 1 else -1
                weights = [w + direction * RATE * f
                           for w, f in zip(weights, features)]
                bias += direction * RATE

    return weights, bias


def score(examples, weights, bias):
    right = sum(
        1 for features, label, _ in examples
        if ((bias + sum(w * f for w, f in zip(weights, features))) > 0)
        == (label == 1)
    )

    return right, right / len(examples)


def main() -> None:
    vectors = build_vectors(read_lines(CORPUS))
    rows = read_messages()

    built = [(as_vector(message, vectors), label, message)
             for label, message in rows]

    training, held_back = built[:TRAIN_SIZE], built[TRAIN_SIZE:]
    weights, bias = train(training)

    train_right, train_accuracy = score(training, weights, bias)
    test_right, test_accuracy = score(held_back, weights, bias)

    rule_right = sum(
        1 for label, message in rows[TRAIN_SIZE:]
        if (message.split()[0] in OPENERS) == (label == 1)
    )

    first_known = sum(1 for _, message in rows if message.split()[0] in vectors)
    opener_in_corpus = sum(1 for word in sorted(OPENERS) if word in vectors)

    SCORES.parent.mkdir(parents=True, exist_ok=True)

    with open(PREDICTIONS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("predicted\tmessage\n")

        for features, _, message in held_back:
            total = bias + sum(w * f for w, f in zip(weights, features))
            handle.write(f"{'question' if total > 0 else 'statement'}"
                         f"\t{message}\n")

    with open(SCORES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("measure\tvalue\n")
        handle.write(f"vectors_train\t{train_accuracy:.4f}\n")
        handle.write(f"vectors_test\t{test_accuracy:.4f}\n")
        handle.write(f"hand_rule_test\t{rule_right / len(held_back):.4f}\n")
        handle.write(f"first_words_known\t{first_known}\n")
        handle.write(f"openers_in_corpus\t{opener_in_corpus}\n")

    print(f"{len(vectors)} words have vectors, from the corpus")
    print()
    print(f"  On what it learned from:  {train_right:2} of {len(training)}"
          f"   {train_accuracy:.1%}")
    print(f"  On what it never saw:     {test_right:2} of {len(held_back)}"
          f"   {test_accuracy:.1%}")
    print()
    print("On the same twenty held back messages:")
    print()
    print(f"  Hand written rule, phase 1      {rule_right} of 20   "
          f"{rule_right / len(held_back):.1%}")
    print(f"  Bag of words, phase 1           15 of 20   75.0%")
    print(f"  Network, phase 2                15 of 20   75.0%")
    print(f"  Word vectors, this phase        {test_right} of 20   "
          f"{test_accuracy:.1%}")
    print()
    print("The same vectors, used three ways:")
    print()

    ways = (
        ("average of every word", lambda message: as_vector(message, vectors)),
        ("first word only",
         lambda message: vectors.get(message.split()[0], [0.0] * DIMENSIONS)),
        ("first word and the average",
         lambda message: vectors.get(message.split()[0], [0.0] * DIMENSIONS)
         + as_vector(message, vectors)),
    )

    for name, make in ways:
        shaped = [(make(message), label, message) for label, message in rows]
        width = len(shaped[0][0])

        found = train(shaped[:TRAIN_SIZE], width)
        held_right, held_accuracy = score(shaped[TRAIN_SIZE:], *found)
        own_right, own_accuracy = score(shaped[:TRAIN_SIZE], *found)

        print(f"  {name:28} train {own_right:2} of 40   "
              f"test {held_right:2} of 20   {held_accuracy:.0%}")

    print()
    print("Two numbers that explain it:")
    print()
    print(f"  Messages whose first word has a vector: {first_known} of {len(rows)}")
    print(f"  Question openers appearing in the corpus at all: "
          f"{opener_in_corpus} of {len(OPENERS)}")


if __name__ == "__main__":
    main()
