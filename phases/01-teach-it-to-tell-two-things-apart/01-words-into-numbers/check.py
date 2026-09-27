"""
Lesson 1: the check.

It does not compare your file against a stored answer. It reads the messages
itself, works out what the counts should be, and compares that with what you
produced. So the check stays right if the data ever changes, and it cannot be
passed by copying numbers from anywhere.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
COUNTS = HERE / ".work" / "counts.tsv"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def truth():
    """What the counts are, worked out from the messages."""
    counts = {}

    with open(MESSAGES, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.strip()
            if not line:
                continue

            label, message = line.split("\t")

            for word in set(message.split()):
                counts.setdefault(word, {"question": 0, "statement": 0})
                counts[word][label] += 1

    return counts


def main() -> None:
    if not COUNTS.exists():
        fail(
            "there is no .work/counts.tsv",
            "write one row per word: the word, its count in questions, "
            "its count in statements, separated by tabs",
        )

    lines = COUNTS.read_text(encoding="utf-8").strip().splitlines()

    if len(lines) < 2:
        fail(
            "counts.tsv has a header and nothing else",
            "write one row for every different word in the messages",
        )

    header = lines[0].split("\t")
    if [part.strip().lower() for part in header] != ["word", "question", "statement"]:
        fail(
            f"the first line is {lines[0]!r}, which is not the expected header",
            "the first line should read: word, question, statement, tab separated",
        )

    yours = {}
    for number, line in enumerate(lines[1:], start=2):
        parts = line.split("\t")

        if len(parts) != 3:
            fail(
                f"line {number} has {len(parts)} columns, not 3",
                "every row is a word and two numbers, separated by tabs",
            )

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(
                f"line {number} has something that is not a number: {line!r}",
                "the second and third columns must be whole numbers",
            )

    expected = truth()

    missing = sorted(set(expected) - set(yours))
    if missing:
        fail(
            f"{len(missing)} words are not in your table, the first being "
            f"{missing[0]!r}",
            "every different word in the messages needs a row",
        )

    extra = sorted(set(yours) - set(expected))
    if extra:
        fail(
            f"your table has {len(extra)} words that are not in the messages, "
            f"the first being {extra[0]!r}",
            "check you are splitting on spaces and not inventing words",
        )

    for word in sorted(expected):
        want = (expected[word]["question"], expected[word]["statement"])

        if yours[word] != want:
            fail(
                f"{word!r} is counted {yours[word]}, but appears in "
                f"{want[0]} questions and {want[1]} statements",
                "count each word once per message, even if it is said twice",
            )

    print(f"PASS  {len(yours)} words counted, every one correct")


if __name__ == "__main__":
    main()
