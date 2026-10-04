"""
Phase 9, lesson 3: it works without looking.

Lesson 2 left a head that clears a ceiling no n-gram can reach, with attention
weights that are nearly flat and nearly identical between the two sentences it
is distinguishing. Something is carrying the signal and it does not appear to
be the weights.

This finds it, by taking things away.

Three questions, each answered by removing something and measuring:

    Does the head need its weights at all?   Train one with the weights nailed
                                             to uniform and compare.
    Does the trained head use its weights?   Force them uniform at test time,
                                             without retraining.
    Where is the signal then?                Silence one position's value at a
                                             time and watch which one matters.

Run it with:  python solve.py
"""

import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE / "agreement.tsv"
LOCATED = HERE / ".work" / "located.tsv"

SUBJECT_AT = 1
TARGET_AT = 6

WIDTH = 8
EPOCHS = 150
RATE = 0.10

#: Both models start from this seed, so they begin from identical weights and
#: the only difference between them is whether the attention is learned.
SEED = 7


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
    """Pairs stay together and every subject appears on both sides."""
    pairs = [rows[at:at + 2] for at in range(0, len(rows), 2)]

    return ([row for index, pair in enumerate(pairs) if index % 3
             for row in pair],
            [row for pair in pairs[::3] for row in pair])


def project(vector, weights):
    return [sum(vector[i] * weights[i][j] for i in range(len(vector)))
            for j in range(len(weights[0]))]


def softmax(values):
    top = max(values)
    raised = [math.exp(value - top) for value in values]
    total = sum(raised)

    return [value / total for value in raised]


def start(words):
    generator = random.Random(SEED)

    def table(height, width):
        return [[generator.uniform(-0.5, 0.5) for _ in range(width)]
                for _ in range(height)]

    return (table(words, WIDTH), table(WIDTH, WIDTH), table(WIDTH, WIDTH),
            table(WIDTH, WIDTH), table(WIDTH, words))


def forward(context, weights, learned, flatten=False, silence=None):
    """One pass, with two switches for the experiments below.

    `flatten` replaces the attention weights with an even share, which is what
    a model with no query and no key would produce. `silence` zeroes one
    position's value, so its contribution to the blend is removed while
    everything else stays as it was.
    """
    embed, query_w, key_w, value_w, out_w = weights
    vectors = [embed[token] for token in context]
    seen = len(context)

    query = project(vectors[-1], query_w)
    keys = [project(vector, key_w) for vector in vectors]
    values = [project(vector, value_w) for vector in vectors]

    if silence is not None:
        values[silence] = [0.0] * WIDTH

    if flatten or not learned:
        attention = [1.0 / seen] * seen
    else:
        scale = 1.0 / math.sqrt(WIDTH)
        attention = softmax([sum(query[i] * key[i] for i in range(WIDTH))
                             * scale for key in keys])

    blended = [sum(attention[j] * values[j][i] for j in range(seen))
               for i in range(WIDTH)]

    return (softmax(project(blended, out_w)), attention, blended, values,
            keys, query, vectors)


def learn(context, target, weights, learned):
    embed, query_w, key_w, value_w, out_w = weights
    predicted, attention, blended, values, keys, query, vectors = forward(
        context, weights, learned)
    words = len(out_w[0])
    seen = len(context)

    d_logits = list(predicted)
    d_logits[target] -= 1.0
    d_blended = [sum(d_logits[j] * out_w[i][j] for j in range(words))
                 for i in range(WIDTH)]

    for i in range(WIDTH):
        for j in range(words):
            out_w[i][j] -= RATE * blended[i] * d_logits[j]

    d_attention = [sum(d_blended[i] * values[j][i] for i in range(WIDTH))
                   for j in range(seen)]
    d_values = [[d_blended[i] * attention[j] for i in range(WIDTH)]
                for j in range(seen)]

    # With the weights nailed to an even share there is no softmax to go back
    # through and no query or key to move, so those gradients do not exist.
    if learned:
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
            if learned:
                query_w[i][j] -= RATE * vectors[-1][i] * d_query[j]
                key_w[i][j] -= RATE * sum(vectors[t][i] * d_keys[t][j]
                                          for t in range(seen))

            value_w[i][j] -= RATE * sum(vectors[t][i] * d_values[t][j]
                                        for t in range(seen))


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

    def train(learned):
        weights = start(len(words))

        for _ in range(EPOCHS):
            for context, target in training:
                learn(context, target, weights, learned)

        return weights

    def score(data, weights, learned, **switches):
        right = 0

        for context, target in data:
            predicted, *_ = forward(context, weights, learned, **switches)
            right += (was if predicted[was] > predicted[were]
                      else were) == target

        return right

    head = train(True)
    pooled = train(False)

    rows_out = [
        ("the attention head", score(training, head, True),
         score(testing, head, True)),
        ("an even share, trained that way", score(training, pooled, False),
         score(testing, pooled, False)),
        ("the head, weights evened at test", score(training, head, True,
                                                   flatten=True),
         score(testing, head, True, flatten=True)),
    ]

    silenced = [(at, score(training, head, True, silence=at),
                 score(testing, head, True, silence=at))
                for at in range(TARGET_AT)]

    LOCATED.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCATED, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("what\ttrained on\theld back\n")

        for name, on_training, on_testing in rows_out:
            handle.write(f"{name}\t{on_training}\t{on_testing}\n")

        for at, on_training, on_testing in silenced:
            handle.write(f"position {at} silenced\t{on_training}\t"
                         f"{on_testing}\n")

    print(f"{len(training)} sentences to train on, {len(testing)} held back. "
          f"Chance is {len(testing) // 2} of {len(testing)}.")
    print()
    print("  what                                 trained on   held back")

    for name, on_training, on_testing in rows_out:
        print(f"  {name:34}  {on_training:3} of {len(training)}   "
              f"{on_testing:3} of {len(testing)}")

    print()
    print("Does it need the weights? An even share, with no query and no key "
          "anywhere in it,")
    print(f"reaches {rows_out[1][2]} of {len(testing)} where the head reaches "
          f"{rows_out[0][2]}. The learned weights are worth "
          f"{rows_out[0][2] - rows_out[1][2]}.")
    print()
    print(f"Does the trained head use them? Evening its own weights at test "
          f"time costs it")
    print(f"{rows_out[0][2] - rows_out[2][2]} of {len(testing)}. It had "
          f"barely been relying on them.")
    print()
    print("So where is the signal? Silence one position's value at a time:")
    print()
    print("  silenced                             trained on   held back")

    for at, on_training, on_testing in silenced:
        note = "  <- the subject" if at == SUBJECT_AT else ""
        print(f"  position {at}                            "
              f"{on_training:3} of {len(training)}   "
              f"{on_testing:3} of {len(testing)}{note}")

    subject = next(row for row in silenced if row[0] == SUBJECT_AT)
    others = [row for row in silenced if row[0] != SUBJECT_AT]
    worst = min(row[2] for row in others)

    print()
    print(f"Silencing the subject's value takes it to {subject[2]} of "
          f"{len(testing)}, which is chance.")
    print(f"Silencing any other position leaves it at {worst} or better.")
    print()
    print("The signal is one vector: the value at the subject's position. The "
          "weights decide")
    print("how much of it reaches the output, and an even share passes enough "
          "of it along.")


if __name__ == "__main__":
    main()
