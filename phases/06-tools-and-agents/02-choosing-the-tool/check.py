"""
Phase 6, lesson 2: the check.

It routes and runs everything itself, then insists your numbers agree. The
row it cares most about is the better rule on the eight held-back questions,
because that is the only measurement in the lesson that was not taken on
questions the rule was written in front of.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
UNSEEN = HERE / "unseen.tsv"
ROUTING = HERE / ".work" / "routing.tsv"

OPERATIONS = ("times", "plus", "minus", "divided")


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_tasks(path):
    tasks = []

    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            tasks.append(tuple(line.rstrip("\n").split("\t")))

    return tasks


def calculate(question):
    words = question.split()
    first, last, operation = int(words[2]), int(words[-1]), words[3]

    return str({
        "times": first * last,
        "plus": first + last,
        "minus": first - last,
        "divided": first // last if last else 0,
    }.get(operation, ""))


def count(question):
    return str(len(question.split()[-1]))


def make_search(sentences):
    documents = [sentence.split() for sentence in sentences]

    def search(question):
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        return sentences[ranked[0][1]]

    return search


def route_by_opening(question):
    if "how many" in question:
        return "count"
    if "what is" in question:
        return "calculate"

    return "search"


def route_by_shape(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def measure(router, tasks, tools):
    routed = 0
    answered = 0

    for question, tool, answer in tasks:
        picked = router(question)
        routed += picked == tool

        try:
            answered += tools[picked](question) == answer
        except (ValueError, IndexError):
            pass

    return routed, answered


def main() -> None:
    sentences = [line.strip()
                 for line in CORPUS.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    tools = {
        "calculate": calculate,
        "count": count,
        "search": make_search(sentences),
    }

    written = read_tasks(TASKS)
    held_back = read_tasks(UNSEEN)

    sets = {
        f"the {len(written)} written first": written,
        f"the {len(held_back)} held back": held_back,
    }
    routers = {
        "obvious keywords": route_by_opening,
        "shape of the question": route_by_shape,
    }

    expected = {}

    for name, router in routers.items():
        for label, tasks in sets.items():
            routed, answered = measure(router, tasks, tools)
            expected[(name, label)] = (routed, answered, len(tasks))

    if not ROUTING.exists():
        fail(
            "there is no .work/routing.tsv",
            "report each rule on each set of questions: how many it routed "
            "correctly and how many it then answered correctly",
        )

    lines = ROUTING.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["router"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 5:
            fail(
                f"line {number} has {len(parts)} columns, and needs 5",
                "each row is the rule, which questions, how many routed, how "
                "many answered, how many asked",
            )

        try:
            yours[(parts[0], parts[1])] = (int(parts[2]), int(parts[3]),
                                           int(parts[4]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "the last three columns are counts",
            )

    held_back_label = f"the {len(held_back)} held back"

    for (name, label), numbers in sorted(expected.items()):
        if (name, label) not in yours:
            if label == held_back_label:
                fail(
                    f"you did not measure {name!r} on {label}",
                    "a rule written while looking at the questions scores "
                    "well on those questions, which is why unseen.tsv is "
                    "held back; measure both rules on both sets",
                )

            fail(
                f"there is no row for {name!r} on {label}",
                "report both rules on both sets of questions",
            )

        if yours[(name, label)] != numbers:
            routed, answered, asked = numbers
            fail(
                f"for {name!r} on {label} you report {yours[(name, label)]} "
                f"and running it gives ({routed}, {answered}, {asked})",
                "route each question, run the tool the rule picked rather "
                "than the tool the label names, and count both",
            )

    better = expected[("shape of the question", held_back_label)]
    perfect = expected[("shape of the question", f"the {len(written)} written first")]

    print(f"PASS  the better rule routes {perfect[0]} of {perfect[2]} on the "
          f"questions it was written for and {better[0]} of {better[2]} on "
          f"the ones it was not")


if __name__ == "__main__":
    main()
