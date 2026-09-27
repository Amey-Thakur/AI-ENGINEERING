"""
Phase 5, lesson 1: the check.

It verifies independently that every answer really is a sentence in the corpus,
and that the model recalls almost none of them.

Generation is random, so the recall count is not required to be exactly zero.
It is required to be near it, because that is the finding, and any sensible
implementation lands in the same place.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"

# Above this and something has gone right, which would mean the lesson is
# wrong rather than that you are.
MOST_RECALLED = 3


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def main() -> None:
    corpus = {line.strip() for line in CORPUS.read_text(encoding="utf-8").splitlines()
              if line.strip()}

    asked = []
    for line in QUESTIONS.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            question, answer = line.rstrip("\n").split("\t")
            asked.append((question, answer))

    missing = [answer for _, answer in asked if answer not in corpus]

    if missing:
        fail(
            f"{len(missing)} answers are not sentences in the corpus, starting "
            f"with {missing[0]!r}",
            "the point of the lesson is that the model has read every answer, "
            "so each one must be a real corpus sentence",
        )

    if not RESULTS.exists():
        fail(
            "there is no .work/results.tsv",
            "report how many questions were asked, how many answers are in "
            "the corpus, and how many the model recalled",
        )

    lines = RESULTS.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["measure"]:
        lines = lines[1:]

    yours = {}
    for number, line in enumerate(lines, start=2):
        parts = line.split("\t")

        if len(parts) != 2:
            fail(
                f"line {number} has {len(parts)} columns, not 2",
                "each row is a name and a whole number",
            )

        try:
            yours[parts[0].strip()] = int(float(parts[1]))
        except ValueError:
            fail(
                f"line {number} has a value that is not a number: {parts[1]!r}",
                "every measure here is a count",
            )

    for name in ("questions", "answers_in_corpus", "recalled_by_model"):
        if name not in yours:
            fail(f"there is no row for {name}", "report all three measures")

    if yours["questions"] != len(asked):
        fail(
            f"you report {yours['questions']} questions, and the file has "
            f"{len(asked)}",
            "ask every question in questions.tsv",
        )

    if yours["answers_in_corpus"] != len(asked):
        fail(
            f"you report {yours['answers_in_corpus']} answers in the corpus, "
            f"and all {len(asked)} of them are",
            "check each answer against the corpus sentences directly",
        )

    if yours["recalled_by_model"] > MOST_RECALLED:
        fail(
            f"you report the model recalling {yours['recalled_by_model']} of "
            f"{len(asked)} answers, which is more than this model can do",
            "count a recall only when the reply contains most of the answer's "
            "own words, rather than any single word from it",
        )

    print(f"PASS  all {len(asked)} answers are in the corpus, and the model "
          f"recalled {yours['recalled_by_model']}")


if __name__ == "__main__":
    main()
