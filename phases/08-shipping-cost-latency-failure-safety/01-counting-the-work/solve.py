"""
Phase 8, lesson 1: counting the work.

Nothing in this course has cost anything yet. The corpus is 217 sentences and
every lesson finishes in under a second, which is exactly the condition under
which cost gets ignored until it arrives all at once.

So count it. Not in seconds, which depend on the machine, but in the work the
system actually does: tool calls, sentences scanned, and words compared.

The distribution is the interesting part, and the average turns out to
describe a question that does not exist.

Run it with:  python solve.py
"""

from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
SPEND = HERE / ".work" / "spend.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
GROWTH = (1, 10, 100, 1000)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


class Meter:
    """What one question cost, in units that do not depend on the machine."""

    def __init__(self):
        self.calls = 0
        self.sentences = 0
        self.comparisons = 0


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


def make_search(sentences):
    documents = [sentence.split() for sentence in sentences]

    def search(question, meter):
        words = set(question.split())

        # Every sentence, every time. There is no index, so the cost of one
        # question is the size of the whole corpus.
        meter.sentences += len(documents)
        meter.comparisons += len(documents) * len(words)

        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap, index = ranked[0]

        return -overlap, sentences[index]

    return search


def make_agent(search):
    def agent(question):
        meter = Meter()
        picked = route(question)

        if picked != "search":
            meter.calls += 1
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found, meter

        meter.calls += 1
        overlap, sentence = search(question, meter)

        return (sentence if overlap >= BAR else REFUSED), meter

    return agent


def percentile(ordered, share):
    return ordered[min(len(ordered) - 1,
                       int(round(share / 100 * (len(ordered) - 1))))]


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    agent = make_agent(make_search(sentences))

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    measured = []

    for question, answer, answerable in questions:
        given, meter = agent(question)
        measured.append((question, given is REFUSED, meter.comparisons,
                         meter.calls))

    spread = Counter(comparisons for _, _, comparisons, _ in measured)

    SPEND.parent.mkdir(parents=True, exist_ok=True)

    with open(SPEND, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("comparisons\tquestions\n")

        for comparisons in sorted(spread):
            handle.write(f"{comparisons}\t{spread[comparisons]}\n")

    words_in_corpus = sum(len(sentence.split()) for sentence in sentences)
    costs = sorted(comparisons for _, _, comparisons, _ in measured)
    total = sum(costs)
    mean = total / len(costs)

    print(f"A corpus of {len(sentences)} sentences and {words_in_corpus} "
          f"words, asked {len(questions)} questions.")
    print()
    print(f"  cheapest question   {costs[0]:6} word comparisons")
    print(f"  median              {percentile(costs, 50):6}")
    print(f"  mean                {mean:6.0f}")
    print(f"  dearest             {costs[-1]:6}")
    print(f"  everything          {total:6}")
    print()

    print("Every cost that occurs, and how many questions have it:")

    for comparisons in sorted(spread):
        many = spread[comparisons]
        print(f"  {comparisons:6} comparisons   {many:2} "
              f"question{'' if many == 1 else 's'}")

    print()

    dearer = [cost for cost in costs if cost > 0]
    nearest = min(dearer)
    between = sum(1 for cost in costs if 0 < cost < nearest)

    print(f"The mean is {mean:.0f}. The cheapest question that does any work "
          f"at all costs {nearest}.")
    print(f"Questions costing between 1 and {nearest - 1}: {between}.")
    print()

    free = [row for row in measured if row[2] == 0]
    paid = [row for row in measured if row[2] > 0]

    print(f"  {len(free):2} questions are answered by a tool and never reach "
          f"search, costing nothing")
    print(f"  {len(paid):2} reach search and cost "
          f"{sum(row[2] for row in paid) / len(paid):.0f} each on average")
    print()

    declined = [row for row in measured if row[1]]
    answered = [row for row in measured if not row[1]]

    print(f"  answered {len(answered):2}: "
          f"{sum(row[2] for row in answered) / len(answered):5.0f} "
          f"comparisons on average")
    print(f"  declined {len(declined):2}: "
          f"{sum(row[2] for row in declined) / len(declined):5.0f} "
          f"comparisons on average")
    print("  the threshold buys honesty and saves nothing, because a "
          "question is searched")
    print("  in full before it is refused.")
    print()

    print(f"And the same {len(questions)} questions against a larger corpus:")

    for factor in GROWTH:
        print(f"  {factor:5} times the sentences "
              f"({len(sentences) * factor:7}): "
              f"{total * factor:11} comparisons")


if __name__ == "__main__":
    main()
