"""
Phase 5, lesson 5: retrieve, then answer.

Puts the search from this phase and the language model from the last one into
one pipeline, and measures the whole thing end to end against each piece alone.

The famous shape is retrieve, then generate. This measures whether the generate
step earns its place, which is a question the shape's popularity tends to
discourage anyone from asking.

Run it with:  python solve.py
"""

import random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
QUESTIONS = HERE / "questions.tsv"
RESULTS = HERE / ".work" / "results.tsv"

START = "<s>"
END = "</s>"

LONGEST = 14
SEED = 17
ENOUGH = 0.6
SHOW = 3


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


def count_pairs(documents):
    following = defaultdict(Counter)

    for document in documents:
        tokens = [START] + document + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1

    return following


def main() -> None:
    sentences = read_corpus()
    documents = [sentence.split() for sentence in sentences]
    asked = read_asked()
    following = count_pairs(documents)
    generator = random.Random(SEED)

    def retrieve(question):
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        return sentences[ranked[0][1]]

    def rephrase(sentence):
        """Continue from the retrieved sentence's first word, as a model would."""
        word = sentence.split()[0]
        produced = [word]

        for _ in range(LONGEST):
            if word not in following:
                break

            choices = sorted(following[word])
            weights = [following[word][choice] for choice in choices]
            word = generator.choices(choices, weights=weights)[0]

            if word == END:
                break

            produced.append(word)

        return " ".join(produced)

    def carries_answer(reply, question, answer):
        """Does the reply contain the part of the answer the question lacked."""
        wanted = set(answer.split()) - set(question.split())
        return len(wanted & set(reply.split())) / len(wanted) >= ENOUGH

    returned_right = 0
    generated_right = 0
    wrong_retrieval_wrong_answer = 0
    examples = []

    for question, answer in asked:
        found = retrieve(question)
        spoken = rephrase(found)

        exact = found == answer
        returned_right += exact
        good = carries_answer(spoken, question, answer)
        generated_right += good

        if not exact:
            wrong_retrieval_wrong_answer += 1

        examples.append((question, answer, found, spoken, exact, good))

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("system\tright\tasked\n")
        handle.write(f"model alone\t0\t{len(asked)}\n")
        handle.write(f"retrieve and return it\t{returned_right}\t{len(asked)}\n")
        handle.write(f"retrieve then generate\t{generated_right}\t{len(asked)}\n")

    print(f"  system                    right")
    print(f"  model alone, lesson 1      0 of {len(asked)}    0%")
    print(f"  retrieve and return it    {returned_right:2} of {len(asked)}   "
          f"{returned_right / len(asked):.0%}")
    print(f"  retrieve then generate    {generated_right:2} of {len(asked)}   "
          f"{generated_right / len(asked):.0%}")
    print()

    for question, answer, found, spoken, exact, good in examples[:SHOW]:
        print(f"  asked:      {question}")
        print(f"  retrieved:  {found}")
        print(f"              {'the right sentence' if exact else 'wrong sentence'}")
        print(f"  generated:  {spoken}")
        print(f"              {'carries the answer' if good else 'lost the answer'}")
        print()

    print(f"Questions where retrieval was right and generating lost it: "
          f"{sum(1 for _, _, _, _, exact, good in examples if exact and not good)}")
    print(f"Questions where retrieval was wrong, so nothing downstream could "
          f"help: {wrong_retrieval_wrong_answer}")


if __name__ == "__main__":
    main()
