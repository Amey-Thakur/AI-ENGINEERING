"""
Phase 8, lesson 3: when something fails.

Take the agent apart while it is running. A tool goes away. The corpus comes
back half loaded, then a tenth loaded, then empty.

The interesting result is not how much accuracy is lost. It is that the total
failure of the retrieval half costs seven questions out of forty-eight, stops
the system saying anything false at all, and would not trip an alarm on any
number anybody normally watches.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
FAILURES = HERE / ".work" / "failures.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


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


def unavailable(question):
    """A tool that is down. It refuses, which is the polite way to fail."""
    return REFUSED


def route(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def make_agent(sentences, arithmetic, letters):
    documents = [set(sentence.split()) for sentence in sentences]

    def agent(question):
        """Returns the answer, and the overlap if search was reached."""
        picked = route(question)

        if picked != "search":
            found = {"calculate": arithmetic, "count": letters}[picked](question)

            if found is not REFUSED:
                return found, None

        # The guard. Without it this line raises IndexError on an empty
        # corpus, which is the whole argument later in the lesson.
        if not documents:
            return REFUSED, 0

        words = set(question.split())
        ranked = sorted(
            ((-len(words & document), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap = -ranked[0][0]

        return (sentences[ranked[0][1]] if overlap >= BAR else REFUSED), overlap

    return agent


def main() -> None:
    corpus = [line.strip() for line in read_lines(CORPUS)]

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    cases = (
        ("everything works", corpus, calculate, count),
        ("calculate unavailable", corpus, unavailable, count),
        ("count unavailable", corpus, calculate, unavailable),
        ("both tools unavailable", corpus, unavailable, unavailable),
        ("half the corpus loaded", corpus[:len(corpus) // 2], calculate, count),
        ("a tenth of the corpus", corpus[:len(corpus) // 10], calculate, count),
        ("no corpus at all", [], calculate, count),
    )

    rows = []

    for label, sentences, arithmetic, letters in cases:
        agent = make_agent(sentences, arithmetic, letters)
        correct = wrong = declined = cleared = searches = 0
        overlaps = []

        for question, answer, answerable in questions:
            given, overlap = agent(question)

            if overlap is not None:
                searches += 1
                overlaps.append(overlap)
                cleared += overlap >= BAR

            if given is REFUSED:
                declined += 1
                correct += not answerable
            elif answerable and given == answer:
                correct += 1
            else:
                wrong += 1

        mean = sum(overlaps) / len(overlaps) if overlaps else 0.0
        rows.append((label, correct, wrong, declined, cleared, searches, mean))

    FAILURES.parent.mkdir(parents=True, exist_ok=True)

    with open(FAILURES, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("failure\tcorrect\twrong\tdeclined\tcleared the bar\n")

        for label, correct, wrong, declined, cleared, _, _ in rows:
            handle.write(f"{label}\t{correct}\t{wrong}\t{declined}\t"
                         f"{cleared}\n")

    print(f"The agent with pieces taken away, over the same "
          f"{len(questions)} questions.")
    print()
    print("  failure                   correct   said false   declined   "
          "mean overlap")

    for label, correct, wrong, declined, cleared, searches, mean in rows:
        print(f"  {label:24}  {correct:2} of {len(questions)}   {wrong:10}   "
              f"{declined:8}   {mean:12.2f}")

    print()

    working = rows[0]
    gone = rows[-1]

    print(f"Losing the corpus entirely takes {working[1]} correct to "
          f"{gone[1]}, a fall of {working[1] - gone[1]}.")
    print(f"It also takes false statements from {working[2]} to {gone[2]}.")
    print()
    print("  a monitor watching accuracy     sees "
          f"{(working[1] - gone[1]) / len(questions):.0%}, which is a quiet "
          f"Tuesday")
    print(f"  a monitor watching wrong answers sees an improvement")
    print(f"  the declined count             goes {working[3]} to {gone[3]}")
    print(f"  the mean overlap               goes {working[6]:.2f} to "
          f"{gone[6]:.2f}")
    print()

    print("What the scores look like as the corpus disappears:")

    for label, _, _, _, cleared, searches, mean in [rows[0]] + list(rows[4:]):
        print(f"  {label:24}  mean overlap {mean:.2f}, {cleared:2} of "
              f"{searches} searches clear the bar")

    print()
    print("That last column is the only one that noticed.")


if __name__ == "__main__":
    main()
