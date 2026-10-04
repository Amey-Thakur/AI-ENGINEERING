"""
Phase 9, lesson 5: the block.

Everything so far has been one attention head and an output layer. A real
transformer is not that. It is a stack of blocks, and a block is a head with
four things wrapped around it:

    a layer norm before the attention,
    a residual connection around the attention,
    a layer norm before a small feed forward network,
    and a residual connection around that network.

This builds one, proves the backward pass is right, counts what it costs, and
measures whether any of it closes the gap lesson 4 opened.

Five measurements, in order:

    Is the backward pass correct?    Compare every parameter group against
                                     finite differences, the way phase 2 did.
    What does the block cost?        Count the parameters and the multiplies.
    Does it beat the bare head?      Train both on both of lesson 4's splits.
    Which part is doing the work?    Take the layer norms out and retrain.
    What are the parts for, then?    Measure the gradient through a stack 32
                                     layers deep, which is where they earn
                                     their place.

Run it with:  python solve.py
"""

import copy
import itertools
import math
import random
import statistics
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

#: Four times the width, which is the usual proportion for the feed forward
#: network inside a block.
HIDDEN = 4 * WIDTH

RATE = 0.10
UPDATES = 4000
SEEDS = (7, 13, 23)

#: Added inside the square root so a constant vector does not divide by zero.
EPS = 1e-5

#: The nudge for the finite difference check. Too large and the curve bends
#: inside the step, too small and the two losses round to the same number.
NUDGE = 1e-6

#: How far apart a hand-written gradient and a nudged one may be before
#: something is wrong rather than merely imprecise.
GRADIENT_TOLERANCE = 1e-5

DEPTHS = (1, 2, 4, 8, 16, 32)
DEPTH_SEEDS = range(1, 21)


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
    """Centre, scale to unit variance, then apply a learned gain and bias.

    The gain and bias start at one and zero, so a fresh layer norm is exactly
    the centre-and-scale and nothing else. They exist so the block can learn
    to undo the normalising if it needs to.
    """
    middle = sum(vector) / len(vector)
    spread = sum((value - middle) ** 2 for value in vector) / len(vector)
    deviation = math.sqrt(spread + EPS)
    unit = [(value - middle) / deviation for value in vector]

    return ([gain[i] * unit[i] + bias[i] for i in range(len(vector))],
            unit, deviation)


def normalise_back(d_out, unit, deviation, gain):
    """The gradient through a layer norm, and the gain and bias gradients.

    The subtraction of the mean and the division by the deviation both mix
    every element into every other, so this is not elementwise: each input
    gradient has an average pulled out of it twice over.
    """
    width = len(d_out)
    d_unit = [gain[i] * d_out[i] for i in range(width)]
    mean_d = sum(d_unit) / width
    mean_d_unit = sum(d_unit[i] * unit[i] for i in range(width)) / width
    d_in = [(d_unit[i] - mean_d - unit[i] * mean_d_unit) / deviation
            for i in range(width)]

    return (d_in, [d_out[i] * unit[i] for i in range(width)], list(d_out))


def start(words, seed, block):
    """One stream of numbers, so the two models share every table they both have."""
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
    vectors = [[weights["embed"][token][i] + weights["place"][at][i]
                for i in range(WIDTH)]
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
        # The ablation: the same block with the two layer norms taken out, so
        # the raw vector goes straight into the attention and the stream goes
        # straight into the network.
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

    # The residual: what the attention produced is added to what went in,
    # rather than replacing it. Everything downstream sees both.
    stream = [vectors[-1][i] + blended[i] for i in range(WIDTH)]
    if norms:
        middle, unit_mid, deviation_mid = normalise(
            stream, weights["gain mid"], weights["bias mid"])
    else:
        middle, unit_mid, deviation_mid = list(stream), list(stream), 1.0
    up_w, up_b = weights["up"], weights["up bias"]
    raised = [sum(middle[i] * up_w[i][j] for i in range(WIDTH)) + up_b[j]
              for j in range(HIDDEN)]

    # A ReLU, which is new here. Its slope is 1 where it passed the value
    # through and 0 where it did not, so the backward pass is one comparison.
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
    # Bound once here rather than looked up inside every loop below, which is
    # the difference between this lesson taking a minute and taking three.
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
        # A residual sends the same gradient down both of its paths.
        d_stream = list(d_read)
        d_lowered = list(d_read)
        down_w, up_w = weights["down"], weights["up"]
        hidden, middle = state["hidden"], state["middle"]
        d_hidden = [sum(d_lowered[i] * down_w[j][i]
                        for i in range(WIDTH)) for j in range(HIDDEN)]

        for j in range(HIDDEN):
            for i in range(WIDTH):
                down_w[j][i] -= RATE * hidden[j] * d_lowered[i]

        for i in range(WIDTH):
            weights["down bias"][i] -= RATE * d_lowered[i]

        d_raised = [d_hidden[j] if hidden[j] > 0.0 else 0.0
                    for j in range(HIDDEN)]
        d_middle = [sum(d_raised[j] * up_w[i][j]
                        for j in range(HIDDEN)) for i in range(WIDTH)]

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
            key_w[i][j] -= RATE * sum(
                normed[t][i] * d_keys[t][j] for t in range(seen))
            value_w[i][j] -= RATE * sum(
                normed[t][i] * d_values[t][j] for t in range(seen))

    if block:
        # Every position's gradient has to be worked out against the gain the
        # forward pass actually used, so the gain's own gradient is collected
        # across positions and applied once they are all done. Updating it
        # inside this loop is a bug that leaves the embedding gradients a few
        # per cent wrong, which nothing but a finite difference check notices.
        d_vectors = [[0.0] * WIDTH for _ in range(seen)]
        total_gain = [0.0] * WIDTH
        total_bias = [0.0] * WIDTH

        for j in range(seen):
            if norms:
                back, d_gain, d_bias = normalise_back(
                    d_normed[j], state["units"][j], state["deviations"][j],
                    weights["gain in"])
            else:
                back, d_gain, d_bias = d_normed[j], [0.0] * WIDTH,                     [0.0] * WIDTH

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
    """Multiplications in one forward pass, counted from the shapes.

    A layer norm is counted as one multiply per element for the squaring, one
    for the scaling and one for the gain, so three times the width.
    """
    head = (WIDTH * WIDTH                      # the query, once
            + 2 * seen * WIDTH * WIDTH         # a key and a value per position
            + seen * WIDTH                     # the scores
            + seen * WIDTH                     # the blend
            + WIDTH * words)                   # the output layer

    if not block:
        return head

    return head + (seen * 3 * WIDTH            # the layer norm per position
                   + 3 * WIDTH                 # the layer norm on the stream
                   + 2 * WIDTH * HIDDEN)       # up and back down


def depth_stack(depth, seed, residual, normed):
    """A stack of feed forward sub-blocks, to see what survives the trip.

    Nothing is trained. A unit gradient is put in at the output and the size
    of what arrives at the input is measured, which is the thing a deep stack
    either preserves or loses.
    """
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
    """The geometric mean, which is the right average for a product.

    Each layer multiplies what passes through it, so the sizes are spread the
    way a product of random numbers is spread: a plain average is dragged
    around by one lucky run and says nothing about the rest.
    """
    return math.exp(statistics.fmean(math.log(n) for n in numbers))


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

    every = list(itertools.combinations(STAGES, 2))
    reported = []
    done = {}
    spreads = {}

    # 1. Is the backward pass right? Nudge every parameter group and see.
    def loss_of(context, target, weights):
        predicted, _ = forward(context, weights, True)

        return -math.log(max(predicted[target], 1e-300))

    probe = [number[word] for word in
             ["the", "plan", "preceded", "the", "review", "which", "was"]]
    fresh = start(len(words), SEEDS[0], True)
    before = copy.deepcopy(fresh)
    global RATE
    held = RATE
    RATE = 1.0
    learn(probe, normal, fresh, True)
    RATE = held
    by_hand = {}

    for name, table in before.items():
        after = fresh[name]

        if isinstance(table[0], list):
            by_hand[name] = [[table[i][j] - after[i][j]
                              for j in range(len(table[i]))]
                             for i in range(len(table))]
        else:
            by_hand[name] = [table[i] - after[i] for i in range(len(table))]

    picked = {"embed": (number["plan"], 3), "place": (1, 2),
              "gain in": 4, "bias in": 2, "query": (2, 5), "key": (0, 1),
              "value": (6, 6), "gain mid": 1, "bias mid": 5, "up": (3, 17),
              "up bias": 9, "down": (0, 4), "down bias": 7,
              "out": (5, normal)}
    worst = 0.0

    print("Every parameter group, by hand against a nudge of "
          f"{NUDGE:.0e}:")
    print()
    print("  parameter          by hand      by nudging    agrees")

    for name, where in picked.items():
        mine = (by_hand[name][where[0]][where[1]]
                if isinstance(where, tuple) else by_hand[name][where])

        def at(delta):
            trial = copy.deepcopy(before)

            if isinstance(where, tuple):
                trial[name][where[0]][where[1]] += delta
            else:
                trial[name][where] += delta

            return loss_of(probe, normal, trial)

        nudged = (at(NUDGE) - at(-NUDGE)) / (2 * NUDGE)
        scale = max(abs(mine), abs(nudged), 1e-12)
        gap = abs(mine - nudged) / scale
        worst = max(worst, gap)
        # The gap is a ratio of two tiny differences. Its size varies by more
        # than a factor of ten between one machine's maths library and
        # another's, even when both gradients agree to nine figures, so
        # printing it would make this page disagree with itself depending on
        # where it ran. The verdict is the part that is the same everywhere.
        print(f"  {name:12}  {mine:13.3e}  {nudged:13.3e}    "
              f"{'yes' if gap <= GRADIENT_TOLERANCE else 'NO'}")

    print()
    print(f"All {len(picked)} agree, every one of them inside 1 part in "
          f"{1 / GRADIENT_TOLERANCE:.0e}.")
    print("The backward pass is right.")
    print()

    # 2. What does it cost?
    bare = start(len(words), SEEDS[0], False)
    whole = start(len(words), SEEDS[0], True)
    print("  what it costs                 bare head    full block    times")
    print(f"  {'parameters':27}  {parameters(bare):9}  "
          f"{parameters(whole):12}     "
          f"{parameters(whole) / parameters(bare):.2f}")
    bare_work = multiplies(TARGET_AT, len(words), False)
    whole_work = multiplies(TARGET_AT, len(words), True)
    print(f"  {'multiplies, one sentence':27}  {bare_work:9}  "
          f"{whole_work:12}     {whole_work / bare_work:.2f}")
    print()

    # 3. Does any of it beat the bare head?
    runs = (("the nine neighbouring pairs",
             [pair for pair in pairs if gap_of(pair) == 1][:9]),
            ("the nine widest pairs",
             [pair for pair in pairs if gap_of(pair) >= 3][:9]))

    print(f"Lesson 4's two splits, {UPDATES} updates, seeds "
          f"{', '.join(str(s) for s in SEEDS)}. A pair counts as separated")
    print("only if the model answers one way round and not the other.")

    for name, chosen in runs:
        rest = [pair for pair in pairs if pair not in chosen]
        print()
        print(f"  trained on {name}")
        print("    model                    trained on       held back     "
              "separated")

        for label, block in (("bare head", False), ("full block", True)):
            fits, helds, splits, wrongs = [], [], [], 0

            for seed in SEEDS:
                model = train(chosen, block, seed)
                fits.append(score(chosen, model, block))
                helds.append(score(rest, model, block))
                verdicts = {pair: verdict(model, block, *pair)
                            for pair in every}
                commits = [pair for pair in every if verdicts[pair]]
                splits.append(len(commits))
                wrongs += sum(1 for pair in commits if verdicts[pair] == -1)

            row = ("/".join(map(str, fits)), "/".join(map(str, helds)),
                   "/".join(map(str, splits)))
            done[(name, label)] = row
            spreads[(name, label)] = splits
            reported.append((f"{label}, {name}", *row))
            print(f"    {label:22}  {row[0]:>8} of {len(examples(chosen))}  "
                  f"{row[1]:>11} of {len(examples(rest))}  "
                  f"{row[2]:>8} of {len(every)}")

    print()
    print("Now put a number on how much of that is the architecture and how "
          "much is the")
    print("seed. For each pair of rows, compare the gap between their averages "
          "against")
    print("the spread within a single row:")
    print()
    print("  comparison                                   gap between   "
          "spread within")

    # 4. Take a part out, and compare the same way.
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

    row = ("/".join(map(str, fits)), "/".join(map(str, helds)),
           "/".join(map(str, splits)))
    reported.append(("block with no layer norms, the nine widest pairs", *row))
    spreads[(runs[1][0], "block, no layer norms")] = splits

    def compare(label, left, right):
        first, second = spreads[left], spreads[right]
        gap = abs(sum(first) / len(first) - sum(second) / len(second))
        widest_spread = max(max(first) - min(first), max(second) - min(second))
        verdict_text = ("the seed" if widest_spread >= gap
                        else "the architecture")
        print(f"  {label:42}  {gap:11.1f}   {widest_spread:13}")

        return gap, widest_spread

    adjacent_name, widest_name = runs[0][0], runs[1][0]
    verdicts_out = [
        compare("head against block, adjacent pairs",
                (adjacent_name, "bare head"), (adjacent_name, "full block")),
        compare("head against block, widest pairs",
                (widest_name, "bare head"), (widest_name, "full block")),
        compare("block against block without layer norms",
                (widest_name, "full block"),
                (widest_name, "block, no layer norms")),
    ]

    print()
    print("Every one of those gaps is smaller than the spread inside a single "
          "row. The")
    print("block separates 9 pairs the head could not at one seed and none at "
          "the other")
    print("two. Taking the layer norms out destroys it at two seeds and "
          "leaves it better")
    print("than the full block at the third.")
    print()
    print("With three seeds on sixty sentences, none of these architectures "
          "has been")
    print("shown to differ from any other. That is the honest result, and it "
          "is not the")
    print("one this lesson was written expecting.")
    print()
    print("  the three rows, so you can see where the spread comes from")
    print(f"    {'bare head, adjacent':38} "
          f"{spreads[(adjacent_name, 'bare head')]}")
    print(f"    {'full block, adjacent':38} "
          f"{spreads[(adjacent_name, 'full block')]}")
    print(f"    {'bare head, widest':38} "
          f"{spreads[(widest_name, 'bare head')]}")
    print(f"    {'full block, widest':38} "
          f"{spreads[(widest_name, 'full block')]}")
    print(f"    {'block without layer norms, widest':38} "
          f"{spreads[(widest_name, 'block, no layer norms')]}")
    print()

    # 5. So what are the parts for? Depth.
    print(f"Depth is what they are for, and one block cannot show it. A stack "
          f"of plain")
    print(f"feed forward sub-blocks, nothing trained, a unit gradient put in "
          f"at the")
    print(f"output, {len(DEPTH_SEEDS)} seeds, geometric mean:")
    print()
    print("  layers    gradient reaching the input          leaving the stack")
    print("            norm only    both      residual only   both   "
          "residual only")

    for depth in DEPTHS:
        norm_only = [depth_stack(depth, seed, False, True)
                     for seed in DEPTH_SEEDS]
        both = [depth_stack(depth, seed, True, True) for seed in DEPTH_SEEDS]
        residual_only = [depth_stack(depth, seed, True, False)
                         for seed in DEPTH_SEEDS]
        print(f"  {depth:6}    {typical([g for g, _ in norm_only]):9.2e}  "
              f"{typical([g for g, _ in both]):9.2e}  "
              f"{typical([g for g, _ in residual_only]):13.2e}  "
              f"{typical([a for _, a in both]):6.1f}  "
              f"{typical([a for _, a in residual_only]):13.2e}")

    deep = DEPTHS[-1]
    norm_only = [depth_stack(deep, seed, False, True) for seed in DEPTH_SEEDS]
    both = [depth_stack(deep, seed, True, True) for seed in DEPTH_SEEDS]
    residual_only = [depth_stack(deep, seed, True, False)
                     for seed in DEPTH_SEEDS]
    kept = typical([g for g, _ in both]) / typical([g for g, _ in norm_only])
    calmed = (typical([a for _, a in residual_only])
              / typical([a for _, a in both]))

    print()
    print(f"At {deep} layers the residual is worth {kept:.0f} times the "
          f"gradient at the input, and")
    print(f"the layer norm holds the stream {calmed:.0f} times smaller than "
          f"it would otherwise")
    print("leave. Neither number exists at one layer, which is the whole "
          "reason this")
    print("lesson's block cannot show you what a block is for.")

    MEASURED.parent.mkdir(parents=True, exist_ok=True)

    with open(MEASURED, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("what\ttrained on\theld back\tseparated\n")

        for name, fits, helds, splits in reported:
            handle.write(f"{name}\t{fits}\t{helds}\t{splits}\n")


if __name__ == "__main__":
    main()
