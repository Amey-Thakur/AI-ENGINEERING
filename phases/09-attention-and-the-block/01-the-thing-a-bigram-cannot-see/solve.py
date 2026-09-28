"""
Phase 9, lesson 1: the thing a bigram cannot see.

Sixty sentences, each one of a pair. The only difference inside a pair is
whether the subject is singular or plural, and the word that has to agree with
it sits five words later.

    the server  that the engineer restarted was  slow
    the servers that the engineer restarted were slow

Phase 4's model predicts the next word from the one before it. The word before
the target is `restarted` in both sentences, so whatever it predicts there, it
predicts for both.

This does not measure a badly trained model. It trains the bigram on all sixty
sentences, including the ones it is then scored on, and measures the best it
could possibly do.

Run it with:  python solve.py
"""

from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE / "agreement.tsv"
CEILING = HERE / ".work" / "ceiling.tsv"

#: Where the corpus puts the two words that matter.
SUBJECT_AT = 1
TARGET_AT = 6


def read_sentences():
    rows = []

    with open(SENTENCES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")

            if line:
                sentence, subject, target = line.split("\t")
                rows.append((sentence.split(), subject, target))

    return rows


def main() -> None:
    rows = read_sentences()
    words = sorted({word for sentence, _, _ in rows for word in sentence})

    # A bigram, counted from every sentence. Nothing is held back, on purpose.
    following = defaultdict(lambda: defaultdict(int))

    for sentence, _, _ in rows:
        for before, after in zip(sentence, sentence[1:]):
            following[before][after] += 1

    # What each context that precedes a target is followed by.
    contexts = defaultdict(lambda: defaultdict(int))

    for sentence, _, target in rows:
        contexts[sentence[TARGET_AT - 1]][target] += 1

    right = 0
    ties = 0

    for sentence, _, target in rows:
        before = sentence[TARGET_AT - 1]
        was = following[before].get("was", 0)
        were = following[before].get("were", 0)

        if was == were:
            ties += 1
            # A tie has to break somewhere, and it breaks the same way every
            # time, which is the only honest thing to do with no information.
            guess = "was"
        else:
            guess = "was" if was > were else "were"

        right += guess == target

    CEILING.parent.mkdir(parents=True, exist_ok=True)

    with open(CEILING, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("context\twas\twere\n")

        for before in sorted(contexts):
            handle.write(f"{before}\t{contexts[before]['was']}\t"
                         f"{contexts[before]['were']}\n")

    print(f"{len(rows)} sentences, {len(words)} words, "
          f"{len(rows) // 2} pairs that differ by one letter.")
    print()
    print("A pair, in full:")
    print(f"  {' '.join(rows[0][0])}")
    print(f"  {' '.join(rows[1][0])}")
    print()
    print(f"The target sits at position {TARGET_AT}. The word before it is "
          f"{rows[0][0][TARGET_AT - 1]!r} in both.")
    print()

    print("Every word that precedes a target, and what follows it:")
    print()
    print("  context      was   were")

    for before in sorted(contexts):
        print(f"  {before:11} {contexts[before]['was']:4} "
              f"{contexts[before]['were']:6}")

    balanced = all(counts["was"] == counts["were"]
                   for counts in contexts.values())

    print()
    print(f"Every context is balanced between the two: {balanced}")
    print()
    print(f"So the bigram, trained on all {len(rows)} sentences and then "
          f"scored on them,")
    print(f"answers {right} of {len(rows)}. All {ties} were ties, and a tie "
          f"broken the same way")
    print("every time is right for exactly half of them.")
    print()
    print("That is not a training score. It is the ceiling. No amount of data "
          "of this shape,")
    print("and no smoothing, moves it, because the information the answer "
          "needs is five words")
    print("away and the model cannot see that far by construction.")


if __name__ == "__main__":
    main()
