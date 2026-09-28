"""
Phase 6, lesson 3: when it chooses wrong.

Lesson 2 left a rule that routes three questions in four correctly on
questions it has not seen, and no prospect of doing much better. So stop
working on the rule and give the tools a say: each one gets a precondition,
refuses work that fails it, and the system falls back to search.

The measurements say this helps much less than it sounds like it should, and
the reasons why are the lesson.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
REFUSALS = HERE / ".work" / "refusals.tsv"

OPERATIONS = ("times", "plus", "minus", "divided")

REFUSED = None
PICKY_OVERLAP = 3


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def read_tasks():
    tasks = []

    with open(TASKS, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")
            if line:
                tasks.append(tuple(line.split("\t")))

    return tasks


def arithmetic(first, last, operation):
    if operation == "times":
        return str(first * last)
    if operation == "plus":
        return str(first + last)
    if operation == "minus":
        return str(first - last)
    if operation == "divided":
        return str(first // last)

    return ""


def calculate_anything(question):
    """Lesson 1's tool. Hand it a sentence and it raises."""
    words = question.split()

    return arithmetic(int(words[2]), int(words[-1]), words[3])


def calculate(question):
    """The same tool, with the precondition it always had, written down."""
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
    """The same tool, with everything it is able to check about its input."""
    words = question.split()

    if not words or not words[-1].isalpha():
        return REFUSED

    return str(len(words[-1]))


def make_search(sentences):
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
    """Route, call, and on a refusal fall back to search."""
    right = 0
    refused = 0
    survived = []

    for question, tool, answer in tasks:
        picked = router(question)

        try:
            given = tools[picked](question)
        except (ValueError, IndexError) as problem:
            survived.append((question, picked, "raised",
                             type(problem).__name__))
            continue

        if given is REFUSED:
            refused += 1
            picked = "search"
            given = tools["search"](question)

        if given == answer:
            right += 1
        elif tool != router(question):
            survived.append((question, picked, "gave", repr(given)))

    return right, refused, survived


def main() -> None:
    sentences = read_corpus()
    tasks = read_tasks()
    best = make_search(sentences)

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

    settings = [
        ("tools accept anything, opening rule", route_by_opening, anything),
        ("tools refuse, opening rule", route_by_opening, refusing),
        ("tools accept anything, shape rule", route_by_shape, anything),
        ("tools refuse, shape rule", route_by_shape, refusing),
    ]

    rows = []
    notes = {}

    for label, router, tools in settings:
        right, refused, survived = run(router, tasks, tools)
        rows.append((label, right, refused, len(tasks)))
        notes[label] = survived

    searchable = [(question, answer) for question, tool, answer in tasks
                  if tool == "search"]

    for label, tool in (("search alone, any overlap", search),
                        (f"search alone, overlap {PICKY_OVERLAP} or more",
                         picky_search)):
        right = sum(1 for question, answer in searchable
                    if tool(question) == answer)
        refused = sum(1 for question, _ in searchable
                      if tool(question) is REFUSED)
        rows.append((label, right, refused, len(searchable)))

    REFUSALS.parent.mkdir(parents=True, exist_ok=True)

    with open(REFUSALS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("setting\tright\trefused\tasked\n")

        for label, right, refused, asked in rows:
            handle.write(f"{label}\t{right}\t{refused}\t{asked}\n")

    print("A tool that can say no, measured against the same tool that cannot.")
    print()
    print("  setting                                right      refused")

    for label, right, refused, asked in rows:
        print(f"  {label:36}  {right:2} of {asked:2}  {refused:2}")

    print()
    print("What the opening rule's five mistakes did once the tools could "
          "refuse:")

    for question, picked, verb, given in notes["tools refuse, opening rule"]:
        print(f"  {question!r}")
        print(f"    ended at {picked}, {verb} {given}")

    print()

    hits = []
    misses = []

    for question, answer in searchable:
        overlap, sentence = best(question)
        (hits if sentence == answer else misses).append(overlap)

    print("Why search cannot be given a confidence threshold:")
    print(f"  the {len(hits)} it answers correctly score "
          f"{min(hits)} to {max(hits)}, mean {sum(hits) / len(hits):.1f}")
    print(f"  the {len(misses)} it gets wrong score "
          f"{min(misses)} to {max(misses)}, mean {sum(misses) / len(misses):.1f}")
    print("  every wrong answer scores what some right answer also scores.")


if __name__ == "__main__":
    main()
