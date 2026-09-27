"""
Phase 4, lesson 2: never say never.

Measures a language model properly, discovers the measurement is infinite,
and then fixes the model two ways and compares them.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import exp, inf, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
RESULTS = HERE / ".work" / "results.tsv"

TRAIN_SENTENCES = 180
START = "<s>"
END = "</s>"

ADDED = (1.0, 0.1, 0.01)
MIXTURES = (0.0, 0.5, 0.8, 0.9)


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def counts(sentences):
    following = defaultdict(Counter)
    context = Counter()
    single = Counter()
    total = 0

    for sentence in sentences:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1
            context[word] += 1
            single[next_word] += 1
            total += 1

    return following, context, single, total


def perplexity(held_back, probability):
    """How surprised the model is, per word, on text it did not see.

    The average log probability, negated and exponentiated. Read it as: the
    model is as uncertain as if it were choosing uniformly between this many
    words at every step. Lower is better, and 1 would be a model that is never
    surprised by anything.
    """
    carried = 0.0
    counted = 0

    for sentence in held_back:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            chance = probability(word, next_word)

            # One impossible word makes the whole thing impossible, which is
            # exactly what the arithmetic should say.
            if chance <= 0:
                return inf

            carried += log(chance)
            counted += 1

    return exp(-carried / counted)


def main() -> None:
    sentences = read_corpus()
    training, held_back = sentences[:TRAIN_SENTENCES], sentences[TRAIN_SENTENCES:]

    following, context, single, total = counts(training)
    vocabulary = len({word for sentence in sentences for word in sentence}) + 2

    def raw(word, next_word):
        if not context.get(word):
            return 0.0
        return following.get(word, {}).get(next_word, 0) / context[word]

    def added(amount):
        def probability(word, next_word):
            seen = following.get(word, {}).get(next_word, 0)
            return (seen + amount) / (context.get(word, 0) + amount * vocabulary)

        return probability

    def mixed(weight):
        def probability(word, next_word):
            bigram = raw(word, next_word)
            unigram = (single.get(next_word, 0) + 1) / (total + vocabulary)
            return weight * bigram + (1 - weight) * unigram

        return probability

    measured = [("none", perplexity(held_back, raw))]

    for amount in ADDED:
        measured.append((f"add {amount:g}", perplexity(held_back, added(amount))))

    for weight in MIXTURES:
        measured.append((f"mix {weight:g}", perplexity(held_back, mixed(weight))))

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("model\tperplexity\n")

        for name, value in measured:
            written = "inf" if value == inf else f"{value:.4f}"
            handle.write(f"{name}\t{written}\n")

    print(f"{vocabulary} words in the vocabulary, counting both markers")
    print(f"A model choosing uniformly would score {vocabulary}.")
    print()
    print("  model                       perplexity")

    for name, value in measured:
        shown = "infinite" if value == inf else f"{value:8.1f}"
        note = ""

        if name == "none":
            note = "   some real sentences are impossible"
        elif name == "mix 0":
            note = "   ignores the previous word entirely"

        print(f"  {name:24} {shown}{note}")

    best = min((value, name) for name, value in measured if value != inf)
    print()
    print(f"Best: {best[1]}, at {best[0]:.1f}")


if __name__ == "__main__":
    main()
