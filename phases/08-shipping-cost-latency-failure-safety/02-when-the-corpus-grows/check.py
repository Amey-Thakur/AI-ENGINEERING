"""
Phase 8, lesson 2: the check.

The row that matters is the middle one. The index has to agree with the scan
on every single question, because an optimisation that changes an answer is
not an optimisation, and the check says so in those words.

Run it with:  python check.py
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
MEASURED = HERE / ".work" / "index.tsv"

BAR = 3
DROPPED = ("the",)


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def build_index(sentences):
    postings = defaultdict(list)

    for index, sentence in enumerate(sentences):
        for word in set(sentence.split()):
            postings[word].append(index)

    return postings


def by_scanning(question, sentences, documents):
    words = set(question.split())
    cost = len(documents) * len(words)
    ranked = sorted(
        ((-len(words & document), index)
         for index, document in enumerate(documents)),
        key=lambda pair: (pair[0], pair[1]),
    )

    return cost, -ranked[0][0], sentences[ranked[0][1]]


def by_index(question, sentences, postings, skip=()):
    words = set(question.split()) - set(skip)
    cost = 0
    hits = Counter()

    for word in words:
        holding = postings.get(word, ())
        cost += len(holding)

        for index in holding:
            hits[index] += 1

    if not hits:
        return cost, 0, sentences[0]

    top = max(hits.values())
    winner = min(index for index, seen in hits.items() if seen == top)

    return cost, top, sentences[winner]


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    documents = [set(sentence.split()) for sentence in sentences]
    postings = build_index(sentences)

    answerable = [(line.split("\t")[0], line.split("\t")[2])
                  for line in read_lines(TASKS)[1:]
                  if line.split("\t")[1] == "search"]
    unanswerable = [line.split("\t")[0]
                    for line in read_lines(IMPOSSIBLE)[1:]]
    questions = [question for question, _ in answerable] + unanswerable

    searches = {
        "scan every sentence":
            lambda question: by_scanning(question, sentences, documents),
        "an inverted index":
            lambda question: by_index(question, sentences, postings),
        f"the index without {DROPPED[0]!r}":
            lambda question: by_index(question, sentences, postings, DROPPED),
    }

    reference = {question: by_scanning(question, sentences, documents)[2]
                 for question in questions}

    expected = {}

    for label, search in searches.items():
        cost = sum(search(question)[0] for question in questions)
        agreed = sum(1 for question in questions
                     if search(question)[2] == reference[question])
        right = sum(1 for question, answer in answerable
                    if search(question)[1] >= BAR
                    and search(question)[2] == answer)
        declined = sum(1 for question in unanswerable
                       if search(question)[1] < BAR)
        expected[label] = (cost, agreed, right, declined, right + declined)

    scan = expected["scan every sentence"]
    index = expected["an inverted index"]
    without = expected[f"the index without {DROPPED[0]!r}"]

    if index[1] != len(questions):
        fail(
            f"the index disagrees with the scan on "
            f"{len(questions) - index[1]} questions",
            "both score a sentence by how many question words it holds, so "
            "they must pick the same one, ties included; check how the tie "
            "is broken",
        )

    if index[0] >= scan[0]:
        fail(
            f"the index reads {index[0]} and the scan reads {scan[0]}",
            "the index should only read the sentences that hold a word from "
            "the question, so its cost is the length of those postings",
        )

    if without[1] == len(questions):
        fail(
            f"dropping {DROPPED[0]!r} changes no answers",
            f"{DROPPED[0]!r} is in 81% of the sentences and is matching, so "
            f"removing it has to move some results",
        )

    if without[4] >= index[4]:
        fail(
            f"dropping {DROPPED[0]!r} scores {without[4]} against "
            f"{index[4]}, so it did not make the system worse",
            "removing a matching word lowers every overlap, so a fixed "
            "threshold admits fewer questions, which is the finding",
        )

    if not MEASURED.exists():
        fail(
            "there is no .work/index.tsv",
            "report each search: its cost, how often it agrees with the "
            "scan, and how many questions it handles correctly",
        )

    lines = read_lines(MEASURED)

    if lines and lines[0].split("\t")[:1] == ["search"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 6:
            fail(
                f"line {number} has {len(parts)} columns, and needs 6",
                "the search, comparisons, same answer, right, declined, "
                "correct",
            )

        try:
            yours[parts[0]] = tuple(int(part) for part in parts[1:6])
        except ValueError:
            fail(
                f"line {number} holds something that is not a whole number",
                "every column after the name is a count",
            )

    for label, numbers in expected.items():
        if label not in yours:
            fail(
                f"there is no row for {label!r}",
                f"report all three: {', '.join(expected)}",
            )

        if yours[label] != numbers:
            fail(
                f"for {label!r} you report {yours[label]} and running it "
                f"gives {numbers}",
                "the index cost is the total length of the postings it "
                "reads, counted once per word in the question",
            )

    print(f"PASS  the index agrees with the scan on all {len(questions)} "
          f"questions for {index[0] / scan[0]:.0%} of the work, and dropping "
          f"{DROPPED[0]!r} costs {index[4] - without[4]} questions")


if __name__ == "__main__":
    main()
