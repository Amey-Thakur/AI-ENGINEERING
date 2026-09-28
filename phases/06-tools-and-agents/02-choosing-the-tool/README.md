# 2. Choosing the tool

> **Lesson 1 answered 29 of 30, and a person picked the tool every time.**
>
> The label was sitting in the file. Take it away and the system has to look
> at *what is 47 times 13* and work out, from the words alone, that this one
> is for the calculator.

**You will:** write the rule anyone writes first, measure it, find the rule that fixes it, and then discover that your fix scored 100% because you wrote it with the answers in front of you.

**You need:** [lesson 1](../01-what-a-model-cannot-do/).

<br>

## Eight more questions, and a rule

`tasks.tsv` has grown from 30 to 38. The eight additions are the awkward ones:

```
how many users did the incident affect      search
how many minutes does the standup take      search
what is the vault for                       search
what is a flaky test                        search
```

Every one of them opens like a question for a different tool. *How many* is how the counting questions open. *What is* is how the arithmetic questions open. All four want search.

So here is the rule, and it is the rule you would write:

```python
def route_by_opening(question):
    if "how many" in question:
        return "count"
    if "what is" in question:
        return "calculate"

    return "search"
```

**33 of 38.** For five lines that is not bad, and the five it misses are all the same miss: a search question stolen by a tool whose opening words it happened to share.

<br>

## Your turn

Write both rules, route all 38 questions and the 8 in `unseen.tsv`, run whichever tool each rule picked, and write `.work/routing.tsv`:

```
router                   questions              routed   answered   asked
obvious keywords         the 38 written first   33       32         38
obvious keywords         the 8 held back        5        5          8
shape of the question    the 38 written first   38       35         38
shape of the question    the 8 held back        6        6          8
```

Run the tool the **rule** picked, not the tool the label names. The label is what you are trying to predict.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Two rules for picking the tool, each measured twice.

  router                 questions              routed    answered
  obvious keywords       the 38 written first  33 of 38  32 of 38
  obvious keywords       the 8 held back        5 of  8   5 of  8
  shape of the question  the 38 written first  38 of 38  35 of 38
  shape of the question  the 8 held back        6 of  8   6 of  8

Routing all 38 correctly still answers 35, because search misses 3 of them on its own.

Sent to the wrong tool by the obvious rule, and what came back:
  'how many users did the incident affect'
    wanted search, picked count, gave '6'
  'how many nodes can the cluster lose'
    wanted search, picked count, gave '4'
  'how many minutes does the standup take'
    wanted search, picked count, gave '4'
  'what is the vault for'
    wanted search, picked calculate, raised ValueError
  'what is a flaky test'
    wanted search, picked calculate, raised ValueError

Sent to the wrong tool by the better rule, on questions it had never seen:
  'letters in the word schema'
    wanted count, picked search, gave 'the schema is documented in the same repository as the code'
  'count the letters in monitoring'
    wanted count, picked search, gave 'the version in production is behind the version on staging'
```
<!-- end output -->

<br>

## Five misroutes, two completely different outcomes

Read that list again, because the five failures are not five of the same thing.

**Two of them crashed.** *What is the vault for* went to the calculator, which did `int(words[2])` on the word `the` and raised `ValueError`. The system stopped. Somebody gets a stack trace, and somebody fixes it this afternoon.

**Three of them answered.** *How many users did the incident affect* went to the counter, which returned **`6`**, and six is the number of letters in the word *affect*. Nothing raised. Nothing logged. The question asked *how many*, and a number came back, and the number is meaningless.

> [!CAUTION]
> The crash is the better failure, by a distance.
>
> A misrouted call that raises has told you it was misrouted. A misrouted
> call that returns a plausible value has produced a wrong answer with the
> full confidence of the system behind it, and it will sit in your output
> until a human happens to read that particular row.
>
> This is why the rigid, narrow, fragile tool is often the safer one to
> build. A tool that accepts anything will answer anything.

<br>

## The rule that fixes it

The first rule read how the question **opens**. The fix is to read what the tool actually **needs**:

```python
def route_by_shape(question):
    if "letters are in" in question:
        return "count"

    words = question.split()

    if (any(word.isdigit() for word in words)
            and any(word in OPERATIONS for word in words)):
        return "calculate"

    return "search"
```

`calculate` needs a number and an operation, so look for a number and an operation. `count` needs the phrase it was built around. Anything else falls through to search, which is the only tool that can take an arbitrary sentence.

**38 of 38, and no crashes.** Every question in the file, routed correctly.

<br>

## Which is exactly the number you should not trust

Stop and look at how that rule came to exist. All 38 questions were on screen. `letters are in` went into the code because twelve questions contained it. `isdigit` went in because eleven questions had digits. The rule was not derived, it was **read off the answers**.

Phase 2 called this fitting the test set. `unseen.tsv` holds eight questions written afterwards and never looked at while the rules were being written:

| Rule | The 38 written first | The 8 held back |
| --- | --- | --- |
| Obvious keywords | 33 of 38 (87%) | **5 of 8 (63%)** |
| Shape of the question | 38 of 38 (**100%**) | **6 of 8 (75%)** |

The perfect rule is not perfect. It is a rule that gets three questions in four right, and the 100% was a measurement of how carefully it had been fitted to 38 sentences.

Both misses are new phrasings of counting:

```
'letters in the word schema'     -> search, gave 'the schema is documented in the same repository as the code'
'count the letters in monitoring' -> search, gave 'the version in production is behind the version on staging'
```

> [!NOTE]
> The better rule is still better. 75% beats 63%, and the work was worth
> doing. The error was never in the rule, it was in believing the 100%.
>
> Every routing number you will ever read (a model picking a function, a
> classifier picking an intent, a planner picking a next step) was measured
> on some set of examples. The only question worth asking is whether those
> examples existed before the thing being measured did.

<br>

## And perfect routing still does not give a perfect system

Look at the row again: the shape rule routes **38 of 38** and answers **35 of 38**.

Three questions went to exactly the right tool and came back wrong, because that tool was search, and search answers 12 of its own 15 questions. Routing cannot repair a tool, it can only reach it.

**Your router's ceiling is your tools' ceiling.** Lesson 5 of phase 5 made the same point about retrieval, and it will keep being true at every layer: a stage that picks correctly between three components is bounded by what those three components can do.

<br>

## Check yourself

```
python tools/run_lessons.py phases/06-tools-and-agents/02-choosing-the-tool
```

The check refuses to pass if you measured only on the 38, because that is the mistake the lesson is about.

<br>

## Going further

Optional, and there is no check for it.

Write five more questions yourself, without looking at either rule, and route them. Whatever score you get is a better estimate than both numbers in this lesson, because your five are the only questions in the phase that neither rule was written near.

Then try to fix the two misses. You will reach for `"letters" in question`, and it will work on both, and it will also grab *how many letters of the alphabet does the schema use*, which wants search. Each patch buys back the case in front of you and costs you a case you have not thought of yet, which is what it feels like to maintain a rule-based router for a year.

<br>

## What you learned

- Choosing the tool is a prediction problem, and it is a harder one than any of the tools.
- The first rule anyone writes keys on how a question opens, and openings are shared between tools.
- A misroute that crashes is far better than a misroute that returns a plausible value, so a narrow tool that refuses bad input is safer than a permissive one.
- A rule written with the examples in front of you scores near perfectly on those examples and tells you nothing.
- Held-back questions are the only honest measurement of a router, and 100% became 75%.
- Perfect routing still only answers 35 of 38, because routing reaches a tool and cannot improve it.

**Next:** [3. When it chooses wrong](../03-when-it-chooses-wrong/), where the tools stop accepting whatever they are handed.
