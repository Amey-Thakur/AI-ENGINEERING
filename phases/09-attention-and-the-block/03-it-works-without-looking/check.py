"""
Phase 9, lesson 3: the check.

It retrains both models from the same seed, repeats the ablations, and
compares your numbers. Then it insists on the three facts the lesson turns
on, because each of them is the kind of thing that would quietly stop being
true if the model changed:

    silencing the subject's value lands on chance exactly,
    silencing any other position barely moves the score,
    and an even share comes within a question or two of the learned head.

If the last of those ever stopped holding, the lesson would be wrong and the
head would be doing something after all.

Run it with:  python check.py
"""

import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE / "agreement.tsv"
LOCATED = HERE / ".work" / "located.tsv"

SUBJECT_AT = 1
TARGET_AT = 6
WIDTH = 8
EPOCHS = 150
RATE = 0.10
SEED = 7

#: How much the learned weights are allowed to be worth before the lesson's
#: claim that they are nearly idle stops being honest.
WEIGHTS_WORTH_AT_MOST = 2

#: How far silencing a position other than the subject may drop the score.
OTHERS_MAY_COST = 3


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_sentences():
    rows = []

    for line in SENTENCES.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            sentence, subject, target = line.rstrip("\n").split("\t")
            rows.append((sentence.split(), subject, target))

    return rows


def split(rows):
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
    chance = len(testing) // 2

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

    expected = {
        "the attention head": (score(training, head, True),
                               score(testing, head, True)),
        "an even share, trained that way": (score(training, pooled, False),
                                            score(testing, pooled, False)),
        "the head, weights evened at test": (
            score(training, head, True, flatten=True),
            score(testing, head, True, flatten=True)),
    }

    for at in range(TARGET_AT):
        expected[f"position {at} silenced"] = (
            score(training, head, True, silence=at),
            score(testing, head, True, silence=at))

    subject = expected[f"position {SUBJECT_AT} silenced"]

    if subject[1] != chance or subject[0] != len(training) // 2:
        fail(f"silencing the subject's value gives {subject}, not chance "
             f"({len(training) // 2}, {chance})",
             "with that one vector removed the model has nothing left that "
             "distinguishes a pair, so it must land on exactly half")

    for at in range(TARGET_AT):
        if at == SUBJECT_AT:
            continue

        other = expected[f"position {at} silenced"]

        if other[1] < expected["the attention head"][1] - OTHERS_MAY_COST:
            fail(f"silencing position {at} costs "
                 f"{expected['the attention head'][1] - other[1]} questions",
                 "only the subject's position carries the answer, so "
                 "silencing any other one should barely register")

    worth = (expected["the attention head"][1]
             - expected["an even share, trained that way"][1])

    if worth > WEIGHTS_WORTH_AT_MOST:
        fail(f"the learned weights are worth {worth} questions, not nearly "
             f"nothing",
             "the lesson's claim is that an even share does as well, so if "
             "the head has pulled ahead the claim needs rewriting rather "
             "than the test relaxing")

    if not LOCATED.exists():
        fail("there is no .work/located.tsv",
             "report each system and each silenced position, on both halves "
             "of the split")

    lines = [line for line in LOCATED.read_text(encoding="utf-8").splitlines()
             if line.strip()]

    if lines and lines[0].split("\t")[:1] == ["what"]:
        lines = lines[1:]

    yours = {}

    for index, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 3:
            fail(f"line {index} has {len(parts)} columns, and needs 3",
                 "the name, how many right on the training half, and how "
                 "many on the held back half")

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(f"line {index} holds something that is not a whole number",
                 "both columns after the name are counts")

    for name, numbers in expected.items():
        if name not in yours:
            fail(f"there is no row for {name!r}",
                 f"report all {len(expected)} of them")

        if yours[name] != numbers:
            fail(f"for {name!r} you report {yours[name]} and running it gives "
                 f"{numbers}",
                 "the seed is fixed, so a different number means the model or "
                 "the ablation differs rather than the luck")

    print(f"PASS  the weights are worth {worth} of {len(testing)}, silencing "
          f"the subject lands on chance at {subject[1]}, and no other "
          f"position costs more than "
          f"{expected['the attention head'][1] - min(expected[f'position {at} silenced'][1] for at in range(TARGET_AT) if at != SUBJECT_AT)}")


if __name__ == "__main__":
    main()
