"""
Phase 5, lesson 3: the check.

It verifies independently that the paraphrased questions really do avoid their
answers' words, measures word matching on both question sets itself, and
insists your figures agree.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
PARAPHRASES = HERE / "paraphrases.tsv"
RESULTS = HERE / ".work" / "results.tsv"

TOP = 3

# The paraphrases are only a fair test if they really are worded differently.
MOST_SHARED = 1.5


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_asked(path):
    asked = []

    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            asked.append(tuple(line.rstrip("\n").split("\t")))

    return asked


def main() -> None:
    sentences = [line.strip()
                 for line in CORPUS.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    documents = [sentence.split() for sentence in sentences]

    plain = read_asked(QUESTIONS)
    reworded = read_asked(PARAPHRASES)

    for name, asked in (("questions.tsv", plain), ("paraphrases.tsv", reworded)):
        missing = [answer for _, answer in asked if answer not in sentences]

        if missing:
            fail(
                f"{len(missing)} answers in {name} are not corpus sentences",
                "every answer has to be a sentence the search could return",
            )

    shared = sum(len(set(question.split()) & set(answer.split()))
                 for question, answer in reworded) / len(reworded)

    if shared > MOST_SHARED:
        fail(
            f"the paraphrased questions share {shared:.1f} words with their "
            f"answers on average, which is too many to be a fair test",
            "reword them to avoid the answer's own words",
        )

    def measure(asked):
        first = within = 0

        for question, answer in asked:
            words = set(question.split())
            ranked = sorted(
                ((-len(words & set(document)), index)
                 for index, document in enumerate(documents)),
                key=lambda pair: (pair[0], pair[1]),
            )
            order = [sentences[index] for _, index in ranked]

            first += order[0] == answer
            within += answer in order[:TOP]

        return first, within

    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report, for each question set and each method, how often the "
            "right sentence came first and how often it was in the top three",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["questions"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) < 4:
            fail(
                f"line {number} has {len(parts)} columns, and needs at least 4",
                "each row is the question set, the method, how many came "
                "first, and how many were in the top three",
            )

        try:
            yours[(parts[0].strip(), parts[1].strip())] = (int(parts[2]),
                                                           int(parts[3]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "both columns after the method are counts",
            )

    checks = (
        ("worded like the answer", plain),
        ("worded differently", reworded),
    )

    for label, asked in checks:
        rows = [key for key in yours
                if key[0] == label and "match" in key[1].lower()]

        if not rows:
            fail(
                f"there is no word matching row for the questions {label}",
                "measure word matching on both question sets",
            )

        first, within = measure(asked)

        if yours[rows[0]] != (first, within):
            fail(
                f"for word matching on the questions {label} you report "
                f"{yours[rows[0]]}, and measuring gives ({first}, {within})",
                "count shared words, and break ties by the order sentences "
                "appear in the file",
            )

    reworded_rows = [value for key, value in yours.items()
                     if key[0] == "worded differently"]

    if not reworded_rows:
        fail(
            "nothing is reported for the paraphrased questions",
            "measure every method on both sets",
        )

    if max(count for count, _ in reworded_rows) > 3:
        fail(
            "something scores well on the paraphrased questions, which this "
            "corpus should not support",
            "check the paraphrased questions are being matched against the "
            "corpus rather than against each other",
        )

    print(f"PASS  paraphrases share {shared:.1f} words with their answers, and "
          f"every method scores at most 3 of {len(reworded)} on them")


if __name__ == "__main__":
    main()
