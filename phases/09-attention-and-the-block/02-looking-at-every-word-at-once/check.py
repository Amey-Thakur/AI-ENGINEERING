"""
Phase 9, lesson 2: the check.

It trains the head again from the same seed and compares your numbers, then
insists on the two things that make the result mean anything.

First, that every subject word appears on both sides of the split. If a noun
were held back entirely, a low score would only show the model had never met
the word, which is phase 3's vocabulary wall rather than anything about
attention.

Second, that the held back score clears what a model capped at half could
reach by luck, using phase 7 lesson 2's test. Beating a ceiling on twenty
questions is not impressive on its own, and the arithmetic says whether this
one is.

Run it with:  python check.py
"""

import math
import random
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE / "agreement.tsv"
SCORES = HERE / ".work" / "scores.tsv"

SUBJECT_AT = 1
TARGET_AT = 6
WIDTH = 8
EPOCHS = 150
RATE = 0.10
SEED = 7

#: How often luck alone is allowed to explain the result.
THRESHOLD = 0.05


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


def forward(context, weights):
    embed, query_w, key_w, value_w, out_w = weights
    vectors = [embed[token] for token in context]
    query = project(vectors[-1], query_w)
    keys = [project(vector, key_w) for vector in vectors]
    values = [project(vector, value_w) for vector in vectors]
    scale = 1.0 / math.sqrt(WIDTH)
    scores = [sum(query[i] * key[i] for i in range(WIDTH)) * scale
              for key in keys]
    attention = softmax(scores)
    blended = [sum(attention[j] * values[j][i] for j in range(len(values)))
               for i in range(WIDTH)]

    return (softmax(project(blended, out_w)), attention, blended, values,
            keys, query, vectors)


def learn(context, target, weights):
    embed, query_w, key_w, value_w, out_w = weights
    predicted, attention, blended, values, keys, query, vectors = forward(
        context, weights)
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


def luck(right, asked):
    """How often a model capped at half scores this well or better."""
    return sum(comb(asked, i) for i in range(right, asked + 1)) / 2 ** asked


def main() -> None:
    rows = read_sentences()
    words = sorted({word for sentence, _, _ in rows for word in sentence})
    number = {word: at for at, word in enumerate(words)}
    was, were = number["was"], number["were"]

    kept, held_back = split(rows)

    if not kept or not held_back:
        fail("the split left one side empty",
             "every third pair is held back and the rest are kept")

    in_training = {subject for _, subject, _ in kept}
    in_testing = {subject for _, subject, _ in held_back}
    unseen = in_testing - in_training

    if unseen:
        fail(f"{len(unseen)} subject words appear only in the held back half, "
             f"such as {sorted(unseen)[0]!r}",
             "a noun the model never met would fail for phase 3's reason "
             "rather than this lesson's, so every subject has to appear on "
             "both sides")

    def examples(data):
        return [([number[word] for word in sentence[:TARGET_AT]],
                 number[sentence[TARGET_AT]]) for sentence, _, _ in data]

    training, testing = examples(kept), examples(held_back)

    generator = random.Random(SEED)
    weights = (
        [[generator.uniform(-0.5, 0.5) for _ in range(WIDTH)]
         for _ in range(len(words))],
        *[[[generator.uniform(-0.5, 0.5) for _ in range(WIDTH)]
           for _ in range(WIDTH)] for _ in range(3)],
        [[generator.uniform(-0.5, 0.5) for _ in range(len(words))]
         for _ in range(WIDTH)],
    )

    for _ in range(EPOCHS):
        for context, target in training:
            learn(context, target, weights)

    def measure(data):
        right = 0

        for context, target in data:
            predicted, *_ = forward(context, weights)
            right += (was if predicted[was] > predicted[were]
                      else were) == target

        return right

    expected = {
        "bigram ceiling": (len(rows) // 2, len(rows)),
        "attention, trained on": (measure(training), len(training)),
        "attention, held back": (measure(testing), len(testing)),
    }

    on_testing, asked = expected["attention, held back"]
    chance = luck(on_testing, asked)

    if chance > THRESHOLD:
        fail(f"held back {on_testing} of {asked}, which luck alone produces "
             f"{chance:.1%} of the time",
             "a model capped at half would reach that often enough for this "
             "not to be a result, so the head has not cleared the ceiling")

    if not SCORES.exists():
        fail("there is no .work/scores.tsv",
             "report the bigram ceiling and the head on both halves of the "
             "split")

    lines = [line for line in SCORES.read_text(encoding="utf-8").splitlines()
             if line.strip()]

    if lines and lines[0].split("\t")[:1] == ["model"]:
        lines = lines[1:]

    yours = {}

    for index, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 3:
            fail(f"line {index} has {len(parts)} columns, and needs 3",
                 "the model, how many it got right, and how many it was "
                 "asked")

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(f"line {index} holds something that is not a whole number",
                 "both columns after the name are counts")

    for name, numbers in expected.items():
        if name not in yours:
            fail(f"there is no row for {name!r}",
                 f"report all three: {', '.join(expected)}")

        if yours[name] != numbers:
            fail(f"for {name!r} you report {yours[name]} and running it gives "
                 f"{numbers}",
                 "the seed is fixed, so a different number means the model or "
                 "the split differs rather than the luck")

    print(f"PASS  the head holds {on_testing} of {asked} held back against a "
          f"ceiling of {len(rows) // 2} of {len(rows)}, which luck produces "
          f"{chance:.2%} of the time")


if __name__ == "__main__":
    main()
