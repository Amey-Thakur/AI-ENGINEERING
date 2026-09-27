"""
Phase 4, lesson 3: making it talk.

Generates sentences from the counts, three ways: always taking the likeliest
word, drawing at random in proportion to the counts, and with a dial between
those two.

The output is the argument. Read it rather than the explanation.

Run it with:  python solve.py
"""

import random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
SENTENCES = HERE / ".work" / "sentences.tsv"

START = "<s>"
END = "</s>"

LONGEST = 18
HOW_MANY = 5
SEED = 11

TEMPERATURES = (0.4, 1.0, 1.6)


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def count_pairs(sentences):
    following = defaultdict(Counter)

    for sentence in sentences:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1

    return following


def greedily(following):
    """Always take the likeliest next word."""
    word = START
    produced = []

    for _ in range(LONGEST):
        if word not in following:
            break

        word = min(following[word].items(),
                   key=lambda pair: (-pair[1], pair[0]))[0]

        if word == END:
            break

        produced.append(word)

    return produced


def sampled(following, generator, temperature):
    """Draw the next word at random, in proportion to the counts.

    Temperature reshapes those proportions before drawing. Below 1 it sharpens
    them, so likely words become even likelier. Above 1 it flattens them, so
    unlikely words get a real chance. At exactly 1 the counts are used as they
    are.
    """
    word = START
    produced = []

    for _ in range(LONGEST):
        if word not in following:
            break

        choices = sorted(following[word])
        weights = [following[word][choice] ** (1.0 / temperature)
                   for choice in choices]

        word = generator.choices(choices, weights=weights)[0]

        if word == END:
            break

        produced.append(word)

    return produced


def main() -> None:
    following = count_pairs(read_corpus())
    generator = random.Random(SEED)

    SENTENCES.parent.mkdir(parents=True, exist_ok=True)
    written = []

    straight = greedily(following)
    written.append(("greedy", " ".join(straight)))

    for temperature in TEMPERATURES:
        for _ in range(HOW_MANY):
            produced = sampled(following, generator, temperature)
            written.append((f"temperature {temperature:g}", " ".join(produced)))

    with open(SENTENCES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("method\tsentence\n")

        for method, sentence in written:
            handle.write(f"{method}\t{sentence}\n")

    print("Always taking the likeliest word:")
    print(f"  {' '.join(straight)}")
    print()

    for temperature in TEMPERATURES:
        note = {
            0.4: "sharpened: the model plays safe",
            1.0: "the counts as they are",
            1.6: "flattened: rare words get a real chance",
        }[temperature]

        print(f"Temperature {temperature:g}, {note}:")

        for method, sentence in written:
            if method == f"temperature {temperature:g}":
                print(f"  {sentence}")

        print()

    lengths = [len(sentence.split()) for method, sentence in written
               if method != "greedy"]

    print(f"Sentences produced: {len(lengths)}")
    print(f"Shortest {min(lengths)} words, longest {max(lengths)}, "
          f"average {sum(lengths) / len(lengths):.1f}")


if __name__ == "__main__":
    main()
