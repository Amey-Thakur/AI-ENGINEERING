# Phase 6. Tools and agents

**Five lessons. About four hours. Still nothing installed.**

Phase 5 ended with a system that could find a sentence in a corpus and a warning that every component you add can subtract. This phase is about the moment a system stops producing text and starts deciding to do something: calling a function, choosing between functions, refusing, giving up, and costing money while it happens.

Nothing here is a simplified version of an agent. A loop that calls a tool, reads the result, decides whether to go again and can terminate three ways **is** an agent, and every framework built on that shape leaves the shape alone.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [What a model cannot do](01-what-a-model-cannot-do/) | Some answers are impossible rather than unlikely |
| 2 | [Choosing the tool](02-choosing-the-tool/) | Picking the tool is harder than any of the tools |
| 3 | [When it chooses wrong](03-when-it-chooses-wrong/) | A tool can only refuse what it can detect |
| 4 | [A loop that can stop](04-a-loop-that-can-stop/) | A retry needs to know something the first try did not |
| 5 | [Measuring an agent](05-measuring-an-agent/) | Two correct measurements, disagreeing |

<br>

## The data

`tasks.tsv` holds 38 questions, each labelled with the tool that answers it: 11 arithmetic, 12 letter counts, 15 to be found in the corpus. Eight of the 38 open like a question for the wrong tool, because *how many* and *what is* are shared between all three.

`unseen.tsv` holds 8 more, written after the routing rules were finished and never looked at while they were being written. It exists because a rule written with the questions on screen scores 100% on those questions, and phase 2 already named that mistake.

`impossible.tsv` holds 10 questions the corpus cannot answer: no people, no money, no dates in the future, no credentials. Their correct answer is a refusal. They are the only questions in the course where declining is the right outcome, and adding them reversed a conclusion.

<br>

## Five results worth carrying

**The corpus contains zero digits, so 20 of 30 answers were outside what the model could say.** Not unlikely, impossible. Models do not do arithmetic, they continue text, and correct arithmetic is a consequence of having seen enough of it.

**A misroute that crashes is far better than one that answers.** Sent *how many users did the incident affect*, the counting tool returned `6`, which is the length of the word *affect*. Nothing raised, nothing logged. The two misroutes that hit the calculator raised `ValueError` and were fixed the same afternoon.

**A routing rule scored 38 of 38 and then 6 of 8.** It was not derived, it was read off the answers. The better rule is still the better rule, and the error was in believing the 100%.

**The retry loop was provably incapable of working.** Dropping a word can only shrink the overlap with every sentence, so a question below the threshold stays below it forever. 128 rewrites, the score rose 0 times, 2.1 times the calls, not one answer changed.

**Ten unanswerable questions reversed lesson 3's conclusion.** The confidence threshold was a 3 for 1 loss measured on questions that had answers, and a 3 for 8 gain once questions without answers were counted. 12 of 25 became 17 of 25.

> [!WARNING]
> A test set made only of answerable questions cannot measure the ability to
> decline, and silently punishes it. Every refusal scores as a failure, every
> confident guess at an unanswerable question scores as nothing, and the
> system that always answers wins.
>
> Almost every benchmark has this shape, because the questions get written by
> reading the documents.

<br>

## And one that has no answer

The two best versions of the finished agent are 35 right with 13 wrong, and 32 right with 4 wrong, at identical cost. Neither is better. They are equal exactly when a confident wrong answer costs a third of what a right answer is worth, and that number is a fact about where the system is deployed rather than anything in the data.

<br>

## Check the phase

```
python tools/run_lessons.py phases/06-tools-and-agents
```

**Next:** [Phase 7](../07-measuring-whether-any-of-it-works/), where measurement stops being the last step and becomes the first.
