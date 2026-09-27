"""
File: tools/guard/sitecustomize.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Closes the network for the duration of a lesson.

Python imports a module named sitecustomize at interpreter start if one is on
the path. The lesson runner puts this directory on PYTHONPATH, so every lesson
process begins with the network already shut, before a single line of the
lesson has run.

This is the mechanism behind the promise on the front page. The course claims
that no lesson needs an API key, an account, a GPU or a paid service, and a
claim like that is worth nothing if it is only ever checked by reading. Here it
is checked by execution: a lesson that reaches for the network fails in CI on
the push that introduced it, and the failure names the file that did it.

The guard is deliberately narrow. It stops outbound connections. It does not
stop a lesson opening a local socket pair, which some standard library code
does for its own bookkeeping, and it says nothing about what a learner does on
their own machine after the lesson ends.
"""

import socket

MESSAGE = (
    "Network access is closed while a lesson runs.\n"
    "\n"
    "No lesson in this course may call an API, download a model or read a\n"
    "dataset from the internet. Everything a lesson needs is either in the\n"
    "standard library or vendored into the repository, so that the course\n"
    "runs on a laptop with no account and no credit card, and so that it\n"
    "cannot break when somebody else's service is retired.\n"
    "\n"
    "The guard that raised this is tools/guard/sitecustomize.py."
)


class NetworkClosed(RuntimeError):
    """Raised when lesson code tries to open a connection."""


def _refuse(*_args, **_kwargs):
    raise NetworkClosed(MESSAGE)


# Bound at import time, before any lesson code exists in memory.
socket.socket.connect = _refuse
socket.socket.connect_ex = _refuse
socket.create_connection = _refuse
