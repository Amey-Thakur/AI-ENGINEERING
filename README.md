<div align="center">

# AI Engineering

**Learn to build AI systems by building them. From nothing installed, to shipping.**

No account. No API key. No GPU. No paid service. No library to install.
Every lesson runs on the Python that comes with your machine, and on a laptop with the network switched off.

<img alt="License" src="https://img.shields.io/github/license/Amey-Thakur/AI-ENGINEERING?color=lightgrey&label=License">
<img alt="Dependencies" src="https://img.shields.io/badge/Dependencies-0-2EA043">
<img alt="Cost" src="https://img.shields.io/badge/Cost-%240-2EA043">
<img alt="Runs offline" src="https://img.shields.io/badge/Runs-Offline-2EA043">
<a href="https://github.com/Amey-Thakur"><img alt="Developed by Amey Thakur" src="https://img.shields.io/badge/Developed%20by-Amey%20Thakur-0969DA"></a>

</div>

<br>

## Start here

You need a computer. That is the whole prerequisite list.

```
git clone https://github.com/Amey-Thakur/AI-ENGINEERING.git
cd AI-ENGINEERING
python tools/run_lessons.py phases/00-your-machine/01-the-terminal
```

If that last line fails because you do not have Python, or because you have never opened a terminal, that is expected and it is [lesson 1](phases/00-your-machine/01-the-terminal/).

> [!TIP]
> Fork this repository before you clone it, and clone your fork. Your work then
> lives on your own account rather than on one machine, and it is a record of
> what you did. [Lesson 5](phases/00-your-machine/05-git-and-your-copy/)
> explains the difference.

<br>

## Why this one

There is no shortage of AI courses. There is a shortage of AI courses that still work.

Open the most popular ones today and you will find lessons whose code no longer runs, datasets that were withdrawn, a statistics page reporting a p-value that is wrong, and a cloud account required before lesson two. None of that is carelessness. It is what happens when material is written faster than it can be checked, and when it is built on services that belong to somebody else.

This course is built the other way round.

| Guarantee | How it is kept |
| --- | --- |
| **Every lesson runs.** | Every solution and every check is executed on Linux, macOS and Windows on each change, and again every night. |
| **Every number shown is generated.** | Output printed in a lesson is compared against what the code actually prints. A figure is never typed by hand. |
| **Nothing can be taken away.** | Only the Python standard library is used, anywhere in the course. This is checked, not promised. |
| **Nothing is fetched.** | Lessons run with the network closed. A lesson that reaches for it fails on the push that introduced it. |
| **The same answer every time.** | Each solution is run under different string hashing and must print the same thing. A number that moves between runs is caught here. |

Those are not aspirations in a contributing guide. They are five programs in [`tools/`](tools/), and they run before anything is merged.

<br>

## The course

| Phase | What you build | Status |
| --- | --- | --- |
| **0** | [Your machine](phases/00-your-machine/) | Ready |
| **1** | [Teach it to tell two things apart](phases/01-teach-it-to-tell-two-things-apart/) | Ready |
| **2** | [A network you wrote yourself](phases/02-a-network-you-wrote-yourself/) | Ready |
| **3** | [Words that know what they mean](phases/03-words-that-know-what-they-mean/) | Ready |
| **4** | [A language model you wrote yourself](phases/04-a-language-model-you-wrote-yourself/) | Ready |
| **5** | [Finding the right thing to say](phases/05-finding-the-right-thing-to-say/) | Ready |
| **6** | [Tools and agents](phases/06-tools-and-agents/) | Ready |
| 7 | Measuring whether any of it works | Planned |
| 8 | Shipping: cost, latency, failure, safety | Planned |

There is no mathematics phase, and that is deliberate. Mathematics arrives in
the lesson where something breaks without it, which is the only time anyone has
ever wanted to learn it. You meet a weighted sum when your program needs one,
not eighty pages earlier.

You build one system across the whole course, rather than a drawer of disconnected exercises. Each phase adds a layer to the thing you already have.

<br>

## How a lesson works

Three files, the same every time.

| File | What it is |
| --- | --- |
| `README.md` | The lesson. |
| `solve.py` | The worked solution, written to be read. |
| `check.py` | Looks at what you produced, and says what is wrong in one line. |

```
python tools/run_lessons.py                    every lesson
python tools/run_lessons.py phases/00          one phase, or one lesson
python tools/run_lessons.py --list             name them and stop
```

<br>

## Checking the course itself

You do not have to take any of the five guarantees on trust. Run them.

```
python tools/run_lessons.py       every lesson still works
python tools/check_output.py      shown output matches real output
python tools/check_imports.py     nothing outside the standard library
python tools/check_determinism.py the same output on every run
python tools/progress.py          how far you have got
```

<br>

## Contributing

A lesson is accepted when it teaches one thing, its solution runs, and its check explains itself on failure. The full contract is in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

<br>

## License

[MIT](LICENSE). Use it, fork it, teach from it, translate it. Attribution is appreciated and not required.
