"""
wildcard_processor.py
----------------------
Responsible for ONE thing: expanding a wildcard term (containing '*') into
the set of matching vocabulary terms from the index.

Supports '*' meaning "zero or more characters", anywhere in the term:
    "sea*"    -> search, seat, sea, seasonal, ...
    "*ing"    -> running, coding, ...
    "s*ch"    -> search, stitch, ...
    "*"       -> every term in the vocabulary

This is a straightforward fnmatch-style implementation (fine for small-to-
medium vocabularies). It is kept separate from query_processor so the
wildcard-matching *strategy* can be swapped out later (e.g. for a permuterm
index or a trie) without changing boolean query logic.
"""

from __future__ import annotations

import fnmatch
from typing import Set

from .normalizer import normalize_token


def is_wildcard_term(term: str) -> bool:
    """True if `term` contains a '*' wildcard character."""
    return "*" in term


def expand_wildcard(term: str, vocabulary: Set[str]) -> Set[str]:
    """
    Expand a wildcard term against the given vocabulary.

    Args:
        term: a term possibly containing '*', e.g. "sea*ch"
        vocabulary: the full set of indexed terms

    Returns:
        set of vocabulary terms that match the wildcard pattern.
    """
    pattern = normalize_token(term)
    if not is_wildcard_term(pattern):
        # No wildcard - exact match only.
        return {pattern} if pattern in vocabulary else set()

    return {word for word in vocabulary if fnmatch.fnmatchcase(word, pattern)}
