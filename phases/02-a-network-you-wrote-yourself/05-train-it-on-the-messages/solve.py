"""
Phase 2, lesson 5: train it on the messages.

Puts the network from this phase on the problem from phase 1, trains it with
backpropagation, and scores it the honest way: on the twenty messages it never
saw.

Then compares it against everything built so far, because a new model that is
not compared against the old one is a press release rather than a result.

Run it with:  python solve.py
"""

import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
SCORES = HERE / ".work" / "scores.tsv"
PREDICTIONS = HERE / ".work" / "predictions.tsv"

TRAIN_SIZE = 40
HIDDEN = 4
EPOCHS = 300
RATE = 0.5

# A seed, so the starting weights are random in shape but identical on every
# machine. Random starts matter: two hidden units that begin the same stay the
# same forever, which is why they cannot all start at zero.
SEED = 7

OPENERS = {
    "what", "how", "why", "who", "where", "when", "which",
    "is", "are", "was", "were", "do", "does", "did",
    "can", "could", "should", "would", "will", "have", "has",
}


def sigmoid(total):
    return 1.0 / (1.0 + math.exp(-total))


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


def build(rows, vocabulary):
    """Each message becomes one number per known word: is it present."""
    built = []

    for label, message in rows:
        words = set(message.split())
        built.append(([1.0 if word in words else 0.0 for word in vocabulary],
                      label, message))

    return built


def start_weights(inputs, generator):
    hidden = [[generator.uniform(-0.5, 0.5) for _ in range(inputs)]
              for _ in range(HIDDEN)]
    hidden_bias = [0.0] * HIDDEN
    output = [generator.uniform(-0.5, 0.5) for _ in range(HIDDEN)]

    return hidden, hidden_bias, output, 0.0


def forward(features, hidden, hidden_bias, output, output_bias):
    activations = []

    for unit in range(len(hidden)):
        total = hidden_bias[unit]

        for index, value in enumerate(features):
            if value:
                total += hidden[unit][index] * value

        activations.append(sigmoid(total))

    total = output_bias
    for unit, activation in enumerate(activations):
        total += output[unit] * activation

    return activations, sigmoid(total)


def train(examples, inputs):
    generator = random.Random(SEED)
    hidden, hidden_bias, output, output_bias = start_weights(inputs, generator)

    for _ in range(EPOCHS):
        for features, label, _ in examples:
            activations, answer = forward(features, hidden, hidden_bias,
                                          output, output_bias)

            delta_out = 2 * (answer - label) * answer * (1 - answer)

            for unit, activation in enumerate(activations):
                delta_hidden = (delta_out * output[unit]
                                * activation * (1 - activation))

                output[unit] -= RATE * delta_out * activation

                for index, value in enumerate(features):
                    if value:
                        hidden[unit][index] -= RATE * delta_hidden * value

                hidden_bias[unit] -= RATE * delta_hidden

            output_bias -= RATE * delta_out

    return hidden, hidden_bias, output, output_bias


def accuracy(examples, network):
    right = sum(
        1 for features, label, _ in examples
        if (forward(features, *network)[1] > 0.5) == (label == 1)
    )

    return right, right / len(examples)


def main() -> None:
    rows = read_messages()

    # The vocabulary comes from the training messages only. Building it from
    # everything would let the held back messages influence the model before
    # it has been scored on them.
    vocabulary = sorted({
        word for _, message in rows[:TRAIN_SIZE] for word in message.split()
    })

    training = build(rows[:TRAIN_SIZE], vocabulary)
    held_back = build(rows[TRAIN_SIZE:], vocabulary)

    network = train(training, len(vocabulary))

    train_right, train_score = accuracy(training, network)
    test_right, test_score = accuracy(held_back, network)

    rule_right = sum(
        1 for label, message in rows[TRAIN_SIZE:]
        if (message.split()[0] in OPENERS) == (label == 1)
    )

    SCORES.parent.mkdir(parents=True, exist_ok=True)

    # The prediction for every held back message, so the reported score can be
    # checked against the model rather than taken on trust.
    with open(PREDICTIONS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("predicted\tmessage\n")

        for features, _, message in held_back:
            answer = forward(features, *network)[1]
            guess = "question" if answer > 0.5 else "statement"
            handle.write(f"{guess}\t{message}\n")

    with open(SCORES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("model\tright\ttotal\taccuracy\n")
        handle.write(f"network_train\t{train_right}\t{len(training)}\t"
                     f"{train_score:.4f}\n")
        handle.write(f"network_test\t{test_right}\t{len(held_back)}\t"
                     f"{test_score:.4f}\n")
        handle.write(f"hand_rule_test\t{rule_right}\t{len(held_back)}\t"
                     f"{rule_right / len(held_back):.4f}\n")

    print(f"{len(vocabulary)} words of vocabulary, from {len(training)} "
          f"training messages")
    print(f"{len(vocabulary) * HIDDEN + HIDDEN + HIDDEN + 1} weights, "
          f"trained on {len(training)} examples")
    print()
    print("  On what it learned from:  "
          f"{train_right:2} of {len(training)}   {train_score:.1%}")
    print("  On what it never saw:     "
          f"{test_right:2} of {len(held_back)}   {test_score:.1%}")
    print()
    print("Everything built so far, on the same twenty held back messages:")
    print()
    print(f"  Hand written rule, phase 1 lesson 2    "
          f"{rule_right} of {len(held_back)}   {rule_right / len(held_back):.1%}")
    print(f"  Perceptron, phase 1 lesson 4           15 of 20   75.0%")
    print(f"  This network                           "
          f"{test_right} of {len(held_back)}   {test_score:.1%}")


if __name__ == "__main__":
    main()
