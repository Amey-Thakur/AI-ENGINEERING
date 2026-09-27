"""
Lesson 2: a rule by hand.

Predicts question or statement using one rule a person can read, writes the
predictions down, and reports how often the rule is right.

The rule is not a guess. English fronts the wh-word or the auxiliary verb when
asking: "what time is it", "do you have it". So the first word carries most of
the signal, and a rule built on it should do well.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
MESSAGES = HERE / "messages.tsv"
PREDICTIONS = HERE / ".work" / "predictions.tsv"

# The words English puts first when it asks something.
OPENERS = {
    "what", "how", "why", "who", "where", "when", "which",
    "is", "are", "was", "were", "do", "does", "did",
    "can", "could", "should", "would", "will", "have", "has",
}


def read_messages(path):
    rows = []

    with open(path, encoding="utf-8") as handle:
        next(handle)

        for line in handle:
            line = line.strip()
            if line:
                label, message = line.split("\t")
                rows.append((label, message))

    return rows


def predict(message: str) -> str:
    """One rule, readable in a sentence: does it open like a question."""
    words = message.split()

    if words and words[0] in OPENERS:
        return "question"

    return "statement"


def main() -> None:
    rows = read_messages(MESSAGES)
    PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)

    right = 0
    confusion = {("question", "question"): 0, ("question", "statement"): 0,
                 ("statement", "question"): 0, ("statement", "statement"): 0}

    with open(PREDICTIONS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("predicted\tmessage\n")

        for label, message in rows:
            guess = predict(message)
            handle.write(f"{guess}\t{message}\n")

            confusion[(label, guess)] += 1
            right += guess == label

    total = len(rows)

    questions = sum(1 for label, _ in rows if label == "question")
    commonest = max(questions, total - questions)

    print(f"{right} of {total} right, {right / total:.1%}")
    print(f"Always guessing one kind would be {commonest / total:.1%}")
    print()
    print("                 called a question   called a statement")
    print(f"  really a question   {confusion[('question', 'question')]:>10}"
          f"   {confusion[('question', 'statement')]:>18}")
    print(f"  really a statement  {confusion[('statement', 'question')]:>10}"
          f"   {confusion[('statement', 'statement')]:>18}")
    print()

    wrong = [(label, message) for label, message in rows
             if predict(message) != label]

    print(f"The {len(wrong)} it got wrong:")
    for label, message in wrong:
        print(f"  called it a {predict(message):9} but it is a {label:9} "
              f"{message!r}")


if __name__ == "__main__":
    main()
