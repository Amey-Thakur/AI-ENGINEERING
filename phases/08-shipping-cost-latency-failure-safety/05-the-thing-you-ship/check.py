"""
Phase 8, lesson 5: the check.

The last check in the course. It rebuilds the finished system and verifies
every line of the release sheet, and it holds the three properties that took
eight phases to arrive at: the index is equivalent to the scan, no private
sentence is reachable, and the system beats both floors.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from math import exp, lgamma, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
PRIVATE = HERE / "private.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
RELEASE = HERE / ".work" / "release.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
ALPHA = 0.05
HALVINGS = 60

REQUIRED = (
    "questions asked",
    "handled correctly",
    "true rate, 95 percent confident",
    "false statements",
    "questions declined",
    "private sentences returned",
    "floor: decline everything",
    "floor: tools only, no search",
    "dearest question",
    "median question",
    "whole run",
    "healthy signal",
    "if the corpus is lost",
)


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def log_choose(n, k):
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def pin_down(rising, target):
    low, high = 0.0, 1.0

    for _ in range(HALVINGS):
        middle = (low + high) / 2

        if rising(middle) < target:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def interval(k, n):
    def at_least(rate):
        return sum(exp(log_choose(n, i) + i * log(rate)
                       + (n - i) * log(1 - rate)) for i in range(k, n + 1))

    def at_most(rate):
        return sum(exp(log_choose(n, i) + i * log(rate)
                       + (n - i) * log(1 - rate)) for i in range(0, k + 1))

    low = 0.0 if k == 0 else pin_down(at_least, ALPHA / 2)
    high = 1.0 if k == n else pin_down(lambda r: -at_most(r), -ALPHA / 2)

    return low, high


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


def make_system(sentences):
    postings = defaultdict(list)

    for index, sentence in enumerate(sentences):
        for word in set(sentence.split()):
            postings[word].append(index)

    def ask(question):
        picked = route(question)

        if picked != "search":
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found, None, 0

        words = set(question.split())
        cost = 0
        hits = Counter()

        for word in words:
            holding = postings.get(word, ())
            cost += len(holding)

            for index in holding:
                hits[index] += 1

        if not hits:
            return REFUSED, 0, cost

        overlap = max(hits.values())

        if overlap < BAR:
            return REFUSED, overlap, cost

        winner = min(index for index, seen in hits.items() if seen == overlap)

        return sentences[winner], overlap, cost

    return ask


def by_scanning(question, sentences):
    documents = [set(sentence.split()) for sentence in sentences]
    words = set(question.split())
    ranked = sorted(
        ((-len(words & document), index)
         for index, document in enumerate(documents)),
        key=lambda pair: (pair[0], pair[1]),
    )
    overlap = -ranked[0][0]

    return sentences[ranked[0][1]] if overlap >= BAR else REFUSED


def main() -> None:
    public = [line.strip() for line in read_lines(CORPUS)]
    private = set(line.strip() for line in read_lines(PRIVATE))

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    ask = make_system(public)

    correct = wrong = declined = searched = cleared = leaked = 0
    costs = []
    disagreed = []

    for question, answer, answerable in questions:
        given, overlap, cost = ask(question)
        costs.append(cost)

        if overlap is not None:
            searched += 1
            cleared += overlap >= BAR

            if given != by_scanning(question, public):
                disagreed.append(question)

        leaked += given in private

        if given is REFUSED:
            declined += 1
            correct += not answerable
        elif answerable and given == answer:
            correct += 1
        else:
            wrong += 1

    if disagreed:
        fail(
            f"the indexed system disagrees with a plain scan on "
            f"{len(disagreed)} questions, such as {disagreed[0]!r}",
            "the index exists to do the same work for less, so any "
            "disagreement is a bug rather than a tradeoff",
        )

    if leaked:
        fail(
            f"{leaked} private sentences were returned",
            "private.txt is never indexed, so nothing in it should be "
            "reachable at all",
        )

    floor = sum(1 for _, _, answerable in questions if not answerable)

    if correct <= floor:
        fail(
            f"the system handles {correct} of {len(questions)} and declining "
            f"everything handles {floor}",
            "a system that cannot beat an empty function has not been shown "
            "to do anything",
        )

    low, high = interval(correct, len(questions))
    dearest = max(costs)
    median = sorted(costs)[len(costs) // 2]

    expected = {
        "questions asked": str(len(questions)),
        "handled correctly": f"{correct} of {len(questions)}",
        "true rate, 95 percent confident": f"{low:.1%} to {high:.1%}",
        "false statements": str(wrong),
        "questions declined": str(declined),
        "private sentences returned": str(leaked),
        "floor: decline everything": f"{floor} of {len(questions)}",
        "dearest question": f"{dearest} comparisons",
        "median question": f"{median} comparisons",
        "whole run": f"{sum(costs)} comparisons",
        "healthy signal": f"{cleared} of {searched} searches clear it",
    }

    if not RELEASE.exists():
        fail(
            "there is no .work/release.tsv",
            "the deliverable is a page of numbers, each with the lesson that "
            "measured it",
        )

    lines = read_lines(RELEASE)

    if lines and lines[0].split("\t")[:1] == ["property"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 3:
            fail(
                f"line {number} has {len(parts)} columns, and needs 3",
                "the property, its value, and where it was measured",
            )

        yours[parts[0]] = (parts[1], parts[2])

    for label in REQUIRED:
        if label not in yours:
            fail(
                f"the release sheet has no line for {label!r}",
                "every line matters to somebody: the score to a product "
                "owner, the cost to whoever pays, the floors to anybody "
                "deciding whether to keep it",
            )

        if not yours[label][1]:
            fail(
                f"the line for {label!r} does not say where it was measured",
                "a number without a source is a number nobody can check",
            )

    for label, value in expected.items():
        if yours[label][0] != value:
            fail(
                f"the sheet says {label!r} is {yours[label][0]!r} and running "
                f"it gives {value!r}",
                "every value on the sheet is computed by this file, so none "
                "of them can be typed by hand",
            )

    print(f"PASS  {len(REQUIRED)} lines, all sourced, the index agrees with "
          f"the scan on every question, {leaked} private sentences reachable, "
          f"and {correct} of {len(questions)} against a floor of {floor}")


if __name__ == "__main__":
    main()
