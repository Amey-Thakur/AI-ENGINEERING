"""
Phase 5, lesson 2: the check.

It runs the simplest search itself and compares your scores with what it
measures, then insists the result is far better than the model managed in
lesson 1.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"

TOP = 3

# Lesson 1's model managed none. Anything calling itself search has to be far
# past that, or it is not doing anything.
LEAST_FIRST = 10


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def measure():
    sentences = [line.strip()
                 for line in CORPUS.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    documents = [sentence.split() for sentence in sentences]

    asked = []
    for line in QUESTIONS.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            asked.append(tuple(line.rstrip("\n").split("\t")))

    first = within = 0

    for question, answer in asked:
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        order = [sentences[index] for _, index in ranked]

        first += order[0] == answer
        within += answer in order[:TOP]

    return first, within, len(asked)


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "for each way of scoring a match, report how often the right "
            "sentence came first and how often it was in the top three",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["method"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 3:
            fail(
                f"line {number} has {len(parts)} columns, and needs at least 3",
                "each row is the method, how many came first, and how many "
                "were in the top three",
            )

        try:
            yours[parts[0].strip()] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "both columns after the method name are counts",
            )

    if not yours:
        fail("results.tsv has no methods in it", "report at least one method")

    first, within, asked = measure()

    simplest = [name for name in yours
                if "shared" in name.lower() and "length" not in name.lower()]

    if not simplest:
        fail(
            "there is no row for the simplest method",
            "include the one that just counts how many words the question and "
            "the sentence share, named so it can be recognised",
        )

    reported_first, reported_within = yours[simplest[0]]

    if (reported_first, reported_within) != (first, within):
        fail(
            f"for {simplest[0]!r} you report {reported_first} first and "
            f"{reported_within} in the top three, and measuring gives "
            f"{first} and {within}",
            "count the words the question and the sentence have in common, "
            "break ties by the order sentences appear in the file",
        )

    best = max(count for count, _ in yours.values())

    if best < LEAST_FIRST:
        fail(
            f"the best method gets only {best} of {asked} right first",
            "search should be far better than the model was in lesson 1, "
            "so something is wrong with the matching",
        )

    print(f"PASS  simplest search puts {first} of {asked} right first, "
          f"{within} in the top {TOP}, against 0 for the model")


if __name__ == "__main__":
    main()
