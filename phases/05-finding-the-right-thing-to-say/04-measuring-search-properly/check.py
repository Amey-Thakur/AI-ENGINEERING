"""
Phase 5, lesson 4: the check.

It measures word matching itself, every way the lesson asks for, and compares
with what you reported.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"

CUTOFFS = (1, 3, 5, 10)
TOLERANCE = 1e-3


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

    places = []

    for question, answer in asked:
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )

        for place, (_, index) in enumerate(ranked, start=1):
            if sentences[index] == answer:
                places.append(place)
                break
        else:
            places.append(len(sentences))

    found = {cut: sum(1 for place in places if place <= cut) for cut in CUTOFFS}
    reciprocal = sum(1 / place for place in places) / len(places)

    return found, reciprocal, max(places), len(asked)


def main() -> None:
    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "for each method report how many answers were found by each "
            "cutoff, the average of one over the place, and the worst place",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if not lines:
        fail("results.tsv is empty", "report at least one method")

    header = lines[0].split("\t")

    if header[:1] != ["method"]:
        fail(
            "the first line of results.tsv is not a header starting with "
            "'method'",
            "name the columns, so the check knows which is which",
        )

    columns = {name.strip(): index for index, name in enumerate(header)}
    rows = {}

    for number, line in enumerate(lines[1:], start=2):
        parts = line.split("\t")

        if len(parts) != len(header):
            fail(
                f"line {number} has {len(parts)} columns and the header has "
                f"{len(header)}",
                "every row needs a value for every column",
            )

        rows[parts[0].strip()] = parts

    simplest = [name for name in rows if "shared" in name.lower()]

    if not simplest:
        fail(
            "there is no row for the method that counts shared words",
            "include it, named so it can be recognised",
        )

    parts = rows[simplest[0]]
    found, reciprocal, worst, asked = measure()

    for cut in CUTOFFS:
        name = f"found_by_{cut}"

        if name not in columns:
            fail(
                f"there is no {name} column",
                f"report how many answers were found by each of "
                f"{', '.join(str(value) for value in CUTOFFS)}",
            )

        try:
            reported = int(parts[columns[name]])
        except ValueError:
            fail(
                f"the {name} value for {simplest[0]!r} is not a whole number",
                "these columns are counts",
            )

        if reported != found[cut]:
            fail(
                f"for {simplest[0]!r} you report {reported} found by place "
                f"{cut}, and measuring gives {found[cut]}",
                "find where the right sentence sits in the full ranking, and "
                "count it as found when that place is at or before the cutoff",
            )

    if "mean_reciprocal_rank" in columns:
        try:
            reported = float(parts[columns["mean_reciprocal_rank"]])
        except ValueError:
            fail(
                "the mean_reciprocal_rank value is not a number",
                "it is the average of one divided by the place",
            )

        if abs(reported - reciprocal) > TOLERANCE:
            fail(
                f"you report an average of {reported:.4f}, and measuring gives "
                f"{reciprocal:.4f}",
                "average one over the place across every question, including "
                "the ones that came first",
            )

    print(f"PASS  shared words finds {found[1]} of {asked} first and all "
          f"{found[5]} by place 5, worst place {worst}")


if __name__ == "__main__":
    main()
