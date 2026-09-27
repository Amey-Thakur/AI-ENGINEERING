"""
Phase 4, lesson 1: predicting the next word.

Counts which word follows which, then uses those counts to guess what comes
next, and measures how often it is right on sentences it has never seen.

This is a language model. Not a simplified stand-in for one: predicting the
next token from the ones before it is exactly what the large models do, and
the difference is how the prediction is computed, not what is being predicted.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
RESULTS = HERE / ".work" / "results.tsv"

# Sentences are split by position rather than shuffled, so everyone gets the
# same split without needing a seed.
TRAIN_SENTENCES = 180

START = "<s>"
END = "</s>"

PROBES = ("the", "server", "we", "customer", START)
SHOW = 4


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def as_tokens(sentence):
    """A sentence with markers, so the model can learn how one starts and ends."""
    return [START] + sentence + [END]


def count_pairs(sentences):
    """For each word, how often each other word follows it."""
    following = defaultdict(Counter)

    for sentence in sentences:
        tokens = as_tokens(sentence)

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1

    return following


def guess(word, following):
    """The commonest word seen after this one, or nothing if it is unknown."""
    if word not in following:
        return None

    # Sorted by count, then alphabetically, so a tie does not depend on the
    # order the dictionary happens to hold things in.
    return min(following[word].items(), key=lambda pair: (-pair[1], pair[0]))[0]


def main() -> None:
    sentences = read_corpus()
    training = sentences[:TRAIN_SENTENCES]
    held_back = sentences[TRAIN_SENTENCES:]

    following = count_pairs(training)

    right = 0
    total = 0
    unknown_context = 0
    never_seen_pair = 0

    for sentence in held_back:
        tokens = as_tokens(sentence)

        for word, next_word in zip(tokens, tokens[1:]):
            total += 1

            if word not in following:
                unknown_context += 1
            elif guess(word, following) == next_word:
                right += 1

            # .get rather than following[word], because reading a missing key
            # from a defaultdict creates it, which would quietly add empty
            # contexts to the model while measuring it.
            if following.get(word, {}).get(next_word, 0) == 0:
                never_seen_pair += 1

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("measure\tvalue\n")
        handle.write(f"predictions\t{total}\n")
        handle.write(f"correct\t{right}\n")
        handle.write(f"unknown_context\t{unknown_context}\n")
        handle.write(f"never_seen_pair\t{never_seen_pair}\n")

    vocabulary = {word for sentence in sentences for word in sentence}

    print(f"{len(training)} sentences to learn from, {len(held_back)} held back")
    print(f"{len(vocabulary)} different words, {len(following)} of them with "
          f"something known to follow")
    print()
    print("What it expects next:")
    print()

    for probe in PROBES:
        if probe not in following:
            continue

        ranked = sorted(following[probe].items(),
                        key=lambda pair: (-pair[1], pair[0]))[:SHOW]
        listed = ", ".join(f"{word} ({count})" for word, count in ranked)
        shown = "at the start of a sentence" if probe == START else f"after {probe!r}"
        print(f"  {shown:30} {listed}")

    print()
    print(f"Guessing the next word on held back sentences:")
    print(f"  right          {right} of {total}   {right / total:.1%}")
    print(f"  context never seen in training   {unknown_context}")
    print(f"  pair never seen in training      {never_seen_pair} of {total}"
          f"   {never_seen_pair / total:.0%}")


if __name__ == "__main__":
    main()
