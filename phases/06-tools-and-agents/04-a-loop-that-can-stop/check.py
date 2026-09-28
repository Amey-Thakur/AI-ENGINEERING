"""
Phase 6, lesson 4: the check.

It rebuilds the three systems on both sets of questions, and it insists on the
two findings the lesson turns on: that the loop scores exactly what the plain
threshold scores, and that shortening a question never raises its best
overlap.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
STOPPING = HERE / ".work" / "stopping.tsv"

REFUSED = None
BAR = 3
CAP = 6


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def make_scorer(sentences):
    documents = [sentence.split() for sentence in sentences]

    def best(question):
        words = set(question.split())
        ranked = sorted(
            ((-len(words & set(document)), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap, index = ranked[0]

        return -overlap, sentences[index]

    return best


def shorten(question):
    words = question.split()

    return " ".join(words[1:]) if len(words) > 1 else ""


def main() -> None:
    sentences = [line.strip() for line in read_lines(CORPUS)]
    answerable = []

    for line in read_lines(TASKS)[1:]:
        question, tool, answer = line.split("\t")

        if tool == "search":
            answerable.append((question, answer))

    impossible = [line.split("\t")[0] for line in read_lines(IMPOSSIBLE)[1:]]
    best = make_scorer(sentences)

    def anything(question):
        return best(question)[1]

    def only_if_confident(question):
        overlap, sentence = best(question)

        return sentence if overlap >= BAR else REFUSED

    def in_a_loop(question):
        asked = question

        for _ in range(CAP):
            found = only_if_confident(asked)

            if found is not REFUSED:
                return found

            asked = shorten(asked)

            if not asked:
                return REFUSED

        return REFUSED

    systems = (
        ("answer whatever wins", anything),
        (f"only if overlap is {BAR} or more", only_if_confident),
        (f"loop, rewrite on refusal, cap {CAP}", in_a_loop),
    )

    expected = {}

    for label, system in systems:
        right = sum(1 for question, answer in answerable
                    if system(question) == answer)
        declined = sum(1 for question, _ in answerable
                       if system(question) is REFUSED)
        expected[(label, f"{len(answerable)} answerable")] = (
            right, declined, len(answerable))

        declined = sum(1 for question in impossible
                       if system(question) is REFUSED)
        expected[(label, f"{len(impossible)} unanswerable")] = (
            declined, declined, len(impossible))

    rewrites = 0
    rose = 0

    for question in [question for question, _ in answerable] + impossible:
        asked = question

        while True:
            shorter = shorten(asked)

            if not shorter:
                break

            rewrites += 1
            rose += best(shorter)[0] > best(asked)[0]
            asked = shorter

    if rose:
        fail(
            f"shortening a question raised its best overlap {rose} times out "
            f"of {rewrites}",
            "removing a word can only shrink the overlap with every sentence, "
            "so check how you are scoring",
        )

    if not STOPPING.exists():
        fail(
            "there is no .work/stopping.tsv",
            "report each system on both sets: how often it behaved correctly "
            "and how often it declined",
        )

    lines = STOPPING.read_text(encoding="utf-8").strip().splitlines()

    if lines and lines[0].split("\t")[:1] == ["system"]:
        lines = lines[1:]

    yours = {}

    for number, line in enumerate(lines, start=2):
        parts = [part.strip() for part in line.split("\t")]

        if len(parts) < 5:
            fail(
                f"line {number} has {len(parts)} columns, and needs 5",
                "each row is the system, which questions, how many correct, "
                "how many declined, how many asked",
            )

        try:
            yours[(parts[0], parts[1])] = (int(parts[2]), int(parts[3]),
                                           int(parts[4]))
        except ValueError:
            fail(
                f"line {number} has a count that is not a whole number",
                "the last three columns are counts",
            )

    for key, numbers in sorted(expected.items()):
        if key not in yours:
            fail(
                f"there is no row for {key[0]!r} on the {key[1]}",
                f"report all {len(expected)} combinations",
            )

        if yours[key] != numbers:
            correct, declined, asked = numbers
            fail(
                f"for {key[0]!r} on the {key[1]} you report {yours[key]} and "
                f"running it gives ({correct}, {declined}, {asked})",
                "on the unanswerable questions the correct behaviour is "
                "declining, so those two columns hold the same number",
            )

    loop_label = f"loop, rewrite on refusal, cap {CAP}"
    bar_label = f"only if overlap is {BAR} or more"

    for which in (f"{len(answerable)} answerable",
                  f"{len(impossible)} unanswerable"):
        if expected[(loop_label, which)] != expected[(bar_label, which)]:
            fail(
                f"the loop and the plain threshold differ on the {which} "
                f"questions",
                "the loop only ever retries a question the threshold "
                "refused, and shortening it cannot raise it above the "
                "threshold, so the two must score the same",
            )

    loose = sum(correct for (label, _), (correct, _, _) in expected.items()
                if label == "answer whatever wins")
    strict = sum(correct for (label, _), (correct, _, _) in expected.items()
                 if label == bar_label)
    total = len(answerable) + len(impossible)

    print(f"PASS  declining takes {loose} of {total} to {strict} of {total}, "
          f"and {rewrites} rewrites raised the overlap {rose} times")


if __name__ == "__main__":
    main()
