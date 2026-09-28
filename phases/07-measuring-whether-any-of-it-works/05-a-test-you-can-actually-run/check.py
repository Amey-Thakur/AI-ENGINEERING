"""
Phase 7, lesson 5: the check.

This one is the thing the lesson is about. It runs the agent against
expectations.tsv and fails if any question has moved, naming it, which is
exactly the test being taught.

It then confirms the two claims that justify writing the test that way: that
the shipped agent matches the file exactly, and that both proposed changes
slip through a test on the score alone.

Run it with:  python check.py
"""

import sys
from math import exp, lgamma, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
EXPECTATIONS = HERE / "expectations.tsv"
DRIFT = HERE / ".work" / "drift.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
SHIPPED = 3
PROPOSED = (2, 4)
ALPHA = 0.05
HALVINGS = 60
NAME_AT_MOST = 5

RIGHT = "right"
WRONG = "wrong"
HELD_BACK = "held back"
DECLINED = "declined"

PREFERENCE = {WRONG: 0, HELD_BACK: 1, RIGHT: 2, DECLINED: 2}


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def log_choose(n, k):
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def chance_of_at_least(k, n, rate):
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(k, n + 1))


def chance_of_at_most(k, n, rate):
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(0, k + 1))


def pin_down(rising, target):
    low, high = 0.0, 1.0

    for _ in range(HALVINGS):
        middle = (low + high) / 2

        if rising(middle) < target:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def interval(k, n):
    low = 0.0 if k == 0 else pin_down(
        lambda rate: chance_of_at_least(k, n, rate), ALPHA / 2)
    high = 1.0 if k == n else pin_down(
        lambda rate: -chance_of_at_most(k, n, rate), -ALPHA / 2)

    return low, high


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


def outcome(given, answer, answerable):
    if given is REFUSED:
        return HELD_BACK if answerable else DECLINED
    if answerable and given == answer:
        return RIGHT

    return WRONG


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    best = make_scorer(sentences)

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    frozen = {}

    for number, line in enumerate(read_lines(EXPECTATIONS)[1:], start=2):
        parts = line.split("\t")

        if len(parts) < 2:
            fail(
                f"expectations.tsv line {number} has {len(parts)} columns",
                "each row is the question and the outcome it currently has",
            )

        if parts[1] not in PREFERENCE:
            fail(
                f"expectations.tsv line {number} records {parts[1]!r}",
                f"the outcome is one of: {', '.join(sorted(PREFERENCE))}",
            )

        frozen[parts[0]] = parts[1]

    asked = {question for question, _, _ in questions}

    if set(frozen) != asked:
        missing = sorted(asked - set(frozen))
        extra = sorted(set(frozen) - asked)
        fail(
            f"expectations.tsv covers {len(frozen)} questions and there are "
            f"{len(asked)}",
            (f"not recorded: {missing[0]!r}" if missing
             else f"recorded but never asked: {extra[0]!r}"),
        )

    # This is the regression test. Everything else in the file is a claim
    # about why it is written this way.
    shipped = make_agent(best, SHIPPED)
    moved = []

    for question, answer, answerable in questions:
        now = outcome(shipped(question), answer, answerable)

        if now != frozen[question]:
            moved.append((question, frozen[question], now))

    if moved:
        print(f"FAIL  {len(moved)} of {len(questions)} questions no longer do "
              f"what expectations.tsv records")

        for question, was, now in moved[:NAME_AT_MOST]:
            print(f"      {was} -> {now}  {question!r}")

        if len(moved) > NAME_AT_MOST:
            print(f"      and {len(moved) - NAME_AT_MOST} more")

        print("      if the change was deliberate, rerun solve.py and commit "
              "the new file alongside it")
        sys.exit(1)

    correct = sum(1 for expected in frozen.values()
                  if PREFERENCE[expected] == 2)
    low, high = interval(correct, len(questions))

    expected_rows = {}

    for bar in PROPOSED:
        agent = make_agent(best, bar)
        changed = worse = better = 0
        now = 0

        for question, answer, answerable in questions:
            after = outcome(agent(question), answer, answerable)
            now += PREFERENCE[after] == 2

            if after != frozen[question]:
                changed += 1
                worse += PREFERENCE[after] < PREFERENCE[frozen[question]]
                better += PREFERENCE[after] > PREFERENCE[frozen[question]]

        inside = low <= now / len(questions) <= high
        expected_rows[bar] = (now, changed, worse, better,
                              "yes" if inside else "no")

        if not inside:
            fail(
                f"moving the bar to {bar} scores {now} of {len(questions)}, "
                f"outside the band {low:.1%} to {high:.1%}",
                "the lesson rests on both changes slipping through a test on "
                "the score, so check how the band is computed",
            )

    if not DRIFT.exists():
        fail(
            "there is no .work/drift.tsv",
            "for each proposed change, report the new score, how many "
            "questions moved, and how many moved each way",
        )

    lines = read_lines(DRIFT)

    if lines and lines[0].split("\t")[:1] == ["bar"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 6:
            fail(
                f"drift.tsv line {number} has {len(parts)} columns, and "
                f"needs 6",
                "the bar, the score, how many moved, how many worse, how "
                "many better, and whether the score stayed inside the band",
            )

        try:
            yours[int(parts[0])] = (int(parts[1]), int(parts[2]),
                                    int(parts[3]), int(parts[4]),
                                    parts[5].lower())
        except ValueError:
            fail(
                f"drift.tsv line {number} holds something unreadable",
                "five numbers after the bar, then yes or no",
            )

    for bar, numbers in expected_rows.items():
        if bar not in yours:
            fail(
                f"there is no row for a bar of {bar}",
                f"report both proposed changes: {', '.join(map(str, PROPOSED))}",
            )

        if yours[bar] != numbers:
            fail(
                f"for a bar of {bar} you report {yours[bar]} and running it "
                f"gives {numbers}",
                "a question counts as moved when its outcome differs from "
                "the recorded one, and worse or better by where the two "
                "outcomes sit in the ordering",
            )

    print(f"PASS  all {len(questions)} questions match the recorded "
          f"outcomes, and both proposed changes move "
          f"{expected_rows[PROPOSED[0]][1]} questions while staying inside "
          f"the band")


if __name__ == "__main__":
    main()
