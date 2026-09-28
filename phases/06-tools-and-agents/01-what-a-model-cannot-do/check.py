"""
Phase 6, lesson 1: the check.

It runs the two exact tools itself and insists they are perfect, because a
tool that computes an answer has no excuse for being wrong. Search is allowed
to miss, because it is a different kind of thing.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
RESULTS = HERE / ".work" / "results.tsv"

EXACT = ("calculate", "count")


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


def search(question, sentences):
    documents = [sentence.split() for sentence in sentences]
    words = set(question.split())
    ranked = sorted(
        ((-len(words & set(document)), index)
         for index, document in enumerate(documents)),
        key=lambda pair: (pair[0], pair[1]),
    )
    return sentences[ranked[0][1]]


def main() -> None:
    tasks = read_tasks()
    sentences = [line.strip()
                 for line in CORPUS.read_text(encoding="utf-8").splitlines()
                 if line.strip()]

    expected = {}

    for tool in EXACT:
        runner = calculate if tool == "calculate" else count
        wanted = [(question, answer) for question, kind, answer in tasks
                  if kind == tool]
        right = sum(1 for question, answer in wanted if runner(question) == answer)
        expected[tool] = (right, len(wanted))

        if right != len(wanted):
            fail(
                f"the {tool} tool should answer all {len(wanted)} of its "
                f"questions and gets {right}",
                "an exact tool computes the answer, so any miss is a bug in "
                "the tool rather than a limitation",
            )

    wanted = [(question, answer) for question, kind, answer in tasks
              if kind == "search"]
    found = sum(1 for question, answer in wanted
                if search(question, sentences) == answer)
    expected["search"] = (found, len(wanted))

    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report how many questions each tool answered correctly",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["tool"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 3:
            fail(
                f"line {number} has {len(parts)} columns, and needs at least 3",
                "each row is the tool, how many it got right, and how many "
                "it was asked",
            )

        try:
            yours[parts[0].strip()] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "both columns after the name are counts",
            )

    for tool, (right, asked) in expected.items():
        if tool not in yours:
            fail(
                f"there is no row for {tool!r}",
                f"report all three tools: {', '.join(sorted(expected))}",
            )

        if yours[tool] != (right, asked):
            fail(
                f"for {tool!r} you report {yours[tool]}, and running it gives "
                f"({right}, {asked})",
                "run each tool on the questions marked for it in tasks.tsv",
            )

    if "model alone" in yours and yours["model alone"][0] != 0:
        fail(
            f"you report the model alone getting {yours['model alone'][0]} "
            f"right",
            "the corpus contains no digits at all, so the model cannot "
            "produce any numeric answer",
        )

    total = sum(right for right, _ in expected.values())
    print(f"PASS  exact tools perfect, search {expected['search'][0]} of "
          f"{expected['search'][1]}, {total} of {len(tasks)} overall")


if __name__ == "__main__":
    main()
