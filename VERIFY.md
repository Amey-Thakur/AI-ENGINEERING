<div align="center">

# Verify a record

### Three ways · None of them ask anybody's permission · All of them say what they prove

[![Back to the course](https://img.shields.io/badge/Back%20to-the%20course-1DE9B6.svg)](README.md)
[![Curriculum](https://img.shields.io/badge/Read-the%20curriculum-0969DA.svg)](CURRICULUM.md)

</div>

<br>

Finishing this course produces a **record of completion**, not a certificate of competence. It asserts one narrow thing: that on a given date, at a given commit, every check in the course ran and passed on the holder's machine. This page is how a reader checks that, and how they find out what the check is worth.

<br>

## What a record carries

Every record is a PNG with the fields written inside the file as well as printed on its face.

| Field | What it is |
|:------|:-----------|
| `name` | The name on the record, as the holder wrote it |
| `commit` | The commit of this repository the course was run at |
| `date` | The day it was issued |
| `passed` / `total` | The score. A record is only issued for a complete pass |
| `credential` | Twelve hexadecimal characters derived from the four above |

The credential is not a secret and not a lookup key. There is no database behind it and nothing to query. It is derived, and that is the whole mechanism:

```
credential = SHA-256( "name|commit|passed/total" )  →  first 12 hex characters, uppercased, in groups of four
```

So `Amey Thakur`, at commit `a2a3360a1370916c84b0a603440e21db79d84c50`, with `50/50`, always gives the same number, and changing any character of any field gives a different one.

<br>

## In your browser

<!-- The site serves this page with a verifier attached. On GitHub the block
     below is stripped, which is why the two command-line methods are here
     as well and why this page reads correctly without it. -->

<div id="verify-widget" markdown="0">
  <noscript>This checker needs JavaScript. The two methods below need only Python and work offline.</noscript>
</div>

**[Open the verifier on the website &rarr;](https://amey-thakur.github.io/AI-ENGINEERING/verify/)** Drop a record on it, or type the fields in. It recomputes the hash in your own browser: nothing is uploaded, and the page works with the network off once it has loaded.

<br>

## With the tool

Reads the fields out of the file, recomputes the credential, and compares.

```bash
python tools/verify_certificate.py record-of-completion.png
```

```text
  on the record
    name          Amey Thakur
    commit        a2a3360a1370916c84b0a603440e21db79d84c50
    date          2026-10-17
    score         50 of 50
    credential    F930-4DEE-F037

PASS  the credential matches the name, commit and score on the record
      which means those three have not been altered since it was issued
      it does not prove the course was run; pass --rerun to do that
```

If you only have a photograph or a printout, type the fields instead:

```bash
python tools/verify_certificate.py --name "Amey Thakur" \
  --commit a2a3360a1370916c84b0a603440e21db79d84c50 \
  --passed 50 --total 50 --credential F930-4DEE-F037
```

<br>

## By running the course yourself

The strongest check, and the only one that establishes the course actually passed.

```bash
python tools/verify_certificate.py record-of-completion.png --rerun
```

It checks out the commit named on the record, runs all fifty lessons at it, and puts your clone back where it was. It refuses if the clone has uncommitted changes, so it cannot lose your work.

<br>

## What each check establishes, exactly

| Check | Establishes | Does not establish |
|:------|:------------|:-------------------|
| The credential matches | The name, commit and score are the ones the record was issued with | That the course was ever run |
| The course passes at that commit | The course does pass, at the commit named | That this holder is the one who ran it |
| Both together | A complete, unaltered record of a course that genuinely passes | Anything about the holder's ability |

> [!IMPORTANT]
> **There is no signing key, and that is deliberate.**
>
> Anybody with a clone of this repository can issue a record for any name,
> because the credential is derived from public fields with a public
> algorithm. A course whose first promise is that it installs nothing and
> needs no account cannot also operate a private key and an issuing service.
>
> So the credential gives you **tamper evidence, not authenticity**: it tells
> you a record has not been edited since it was made, and says nothing about
> who made it. If you need to know that a particular person ran the course,
> ask them to run it in front of you, or to run it in a public GitHub Actions
> log from their own fork, which is what
> [`certificate.yml`](.github/workflows/certificate.yml) is for. That log is
> timestamped, public, and not editable by the person it is about.
>
> This is the same standard the lessons are held to. Phase 7 measures the
> course's own results and reports the ones that do not hold up; a
> verification page that overstated what it proves would fail that standard
> on its first line.

<br>

## Issuing one

```bash
python tools/certificate.py --name "Your Name"
```

It runs all fifty lessons first and writes nothing if one fails. There is no flag to skip that.

<br>

---

<div align="center">

[Start the course](phases/00-your-machine/) &nbsp;·&nbsp;
[The curriculum](CURRICULUM.md) &nbsp;·&nbsp;
[Questions](FAQ.md) &nbsp;·&nbsp;
[Glossary](GLOSSARY.md)

</div>
