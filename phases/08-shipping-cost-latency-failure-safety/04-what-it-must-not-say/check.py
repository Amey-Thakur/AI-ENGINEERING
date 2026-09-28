"""
Phase 8, lesson 4: the check.

It rebuilds all three defences and insists on the result: that filtering the
question leaves private sentences reachable, that it refuses a legitimate
question on the way, and that removing the sentences from the index leaks
nothing and costs nothing.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
PRIVATE = HERE / "private.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
LEAKS = HERE / ".work" / "leaks.tsv"

REFUSED = None
BLOCKED = ("password", "key", "secret", "credential", "credentials",
           "private", "admin", "token")
BAR = 3

NONE = "no protection"
QUESTION = "refuse the question"
INDEX = "never index it"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def make_search(sentences):
    documents = [set(sentence.split()) for sentence in sentences]

    def search(question):
        if not documents:
            return REFUSED

        words = set(question.split())
        ranked = sorted(
            ((-len(words & document), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap = -ranked[0][0]

        return sentences[ranked[0][1]] if overlap >= BAR else REFUSED

    return search


def main() -> None:
    public = [line.strip() for line in read_lines(CORPUS)]
    private = [line.strip() for line in read_lines(PRIVATE)]
    secret = set(private)

    if not secret:
        fail(
            "private.txt is empty",
            "the lesson needs sentences that must never be returned",
        )

    overlap = secret & set(public)

    if overlap:
        fail(
            f"a private sentence is also in the public corpus: "
            f"{sorted(overlap)[0]!r}",
            "the two files have to be disjoint or leaking cannot be measured",
        )

    answerable = [(line.split("\t")[0], line.split("\t")[2])
                  for line in read_lines(TASKS)[1:]
                  if line.split("\t")[1] == "search"]
    unanswerable = [line.split("\t")[0]
                    for line in read_lines(IMPOSSIBLE)[1:]]
    questions = [(question, answer, True) for question, answer in answerable]
    questions += [(question, None, False) for question in unanswerable]

    leaky = make_search(public + private)
    clean = make_search(public)

    def filtered(question):
        if any(word in BLOCKED for word in question.split()):
            return REFUSED

        return leaky(question)

    systems = ((NONE, leaky), (QUESTION, filtered), (INDEX, clean))
    expected = {}

    for label, system in systems:
        leaked = correct = 0

        for question, answer, answerable_here in questions:
            given = system(question)
            leaked += given in secret

            if given is REFUSED:
                correct += not answerable_here
            elif answerable_here and given == answer:
                correct += 1

        expected[label] = (leaked, correct, len(questions))

    if expected[NONE][0] == 0:
        fail(
            "nothing leaks even with no protection at all",
            "a private sentence has to win at least one question on word "
            "overlap, or there is nothing here to defend against",
        )

    if expected[QUESTION][0] == 0:
        fail(
            "filtering the question stops every leak",
            "retrieval matches on words rather than intent, so a question "
            "with no blocked word in it should still be able to reach a "
            "private sentence",
        )

    if expected[QUESTION][0] >= expected[NONE][0]:
        fail(
            f"filtering the question stops none of the "
            f"{expected[NONE][0]} leaks",
            "one of the leaking questions does contain a blocked word, so "
            "the filter has to catch that one",
        )

    if expected[INDEX][0] != 0:
        fail(
            f"{expected[INDEX][0]} private sentences are returned even "
            f"though they were never indexed",
            "if a sentence is not in the corpus the search cannot reach it, "
            "so check which corpus is being searched",
        )

    if expected[INDEX][1] <= expected[QUESTION][1]:
        fail(
            f"not indexing scores {expected[INDEX][1]} and filtering the "
            f"question scores {expected[QUESTION][1]}",
            "the blocked word list refuses a legitimate question about "
            "rotating credentials, so it has to score lower",
        )

    wrongly_refused = [question for question, _, answerable_here in questions
                       if answerable_here
                       and any(word in BLOCKED for word in question.split())]

    if not wrongly_refused:
        fail(
            "the blocked word list refuses no legitimate question",
            "a real question about credentials contains a word on any list "
            "long enough to be useful, which is the cost of the approach",
        )

    if not LEAKS.exists():
        fail(
            "there is no .work/leaks.tsv",
            "for each defence, report how many private sentences were "
            "returned and how many questions were handled correctly",
        )

    lines = read_lines(LEAKS)

    if lines and lines[0].split("\t")[:1] == ["defence"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 4:
            fail(
                f"line {number} has {len(parts)} columns, and needs 4",
                "the defence, how many leaked, how many correct, how many "
                "asked",
            )

        try:
            yours[parts[0]] = tuple(int(part) for part in parts[1:4])
        except ValueError:
            fail(
                f"line {number} holds something that is not a whole number",
                "the three columns after the name are counts",
            )

    for label, numbers in expected.items():
        if label not in yours:
            fail(
                f"there is no row for {label!r}",
                f"report all three defences: {', '.join(expected)}",
            )

        if yours[label] != numbers:
            fail(
                f"for {label!r} you report {yours[label]} and running it "
                f"gives {numbers}",
                "a leak is any private sentence returned to any question, "
                "whether or not the question asked for one",
            )

    print(f"PASS  {expected[NONE][0]} leaks unprotected, "
          f"{expected[QUESTION][0]} still leaking once questions are "
          f"filtered and one good answer refused, "
          f"{expected[INDEX][0]} once the sentences are not indexed")


if __name__ == "__main__":
    main()
