"""
Phase 7, lesson 4: the check.

It reruns the whole sweep on both sets of questions and insists on the shape
of the answer: that the threshold picked on the first set is still the best
on the second, and that the overall score falls anyway.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
FRESH = HERE / "fresh.tsv"
FRESH_IMPOSSIBLE = HERE / "fresh-impossible.tsv"
SWEEP = HERE / ".work" / "sweep.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BARS = range(0, 7)
CHOSEN = 3


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def make_scorer(sentences):
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


def calculate(question):
    words = question.split()

    if len(words) < 4:
        return REFUSED
    if not words[2].isdigit() or not words[-1].isdigit():
        return REFUSED
    if words[3] not in OPERATIONS:
        return REFUSED

    first, last, operation = int(words[2]), int(words[-1]), words[3]

    return {
        "times": str(first * last),
        "plus": str(first + last),
        "minus": str(first - last),
        "divided": str(first // last) if last else "",
    }[operation]


def count(question):
    words = question.split()

    if not words or not words[-1].isalpha():
        return REFUSED

    return str(len(words[-1]))


def route(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def make_agent(best, bar):
    def agent(question):
        picked = route(question)

        if picked != "search":
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found

        overlap, sentence = best(question)

        return sentence if overlap >= bar else REFUSED

    return agent


def behaved_correctly(given, answer, answerable):
    return given == answer if answerable else given is REFUSED


def score(agent, questions):
    return sum(1 for question, answer, answerable in questions
               if behaved_correctly(agent(question), answer, answerable))


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    best = make_scorer(sentences)

    chosen_on = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        chosen_on.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        chosen_on.append((line.split("\t")[0], None, False))

    fresh_answerable = [(line.split("\t")[0], line.split("\t")[1], True)
                        for line in read_lines(FRESH)[1:]]
    fresh_unanswerable = [(line.split("\t")[0], None, False)
                          for line in read_lines(FRESH_IMPOSSIBLE)[1:]]
    fresh = fresh_answerable + fresh_unanswerable

    expected = {}

    for bar in BARS:
        agent = make_agent(best, bar)
        expected[bar] = (score(agent, chosen_on), score(agent, fresh),
                         score(agent, fresh_answerable),
                         score(agent, fresh_unanswerable))

    if not SWEEP.exists():
        fail(
            "there is no .work/sweep.tsv",
            "for every threshold, report the score on the questions it was "
            "chosen on and on the ones written afterwards",
        )

    lines = read_lines(SWEEP)

    if lines and lines[0].split("\t")[:1] == ["bar"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 5:
            fail(
                f"line {number} has {len(parts)} columns, and needs 5",
                "the threshold, the score on the first set, the score on the "
                "fresh set, and the fresh set split into answerable and not",
            )

        try:
            yours[int(parts[0])] = tuple(int(part) for part in parts[1:5])
        except ValueError:
            fail(
                f"line {number} holds something that is not a whole number",
                "every column is a count",
            )

    for bar, numbers in expected.items():
        if bar not in yours:
            fail(
                f"there is no row for a threshold of {bar}",
                f"sweep every threshold from {BARS.start} to {BARS.stop - 1}",
            )

        if yours[bar] != numbers:
            fail(
                f"for a threshold of {bar} you report {yours[bar]} and "
                f"running it gives {numbers}",
                "a question with no answer counts as correct only when the "
                "agent declines it",
            )

    best_on_old = max(expected, key=lambda bar: (expected[bar][0], -bar))
    best_on_new = max(expected, key=lambda bar: (expected[bar][1], -bar))

    if best_on_old != CHOSEN:
        fail(
            f"the threshold that wins on the first set is {best_on_old} and "
            f"phase 6 used {CHOSEN}",
            "phase 6 picked the value that scored highest on those 48 "
            "questions, so the sweep has to agree with it",
        )

    if best_on_new != best_on_old:
        fail(
            f"the best threshold on the fresh questions is {best_on_new} and "
            f"on the first set it is {best_on_old}",
            "on this data the choice does survive, and the lesson is that "
            "the score does not",
        )

    fell = expected[CHOSEN][0] / len(chosen_on) - expected[CHOSEN][1] / len(fresh)

    if fell <= 0:
        fail(
            "the chosen threshold scores at least as well on the fresh "
            "questions as on the ones it was chosen on",
            "the fresh questions are harder, so the rate has to drop even "
            "though the choice was right",
        )

    declined_before = expected[CHOSEN][3] / len(fresh_unanswerable)

    print(f"PASS  bar {CHOSEN} wins on both sets, the rate falls "
          f"{fell:.1%}, and declining the unanswerable drops to "
          f"{declined_before:.0%}")


if __name__ == "__main__":
    main()
