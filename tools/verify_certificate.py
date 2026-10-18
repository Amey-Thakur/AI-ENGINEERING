"""
File: tools/verify_certificate.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Checks a record of completion, and says exactly what the check establishes.

A record issued by tools/certificate.py carries a credential number that is a
hash of the name on it, the commit it was issued at, and the score. This reads
those fields back out of the file, recomputes the number, and reports whether
it still matches.

What that establishes, precisely:

    It matches     the name, commit and score on the record are the ones it
                   was issued with. Change any of them, by editing the image
                   or by retyping the fields, and the number stops matching.
    It does not    prove the course was actually run. Anybody with this
                   repository can issue a record for any name, because there
                   is no secret in it and deliberately so: a course that
                   installs nothing cannot also hold a signing key.

The proof that the course ran is the course running. Pass --rerun and this
checks out the commit on the record and runs all fifty lessons, which is the
same thing the record tells its reader to do.

Usage:
    python tools/verify_certificate.py record.png
    python tools/verify_certificate.py record.png --rerun
    python tools/verify_certificate.py --name "A Name" --commit abc123...
        --passed 50 --total 50 --credential ABCD-EF01-2345
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import lesson

#: The keys certificate.py writes into the png, so a record carries the fields
#: it was issued with rather than only a picture of them.
FIELDS = ("name", "commit", "date", "passed", "total", "credential")

#: Written into every record, so a file from some other tool is not read as
#: one of these.
MARKER = "AI Engineering record of completion"


def credential(name: str, at: str, passed: int, total: int) -> str:
    """The same derivation certificate.py uses. Kept identical on purpose."""
    seed = f"{name}|{at}|{passed}/{total}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()[:12].upper()

    return "-".join(digest[start:start + 4] for start in (0, 4, 8))


def read_png(path: Path) -> dict[str, str]:
    """The fields a record carries, read without needing Pillow.

    A png is a signature then a run of chunks. The text chunks hold the
    fields, and walking to them by hand keeps this tool runnable on a machine
    that has not installed anything, which is the promise the rest of the
    course makes.
    """
    raw = path.read_bytes()

    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"FAIL  {path} is not a png\n"
                         f"      a record is the png that certificate.py "
                         f"wrote")

    found: dict[str, str] = {}
    at = 8

    while at + 8 <= len(raw):
        length = int.from_bytes(raw[at:at + 4], "big")
        kind = raw[at + 4:at + 8]
        body = raw[at + 8:at + 8 + length]

        if kind == b"tEXt" and b"\x00" in body:
            key, _, value = body.partition(b"\x00")
            found[key.decode("latin-1")] = value.decode("utf-8", "replace")
        elif kind == b"IEND":
            break

        at += 12 + length

    return found


def report(fields: dict[str, str]) -> int:
    """Say what the record claims, then whether it holds together."""
    missing = [key for key in FIELDS if key not in fields]

    if missing:
        print(f"FAIL  the record does not carry {', '.join(missing)}")
        print("      records issued before these fields were written cannot "
              "be checked this way; re-issue it, or pass the fields with "
              "--name, --commit, --passed, --total and --credential")

        return 1

    try:
        passed = int(fields["passed"])
        total = int(fields["total"])
    except ValueError:
        print("FAIL  the score on the record is not a pair of whole numbers")

        return 1

    name = fields["name"]
    at = fields["commit"]
    claimed = fields["credential"].strip().upper()
    recomputed = credential(name, at, passed, total)

    print("  on the record")
    print(f"    name          {name}")
    print(f"    commit        {at}")
    print(f"    date          {fields['date']}")
    print(f"    score         {passed} of {total}")
    print(f"    credential    {claimed}")
    print()

    if claimed != recomputed:
        print(f"FAIL  the credential does not match those fields")
        print(f"      it reads {claimed} and those fields give {recomputed}, "
              f"so something on the record has been changed since it was "
              f"issued")

        return 1

    if passed != total:
        print(f"FAIL  the record says {passed} of {total}, and a record is "
              f"only issued for a complete pass")

        return 1

    print(f"PASS  the credential matches the name, commit and score on the "
          f"record")
    print(f"      which means those three have not been altered since it was "
          f"issued")
    print(f"      it does not prove the course was run; pass --rerun to do "
          f"that")

    return 0


def rerun(at: str) -> int:
    """Check out the commit on the record and run every lesson at it."""
    print()
    print(f"  checking out {at[:12]} and running the course at it")

    here = subprocess.run(["git", "-C", str(lesson.ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True)

    if here.returncode != 0:
        print("FAIL  this is not a git clone, so there is no commit to check "
              "out")
        print("      clone the repository and run this inside the clone")

        return 1

    started_at = here.stdout.strip()
    known = subprocess.run(["git", "-C", str(lesson.ROOT), "cat-file", "-e",
                            f"{at}^{{commit}}"], capture_output=True)

    if known.returncode != 0:
        print(f"FAIL  this clone does not have commit {at[:12]}")
        print(f"      fetch it first, or check the record came from this "
              f"repository")

        return 1

    dirty = subprocess.run(["git", "-C", str(lesson.ROOT), "status",
                           "--porcelain"], capture_output=True, text=True)

    if dirty.stdout.strip():
        print("FAIL  this clone has uncommitted changes, and checking out "
              "would lose them")
        print("      commit or stash them, then run this again")

        return 1

    moved = subprocess.run(["git", "-C", str(lesson.ROOT), "checkout",
                           "--quiet", at], capture_output=True, text=True)

    if moved.returncode != 0:
        print(f"FAIL  could not check out {at[:12]}")
        print(f"      {moved.stderr.strip()}")

        return 1

    try:
        ran = subprocess.run([sys.executable, "tools/run_lessons.py"],
                             cwd=lesson.ROOT)
    finally:
        subprocess.run(["git", "-C", str(lesson.ROOT), "checkout", "--quiet",
                        started_at], capture_output=True)
        print(f"  put back on {started_at[:12]}")

    if ran.returncode != 0:
        print()
        print("FAIL  the course does not pass at the commit on the record")

        return 1

    print()
    print("PASS  every lesson passes at the commit on the record, which is "
          "the thing")
    print("      the record was issued for")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a record of completion issued by this course.")
    parser.add_argument("record", nargs="?", type=Path,
                        help="the png to check")
    parser.add_argument("--name", help="instead of reading a file")
    parser.add_argument("--commit", help="the commit on the record")
    parser.add_argument("--date", default="not given")
    parser.add_argument("--passed", type=int)
    parser.add_argument("--total", type=int)
    parser.add_argument("--credential", help="the number printed on it")
    parser.add_argument("--rerun", action="store_true",
                        help="also check out that commit and run the course")
    parsed = parser.parse_args()

    if parsed.record:
        if not parsed.record.exists():
            print(f"FAIL  {parsed.record} does not exist")

            return 1

        fields = read_png(parsed.record)

        if fields.get("issued-by") and fields["issued-by"] != MARKER:
            print(f"FAIL  {parsed.record} was not issued by this course")

            return 1

        print(f"  reading {parsed.record}")
        print()
    elif parsed.name and parsed.commit and parsed.credential:
        fields = {"name": " ".join(parsed.name.split()),
                  "commit": parsed.commit, "date": parsed.date,
                  "passed": str(parsed.passed if parsed.passed is not None
                                else 0),
                  "total": str(parsed.total if parsed.total is not None
                               else 0),
                  "credential": parsed.credential}
    else:
        parser.print_help()
        print()
        print("Give it a record, or give it --name, --commit, --passed, "
              "--total and --credential.")

        return 1

    outcome = report(fields)

    if outcome == 0 and parsed.rerun:
        return rerun(fields["commit"])

    return outcome


if __name__ == "__main__":
    raise SystemExit(main())
