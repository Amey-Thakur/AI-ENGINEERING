"""
Phase 7, lesson 2: is the difference real.

Phase 6 finished with two agents, 35 correct against 40, and said the choice
between them was a business decision. Lesson 1 said a score of that size on
48 questions carries about twenty points of uncertainty.

Both were run on the same 48 questions, which allows a much sharper question
than either: not how good is each one, but on which questions do they
actually disagree. There turn out to be eleven, and the answer depends
entirely on which outcome you are counting.

Run it with:  python solve.py
"""

from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
DISAGREEMENTS = HERE / ".work" / "disagreements.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
SHOW = 3


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
    if answerable:
        return given == answer

    return given is REFUSED


def said_something_false(given, answer, answerable):
    if given is REFUSED:
        return False

    return not (answerable and given == answer)


def coin_flip_chance(wins, losses):
    """If the disagreements were coin flips, how often is it this lopsided."""
    total = wins + losses

    if total == 0:
        return 1.0

    fewer = min(wins, losses)
    one_side = sum(comb(total, i) for i in range(0, fewer + 1)) / 2 ** total

    return min(1.0, 2 * one_side)


def compare(questions, first, second, measure):
    both = neither = 0
    only_first = []
    only_second = []

    for question, answer, answerable in questions:
        left = measure(first(question), answer, answerable)
        right = measure(second(question), answer, answerable)

        if left and not right:
            only_first.append(question)
        elif right and not left:
            only_second.append(question)
        elif left:
            both += 1
        else:
            neither += 1

    return both, neither, only_first, only_second


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    best = make_scorer(sentences)

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    confident = make_agent(best, 0)
    cautious = make_agent(best, BAR)

    outcomes = (
        ("behaved correctly", behaved_correctly),
        ("said something false", said_something_false),
    )

    rows = []
    detail = {}

    for name, measure in outcomes:
        both, neither, only_first, only_second = compare(
            questions, confident, cautious, measure)
        chance = coin_flip_chance(len(only_first), len(only_second))
        rows.append((name, both + len(only_first), both + len(only_second),
                     len(only_first), len(only_second), chance))
        detail[name] = (only_first, only_second, both, neither)

    DISAGREEMENTS.parent.mkdir(parents=True, exist_ok=True)

    with open(DISAGREEMENTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("outcome\tconfident\tcautious\tonly confident\t"
                     "only cautious\tchance\n")

        for name, left, right, first_only, second_only, chance in rows:
            handle.write(f"{name}\t{left}\t{right}\t{first_only}\t"
                         f"{second_only}\t{chance:.4f}\n")

    print(f"Two agents, the same {len(questions)} questions, two outcomes "
          f"worth counting.")
    print()

    for name, left, right, first_only, second_only, chance in rows:
        only_first, only_second, both, neither = detail[name]

        print(f"  {name}")
        print(f"    confident {left:2}, cautious {right:2}")
        print(f"    they agree on {both + neither} of {len(questions)} "
              f"questions and disagree on {first_only + second_only}")
        print(f"    {first_only:2} only the confident one, "
              f"{second_only:2} only the cautious one")
        print(f"    if those were coin flips, this lopsided or worse "
              f"{chance:.1%} of the time")

        for question in only_first[:SHOW]:
            print(f"      only confident: {question!r}")

        for question in only_second[:SHOW]:
            print(f"      only cautious:  {question!r}")

        print()

    correct_row, false_row = rows

    print(f"The gap in {correct_row[0]} is {abs(correct_row[1] - correct_row[2])} "
          f"questions and could easily be chance.")
    print(f"The gap in {false_row[0]} is {abs(false_row[1] - false_row[2])} "
          f"questions and could not.")
    print()
    print("Both gaps come from one behaviour: answering a question the "
          "evidence was weak for.")
    print(f"It won the confident agent {correct_row[3]} questions and cost it "
          f"{false_row[3]} false statements,")
    print("and the cautious agent never once answered something the "
          "confident one declined.")


if __name__ == "__main__":
    main()
