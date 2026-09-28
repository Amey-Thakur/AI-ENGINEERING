"""
Phase 6, lesson 4: a loop that can stop.

Everything so far answered every question it was given. This adds ten
questions with no answer anywhere in the corpus, and a loop that is allowed
to try again, give up, or run out of budget.

Two of the three measurements here are negative. The retrying is worthless
and provably so. The giving up is worth more than lesson 3 was able to see.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
STOPPING = HERE / ".work" / "stopping.tsv"

REFUSED = None
BAR = 3
CAP = 6

ANSWERED = "answered"
OUT_OF_MOVES = "ran out of rewrites"
OUT_OF_BUDGET = "hit the limit"


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle if line.strip()]


def read_corpus():
    return [line.strip() for line in read_lines(CORPUS)]


def read_answerable():
    rows = []

    for line in read_lines(TASKS)[1:]:
        question, tool, answer = line.split("\t")

        if tool == "search":
            rows.append((question, answer))

    return rows


def read_impossible():
    return [line.split("\t")[0] for line in read_lines(IMPOSSIBLE)[1:]]


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


def shorten(question):
    """The rewrite: drop the leading word and ask again."""
    words = question.split()

    return " ".join(words[1:]) if len(words) > 1 else ""


def main() -> None:
    sentences = read_corpus()
    answerable = read_answerable()
    impossible = read_impossible()
    best = make_scorer(sentences)

    def anything(question):
        return best(question)[1]

    def only_if_confident(question):
        overlap, sentence = best(question)

        return sentence if overlap >= BAR else REFUSED

    def loop(question, cap):
        """Try, rewrite, try again. Three ways out, and all of them exist."""
        asked = question

        for step in range(1, cap + 1):
            found = only_if_confident(asked)

            if found is not REFUSED:
                return found, step, ANSWERED

            asked = shorten(asked)

            if not asked:
                return REFUSED, step, OUT_OF_MOVES

        return REFUSED, cap, OUT_OF_BUDGET

    def in_a_loop(question):
        return loop(question, CAP)[0]

    systems = (
        ("answer whatever wins", anything),
        (f"only if overlap is {BAR} or more", only_if_confident),
        (f"loop, rewrite on refusal, cap {CAP}", in_a_loop),
    )

    rows = []

    for label, system in systems:
        right = sum(1 for question, answer in answerable
                    if system(question) == answer)
        declined = sum(1 for question, _ in answerable
                       if system(question) is REFUSED)
        rows.append((label, f"{len(answerable)} answerable", right, declined,
                     len(answerable)))

    for label, system in systems:
        declined = sum(1 for question in impossible
                       if system(question) is REFUSED)
        rows.append((label, f"{len(impossible)} unanswerable", declined,
                     declined, len(impossible)))

    STOPPING.parent.mkdir(parents=True, exist_ok=True)

    with open(STOPPING, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("system\tquestions\tcorrect\tdeclined\tasked\n")

        for label, which, correct, declined, asked in rows:
            handle.write(f"{label}\t{which}\t{correct}\t{declined}\t{asked}\n")

    print("Correct behaviour is answering an answerable question and "
          "declining an unanswerable one.")
    print()
    print("  system                            questions          correct   declined")

    for label, which, correct, declined, asked in rows:
        print(f"  {label:32}  {which:16}  {correct:2} of {asked:2}  {declined:2}")

    print()

    for label, _ in systems:
        total = sum(correct for row_label, _, correct, _, _ in rows
                    if row_label == label)
        asked = sum(asked for row_label, _, _, _, asked in rows
                    if row_label == label)
        print(f"  {label:32}  {total} of {asked} across both sets")

    print()
    print("Raising the cap, on the questions that can be answered:")

    for cap in (1, 2, 3, 4, 6):
        right = 0
        calls = 0
        capped = 0

        for question, answer in answerable:
            found, steps, why = loop(question, cap)
            right += found == answer
            calls += steps
            capped += why == OUT_OF_BUDGET

        print(f"  cap {cap}: {right} of {len(answerable)} right, "
              f"{calls} searches, {capped} questions stopped by the cap")

    print()
    print("Every way the loop ended, on all "
          f"{len(answerable) + len(impossible)} questions:")

    endings = {}

    for question in [question for question, _ in answerable] + impossible:
        _, _, why = loop(question, CAP)
        endings[why] = endings.get(why, 0) + 1

    for why in (ANSWERED, OUT_OF_MOVES, OUT_OF_BUDGET):
        print(f"  {why:20} {endings.get(why, 0):2}")

    print()

    rewrites = 0
    rose = 0

    for question in [question for question, _ in answerable] + impossible:
        asked = question

        while True:
            shorter = shorten(asked)

            if not shorter:
                break

            rewrites += 1

            if best(shorter)[0] > best(asked)[0]:
                rose += 1

            asked = shorter

    print(f"Across {rewrites} rewrites, the best overlap rose {rose} times.")
    print("Dropping a word can only shrink the overlap with every sentence, "
          "so a question")
    print(f"below the bar of {BAR} can never get above it by being shortened.")


if __name__ == "__main__":
    main()
