"""
Phase 7, lesson 4: the test set you keep looking at.

Phase 6 set the search threshold to 3. That number came from trying every
value on the 48 questions and keeping whichever scored highest, which is the
thing every course tells you not to do.

So here is the same sweep, alongside twenty questions written afterwards. The
result is not the one the warning prepares you for, and the difference between
what did generalise and what did not is the lesson.

Run it with:  python solve.py
"""

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

    rows = []

    for bar in BARS:
        agent = make_agent(best, bar)
        rows.append((bar, score(agent, chosen_on), score(agent, fresh),
                     score(agent, fresh_answerable),
                     score(agent, fresh_unanswerable)))

    SWEEP.parent.mkdir(parents=True, exist_ok=True)

    with open(SWEEP, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("bar\tchosen on\tfresh\tfresh answerable\t"
                     "fresh unanswerable\n")

        for bar, old, new, answerable, unanswerable in rows:
            handle.write(f"{bar}\t{old}\t{new}\t{answerable}\t"
                         f"{unanswerable}\n")

    print(f"Every threshold, on the {len(chosen_on)} questions it was chosen "
          f"on and {len(fresh)} written afterwards.")
    print()
    print(f"  bar   the {len(chosen_on)} it was chosen on   "
          f"the {len(fresh)} written after")

    for bar, old, new, _, _ in rows:
        mark = "  <= phase 6 picked this" if bar == CHOSEN else ""
        print(f"  {bar:3}      {old:2} of {len(chosen_on)}  "
              f"{old / len(chosen_on):6.1%}         {new:2} of {len(fresh)}  "
              f"{new / len(fresh):6.1%}{mark}")

    print()

    on_old = max(rows, key=lambda row: (row[1], -row[0]))
    on_new = max(rows, key=lambda row: (row[2], -row[0]))

    print(f"  best on the {len(chosen_on)}:      bar {on_old[0]}, scoring "
          f"{on_old[1] / len(chosen_on):.1%} there and "
          f"{on_old[2] / len(fresh):.1%} on the fresh questions")
    print(f"  best on the fresh {len(fresh)}: bar {on_new[0]}, scoring "
          f"{on_new[2] / len(fresh):.1%}")
    print(f"  choosing on the test set cost {on_new[2] - on_old[2]} "
          f"questions")
    print()

    print("Where the fresh questions were lost, at the threshold that was "
          "chosen:")
    print()
    print("                      the 25 it was chosen on   the 20 written "
          "after")

    # Only the questions that reach search, so the two sets are the same
    # shape. The 23 arithmetic and counting questions have no counterpart in
    # the fresh set and never touch the threshold.
    chosen_answerable = [row for row in chosen_on
                         if row[2] and route(row[0]) == "search"]
    chosen_unanswerable = [row for row in chosen_on if not row[2]]
    agent = make_agent(best, CHOSEN)

    for label, old_rows, new_rows in (
        ("answered correctly", chosen_answerable, fresh_answerable),
        ("declined correctly", chosen_unanswerable, fresh_unanswerable),
    ):
        old_hit = score(agent, old_rows)
        new_hit = score(agent, new_rows)
        print(f"  {label:20}  {old_hit:2} of {len(old_rows):2}  "
              f"{old_hit / len(old_rows):6.1%}          {new_hit:2} of "
              f"{len(new_rows):2}  {new_hit / len(new_rows):6.1%}")


if __name__ == "__main__":
    main()
