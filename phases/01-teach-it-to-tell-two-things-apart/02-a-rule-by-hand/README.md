# 2. A rule by hand

> **Before you let a machine find a rule, write one yourself.**
>
> Not as a warm-up. Without a number of your own, you have no way of knowing
> whether the clever thing you build next is clever. Teams skip this step and
> then spend a month proud of a model that is worse than one line of code.

**You will:** write a rule, measure how often it is right, and learn why that number on its own can be a lie.

**You need:** [lesson 1](../01-words-into-numbers/).

<br>

## The number to beat

Sixty messages, thirty of each kind. So a rule that ignores the message entirely and always says "question" is right **50%** of the time.

That is your floor, and it is called the **baseline**. Every result you ever produce has to be read against it. 95% sounds excellent until you learn that 94% of the data was one class, at which point your model has learned to say one word.

> [!IMPORTANT]
> Always work out what guessing scores before you build anything. It takes one
> line and it is the difference between knowing your result is good and hoping.

<br>

## A rule worth trying

Lesson 1 showed which words lean towards questions: *does*, *do*, *can*, *how*, *what*. Now use where they sit.

English moves the wh-word or the auxiliary verb to the front when it asks something. *What time is it.* *Do you have it.* *Can this run without a gpu.* The signal is not just that those words appear, it is that they appear **first**.

```python
OPENERS = {"what", "how", "why", "who", "where", "when",
           "is", "are", "do", "does", "can", "could", "should"}

def predict(message):
    words = message.split()
    if words and words[0] in OPENERS:
        return "question"
    return "statement"
```

That is the whole model. Nine lines, no training, and you can read it aloud.

<br>

## Measuring it honestly

Counting how many you got right gives one number. It hides which kind of mistake you made, and those are rarely equally bad.

Lay it out as a **confusion matrix**: what it was, against what you called it.

|  | called a question | called a statement |
| --- | --- | --- |
| **really a question** | correct | missed |
| **really a statement** | false alarm | correct |

The diagonal is what went right. Everything off it is a different kind of wrong. A spam filter that misses spam is annoying; one that files your job offer as spam is not the same failure at all, and a single accuracy number treats them as identical.

<br>

## Your turn

Write `.work/predictions.tsv`, one row per message, in the order they appear:

```
predicted    message
question     what time does the meeting start
statement    the meeting starts at ten
```

Then count how many you got right. The check needs **80%**, which any sensible rule clears.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
57 of 60 right, 95.0%
Always guessing one kind would be 50.0%

                 called a question   called a statement
  really a question           30                    0
  really a statement           3                   27

The 3 it got wrong:
  called it a question  but it is a statement 'why it is slow is still unclear'
  called it a question  but it is a statement 'how the cache works is documented'
  called it a question  but it is a statement 'what happened is written in the postmortem'
```
<!-- end output -->

<br>

## Look at what it got wrong

Three mistakes, and they are all the same mistake: a statement that opens with a question word.

> *why it is slow is still unclear*
> *how the cache works is documented*
> *what happened is written in the postmortem*

Each one begins like a question and then does something a question never does: it goes on to make a claim. The rule cannot see that, because the rule only ever looks at word one.

Notice also that the errors are **all on one side**. It never called a question a statement. A rule that leans one way is not broken, but it is a thing to know about your system rather than to discover in production.

> [!TIP]
> Three wrong out of sixty is where the real work starts. The 95% tells you
> almost nothing you did not already know. The three tell you exactly what your
> model cannot see, and that is the only list worth having.

<br>

## Check yourself

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart/02-a-rule-by-hand
```

<br>

## Going further

Optional, and there is no check for it.

Try to fix those three without breaking the other fifty-seven. The obvious patch is to look at the second word, or at whether a verb like *is* appears later. Try it, and measure. Most patches that fix three cases break four others, and finding that out by measuring rather than by arguing is the habit this whole course is built on.

<br>

## What you learned

- The baseline is what guessing scores, and no result means anything without it.
- A rule you can read aloud is a legitimate model, and it is the number to beat.
- Accuracy hides which kind of mistake you made; a confusion matrix does not.
- Errors that all fall on one side tell you something specific about your model.
- The handful it gets wrong is worth more of your attention than the many it gets right.

**Next:** [3. Let it learn](../03-let-it-learn/), where you stop choosing the words yourself and let the program find them.
