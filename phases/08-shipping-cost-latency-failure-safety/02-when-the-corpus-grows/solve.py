"""
Phase 8, lesson 2: when the corpus grows.

Lesson 1 found the search costs the whole corpus for every question, which is
fine at 217 sentences and not fine later. An inverted index fixes it, does
identical work, and returns identical answers.

Then it suggests an obvious second optimisation, which is six times faster
again and makes the system worse, for a reason that lives in a different
lesson entirely.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
MEASURED = HERE / ".work" / "index.tsv"

BAR = 3
COMMONEST = 10
DROPPED = ("the",)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def build_index(sentences):
    """Every word, and which sentences hold it."""
    postings = defaultdict(list)

    for index, sentence in enumerate(sentences):
        for word in set(sentence.split()):
            postings[word].append(index)

    return postings


def by_scanning(question, sentences, documents):
    """Read every sentence. The cost is the corpus, whatever the question."""
    words = set(question.split())
    cost = len(documents) * len(words)
    ranked = sorted(
        ((-len(words & document), index)
         for index, document in enumerate(documents)),
        key=lambda pair: (pair[0], pair[1]),
    )

    return cost, -ranked[0][0], sentences[ranked[0][1]]


def by_index(question, sentences, postings, skip=()):
    """Read only the sentences that hold a word from the question."""
    words = set(question.split()) - set(skip)
    cost = 0
    hits = Counter()

    for word in words:
        holding = postings.get(word, ())
        cost += len(holding)

        for index in holding:
            hits[index] += 1

    if not hits:
        return cost, 0, sentences[0]

    top = max(hits.values())
    winner = min(index for index, seen in hits.items() if seen == top)

    return cost, top, sentences[winner]


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    documents = [set(sentence.split()) for sentence in sentences]
    postings = build_index(sentences)

    answerable = [(line.split("\t")[0], line.split("\t")[2])
                  for line in read_lines(TASKS)[1:]
                  if line.split("\t")[1] == "search"]
    unanswerable = [line.split("\t")[0]
                    for line in read_lines(IMPOSSIBLE)[1:]]
    questions = [question for question, _ in answerable] + unanswerable

    holding = Counter({word: len(where) for word, where in postings.items()})

    print(f"A corpus of {len(sentences)} sentences holding "
          f"{len(postings)} distinct words.")
    print()
    print(f"  the {COMMONEST} commonest, and how many sentences hold each:")

    for word, total in holding.most_common(COMMONEST):
        print(f"    {word:10} {total:4} of {len(sentences)}  "
              f"{total / len(sentences):6.1%}")

    print()

    searches = {
        "scan every sentence":
            lambda question: by_scanning(question, sentences, documents),
        "an inverted index":
            lambda question: by_index(question, sentences, postings),
        f"the index without {DROPPED[0]!r}":
            lambda question: by_index(question, sentences, postings, DROPPED),
    }

    reference = {question: by_scanning(question, sentences, documents)[2]
                 for question in questions}

    rows = []

    for label, search in searches.items():
        cost = sum(search(question)[0] for question in questions)
        agreed = sum(1 for question in questions
                     if search(question)[2] == reference[question])
        right = sum(1 for question, answer in answerable
                    if search(question)[1] >= BAR
                    and search(question)[2] == answer)
        declined = sum(1 for question in unanswerable
                       if search(question)[1] < BAR)
        rows.append((label, cost, agreed, right, declined, right + declined))

    MEASURED.parent.mkdir(parents=True, exist_ok=True)

    with open(MEASURED, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("search\tcomparisons\tsame answer\tright\tdeclined\t"
                     "correct\n")

        for label, cost, agreed, right, declined, correct in rows:
            handle.write(f"{label}\t{cost}\t{agreed}\t{right}\t{declined}\t"
                         f"{correct}\n")

    scan_cost = rows[0][1]

    print(f"Three ways to find the same sentence, over {len(questions)} "
          f"questions:")
    print()
    print("  search                     comparisons   of the scan   same "
          "answer   correct")

    for label, cost, agreed, right, declined, correct in rows:
        print(f"  {label:25}  {cost:11}   {cost / scan_cost:11.1%}   "
              f"{agreed:2} of {len(questions):2}    {correct:2} of "
              f"{len(questions)}")

    print()

    index_row = rows[1]
    dropped_row = rows[2]

    print(f"The index reads {index_row[1]} where the scan reads {scan_cost}, "
          f"and returns the")
    print(f"same sentence for all {index_row[2]} questions. Nothing about the "
          f"system changed.")
    print()
    print(f"Dropping {DROPPED[0]!r} reads {dropped_row[1]}, which is "
          f"{index_row[1] / dropped_row[1]:.0f} times less again, and the "
          f"answers move")
    print(f"on {len(questions) - dropped_row[2]} questions. Right answers go "
          f"from {index_row[3]} to {dropped_row[3]} and refusals from "
          f"{index_row[4]} to {dropped_row[4]}.")
    print()

    before = [by_index(question, sentences, postings)[1]
              for question in questions]
    after = [by_index(question, sentences, postings, DROPPED)[1]
             for question in questions]
    fell = sum(1 for was, now in zip(before, after) if now < was)
    passed_before = sum(1 for score in before if score >= BAR)
    passed_after = sum(1 for score in after if score >= BAR)

    print(f"Why: {fell} of {len(questions)} questions lost a point of "
          f"overlap, because {DROPPED[0]!r} was")
    print(f"matching. The number clearing a threshold of {BAR} fell from "
          f"{passed_before} to {passed_after}.")
    print()
    print("The threshold was not touched. It was set in phase 6 and it now "
          "means something")
    print("different, because the scale underneath it moved.")


if __name__ == "__main__":
    main()
