"""
Phase 7, lesson 3: the check.

It rebuilds every system, including the ones that barely exist, and insists
your numbers agree. It also holds the two findings in place: that a system
which never answers still gets the unanswerable questions right, and that
deleting the whole search half costs less than it sounds like it should.

Run it with:  python check.py
"""

import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
BASELINES = HERE / ".work" / "baselines.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
THRESHOLD = 0.05


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


def build(best, sentences):
    def always_decline(_):
        return REFUSED

    def the_first_sentence(_):
        return sentences[0]

    def always_search(question):
        return best(question)[1]

    def tools_only(question):
        picked = route(question)

        if picked == "search":
            return REFUSED

        return {"calculate": calculate, "count": count}[picked](question)

    def agent(bar):
        def run(question):
            picked = route(question)

            if picked != "search":
                found = {"calculate": calculate,
                         "count": count}[picked](question)

                if found is not REFUSED:
                    return found

            overlap, sentence = best(question)

            return sentence if overlap >= bar else REFUSED

        return run

    return {
        "always decline": always_decline,
        "always return the first sentence": the_first_sentence,
        "always search, no routing": always_search,
        "the tools only, decline the rest": tools_only,
        "the confident agent": agent(0),
        "the cautious agent": agent(BAR),
    }


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

    unanswerable = 0

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))
        unanswerable += 1

    systems = build(best, sentences)
    expected = {}

    for name, system in systems.items():
        correct = sum(1 for question, answer, answerable in questions
                      if behaved_correctly(system(question), answer,
                                           answerable))
        false = sum(1 for question, answer, answerable in questions
                    if said_something_false(system(question), answer,
                                            answerable))
        expected[name] = (correct, false, len(questions))

    if not BASELINES.exists():
        fail(
            "there is no .work/baselines.tsv",
            "report every system, including the ones that do nothing: how "
            "many questions it handled correctly and how many false things "
            "it said",
        )

    lines = read_lines(BASELINES)

    if lines and lines[0].split("\t")[:1] == ["system"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 4:
            fail(
                f"line {number} has {len(parts)} columns, and needs 4",
                "the system, how many correct, how many false, how many "
                "asked",
            )

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]), int(parts[3]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "the three columns after the name are counts",
            )

    for name, numbers in expected.items():
        if name not in yours:
            fail(
                f"there is no row for {name!r}",
                f"report all {len(expected)} systems, the trivial ones "
                f"included, because they are the point",
            )

        if yours[name] != numbers:
            correct, false, asked = numbers
            fail(
                f"for {name!r} you report {yours[name]} and running it gives "
                f"({correct}, {false}, {asked})",
                "declining is correct on a question with no answer and wrong "
                "on one that has an answer, and a decline is never a false "
                "statement",
            )

    if expected["always decline"][0] != unanswerable:
        fail(
            f"a system that never answers scores "
            f"{expected['always decline'][0]} and there are {unanswerable} "
            f"unanswerable questions",
            "declining everything is exactly right on every question that "
            "has no answer, and wrong on every other one",
        )

    if expected["always decline"][1] != 0:
        fail(
            "a system that never answers is recorded as saying something "
            "false",
            "refusing to answer states nothing, so it cannot state anything "
            "untrue",
        )

    stripped = systems["the tools only, decline the rest"]

    for name in ("the confident agent", "the cautious agent"):
        ahead = behind = 0

        for question, answer, answerable in questions:
            mine = behaved_correctly(systems[name](question), answer,
                                     answerable)
            theirs = behaved_correctly(stripped(question), answer, answerable)
            ahead += mine and not theirs
            behind += theirs and not mine

        if coin_flip_chance(ahead, behind) <= THRESHOLD:
            fail(
                f"{name!r} comes out reliably better than deleting the "
                f"search half",
                "on these 48 questions neither agent clears the usual bar "
                "against the stripped down system, which is the finding",
            )

    print(f"PASS  doing nothing scores {expected['always decline'][0]} of "
          f"{len(questions)}, the tools alone score "
          f"{expected['the tools only, decline the rest'][0]} with no false "
          f"statements, and the full agent scores "
          f"{expected['the cautious agent'][0]}")


if __name__ == "__main__":
    main()
