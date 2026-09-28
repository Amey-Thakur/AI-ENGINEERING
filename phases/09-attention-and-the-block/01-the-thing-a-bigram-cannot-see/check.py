"""
Phase 9, lesson 1: the check.

It rebuilds the bigram itself and insists on the two facts the phase rests on:
that every context preceding a target is exactly balanced between the two
answers, and that the corpus puts the subject and the target where the lessons
say it does.

A balanced context is the whole argument. If one of them tips, the bigram has
a signal, the ceiling is no longer 50%, and every number in the next four
lessons is measured against the wrong floor.

Run it with:  python check.py
"""

import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTENCES = HERE / "agreement.tsv"
CEILING = HERE / ".work" / "ceiling.tsv"

SUBJECT_AT = 1
TARGET_AT = 6
LENGTH = 8
ANSWERS = ("was", "were")


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_sentences():
    rows = []

    for line in SENTENCES.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            sentence, subject, target = line.rstrip("\n").split("\t")
            rows.append((sentence.split(), subject, target))

    return rows


def main() -> None:
    rows = read_sentences()

    if not rows:
        fail("agreement.tsv holds no sentences",
             "the corpus is the lesson, so it has to be there")

    for sentence, subject, target in rows:
        if len(sentence) != LENGTH:
            fail(f"{' '.join(sentence)!r} is {len(sentence)} words, not "
                 f"{LENGTH}",
                 "every sentence is the same shape, so a position means the "
                 "same thing in all of them")

        if sentence[SUBJECT_AT] != subject:
            fail(f"{' '.join(sentence)!r} does not hold its subject at "
                 f"position {SUBJECT_AT}",
                 "the later lessons name that position rather than search "
                 "for it")

        if sentence[TARGET_AT] != target or target not in ANSWERS:
            fail(f"{' '.join(sentence)!r} does not hold {target!r} at "
                 f"position {TARGET_AT}",
                 f"the target is one of {ANSWERS} and it always sits there")

    contexts = defaultdict(lambda: defaultdict(int))

    for sentence, _, target in rows:
        contexts[sentence[TARGET_AT - 1]][target] += 1

    for before, counts in sorted(contexts.items()):
        if counts["was"] != counts["were"]:
            fail(f"the context {before!r} is followed by {counts['was']} "
                 f"{ANSWERS[0]} and {counts['were']} {ANSWERS[1]}",
                 "an unbalanced context gives a bigram a real signal, which "
                 "would make the 50% ceiling wrong and every later "
                 "comparison meaningless")

    following = defaultdict(lambda: defaultdict(int))

    for sentence, _, _ in rows:
        for before, after in zip(sentence, sentence[1:]):
            following[before][after] += 1

    right = 0

    for sentence, _, target in rows:
        counts = following[sentence[TARGET_AT - 1]]
        guess = ("was" if counts.get("was", 0) >= counts.get("were", 0)
                 else "were")
        right += guess == target

    if right != len(rows) // 2:
        fail(f"the bigram answers {right} of {len(rows)} and the ceiling is "
             f"{len(rows) // 2}",
             "with every context balanced, breaking the tie one way is right "
             "for exactly half the sentences")

    if not CEILING.exists():
        fail("there is no .work/ceiling.tsv",
             "report each context that precedes a target, and how often each "
             "answer follows it")

    lines = [line for line in CEILING.read_text(encoding="utf-8").splitlines()
             if line.strip()]

    if lines and lines[0].split("\t")[:1] == ["context"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 3:
            fail(f"line {number} has {len(parts)} columns, and needs 3",
                 "the context, then how many times each answer follows it")

        try:
            yours[parts[0]] = (int(parts[1]), int(parts[2]))
        except ValueError:
            fail(f"line {number} holds something that is not a whole number",
                 "both columns after the context are counts")

    for before, counts in sorted(contexts.items()):
        if before not in yours:
            fail(f"there is no row for the context {before!r}",
                 f"report all {len(contexts)} of them")

        if yours[before] != (counts["was"], counts["were"]):
            fail(f"for {before!r} you report {yours[before]} and counting "
                 f"gives ({counts['was']}, {counts['were']})",
                 "count what follows the word that precedes each target")

    print(f"PASS  {len(rows)} sentences, {len(contexts)} contexts, every one "
          f"balanced, and the bigram capped at {right} of {len(rows)}")


if __name__ == "__main__":
    main()
