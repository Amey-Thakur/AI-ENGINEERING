"""
Phase 9, lesson 5: the check.

It builds its own block, proves that block's backward pass against finite
differences, recounts the cost, retrains every configuration and compares your
numbers. The model is written out again here rather than imported from
`solve.py` on purpose: a check that calls the code it is checking cannot catch
a mistake in it, it can only reproduce it.

Then it insists on the four facts the lesson turns on:

    the hand-written backward pass agrees with finite differences,
    the block costs more than the bare head in both parameters and work,
    no difference between these architectures is larger than the spread
        between seeds of a single one of them,
    and at depth the residual and the layer norm do what they are there for.

The third is the lesson's result. An earlier version of this check asserted
something stronger and more flattering, that the block separates nothing the
head could not and that removing the layer norms stops it working. Both held
for the three seeds the lesson first used and failed for the three it uses
now, which is how the lesson ended up being about the spread rather than
about the architecture.

The first is worth keeping for its own sake. The block in this lesson had a
real bug the first time it was written: the input layer norm's gain was
updated inside the loop over positions, so every position after the first
computed its gradient against a gain that had already moved. The loss still
fell, the training looked ordinary, and the broken version scored better on
one seed than the correct one does. Nothing but a finite difference check
found it.

Run it with:  python check.py
"""

import copy
import itertools
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE.parent / "order.tsv"
MEASURED = HERE / ".work" / "measured.tsv"

STAGES = ["plan", "design", "code", "review", "merge", "test", "build",
          "stage", "deploy", "monitor"]

FIRST_AT = 1
SECOND_AT = 4
TARGET_AT = 7
WIDTH = 8
HIDDEN = 4 * WIDTH
RATE = 0.10
UPDATES = 4000
SEEDS = (7, 13, 23)
EPS = 1e-5
NUDGE = 1e-6
GRADIENT_TOLERANCE = 1e-5
DEPTHS = (1, 2, 4, 8, 16, 32)
DEPTH_SEEDS = range(1, 21)

#: Every architecture comparison in this lesson must stay inside the noise:
#: the gap between two configurations' averages may not exceed the spread
#: within either of them. If one ever did, this lesson would have found a real
#: architectural difference and would need rewriting to say so.
GAP_MAY_NOT_EXCEED_SPREAD = True

#: How much more gradient a 32 layer stack with residuals must deliver to its
#: input than the same stack without them. Measured at over 600, so a tenth of
#: that still makes the point and anything less means the measurement itself
#: has stopped working.
RESIDUAL_WORTH_AT_LEAST = 60.0


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


def project(vector, weights):
    return [sum(vector[i] * weights[i][j] for i in range(len(vector)))
            for j in range(len(weights[0]))]


def softmax(values):
    top = max(values)
    raised = [math.exp(value - top) for value in values]
    total = sum(raised)

    return [value / total for value in raised]


def normalise(vector, gain, bias):
    middle = sum(vector) / len(vector)
    spread = sum((value - middle) ** 2 for value in vector) / len(vector)
    deviation = math.sqrt(spread + EPS)
    unit = [(value - middle) / deviation for value in vector]

    return ([gain[i] * unit[i] + bias[i] for i in range(len(vector))],
            unit, deviation)


def normalise_back(d_out, unit, deviation, gain):
    width = len(d_out)
    d_unit = [gain[i] * d_out[i] for i in range(width)]
    mean_d = sum(d_unit) / width
    mean_d_unit = sum(d_unit[i] * unit[i] for i in range(width)) / width

    return ([(d_unit[i] - mean_d - unit[i] * mean_d_unit) / deviation
             for i in range(width)],
            [d_out[i] * unit[i] for i in range(width)], list(d_out))


def start(words, seed, block):
    generator = random.Random(seed)

    def table(height, width):
        return [[generator.uniform(-0.5, 0.5) for _ in range(width)]
                for _ in range(height)]

    weights = {"embed": table(words, WIDTH), "place": table(TARGET_AT, WIDTH),
               "query": table(WIDTH, WIDTH), "key": table(WIDTH, WIDTH),
               "value": table(WIDTH, WIDTH), "out": table(WIDTH, words)}

    if block:
        weights.update({
            "gain in": [1.0] * WIDTH, "bias in": [0.0] * WIDTH,
            "gain mid": [1.0] * WIDTH, "bias mid": [0.0] * WIDTH,
            "up": table(WIDTH, HIDDEN), "up bias": [0.0] * HIDDEN,
            "down": table(HIDDEN, WIDTH), "down bias": [0.0] * WIDTH})

    return weights


def forward(context, weights, block, norms=True):
    seen = len(context)
    embed, place = weights["embed"], weights["place"]
    vectors = [[embed[token][i] + place[at][i] for i in range(WIDTH)]
               for at, token in enumerate(context)]

    if block and norms:
        normed, units, deviations = [], [], []

        for vector in vectors:
            value, unit, deviation = normalise(
                vector, weights["gain in"], weights["bias in"])
            normed.append(value)
            units.append(unit)
            deviations.append(deviation)
    elif block:
        normed = vectors
        units = [list(vector) for vector in vectors]
        deviations = [1.0] * seen
    else:
        normed, units, deviations = vectors, None, None

    query = project(normed[-1], weights["query"])
    keys = [project(vector, weights["key"]) for vector in normed]
    values = [project(vector, weights["value"]) for vector in normed]
    scale = 1.0 / math.sqrt(WIDTH)
    attention = softmax([sum(query[i] * key[i] for i in range(WIDTH)) * scale
                         for key in keys])
    blended = [sum(attention[j] * values[j][i] for j in range(seen))
               for i in range(WIDTH)]
    state = {"vectors": vectors, "normed": normed, "units": units,
             "deviations": deviations, "attention": attention,
             "values": values, "keys": keys, "query": query}

    if not block:
        state["read"] = blended

        return softmax(project(blended, weights["out"])), state

    stream = [vectors[-1][i] + blended[i] for i in range(WIDTH)]

    if norms:
        middle, unit_mid, deviation_mid = normalise(
            stream, weights["gain mid"], weights["bias mid"])
    else:
        middle, unit_mid, deviation_mid = list(stream), list(stream), 1.0

    up_w, up_b = weights["up"], weights["up bias"]
    raised = [sum(middle[i] * up_w[i][j] for i in range(WIDTH)) + up_b[j]
              for j in range(HIDDEN)]
    hidden = [value if value > 0.0 else 0.0 for value in raised]
    down_w, down_b = weights["down"], weights["down bias"]
    lowered = [sum(hidden[j] * down_w[j][i] for j in range(HIDDEN))
               + down_b[i] for i in range(WIDTH)]
    read = [stream[i] + lowered[i] for i in range(WIDTH)]
    state.update({"stream": stream, "middle": middle, "unit mid": unit_mid,
                  "deviation mid": deviation_mid, "hidden": hidden,
                  "read": read})

    return softmax(project(read, weights["out"])), state


def learn(context, target, weights, block, norms=True):
    predicted, state = forward(context, weights, block, norms)
    out_w, embed, place = weights["out"], weights["embed"], weights["place"]
    query_w, key_w, value_w = (weights["query"], weights["key"],
                               weights["value"])
    words = len(out_w[0])
    seen = len(context)
    read = state["read"]

    d_logits = list(predicted)
    d_logits[target] -= 1.0
    d_read = [sum(d_logits[j] * out_w[i][j] for j in range(words))
              for i in range(WIDTH)]

    for i in range(WIDTH):
        for j in range(words):
            out_w[i][j] -= RATE * read[i] * d_logits[j]

    if block:
        d_stream = list(d_read)
        d_lowered = list(d_read)
        down_w, up_w = weights["down"], weights["up"]
        hidden, middle = state["hidden"], state["middle"]
        d_hidden = [sum(d_lowered[i] * down_w[j][i] for i in range(WIDTH))
                    for j in range(HIDDEN)]

        for j in range(HIDDEN):
            for i in range(WIDTH):
                down_w[j][i] -= RATE * hidden[j] * d_lowered[i]

        for i in range(WIDTH):
            weights["down bias"][i] -= RATE * d_lowered[i]

        d_raised = [d_hidden[j] if hidden[j] > 0.0 else 0.0
                    for j in range(HIDDEN)]
        d_middle = [sum(d_raised[j] * up_w[i][j] for j in range(HIDDEN))
                    for i in range(WIDTH)]

        for i in range(WIDTH):
            for j in range(HIDDEN):
                up_w[i][j] -= RATE * middle[i] * d_raised[j]

        for j in range(HIDDEN):
            weights["up bias"][j] -= RATE * d_raised[j]

        if norms:
            back, d_gain, d_bias = normalise_back(
                d_middle, state["unit mid"], state["deviation mid"],
                weights["gain mid"])

            for i in range(WIDTH):
                d_stream[i] += back[i]
                weights["gain mid"][i] -= RATE * d_gain[i]
                weights["bias mid"][i] -= RATE * d_bias[i]
        else:
            for i in range(WIDTH):
                d_stream[i] += d_middle[i]

        d_blended = list(d_stream)
    else:
        d_blended = list(d_read)
        d_stream = None

    attention, values = state["attention"], state["values"]
    keys, query, normed = state["keys"], state["query"], state["normed"]
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
    d_normed = [[0.0] * WIDTH for _ in range(seen)]

    for j in range(seen):
        for i in range(WIDTH):
            d_normed[j][i] += sum(d_keys[j][k] * key_w[i][k]
                                  for k in range(WIDTH))
            d_normed[j][i] += sum(d_values[j][k] * value_w[i][k]
                                  for k in range(WIDTH))

    for i in range(WIDTH):
        d_normed[-1][i] += sum(d_query[k] * query_w[i][k]
                               for k in range(WIDTH))

    for i in range(WIDTH):
        for j in range(WIDTH):
            query_w[i][j] -= RATE * normed[-1][i] * d_query[j]
            key_w[i][j] -= RATE * sum(normed[t][i] * d_keys[t][j]
                                      for t in range(seen))
            value_w[i][j] -= RATE * sum(normed[t][i] * d_values[t][j]
                                        for t in range(seen))

    if block:
        d_vectors = [[0.0] * WIDTH for _ in range(seen)]
        total_gain = [0.0] * WIDTH
        total_bias = [0.0] * WIDTH

        for j in range(seen):
            if norms:
                back, d_gain, d_bias = normalise_back(
                    d_normed[j], state["units"][j], state["deviations"][j],
                    weights["gain in"])
            else:
                back = d_normed[j]
                d_gain = d_bias = [0.0] * WIDTH

            for i in range(WIDTH):
                d_vectors[j][i] += back[i]
                total_gain[i] += d_gain[i]
                total_bias[i] += d_bias[i]

        for i in range(WIDTH):
            weights["gain in"][i] -= RATE * total_gain[i]
            weights["bias in"][i] -= RATE * total_bias[i]
            d_vectors[-1][i] += d_stream[i]
    else:
        d_vectors = d_normed

    for at, token in enumerate(context):
        for i in range(WIDTH):
            embed[token][i] -= RATE * d_vectors[at][i]
            place[at][i] -= RATE * d_vectors[at][i]


def parameters(weights):
    total = 0

    for table in weights.values():
        total += sum(len(row) for row in table) if isinstance(table[0], list) \
            else len(table)

    return total


def multiplies(seen, words, block):
    head = (WIDTH * WIDTH + 2 * seen * WIDTH * WIDTH + seen * WIDTH
            + seen * WIDTH + WIDTH * words)

    if not block:
        return head

    return head + seen * 3 * WIDTH + 3 * WIDTH + 2 * WIDTH * HIDDEN


def depth_stack(depth, seed, residual, normed):
    generator = random.Random(seed)

    def table(height, width):
        return [[generator.gauss(0.0, 1.0 / math.sqrt(height))
                 for _ in range(width)] for _ in range(height)]

    layers = [(table(WIDTH, HIDDEN), table(HIDDEN, WIDTH))
              for _ in range(depth)]
    generator = random.Random(seed + 9999)
    value = [generator.gauss(0.0, 1.0) for _ in range(WIDTH)]
    saved = []

    for up, down in layers:
        if normed:
            unit, deviation = normalise(value, [1.0] * WIDTH,
                                        [0.0] * WIDTH)[1:]
        else:
            unit, deviation = list(value), 1.0

        raised = [sum(unit[i] * up[i][j] for i in range(WIDTH))
                  for j in range(HIDDEN)]
        hidden = [v if v > 0.0 else 0.0 for v in raised]
        lowered = [sum(hidden[j] * down[j][i] for j in range(HIDDEN))
                   for i in range(WIDTH)]
        saved.append((unit, deviation, hidden))
        value = [value[i] + lowered[i] for i in range(WIDTH)] if residual \
            else lowered

    size = lambda v: math.sqrt(sum(c * c for c in v))
    leaving = size(value)
    d = [1.0] * WIDTH

    for (up, down), (unit, deviation, hidden) in zip(reversed(layers),
                                                     reversed(saved)):
        d_hidden = [sum(d[i] * down[j][i] for i in range(WIDTH))
                    for j in range(HIDDEN)]
        d_raised = [d_hidden[j] if hidden[j] > 0.0 else 0.0
                    for j in range(HIDDEN)]
        d_unit = [sum(d_raised[j] * up[i][j] for j in range(HIDDEN))
                  for i in range(WIDTH)]
        d_in = normalise_back(d_unit, unit, deviation, [1.0] * WIDTH)[0] \
            if normed else d_unit
        d = [d_in[i] + d[i] for i in range(WIDTH)] if residual else d_in

    return size(d), leaving


def typical(numbers):
    return math.exp(statistics.fmean(math.log(n) for n in numbers))


def main() -> None:
    global RATE

    rows = read_sentences()
    words = sorted({word for sentence, _, _, _ in rows for word in sentence})
    number = {word: at for at, word in enumerate(words)}
    normal, backwards = number["normal"], number["backwards"]
    pairs = as_pairs(rows)
    frame = list(rows[0][0][:TARGET_AT])
    every = list(itertools.combinations(STAGES, 2))

    def examples(chosen):
        return [([number[word] for word in sentence[:TARGET_AT]],
                 number[outcome])
                for pair in chosen for sentence, _, _, outcome in pair]

    def train(chosen, block, seed, norms=True):
        weights = start(len(words), seed, block)
        data = examples(chosen)

        for _ in range(max(1, UPDATES // len(data))):
            for context, target in data:
                learn(context, target, weights, block, norms)

        return weights

    def score(chosen, weights, block, norms=True):
        right = 0

        for context, target in examples(chosen):
            predicted, *_ = forward(context, weights, block, norms)
            right += (normal if predicted[normal] > predicted[backwards]
                      else backwards) == target

        return right

    def verdict(weights, block, earlier, later, norms=True):
        answers = []

        for first, second in ((earlier, later), (later, earlier)):
            sentence = list(frame)
            sentence[FIRST_AT], sentence[SECOND_AT] = first, second
            context = [number[word] for word in sentence]
            predicted, *_ = forward(context, weights, block, norms)
            answers.append(predicted[normal] > predicted[backwards])

        if answers[0] and not answers[1]:
            return 1

        if answers[1] and not answers[0]:
            return -1

        return 0

    # 1. This file's own backward pass, against finite differences.
    def loss_of(context, target, weights):
        predicted, _ = forward(context, weights, True)

        return -math.log(max(predicted[target], 1e-300))

    probe = [number[word] for word in
             ["the", "plan", "preceded", "the", "review", "which", "was"]]
    fresh = start(len(words), SEEDS[0], True)
    before = copy.deepcopy(fresh)
    held = RATE
    RATE = 1.0
    learn(probe, normal, fresh, True)
    RATE = held
    worst = 0.0
    worst_name = ""

    for name, table in before.items():
        after = fresh[name]
        flat = isinstance(table[0], list)
        places = ([(i, j) for i in range(len(table))
                   for j in range(len(table[i]))] if flat
                  else list(range(len(table))))

        # One cell per group. A wrong gradient is wrong everywhere, and
        # nudging every cell would take minutes rather than a second.
        where = places[len(places) // 3]
        mine = (table[where[0]][where[1]] - after[where[0]][where[1]]
                if flat else table[where] - after[where])

        def at(delta):
            trial = copy.deepcopy(before)

            if flat:
                trial[name][where[0]][where[1]] += delta
            else:
                trial[name][where] += delta

            return loss_of(probe, normal, trial)

        nudged = (at(NUDGE) - at(-NUDGE)) / (2 * NUDGE)
        scale = max(abs(mine), abs(nudged), 1e-12)
        gap = abs(mine - nudged) / scale

        if gap > worst:
            worst, worst_name = gap, name

    if worst > GRADIENT_TOLERANCE:
        fail(f"the {worst_name!r} gradient is {worst:.2e} away from the "
             f"nudged one",
             "the backward pass disagrees with the loss it is supposed to be "
             "differentiating, so something in it is wrong; the layer norm "
             "gain is the usual culprit, because updating it inside the loop "
             "over positions corrupts every position after the first")

    # 2. The cost.
    bare = parameters(start(len(words), SEEDS[0], False))
    whole = parameters(start(len(words), SEEDS[0], True))
    bare_work = multiplies(TARGET_AT, len(words), False)
    whole_work = multiplies(TARGET_AT, len(words), True)

    if whole <= bare or whole_work <= bare_work:
        fail(f"the block has {whole} parameters and {whole_work} multiplies "
             f"against the head's {bare} and {bare_work}",
             "the lesson's point is that the block costs more and buys "
             "nothing here, so if it stopped costing more the arithmetic is "
             "wrong")

    # 3. Every configuration, retrained.
    runs = (("the nine neighbouring pairs",
             [pair for pair in pairs if gap_of(pair) == 1][:9]),
            ("the nine widest pairs",
             [pair for pair in pairs if gap_of(pair) >= 3][:9]))
    expected = {}
    separated = {}

    for name, chosen in runs:
        rest = [pair for pair in pairs if pair not in chosen]

        for label, block in (("bare head", False), ("full block", True)):
            fits, helds, splits = [], [], []

            for seed in SEEDS:
                model = train(chosen, block, seed)
                fits.append(score(chosen, model, block))
                helds.append(score(rest, model, block))
                verdicts = {pair: verdict(model, block, *pair)
                            for pair in every}
                splits.append(len([pair for pair in every if verdicts[pair]]))

            expected[f"{label}, {name}"] = ("/".join(map(str, fits)),
                                            "/".join(map(str, helds)),
                                            "/".join(map(str, splits)))
            separated[(name, label)] = splits

    widest = runs[1][1]
    rest = [pair for pair in pairs if pair not in widest]
    fits, helds, splits = [], [], []

    for seed in SEEDS:
        model = train(widest, True, seed, False)
        fits.append(score(widest, model, True, False))
        helds.append(score(rest, model, True, False))
        verdicts = {pair: verdict(model, True, *pair, norms=False)
                    for pair in every}
        splits.append(len([pair for pair in every if verdicts[pair]]))

    expected["block with no layer norms, the nine widest pairs"] = (
        "/".join(map(str, fits)), "/".join(map(str, helds)),
        "/".join(map(str, splits)))

    adjacent, widest_name = runs[0][0], runs[1][0]
    separated[(widest_name, "block, no layer norms")] = splits
    head_on_adjacent = separated[(adjacent, "bare head")]

    if max(head_on_adjacent) > 0:
        fail(f"on the adjacent split the bare head separates "
             f"{'/'.join(map(str, head_on_adjacent))} of {len(every)} pairs",
             "lesson 4's finding was that adjacent pairs teach it no order, "
             "and this lesson rests on it")

    comparisons = (("head against block on the adjacent pairs",
                    (adjacent, "bare head"), (adjacent, "full block")),
                   ("head against block on the widest pairs",
                    (widest_name, "bare head"), (widest_name, "full block")),
                   ("the block against the block with no layer norms",
                    (widest_name, "full block"),
                    (widest_name, "block, no layer norms")))
    biggest = 0.0

    for label, left, right in comparisons:
        first, second = separated[left], separated[right]
        gap = abs(sum(first) / len(first) - sum(second) / len(second))
        spread = max(max(first) - min(first), max(second) - min(second))
        biggest = max(biggest, gap)

        if GAP_MAY_NOT_EXCEED_SPREAD and gap > spread:
            fail(f"{label}: the gap between the averages is {gap:.1f} and the "
                 f"spread within a row is only {spread}",
                 "that would be a real architectural difference rather than "
                 "seed noise, which is the opposite of what this lesson "
                 "reports; measure it over more seeds and rewrite the lesson "
                 "rather than relaxing this")

    # 4. What the parts are for, at depth.
    deep = DEPTHS[-1]
    norm_only = [depth_stack(deep, seed, False, True) for seed in DEPTH_SEEDS]
    both = [depth_stack(deep, seed, True, True) for seed in DEPTH_SEEDS]
    residual_only = [depth_stack(deep, seed, True, False)
                     for seed in DEPTH_SEEDS]
    kept = typical([g for g, _ in both]) / typical([g for g, _ in norm_only])
    calmed = (typical([a for _, a in residual_only])
              / typical([a for _, a in both]))

    if kept < RESIDUAL_WORTH_AT_LEAST:
        fail(f"at {deep} layers the residual is worth {kept:.1f} times the "
             f"gradient, not the large factor the lesson reports",
             "this is the one measurement in the lesson where the block's "
             "parts earn their place, so if it stopped holding there would "
             "be nothing supporting the closing argument")

    if calmed <= 1.0:
        fail(f"at {deep} layers the layer norm leaves the stream "
             f"{calmed:.2f} times smaller, so it is no longer holding it down",
             "without a layer norm every layer adds to the stream and its "
             "size compounds, which is what the measurement is for")

    # 5. Now compare what you reported.
    if not MEASURED.exists():
        fail("there is no .work/measured.tsv",
             "report each configuration, with the three seeds separated by "
             "slashes")

    lines = [line for line in MEASURED.read_text(encoding="utf-8").splitlines()
             if line.strip()]

    if lines and lines[0].split("\t")[:1] == ["what"]:
        lines = lines[1:]

    yours = {}

    for index, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 4:
            fail(f"line {index} has {len(parts)} columns, and needs 4",
                 "the name, then the three seeds for the half it trained on, "
                 "the half held back, and the pairs it separated")

        yours[parts[0]] = tuple(parts[1:4])

    for name, numbers in expected.items():
        if name not in yours:
            fail(f"there is no row for {name!r}",
                 f"report all {len(expected)} of them")

        if yours[name] != numbers:
            fail(f"for {name!r} you report {yours[name]} and running it gives "
                 f"{numbers}",
                 "the seeds are fixed, so a different number means the model "
                 "differs rather than the luck")

    print(f"PASS  gradients all agree inside 1 part in "
          f"{1 / GRADIENT_TOLERANCE:.0e}, the block costs "
          f"{whole / bare:.2f} times the parameters and "
          f"{whole_work / bare_work:.2f} times the work, every architecture "
          f"gap stays inside the seed spread with the largest at "
          f"{biggest:.1f}, and at {deep} layers the residual is worth "
          f"{kept:.0f} times the gradient while the layer norm holds the "
          f"stream {calmed:.0f} times smaller")


if __name__ == "__main__":
    main()
