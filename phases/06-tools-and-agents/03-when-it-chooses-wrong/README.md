# 3. When it chooses wrong

> **The rule from lesson 2 gets three questions in four right on questions it
> has not seen, and no amount of patching is going to move that much.**
>
> So stop working on the chooser. The calculator knows perfectly well that
> *what is the vault for* is not arithmetic. Nobody ever asked it.

**You will:** give each tool the power to refuse work, measure what that buys, and find that it rescues one failure out of five and cannot touch the other four.

**You need:** [lesson 2](../02-choosing-the-tool/).

<br>

## The precondition was always there

Here is lesson 1's calculator:

```python
def calculate_anything(question):
    words = question.split()

    return arithmetic(int(words[2]), int(words[-1]), words[3])
```

It requires the third word to be a number, the last word to be a number, and the fourth word to name an operation. That requirement has been real since lesson 1. It was simply never written down, so the only way the tool could express it was to raise `ValueError` halfway through doing the work.

Write it down and the tool gains a third option, next to answering and crashing:

```python
REFUSED = None


def calculate(question):
    words = question.split()

    if len(words) < 4:
        return REFUSED
    if not words[2].isdigit() or not words[-1].isdigit():
        return REFUSED
    if words[3] not in OPERATIONS:
        return REFUSED

    return arithmetic(int(words[2]), int(words[-1]), words[3])
```

When a tool refuses, the system falls back to search, which is the only tool that accepts an arbitrary sentence.

<br>

## Your turn

Guard both exact tools, run the whole thing under both of lesson 2's rules, and write `.work/refusals.tsv`:

```
setting                                 right   refused   asked
tools accept anything, opening rule     32      0         38
tools refuse, opening rule              33      2         38
tools accept anything, shape rule       35      0         38
tools refuse, shape rule                35      0         38
search alone, any overlap               12      0         15
search alone, overlap 3 or more         9       4         15
```

Count a refusal whether or not the fallback then got the answer right.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
A tool that can say no, measured against the same tool that cannot.

  setting                                right      refused
  tools accept anything, opening rule   32 of 38   0
  tools refuse, opening rule            33 of 38   2
  tools accept anything, shape rule     35 of 38   0
  tools refuse, shape rule              35 of 38   0
  search alone, any overlap             12 of 15   0
  search alone, overlap 3 or more        9 of 15   4

What the opening rule's five mistakes did once the tools could refuse:
  'how many users did the incident affect'
    ended at count, gave '6'
  'how many nodes can the cluster lose'
    ended at count, gave '4'
  'how many minutes does the standup take'
    ended at count, gave '4'
  'what is the vault for'
    ended at search, gave 'the build number is stamped into the image'

Why search cannot be given a confidence threshold:
  the 12 it answers correctly score 2 to 5, mean 2.9
  the 3 it gets wrong score 2 to 3, mean 2.7
  every wrong answer scores what some right answer also scores.
```
<!-- end output -->

<br>

## One rescued out of five

**32 of 38 becomes 33 of 38.** Two calls were refused, both of them the questions that used to crash:

- *what is a flaky test* was refused by the calculator, went to search, and came back with **the right sentence**. It is not in the failure list any more.
- *what is the vault for* was refused, went to search, and came back with *the build number is stamped into the image*, which is wrong. Search misses that question on its own, so the fallback had nothing to rescue it with.

That is the honest size of the win: one question, and the other refusal only moved the failure rather than fixing it. What the guard reliably bought is that neither call crashed, which is worth having and is not worth much on a scoreboard.

<br>

## And the other three are exactly where they were

The three counting failures are untouched. *How many users did the incident affect* still returns **`6`**.

Look at what `count` is able to check:

```python
def count(question):
    words = question.split()

    if not words or not words[-1].isalpha():
        return REFUSED

    return str(len(words[-1]))
```

That is not a lazy guard. It is everything `count` can test. The tool needs a last word made of letters, and *how many users did the incident affect* ends in `affect`, which is a word made of letters. The precondition is satisfied. The tool does its job correctly and the answer is meaningless.

> [!WARNING]
> **A tool can only refuse what it can detect.**
>
> `calculate` has a contract about its *input*: two numbers and an operation,
> checkable in four lines. `count` has a contract about the caller's
> *intent*: this question is asking about letters. Nothing in the string
> distinguishes a question about letters from a question about users, so
> there is no guard to write. Care does not help. It is a property of the
> tool, not of the engineer.

<br>

## Which tells you where to spend the effort

Go through the tools in any system and sort them by how much of their contract is checkable from the arguments alone:

| | `calculate` | `count` |
| --- | --- | --- |
| What it needs | two numbers and an operation | a word |
| Checkable from the input? | **Yes, completely** | No, the requirement is about intent |
| Effect of a misroute | refused, falls back | confident wrong answer |
| Who has to be right | either the router or the tool | **only the router** |

The tools in the right-hand column are your real exposure. Nothing downstream will catch a mistake, so the accuracy of the chooser is the whole story for them, and lesson 2 measured that at 75% on questions it had not seen.

> [!TIP]
> Widen the contract until it is checkable, where you can. A `count` that
> took the word as an argument rather than digging it out of a sentence
> (`count("deployment")`) could not be misused this way, because the caller
> would have to commit to what it was counting.
>
> Most tool failures in real systems are this shape: a function that accepts
> a whole user utterance and infers what it was asked, instead of accepting
> the specific thing it operates on.

<br>

## The guards do nothing at all under the good rule

Both shape-rule rows read **35 of 38, 0 refusals**. Not one guard fired.

Of course they did not. The shape rule never misroutes on these 38 questions, so no tool is ever handed input it cannot take. The guards sit there being worth nothing measurable.

> [!IMPORTANT]
> This is the shape of every safety measure, and it is why they get deleted.
>
> On the run where nothing goes wrong, a guard and a missing guard produce
> identical numbers. Its value is entirely in the misroutes, which is to say
> in the inputs nobody thought of, which is to say in the ones that are not
> in your test file. You cannot demonstrate the value with the data you have,
> and you will be able to demonstrate it exactly once, at an inconvenient
> time.

<br>

## Search has no way to say no

The obvious repair is a confidence threshold: if the best sentence barely overlaps the question, refuse. Overlap of **3 or more** is a reasonable bar, and the result is bad:

| Search | Right | Refused |
| --- | --- | --- |
| Answer whatever wins | **12 of 15** | 0 |
| Only when overlap is 3 or more | 9 of 15 | 4 |

Three correct answers thrown away, to suppress one wrong one. The threshold is a 3 for 1 loss.

The reason is in the last block of output. The twelve right answers score **2 to 5**, mean 2.9. The three wrong answers score **2 to 3**, mean 2.7. Every score a wrong answer achieves is a score some right answer also achieves, so there is no line to draw anywhere.

> [!CAUTION]
> A confidence gate only works if the confidence correlates with being
> right. That is a separate fact about your scorer, and it is measurable in
> about ten lines, and almost nobody measures it before building the gate.
>
> Retrieval scores, softmax probabilities and model self-reports are all
> routinely used as confidence when nobody has checked whether the high
> numbers are more often correct than the low ones. Plot yours against
> correctness before you threshold on it.

<br>

## Check yourself

```
python tools/run_lessons.py phases/06-tools-and-agents/03-when-it-chooses-wrong
```

The check insists the guarded and unguarded tools score identically under the shape rule, because a guard that changes a result on the happy path is a guard that is rejecting valid work.

<br>

## Going further

Optional, and there is no check for it.

Rewrite `count` to take the word rather than the question, and move the extraction into the router where the intent is being decided anyway. The three surviving failures become failures of the router, which lesson 2 already measures, instead of silent wrong answers from a tool that did nothing wrong. Nothing gets more correct. The problem moves to the one place in the system that is being measured, which is most of what good structure does.

<br>

## What you learned

- Every tool already has a precondition; writing it down turns a crash into a refusal and gives the system somewhere to go next.
- Refusal rescued one failure in five here, and moved a second without fixing it. It is a small win honestly measured.
- A tool can only refuse what it can detect, and a contract about the caller's intent is not detectable from the input.
- Tools that cannot check themselves are the ones where the chooser's accuracy is the entire safety story.
- Widening a tool's signature so the caller must state what it is operating on removes the whole failure class.
- Guards contribute nothing measurable on the runs where the routing is correct, which is why they are hard to justify and easy to delete.
- A confidence threshold requires the score to correlate with correctness, and here it does not: the wrong answers score inside the range of the right ones.

**Next:** [4. A loop that can stop](../04-a-loop-that-can-stop/). Every question in this lesson got an answer, including the ones with no answer at all.
