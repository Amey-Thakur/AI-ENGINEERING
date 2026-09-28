"""
Phase 8, lesson 5: the thing you ship.

The whole course, assembled: an index rather than a scan, tools that refuse
work they cannot do, a threshold that declines rather than guessing, private
sentences kept out of the index rather than filtered out of the answers, and
a meter on everything.

What it produces is not a score. It is a page of numbers, each one traceable
to the lesson that measured it, including the ones that say the system cannot
be shown to work.

Run it with:  python solve.py
"""

from collections import Counter, defaultdict
from math import exp, lgamma, log
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus.txt"
PRIVATE = HERE / "private.txt"
TASKS = HERE / "tasks.tsv"
IMPOSSIBLE = HERE / "impossible.tsv"
RELEASE = HERE / ".work" / "release.tsv"

REFUSED = None
OPERATIONS = ("times", "plus", "minus", "divided")
BAR = 3
ALPHA = 0.05
HALVINGS = 40


def read_lines(path):
    return [line.rstrip("\n")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def log_choose(n, k):
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def chance_of_at_least(k, n, rate):
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(k, n + 1))


def chance_of_at_most(k, n, rate):
    return sum(exp(log_choose(n, i) + i * log(rate) + (n - i) * log(1 - rate))
               for i in range(0, k + 1))


def pin_down(rising, target):
    low, high = 0.0, 1.0

    for _ in range(HALVINGS):
        middle = (low + high) / 2

        if rising(middle) < target:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def interval(k, n):
    low = 0.0 if k == 0 else pin_down(
        lambda rate: chance_of_at_least(k, n, rate), ALPHA / 2)
    high = 1.0 if k == n else pin_down(
        lambda rate: -chance_of_at_most(k, n, rate), -ALPHA / 2)

    return low, high


def calculate(question):
    words = question.split()

    if len(words) < 4:
        return REFUSED
    if not words[2].isdigit() or not words[-1].isdigit():
        return REFUSED
    if words[3] not in OPERATIONS:
        return REFUSED

    first, last, operation = int(words[2]), int(words[-1]), words[3]

    return {
        "times": str(first * last),
        "plus": str(first + last),
        "minus": str(first - last),
        "divided": str(first // last) if last else "",
    }[operation]


def count(question):
    words = question.split()

    if not words or not words[-1].isalpha():
        return REFUSED

    return str(len(words[-1]))


def route(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"


def build(sentences):
    """The index, built once, over the sentences we are allowed to return."""
    postings = defaultdict(list)

    for index, sentence in enumerate(sentences):
        for word in set(sentence.split()):
            postings[word].append(index)

    return postings


def make_system(sentences):
    postings = build(sentences)

    def ask(question):
        """Returns the answer, the overlap if searched, and what it cost."""
        picked = route(question)

        if picked != "search":
            found = {"calculate": calculate, "count": count}[picked](question)

            if found is not REFUSED:
                return found, None, 0

        words = set(question.split())
        cost = 0
        hits = Counter()

        for word in words:
            holding = postings.get(word, ())
            cost += len(holding)

            for index in holding:
                hits[index] += 1

        if not hits:
            return REFUSED, 0, cost

        overlap = max(hits.values())

        if overlap < BAR:
            return REFUSED, overlap, cost

        winner = min(index for index, seen in hits.items() if seen == overlap)

        return sentences[winner], overlap, cost

    return ask


def main() -> None:
    public = [line.strip() for line in read_lines(CORPUS)]
    private = [line.strip() for line in read_lines(PRIVATE)]

    questions = []

    for line in read_lines(TASKS)[1:]:
        question, _, answer = line.split("\t")
        questions.append((question, answer, True))

    for line in read_lines(IMPOSSIBLE)[1:]:
        questions.append((line.split("\t")[0], None, False))

    ask = make_system(public)
    outage = make_system([])

    correct = wrong = declined = searched = cleared = leaked = 0
    costs = []

    for question, answer, answerable in questions:
        given, overlap, cost = ask(question)
        costs.append(cost)

        if overlap is not None:
            searched += 1
            cleared += overlap >= BAR

        if given in set(private):
            leaked += 1

        if given is REFUSED:
            declined += 1
            correct += not answerable
        elif answerable and given == answer:
            correct += 1
        else:
            wrong += 1

    low, high = interval(correct, len(questions))

    floor = sum(1 for _, _, answerable in questions if not answerable)
    tools_only = 0

    for question, answer, answerable in questions:
        if route(question) == "search":
            tools_only += not answerable
        else:
            given = {"calculate": calculate,
                     "count": count}[route(question)](question)
            tools_only += given is not REFUSED and answerable and given == answer

    surviving = 0

    for question, answer, answerable in questions:
        given, _, _ = outage(question)
        surviving += (not answerable) if given is REFUSED else (
            answerable and given == answer)

    dearest = max(costs)
    median = sorted(costs)[len(costs) // 2]

    sheet = [
        ("questions asked", f"{len(questions)}", "phase 6, phase 7"),
        ("handled correctly", f"{correct} of {len(questions)}",
         "phase 6 lesson 5"),
        ("true rate, 95 percent confident", f"{low:.1%} to {high:.1%}",
         "phase 7 lesson 1"),
        ("false statements", f"{wrong}", "phase 6 lesson 5"),
        ("questions declined", f"{declined}", "phase 6 lesson 4"),
        ("private sentences returned", f"{leaked}", "phase 8 lesson 4"),
        ("floor: decline everything", f"{floor} of {len(questions)}",
         "phase 7 lesson 3"),
        ("floor: tools only, no search", f"{tools_only} of {len(questions)}",
         "phase 7 lesson 3"),
        ("dearest question", f"{dearest} comparisons", "phase 8 lesson 1"),
        ("median question", f"{median} comparisons", "phase 8 lesson 1"),
        ("whole run", f"{sum(costs)} comparisons", "phase 8 lesson 2"),
        ("healthy signal", f"{cleared} of {searched} searches clear it",
         "phase 8 lesson 3"),
        ("if the corpus is lost", f"{surviving} of {len(questions)} survive",
         "phase 8 lesson 3"),
    ]

    RELEASE.parent.mkdir(parents=True, exist_ok=True)

    with open(RELEASE, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("property\tvalue\tmeasured in\n")

        for label, value, where in sheet:
            handle.write(f"{label}\t{value}\t{where}\n")

    print("What this system is, on one page.")
    print()

    for label, value, where in sheet:
        print(f"  {label:32} {value:32} {where}")

    print()
    print("What the numbers above do not establish:")
    print()
    print(f"  The interval is {high - low:.0%} wide, so the true rate could "
          f"be {low:.0%} or {high:.0%}.")
    print(f"  Reaching plus or minus 5 points needs about 250 questions "
          f"rather than {len(questions)}.")
    print(f"  Removing the whole search half leaves {surviving} of "
          f"{len(questions)}, and phase 7 could not")
    print(f"  distinguish that from the full system, so the retrieval half is "
          f"unproven.")
    print(f"  The threshold of {BAR} was chosen on these questions. On twenty "
          f"written later it")
    print(f"  was still the best value, and it scored 18 points lower.")
    print()
    print("What it must not be asked to do:")
    print()
    print(f"  Answer from a corpus it has not indexed, which is the only "
          f"control on")
    print(f"  what it can say. {len(private)} sentences are excluded and "
          f"{leaked} were returned.")
    print(f"  Serve users with different permissions from this one index.")
    print(f"  Be trusted when the healthy signal falls, because accuracy will "
          f"not move.")


if __name__ == "__main__":
    main()
