"""
Phase 5, lesson 4: measuring search properly.

Scores the same three searches several different ways, and finds that the
answer to "which is best" depends on which question you asked.

Run it with:  python solve.py
"""

from collections import Counter
from math import log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"

CUTOFFS = (1, 3, 5, 10)


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def read_asked():
    asked = []

    with open(QUESTIONS, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")
            if line:
                asked.append(tuple(line.split("\t")))

    return asked


def main() -> None:
    sentences = read_corpus()
    documents = [sentence.split() for sentence in sentences]
    asked = read_asked()

    holding = Counter()
    for document in documents:
        holding.update(set(document))

    rare = {word: log(len(documents) / count) for word, count in holding.items()}
    average = sum(len(document) for document in documents) / len(documents)

    def shared(query, document):
        return len(set(query) & set(document))

    def rare_words(query, document):
        return sum(rare[word] for word in set(query) & set(document))

    def bm25(query, document, saturation=1.2, length_pull=0.75):
        counted = Counter(document)
        total = 0.0

        for word in set(query):
            if word in counted:
                seen = counted[word]
                total += rare[word] * seen * (saturation + 1) / (
                    seen + saturation * (1 - length_pull
                                         + length_pull * len(document) / average))

        return total

    def position_of(question, answer, score):
        """Where the right sentence came in the ranking, counting from 1."""
        ranked = sorted(
            ((-score(question.split(), document), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )

        for place, (_, index) in enumerate(ranked, start=1):
            if sentences[index] == answer:
                return place

        return len(sentences)

    methods = (("shared words", shared), ("rare words", rare_words),
               ("bm25", bm25))

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    measured = []

    for name, score in methods:
        places = [position_of(question, answer, score)
                  for question, answer in asked]

        found = {cut: sum(1 for place in places if place <= cut)
                 for cut in CUTOFFS}
        reciprocal = sum(1 / place for place in places) / len(places)

        measured.append((name, found, reciprocal, max(places), places))

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("method\t" + "\t".join(f"found_by_{cut}" for cut in CUTOFFS)
                     + "\tmean_reciprocal_rank\tworst_place\tasked\n")

        for name, found, reciprocal, worst, _ in measured:
            counts = "\t".join(str(found[cut]) for cut in CUTOFFS)
            handle.write(f"{name}\t{counts}\t{reciprocal:.4f}\t{worst}\t"
                         f"{len(asked)}\n")

    header = "  ".join(f"top {cut:<2}" for cut in CUTOFFS)
    print(f"  method          {header}   average 1/place   worst place")

    for name, found, reciprocal, worst, _ in measured:
        counts = "  ".join(f"{found[cut]:2} of {len(asked)}" for cut in CUTOFFS)
        print(f"  {name:14}  {counts}       {reciprocal:.3f}            {worst}")

    print()
    print("Where the right sentence actually came:")
    print()

    for name, _, _, _, places in measured:
        spread = Counter(places)
        described = ", ".join(f"place {place}: {spread[place]}"
                              for place in sorted(spread))
        print(f"  {name:14} {described}")


if __name__ == "__main__":
    main()
