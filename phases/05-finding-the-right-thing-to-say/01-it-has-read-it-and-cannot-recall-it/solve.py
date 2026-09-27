"""
Phase 5, lesson 1: it has read it and cannot recall it.

Trains the language model on the whole corpus, then asks it twenty questions
whose answers are sentences inside that very corpus, and measures how often it
produces the answer.

The gap this exposes is between storing something and being able to get it
back. The model has seen every one of these sentences. That turns out not to
be the same as knowing them.

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
TRIES = 5
SEED = 5

# What share of the answer's own words a reply must contain to count.
ENOUGH = 0.6

SHOW = 4


def read_corpus():
    with open(CORPUS, encoding="utf-8") as handle:
        return [line.split() for line in handle if line.strip()]


def read_questions():
    asked = []

    with open(QUESTIONS, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.rstrip("\n")
            if line:
                question, answer = line.split("\t")
                asked.append((question, answer))

    return asked


def count_pairs(sentences):
    following = defaultdict(Counter)

    for sentence in sentences:
        tokens = [START] + sentence + [END]

        for word, next_word in zip(tokens, tokens[1:]):
            following[word][next_word] += 1

    return following


def continue_from(word, following, generator):
    produced = []

    for _ in range(LONGEST):
        if word not in following:
            break

        choices = sorted(following[word])
        weights = [following[word][choice] for choice in choices]
        word = generator.choices(choices, weights=weights)[0]

        if word == END:
            break

        produced.append(word)

    return produced


def main() -> None:
    sentences = read_corpus()
    asked = read_questions()
    following = count_pairs(sentences)
    generator = random.Random(SEED)

    recalled = 0
    examples = []

    for question, answer in asked:
        # Start from the last word of the question the model has ever seen.
        known = [word for word in question.split() if word in following]
        seed = known[-1] if known else START

        wanted = set(answer.split()) - set(question.split())
        best = []
        matched = False

        for attempt in range(TRIES):
            produced = continue_from(seed, following, generator)

            if attempt == 0:
                best = produced

            overlap = len(wanted & set(produced)) / len(wanted)

            if overlap >= ENOUGH:
                matched = True

        recalled += matched
        examples.append((question, answer, seed, " ".join(best), matched))

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("measure\tvalue\n")
        handle.write(f"questions\t{len(asked)}\n")
        handle.write(f"answers_in_corpus\t{len(asked)}\n")
        handle.write(f"recalled_by_model\t{recalled}\n")

    words = sum(len(sentence) for sentence in sentences)

    print(f"The model has read all {len(sentences)} sentences, {words} words.")
    print(f"Every one of the {len(asked)} answers is a sentence inside that "
          f"corpus.")
    print()

    for question, answer, seed, produced, matched in examples[:SHOW]:
        print(f"  asked:  {question}")
        print(f"  model:  {seed} {produced}")
        print(f"  wanted: {answer}")
        print(f"  got it: {'yes' if matched else 'no'}")
        print()

    print(f"Answers recalled in {TRIES} attempts each: {recalled} of {len(asked)}")


if __name__ == "__main__":
    main()
