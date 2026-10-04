"""
Phase 9, lesson 4: where a word sits.

Lesson 3 left a model with no query and no key in it that takes the mean of the
values and comes within one question of the learned head. A mean cannot see
order. This lesson gives the model order, in the only way a model of this shape
can have it: a learned vector per position, added to the word's vector before
anything else happens.

Then it measures what that buys, which is not what it looks like at first.

Five measurements, in order:

    Is the mean really order blind?     Shuffle the context and see whether
                                        anything at all changes.
    Does position make order visible?   Train with and without the place table
                                        on the same split, at three seeds.
    Is the held-back number honest?     Audit the split. How many held-back
                                        pairs does the training data settle?
    Does it matter which examples?      Train on nine pairs twice, on adjacent
                                        stages and on distant ones.
    What has it actually learned?       Probe all forty five stage pairs,
                                        including the ones no sentence mentions.

Run it with:  python solve.py
"""

import itertools
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE.parent / "order.tsv"
PLACED = HERE / ".work" / "placed.tsv"

#: The stages in the order they really happen. No sentence says this out loud;
#: the sentences are evidence of it, which is the whole point.
STAGES = ["plan", "design", "code", "review", "merge", "test", "build",
          "stage", "deploy", "monitor"]

FIRST_AT = 1
SECOND_AT = 4
TARGET_AT = 7

WIDTH = 8
RATE = 0.10

#: Every model here gets the same number of weight updates whatever the size of
#: its training set, so a run on nine pairs cannot be waved away as having been
#: trained less than a run on twenty.
UPDATES = 4000

#: Three seeds, because one held-back number from one seed would not show how
#: much of it is luck. These three were chosen for a second reason as well:
#: their results do not move when the arithmetic is perturbed by a single
#: last bit. Seed 11's does, which means its number depends on which C
#: library Python was built against. Going further at the end of the lesson
#: has the measurement.
SEEDS = (7, 13, 23)


def read_sentences():
    rows = []

    with open(SENTENCES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")

            if line:
                sentence, first, second, outcome = line.split("\t")
                rows.append((sentence.split(), first, second, outcome))

    return rows


def as_pairs(rows):
    """The two readings of one stage pair always sit next to each other."""
    return [rows[at:at + 2] for at in range(0, len(rows), 2)]


def stages_of(pair):
    """The earlier stage and the later one, read off the normal sentence."""
    for _, first, second, outcome in pair:
        if outcome == "normal":
            return first, second

    raise AssertionError("every pair has a normal reading")


def gap_of(pair):
    earlier, later = stages_of(pair)

    return STAGES.index(later) - STAGES.index(earlier)


def settled_by(trained_on):
    """Every order that follows from the training pairs by chaining.

    If the training data says the plan precedes the design and the design
    precedes the code, then the plan precedes the code whether or not that
    sentence was ever shown. Anything outside this closure is a question the
    training data does not answer, and no model can be expected to get it right
    except by luck.
    """
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
    """Both models draw from one stream, so only the place table differs.

    The place table is drawn whether or not it will be used, so that every
    table after it gets identical numbers in both models. Without that the two
    models would differ in where they started as well as in their shape, and
    the comparison would mean nothing.
    """
    generator = random.Random(seed)

    def table(height, width):
        return [[generator.uniform(-0.5, 0.5) for _ in range(width)]
                for _ in range(height)]

    return (table(words, WIDTH), table(TARGET_AT, WIDTH), table(WIDTH, WIDTH),
            table(WIDTH, WIDTH), table(WIDTH, WIDTH), table(WIDTH, words))


def vectors_for(context, weights, placed):
    """A word's vector, with its position's vector added in if it has one."""
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

    # The gradient arriving at each position's input vector, which is what the
    # place table needs: a position's vector was added to the word's, so the
    # two of them take the same gradient.
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

    #: Any sentence works as the frame; only the two stage words ever change.
    #: Taking it from the data rather than writing it out again means the probe
    #: below cannot drift away from the sentences the model was trained on.
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
        """Which way round the model will commit to, or nothing.

        It is asked both ways. Saying normal to one ordering and backwards to
        the other is a commitment. Giving the same answer to both is a refusal
        to separate them, and scores exactly one of the two sentences.
        """
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

    sentences = lambda chosen: len(chosen) * 2
    reported = []

    print(f"{len(rows)} sentences built from a {len(STAGES)} stage chain, "
          f"{len(words)} words.")
    print("Every context appears twice, once with each answer, so a model that "
          "cannot tell")
    print("order apart is capped at half whatever else it does.")
    print()

    # 1. Is the mean really order blind? Shuffle the context and look.
    kept = [pair for at, pair in enumerate(pairs) if at % 3]
    held = pairs[::3]

    flat = train(kept, False, SEEDS[0])
    generator = random.Random(99)
    changed = 0
    worst = 0.0

    for context, _ in examples(kept) + examples(held):
        shuffled = context[:-1]
        generator.shuffle(shuffled)
        shuffled = shuffled + context[-1:]
        before, *_ = forward(context, flat, False)
        after, *_ = forward(shuffled, flat, False)
        worst = max(worst, max(abs(a - b) for a, b in zip(before, after)))
        changed += (max(range(len(words)), key=lambda i: before[i])
                    != max(range(len(words)), key=lambda i: after[i]))

    print("Shuffle the context of lesson 3's model, keeping the query word "
          "last:")
    print(f"  decisions changed: {changed} of {len(rows)}")
    print(f"  largest probability difference: {worst:.2e}")
    print()
    print("Not approximately unchanged. Unchanged. Order is not an input to "
          "that model.")
    print()

    # 2. Does a place table make order visible?
    print(f"Split A holds back every third pair: {sentences(kept)} sentences "
          f"to train on, {sentences(held)} held")
    print(f"back, chance {sentences(held) // 2}. Every model below gets "
          f"{UPDATES} weight updates.")
    print()
    print("  model                                 trained on   held back")

    reported.append(("no position, split A", score(kept, flat, False),
                     score(held, flat, False)))
    print(f"  {'no position':35}  {reported[-1][1]:3} of {sentences(kept)}   "
          f"{reported[-1][2]:3} of {sentences(held)}")

    for seed in SEEDS:
        model = train(kept, True, seed)
        reported.append((f"position embeddings, split A, seed {seed}",
                         score(kept, model, True), score(held, model, True)))
        print(f"  {f'position embeddings, seed {seed}':35}  "
              f"{reported[-1][1]:3} of {sentences(kept)}   "
              f"{reported[-1][2]:3} of {sentences(held)}")

    spread = [row[2] for row in reported[1:]]
    print()
    print(f"Position makes the training set solvable: {reported[0][1]} of "
          f"{sentences(kept)} becomes {reported[1][1]} of "
          f"{sentences(kept)} at all")
    print("three of these seeds, which the model without it cannot do at any "
          "seed at all.")
    print(f"Held back it gives "
          f"{', '.join(str(n) for n in spread[:-1])} and {spread[-1]} against "
          f"a chance of {sentences(held) // 2}.")
    print()

    # 3. Is that held-back number even meaningful?
    known = settled_by(kept)
    settled = sum(1 for pair in held if stages_of(pair) in known)
    ceiling = settled * 2 + (len(held) - settled)

    print(f"Before concluding anything about the model, audit the split. Of "
          f"the {len(held)} held-back")
    print("pairs, how many have an order that follows from the training pairs "
          "by chaining?")
    print()
    print(f"  order settled by the training pairs:        "
          f"{settled:2} of {len(held)}")
    print(f"  order the training data never determines:   "
          f"{len(held) - settled:2} of {len(held)}")
    print(f"  so the most an order learner could expect:  "
          f"{ceiling:2} of {sentences(held)}")
    print()
    print(f"{len(held) - settled} of those {len(held)} questions have no "
          f"answer anywhere in the training data.")
    print()

    # 4. Ask something answerable, and change which nine pairs are shown.
    runs = (("the nine neighbouring pairs",
             [pair for pair in pairs if gap_of(pair) == 1][:9]),
            ("the nine widest pairs",
             [pair for pair in pairs if gap_of(pair) >= 3][:9]))

    print(f"Split B asks something answerable. Train on nine pairs and hold "
          f"back the other {len(pairs) - 9}.")
    print(f"Chance is {len(pairs) - 9} of {(len(pairs) - 9) * 2} in both rows, "
          f"and both rows get {UPDATES} updates.")
    print()
    print("  nine pairs trained on                 trained on   held back   "
          "chain settles")

    models = {}

    for name, chosen in runs:
        rest = [pair for pair in pairs if pair not in chosen]
        chains = settled_by(chosen)
        chained = sum(1 for pair in rest if stages_of(pair) in chains)
        model = train(chosen, True, SEEDS[0])
        models[name] = model
        reported.append((f"position embeddings, {name}",
                         score(chosen, model, True), score(rest, model, True)))
        print(f"  {name:35}  {reported[-1][1]:3} of {sentences(chosen)}   "
              f"{reported[-1][2]:3} of {sentences(rest)}   "
              f"{chained:2} of {len(rest)}")

    print()
    print("Read that table twice. The split whose held-back answers are fully "
          "settled by")
    print("chaining is the one the model cannot do at all, and the split where "
          "chaining")
    print("settles nothing is the one it gets most of right.")
    print()

    # 5. So what has it actually learned? Ask it about every stage pair.
    every = list(itertools.combinations(STAGES, 2))
    print(f"So it is not chaining. Probe all {len(every)} stage pairs, "
          f"including the "
          f"{len(every) - len(pairs)} that")
    print("appear in no sentence, and ask which it will commit to an order on:")
    print()
    print("  model trained on                   commits     agrees with the "
          "chain")

    commitments = {}

    for name, _ in runs:
        verdicts = {pair: verdict(models[name], *pair) for pair in every}
        commits = [pair for pair in every if verdicts[pair]]
        agrees = sum(1 for pair in commits if verdicts[pair] == 1)
        commitments[name] = (commits, agrees, verdicts)
        out = f"{agrees:2} of {len(commits):2}" if commits else "nothing to ask"
        print(f"  {name:35}  {len(commits):2} of {len(every)}    {out}")

    widest = runs[1][0]
    commits, agrees, _ = commitments[widest]
    print()
    print("  how far apart the two stages sit   the widest trained model "
          "commits on")

    bands = ((1, "1 stage"), (2, "2 stages"), (3, "3 stages"))

    for distance, label in bands:
        total = [pair for pair in every
                 if STAGES.index(pair[1]) - STAGES.index(pair[0]) == distance]
        got = [pair for pair in total if pair in commits]
        print(f"  {label:33}            {len(got):2} of {len(total)}")

    far = [pair for pair in every
           if STAGES.index(pair[1]) - STAGES.index(pair[0]) >= 4]
    print(f"  {'4 stages or more':33}            "
          f"{len([pair for pair in far if pair in commits]):2} of {len(far)}")

    print()
    print(f"Nothing it commits to is wrong: {agrees} of {len(commits)} agree "
          f"with the chain. What it will")
    print("not do is separate stages that sit next to each other, and trained "
          "on adjacent")
    print(f"pairs alone it separates nothing at all "
          f"({len(commitments[runs[0][0]][0])} of {len(every)}).")
    print()
    print("It has not learned a chain. It has put the ten stages on a line and "
          "compares")
    print("positions on that line, which answers pairs no chain reaches and "
          "fails on pairs")
    print("too close together to tell apart. Position told it where a word "
          "sits. It did")
    print("not give it anything to compare two words with except distance.")

    PLACED.parent.mkdir(parents=True, exist_ok=True)

    with open(PLACED, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("what\ttrained on\theld back\n")

        for name, on_training, on_held in reported:
            handle.write(f"{name}\t{on_training}\t{on_held}\n")


if __name__ == "__main__":
    main()
