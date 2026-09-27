"""
Lesson 4: tell the truth.

Trains on part of the data, and scores on the part it never saw.

The split is by position and not at random: the messages alternate question,
statement, question, statement down the file, so taking the first forty and the
last twenty gives two balanced halves and gives them identically on every
machine. A shuffle would need a seed, and a seed is one more thing that can
quietly differ between two people comparing results.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
WEIGHTS = HERE / ".work" / "weights.tsv"
SCORES = HERE / ".work" / "scores.tsv"

TRAIN_SIZE = 40
PASSES = 10


def read_messages(path):
    rows = []

    with open(path, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.strip()
            if line:
                label, message = line.split("\t")
                rows.append((label, sorted(set(message.split()))))

    return rows


def score(words, weights, bias):
    total = bias

    for word in words:
        total += weights.get(word, 0)

    return total


def train(rows):
    weights = {}
    bias = 0

    for _ in range(PASSES):
        mistakes = 0

        for label, words in rows:
            target = 1 if label == "question" else -1
            guess = 1 if score(words, weights, bias) > 0 else -1

            if guess != target:
                mistakes += 1

                for word in words:
                    weights[word] = weights.get(word, 0) + target

                bias += target

        if mistakes == 0:
            break

    return weights, bias


def accuracy(rows, weights, bias):
    right = sum(
        1 for label, words in rows
        if (score(words, weights, bias) > 0) == (label == "question")
    )

    return right, right / len(rows)


def main() -> None:
    rows = read_messages(MESSAGES)

    training = rows[:TRAIN_SIZE]
    held_back = rows[TRAIN_SIZE:]

    # Trained on the first part only. The second part does not exist as far as
    # this line is concerned, and that is the entire point of the lesson.
    weights, bias = train(training)

    train_right, train_score = accuracy(training, weights, bias)
    test_right, test_score = accuracy(held_back, weights, bias)

    WEIGHTS.parent.mkdir(parents=True, exist_ok=True)

    with open(WEIGHTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tweight\n")
        handle.write(f"__bias__\t{bias}\n")

        for word in sorted(weights):
            handle.write(f"{word}\t{weights[word]}\n")

    with open(SCORES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("split\tright\ttotal\taccuracy\n")
        handle.write(f"train\t{train_right}\t{len(training)}\t{train_score:.4f}\n")
        handle.write(f"test\t{test_right}\t{len(held_back)}\t{test_score:.4f}\n")

    unseen = sum(
        1 for _, words in held_back
        for word in words if word not in weights
    )

    print(f"Trained on {len(training)} messages, tested on {len(held_back)} it never saw")
    print()
    print(f"  On what it learned from:  {train_right:2} of {len(training)}"
          f"   {train_score:.1%}")
    print(f"  On what it never saw:     {test_right:2} of {len(held_back)}"
          f"   {test_score:.1%}")
    print()
    print(f"The held back messages contain {unseen} words the model has no "
          f"weight for.")
    print("It is deciding those messages on the words it does know, and on the bias.")


if __name__ == "__main__":
    main()
