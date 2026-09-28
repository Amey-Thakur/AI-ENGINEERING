# 4. What it must not say

> **Ask the system what the budget for next quarter is.**
>
> It returns *the api key for the payment provider is live and sits in the
> config*, because that sentence shares the words *the*, *is* and *for* with
> your question, and nothing in a word overlap score has any concept of what
> it is holding.

**You will:** put eight sentences in the corpus that must never come out, measure how many leak, and measure the two defences, one of which is the one everybody builds and does not work.

**You need:** [lesson 3](../03-when-something-fails/).

<br>

## Nobody indexes a secret on purpose

`private.txt` holds eight sentences of the kind that end up in a document store by accident, because a folder was included, a wiki space was public, a backup was dropped in the wrong bucket, or a ticket quoted a config file:

```
the database password is hunter2 and has not been rotated
the api key for the payment provider is live and sits in the config
the customer record holds a home address and a phone number
the staging database is a copy of production with real names in it
```

Add them to the corpus. Change nothing else. Ask the same 25 questions phase 6 and 7 have been asking all along.

<br>

## Your turn

Measure all three and write `.work/leaks.tsv`:

```
defence              leaked  correct  asked
no protection        3       15       25
refuse the question  2       15       25
never index it       0       17       25
```

A leak is a private sentence returned to any question, whether or not the question asked for one.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
8 private sentences added to a corpus of 217, then 25 ordinary questions.

  defence               private sentences returned   handled correctly
  no protection                                  3   15 of 25
  refuse the question                            2   15 of 25
  never index it                                 0   17 of 25

What leaked with no protection at all:
  'what is the vault for'
    -> 'the api key for the payment provider is live and sits in the config'
       the question contains nothing a filter would catch
  'what is the database password'
    -> 'the database password is hunter2 and has not been rotated'
       the question contains a word a filter would catch
  'what is the budget for next quarter'
    -> 'the api key for the payment provider is live and sits in the config'
       the question contains nothing a filter would catch

Still leaking once the questions are filtered:
  'what is the vault for'
    -> 'the api key for the payment provider is live and sits in the config'
  'what is the budget for next quarter'
    -> 'the api key for the payment provider is live and sits in the config'

Filtering the question stops 1 of 3 leaks, and refuses 1 question
that had a perfectly good answer:
  'how often are credentials rotated'

So it trades one leak stopped for one answer lost, and the score stays at 15
of 25 either way. Two private sentences are still being handed out.

Not indexing them stops all 3 leaks and costs nothing: 17 of 25,
which is what the system scored before anybody pointed the indexer at the wrong folder.
```
<!-- end output -->

<br>

## Two of the three questions never asked for anything

*What is the database password* asked for a secret and got one. That is the case everybody imagines, and it is the least interesting of the three.

The other two are the lesson:

- *what is the vault for* is an ordinary question about infrastructure.
- *what is the budget for next quarter* is one of phase 7's **unanswerable** questions. Before the accident it was correctly declined. It now returns a payment credential.

Both retrieved the API key sentence on the words `the`, `is` and `for`. There was no attack, no cleverness, and nothing a reviewer reading the questions would flag.

> [!WARNING]
> **Retrieval has no concept of who is asking or what it is holding.**
>
> It is a similarity function over strings. It does not know that one
> sentence is a runbook and another is a credential, it cannot tell a curious
> user from an authorised one, and it will rank a secret first if the secret
> happens to share three common words with the question.
>
> Everything that makes a retrieval system feel intelligent, the fact that
> you can ask it anything in any words, is exactly what makes it unable to
> hold a boundary.

<br>

## The defence everybody builds first

Check the question for dangerous words and refuse:

```python
BLOCKED = ("password", "key", "secret", "credential", "credentials",
           "private", "admin", "token")
```

It stops **one leak of three**. The other two questions contain no word on the list and never will, because the leak is not caused by what the question asked for.

And it refuses *how often are credentials rotated*, which is a real question with a real answer in the public corpus, because any list long enough to be useful contains a word that legitimate questions use.

| | Leaked | Handled correctly |
| --- | --- | --- |
| No protection | 3 | 15 of 25 |
| Refuse the question | **2** | 15 of 25 |
| Never index it | **0** | **17 of 25** |

One leak stopped, one good answer lost, the same score, two secrets still going out of the door.

> [!CAUTION]
> Filtering the input is guessing at intent, and intent is not what selects
> the document. It is the same error as phase 6 lesson 3, where a tool could
> only refuse what it could detect: a filter can only catch what appears in
> the text it inspects, and the secret is in the text it does not inspect.
>
> Output filtering is better and still wrong. Scanning the returned sentence
> for `password` would catch the first leak and miss `the api key for the
> payment provider`, and you would be writing patterns for the rest of your
> life against a corpus you do not control.

<br>

## The defence that works is upstream and boring

Do not index it. **Zero leaks, 17 of 25, which is the score the system had before the mistake.** No pattern list, no model, no filter to maintain, no false refusals.

This is not a clever result and that is the point. The only reliable control on what a retrieval system can say is what is in the index, because everything downstream of the index is a similarity function that will happily rank anything it has been given.

> [!IMPORTANT]
> The practical form of this: retrieval boundaries have to be **enforced at
> index time, or per request by filtering the candidate set before scoring**,
> never by inspecting the question or the answer.
>
> If different users may see different documents, you need one index per
> permission set, or a filter applied to the candidates before ranking. A
> single shared index plus a clever prompt telling the model not to reveal
> things is not access control, and the sentence above is the entire security
> review of a great many systems shipped this year.

<br>

## Check yourself

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety/04-what-it-must-not-say
```

The check insists the question filter still leaks, because a defence that passed this test would mean the measurement was wrong.

<br>

## Going further

Optional, and there is no check for it.

Add the eight private sentences back and turn the threshold up until nothing leaks. It works, and you will find you have also stopped answering most of the legitimate questions, which is lesson 2's dial again: the threshold cannot tell a secret from a poor match because it cannot tell anything apart.

Then try the version that really is used in production: keep one index, and attach a permission label to every sentence. Filter the candidate list by label before scoring rather than after. Notice that the cost is the same as lesson 1's scan, because you are back to touching every document to decide whether you are allowed to look at it, and that this is why per-user indexes exist.

<br>

## What you learned

- A retrieval score has no concept of who is asking or what it is holding, so it will rank a credential first if the words line up.
- Two of the three leaks came from questions that asked for nothing sensitive, one of which was a question with no answer at all.
- A blocked word list on the question stopped one leak in three and refused a legitimate question, because the leak is not caused by what was asked.
- Output filtering has the same flaw and needs patterns for a corpus you do not control.
- Removing the sentences from the index stopped every leak and cost nothing.
- Retrieval boundaries belong at index time, or as a filter on the candidates before scoring, never as an inspection of the question or the answer.
- An instruction telling a model not to reveal something is not access control.

**Next:** [5. The thing you ship](../05-the-thing-you-ship/), which is the whole course in one file and one page.
