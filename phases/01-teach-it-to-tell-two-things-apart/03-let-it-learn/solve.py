"""
Lesson 3: let it learn.

Gives every word a weight, starting at nothing, and adjusts those weights every
time the program gets a message wrong. That loop is the whole of learning here:
a way to be wrong, and a rule for what to change when you are.

Nothing is random. The messages are visited in the order they sit in the file
and the weights start at zero, so this produces the same answer every time it
is run, on any machine.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
WEIGHTS = HERE / ".work" / "weights.tsv"

PASSES = 10
SHOW = 6


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
    """How strongly this message leans towards being a question."""
    total = bias

    for word in words:
        total += weights.get(word, 0)

    return total


def train(rows):
    """Adjust the weights every time the current ones get a message wrong."""
    weights = {}
    bias = 0
    history = []

    for pass_number in range(1, PASSES + 1):
        mistakes = 0

        for label, words in rows:
            # +1 means question, -1 means statement. One number, so that being
            # wrong has a direction as well as a size.
            target = 1 if label == "question" else -1
            guess = 1 if score(words, weights, bias) > 0 else -1

            if guess != target:
                mistakes += 1

                # Wrong, so move every word in this message towards the right
                # answer. Words that keep appearing in mistakes keep moving,
                # and words that are never in a mistake never move at all.
                for word in words:
                    weights[word] = weights.get(word, 0) + target

                bias += target

        history.append(mistakes)

        if mistakes == 0:
            break

    return weights, bias, history


def main() -> None:
    rows = read_messages(MESSAGES)
    weights, bias, history = train(rows)

    WEIGHTS.parent.mkdir(parents=True, exist_ok=True)

    with open(WEIGHTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tweight\n")
        handle.write(f"__bias__\t{bias}\n")

        for word in sorted(weights):
            handle.write(f"{word}\t{weights[word]}\n")

    right = sum(
        1 for label, words in rows
        if (score(words, weights, bias) > 0) == (label == "question")
    )

    print(f"Learned {len(weights)} weights in {len(history)} passes")
    print("Mistakes per pass: " + ", ".join(str(count) for count in history))
    print(f"Right on the data it learned from: {right} of {len(rows)}, "
          f"{right / len(rows):.1%}")
    print()

    ranked = sorted(weights, key=lambda word: (-weights[word], word))

    print("Words it decided mean question:")
    for word in ranked[:SHOW]:
        print(f"  {word:12} {weights[word]:+d}")

    print()
    print("Words it decided mean statement:")
    for word in sorted(ranked[-SHOW:], key=lambda word: (weights[word], word)):
        print(f"  {word:12} {weights[word]:+d}")


if __name__ == "__main__":
    main()
