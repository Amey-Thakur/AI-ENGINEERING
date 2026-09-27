# Phase 1. Teach it to tell two things apart

**Five lessons. About four hours. Nothing installed.**

By the end of this phase you will have written something that learns. Not downloaded, not called over an API, not configured. Written, by you, in plain Python, on sixty messages that live in this folder.

Telling two things apart is the smallest problem in the field that is still a real one. Everything larger is this with more of it: more classes, more data, more layers. The questions that decide whether it works are the same questions, and they are all asked in this phase.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [Words into numbers](01-words-into-numbers/) | Text becomes numbers by a decision a person makes |
| 2 | [A rule by hand](02-a-rule-by-hand/) | Nothing means anything without a baseline |
| 3 | [Let it learn](03-let-it-learn/) | A machine can find the rule, given a way to be wrong |
| 4 | [Tell the truth](04-tell-the-truth/) | Scoring on what you trained on is not a score |
| 5 | [When it breaks](05-when-it-breaks/) | The failures are the part worth reading |

<br>

## The data

`messages.tsv` sits in every lesson folder: sixty short messages, thirty questions and thirty statements, written for this course so that nothing here can be withdrawn by anyone.

Two things were done to it on purpose.

**The question marks are gone.** With them, this is one line of code and teaches nothing.

**Three statements open with a question word.** *Why it is slow is still unclear.* Those three exist so that the obvious rule fails somewhere, because a problem where the obvious rule works perfectly teaches you that the obvious rule always works.

> [!NOTE]
> Sixty messages is a small dataset, and that is deliberate too. You can read
> all of it in two minutes. Knowing your data by eye, before you model it, is a
> habit that gets rarer as datasets get bigger, and it is the one that catches
> the mistakes that matter.

<br>

## Check the phase

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart
```

**Next:** [Phase 2](../02-a-network-you-wrote-yourself/), where the single rule becomes a network of them.
