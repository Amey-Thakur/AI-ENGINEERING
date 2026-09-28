"""
Phase 6, lesson 5: the check.

It rebuilds all three agents over all 48 questions and compares your six
numbers for each. It also insists on the two structural facts the lesson
rests on: that the four outcome counts sum to the number of questions, and
that the retrying version is indistinguishable from the one it wraps except
on cost.

Run it with:  python check.py
"""

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
SCORECARD = HERE / ".work" / "scorecard.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
CAP = 6

COLUMNS = ("right", "wrong", "held back", "declined", "behaved correctly",
           "calls")


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


def shorten(question):
    words = question.split()

    return " ".join(words[1:]) if len(words) > 1 else ""


def make_agent(best, bar, retry):
    def search(question):
        overlap, sentence = best(question)

        return sentence if overlap >= bar else REFUSED

    def agent(question):
        calls = 0
        picked = route(question)

        if picked != "search":
            calls += 1
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found, calls

        asked = question

        for _ in range(CAP if retry else 1):
            calls += 1
            found = search(asked)

            if found is not REFUSED:
                return found, calls

            asked = shorten(asked)

            if not asked:
                break

        return REFUSED, calls

    return agent


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    best = make_scorer(sentences)

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    systems = (
        ("answer whatever wins", 0, False),
        (f"decline below overlap {BAR}", BAR, False),
        (f"decline, then retry, cap {CAP}", BAR, True),
    )

    expected = {}

    for label, bar, retry in systems:
        agent = make_agent(best, bar, retry)
        right = wrong = held = declined = calls = 0

        for question, answer, answerable in questions:
            given, made = agent(question)
            calls += made

            if given is REFUSED:
                if answerable:
                    held += 1
                else:
                    declined += 1
            elif answerable and given == answer:
                right += 1
            else:
                wrong += 1

        expected[label] = (right, wrong, held, declined, right + declined,
                           calls)

    if not SCORECARD.exists():
        fail(
            "there is no .work/scorecard.tsv",
            "report six numbers for each of the three systems: "
            + ", ".join(COLUMNS),
        )

    lines = SCORECARD.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["system"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 7:
            fail(
                f"line {number} has {len(parts)} columns, and needs 7",
                "the system name followed by " + ", ".join(COLUMNS),
            )

        try:
            yours[parts[0]] = tuple(int(part) for part in parts[1:7])
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "every column after the name is a count",
            )

    for label, numbers in expected.items():
        if label not in yours:
            fail(
                f"there is no row for {label!r}",
                f"report all three systems: {', '.join(expected)}",
            )

        if yours[label] != numbers:
            named = ", ".join(f"{name} {value}"
                              for name, value in zip(COLUMNS, numbers))
            fail(
                f"for {label!r} you report {yours[label]} and running it "
                f"gives ({named})",
                "a question with no answer that gets answered counts as "
                "wrong, and every call the agent makes counts, including the "
                "one that was refused",
            )

        outcomes = sum(numbers[:4])

        if outcomes != len(questions):
            fail(
                f"for {label!r} the four outcomes add up to {outcomes} and "
                f"there are {len(questions)} questions",
                "every question ends as right, wrong, held back or declined, "
                "and no question ends as two of them",
            )

    plain = expected[f"decline below overlap {BAR}"]
    retrying = expected[f"decline, then retry, cap {CAP}"]

    if plain[:5] != retrying[:5]:
        fail(
            "the retrying agent differs from the plain one on an outcome",
            "shortening a question cannot raise its overlap, so the retry "
            "cannot change any answer and may only change the cost",
        )

    if retrying[5] <= plain[5]:
        fail(
            f"the retrying agent makes {retrying[5]} calls and the plain one "
            f"{plain[5]}",
            "every refused search is followed by another attempt, so "
            "retrying has to cost more",
        )

    loose = expected["answer whatever wins"]
    breakeven = Fraction(loose[0] - plain[0], loose[1] - plain[1])

    print(f"PASS  {loose[0]} right against {plain[0]}, {loose[1]} wrong "
          f"against {plain[1]}, and neither wins until you price a wrong "
          f"answer above {breakeven} of a right one")


if __name__ == "__main__":
    main()
