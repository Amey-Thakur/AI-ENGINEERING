"""
Phase 8, lesson 1: the check.

It meters every question itself and compares your distribution. It also holds
the two findings: that no question costs anything near the average, and that
refusing a question costs as much as answering one.

Run it with:  python check.py
"""

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
SPEND = HERE / ".work" / "spend.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3


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


def route(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    documents = [sentence.split() for sentence in sentences]

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    measured = []

    for question, answer, answerable in questions:
        picked = route(question)
        comparisons = 0
        given = REFUSED

        if picked != "search":
            given = {"calculate": calculate, "count": count}[picked](question)

        if given is REFUSED:
            words = set(question.split())
            comparisons = len(documents) * len(words)
            ranked = sorted(
                ((-len(words & set(document)), index)
                 for index, document in enumerate(documents)),
                key=lambda pair: (pair[0], pair[1]),
            )
            overlap, index = ranked[0]
            given = sentences[index] if -ranked[0][0] >= BAR else REFUSED

        measured.append((given is REFUSED, comparisons))

    expected = Counter(comparisons for _, comparisons in measured)

    if not SPEND.exists():
        fail(
            "there is no .work/spend.tsv",
            "report every cost that occurs and how many questions have it",
        )

    lines = read_lines(SPEND)

    if lines and lines[0].split("\t")[:1] == ["comparisons"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 2:
            fail(
                f"line {number} has {len(parts)} columns, and needs 2",
                "the cost in word comparisons, and how many questions cost "
                "that much",
            )

        try:
            yours[int(parts[0])] = int(parts[1])
        except ValueError:
            fail(
                f"line {number} holds something that is not a whole number",
                "both columns are counts",
            )

    if yours != dict(expected):
        missing = sorted(set(expected) - set(yours))
        wrong = [cost for cost in sorted(set(expected) & set(yours))
                 if yours[cost] != expected[cost]]

        if missing:
            fail(
                f"you report no questions costing {missing[0]} comparisons, "
                f"and {expected[missing[0]]} do",
                "one search compares the question against every sentence, so "
                "the cost is the corpus size times the number of words in "
                "the question",
            )

        if wrong:
            cost = wrong[0]
            fail(
                f"you report {yours[cost]} questions costing {cost} and there "
                f"are {expected[cost]}",
                "a question answered by a tool never reaches search and "
                "costs nothing",
            )

        fail(
            f"you report costs of {sorted(set(yours) - set(expected))} that "
            f"do not occur",
            "every cost is the corpus size times a question length",
        )

    costs = sorted(comparisons for _, comparisons in measured)
    mean = sum(costs) / len(costs)
    cheapest_real = min(cost for cost in costs if cost > 0)

    if any(0 < cost < cheapest_real for cost in costs):
        fail(
            "some question costs between nothing and the cheapest search",
            "a question either reaches search and pays for the whole corpus, "
            "or it does not and pays nothing",
        )

    if not 0 < mean < cheapest_real:
        fail(
            f"the mean cost is {mean:.0f} and the cheapest search is "
            f"{cheapest_real}",
            "with 23 questions costing nothing the average falls into the "
            "gap, which is the finding",
        )

    declined = [cost for refused, cost in measured if refused]
    answered = [cost for refused, cost in measured if not refused]

    if sum(declined) / len(declined) <= sum(answered) / len(answered):
        fail(
            "declined questions come out cheaper than answered ones",
            "every declined question was searched in full first, and many "
            "answered ones never reached search at all",
        )

    print(f"PASS  {len(set(costs))} distinct costs, a mean of {mean:.0f} that "
          f"no question has, and refusing costs "
          f"{sum(declined) / len(declined):.0f} against "
          f"{sum(answered) / len(answered):.0f} to answer")


if __name__ == "__main__":
    main()
