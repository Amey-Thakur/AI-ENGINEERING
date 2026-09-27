"""
Lesson 1: words into numbers.

Reads the messages, counts how often each word appears in each kind, and writes
the table out. Then it reports which words lean hardest one way or the other,
which is the first honest look at where the signal in this problem lives.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
COUNTS = HERE / ".work" / "counts.tsv"

SHOW = 6


def read_messages(path):
    """Every row of the file, as (label, list of words)."""
    rows = []

    with open(path, encoding="utf-8") as handle:
        next(handle)  # the header line, which is not data

        for line in handle:
            line = line.strip()
            if not line:
                continue

            label, message = line.split("\t")
            rows.append((label, message.split()))

    return rows


def count_words(rows):
    """How many messages of each kind contain each word."""
    counts = {}

    for label, words in rows:
        # A set, so a word said twice in one message still counts once. The
        # question is whether a word appears, not how enthusiastically.
        for word in set(words):
            if word not in counts:
                counts[word] = {"question": 0, "statement": 0}
            counts[word][label] += 1

    return counts


def main() -> None:
    rows = read_messages(MESSAGES)
    counts = count_words(rows)

    COUNTS.parent.mkdir(parents=True, exist_ok=True)

    with open(COUNTS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word\tquestion\tstatement\n")

        for word in sorted(counts):
            seen = counts[word]
            handle.write(f"{word}\t{seen['question']}\t{seen['statement']}\n")

    questions = sum(1 for label, _ in rows if label == "question")

    print(f"{len(rows)} messages: {questions} questions, "
          f"{len(rows) - questions} statements")
    print(f"{len(counts)} different words")
    print()

    # Sorted by the gap, then alphabetically, so the answer never depends on
    # the order a dictionary happens to hand things back in.
    def gap(word):
        return counts[word]["question"] - counts[word]["statement"]

    leaning = sorted(counts, key=lambda word: (-gap(word), word))

    print("Leans towards a question:")
    for word in leaning[:SHOW]:
        seen = counts[word]
        print(f"  {word:12} {seen['question']:2} of the questions, "
              f"{seen['statement']:2} of the statements")

    print()
    print("Leans towards a statement:")
    for word in sorted(leaning[-SHOW:], key=lambda word: (gap(word), word)):
        seen = counts[word]
        print(f"  {word:12} {seen['question']:2} of the questions, "
              f"{seen['statement']:2} of the statements")


if __name__ == "__main__":
    main()
