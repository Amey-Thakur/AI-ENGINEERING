"""
Phase 8, lesson 4: what it must not say.

Somebody points the indexer at one folder too many. Eight sentences that
should never leave the building are now in the corpus, and the search has no
idea, because a search has no idea who is asking or what it is holding.

Three defences, measured. The one everybody builds first catches a third of
the leaks and breaks a working answer on the way.

Run it with:  python solve.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
PRIVATE = HERE / "private.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
LEAKS = HERE / ".work" / "leaks.tsv"

REFUSED = None
BLOCKED = ("password", "key", "secret", "credential", "credentials",
           "private", "admin", "token")
BAR = 3


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def make_search(sentences):
    documents = [set(sentence.split()) for sentence in sentences]

    def search(question):
        if not documents:
            return 0, None

        words = set(question.split())
        ranked = sorted(
            ((-len(words & document), index)
             for index, document in enumerate(documents)),
            key=lambda pair: (pair[0], pair[1]),
        )
        overlap = -ranked[0][0]

        return overlap, sentences[ranked[0][1]]

    return search


def unprotected(search):
    def answer(question):
        overlap, sentence = search(question)

        return sentence if overlap >= BAR else REFUSED

    return answer


def refuse_the_question(search):
    """Check what was asked. The defence everybody writes first."""
    def answer(question):
        if any(word in BLOCKED for word in question.split()):
            return REFUSED

        overlap, sentence = search(question)

        return sentence if overlap >= BAR else REFUSED

    return answer


def main() -> None:
    public = [line.strip() for line in read_lines(CORPUS)]
    private = [line.strip() for line in read_lines(PRIVATE)]
    secret = set(private)

    answerable = [(line.split("\t")[0], line.split("\t")[2])
                  for line in read_lines(TASKS)[1:]
                  if line.split("\t")[1] == "search"]
    unanswerable = [line.split("\t")[0]
                    for line in read_lines(IMPOSSIBLE)[1:]]
    questions = [(question, answer, True) for question, answer in answerable]
    questions += [(question, None, False) for question in unanswerable]

    leaky = make_search(public + private)
    clean = make_search(public)

    systems = (
        ("no protection", unprotected(leaky)),
        ("refuse the question", refuse_the_question(leaky)),
        ("never index it", unprotected(clean)),
    )

    rows = []
    found = {}

    for label, system in systems:
        leaked = []
        correct = 0

        for question, answer, answerable_here in questions:
            given = system(question)

            if given in secret:
                leaked.append((question, given))

            if given is REFUSED:
                correct += not answerable_here
            elif answerable_here and given == answer:
                correct += 1

        rows.append((label, len(leaked), correct, len(questions)))
        found[label] = leaked

    LEAKS.parent.mkdir(parents=True, exist_ok=True)

    with open(LEAKS, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("defence\tleaked\tcorrect\tasked\n")

        for label, leaked, correct, asked in rows:
            handle.write(f"{label}\t{leaked}\t{correct}\t{asked}\n")

    print(f"{len(private)} private sentences added to a corpus of "
          f"{len(public)}, then {len(questions)} ordinary questions.")
    print()
    print("  defence               private sentences returned   handled "
          "correctly")

    for label, leaked, correct, asked in rows:
        print(f"  {label:20}  {leaked:26}   {correct:2} of {asked}")

    print()
    print("What leaked with no protection at all:")

    for question, sentence in found["no protection"]:
        asked_for_it = any(word in BLOCKED for word in question.split())
        print(f"  {question!r}")
        print(f"    -> {sentence!r}")
        print(f"       the question "
              f"{'contains a word a filter would catch' if asked_for_it else 'contains nothing a filter would catch'}")

    print()
    print("Still leaking once the questions are filtered:")

    for question, sentence in found["refuse the question"]:
        print(f"  {question!r}")
        print(f"    -> {sentence!r}")

    print()

    unfiltered, filtered, removed = rows
    refused_wrongly = [question for question, _, answerable_here in questions
                       if answerable_here
                       and any(word in BLOCKED for word in question.split())]

    print(f"Filtering the question stops {unfiltered[1] - filtered[1]} of "
          f"{unfiltered[1]} leaks, and refuses "
          f"{len(refused_wrongly)} question")
    print(f"that had a perfectly good answer:")

    for question in refused_wrongly:
        print(f"  {question!r}")

    print()
    print(f"So it trades one leak stopped for one answer lost, and the score "
          f"stays at {filtered[2]}")
    print(f"of {filtered[3]} either way. Two private sentences are still "
          f"being handed out.")
    print()
    print(f"Not indexing them stops all {unfiltered[1]} leaks and costs "
          f"nothing: {removed[2]} of {removed[3]},")
    print(f"which is what the system scored before anybody pointed the "
          f"indexer at the wrong folder.")


if __name__ == "__main__":
    main()
