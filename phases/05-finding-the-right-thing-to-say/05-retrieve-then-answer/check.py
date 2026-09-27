"""
Phase 5, lesson 5: the check.

It measures retrieval itself, compares with what you reported, and insists the
comparison between the two pipelines is the right way round.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def measure():
    sentences = [line.strip()
                 for line in CORPUS.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    documents = [sentence.split() for sentence in sentences]

    asked = []
    for line in QUESTIONS.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            asked.append(tuple(line.rstrip("\n").split("\t")))

    right = 0

    for question, answer in asked:
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        right += sentences[ranked[0][1]] == answer

    return right, len(asked)


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report how many questions each of the three systems got right",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["system"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 2:
            fail(
                f"line {number} has {len(parts)} columns, and needs at least 2",
                "each row is the system and how many it got right",
            )

        try:
            yours[parts[0].strip().lower()] = int(parts[1])
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "the second column is a count",
            )

    right, asked = measure()

    returning = [name for name in yours
                 if "retrieve" in name and "generat" not in name]
    generating = [name for name in yours if "generat" in name]

    if not returning:
        fail(
            "there is no row for retrieving and returning the sentence",
            "measure the pipeline that stops after search",
        )

    if not generating:
        fail(
            "there is no row for retrieving and then generating",
            "measure the pipeline that continues into the model, so the two "
            "can be compared",
        )

    if yours[returning[0]] != right:
        fail(
            f"you report retrieval getting {yours[returning[0]]} of {asked} "
            f"right, and measuring gives {right}",
            "count a question right when the retrieved sentence is exactly "
            "the answer sentence",
        )

    if yours[generating[0]] > yours[returning[0]]:
        fail(
            f"you report generating ({yours[generating[0]]}) doing better than "
            f"returning the sentence ({yours[returning[0]]})",
            "with a model this weak the generate step cannot add anything: "
            "check the reply is scored against the answer rather than against "
            "the retrieved sentence",
        )

    lost = yours[returning[0]] - yours[generating[0]]

    print(f"PASS  retrieval {right} of {asked}, and the generate step loses "
          f"{lost} of them")


if __name__ == "__main__":
    main()
