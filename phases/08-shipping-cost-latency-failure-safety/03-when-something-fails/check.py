"""
Phase 8, lesson 3: the check.

It takes the same pieces away and insists on the uncomfortable part: that
losing the corpus entirely costs only a handful of questions and reduces
false statements to zero, so neither of the two numbers anybody watches goes
in the direction that would raise an alarm.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
FAILURES = HERE / ".work" / "failures.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
WORKING = "everything works"
EMPTY = "no corpus at all"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


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


def unavailable(question):
    return REFUSED


def route(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def make_agent(sentences, arithmetic, letters):
    documents = [set(sentence.split()) for sentence in sentences]

    def agent(question):
        picked = route(question)

        if picked != "search":
            found = {"calculate": arithmetic,
                     "count": letters}[picked](question)

            if found is not REFUSED:
                return found, None

        if not documents:
            return REFUSED, 0

        words = set(question.split())
        ranked = sorted(
            ((-len(words & document), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap = -ranked[0][0]

        return (sentences[ranked[0][1]] if overlap >= BAR else REFUSED), overlap

    return agent


def main() -> None:
    corpus = [line.strip() for line in read_lines(CORPUS)]

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    cases = (
        (WORKING, corpus, calculate, count),
        ("calculate unavailable", corpus, unavailable, count),
        ("count unavailable", corpus, calculate, unavailable),
        ("both tools unavailable", corpus, unavailable, unavailable),
        ("half the corpus loaded", corpus[:len(corpus) // 2], calculate, count),
        ("a tenth of the corpus", corpus[:len(corpus) // 10], calculate, count),
        (EMPTY, [], calculate, count),
    )

    expected = {}

    for label, sentences, arithmetic, letters in cases:
        agent = make_agent(sentences, arithmetic, letters)
        correct = wrong = declined = cleared = 0

        for question, answer, answerable in questions:
            given, overlap = agent(question)

            if overlap is not None:
                cleared += overlap >= BAR

            if given is REFUSED:
                declined += 1
                correct += not answerable
            elif answerable and given == answer:
                correct += 1
            else:
                wrong += 1

        expected[label] = (correct, wrong, declined, cleared)

    if not FAILURES.exists():
        fail(
            "there is no .work/failures.tsv",
            "for each failure, report how many questions were handled "
            "correctly, how many answers were false, how many were declined, "
            "and how many searches cleared the threshold",
        )

    lines = read_lines(FAILURES)

    if lines and lines[0].split("\t")[:1] == ["failure"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 5:
            fail(
                f"line {number} has {len(parts)} columns, and needs 5",
                "the failure, correct, false, declined, cleared the bar",
            )

        try:
            yours[parts[0]] = tuple(int(part) for part in parts[1:5])
        except ValueError:
            fail(
                f"line {number} holds something that is not a whole number",
                "every column after the name is a count",
            )

    for label, numbers in expected.items():
        if label not in yours:
            fail(
                f"there is no row for {label!r}",
                f"report all {len(expected)} failures",
            )

        if yours[label] != numbers:
            fail(
                f"for {label!r} you report {yours[label]} and running it "
                f"gives {numbers}",
                "a tool that is down refuses, so its questions fall through "
                "to search rather than raising",
            )

    working = expected[WORKING]
    empty = expected[EMPTY]

    if empty[1] >= working[1]:
        fail(
            f"with no corpus the system makes {empty[1]} false statements "
            f"and with one it makes {working[1]}",
            "nothing can clear the threshold against an empty corpus, so a "
            "total outage cannot produce a false answer",
        )

    if working[0] - empty[0] > len(questions) // 4:
        fail(
            f"losing the corpus costs {working[0] - empty[0]} of "
            f"{len(questions)} questions",
            "the tools still answer 23 and the unanswerable 10 are now "
            "declined correctly, so the headline barely moves, which is the "
            "point",
        )

    if empty[3] != 0 or working[3] == 0:
        fail(
            "the count of searches clearing the threshold does not "
            "distinguish a working corpus from an empty one",
            "this is the only number in the table that detects the outage, "
            "so it has to move",
        )

    print(f"PASS  a total outage costs {working[0] - empty[0]} of "
          f"{len(questions)} questions and removes all {working[1]} false "
          f"statements, while searches clearing the bar go {working[3]} to "
          f"{empty[3]}")


if __name__ == "__main__":
    main()
