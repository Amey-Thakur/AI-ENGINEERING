"""
Phase 7, lesson 3: the baseline you forgot.

A score means nothing on its own. It means something against the cheapest
thing that could have produced it, and the cheapest things here contain no
model, no search and in one case no code worth the name.

Two sets of baselines: the four trivial systems nobody builds, against the
phase 6 agent, and a coin, against every classifier in phases 1 to 3.

Run it with:  python solve.py
"""

from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
MESSAGES = HERE / "messages.tsv"
CLASSIFIERS = HERE / "classifiers.tsv"
BASELINES = HERE / ".work" / "baselines.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
HELD_BACK = 20


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


def build(best, sentences):
    """Every system, from the emptiest to the finished agent."""
    def always_decline(_):
        return REFUSED

    def the_first_sentence(_):
        return sentences[0]

    def always_search(question):
        return best(question)[1]

    def tools_only(question):
        picked = route(question)

        if picked == "search":
            return REFUSED

        return {"calculate": calculate, "count": count}[picked](question)

    def agent(bar):
        def run(question):
            picked = route(question)

            if picked != "search":
                found = {"calculate": calculate,
                         "count": count}[picked](question)

                if found is not REFUSED:
                    return found

            overlap, sentence = best(question)

            return sentence if overlap >= bar else REFUSED

        return run

    return (
        ("always decline", always_decline),
        ("always return the first sentence", the_first_sentence),
        ("always search, no routing", always_search),
        ("the tools only, decline the rest", tools_only),
        ("the confident agent", agent(0)),
        ("the cautious agent", agent(BAR)),
    )


def behaved_correctly(given, answer, answerable):
    return given == answer if answerable else given is REFUSED


def said_something_false(given, answer, answerable):
    if given is REFUSED:
        return False

    return not (answerable and given == answer)


def coin_flip_chance(wins, losses):
    total = wins + losses

    if total == 0:
        return 1.0

    fewer = min(wins, losses)

    return min(1.0, 2 * sum(comb(total, i)
                            for i in range(0, fewer + 1)) / 2 ** total)


def chance_a_coin_does_this_well(k, n):
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def paired(questions, left, right):
    ahead = behind = 0

    for question, answer, answerable in questions:
        mine = behaved_correctly(left(question), answer, answerable)
        theirs = behaved_correctly(right(question), answer, answerable)

        if mine and not theirs:
            ahead += 1
        elif theirs and not mine:
            behind += 1

    return ahead, behind, coin_flip_chance(ahead, behind)


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    best = make_scorer(sentences)

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    systems = build(best, sentences)
    rows = []

    for name, system in systems:
        correct = sum(1 for question, answer, answerable in questions
                      if behaved_correctly(system(question), answer,
                                           answerable))
        false = sum(1 for question, answer, answerable in questions
                    if said_something_false(system(question), answer,
                                            answerable))
        rows.append((name, correct, false, len(questions)))

    BASELINES.parent.mkdir(parents=True, exist_ok=True)

    with open(BASELINES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("system\tcorrect\tfalse\tasked\n")

        for name, correct, false, asked in rows:
            handle.write(f"{name}\t{correct}\t{false}\t{asked}\n")

    print(f"The phase 6 agent, and four systems that barely exist, over "
          f"{len(questions)} questions.")
    print()
    print("  system                              correct   said something false")

    for name, correct, false, asked in rows:
        print(f"  {name:34}  {correct:2} of {asked}   {false:2}")

    print()

    named = dict(systems)
    stripped = named["the tools only, decline the rest"]

    print("Against deleting the entire search half of the system:")

    for name in ("the confident agent", "the cautious agent"):
        ahead, behind, chance = paired(questions, named[name], stripped)
        print(f"  {name:22} wins {ahead:2}, loses {behind:2}, "
              f"chance alone does this {chance:6.1%} of the time")

    print()

    labels = [line.split("\t")[0] for line in read_lines(MESSAGES)[1:]]
    held_back = labels[-HELD_BACK:]

    # Sorted, so a tie between two equally common labels breaks the same way
    # on every machine rather than following the order a set happens to have.
    counts = {label: held_back.count(label) for label in sorted(set(held_back))}
    floor = max(counts.values())
    commonest = min(label for label, total in counts.items()
                    if total == floor)
    spread = ", ".join(f"{total} {label}" for label, total in counts.items())

    print(f"And the classifiers of phases 1 to 3, against saying "
          f"{commonest!r} every time.")
    print(f"The held back messages are {spread}, so that scores {floor} of "
          f"{len(held_back)}:")
    print()

    for line in read_lines(CLASSIFIERS)[1:]:
        what, right, asked = line.split("\t")
        right, asked = int(right), int(asked)
        chance = chance_a_coin_does_this_well(right, asked)
        verdict = "beats a coin" if chance < 0.05 else "does not beat a coin"
        print(f"  {what:42} {right:2} of {asked}  "
              f"{right - floor:+2}   {chance:6.2%}  {verdict}")


if __name__ == "__main__":
    main()
