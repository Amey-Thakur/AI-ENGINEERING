"""
Phase 9, lesson 4: the check.

It retrains every model from the same seeds, repeats the probe, and compares
your numbers. Then it insists on the five facts the lesson turns on, because
each of them would quietly stop being true if the model changed:

    the model without a place table is exactly order blind, to the last
        decimal place and not approximately,
    a place table makes the training set solvable,
    the held-back half of split A is mostly undetermined, so the split cannot
        be used to judge generalisation,
    trained on adjacent pairs the model separates nothing at all,
    and trained on distant pairs it commits to an order on most pairs and,
        at this seed, is wrong about none of them.

That last pair is the lesson. The seed moves the distant run more than the
adjacent one: across eight seeds it is wrong about 5 of 257 commitments and at
one seed it separates nothing at all, so what is checked here is the one run
the lesson reports. If the adjacent run ever started working, the lesson would
be wrong and should be rewritten rather than the check relaxed.

Run it with:  python check.py
"""

import itertools
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE.parent / "order.tsv"
PLACED = HERE / ".work" / "placed.tsv"

STAGES = ["plan", "design", "code", "review", "merge", "test", "build",
          "stage", "deploy", "monitor"]

FIRST_AT = 1
SECOND_AT = 4
TARGET_AT = 7

WIDTH = 8
RATE = 0.10
UPDATES = 4000
SEEDS = (7, 11, 23)

#: How far from exactly half the order blind model is allowed to land. Zero.
#: Its ceiling is a proof, not a tendency: every context carries both answers,
#: so anything other than half would mean the data had changed.
BLIND_MUST_BE_EXACTLY_HALF = True

#: The largest probability difference shuffling the context may produce in the
#: order blind model. A mean of the values does not depend on the order of the
#: values, so this is a floating point tolerance and nothing more.
SHUFFLE_MAY_MOVE = 1e-12

#: How many of the 45 stage pairs the adjacent-pairs run may separate before
#: the lesson's claim that it separates nothing stops being true.
ADJACENT_MAY_COMMIT_TO = 2

#: How many pairs the distant-pairs run must commit to, and how many of those
#: it is allowed to get the wrong way round. Zero is right for this seed and
#: would be wrong as a general claim: other seeds do get some wrong.
DISTANT_MUST_COMMIT_TO = 25
DISTANT_MAY_BE_WRONG_ABOUT = 0


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_sentences():
    rows = []

    for line in SENTENCES.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            sentence, first, second, outcome = line.rstrip("\n").split("\t")
            rows.append((sentence.split(), first, second, outcome))

    return rows


def as_pairs(rows):
    return [rows[at:at + 2] for at in range(0, len(rows), 2)]


def stages_of(pair):
    for _, first, second, outcome in pair:
        if outcome == "normal":
            return first, second

    raise AssertionError("every pair has a normal reading")


def gap_of(pair):
    earlier, later = stages_of(pair)

    return STAGES.index(later) - STAGES.index(earlier)


def settled_by(trained_on):
    known = {stages_of(pair) for pair in trained_on}
    growing = True

    while growing:
        growing = False

        for earlier, middle in list(known):
            for second, later in list(known):
                if middle == second and (earlier, later) not in known:
                    known.add((earlier, later))
                    growing = True

    return known


def project(vector, weights):
    return [sum(vector[i] * weights[i][j] for i in range(len(vector)))
            for j in range(len(weights[0]))]


def softmax(values):
    top = max(values)
    raised = [math.exp(value - top) for value in values]
    total = sum(raised)

    return [value / total for value in raised]


def start(words, seed):
    generator = random.Random(seed)

    def table(height, width):
        return [[generator.uniform(-0.5, 0.5) for _ in range(width)]
                for _ in range(height)]

    return (table(words, WIDTH), table(TARGET_AT, WIDTH), table(WIDTH, WIDTH),
            table(WIDTH, WIDTH), table(WIDTH, WIDTH), table(WIDTH, words))


def vectors_for(context, weights, placed):
    embed, place = weights[0], weights[1]

    if placed:
        return [[embed[token][i] + place[at][i] for i in range(WIDTH)]
                for at, token in enumerate(context)]

    return [list(embed[token]) for token in context]


def forward(context, weights, placed):
    _, _, query_w, key_w, value_w, out_w = weights
    vectors = vectors_for(context, weights, placed)
    seen = len(context)

    query = project(vectors[-1], query_w)
    keys = [project(vector, key_w) for vector in vectors]
    values = [project(vector, value_w) for vector in vectors]

    scale = 1.0 / math.sqrt(WIDTH)
    attention = softmax([sum(query[i] * key[i] for i in range(WIDTH)) * scale
                         for key in keys])
    blended = [sum(attention[j] * values[j][i] for j in range(seen))
               for i in range(WIDTH)]

    return (softmax(project(blended, out_w)), attention, blended, values,
            keys, query, vectors)


def learn(context, target, weights, placed):
    embed, place, query_w, key_w, value_w, out_w = weights
    predicted, attention, blended, values, keys, query, vectors = forward(
        context, weights, placed)
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

    d_vectors = [[0.0] * WIDTH for _ in range(seen)]

    for j in range(seen):
        for i in range(WIDTH):
            d_vectors[j][i] += sum(d_keys[j][k] * key_w[i][k]
                                   for k in range(WIDTH))
            d_vectors[j][i] += sum(d_values[j][k] * value_w[i][k]
                                   for k in range(WIDTH))

    for i in range(WIDTH):
        d_vectors[-1][i] += sum(d_query[k] * query_w[i][k]
                                for k in range(WIDTH))

    for i in range(WIDTH):
        for j in range(WIDTH):
            query_w[i][j] -= RATE * vectors[-1][i] * d_query[j]
            key_w[i][j] -= RATE * sum(vectors[t][i] * d_keys[t][j]
                                      for t in range(seen))
            value_w[i][j] -= RATE * sum(vectors[t][i] * d_values[t][j]
                                        for t in range(seen))

    for at, token in enumerate(context):
        for i in range(WIDTH):
            embed[token][i] -= RATE * d_vectors[at][i]

            if placed:
                place[at][i] -= RATE * d_vectors[at][i]


def main() -> None:
    rows = read_sentences()
    words = sorted({word for sentence, _, _, _ in rows for word in sentence})
    number = {word: at for at, word in enumerate(words)}
    normal, backwards = number["normal"], number["backwards"]
    pairs = as_pairs(rows)
    frame = list(rows[0][0][:TARGET_AT])

    def examples(chosen):
        return [([number[word] for word in sentence[:TARGET_AT]],
                 number[outcome])
                for pair in chosen for sentence, _, _, outcome in pair]

    def train(chosen, placed, seed):
        weights = start(len(words), seed)
        data = examples(chosen)

        for _ in range(max(1, UPDATES // len(data))):
            for context, target in data:
                learn(context, target, weights, placed)

        return weights

    def score(chosen, weights, placed):
        right = 0

        for context, target in examples(chosen):
            predicted, *_ = forward(context, weights, placed)
            right += (normal if predicted[normal] > predicted[backwards]
                      else backwards) == target

        return right

    def verdict(weights, earlier, later):
        answers = []

        for first, second in ((earlier, later), (later, earlier)):
            sentence = list(frame)
            sentence[FIRST_AT], sentence[SECOND_AT] = first, second
            context = [number[word] for word in sentence]
            predicted, *_ = forward(context, weights, True)
            answers.append(predicted[normal] > predicted[backwards])

        if answers[0] and not answers[1]:
            return 1

        if answers[1] and not answers[0]:
            return -1

        return 0

    kept = [pair for at, pair in enumerate(pairs) if at % 3]
    held = pairs[::3]
    expected = {}

    # The order blind model, and the claim that it is exactly order blind.
    flat = train(kept, False, SEEDS[0])
    expected["no position, split A"] = (score(kept, flat, False),
                                        score(held, flat, False))

    generator = random.Random(99)
    worst = 0.0
    changed = 0

    for context, _ in examples(kept) + examples(held):
        shuffled = context[:-1]
        generator.shuffle(shuffled)
        shuffled = shuffled + context[-1:]
        before, *_ = forward(context, flat, False)
        after, *_ = forward(shuffled, flat, False)
        worst = max(worst, max(abs(a - b) for a, b in zip(before, after)))
        changed += (max(range(len(words)), key=lambda i: before[i])
                    != max(range(len(words)), key=lambda i: after[i]))

    if changed or worst > SHUFFLE_MAY_MOVE:
        fail(f"shuffling the context moved {changed} decisions and up to "
             f"{worst:.2e}",
             "a mean of the values cannot depend on the order of the values, "
             "so either a position has leaked into that model or the query is "
             "no longer the last word")

    if BLIND_MUST_BE_EXACTLY_HALF:
        blind = expected["no position, split A"]

        if blind != (len(examples(kept)) // 2, len(examples(held)) // 2):
            fail(f"the order blind model scores {blind}, not exactly half "
                 f"({len(examples(kept)) // 2}, "
                 f"{len(examples(held)) // 2})",
                 "every context in order.tsv carries both answers, so a model "
                 "that cannot see order has to land on exactly half; if it "
                 "did not, the corpus is no longer balanced")

    # The place table, at three seeds.
    for seed in SEEDS:
        model = train(kept, True, seed)
        expected[f"position embeddings, split A, seed {seed}"] = (
            score(kept, model, True), score(held, model, True))

    fitted = [expected[f"position embeddings, split A, seed {seed}"][0]
              for seed in SEEDS]

    if min(fitted) < len(examples(kept)):
        fail(f"with a place table the training set is fitted "
             f"{min(fitted)} of {len(examples(kept))} at worst, not "
             f"completely",
             "the lesson's first claim is that position is what makes this "
             "task learnable at all, so if the place table no longer fits the "
             "training set the claim needs rewriting")

    # The audit of split A.
    known = settled_by(kept)
    settled = sum(1 for pair in held if stages_of(pair) in known)

    if settled > len(held) // 2:
        fail(f"{settled} of {len(held)} held-back pairs are settled by the "
             f"training pairs, so split A is no longer mostly undetermined",
             "the lesson uses split A as an example of a split that cannot "
             "measure generalisation; if the split got better the point is "
             "gone and the lesson needs rewriting")

    # The two nine-pair runs, which are the lesson.
    runs = (("the nine neighbouring pairs",
             [pair for pair in pairs if gap_of(pair) == 1][:9]),
            ("the nine widest pairs",
             [pair for pair in pairs if gap_of(pair) >= 3][:9]))
    every = list(itertools.combinations(STAGES, 2))
    commitments = {}

    for name, chosen in runs:
        rest = [pair for pair in pairs if pair not in chosen]
        model = train(chosen, True, SEEDS[0])
        expected[f"position embeddings, {name}"] = (
            score(chosen, model, True), score(rest, model, True))
        verdicts = {pair: verdict(model, *pair) for pair in every}
        commits = [pair for pair in every if verdicts[pair]]
        commitments[name] = (commits,
                             sum(1 for pair in commits
                                 if verdicts[pair] == -1))

    adjacent, distant = runs[0][0], runs[1][0]

    if len(commitments[adjacent][0]) > ADJACENT_MAY_COMMIT_TO:
        fail(f"trained on adjacent pairs the model separates "
             f"{len(commitments[adjacent][0])} of {len(every)} stage pairs",
             "the lesson's claim is that adjacent pairs teach it no order at "
             "all; if it has started separating them, say so and rewrite the "
             "lesson rather than relaxing this")

    if len(commitments[distant][0]) < DISTANT_MUST_COMMIT_TO:
        fail(f"trained on distant pairs the model separates only "
             f"{len(commitments[distant][0])} of {len(every)} stage pairs",
             "the lesson's claim is that the same model learns a usable scale "
             "from well separated examples, so this is the half of the "
             "comparison that has to work")

    if commitments[distant][1] > DISTANT_MAY_BE_WRONG_ABOUT:
        fail(f"trained on distant pairs the model puts "
             f"{commitments[distant][1]} stage pairs the wrong way round",
             "at this seed the lesson reports none of them wrong, which is "
             "what makes a line the right description of what it learned; a "
             "wrong commitment here means that description has stopped "
             "fitting")

    held_back_adjacent = expected[f"position embeddings, {adjacent}"][1]
    held_back_distant = expected[f"position embeddings, {distant}"][1]

    if held_back_distant <= held_back_adjacent:
        fail(f"the distant run scores {held_back_distant} held back and the "
             f"adjacent run {held_back_adjacent}, so which examples it saw no "
             f"longer decides the outcome",
             "the whole lesson is that the same model on the same number of "
             "examples and updates succeeds or fails depending on which pairs "
             "it was shown")

    # Now compare what you reported.
    if not PLACED.exists():
        fail("there is no .work/placed.tsv",
             "report every model, on the half it trained on and the half held "
             "back")

    lines = [line for line in PLACED.read_text(encoding="utf-8").splitlines()
             if line.strip()]

    if lines and lines[0].split("\t")[:1] == ["what"]:
        lines = lines[1:]

    yours = {}

    for index, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 3:
            fail(f"line {index} has {len(parts)} columns, and needs 3",
                 "the name, how many right on the half it trained on, and how "
                 "many on the half held back")

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
                 "the seeds are fixed, so a different number means the model "
                 "or the split differs rather than the luck")

    print(f"PASS  order blind to {worst:.0e} and exactly half, a place table "
          f"fits {min(fitted)} of {len(examples(kept))}, "
          f"{len(held) - settled} of {len(held)} of split A undetermined, and "
          f"the same nine pairs' worth of examples separates "
          f"{len(commitments[adjacent][0])} of {len(every)} stage pairs from "
          f"neighbours against {len(commitments[distant][0])} from distant "
          f"pairs, {commitments[distant][1]} of them wrong")


if __name__ == "__main__":
    main()
