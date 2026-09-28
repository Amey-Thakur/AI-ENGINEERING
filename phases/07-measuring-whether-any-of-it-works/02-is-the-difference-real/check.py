"""
Phase 7, lesson 2: the check.

It reruns both agents on all 48 questions, rebuilds both comparisons, and
insists on the shape of the result: that the two outcomes land on opposite
sides of the usual threshold, and that the disagreements account for every
question that is not agreed on.

Run it with:  python check.py
"""

import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
DISAGREEMENTS = HERE / ".work" / "disagreements.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
THRESHOLD = 0.05
TOLERANCE = 0.001


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def make_scorer(sentences):
    documents = [sentence.split() for sentence in sentences]

    def best(question):
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap, index = ranked[0]

        return -overlap, sentences[index]

    return best


def calculate(question):
    words = question.split()

    if len(words) < 4:
        return REFUSED
    if not words[2].isdigit() or not words[-1].isdigit():
        return REFUSED
    if words[3] not in OPERATIONS:
        return REFUSED

    first, last, operation = int(words[2]), int(words[-1]), words[3]

    return {
        "times": str(first * last),
        "plus": str(first + last),
        "minus": str(first - last),
        "divided": str(first // last) if last else "",
    }[operation]


def count(question):
    words = question.split()

    if not words or not words[-1].isalpha():
        return REFUSED

    return str(len(words[-1]))


def route(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def make_agent(best, bar):
    def agent(question):
        picked = route(question)

        if picked != "search":
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found

        overlap, sentence = best(question)

        return sentence if overlap >= bar else REFUSED

    return agent


def behaved_correctly(given, answer, answerable):
    return given == answer if answerable else given is REFUSED


def said_something_false(given, answer, answerable):
    if given is REFUSED:
        return False

    return not (answerable and given == answer)


def coin_flip_chance(wins, losses):
    total = wins + losses

    if total == 0:
        return 1.0

    fewer = min(wins, losses)

    return min(1.0, 2 * sum(comb(total, i)
                            for i in range(0, fewer + 1)) / 2 ** total)


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    best = make_scorer(sentences)

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    confident = make_agent(best, 0)
    cautious = make_agent(best, BAR)

    expected = {}

    for name, measure in (("behaved correctly", behaved_correctly),
                          ("said something false", said_something_false)):
        both = neither = first_only = second_only = 0

        for question, answer, answerable in questions:
            left = measure(confident(question), answer, answerable)
            right = measure(cautious(question), answer, answerable)

            if left and not right:
                first_only += 1
            elif right and not left:
                second_only += 1
            elif left:
                both += 1
            else:
                neither += 1

        expected[name] = (both + first_only, both + second_only, first_only,
                          second_only, coin_flip_chance(first_only,
                                                        second_only),
                          both + neither)

    if not DISAGREEMENTS.exists():
        fail(
            "there is no .work/disagreements.tsv",
            "for each outcome, report both totals, how many questions only "
            "one agent got, and how often chance alone is that lopsided",
        )

    lines = DISAGREEMENTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["outcome"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 6:
            fail(
                f"line {number} has {len(parts)} columns, and needs 6",
                "the outcome, the confident total, the cautious total, how "
                "many only the confident one, how many only the cautious "
                "one, and the chance",
            )

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]), int(parts[3]),
                               int(parts[4]), float(parts[5]))
        except ValueError:
            fail(
                f"line {number} has a value that will not parse",
                "four whole numbers and then the chance as a decimal",
            )

    for name, numbers in expected.items():
        if name not in yours:
            fail(
                f"there is no row for {name!r}",
                f"report both outcomes: {', '.join(expected)}",
            )

        mine = yours[name]

        if mine[:4] != numbers[:4]:
            fail(
                f"for {name!r} you report {mine[:4]} and running it gives "
                f"{numbers[:4]}",
                "a question counts as a disagreement only when one agent "
                "has the outcome and the other does not",
            )

        if abs(mine[4] - numbers[4]) > TOLERANCE:
            fail(
                f"for {name!r} you report a chance of {mine[4]:.4f} and it "
                f"should be {numbers[4]:.4f}",
                "with the disagreements as coin flips, add up the chance of "
                "a split this lopsided or worse, at both ends",
            )

        if mine[2] + mine[3] + numbers[5] != len(questions):
            fail(
                f"for {name!r} the agreements and disagreements add up to "
                f"{mine[2] + mine[3] + numbers[5]} rather than "
                f"{len(questions)}",
                "every question either agrees or disagrees, and none does "
                "both",
            )

    correct = expected["behaved correctly"]
    false = expected["said something false"]

    if correct[4] <= THRESHOLD:
        fail(
            f"the gap in correct behaviour comes out at {correct[4]:.4f}",
            "the two agents differ by 5 questions there, split 3 against 8, "
            "which is well inside what coin flips produce",
        )

    if false[4] > THRESHOLD:
        fail(
            f"the gap in false statements comes out at {false[4]:.4f}",
            "the split there is 9 against 0, which coin flips almost never "
            "produce",
        )

    print(f"PASS  correct behaviour differs by {abs(correct[0] - correct[1])} "
          f"at p = {correct[4]:.3f} and false statements by "
          f"{abs(false[0] - false[1])} at p = {false[4]:.3f}")


if __name__ == "__main__":
    main()
