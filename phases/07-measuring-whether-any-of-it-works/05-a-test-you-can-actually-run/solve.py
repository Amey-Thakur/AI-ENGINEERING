"""
Phase 7, lesson 5: a test you can actually run.

Four lessons of measurement, and none of it stops anybody breaking the system
on a Tuesday. This turns it into a file that fails a pull request.

The obvious tests do not work. Asserting the score is 40 breaks on every
improvement. Asserting the score is inside the interval from lesson 1 cannot
detect a change that moves a quarter of the questions, which is measured here
rather than argued.

What does work is recording what the system currently does, question by
question, and reporting what moved.

Run it with:  python solve.py
"""

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
HALVINGS = 40
SHOW = 4

RIGHT = "right"
WRONG = "wrong"
HELD_BACK = "held back"
DECLINED = "declined"

#: Better to decline than to be wrong, which is phase 6's pricing written down
#: as an order. Anything that moves a question up this list is an improvement.
PREFERENCE = {WRONG: 0, HELD_BACK: 1, RIGHT: 2, DECLINED: 2}


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


def drifted(agent, questions, frozen):
    """Which questions no longer do what the recorded file says they do."""
    moved = []

    for question, answer, answerable in questions:
        now = outcome(agent(question), answer, answerable)

        if now != frozen[question]:
            moved.append((question, frozen[question], now))

    worse = [row for row in moved if PREFERENCE[row[2]] < PREFERENCE[row[1]]]
    better = [row for row in moved if PREFERENCE[row[2]] > PREFERENCE[row[1]]]

    return moved, worse, better


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

    for line in read_lines(EXPECTATIONS)[1:]:
        question, expected = line.split("\t")
        frozen[question] = expected

    correct = sum(1 for expected in frozen.values()
                  if PREFERENCE[expected] == 2)
    low, high = interval(correct, len(questions))

    print(f"{len(frozen)} recorded outcomes, taken from the agent as it "
          f"stands.")
    print()

    for label in (RIGHT, WRONG, HELD_BACK, DECLINED):
        total = sum(1 for expected in frozen.values() if expected == label)
        print(f"  {label:12} {total:2}")

    print()
    print(f"That is {correct} of {len(questions)} handled correctly, and "
          f"lesson 1 puts the true rate")
    print(f"between {low:.1%} and {high:.1%}.")
    print()

    rows = []

    for bar in PROPOSED:
        agent = make_agent(best, bar)
        moved, worse, better = drifted(agent, questions, frozen)
        now = sum(1 for question, answer, answerable in questions
                  if PREFERENCE[outcome(agent(question), answer,
                                        answerable)] == 2)
        inside = low <= now / len(questions) <= high
        rows.append((bar, now, len(moved), len(worse), len(better), inside))

        print(f"A change that moves the threshold from {SHIPPED} to {bar}:")
        print(f"  the score goes from {correct} to {now}, a difference of "
              f"{now - correct}")
        print(f"  {len(moved)} of {len(questions)} questions changed: "
              f"{len(worse)} worse, {len(better)} better")
        print(f"  a test on the score alone would "
              f"{'pass, seeing nothing' if inside else 'fail'}")

        for question, was, now_at in moved[:SHOW]:
            print(f"    {was:10} -> {now_at:10}  {question!r}")

        print()

    DRIFT.parent.mkdir(parents=True, exist_ok=True)

    with open(DRIFT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("bar\tcorrect\tmoved\tworse\tbetter\tinside the band\n")

        for bar, now, moved, worse, better, inside in rows:
            handle.write(f"{bar}\t{now}\t{moved}\t{worse}\t{better}\t"
                         f"{'yes' if inside else 'no'}\n")

    shipped = make_agent(best, SHIPPED)
    moved, _, _ = drifted(shipped, questions, frozen)

    print(f"And the agent as it stands, against the same file: {len(moved)} "
          f"questions changed.")
    print("That is what a passing run looks like, and it is the only test "
          "here that is exact.")


if __name__ == "__main__":
    main()
