"""
Lesson 5: when it breaks.

Trains exactly as lesson 4 did, then stops looking at the score and reads the
individual failures instead: what the model was asked, what it answered, how
strongly, and how much of the message it had never seen before.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
WEIGHTS = HERE / ".work" / "weights.tsv"
ERRORS = HERE / ".work" / "errors.tsv"

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
                rows.append((label, message))

    return rows


def features(message):
    return sorted(set(message.split()))


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

        for label, message in rows:
            words = features(message)
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


def main() -> None:
    rows = read_messages(MESSAGES)
    training, held_back = rows[:TRAIN_SIZE], rows[TRAIN_SIZE:]

    weights, bias = train(training)

    WEIGHTS.parent.mkdir(parents=True, exist_ok=True)

    with open(WEIGHTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tweight\n")
        handle.write(f"__bias__\t{bias}\n")
        for word in sorted(weights):
            handle.write(f"{word}\t{weights[word]}\n")

    wrong = []

    for label, message in held_back:
        words = features(message)
        total = score(words, weights, bias)
        guess = "question" if total > 0 else "statement"

        if guess != label:
            unknown = sum(1 for word in words if word not in weights)
            wrong.append((message, label, guess, total, unknown, len(words)))

    with open(ERRORS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("message\ttrue\tpredicted\tscore\n")
        for message, label, guess, total, _, _ in wrong:
            handle.write(f"{message}\t{label}\t{guess}\t{total}\n")

    missed = sum(1 for _, label, _, _, _, _ in wrong if label == "question")

    print(f"{len(wrong)} wrong out of {len(held_back)}")
    print(f"  questions called statements: {missed}")
    print(f"  statements called questions: {len(wrong) - missed}")
    print()
    print("Each failure, with how sure it was and how much it had never seen:")
    print()

    for message, label, guess, total, unknown, size in wrong:
        print(f"  {message}")
        print(f"    really a {label}, called a {guess}, score {total:+}")
        print(f"    {unknown} of its {size} words were new to the model")
        print()


if __name__ == "__main__":
    main()
