"""
Phase 9, lesson 2: looking at every word at once.

Lesson 1 left a ceiling of exactly half, because the model could only see one
word back and the word it needed was five back.

Attention removes that limit in one move. Instead of reading the previous
word, the model looks at every earlier word at the same time, scores each one
for how much it wants it, and reads a blend weighted by those scores. Nothing
about it requires having seen a pair of words together before, which is what
widening an n-gram would have required.

One head, three projections, a softmax and a weighted sum. About forty lines
of arithmetic, and all of it written out here rather than called.

Run it with:  python solve.py
"""

import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE / "agreement.tsv"
SCORES = HERE / ".work" / "scores.tsv"

SUBJECT_AT = 1
TARGET_AT = 6

#: Width of the space the words are projected into. Small on purpose: the
#: whole model has to fit in a reader's head as well as in memory.
WIDTH = 8

EPOCHS = 150
RATE = 0.10

#: A seed, so the starting weights are random in shape and identical on every
#: machine.
SEED = 7

SHOW = 2


def read_sentences():
    rows = []

    with open(SENTENCES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")

            if line:
                sentence, subject, target = line.split("\t")
                rows.append((sentence.split(), subject, target))

    return rows


def split(rows):
    """Pairs stay together, and every subject appears on both sides.

    The corpus holds three pairs per subject, so taking every third pair for
    the test set puts one pair of each subject there and leaves two in
    training. A sentence and its opposite are never separated, so the model
    cannot answer by recognising a sentence it has already seen.
    """
    pairs = [rows[at:at + 2] for at in range(0, len(rows), 2)]
    held_back = pairs[::3]
    kept = [pair for index, pair in enumerate(pairs) if index % 3]

    return ([row for pair in kept for row in pair],
            [row for pair in held_back for row in pair])


def table(height, width, generator):
    return [[generator.uniform(-0.5, 0.5) for _ in range(width)]
            for _ in range(height)]


def project(vector, weights):
    """One matrix multiply, written out."""
    return [sum(vector[i] * weights[i][j] for i in range(len(vector)))
            for j in range(len(weights[0]))]


def softmax(values):
    """The largest is subtracted first, which stops exp overflowing."""
    top = max(values)
    raised = [math.exp(value - top) for value in values]
    total = sum(raised)

    return [value / total for value in raised]


def forward(context, weights):
    """Attend over the context, then score every word in the vocabulary."""
    embed, query_w, key_w, value_w, out_w = weights
    vectors = [embed[token] for token in context]

    # The query comes from the last word seen, because that is where the
    # prediction is being made from. The keys and values come from everywhere.
    query = project(vectors[-1], query_w)
    keys = [project(vector, key_w) for vector in vectors]
    values = [project(vector, value_w) for vector in vectors]

    # How much this position wants each earlier one. Dividing by the square
    # root of the width keeps the scores small enough that the softmax does
    # not saturate into a hard choice before training has learned anything.
    scale = 1.0 / math.sqrt(WIDTH)
    scores = [sum(query[i] * key[i] for i in range(WIDTH)) * scale
              for key in keys]
    attention = softmax(scores)

    blended = [sum(attention[j] * values[j][i] for j in range(len(values)))
               for i in range(WIDTH)]

    return softmax(project(blended, out_w)), attention, blended, values, keys, query, vectors


def learn(context, target, weights):
    """One step of gradient descent, with every derivative written out."""
    embed, query_w, key_w, value_w, out_w = weights
    predicted, attention, blended, values, keys, query, vectors = forward(
        context, weights)
    words = len(out_w[0])
    seen = len(context)

    # Cross entropy through softmax: the predicted probability, minus one at
    # the true word. Phase 4 lesson 4 derived this.
    d_logits = list(predicted)
    d_logits[target] -= 1.0

    d_blended = [sum(d_logits[j] * out_w[i][j] for j in range(words))
                 for i in range(WIDTH)]

    for i in range(WIDTH):
        for j in range(words):
            out_w[i][j] -= RATE * blended[i] * d_logits[j]

    # Back through the weighted sum: the blend is linear in both the attention
    # weights and the values, so each takes the other as its coefficient.
    d_attention = [sum(d_blended[i] * values[j][i] for i in range(WIDTH))
                   for j in range(seen)]
    d_values = [[d_blended[i] * attention[j] for i in range(WIDTH)]
                for j in range(seen)]

    # Back through the softmax over positions. A change in one score moves
    # every weight, so the shared term is subtracted from each.
    shared = sum(d_attention[j] * attention[j] for j in range(seen))
    scale = 1.0 / math.sqrt(WIDTH)
    d_scores = [attention[j] * (d_attention[j] - shared) * scale
                for j in range(seen)]

    d_query = [sum(d_scores[j] * keys[j][i] for j in range(seen))
               for i in range(WIDTH)]
    d_keys = [[d_scores[j] * query[i] for i in range(WIDTH)]
              for j in range(seen)]

    for i in range(WIDTH):
        for j in range(WIDTH):
            query_w[i][j] -= RATE * vectors[-1][i] * d_query[j]
            key_w[i][j] -= RATE * sum(vectors[t][i] * d_keys[t][j]
                                      for t in range(seen))
            value_w[i][j] -= RATE * sum(vectors[t][i] * d_values[t][j]
                                        for t in range(seen))


def score(examples, weights, was, were):
    """Agreement is judged by which of the two the model prefers."""
    right = 0

    for context, target in examples:
        predicted, *_ = forward(context, weights)
        right += (was if predicted[was] > predicted[were] else were) == target

    return right


def main() -> None:
    rows = read_sentences()
    words = sorted({word for sentence, _, _ in rows for word in sentence})
    number = {word: at for at, word in enumerate(words)}
    was, were = number["was"], number["were"]

    kept, held_back = split(rows)

    def examples(data):
        return [([number[word] for word in sentence[:TARGET_AT]],
                 number[sentence[TARGET_AT]]) for sentence, _, _ in data]

    training, testing = examples(kept), examples(held_back)

    generator = random.Random(SEED)
    weights = (
        table(len(words), WIDTH, generator),
        table(WIDTH, WIDTH, generator),
        table(WIDTH, WIDTH, generator),
        table(WIDTH, WIDTH, generator),
        table(WIDTH, len(words), generator),
    )

    for _ in range(EPOCHS):
        for context, target in training:
            learn(context, target, weights)

    on_training = score(training, weights, was, were)
    on_testing = score(testing, weights, was, were)
    ceiling = len(rows) // 2

    SCORES.parent.mkdir(parents=True, exist_ok=True)

    with open(SCORES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("model\tright\tasked\n")
        handle.write(f"bigram ceiling\t{ceiling}\t{len(rows)}\n")
        handle.write(f"attention, trained on\t{on_training}\t"
                     f"{len(training)}\n")
        handle.write(f"attention, held back\t{on_testing}\t{len(testing)}\n")

    print(f"{len(words)} words, {len(training)} sentences to train on, "
          f"{len(testing)} held back.")
    print(f"One head, {WIDTH} wide, {EPOCHS} passes.")
    print()
    print("  model                    right      of")
    print(f"  bigram ceiling          {ceiling:6} {len(rows):7}   "
          f"{ceiling / len(rows):6.0%}")
    print(f"  attention, trained on   {on_training:6} {len(training):7}   "
          f"{on_training / len(training):6.0%}")
    print(f"  attention, held back    {on_testing:6} {len(testing):7}   "
          f"{on_testing / len(testing):6.0%}")
    print()

    print("Two held back sentences, and how the weight was spread:")
    print()

    for context, target in testing[:SHOW]:
        predicted, attention, *_ = forward(context, weights)
        said = "was" if predicted[was] > predicted[were] else "were"

        print("  " + " ".join(f"{words[token]:>10}" for token in context))
        print("  " + " ".join(f"{weight:>10.2f}" for weight in attention))
        print(f"  said {said}, wanted {words[target]}")
        print()

    heaviest = [0.0] * TARGET_AT

    for context, _ in training:
        _, attention, *_ = forward(context, weights)

        for at, weight in enumerate(attention):
            heaviest[at] += weight / len(training)

    print("Average weight per position, over the training sentences:")
    print("  position  " + "  ".join(f"{at:4}" for at in range(TARGET_AT)))
    print("  weight    " + "  ".join(f"{weight:.2f}" for weight in heaviest))
    print()

    top = max(heaviest)
    tied = [at for at, weight in enumerate(heaviest)
            if round(weight, 2) == round(top, 2)]
    flat = 1.0 / TARGET_AT

    print(f"Heaviest: {', '.join(str(at) for at in tied)}, at "
          f"{top:.2f} each. Spreading the weight evenly would")
    print(f"give every position {flat:.2f}, so the subject at position "
          f"{SUBJECT_AT} is not picked out.")
    print()
    print("The two sentences above need opposite answers and were given "
          "almost the same")
    print(f"weights. It still answered one of them correctly, and the next "
          f"lesson is about how.")


if __name__ == "__main__":
    main()
