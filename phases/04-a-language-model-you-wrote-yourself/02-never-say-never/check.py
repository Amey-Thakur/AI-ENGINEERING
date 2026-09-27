"""
Phase 4, lesson 2: the check.

It measures every model itself and compares with what you reported, including
that the unsmoothed one comes out infinite.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from math import exp, inf, isinf, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
RESULTS = HERE / ".work" / "results.tsv"

TRAIN_SENTENCES = 180
START = "<s>"
END = "</s>"

ADDED = (1.0, 0.1, 0.01)
MIXTURES = (0.0, 0.5, 0.8, 0.9)

# Perplexities run into the hundreds, so a relative tolerance is the sane test.
RELATIVE = 0.01


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def measure():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

    training, held_back = sentences[:TRAIN_SENTENCES], sentences[TRAIN_SENTENCES:]

    following = defaultdict(Counter)
    context = Counter()
    single = Counter()
    total = 0

    for sentence in training:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1
            context[word] += 1
            single[next_word] += 1
            total += 1

    vocabulary = len({word for sentence in sentences for word in sentence}) + 2

    def raw(word, next_word):
        if not context.get(word):
            return 0.0
        return following.get(word, {}).get(next_word, 0) / context[word]

    def perplexity(probability):
        carried = 0.0
        counted = 0

        for sentence in held_back:
            tokens = [START] + sentence + [END]

            for word, next_word in zip(tokens, tokens[1:]):
                chance = probability(word, next_word)

                if chance <= 0:
                    return inf

                carried += log(chance)
                counted += 1

        return exp(-carried / counted)

    results = {"none": perplexity(raw)}

    for amount in ADDED:
        def added(word, next_word, amount=amount):
            seen = following.get(word, {}).get(next_word, 0)
            return (seen + amount) / (context.get(word, 0) + amount * vocabulary)

        results[f"add {amount:g}"] = perplexity(added)

    for weight in MIXTURES:
        def mixed(word, next_word, weight=weight):
            unigram = (single.get(next_word, 0) + 1) / (total + vocabulary)
            return weight * raw(word, next_word) + (1 - weight) * unigram

        results[f"mix {weight:g}"] = perplexity(mixed)

    return results


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report the perplexity of each model",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["model"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is the model name and its perplexity",
            )

        value = parts[1].strip().lower()

        try:
            yours[parts[0].strip()] = inf if value in ("inf", "infinite") \
                else float(value)
        except ValueError:
            fail(
                f"line {number} has a perplexity that is not a number: "
                f"{parts[1]!r}",
                "write a number, or inf when the model says something real is "
                "impossible",
            )

    expected = measure()

    for name, want in expected.items():
        if name not in yours:
            fail(
                f"there is no row for {name!r}",
                f"report all {len(expected)} models",
            )

        got = yours[name]

        if isinf(want) != isinf(got):
            if isinf(want):
                fail(
                    f"you report {name!r} at {got:g}, and it should be infinite",
                    "a pair the model never saw has probability zero, and one "
                    "zero makes the whole thing impossible",
                )

            fail(
                f"you report {name!r} as infinite, and it should be {want:.1f}",
                "smoothing must leave every word some chance, however small",
            )

        if not isinf(want) and abs(got - want) > want * RELATIVE:
            fail(
                f"you report {name!r} at {got:.1f}, and measuring gives "
                f"{want:.1f}",
                "perplexity is the average log probability per word, negated "
                "and exponentiated, over every pair in the held back sentences",
            )

    best = min((value, name) for name, value in expected.items()
               if not isinf(value))

    print(f"PASS  all {len(expected)} perplexities match, and the best is "
          f"{best[1]!r} at {best[0]:.1f}")


if __name__ == "__main__":
    main()
