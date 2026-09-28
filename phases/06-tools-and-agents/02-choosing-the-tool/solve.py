"""
Phase 6, lesson 2: choosing the tool.

Lesson 1 answered 29 of 30 with a person reading the label and picking the
tool. Here the system picks for itself, from two rules, and both are measured
twice: once on the questions that were in front of us while the rules were
written, and once on eight questions that were held back.

The second measurement is the one that means anything.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
UNSEEN = HERE / "unseen.tsv"
ROUTING = HERE / ".work" / "routing.tsv"

OPERATIONS = ("times", "plus", "minus", "divided")


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def read_tasks(path):
    tasks = []

    with open(path, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")
            if line:
                tasks.append(tuple(line.split("\t")))

    return tasks


def calculate(question):
    """Lesson 1's arithmetic tool, unchanged."""
    words = question.split()
    first = int(words[2])
    last = int(words[-1])
    operation = words[3]

    if operation == "times":
        return str(first * last)
    if operation == "plus":
        return str(first + last)
    if operation == "minus":
        return str(first - last)
    if operation == "divided":
        return str(first // last)

    return ""


def count(question):
    """How many letters are in the last word of the question."""
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
    """The rule anyone writes first: look at how the question starts."""
    if "how many" in question:
        return "count"
    if "what is" in question:
        return "calculate"

    return "search"


def route_by_shape(question):
    """Look for what the tool actually needs instead of how the question opens."""
    if "letters are in" in question:
        return "count"

    words = question.split()
    has_number = any(word.isdigit() for word in words)
    has_operation = any(word in OPERATIONS for word in words)

    if has_number and has_operation:
        return "calculate"

    return "search"


def measure(router, tasks, tools):
    """Route every question, run whatever tool was picked, and count both."""
    routed = 0
    answered = 0
    wrong = []

    for question, tool, answer in tasks:
        picked = router(question)

        if picked == tool:
            routed += 1

        try:
            given = tools[picked](question)
        except (ValueError, IndexError) as problem:
            given = f"{type(problem).__name__}"
            wrong.append((question, tool, picked, given, True))
            continue

        if given == answer:
            answered += 1
        elif picked != tool:
            wrong.append((question, tool, picked, repr(given), False))

    return routed, answered, wrong


def main() -> None:
    sentences = read_corpus()
    tools = {
        "calculate": calculate,
        "count": count,
        "search": make_search(sentences),
    }

    written = read_tasks(TASKS)
    held_back = read_tasks(UNSEEN)

    sets = (
        (f"the {len(written)} written first", written),
        (f"the {len(held_back)} held back", held_back),
    )
    routers = (
        ("obvious keywords", route_by_opening),
        ("shape of the question", route_by_shape),
    )

    rows = []
    misroutes = {}

    for name, router in routers:
        for label, tasks in sets:
            routed, answered, wrong = measure(router, tasks, tools)
            rows.append((name, label, routed, answered, len(tasks)))
            misroutes[(name, label)] = wrong

    ROUTING.parent.mkdir(parents=True, exist_ok=True)

    with open(ROUTING, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("router\tquestions\trouted\tanswered\tasked\n")

        for name, label, routed, answered, asked in rows:
            handle.write(f"{name}\t{label}\t{routed}\t{answered}\t{asked}\n")

    print("Two rules for picking the tool, each measured twice.")
    print()
    print("  router                 questions              routed    answered")

    for name, label, routed, answered, asked in rows:
        print(f"  {name:21}  {label:20}  {routed:2} of {asked:2}  {answered:2} of {asked:2}")

    print()

    perfect = [row for row in rows
               if row[0] == "shape of the question" and row[1] == sets[0][0]][0]
    print(f"Routing all {perfect[4]} correctly still answers {perfect[3]}, "
          f"because search misses {perfect[4] - perfect[3]} of them on its own.")
    print()

    print("Sent to the wrong tool by the obvious rule, and what came back:")

    for question, tool, picked, given, crashed in misroutes[
            ("obvious keywords", sets[0][0])]:
        noise = "raised" if crashed else "gave"
        print(f"  {question!r}")
        print(f"    wanted {tool}, picked {picked}, {noise} {given}")

    print()
    print("Sent to the wrong tool by the better rule, on questions it had "
          "never seen:")

    for question, tool, picked, given, crashed in misroutes[
            ("shape of the question", sets[1][0])]:
        noise = "raised" if crashed else "gave"
        print(f"  {question!r}")
        print(f"    wanted {tool}, picked {picked}, {noise} {given}")


if __name__ == "__main__":
    main()
