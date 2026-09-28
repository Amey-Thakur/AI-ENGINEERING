"""
Phase 6, lesson 1: what a model cannot do.

Asks thirty questions that a language model has no way of answering, then
answers them with three small programs instead.

Two of those programs are exact: given the same question they return the same
correct answer, every time, forever. The third is search from phase 5, which is
a tool in the same sense but not in the same league, and telling those two
kinds apart is most of the lesson.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
RESULTS = HERE / ".work" / "results.tsv"

SHOW = 3


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


def calculate(question):
    """Arithmetic. Exact, and the same answer every time."""
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
        """Phase 5's search. A tool, but one that can be wrong."""
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        return sentences[ranked[0][1]]

    return search


def main() -> None:
    sentences = read_corpus()
    tasks = read_tasks()

    tools = {
        "calculate": calculate,
        "count": count,
        "search": make_search(sentences),
    }

    vocabulary = {word for sentence in sentences for word in sentence.split()}

    unsayable = sum(
        1 for _, _, answer in tasks
        if any(word not in vocabulary for word in answer.split())
    )

    scored = defaultdict(lambda: [0, 0])
    misses = []

    for question, tool, answer in tasks:
        given = tools[tool](question)
        right = given == answer

        scored[tool][0] += right
        scored[tool][1] += 1

        if not right:
            misses.append((question, tool, given, answer))

    total_right = sum(right for right, _ in scored.values())

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("tool\tright\tasked\n")
        handle.write(f"model alone\t0\t{len(tasks)}\n")

        for tool in sorted(scored):
            right, asked = scored[tool]
            handle.write(f"{tool}\t{right}\t{asked}\n")

    digits = sum(1 for word in vocabulary if any(mark.isdigit() for mark in word))

    print(f"The model's vocabulary is {len(vocabulary)} words, of which "
          f"{digits} contain a digit.")
    print(f"{unsayable} of the {len(tasks)} answers contain something it has "
          f"never seen, so it could not produce them at any temperature.")
    print()
    print("  tool         right        exact?")
    print(f"  model alone   0 of {len(tasks)}   no")

    for tool in sorted(scored):
        right, asked = scored[tool]
        exact = "yes" if tool in ("calculate", "count") else "no"
        print(f"  {tool:11}  {right:2} of {asked:2}   {exact}")

    print()
    print(f"With the right tool for each question: {total_right} of {len(tasks)}")
    print()

    for question, tool, given, answer in misses[:SHOW]:
        print(f"  {tool} got {question!r} wrong")
        print(f"    gave:  {given}")
        print(f"    wanted: {answer}")


if __name__ == "__main__":
    main()
