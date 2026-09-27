"""
Phase 4, lesson 1: the check.

It counts the pairs itself and works out the same four numbers, then compares.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
RESULTS = HERE / ".work" / "results.tsv"

TRAIN_SENTENCES = 180
START = "<s>"
END = "</s>"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def measure():
    with open(CORPUS, encoding="utf-8") as handle:
        sentences = [line.split() for line in handle if line.strip()]

    following = defaultdict(Counter)

    for sentence in sentences[:TRAIN_SENTENCES]:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1

    right = total = unknown = never = 0

    for sentence in sentences[TRAIN_SENTENCES:]:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            total += 1

            if word not in following:
                unknown += 1
            else:
                best = min(following[word].items(),
                           key=lambda pair: (-pair[1], pair[0]))[0]
                right += best == next_word

            if following.get(word, {}).get(next_word, 0) == 0:
                never += 1

    return {
        "predictions": total,
        "correct": right,
        "unknown_context": unknown,
        "never_seen_pair": never,
    }


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report how many predictions were made, how many were right, how "
            "many contexts were unknown, and how many pairs had never been seen",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["measure"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is the name of a measure and a whole number",
            )

        try:
            yours[parts[0].strip()] = int(float(parts[1]))
        except ValueError:
            fail(
                f"line {number} has a value that is not a number: {parts[1]!r}",
                "every measure here is a count",
            )

    expected = measure()

    for name, want in expected.items():
        if name not in yours:
            fail(
                f"there is no row for {name}",
                "report all four measures",
            )

        if yours[name] != want:
            extra = ""

            if name == "never_seen_pair" and yours[name] < want:
                extra = (". Reading a missing key from a defaultdict creates "
                         "it, so counting this way can quietly change the model")

            fail(
                f"{name} is reported as {yours[name]}, and counting gives {want}"
                f"{extra}",
                f"train on the first {TRAIN_SENTENCES} sentences, add {START} "
                f"and {END} markers, and score every pair in the rest",
            )

    accuracy = expected["correct"] / expected["predictions"]
    print(f"PASS  {expected['correct']} of {expected['predictions']} next words "
          f"right, {accuracy:.1%}, and all four counts match")


if __name__ == "__main__":
    main()
