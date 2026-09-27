"""
Phase 4, lesson 3: the check.

Sampling means your sentences will not be the same as anyone else's, so this
does not compare text. It checks two things that must hold however you drew
the words:

  the greedy sentence, which involves no randomness at all, is exact
  every pair of adjacent words in every sentence really was seen in the corpus

The second is the important one. It is the difference between text generated
by the model and text that came from somewhere else.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
SENTENCES = HERE / ".work" / "sentences.tsv"

START = "<s>"
END = "</s>"
LONGEST = 18

NEEDED = 6


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def count_pairs():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

    following = defaultdict(Counter)

    for sentence in sentences:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1

    return following


def greedily(following):
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


def main() -> None:
    if not SENTENCES.exists():
        fail(
            "there is no .work/sentences.tsv",
            "write the sentences you generated, with how each was produced",
        )

    lines = SENTENCES.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["method"]:
        lines = lines[1:]

    produced = []
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is how it was produced, a tab, and the sentence",
            )

        produced.append((parts[0].strip(), parts[1].strip()))

    if len(produced) < NEEDED:
        fail(
            f"only {len(produced)} sentences were written",
            f"generate at least {NEEDED}: one greedy and several sampled",
        )

    following = count_pairs()

    greedy = [sentence for method, sentence in produced if method == "greedy"]

    if not greedy:
        fail(
            "none of the rows is marked greedy",
            "include the sentence produced by always taking the likeliest word",
        )

    expected = " ".join(greedily(following))

    if greedy[0] != expected:
        fail(
            f"the greedy sentence is {greedy[0]!r}, and it should be "
            f"{expected!r}",
            "greedy involves no randomness: take the commonest next word every "
            "time, breaking ties alphabetically, and stop at the end marker",
        )

    for method, sentence in produced:
        words = sentence.split()

        if not words:
            continue

        for word, next_word in zip([START] + words, words):
            if following.get(word, {}).get(next_word, 0) == 0:
                fail(
                    f"in the {method} sentence, {next_word!r} never follows "
                    f"{word!r} anywhere in the corpus",
                    "every word has to be drawn from what the model saw "
                    "following the word before it",
                )

    sampled = [sentence for method, sentence in produced if method != "greedy"]
    lengths = [len(sentence.split()) for sentence in sampled]

    if len(set(sampled)) < 2:
        fail(
            "every sampled sentence is identical",
            "draw in proportion to the counts rather than taking the "
            "likeliest word each time",
        )

    print(f"PASS  greedy exact, {len(sampled)} sampled sentences, "
          f"{min(lengths)} to {max(lengths)} words, every pair real")


if __name__ == "__main__":
    main()
