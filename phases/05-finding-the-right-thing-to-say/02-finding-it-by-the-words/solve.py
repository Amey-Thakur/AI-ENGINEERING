"""
Phase 5, lesson 2: finding it by the words.

Searches the corpus for the sentence that answers each question, by matching
words, and measures how often the right sentence comes back first.

Five ways of scoring a match are compared, from the most obvious to the one
search engines actually use, because the obvious one turns out to win here and
that is worth knowing rather than guessing at.

Run it with:  python solve.py
"""

from collections import Counter
from math import log, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"

TOP = 3
SHOW = 4


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def read_questions():
    asked = []

    with open(QUESTIONS, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")
            if line:
                asked.append(tuple(line.split("\t")))

    return asked


def rarity(documents):
    """How rare each word is across the corpus: log of how few hold it."""
    holding = Counter()

    for document in documents:
        holding.update(set(document))

    total = len(documents)
    return {word: log(total / count) for word, count in holding.items()}


def scorers(documents, rare):
    average = sum(len(document) for document in documents) / len(documents)

    def shared(query, document):
        """The obvious one: how many words do they have in common."""
        return len(set(query) & set(document))

    def shared_per_length(query, document):
        """The same, divided by length, so long sentences do not win by size."""
        return len(set(query) & set(document)) / sqrt(len(document))

    def rare_words(query, document):
        """Rare shared words count for more than common ones."""
        return sum(rare[word] for word in set(query) & set(document))

    def rare_per_length(query, document):
        return (sum(rare[word] for word in set(query) & set(document))
                / sqrt(len(document)))

    def bm25(query, document, saturation=1.2, length_pull=0.75):
        """What search engines actually use.

        Rare words count for more, repeated words count for progressively
        less, and length is corrected against the average.
        """
        counted = Counter(document)
        total = 0.0

        for word in set(query):
            if word in counted:
                seen = counted[word]
                total += rare[word] * seen * (saturation + 1) / (
                    seen + saturation * (1 - length_pull
                                         + length_pull * len(document) / average))

        return total

    return (
        ("shared words", shared),
        ("shared / length", shared_per_length),
        ("rare words", rare_words),
        ("rare / length", rare_per_length),
        ("bm25", bm25),
    )


def search(query, sentences, documents, score):
    ranked = sorted(
        ((-score(query.split(), document), index)
         for index, document in enumerate(documents)),
        key=lambda pair: (pair[0], pair[1]),
    )

    return [sentences[index] for _, index in ranked]


def main() -> None:
    sentences = read_corpus()
    asked = read_questions()
    documents = [sentence.split() for sentence in sentences]
    rare = rarity(documents)

    measured = []

    for name, score in scorers(documents, rare):
        first = 0
        within = 0

        for question, answer in asked:
            ranked = search(question, sentences, documents, score)
            first += ranked[0] == answer
            within += answer in ranked[:TOP]

        measured.append((name, first, within))

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("method\tfirst\twithin_three\tasked\n")

        for name, first, within in measured:
            handle.write(f"{name}\t{first}\t{within}\t{len(asked)}\n")

    print(f"{len(sentences)} sentences to search, {len(asked)} questions")
    print()
    print(f"  method              right first    in the top {TOP}")

    for name, first, within in measured:
        print(f"  {name:18}  {first:2} of {len(asked)}   {first / len(asked):4.0%}"
              f"     {within:2} of {len(asked)}   {within / len(asked):4.0%}")

    best = max(measured, key=lambda entry: (entry[1], entry[2]))

    print()
    print(f"Best: {best[0]}")
    print()

    _, simplest = scorers(documents, rare)[0]

    for question, answer in asked[:SHOW]:
        ranked = search(question, sentences, documents, simplest)
        verdict = "correct" if ranked[0] == answer else f"wanted: {answer}"
        print(f"  asked:  {question}")
        print(f"  found:  {ranked[0]}")
        print(f"          {verdict}")
        print()


if __name__ == "__main__":
    main()
