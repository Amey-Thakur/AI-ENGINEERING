"""
Phase 5, lesson 3: finding it by meaning.

Searches the same corpus using the word vectors from phase 3 rather than by
matching words, and compares the two on two sets of questions: one worded like
the answers, and one deliberately worded differently.

The second set is the whole point. Keyword search is expected to do well when
the asker happens to use the document's words, and the interesting question is
what happens when they do not.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import log, sin, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
PARAPHRASES = HERE / "paraphrases.tsv"
RESULTS = HERE / ".work" / "results.tsv"

WINDOW = 4
DIMENSIONS = 24
ITERATIONS = 30
TOP = 3
COMMONEST = 25


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def read_asked(path):
    asked = []

    with open(path, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")
            if line:
                asked.append(tuple(line.split("\t")))

    return asked


def normalise(vector):
    size = sqrt(sum(value * value for value in vector))
    return [value / size for value in vector] if size else vector


def word_vectors(documents):
    """Phase 3 in one function: count, weight by surprise, squeeze."""
    together = Counter()
    word_total = Counter()
    context_total = Counter()
    grand = 0

    for document in documents:
        for position, word in enumerate(document):
            start = max(0, position - WINDOW)
            stop = min(len(document), position + WINDOW + 1)

            for other in range(start, stop):
                if other == position:
                    continue

                near = document[other]
                together[(word, near)] += 1
                word_total[word] += 1
                context_total[near] += 1
                grand += 1

    profiles = defaultdict(dict)

    for (word, near), count in together.items():
        expected = (word_total[word] * context_total[near]) / grand
        value = log(count / expected)

        if value > 0:
            profiles[word][near] = value

    words = sorted(profiles)
    contexts = sorted({near for profile in profiles.values() for near in profile})
    slot = {near: index for index, near in enumerate(contexts)}
    rows = {word: {slot[near]: value for near, value in profiles[word].items()}
            for word in words}

    axes = []
    for index in range(DIMENSIONS):
        current = normalise([sin(index * 7.0 + position * 0.7) + 0.1
                             for position in range(len(contexts))])

        for _ in range(ITERATIONS):
            carried = [0.0] * len(contexts)

            for row in rows.values():
                along = sum(value * current[position]
                            for position, value in row.items())

                if along:
                    for position, value in row.items():
                        carried[position] += value * along

            for earlier in axes:
                overlap = sum(a * b for a, b in zip(carried, earlier))
                carried = [a - overlap * b for a, b in zip(carried, earlier)]

            current = normalise(carried)

        axes.append(current)

    return {word: [sum(value * axis[position]
                       for position, value in rows[word].items())
                   for axis in axes]
            for word in words}


def closeness(first, second):
    left = sqrt(sum(value * value for value in first))
    right = sqrt(sum(value * value for value in second))

    if not left or not right:
        return 0.0

    return sum(a * b for a, b in zip(first, second)) / (left * right)


def main() -> None:
    sentences = read_corpus()
    documents = [sentence.split() for sentence in sentences]
    vectors = word_vectors(documents)

    frequency = Counter(word for document in documents for word in document)
    common = {word for word, _ in frequency.most_common(COMMONEST)}

    holding = Counter()
    for document in documents:
        holding.update(set(document))
    rare = {word: log(len(documents) / count) for word, count in holding.items()}

    empty = [0.0] * DIMENSIONS

    def as_vector(words, how):
        """A sentence as one vector, three different ways of averaging."""
        if how == "every word":
            chosen = [(1.0, vectors[word]) for word in words if word in vectors]
        elif how == "without the commonest":
            chosen = [(1.0, vectors[word]) for word in words
                      if word in vectors and word not in common]
        else:
            chosen = [(rare.get(word, 1.0), vectors[word]) for word in words
                      if word in vectors]

        if not chosen:
            return empty

        total = sum(weight for weight, _ in chosen)
        return [sum(weight * vector[index] for weight, vector in chosen) / total
                for index in range(DIMENSIONS)]

    def by_words(query, index):
        return len(set(query.split()) & set(documents[index]))

    def measure(asked, score):
        first = within = 0

        for question, answer in asked:
            ranked = sorted(
                ((-score(question, index), index)
                 for index in range(len(documents))),
                key=lambda pair: (pair[0], pair[1]),
            )
            order = [sentences[index] for _, index in ranked]

            first += order[0] == answer
            within += answer in order[:TOP]

        return first, within

    sets = (("worded like the answer", read_asked(QUESTIONS)),
            ("worded differently", read_asked(PARAPHRASES)))

    ways = ("every word", "without the commonest", "weighted by rarity")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    written = []

    for label, asked in sets:
        first, within = measure(asked, by_words)
        written.append((label, "matching words", first, within, len(asked)))

        for how in ways:
            prepared = [as_vector(document, how) for document in documents]

            def by_meaning(question, index, how=how, prepared=prepared):
                return closeness(as_vector(question.split(), how),
                                 prepared[index])

            first, within = measure(asked, by_meaning)
            written.append((label, f"meaning, {how}", first, within, len(asked)))

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("questions\tmethod\tfirst\twithin_three\tasked\n")

        for label, method, first, within, asked in written:
            handle.write(f"{label}\t{method}\t{first}\t{within}\t{asked}\n")

    shared = []
    for _, asked in sets:
        shared.append(sum(len(set(question.split()) & set(answer.split()))
                          for question, answer in asked) / len(asked))

    print(f"{len(sentences)} sentences, {len(vectors)} words with vectors")
    print()
    print(f"Words a question shares with its own answer:")
    print(f"  worded like the answer   {shared[0]:.1f}")
    print(f"  worded differently       {shared[1]:.1f}")
    print()

    for label, _ in sets:
        print(f"Questions {label}:")

        for entry in written:
            if entry[0] != label:
                continue

            _, method, first, within, asked = entry
            print(f"  {method:30} first {first:2} of {asked}   "
                  f"top {TOP} {within:2} of {asked}")

        print()


if __name__ == "__main__":
    main()
