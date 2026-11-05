"""Tiny, dependency-free text helpers for matching plain-language questions to catalog entries."""

from __future__ import annotations

import re

_NON_WORD = re.compile(r"[^a-z0-9]+")

STOPWORDS = frozenset(
    """
    a an and are at be been but by can could do does for from get got has have how i if in
    into is it its me my of on or our please should so some that the their them then there
    these this to up us was we were what when where which who why will with would you your
    """.split()  # noqa: SIM905 - easier to edit as prose
)


def singular(word: str) -> str:
    """Very small English singularizer, good enough for matching 'potholes' to 'pothole'."""
    if len(word) <= 3:
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("ches", "shes", "sses", "xes", "zes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokens(text: str, *, drop_stopwords: bool = False) -> list[str]:
    """Lowercase, split on non-alphanumerics, singularize. ``non-emergency`` → ``non emergency``."""
    words = [singular(w) for w in _NON_WORD.split(text.lower()) if w]
    if drop_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    return words


def contains_phrase(haystack: list[str], phrase: list[str]) -> bool:
    """True if ``phrase`` appears as a contiguous run of tokens in ``haystack``."""
    n = len(phrase)
    if n == 0 or n > len(haystack):
        return False
    return any(haystack[i : i + n] == phrase for i in range(len(haystack) - n + 1))


def remove_phrase(haystack: list[str], phrase: list[str]) -> list[str]:
    """Return ``haystack`` with every occurrence of ``phrase`` removed."""
    n = len(phrase)
    out: list[str] = []
    i = 0
    while i < len(haystack):
        if n and haystack[i : i + n] == phrase:
            i += n
        else:
            out.append(haystack[i])
            i += 1
    return out
