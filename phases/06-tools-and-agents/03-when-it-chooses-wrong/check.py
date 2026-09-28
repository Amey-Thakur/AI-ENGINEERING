"""
Phase 6, lesson 3: the check.

It rebuilds all six settings itself and insists your numbers agree. Two rows
matter more than the others: the guarded tools under the good rule, which
must show that nothing refused, and the picky search, which must show that
refusing cost more answers than it saved.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
REFUSALS = HERE / ".work" / "refusals.tsv"

OPERATIONS = ("times", "plus", "minus", "divided")

REFUSED = None
PICKY_OVERLAP = 3


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_tasks():
    tasks = []

    for line in TASKS.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            tasks.append(tuple(line.rstrip("\n").split("\t")))

    return tasks


def arithmetic(first, last, operation):
    return {
        "times": str(first * last),
        "plus": str(first + last),
        "minus": str(first - last),
        "divided": str(first // last) if last else "",
    }.get(operation, "")


def calculate_anything(question):
    words = question.split()

    return arithmetic(int(words[2]), int(words[-1]), words[3])


def calculate(question):
    words = question.split()

    if len(words) < 4:
        return REFUSED
    if not words[2].isdigit() or not words[-1].isdigit():
        return REFUSED
    if words[3] not in OPERATIONS:
        return REFUSED

    return arithmetic(int(words[2]), int(words[-1]), words[3])


def count_anything(question):
    return str(len(question.split()[-1]))


def count(question):
    words = question.split()

    if not words or not words[-1].isalpha():
        return REFUSED

    return str(len(words[-1]))


def make_best(sentences):
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


def run(router, tasks, tools):
    right = 0
    refused = 0

    for question, _, answer in tasks:
        picked = router(question)

        try:
            given = tools[picked](question)
        except (ValueError, IndexError):
            continue

        if given is REFUSED:
            refused += 1
            given = tools["search"](question)

        right += given == answer

    return right, refused


def main() -> None:
    sentences = [line.strip()
                 for line in CORPUS.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    tasks = read_tasks()
    best = make_best(sentences)

    def search(question):
        return best(question)[1]

    def picky_search(question):
        overlap, sentence = best(question)

        return sentence if overlap >= PICKY_OVERLAP else REFUSED

    anything = {
        "calculate": calculate_anything,
        "count": count_anything,
        "search": search,
    }
    refusing = {"calculate": calculate, "count": count, "search": search}

    expected = {}

    for label, router, tools in (
        ("tools accept anything, opening rule", route_by_opening, anything),
        ("tools refuse, opening rule", route_by_opening, refusing),
        ("tools accept anything, shape rule", route_by_shape, anything),
        ("tools refuse, shape rule", route_by_shape, refusing),
    ):
        right, refused = run(router, tasks, tools)
        expected[label] = (right, refused, len(tasks))

    searchable = [(question, answer) for question, tool, answer in tasks
                  if tool == "search"]

    for label, tool in (("search alone, any overlap", search),
                        (f"search alone, overlap {PICKY_OVERLAP} or more",
                         picky_search)):
        right = sum(1 for question, answer in searchable
                    if tool(question) == answer)
        refused = sum(1 for question, _ in searchable
                      if tool(question) is REFUSED)
        expected[label] = (right, refused, len(searchable))

    if not REFUSALS.exists():
        fail(
            "there is no .work/refusals.tsv",
            "report each setting: how many questions it answered correctly "
            "and how many calls were refused",
        )

    lines = REFUSALS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["setting"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 4:
            fail(
                f"line {number} has {len(parts)} columns, and needs 4",
                "each row is the setting, how many right, how many refused, "
                "how many asked",
            )

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]), int(parts[3]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "the last three columns are counts",
            )

    for label, numbers in sorted(expected.items()):
        if label not in yours:
            fail(
                f"there is no row for {label!r}",
                f"report all {len(expected)} settings",
            )

        if yours[label] != numbers:
            right, refused, asked = numbers
            fail(
                f"for {label!r} you report {yours[label]} and running it "
                f"gives ({right}, {refused}, {asked})",
                "on a refusal the question falls back to search, and a "
                "refusal is counted whether or not the fallback then "
                "answered it",
            )

    guarded = expected["tools refuse, shape rule"]
    loose = expected["tools accept anything, shape rule"]

    if guarded != loose:
        fail(
            "the guarded and unguarded tools differ under the shape rule",
            "under a rule that never misroutes, no precondition is ever "
            "violated, so the two must score the same",
        )

    open_loose = expected["tools accept anything, opening rule"]
    open_guarded = expected["tools refuse, opening rule"]
    permissive = expected["search alone, any overlap"]
    picky = expected[f"search alone, overlap {PICKY_OVERLAP} or more"]

    print(f"PASS  refusing turns {open_loose[0]} of {open_loose[2]} into "
          f"{open_guarded[0]}, and a picky search trades "
          f"{permissive[0] - picky[0]} right answers for "
          f"{picky[1]} refusals")


if __name__ == "__main__":
    main()
