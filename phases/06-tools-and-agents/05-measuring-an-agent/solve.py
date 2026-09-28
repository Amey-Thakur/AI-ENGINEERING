"""
Phase 6, lesson 5: measuring an agent.

The whole phase assembled: a rule that picks a tool, tools that can refuse,
a search that can decline, and a loop with a budget. Three versions of it,
over all 48 questions, scored on six numbers instead of one.

Two of the three versions cannot be ranked without a number that is nowhere
in the data.

Run it with:  python solve.py
"""

from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
SCORECARD = HERE / ".work" / "scorecard.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
CAP = 6

RIGHT = "right"
WRONG = "wrong"
HELD_BACK = "declined, answer existed"
DECLINED = "declined, no answer existed"


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


def shorten(question):
    words = question.split()

    return " ".join(words[1:]) if len(words) > 1 else ""


def make_agent(best, bar, retry):
    """The phase, assembled. Returns the answer and the number of calls made."""
    def search(question):
        overlap, sentence = best(question)

        return sentence if overlap >= bar else REFUSED

    def agent(question):
        calls = 0
        picked = route(question)

        if picked != "search":
            calls += 1
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found, calls

        asked = question

        for _ in range(CAP if retry else 1):
            calls += 1
            found = search(asked)

            if found is not REFUSED:
                return found, calls

            asked = shorten(asked)

            if not asked:
                break

        return REFUSED, calls

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

    systems = (
        ("answer whatever wins", 0, False),
        (f"decline below overlap {BAR}", BAR, False),
        (f"decline, then retry, cap {CAP}", BAR, True),
    )

    rows = []

    for label, bar, retry in systems:
        agent = make_agent(best, bar, retry)
        tally = {RIGHT: 0, WRONG: 0, HELD_BACK: 0, DECLINED: 0}
        calls = 0

        for question, answer, answerable in questions:
            given, made = agent(question)
            calls += made
            tally[outcome(given, answer, answerable)] += 1

        rows.append((label, tally[RIGHT], tally[WRONG], tally[HELD_BACK],
                     tally[DECLINED], tally[RIGHT] + tally[DECLINED], calls))

    SCORECARD.parent.mkdir(parents=True, exist_ok=True)

    with open(SCORECARD, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("system\tright\twrong\theld back\tdeclined\t"
                     "behaved correctly\tcalls\n")

        for row in rows:
            handle.write("\t".join(str(part) for part in row) + "\n")

    print(f"The same agent, three ways, over all {len(questions)} questions.")
    print()
    print("  system                          right  wrong  held  decl  "
          "correct  calls")

    for label, right, wrong, held, declined, correct, calls in rows:
        print(f"  {label:30}  {right:5}  {wrong:5}  {held:4}  {declined:4}  "
              f"{correct:7}  {calls:5}")

    print()
    print("  right     answered correctly")
    print("  wrong     answered confidently and incorrectly")
    print("  held      declined a question that did have an answer")
    print("  decl      declined a question that had none, which is correct")
    print()

    first, second, third = rows

    print("Which of the first two is better depends on what you report:")
    print(f"  questions it got right          {first[1]} against {second[1]}, "
          f"the first one wins")
    print(f"  questions it handled correctly  {first[5]} against {second[5]}, "
          f"the second one wins")
    print(f"  confident wrong answers         {first[2]} against {second[2]}, "
          f"the second one wins")
    print(f"  tool calls                      {first[6]} against {second[6]}, "
          f"no difference")
    print()

    gained = first[1] - second[1]
    avoided = first[2] - second[2]
    breakeven = Fraction(gained, avoided)

    print(f"Score a right answer as 1 and a wrong answer as minus k, and "
          f"declining as 0:")
    print(f"  the first scores  {first[1]} - {first[2]}k")
    print(f"  the second scores {second[1]} - {second[2]}k")
    print(f"  they are equal at k = {breakeven}")
    print()

    for k in (Fraction(0), Fraction(1, 4), breakeven, Fraction(1),
              Fraction(3)):
        left = first[1] - first[2] * k
        right_side = second[1] - second[2] * k
        winner = ("the first" if left > right_side
                  else "the second" if right_side > left else "a tie")
        print(f"  a wrong answer costs {str(k):4} of a right one:  "
              f"{float(left):6.2f} against {float(right_side):6.2f}, "
              f"{winner}")

    print()
    print(f"The third is the second with a retry bolted on. Identical on all "
          f"four outcomes,")
    print(f"and {third[6]} calls against {second[6]}. Only the cost column "
          f"can see it.")


if __name__ == "__main__":
    main()
